"""DA vòng 2 — BẢN THAM CHIẾU của DA cho đặc trưng "as-of t" (RA-DEC-02 mục 2–4) và bộ CA BIÊN có kỳ vọng viết tay (T2.4).

KHÔNG import src/ (cũ hay mới). Đây là cách DA đọc quyết định của RA, dùng làm đối chứng cho mã Dev; nó không phải mã được nghiệm thu,
và không được dùng để tính metric mô hình thay cho mã Dev.

Quy tắc cho 5 chất (PM2.5, NO2, CO, SO2, O3), tại mỗi hàng (thành phố, ngày t), chỉ đọc raw của chính thành phố với ngày <= t:
  1. Chuỗi 0 = các ngày LỊCH liên tiếp có giá trị quan sát bằng 0; không nối qua ô NaN, qua ngày lịch thiếu dòng, hay qua thành phố khác.
  2. Trong prefix <= t, chuỗi 0 đã dài >= 3 ngày thì bị mask cả chuỗi (phần đã quan sát). Chuỗi mới dài 1–2 ngày: giữ số 0.
  3. Sau mask: forward-fill tối đa 2 ngày lịch; số 0 đã mask không làm nguồn điền. Không backward-fill, không nội suy.
  4. Đặc trưng = log1p(giá trị ở t sau bước 3). Hàng của ngày t KHÔNG bị tính lại khi có thêm ngày sau t.
AQI (theo công thức của baseline, áp lên AQI raw): aqi_0 = log AQI(t); aqi_1, aqi_2 = log AQI(t−1), AQI(t−2);
  aqi_wk = log trung bình AQI của 7 ngày t−7…t−1, cần ít nhất 3 ngày có số.

Dùng:
  python r2_ref_asof.py ref <raw.csv> <out.csv.gz>                         # bảng tham chiếu trên một file raw
  python r2_ref_asof.py fixture <raw.csv gốc> <thư mục out>                # tạo 2 file raw ca biên (bộ chính; bộ xóa dòng) + bảng kỳ vọng viết tay, tự kiểm
  python r2_ref_asof.py diff <ref.csv.gz> <R2_B03_baseline_features_L3.csv.gz> <R2_B03_baseline_cohort_keys.csv> <thư mục out>
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

CITIES = ["Delhi", "Gurugram", "Lucknow", "Jaipur", "Bengaluru", "Amritsar", "Chennai", "Hyderabad"]
POLL = {"PM2.5": "pm25_0", "NO2": "no2_0", "CO": "co_0", "SO2": "so2_0", "O3": "o3_0"}
START, END = pd.Timestamp("2017-06-14"), pd.Timestamp("2020-07-01")
ONE = pd.Timedelta(days=1)


def asof_value(dates, vals, i):
    """Giá trị 'as-of' của hàng i, chỉ đọc vals[0..i]. dates: mảng SỐ NGÀY (số nguyên, tăng dần) của MỘT thành phố (có thể thiếu ngày lịch)."""
    def masked(j):                                   # ô j (<= i) có thuộc chuỗi 0 đã dài >= 3 trong prefix <= i không?
        if not (vals[j] == 0):
            return False
        a = j
        while a - 1 >= 0 and vals[a - 1] == 0 and dates[a] - dates[a - 1] == 1:
            a -= 1
        b = j
        while b + 1 <= i and vals[b + 1] == 0 and dates[b + 1] - dates[b] == 1:      # không bao giờ nhìn quá i
            b += 1
        return (b - a + 1) >= 3
    for j in range(i, -1, -1):                       # ngày t, rồi lùi tối đa 2 ngày LỊCH
        if dates[i] - dates[j] > 2:
            break
        if not np.isnan(vals[j]) and not masked(j):
            return float(vals[j])
    return np.nan


def reference(raw):
    """Bảng tham chiếu: mọi hàng (thành phố, ngày) của 8 thành phố, đặc trưng chất ô nhiễm và AQI theo quy tắc as-of."""
    out = []
    for c in CITIES:
        g = raw[raw.City == c].sort_values("Date").reset_index(drop=True)
        dates = g.Date.to_numpy().astype("datetime64[D]").astype(np.int64)
        r = pd.DataFrame({"City": c, "Date": g.Date})
        for col, name in POLL.items():
            v = g[col].to_numpy(float)
            x = np.array([asof_value(dates, v, i) for i in range(len(g))])
            r[name] = np.log1p(x)
        a = g.set_index("Date").AQI.astype(float)
        cal = lambda k: a.reindex(g.Date - k * ONE).to_numpy()            # AQI của ngày lịch t−k (NaN nếu không có dòng)
        with np.errstate(invalid="ignore", divide="ignore"):
            r["aqi_0"], r["aqi_1"], r["aqi_2"] = np.log(cal(0)), np.log(cal(1)), np.log(cal(2))
            past = np.column_stack([cal(k) for k in range(1, 8)])
            n = (~np.isnan(past)).sum(1)
            r["aqi_wk"] = np.log(np.where(n >= 3, np.nansum(past, 1) / np.maximum(n, 1), np.nan))
        out.append(r)
    return pd.concat(out, ignore_index=True)


# ------------------------------------------------------------------ ca biên: giá trị tiêm vào raw và KỲ VỌNG VIẾT TAY (trước log1p)
N = np.nan
A, B = 61.1, 62.2
FIX = [  # (ca, thành phố, cột raw, ngày đầu, [giá trị tiêm], [kỳ vọng as-of từng ngày], giải thích)
    ("M1 chuỗi 0 dài 1, giữa chuỗi", "Delhi", "PM2.5", "2018-03-05", [A, 0, B], [A, 0, B], "1 ngày 0: giữ"),
    ("M2 chuỗi 0 dài 2, giữa chuỗi", "Delhi", "PM2.5", "2018-03-12", [A, 0, 0, B], [A, 0, 0, B], "2 ngày 0: giữ cả hai"),
    ("M3 chuỗi 0 dài 3, giữa chuỗi", "Delhi", "PM2.5", "2018-03-19", [A, 0, 0, 0, B], [A, 0, 0, N, B], "ngày 1–2 giữ 0 (hàng đã phát hành); ngày 3 mask; 3 ô mask liền nhau nên không điền được từ A"),
    ("M4 chuỗi 0 dài 4, giữa chuỗi", "Delhi", "PM2.5", "2018-03-26", [A, 0, 0, 0, 0, B], [A, 0, 0, N, N, B], "ngày 3 và 4 mask"),
    ("G1 chuỗi 0 bị ô NaN cắt đôi", "Delhi", "NO2", "2018-04-02", [A, 0, 0, N, 0, B], [A, 0, 0, 0, 0, B], "2 ngày 0 + NaN + 1 ngày 0: không nối qua NaN nên không chuỗi nào đủ 3; ô NaN được điền từ số 0 hợp lệ liền trước"),
    ("G2 số 0 đã mask không làm nguồn điền", "Delhi", "NO2", "2018-04-16", [A, 0, 0, 0, N, N, B], [A, 0, 0, N, N, N, B], "chuỗi 3 ngày 0 bị mask; hai ô NaN sau đó không được điền bằng 0, và A đã xa quá 2 ngày"),
    ("F1 forward-fill tối đa 2 ngày, không backward-fill, không nội suy", "Delhi", "SO2", "2018-05-07", [A, N, N, N, B], [A, A, A, N, B], "2 ngày đầu điền A; ngày thứ 3 để trống (không lấy B, không nội suy)"),
    ("S đầu chuỗi: 4 ngày 0", "Jaipur", "CO", "2017-06-14", [0, 0, 0, 0, 1.11], [0, 0, N, N, 1.11], "như M4 nhưng không có giá trị nào trước đó"),
    ("C1 chuyển thành phố: không nối chuỗi 0", "Jaipur", "NO2", "2017-06-14", [0, 33.3], [0, 33.3], "hai ngày cuối của Hyderabad và Lucknow bị đặt 0; ngày đầu của Jaipur vẫn là chuỗi dài 1"),
    ("C2 chuyển thành phố: không forward-fill", "Jaipur", "SO2", "2017-06-14", [N, N, 12.3], [N, N, 12.3], "ngày cuối của Hyderabad và Lucknow bị đặt 77,7; hai ngày đầu của Jaipur vẫn trống"),
    ("T ranh train/test: chuỗi 0 vắt qua 30/06–01/07/2019", "Delhi", "O3", "2019-06-28", [A, 0, 0, 0, 0, B], [A, 0, 0, N, N, B], "29/06 và 30/06 giữ 0; 01/07 và 02/07 mask"),
]
# Bộ thứ hai: raw bị XÓA DÒNG để có "ngày lịch thiếu" (raw thật không thiếu ngày nào). "DEL" = xóa dòng của ngày đó; ngày bị xóa không có kỳ vọng.
DEL = "DEL"
FIX_GAP = [
    ("D1 chuỗi 0 sát ngày lịch thiếu: không nối qua ngày thiếu", "Lucknow", "CO", "2018-08-06", [1.11, 0, 0, DEL, 0, 2.22], [1.11, 0, 0, DEL, 0, 2.22], "2 ngày 0 + ngày thiếu + 1 ngày 0: không chuỗi nào đủ 3"),
    ("D2 forward-fill đếm theo ngày lịch qua ngày thiếu", "Lucknow", "SO2", "2018-09-03", [A, DEL, N, N, B], [A, DEL, A, N, B], "ô NaN cách A 2 ngày lịch: điền A; ô cách 3 ngày lịch: trống"),
    ("D3 chuỗi 0 đếm lại sau ngày thiếu", "Lucknow", "NO2", "2018-10-01", [A, 0, DEL, 0, 0, 0, B], [A, 0, DEL, 0, 0, N, B], "sau ngày thiếu, ngày 0 thứ 1–2 giữ 0; ngày 0 thứ 3 mask và hai ô 0 trước nó không làm nguồn điền"),
]
AUX = [("Hyderabad", "NO2", "2020-06-30", [0, 0]), ("Lucknow", "NO2", "2020-06-30", [0, 0]), ("Hyderabad", "SO2", "2020-07-01", [77.7]), ("Lucknow", "SO2", "2020-07-01", [77.7])]


def make_fixture(raw, fix=None, aux=None):
    fix = FIX if fix is None else fix; aux = AUX if aux is None else aux
    r = raw.copy(); rows = []; drop = []
    idx = {(c, d): i for i, (c, d) in enumerate(zip(r.City, r.Date))}
    for case, city, col, d0, inj, expd, why in fix:
        assert len(inj) == len(expd)
        for k, (v, e) in enumerate(zip(inj, expd)):
            d = pd.Timestamp(d0) + k * ONE
            if isinstance(v, str):                       # DEL: xóa dòng
                assert v == DEL and e == DEL; drop.append(idx[(city, d)]); continue
            r.loc[idx[(city, d)], col] = v
            rows.append({"ca": case, "City": city, "Date": d, "cot_raw": col, "dac_trung": POLL[col], "gia_tri_tiem": v, "ky_vong_truoc_log1p": e,
                         "ky_vong_dac_trung": np.log1p(e), "giai_thich": why})
    for city, col, d0, inj in aux:
        for k, v in enumerate(inj):
            r.loc[idx[(city, pd.Timestamp(d0) + k * ONE)], col] = v
    return r.drop(index=drop).reset_index(drop=True), pd.DataFrame(rows)


def self_check(fx, exp):
    """So kỳ vọng viết tay với bản tham chiếu, và kiểm bất biến hàng khi cắt raw ở chính ngày của hàng. Trả (exp có thêm cột, số hàng đổi khi cắt)."""
    ref = reference(fx).set_index(["City", "Date"])
    got = np.array([ref.loc[(r.City, r.Date), r.dac_trung] for r in exp.itertuples()])
    exp = exp.copy(); exp["tham_chieu_DA"] = got
    exp["viet_tay_khop_tham_chieu"] = np.isclose(got, exp.ky_vong_dac_trung.to_numpy(), equal_nan=True, rtol=0, atol=1e-12)
    bad = 0
    for r in exp.itertuples():
        cut = reference(fx[fx.Date <= r.Date]).set_index(["City", "Date"])
        a, b = cut.loc[(r.City, r.Date), r.dac_trung], ref.loc[(r.City, r.Date), r.dac_trung]
        bad += int(not ((np.isnan(a) and np.isnan(b)) or a == b))
    return exp, bad


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "ref":
        raw = pd.read_csv(sys.argv[2], parse_dates=["Date"])
        ref = reference(raw)
        ref.to_csv(sys.argv[3], index=False, date_format="%Y-%m-%d", float_format="%.12g")
        print(len(ref), "hàng ->", sys.argv[3])
    elif mode == "fixture":
        raw = pd.read_csv(sys.argv[2], parse_dates=["Date"]); out = Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
        fx, exp = make_fixture(raw)
        assert len(fx) == len(raw) and list(fx.columns) == list(raw.columns)
        changed = int(sum(((fx[c] != raw[c]) & ~(fx[c].isna() & raw[c].isna())).sum() for c in POLL))
        assert bool((fx.AQI.fillna(-1) == raw.AQI.fillna(-1)).all()), "ca biên không được đụng tới AQI"
        fx.to_csv(out / "R2_F01_fixture_city_day.csv", index=False, date_format="%Y-%m-%d")
        exp, bad = self_check(fx, exp); exp.insert(0, "bo", "chinh (đủ 14.056 dòng)")
        # bộ thứ hai: xóa dòng để có ngày lịch thiếu
        fx2, exp2 = make_fixture(raw, FIX_GAP, [])
        ndel = len(raw) - len(fx2); assert ndel == sum(v == DEL for f in FIX_GAP for v in f[4] if isinstance(v, str))
        fx2.to_csv(out / "R2_F01_fixture_thieu_ngay_city_day.csv", index=False, date_format="%Y-%m-%d")
        exp2, bad2 = self_check(fx2, exp2); exp2.insert(0, "bo", f"thieu_ngay (xóa {ndel} dòng)")
        exp = pd.concat([exp, exp2], ignore_index=True); bad += bad2
        exp.to_csv(out / "R2_F01_fixture_expected.csv", index=False, date_format="%Y-%m-%d", float_format="%.12g")
        pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
        print(exp[["bo", "ca", "City", "Date", "cot_raw", "gia_tri_tiem", "ky_vong_truoc_log1p", "viet_tay_khop_tham_chieu"]].to_string(index=False))
        print(f"\n{len(FIX)} + {len(FIX_GAP)} ca, {len(exp)} hàng kỳ vọng; ô raw bị đổi ở bộ chính: {changed}; dòng bị xóa ở bộ thiếu ngày: {ndel}; "
              f"viết tay khớp bản tham chiếu: {int(exp.viet_tay_khop_tham_chieu.sum())}/{len(exp)}; hàng đổi khi cắt raw ở chính ngày đó: {bad}")
        sys.exit(0 if exp.viet_tay_khop_tham_chieu.all() and bad == 0 else 1)
    elif mode == "diff":
        ref = pd.read_csv(sys.argv[2], parse_dates=["Date"]); old = pd.read_csv(sys.argv[3], parse_dates=["Date"])
        keys = pd.read_csv(sys.argv[4], parse_dates=["Date"])[["City", "Date", "split"]]; out = Path(sys.argv[5])
        m = old.merge(ref, on=["City", "Date"], suffixes=("_cu", "_ref"), validate="1:1").merge(keys, on=["City", "Date"], validate="1:1")
        assert len(m) == len(old)
        feats = list(POLL.values()) + ["aqi_0", "aqi_1", "aqi_2", "aqi_wk"]
        rows, cells = [], []
        for f in feats:
            a, b = m[f + "_cu"], m[f + "_ref"]
            same = (a.isna() & b.isna()) | ((a - b).abs() <= 1e-9)
            kind = np.select([same, a.isna() & b.notna(), a.notna() & b.isna()], ["giống", "cũ trống → tham chiếu có số", "cũ có số → tham chiếu trống"], "khác giá trị")
            for (city, sp), g in m.assign(kind=kind).groupby(["City", "split"]):
                if (g.kind != "giống").any():
                    rows.append({"dac_trung": f, "City": city, "split": sp, "so_hang": len(g), "o_khac": int((g.kind != "giống").sum()),
                                 **{k: int((g.kind == k).sum()) for k in ("cũ trống → tham chiếu có số", "cũ có số → tham chiếu trống", "khác giá trị")},
                                 "chenh_lon_nhat (log)": float((g[f + "_cu"] - g[f + "_ref"]).abs().max())})
            d = m.loc[~same, ["City", "Date", "split"]].assign(dac_trung=f, gia_tri_cu=a[~same], gia_tri_tham_chieu=b[~same], loai=kind[~same.to_numpy()])
            cells.append(d)
        s = pd.DataFrame(rows); cells = pd.concat(cells, ignore_index=True)
        s.to_csv(out / "R2_C06_ref_vs_baseline_feature_diff_summary.csv", index=False)
        cells.sort_values(["dac_trung", "City", "Date"]).to_csv(out / "R2_C06_ref_vs_baseline_feature_diff_cells.csv", index=False, date_format="%Y-%m-%d", float_format="%.6g")
        pd.set_option("display.width", 250)
        print(s.groupby("dac_trung", sort=False)[["o_khac", "cũ trống → tham chiếu có số", "cũ có số → tham chiếu trống", "khác giá trị"]].sum().to_string())
        print("\ntheo split (ô):"); print(s.groupby(["dac_trung", "split"], sort=False).o_khac.sum().unstack(fill_value=0).to_string())
        print("\ntheo thành phố (ô):"); print(s.groupby(["dac_trung", "City"], sort=False).o_khac.sum().unstack(fill_value=0).to_string())
        print(f"\ntổng: {len(cells)} ô khác trên {len(m)} hàng × {len(feats)} đặc trưng; số hàng có ít nhất 1 ô khác: {len(cells.drop_duplicates(['City', 'Date']))}")
        print(cells.drop_duplicates(["City", "Date"]).groupby("split").size().to_string())
