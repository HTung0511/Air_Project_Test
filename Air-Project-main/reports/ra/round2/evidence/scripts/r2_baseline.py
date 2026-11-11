"""DA vòng 2 — dựng BASELINE (mã cũ) cho so sánh cùng mẫu: bảng mẫu, đặc trưng, alpha, ngưỡng, metric, dự đoán.

Dùng: python r2_baseline.py <root Air-Project-main của snapshot baseline> <thư mục out> [thư mục bằng chứng v1.1 để đối chiếu]
Đọc model_utils.build_dataset() của snapshot baseline (chỉ để lấy bảng đặc trưng cũ), rồi chấm bằng r2_protocol (độc lập với src/).
"""
import sys, warnings
from pathlib import Path
sys.dont_write_bytecode = True
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

root, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
v11 = Path(sys.argv[3]) if len(sys.argv) > 3 else None
sys.path.insert(0, str(root / "src")); sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_utils as M                                   # mã baseline
import r2_protocol as P

ds = M.build_dataset(verbose=False)
LV = {k: list(M.LEVELS[k]) for k in ("L1", "L2", "L3", "L4")}
feats = sorted(set(sum(LV.values(), [])), key=lambda f: (LV["L4"]).index(f))
ds = ds.assign(City=ds.City.astype(str))
R = P.run(ds, LV, "baseline", hgb_level="L3")
d = P.prepare(ds)
d[["City", "Date", "Date_target", "split", "AQI", "y"]].to_csv(out / "R2_B03_baseline_cohort_keys.csv", index=False, date_format="%Y-%m-%d")
d[["City", "Date"] + [f for f in feats if f in LV["L3"]]].to_csv(out / "R2_B03_baseline_features_L3.csv.gz", index=False, date_format="%Y-%m-%d", float_format="%.12g")
for k in ("split", "alpha", "metrics", "alerts", "paired_mae", "paired_alert"):
    R[k].to_csv(out / f"R2_B04_baseline_{k}.csv", index=False, date_format="%Y-%m-%d", float_format="%.6f")
R["predictions"].to_csv(out / "R2_B04_baseline_predictions.csv", index=False, date_format="%Y-%m-%d", float_format="%.6f")
pd.set_option("display.width", 220)
print(R["split"].to_string(index=False)); print(R["alpha"][["mo_hinh", "alpha", "nguong_F2", "n_OOF"]].to_string(index=False))
print(R["metrics"].round(4).to_string(index=False))

# ---- đối chiếu với bằng chứng v1.1 (vòng 1): cùng mã, cùng dữ liệu, bộ máy chấm khác -> phải trùng trong sai số làm tròn 4 chữ số
if v11:
    rows = []
    def chk(name, new, old, tol):
        rows.append({"doi_tuong": name, "gia_tri_vong2": new, "gia_tri_v1.1": old, "lech_tuyet_doi": abs(float(new) - float(old)), "dung_sai": tol,
                     "khop": bool(abs(float(new) - float(old)) <= tol)})
    m = R["metrics"]; al = R["alerts"]; pm = R["paired_mae"]
    for fn, tap in (("V21_model_test_metrics.csv", "test"), ("V24_model_holdout_metrics.csv", "holdout")):
        o = pd.read_csv(v11 / fn, index_col=0)
        for k in o.index:
            for c in ("n", "ngay_nang", "MAE", "RMSE", "R2", "MAE_ngay_nang", "MAE_con_lai"):
                chk(f"{tap} | {k} | {c}", m[(m.tap == tap) & (m.mo_hinh == k)][c].iloc[0], o.loc[k, c], 0 if c in ("n", "ngay_nang") else 5.01e-5)
    o = pd.read_csv(v11 / "V22_model_alerts_test.csv", index_col=0)
    for k in o.index:
        name, lab = k.rsplit(" @", 1)
        if name == "Ridge L4" and "Ridge L4" not in set(al.mo_hinh): continue
        r = al[(al.tap == "test") & (al.mo_hinh == name) & (al.loai_nguong == lab)].iloc[0]
        for c in ("nguong", "TP", "FP", "FN", "TN"):
            chk(f"test | {k} | {c}", r[c], o.loc[k, c], 0)
        for c in ("recall", "precision", "F1"):
            chk(f"test | {k} | {c}", r[c], o.loc[k, c], 5.01e-5)
    o = pd.read_csv(v11 / "V21_model_paired_mae_diff.csv")
    for _, r0 in o.iterrows():
        r = pm[(pm.tap == "test") & (pm.khoi_ngay == 14) & (pm.A == r0.A) & (pm.B == r0.B)]
        if len(r):
            for c in ("dMAE", "lo", "hi"):
                chk(f"test | khối 14 | {r0.A} − {r0.B} | {c}", r[c].iloc[0], r0[c], 5.01e-5)
    o = pd.read_csv(v11 / "V24_model_holdout_paired_diff.csv")
    for _, r0 in o.iterrows():
        r = pm[(pm.tap == "holdout") & (pm.khoi_ngay == 14) & (pm.A == r0.A) & (pm.B == r0.B)]
        if len(r):
            for c in ("dMAE", "lo", "hi"):
                chk(f"holdout | khối 14 | {r0.A} − {r0.B} | {c}", r[c].iloc[0], r0[c], 5.01e-5)
    o = pd.read_csv(v11 / "S06_block_length_model.csv")
    nm = {"L3 − hôm nay": ("Ridge L3", P.PERSIST), "L3 − L2 (thêm thời tiết)": ("Ridge L3", "Ridge L2"), "L2 − L1 (thêm chất ô nhiễm)": ("Ridge L2", "Ridge L1"), "L1 − hôm nay": ("Ridge L1", P.PERSIST)}
    for _, r0 in o.iterrows():
        a, b = nm[r0.so_sanh]
        r = pm[(pm.tap == r0.tap) & (pm.khoi_ngay == r0.khoi_ngay) & (pm.A == a) & (pm.B == b)].iloc[0]
        chk(f"{r0.tap} | khối {r0.khoi_ngay} | {a} − {b} | so_khoi", r.so_khoi, r0.so_khoi, 0)
        for c0, c in (("delta_MAE", "dMAE"), ("lo", "lo"), ("hi", "hi")):
            chk(f"{r0.tap} | khối {r0.khoi_ngay} | {a} − {b} | {c}", r[c], r0[c0], 5.01e-4)
    o = pd.read_csv(v11 / "V22_model_alert_paired_diff.csv"); pa = R["paired_alert"]
    for _, r0 in o.iterrows():
        lab = {"L3@201": "201", "L3@F2": "F2"}[r0.A]
        if (r0.A, r0.B) not in (("L3@201", "hôm nay@201"), ("L3@F2", "hôm nay@F2")): continue
        r = pa[(pa.khoi_ngay == 14) & (pa.A == f"Ridge L3 @{lab}") & (pa.chi_so == r0.chi_so)].iloc[0]
        for c in ("delta", "lo", "hi"):
            chk(f"test | khối 14 | {r0.A} − {r0.B} | {r0.chi_so} | {c}", r[c], r0[c], 5.01e-5)
    c = pd.DataFrame(rows); c.to_csv(out / "R2_B05_baseline_vs_v11.csv", index=False, float_format="%.6f")
    print(f"\nĐối chiếu với v1.1: {int(c.khop.sum())}/{len(c)} giá trị khớp; lệch lớn nhất {c.lech_tuyet_doi.max():.2e}")
    if not c.khop.all(): print(c[~c.khop].to_string(index=False))
