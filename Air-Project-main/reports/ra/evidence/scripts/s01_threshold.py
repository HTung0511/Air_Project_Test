"""S01 — Độ nhạy theo ngưỡng "ngày nặng": AQI ≥ 201 (tác giả, CPCB 'Poor') so với ≥ 151 (ngưỡng thay thế), kèm 101 và 301 để thấy xu hướng.
(1) EDA: tỉ lệ ngày nặng, thứ hạng, mùa, ratio PM2.5. (2) Cảnh báo: recall/precision của 'hôm nay' và Ridge L3 khi nhãn đổi ngưỡng.
Hồi quy (MAE) không phụ thuộc ngưỡng. Ngưỡng F2 vẫn chọn trên OOF của train. Chạy: python s01_threshold.py
"""
from da_model import *
from da_eda import *
base = pd.read_csv(CLEAN, parse_dates=["Date"]); ds = M.build_dataset(verbose=False)
er, ar = [], []
for thr in (101, 151, 201, 301):
    e, win, s_, e_ = prep(base, thr); m = eda_metrics(win); d = win.dropna(subset=["AQI"])
    r = {"nguong": thr, "n_ngay_co_AQI": m["n_ngay_co_AQI"], "n_ngay_nang": m["n_ngay_nang"], "pct_chung": m["n_ngay_nang"] / m["n_ngay_co_AQI"] * 100}
    for c in CITIES: r[f"{c}"] = f"{m[f'nang_{c}']}/{m[f'n_{c}']} = {m[f'pct_{c}']:.1f}%"; r[f"pct_{c}"] = m[f"pct_{c}"]
    r["thu_hang"] = m["thu_hang"]; r["TP_≥100_ngay_nang"] = m["TP_du_ngay_nang"]; r["ratio_PM25_trung_vi_TP"] = m["ratio_PM25_trung_vi_cac_TP"]
    for c in CITIES: r[f"ratio_PM25_{c}"] = m.get(f"ratio_PM25_{c}", np.nan)
    r["ratio_2_median_gop"] = m["ratio_cua_2_median_gop"]; r["pct_ngay_nang_T10-2"] = m["pct_ngay_nang_thang_10_2"]
    hm = d[d.poor].groupby("month").size().reindex(range(1, 13), fill_value=0); r["pct_ngay_nang_T11-12"] = hm[[11, 12]].sum() / hm.sum() * 100; r["thang_nhieu_ngay_nang_nhat"] = int(hm.idxmax())
    r["ti_le_Delhi/Jaipur"] = m["pct_Delhi"] / m["pct_Jaipur"]; r["ti_le_Delhi/Chennai"] = m["pct_Delhi"] / m["pct_Chennai"] if m["pct_Chennai"] else np.nan
    # bootstrap khối lịch 14 ngày: P(nhóm 3 TP cao nhất giữ nguyên), P(Delhi hạng 1)
    ci = {c: i for i, c in enumerate(CITIES)}; blk = ((d.Date - s_).dt.days // 14).to_numpy(); nb = blk.max() + 1; H = np.zeros((nb, 8)); N = np.zeros((nb, 8)); cx = d.City.map(ci).to_numpy()
    np.add.at(H, (blk, cx), d.poor.to_numpy(float)); np.add.at(N, (blk, cx), 1.0); rng = np.random.default_rng(0); idx = rng.integers(0, nb, (4000, nb)); cnt = np.zeros((4000, nb)); np.add.at(cnt, (np.arange(4000)[:, None], idx), 1)
    sh = (cnt @ H) / (cnt @ N) * 100; o = np.argsort(-sh, axis=1)
    r["P(3 TP cao nhất = Delhi,Lucknow,Gurugram)_%"] = np.mean([set(x[:3]) == {0, 1, 2} for x in o]) * 100; r["P(Delhi hạng 1)_%"] = np.mean(o[:, 0] == 0) * 100
    r["Delhi_CI95"] = f"[{np.percentile(sh[:, 0], 2.5):.1f}; {np.percentile(sh[:, 0], 97.5):.1f}]"
    er.append(r)
    R = run_protocol(ds, poor=thr, levels=("L1", "L2", "L3"), alphas={"L1": 10, "L2": 0.1, "L3": 30})     # alpha chọn bằng MAE-CV nên không phụ thuộc ngưỡng
    al = R["alert_tab"]; te = R["te"]; y = te.y_poor.to_numpy(); bl = R["blocks"]
    for k in al.index:
        ar.append({"nguong_nhan": thr, "quy_tac": k, "ngay_nang_test": int(y.sum()), "ty_le_nen_%": y.mean() * 100, "ngay_nang_train": int(R["tr"].y_poor.sum()), "ngay_nang_holdout": int(R["lk"].y_poor.sum()), **al.loc[k].to_dict()})
    for a_, b_ in ((f"Ridge L3 @{thr}", f"{PERSIST} @{thr}"), ("Ridge L3 @F2", f"{PERSIST} @F2")):
        sc = lambda k: (te.AQI.to_numpy() if k.startswith(PERSIST) else R["pred_te"]["Ridge L3"]) >= al.loc[k, "nguong"]
        for met in ("recall", "precision", "F1"):
            dlt, lo, hi = M.boot_alert_diff(bl, y, sc(a_), sc(b_), met); ar.append({"nguong_nhan": thr, "quy_tac": f"Δ {met}: {a_} − {b_}", "delta": dlt, "lo": lo, "hi": hi, "ket_luan": "A hơn B" if lo > 0 else "A kém B" if hi < 0 else "chưa tách khỏi 0"})
E = pd.DataFrame(er).set_index("nguong"); A = pd.DataFrame(ar); save(E.round(3), "S01_threshold_eda.csv"); save(A.round(4), "S01_threshold_alerts.csv", index=False)
pd.set_option("display.width", 300); print(E.T.to_string()); print(A[A.delta.isna()].drop(columns=["delta", "lo", "hi", "ket_luan"]).round(3).to_string()); print(A[A.delta.notna()][["nguong_nhan", "quy_tac", "delta", "lo", "hi", "ket_luan"]].round(3).to_string())
