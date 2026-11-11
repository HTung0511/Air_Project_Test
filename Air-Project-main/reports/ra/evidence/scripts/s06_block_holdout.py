"""S06 — (a) Độ dài khối bootstrap 7/14/28 ngày cho các hiệu MAE chính (test và holdout); (b) cảnh báo trên holdout ở ngưỡng 151 (94 ngày nặng thay vì 18).
Giao thức định trước: mô hình, alpha và ngưỡng F2 giữ nguyên như NB06 (chọn trên train/OOF); B=4000; seed 0; khối lịch chung giữa các TP.
"""
from da_model import *
ds = M.build_dataset(verbose=False); rows = []
R = run_protocol(ds, poor=201, levels=("L1", "L2", "L3"), alphas={"L1": 10, "L2": 0.1, "L3": 30}, thresholds=False)
for nm, part, pred in (("test", R["te"], R["pred_te"]), ("holdout", R["lk"], R["pred_lk"])):
    y = part.y.to_numpy(); ep = np.abs(y - part.AQI.to_numpy()); e = {k: np.abs(y - pred[f"Ridge {k}"]) for k in ("L1", "L2", "L3")}
    for days in (7, 14, 28):
        bl = M.calendar_blocks(part.Date_target, days=days)
        for lab, a, b in (("L3 − hôm nay", e["L3"], ep), ("L3 − L2 (thêm thời tiết)", e["L3"], e["L2"]), ("L2 − L1 (thêm chất ô nhiễm)", e["L2"], e["L1"]), ("L1 − hôm nay", e["L1"], ep)):
            d, lo, hi = M.boot_mae_diff(bl, a, b); rows.append({"tap": nm, "khoi_ngay": days, "so_khoi": len(np.unique(bl)), "so_sanh": lab, "delta_MAE": d, "lo": lo, "hi": hi, "ket_luan": "tách khỏi 0" if (lo > 0 or hi < 0) else "chưa tách khỏi 0"})
B = pd.DataFrame(rows); save(B.round(3), "S06_block_length_model.csv", index=False); pd.set_option("display.width", 250); print(B.round(2).to_string())
rows = []
for thr in (151, 201):
    R = run_protocol(ds, poor=thr, levels=("L3",), alphas={"L3": 30})
    lk = R["lk"]; y = (lk.y >= thr).to_numpy(); bl = M.calendar_blocks(lk.Date_target); f2 = R["thr"]
    for k, sc in ((PERSIST, lk.AQI.to_numpy()), ("Ridge L3", R["pred_lk"]["Ridge L3"])):
        for tn, t in ((f"@{thr}", thr), ("@F2", f2[k])):
            m = M.alert_metrics(y, sc >= t); rows.append({"nguong_nhan": thr, "quy_tac": f"{k} {tn}", "nguong": t, "n_holdout": len(y), "ngay_nang_holdout": int(y.sum()), **{q: m[q] for q in ("recall", "precision", "F1", "TP", "FP", "FN", "TN")}})
    for tn in (f"@{thr}", "@F2"):
        ta = thr if tn != "@F2" else f2["Ridge L3"]; tb = thr if tn != "@F2" else f2[PERSIST]
        for met in ("recall", "precision", "F1"):
            d, lo, hi = M.boot_alert_diff(bl, y, R["pred_lk"]["Ridge L3"] >= ta, lk.AQI.to_numpy() >= tb, met); rows.append({"nguong_nhan": thr, "quy_tac": f"Δ {met}: L3 {tn} − hôm nay {tn}", "delta": d, "lo": lo, "hi": hi})
H = pd.DataFrame(rows); save(H.round(4), "S06_holdout_alerts_151_201.csv", index=False); print(H.round(3).to_string())
