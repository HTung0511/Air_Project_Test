"""V07 [Q02] Walk-forward chính xác: với MỖI ngày t trong khoảng chung, cắt RAW ở t, chạy lại đúng pipeline làm sạch của tác giả,
rồi tính đặc trưng của ngày t bằng model_utils.make_features(as_of=t). Đây là "đặc trưng thời gian thực": thứ mà hệ thống
thực sự có ở cuối ngày t. So với đặc trưng baseline (làm sạch trên TOÀN chuỗi rồi mới cắt) => định lượng leakage raw→clean.

Chạy (2 tiến trình song song):  python v02b_walkforward.py 0 2  &  python v02b_walkforward.py 1 2
Gộp + so sánh:                  python v02b_walkforward.py merge
"""
from da_clean import *
import model_utils as M

L3 = M.LEVELS["L3"]; START, END = pd.Timestamp("2017-06-14"), pd.Timestamp("2020-07-01")
OUT = SCRATCH / "walkforward"; OUT.mkdir(exist_ok=True)

if sys.argv[1] != "merge":
    part, nparts = int(sys.argv[1]), int(sys.argv[2])
    raw8 = load_raw(); days = pd.date_range(START, END)
    feats, flags = [], []
    for i, t in enumerate(days):
        if i % nparts != part: continue
        cc, ev = clean_all(raw8[raw8.Date <= t], fast=True)
        f = features_from(cc[cc.Date >= t - pd.Timedelta(days=60)], as_of=t, tag=f"wf{part}")
        f = f[f.Date == t][["City", "Date", "AQI"] + L3].copy()
        last = cc[cc.Date == t].set_index("City")
        f["suspect_at_t"] = f.City.map(last.suspect_sensor_error.astype(bool)).to_numpy()
        feats.append(f)
        if len(ev):
            e = ev[ev.action == "đặt NaN"][["city", "date", "column", "value_original", "suggestion"]].copy(); e["as_of"] = t; flags.append(e)
        if i % 100 == part: print(t.date(), flush=True)
    pd.concat(feats).to_csv(OUT / f"feat_{part}.csv", index=False)
    pd.concat(flags).to_csv(OUT / f"flags_{part}.csv", index=False)
    print("DONE", part)
    sys.exit(0)

# ------------------------------------------------------------------ merge + so sánh
rt = pd.concat([pd.read_csv(p, parse_dates=["Date"]) for p in sorted(OUT.glob("feat_*.csv"))]).sort_values(["City", "Date"]).reset_index(drop=True)
fl = pd.concat([pd.read_csv(p, parse_dates=["date", "as_of"]) for p in sorted(OUT.glob("flags_*.csv"))])
assert rt.Date.nunique() == 1114, rt.Date.nunique()
full = M.make_features()
full = full[(full.Date >= START) & (full.Date <= END)][["City", "Date", "AQI", "y", "split", "Date_target"] + L3]
m = full.merge(rt, on=["City", "Date"], suffixes=("", "_rt"), how="left", validate="1:1")
assert m.aqi_0_rt.notna().sum() > 0 and len(m) == 8912
rows = []
for c in ["AQI"] + L3:
    e = eqnan(m[c], m[c + "_rt"], 1e-9)
    a, b = m[c], m[c + "_rt"]
    rows.append({"feature": c, "n_dong": len(m), "o_khac": int((~e).sum()), "pct": round((~e).mean() * 100, 3),
                 "baseline_co_gia_tri_RT_NaN": int((a.notna() & b.isna()).sum()), "baseline_NaN_RT_co_gia_tri": int((a.isna() & b.notna()).sum()),
                 "ca_hai_co_gia_tri_nhung_khac": int((a.notna() & b.notna() & ~e.to_numpy()).sum()),
                 "max_abs_diff": float((a - b).abs().max())})
cmp = pd.DataFrame(rows); save(cmp, "V07_walkforward_feature_diff.csv", index=False); print(cmp.to_string())
anyd = pd.concat([~eqnan(m[c], m[c + "_rt"], 1e-9) for c in L3], axis=1).any(axis=1).to_numpy()
keep = (m.AQI.notna() & m.y.notna()).to_numpy()
print("dòng (TP, ngày) có ≥1 đặc trưng L3 khác:", int(anyd.sum()), "/", len(m), "| trong mẫu mô hình baseline:", int((anyd & keep).sum()), "/", int(keep.sum()))
print(pd.crosstab(m.split[keep], anyd[keep]))
det = []
for c in ["AQI"] + L3:
    e = ~eqnan(m[c], m[c + "_rt"], 1e-9).to_numpy()
    for i in np.flatnonzero(e):
        det.append({"City": m.City[i], "Date": m.Date[i].date(), "split": m.split[i], "trong_mau_mo_hinh": bool(keep[i]), "feature": c, "baseline": m[c][i], "thoi_gian_thuc": m[c + "_rt"][i]})
det = pd.DataFrame(det); save(det, "V07_walkforward_feature_diff_cells.csv", index=False)
print(det.groupby(["feature", "split"]).size().unstack(fill_value=0))

# ---- quyết định nghi lỗi theo thời gian thực so với cuối cùng
base = pd.read_csv(CLEAN, parse_dates=["Date"]); sp = pd.read_csv(ROOT / "reports" / "suspect_points_8cities.csv", parse_dates=["date"])
final = set(zip(sp[sp.action == "đặt NaN"].city, sp[sp.action == "đặt NaN"].date, sp[sp.action == "đặt NaN"].column))
g = fl.groupby(["city", "date", "column"]).agg(value_original=("value_original", "first"), lan_dau_bi_co=("as_of", "min"), lan_cuoi_bi_co=("as_of", "max"), so_ngay_bi_co=("as_of", "size")).reset_index()
g["trong_khoang_chung"] = g.date >= START
g["la_nghi_loi_cuoi_cung"] = [(a, b, c) in final for a, b, c in zip(g.city, g.date, g.column)]
g["tre_ngay_tu_su_kien_den_khi_bi_co"] = (g.lan_dau_bi_co - g.date).dt.days
g["so_ngay_co_the_bi_co"] = (END - g[["date"]].assign(s=START).max(axis=1)).dt.days + 1
g["loai"] = np.where(g.la_nghi_loi_cuoi_cung, "cuối cùng vẫn nghi lỗi", "MA: thời gian thực từng xoá, bản cuối GIỮ")
save(g.sort_values(["city", "date", "column"]), "V07_walkforward_suspect_decisions.csv", index=False)
print(g[g.trong_khoang_chung].to_string())
print(g.groupby(["trong_khoang_chung", "loai"]).size())
rt.to_csv(out("V07_walkforward_realtime_features.csv.gz"), index=False, compression="gzip")
