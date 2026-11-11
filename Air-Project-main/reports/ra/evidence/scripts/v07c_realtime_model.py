"""V07 (phần c) [Q02] Biến thể 'thời gian thực' (causal) RIÊNG: thay đặc trưng L3 + AQI(t) của mọi dòng bằng bản tính từ raw cắt ở t
(V07_walkforward_realtime_features.csv.gz), giữ nhãn y của baseline; chạy lại đúng giao thức NB06 và so metric.
Không sửa baseline. Chạy sau `v02b_walkforward.py merge`.
"""
from da_model import *
L3 = M.LEVELS["L3"]
rt = pd.read_csv(out("V07_walkforward_realtime_features.csv.gz"), parse_dates=["Date"])
full = M.make_features()
_, _, start, end = __import__("eda_utils").load(verbose=False)
m = full.merge(rt[["City", "Date", "AQI"] + L3].rename(columns={c: c + "_rt" for c in ["AQI"] + L3}), on=["City", "Date"], how="left", validate="1:1")
var = m.copy()
for c in ["AQI"] + L3: var[c] = np.where(var[c + "_rt"].notna() | (var.Date >= start), var[c + "_rt"], var[c])
var["today_poor"] = var.AQI >= 201
def finish(d):
    keep = d.AQI.notna() & d.y.notna() & (d.Date >= start) & (d.Date_target <= end)
    o = d[keep].sort_values(["Date_target", "City"]).reset_index(drop=True); o["City"] = pd.Categorical(o.City, categories=M.CITIES, ordered=True); return o
ds_b, ds_v = finish(full), finish(var)
rows = []
for nm, d in (("baseline (làm sạch toàn chuỗi)", ds_b), ("thời gian thực (raw cắt ở t)", ds_v)):
    R = run_protocol(d, levels=("L1", "L2", "L3"), thresholds=True)
    tt, md, al = R["test_tab"], R["mdiff"].set_index(["A", "B"]), R["alert_tab"]
    r = {"bien_the": nm, "n_train": len(R["tr"]), "n_test": len(R["te"]), "n_holdout": len(R["lk"]), "alpha": str(R["best_alpha"]), "nguong_F2": str(R["thr"])}
    for k, s in [(PERSIST, "hom_nay"), ("Ridge L1", "L1"), ("Ridge L2", "L2"), ("Ridge L3", "L3")]: r[f"MAE_test_{s}"] = tt.loc[k, "MAE"]; r[f"MAE_holdout_{s}"] = R["lock_tab"].loc[k, "MAE"]
    for (a, b), s in [(("Ridge L3", PERSIST), "L3−hom_nay"), (("Ridge L3", "Ridge L2"), "L3−L2")]: r[f"d_{s}"] = f"{md.loc[(a, b), 'dMAE']:.3f} [{md.loc[(a, b), 'lo']:.2f}; {md.loc[(a, b), 'hi']:.2f}]"
    for k in ("Ngày mai = hôm nay @201", "Ridge L3 @201", "Ridge L3 @F2"): r[f"{k} recall/precision"] = f"{al.loc[k, 'recall']:.4f}/{al.loc[k, 'precision']:.4f}"
    rows.append(r)
res = pd.DataFrame(rows).set_index("bien_the"); save(res, "V07_realtime_variant_metrics.csv"); print(res.T.to_string())
kb, kv = set(zip(ds_b.City.astype(str), ds_b.Date)), set(zip(ds_v.City.astype(str), ds_v.Date))
print("dòng chỉ có ở baseline:", sorted(kb - kv)[:10], "| chỉ có ở thời gian thực:", sorted(kv - kb)[:10])
