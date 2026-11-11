"""V20–V24 [Q07] Mô hình dự đoán AQI ngày mai: tái lập split/fold, 3 baseline, Ridge L1–L4, HGB, cảnh báo, theo TP/mùa, holdout.
Dùng nguyên hàm của src/model_utils.py qua da_model.run_protocol (alpha, ngưỡng F2 chỉ chọn trên train/OOF). B=4000, seed 0.
Chạy: python v20_model.py
"""
from da_model import *

ds = M.build_dataset(verbose=False)
R = run_protocol(ds, hgb=True)
tr, te, lk, P, PL, bl = R["tr"], R["te"], R["lk"], R["pred_te"], R["pred_lk"], R["blocks"]

# ---------------- V20: split + fold
rows = [{"muc": "số cặp train/test/holdout", "expected": "5741/1947/975", "actual": f"{len(tr)}/{len(te)}/{len(lk)}"},
        {"muc": "ngày nặng (y>=201) train/test/holdout", "expected": "1432/389/18", "actual": f"{int(tr.y_poor.sum())}/{int(te.y_poor.sum())}/{int(lk.y_poor.sum())}"},
        {"muc": "ngày được dự đoán: train", "expected": "đến 30/06/2019", "actual": f"{tr.Date_target.min():%d/%m/%Y}–{tr.Date_target.max():%d/%m/%Y}"},
        {"muc": "ngày được dự đoán: test", "expected": "01/07/2019–29/02/2020", "actual": f"{te.Date_target.min():%d/%m/%Y}–{te.Date_target.max():%d/%m/%Y}"},
        {"muc": "ngày được dự đoán: holdout", "expected": "từ 01/03/2020", "actual": f"{lk.Date_target.min():%d/%m/%Y}–{lk.Date_target.max():%d/%m/%Y}"},
        {"muc": "dòng 'other' bị loại khỏi 3 tập", "expected": "0", "actual": str(int((ds.split == "other").sum()))},
        {"muc": "ngày đặc trưng (Date) lớn nhất của train < ngày được dự đoán nhỏ nhất của test", "expected": "True", "actual": str(bool(tr.Date.max() < te.Date_target.min()))},
        {"muc": "dòng test có đặc trưng lag (aqi_1, aqi_2, aqi_wk) lấy từ ngày thuộc train", "expected": "(thông tin)", "actual": f"aqi_0 của test ngày đầu = AQI 30/06/2019 (ngày được dự đoán cuối của train): {int((te.Date <= M.TRAIN_END).sum())} dòng"},
        {"muc": "alpha Ridge chọn bằng CV trong train", "expected": "(NB06 c10)", "actual": str(R["best_alpha"])},
        {"muc": "HGB L3 chọn bằng CV trong train", "expected": "(NB06 c10)", "actual": str(R["best_hgb"])},
        {"muc": "ngưỡng F2 chọn trên OOF train", "expected": "hôm nay 160, L3 166", "actual": str(R["thr"]) + f" | n_oof={R['n_oof']}, ngày nặng OOF={R['oof_heavy']}"}]
for r in rows: r["khop"] = (r["expected"] == r["actual"]) if not r["expected"].startswith(("(", "đến", "từ", "hôm")) else ""
folds = []
for k, (a, b) in enumerate(M.time_cv(len(tr)).split(tr)):
    A, Bv = tr.iloc[a], tr.iloc[b]
    folds.append({"fold": k + 1, "n_fit": len(a), "n_val": len(b), "fit_target_tu": A.Date_target.min().date(), "fit_target_den": A.Date_target.max().date(),
                  "val_target_tu": Bv.Date_target.min().date(), "val_target_den": Bv.Date_target.max().date(), "ngay_nang_val": int(Bv.y_poor.sum()),
                  "dong_bo_giua (GAP_ROWS)": int(b[0] - a[-1] - 1), "gap_lich_ngay (val_target_min − fit_target_max)": int((Bv.Date_target.min() - A.Date_target.max()).days),
                  "so_dong_trong_khoang_gap": int(b[0] - a[-1] - 1), "so_TP_co_dong_o_ngay_dau_val": int(Bv[Bv.Date_target == Bv.Date_target.min()].City.nunique()),
                  "val_Date_min − fit_target_max (ngày)": int((Bv.Date.min() - A.Date_target.max()).days),
                  "aqi_wk cua val dau tien nhin lui toi": (Bv.Date.min() - pd.Timedelta(days=7)).date(),
                  "nhan y cua fit bi dung lam feature cua val? (fit_target_max >= val_Date_min − 7)": bool(A.Date_target.max() >= Bv.Date.min() - pd.Timedelta(days=7))})
folds = pd.DataFrame(folds); save(pd.DataFrame(rows), "V20_model_split_checks.csv", index=False); save(folds, "V20_model_cv_folds.csv", index=False)
print(pd.DataFrame(rows).to_string()); print(folds.T.to_string())
# số dòng/ngày: mỗi ngày lịch có bao nhiêu TP có dòng trong train (gap 16 dòng = 2 ngày chỉ khi đủ 8 TP)
per_day = tr.groupby("Date_target").size()
print("train: số dòng mỗi ngày được dự đoán — phân bố:", per_day.value_counts().sort_index().to_dict())
split_city = ds.groupby(["City", "split"], observed=True).agg(n=("y", "size"), ngay_nang=("y_poor", "sum")).unstack("split"); save(split_city, "V20_model_split_by_city.csv")

# ---------------- V21: bảng điểm test + chênh lệch ghép cặp
exp = {"Trung bình theo thành phố": 64.47, "Trung vị cùng tháng (khí hậu)": 43.41, PERSIST: 23.47, "Ridge L1": 22.94, "Ridge L2": 20.92, "Ridge L3": 19.52, "Ridge L4": 19.08, "HGB L3": 18.03}
tt = R["test_tab"].copy(); tt["MAE_tac_gia"] = pd.Series(exp); tt["lech_MAE"] = (tt.MAE - tt.MAE_tac_gia).round(3); tt["giam_so_voi_hom_nay_%"] = (1 - tt.MAE / tt.loc[PERSIST, "MAE"]) * 100
save(tt.round(4), "V21_model_test_metrics.csv"); print(tt.round(2).to_string())
md = R["mdiff"].copy()
exp_d = {("Ridge L1", PERSIST): (-0.53, -1.19, 0.08), ("Ridge L2", "Ridge L1"): (-2.02, -3.06, -1.05), ("Ridge L3", "Ridge L2"): (-1.40, -1.93, -0.93), ("Ridge L3", PERSIST): (-3.95, -5.40, -2.56),
         ("Ridge L4", "Ridge L3"): (-0.43, -0.62, -0.26), ("HGB L3", "Ridge L3"): (-1.49, -2.21, -0.70)}
md["tac_gia"] = [str(exp_d.get((a, b))) for a, b in zip(md.A, md.B)]; md["ket_luan"] = np.where(md.hi < 0, "A tốt hơn B", np.where(md.lo > 0, "A kém hơn B", "chưa tách khỏi 0"))
md["n_khoi_14_ngay"] = len(np.unique(bl)); save(md.round(4), "V21_model_paired_mae_diff.csv", index=False); print(md.round(2).to_string())

# ---------------- V22: cảnh báo
al = R["alert_tab"].copy(); save(al.round(4), "V22_model_alerts_test.csv"); print(al.round(3).to_string())
y_te = te.y_poor.to_numpy(); flags = {"hôm nay@201": te.AQI.to_numpy() >= 201, "hôm nay@F2": te.AQI.to_numpy() >= R["thr"][PERSIST], "L3@201": P["Ridge L3"] >= 201, "L3@F2": P["Ridge L3"] >= R["thr"]["Ridge L3"]}
ad = []
for a, b in [("L3@201", "hôm nay@201"), ("L3@F2", "hôm nay@F2"), ("L3@F2", "hôm nay@201")]:
    for met in ("recall", "precision", "F1"):
        d, lo, hi = M.boot_alert_diff(bl, y_te, flags[a], flags[b], met); ad.append({"A": a, "B": b, "chi_so": met, "delta": d, "lo": lo, "hi": hi, "ket_luan": "A hơn B" if lo > 0 else "A kém B" if hi < 0 else "chưa tách khỏi 0"})
ad = pd.DataFrame(ad); save(ad.round(4), "V22_model_alert_paired_diff.csv", index=False); print(ad.round(3).to_string())

# ---------------- V23: theo thành phố / mùa / tháng
def seg_table(d, preds, key, lab):
    rows = []
    for g, ix in d.groupby(key, observed=True).indices.items():
        sub = d.iloc[ix]; y = sub.y.to_numpy(); r = {lab: g, "n": len(ix), "ngay_nang": int((y >= 201).sum()), "AQI_TB": y.mean()}
        for k, nm in [(PERSIST, "hom_nay"), ("Ridge L1", "L1"), ("Ridge L2", "L2"), ("Ridge L3", "L3"), ("HGB L3", "HGB")]:
            r[f"MAE_{nm}"] = M.mae(y, preds[k][ix]); 
        r["RMSE_hom_nay"], r["RMSE_L3"] = M.rmse(y, preds[PERSIST][ix]), M.rmse(y, preds["Ridge L3"][ix])
        r["MAE_L3/AQI_TB_%"] = r["MAE_L3"] / y.mean() * 100
        blk = M.calendar_blocks(sub.Date_target)
        for a, b, nm in [("Ridge L3", PERSIST, "L3−hom_nay"), ("Ridge L3", "Ridge L2", "L3−L2")]:
            dd, lo, hi = M.boot_mae_diff(blk, np.abs(y - preds[a][ix]), np.abs(y - preds[b][ix])); r[f"d_{nm}"], r[f"d_{nm}_lo"], r[f"d_{nm}_hi"] = dd, lo, hi
        r["giam_%"] = (1 - r["MAE_L3"] / r["MAE_hom_nay"]) * 100; r["bias_L3 (dự đoán − thực)"] = float((preds["Ridge L3"][ix] - y).mean())
        for nm, sc, th in [("hom_nay@201", sub.AQI.to_numpy(), 201), ("L3@201", preds["Ridge L3"][ix], 201), ("L3@F2", preds["Ridge L3"][ix], R["thr"]["Ridge L3"])]:
            m = M.alert_metrics(y >= 201, sc >= th); r[f"{nm}_TP/FP/FN"] = f"{m['TP']}/{m['FP']}/{m['FN']}"; r[f"{nm}_recall"], r[f"{nm}_precision"] = m["recall"], m["precision"]
        rows.append(r)
    return pd.DataFrame(rows).set_index(lab)
te2 = te.copy(); mo = te2.Date_target.dt.month
te2["mua"] = np.select([mo.isin([7, 8, 9]), mo.isin([10, 11]), mo.isin([12, 1, 2])], ["07–09 (gió mùa)", "10–11 (sau gió mùa)", "12–02 (mùa đông)"], "khác")
te2["thang"] = te2.Date_target.dt.strftime("%Y-%m"); te2["nhom"] = np.where(te2.y >= 201, "ngày nặng (y≥201)", "ngày còn lại")
byc = seg_table(te2, P, "City", "City").loc[M.CITIES]; bys = seg_table(te2, P, "mua", "mua"); bym = seg_table(te2, P, "thang", "thang"); byh = seg_table(te2, P, "nhom", "nhom")
save(byc.round(4), "V23_model_by_city.csv"); save(bys.round(4), "V23_model_by_season.csv"); save(bym.round(4), "V23_model_by_month.csv"); save(byh.round(4), "V23_model_by_heavy.csv")
cs = seg_table(te2.assign(cm=te2.City.astype(str) + " | " + te2.mua), P, "cm", "City|mua"); save(cs.round(4), "V23_model_by_city_season.csv")
show = ["n", "ngay_nang", "AQI_TB", "MAE_hom_nay", "MAE_L1", "MAE_L3", "MAE_HGB", "d_L3−hom_nay", "d_L3−hom_nay_lo", "d_L3−hom_nay_hi", "giam_%", "MAE_L3/AQI_TB_%", "bias_L3 (dự đoán − thực)", "hom_nay@201_TP/FP/FN", "L3@201_TP/FP/FN", "L3@F2_TP/FP/FN"]
for t in (byc, bys, byh): print(t[show].round(2).to_string())
print(bym[["n", "ngay_nang", "MAE_hom_nay", "MAE_L3", "d_L3−hom_nay", "d_L3−hom_nay_lo", "d_L3−hom_nay_hi"]].round(2).to_string())

# ---------------- V24: holdout (01/03–01/07/2020); 25/03 là mốc phong toả thực tế, đặt tên riêng
lt = R["lock_tab"].copy(); save(lt.round(4), "V24_model_holdout_metrics.csv"); print(lt.round(2).to_string())
lk2 = lk.copy(); lk2["giai_doan"] = np.where(lk2.Date_target < pd.Timestamp("2020-03-25"), "01/03–24/03/2020 (trước phong toả toàn quốc)", "25/03–01/07/2020 (từ ngày phong toả)")
hs = seg_table(lk2, PL, "giai_doan", "giai_doan"); save(hs.round(4), "V24_model_holdout_by_period.csv"); print(hs[show[:11]].round(2).to_string())
blk = M.calendar_blocks(lk.Date_target); yl = lk.y.to_numpy(); hd = []
for a, b in [("Ridge L1", PERSIST), ("Ridge L3", PERSIST), ("Ridge L3", "Ridge L2"), ("Ridge L3", "Ridge L1"), ("HGB L3", "Ridge L3")]:
    d, lo, hi = M.boot_mae_diff(blk, np.abs(yl - PL[a]), np.abs(yl - PL[b])); hd.append({"A": a, "B": b, "dMAE": d, "lo": lo, "hi": hi, "n_khoi": len(np.unique(blk))})
hd = pd.DataFrame(hd); save(hd.round(4), "V24_model_holdout_paired_diff.csv", index=False); print(hd.round(2).to_string())
m = M.alert_metrics(yl >= 201, lk.AQI.to_numpy() >= 201); m3 = M.alert_metrics(yl >= 201, PL["Ridge L3"] >= 201)
print("holdout cảnh báo @201: hôm nay", m, "| L3", m3)
# lưu dự đoán test để các script S dùng lại
te.assign(**{f"pred_{k}": v for k, v in P.items()})[["City", "Date", "Date_target", "AQI", "y"] + [f"pred_{k}" for k in P]].to_csv(out("V21_model_test_predictions.csv"), index=False)
