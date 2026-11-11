"""DA vòng 2 — T1.4 / T1.5: kiểm ĐỘC LẬP bảng thời tiết ngày và bảng gộp từ 8 file cache giờ. Không import src/.

Dùng: python r2_weather_check.py <thư mục cache> <daily.csv cần kiểm> <merged.csv cần kiểm> <bảng sạch air_quality_8cities.csv>
                                <daily.csv đối chiếu (đã commit)> <thư mục out> <nhãn>
Cách tính đối chiếu: giá trị giờ trong cache có tối đa 2 chữ số thập phân, nên tổng 24 giờ được tính bằng SỐ NGUYÊN (phần trăm đơn vị).
Trung bình ngày vì thế có giá trị đúng tuyệt đối, và ô "nằm đúng biên x,xx5" được nhận ra chính xác (tổng mod 24 == 12), không phụ thuộc
cách cộng số thực của numpy/pandas.
  Phần 2 (so với kỳ vọng độc lập): ô đúng biên được nhận cả làm tròn lên và xuống; ô khác phải khớp ở 1e-9.
  Phần 3 (so với file đã commit, T1.5): chỉ temp_mean, pressure_mean, wind_speed_mean được lệch tới 0,01 và chỉ ở ô đúng biên; cột khác 1e-9;
  rain_day, wind_dir_8, mặt nạ NaN so chính xác. Quy tắc theo da_verification_protocol.md mục 9.1.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

cache, daily_p, merged_p, clean_p, ref_p, out, tag = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], Path(sys.argv[6]), sys.argv[7]
out.mkdir(parents=True, exist_ok=True)
CITIES = ["Delhi", "Gurugram", "Lucknow", "Jaipur", "Bengaluru", "Amritsar", "Chennai", "Hyderabad"]
START, END = "2014-12-25", "2020-07-01"
DIRS8 = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
MEAN = {"temp_mean": "temperature_2m", "humidity_mean": "relative_humidity_2m", "pressure_mean": "surface_pressure", "wind_speed_mean": "wind_speed_10m", "blh_mean": "boundary_layer_height"}
TOL_COLS = ["temp_mean", "pressure_mean", "wind_speed_mean"]          # ba cột được phép lệch 0,01 nếu đúng biên (RA-DEC-02 mục 5)
EPS = 1e-9
rows = []
def rec(crit, expected, actual, note=""):
    rows.append({"bo": tag, "tieu_chi": crit, "mong_doi": expected, "thuc_te": actual, "dat": bool(expected == actual), "ghi_chu": note})

# ------------------------------------------------------------------ 1. cache giờ
full = pd.date_range(START + " 00:00", END + " 23:00", freq="h")
rec("số giờ lịch mỗi thành phố (tính từ lịch)", 48384, len(full))
exp, tie = [], []
n_files = 0
for c in CITIES:
    p = cache / f"openmeteo_{c.lower()}_hourly.csv.gz"
    if not p.exists():
        rec(f"cache {c} tồn tại", True, False); continue
    n_files += 1
    h = pd.read_csv(p); t = pd.to_datetime(h["time"])
    ok_grid = len(h) == len(full) and bool((t.reset_index(drop=True) == pd.Series(full)).all())
    rec(f"{c}: lưới giờ liên tục đúng lịch, không trùng", True, ok_grid, f"{len(h)} dòng; trùng {int(t.duplicated().sum())}")
    rec(f"{c}: có cột boundary_layer_height và không trống", True, "boundary_layer_height" in h.columns and int(h["boundary_layer_height"].isna().sum()) == 0)
    core = ["temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "precipitation"]
    rec(f"{c}: ô trống ở 6 biến lõi", 0, int(h[core].isna().sum().sum()))
    peak = int(h.groupby(t.dt.hour)["temperature_2m"].mean().idxmax())
    rec(f"{c}: giờ nóng nhất trung bình nằm trong 12–16h (thời gian trong cache là giờ địa phương)", True, 12 <= peak <= 16, f"giờ nóng nhất = {peak}h; nếu chuỗi là UTC đỉnh sẽ rơi khoảng 7–10h")
    h["Date"] = t.dt.normalize(); g = h.groupby("Date")
    rec(f"{c}: mọi ngày đủ 24 giờ", True, bool((g.size() == 24).all()))
    e = pd.DataFrame(index=g.size().index); tm = pd.DataFrame(index=e.index)
    for col, src in MEAN.items():
        cents = np.rint(h[src].to_numpy() * 100).astype(np.int64)
        assert np.abs(h[src].to_numpy() * 100 - cents).max() < 1e-6, f"{src} có hơn 2 chữ số thập phân"
        S = pd.Series(cents, index=h.index).groupby(h["Date"]).sum()            # tổng 24 giờ, đơn vị 0,01
        q, r = np.divmod(S.to_numpy(), 24)                                         # S/24 = q + r/24 (đơn vị 0,01)
        e[col] = np.where(r * 2 > 24, q + 1, q) / 100.0                            # làm tròn gần nhất; ô r == 12 là đúng biên
        e[col + "__lo"], e[col + "__hi"] = q / 100.0, (q + 1) / 100.0
        tm[col] = (r == 12)
    for col, src, fn in (("temp_min", "temperature_2m", "min"), ("temp_max", "temperature_2m", "max"), ("wind_speed_max", "wind_speed_10m", "max"), ("blh_min", "boundary_layer_height", "min")):
        e[col] = getattr(g[src], fn)().round(2)
    pc = np.rint(h["precipitation"].to_numpy() * 100).astype(np.int64)
    e["precip_sum"] = pd.Series(pc, index=h.index).groupby(h["Date"]).sum() / 100.0
    ang = np.deg2rad(h["wind_direction_10m"].to_numpy(float)); ws = h["wind_speed_10m"].to_numpy(float)
    for col, comp in (("wind_u", -ws * np.sin(ang)), ("wind_v", -ws * np.cos(ang))):
        m = pd.Series(comp, index=h.index).groupby(h["Date"]).mean()
        e[col] = m.round(2); e[col + "__near_tie"] = np.abs(m * 100 - np.floor(m * 100) - 0.5) < 1e-6
    e["rain_day"] = e["precip_sum"] >= 1.0
    deg = (np.degrees(np.arctan2(-e["wind_u"], -e["wind_v"])) + 360) % 360
    e["wind_dir_8"] = np.array(DIRS8)[(((deg + 22.5) // 45).astype(int) % 8).to_numpy()]
    e.insert(0, "City", c); exp.append(e.reset_index()); tm.insert(0, "City", c); tie.append(tm.reset_index())
rec("số file cache đọc được", 8, n_files)
exp, tie = pd.concat(exp, ignore_index=True), pd.concat(tie, ignore_index=True)
rec("bảng ngày kỳ vọng: số hàng (8 × 2.016)", 16128, len(exp))
rec("số ô trung bình nằm đúng biên x,xx5 (tính bằng số nguyên)", "—", "—", "; ".join(f"{c} {int(tie[c].sum())}" for c in MEAN))

# ------------------------------------------------------------------ 2. bảng ngày cần kiểm so với kỳ vọng độc lập
def compare_daily(d, label):
    d = d.copy(); d["Date"] = pd.to_datetime(d["Date"])
    rec(f"[{label}] số hàng", 16128, len(d)); rec(f"[{label}] khóa (City, Date) trùng", 0, int(d.duplicated(["City", "Date"]).sum()))
    cols = ["City", "Date", "temp_mean", "temp_min", "temp_max", "humidity_mean", "pressure_mean", "wind_speed_mean", "wind_speed_max", "wind_u", "wind_v", "precip_sum", "blh_mean", "blh_min", "rain_day", "wind_dir_8"]
    rec(f"[{label}] tên và thứ tự cột", ",".join(cols), ",".join(d.columns))
    m = exp.merge(d, on=["City", "Date"], how="outer", suffixes=("", "__got"), indicator=True).merge(tie, on=["City", "Date"], how="left", suffixes=("", "__tie"))
    rec(f"[{label}] khóa khớp bảng kỳ vọng", True, bool((m._merge == "both").all()))
    m = m[m._merge == "both"]
    det = []
    for col in [c for c in cols if c not in ("City", "Date")]:
        got = m[col + "__got"]
        rec(f"[{label}] {col}: ô trống", 0, int(got.isna().sum()))
        if col in ("rain_day", "wind_dir_8"):
            bad = got.astype(str) != m[col].astype(str); rule = pd.Series("so chính xác", index=m.index); dv = bad.astype(float)
        else:
            dv = (got - m[col]).abs()
            if col in MEAN:
                at_tie = m[col + "__tie"].astype(bool)
                okt = ((got - m[col + "__lo"]).abs() <= EPS) | ((got - m[col + "__hi"]).abs() <= EPS)
                # So với kỳ vọng ĐỘC LẬP: ở ô đúng biên, cả hai cách làm tròn đều là kết quả đúng của phép tính (script này không đoán được
                # numpy làm tròn về phía nào), nên chấp nhận cả hai cho MỌI cột trung bình. Việc chỉ ba cột được lệch so với FILE ĐÃ COMMIT
                # (RA-DEC-02 mục 5) được kiểm riêng ở phần 3.
                bad = pd.Series(np.where(at_tie, ~okt, dv > EPS), index=m.index)
                rule = pd.Series(np.where(at_tie, "đúng biên x,xx5", "không ở biên"), index=m.index)
            else:
                bad = dv > EPS; rule = pd.Series("1e-9", index=m.index)
        differs = dv > EPS if col not in ("rain_day", "wind_dir_8") else bad
        for city in CITIES:
            k = m.City == city
            det.append({"bo": tag, "doi_chieu": label, "cot": col, "City": city, "so_o": int(k.sum()), "o_khac_ky_vong_doc_lap": int((differs & k).sum()),
                        "trong_do_o_dung_bien": int((differs & k & (rule.str.startswith("đúng biên"))).sum()), "o_vi_pham_quy_tac": int((bad & k).sum()),
                        "chenh_lon_nhat": float(dv[k].max()) if col not in ("rain_day", "wind_dir_8") else float((bad & k).sum() > 0)})
    return pd.DataFrame(det)

daily = pd.read_csv(daily_p)
det = compare_daily(daily, "bảng ngày cần kiểm so với kỳ vọng độc lập")
s = det.groupby("cot", sort=False)[["o_khac_ky_vong_doc_lap", "trong_do_o_dung_bien", "o_vi_pham_quy_tac"]].sum()
rec("bảng ngày: ô vi phạm quy tắc dung sai (mọi cột)", 0, int(s.o_vi_pham_quy_tac.sum()), "; ".join(f"{i}: khác {r.o_khac_ky_vong_doc_lap}, đúng biên {r.trong_do_o_dung_bien}, vi phạm {r.o_vi_pham_quy_tac}" for i, r in s.iterrows() if r.o_khac_ky_vong_doc_lap))

# ------------------------------------------------------------------ 3. bảng ngày cần kiểm so với file đã commit (T1.5)
ref = pd.read_csv(ref_p)
if Path(ref_p).resolve() != Path(daily_p).resolve():
    a, b = daily.copy(), ref.copy()
    rec("[so với file đã commit] cùng số hàng, cùng cột, cùng thứ tự khóa", True, a.shape == b.shape and list(a.columns) == list(b.columns) and bool((a[["City", "Date"]].astype(str).values == b[["City", "Date"]].astype(str).values).all()))
    tj = tie.assign(Date=tie.Date.dt.strftime("%Y-%m-%d")).set_index(["City", "Date"]).reindex(pd.MultiIndex.from_frame(a[["City", "Date"]].astype(str)))
    d2 = []
    for col in a.columns[2:]:
        if col in ("rain_day", "wind_dir_8"):
            df = (a[col].astype(str) != b[col].astype(str)).to_numpy(); mx = float(df.any()); viol = df
        else:
            dv = (a[col] - b[col]).abs().to_numpy(); df = dv > EPS; mx = float(np.nanmax(dv))
            viol = df & ~(tj[col].to_numpy(bool) & (dv <= 0.01 + EPS)) if col in TOL_COLS else df
        nan_mis = int((a[col].isna() != b[col].isna()).sum())
        for city in CITIES:
            k = (a.City == city).to_numpy()
            d2.append({"bo": tag, "doi_chieu": "bảng ngày cần kiểm so với file đã commit", "cot": col, "City": city, "so_o": int(k.sum()), "o_khac": int((df & k).sum()),
                       "o_vi_pham_quy_tac": int((viol & k).sum()), "chenh_lon_nhat": float(np.nanmax(np.where(k, (a[col] - b[col]).abs(), 0))) if col not in ("rain_day", "wind_dir_8") else float((df & k).any()),
                       "lech_mat_na_NaN": nan_mis})
    d2 = pd.DataFrame(d2); d2.to_csv(out / f"R2_W02_{tag}_daily_vs_committed.csv", index=False)
    s2 = d2.groupby("cot", sort=False)[["o_khac", "o_vi_pham_quy_tac"]].sum()
    rec("[so với file đã commit] tổng ô số khác", "—", int(s2.o_khac.sum()), "; ".join(f"{i} {r.o_khac}" for i, r in s2.iterrows() if r.o_khac) + f"; chênh lớn nhất {d2.chenh_lon_nhat.max():.4f}")
    rec("[so với file đã commit] ô vi phạm quy tắc dung sai", 0, int(s2.o_vi_pham_quy_tac.sum()))
else:
    rec("[so với file đã commit]", "—", "—", "bảng cần kiểm chính là file đã commit; bỏ qua phép so này")

# ------------------------------------------------------------------ 4. bảng gộp
mg = pd.read_csv(merged_p); cl = pd.read_csv(clean_p)
rec("bảng gộp: kích thước", "14056x54", f"{mg.shape[0]}x{mg.shape[1]}")
rec("bảng gộp: khóa (City, Date) trùng", 0, int(mg.duplicated(["City", "Date"]).sum()))
aq_cols = list(cl.columns); rec("bảng gộp: 40 cột đầu là 40 cột của bảng sạch, đúng thứ tự", True, list(mg.columns[:40]) == aq_cols and len(aq_cols) == 40)
same_keys = bool((mg[["City", "Date"]].values == cl[["City", "Date"]].values).all()) if len(mg) == len(cl) else False
rec("bảng gộp: thứ tự hàng trùng bảng sạch", True, same_keys)
if same_keys:
    nd = 0
    for c in aq_cols:
        x, y = mg[c], cl[c]
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y) and x.dtype != bool:
            nd += int((~((x.isna() & y.isna()) | ((x - y).abs() <= EPS))).sum())
        else:
            nd += int((~((x.isna() & y.isna()) | (x.astype(str) == y.astype(str)))).sum())
    rec("bảng gộp: ô khác bảng sạch ở 40 cột chất lượng không khí", 0, nd)
wcols = list(mg.columns[40:])
rec("bảng gộp: 14 cột thời tiết", ",".join(daily.columns[2:]), ",".join(wcols))
rec("bảng gộp: ô thời tiết thiếu", 0, int(mg[wcols].isna().sum().sum()))
j = mg[["City", "Date"] + wcols].merge(daily, on=["City", "Date"], how="left", suffixes=("", "__d"), validate="1:1")
nd = sum(int((~((j[c] - j[c + "__d"]).abs() <= EPS)).sum()) if pd.api.types.is_numeric_dtype(j[c]) and j[c].dtype != bool else int((j[c].astype(str) != j[c + "__d"].astype(str)).sum()) for c in wcols)
rec("bảng gộp: ô thời tiết khác bảng ngày cùng khóa", 0, nd)

res = pd.DataFrame(rows); res.to_csv(out / f"R2_W01_{tag}_checks.csv", index=False); det.to_csv(out / f"R2_W01_{tag}_daily_vs_independent.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120); pd.set_option("display.max_rows", 300)
show = res[~res.tieu_chi.str.match(r"^(Delhi|Gurugram|Lucknow|Jaipur|Bengaluru|Amritsar|Chennai|Hyderabad): ") & ~res.tieu_chi.str.contains("ô trống")]
print(show[["tieu_chi", "mong_doi", "thuc_te", "dat", "ghi_chu"]].to_string(index=False))
chk = res[res.mong_doi.astype(str) != "—"]
print(f"\n{tag}: {int(chk.dat.sum())}/{len(chk)} tiêu chí đạt; không đạt: {list(chk[~chk.dat].tieu_chi)}")
sys.exit(0 if chk.dat.all() else 1)
