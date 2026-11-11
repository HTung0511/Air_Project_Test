"""S02–S04 — Kết luận có bị chi phối bởi một thành phố / một mùa không?
S02: vì sao mô hình sai nhiều/ít theo TP (liên hệ với mức AQI, độ biến động ngày-qua-ngày, tỉ lệ ngày nặng).
S03: bỏ lần lượt từng TP (leave-one-city-out) cho mô hình và cho số EDA gộp; huấn luyện 7 TP → thử trên TP bị bỏ.
S04: bỏ lần lượt từng mùa; thứ hạng TP trong từng mùa; tương quan độ ẩm theo mùa.
Giao thức định trước: alpha giữ như NB06 (L1 10, L2 0,1, L3 30 — đã chọn bằng CV train), B=4000, khối lịch 14 ngày, seed 0. Không tune trên test.
"""
from da_model import *
from da_eda import *
import corr_utils as C
ALPHA = {"L1": 10, "L2": 0.1, "L3": 30}
ds = M.build_dataset(verbose=False); tr, te, lk = splits(ds); base = pd.read_csv(CLEAN, parse_dates=["Date"]); e, win, START, END = prep(base); d = win.dropna(subset=["AQI"])
pt = pd.read_csv(out("V21_model_test_predictions.csv"), parse_dates=["Date", "Date_target"])

# ---------- S02: đặc điểm chuỗi theo TP và sai số
rows = []
for c in CITIES:
    x = pt[pt.City == c]; t = tr[tr.City == c]; dy = (x.y - x.AQI)
    r = {"City": c, "n_test": len(x), "AQI_TB_test": x.y.mean(), "AQI_std_test": x.y.std(), "ngay_nang_test": int((x.y >= 201).sum()), "|ΔAQI ngày-qua-ngày| TB (= MAE hôm nay)": dy.abs().mean(), "|ΔAQI| p90": dy.abs().quantile(.9),
         "tu_tuong_quan_bac1_AQI": x.y.corr(x.AQI), "MAE_L3": (x.y - x["pred_Ridge L3"]).abs().mean(), "MAE_HGB": (x.y - x["pred_HGB L3"]).abs().mean(), "MAE_L3/AQI_TB_%": (x.y - x["pred_Ridge L3"]).abs().mean() / x.y.mean() * 100,
         "MAPE_L3_%": ((x.y - x["pred_Ridge L3"]).abs() / x.y).mean() * 100, "MAPE_hom_nay_%": (dy.abs() / x.y).mean() * 100, "giam_MAE_%": (1 - (x.y - x["pred_Ridge L3"]).abs().mean() / dy.abs().mean()) * 100,
         "R2_L3_trong_TP": M.r2(x.y, x["pred_Ridge L3"]), "R2_hom_nay_trong_TP": M.r2(x.y, x.AQI), "bias_L3": (x["pred_Ridge L3"] - x.y).mean(), "bias_L3_ngay_nang": (x["pred_Ridge L3"] - x.y)[x.y >= 201].mean() if (x.y >= 201).any() else np.nan,
         "n_train": len(t), "ngay_nang_train": int(t.y_poor.sum()), "PM25_thieu_train_%": t.pm25_0.isna().mean() * 100, "sai_so_lon_nhat_L3": (x.y - x["pred_Ridge L3"]).abs().max(),
         "% MAE L3 đến từ 10% ngày sai nhất": (x.y - x["pred_Ridge L3"]).abs().nlargest(max(1, len(x) // 10)).sum() / (x.y - x["pred_Ridge L3"]).abs().sum() * 100}
    rows.append(r)
S2 = pd.DataFrame(rows).set_index("City"); save(S2.round(3), "S02_city_error_profile.csv")
print(S2.round(2).T.to_string())
cc = S2[["AQI_TB_test", "AQI_std_test", "|ΔAQI ngày-qua-ngày| TB (= MAE hôm nay)", "ngay_nang_test", "MAE_L3", "giam_MAE_%", "MAE_L3/AQI_TB_%"]].corr(method="spearman")
save(cc.round(3), "S02_city_error_rank_correlation.csv"); print("Spearman giữa 8 TP (n=8, chỉ mô tả):\n", cc.round(2).to_string())
contrib = (pt.assign(e3=(pt.y - pt["pred_Ridge L3"]).abs(), ep=(pt.y - pt.AQI).abs()).groupby("City")[["e3", "ep"]].sum().reindex(CITIES)); contrib["gain"] = contrib.ep - contrib.e3
contrib["% tổng mức giảm sai số đến từ TP"] = contrib.gain / contrib.gain.sum() * 100; contrib["% tổng sai số L3"] = contrib.e3 / contrib.e3.sum() * 100; save(contrib.round(2), "S02_city_contribution.csv"); print(contrib.round(1).to_string())

# ---------- S03a: mô hình — bỏ từng TP khỏi cả train và test
def fit3(trx, tex):
    p = {lv: fit_predict(trx, tex, M.LEVELS[lv], ALPHA[lv]) for lv in ("L1", "L2", "L3")}; y = tex.y.to_numpy(); bl = M.calendar_blocks(tex.Date_target); ep = np.abs(y - tex.AQI.to_numpy())
    r = {"n_train": len(trx), "n_test": len(tex), "ngay_nang_test": int((y >= 201).sum()), "MAE_hom_nay": ep.mean(), "MAE_L1": np.abs(y - p["L1"]).mean(), "MAE_L2": np.abs(y - p["L2"]).mean(), "MAE_L3": np.abs(y - p["L3"]).mean()}
    for a, b, nm in (("L3", None, "L3−hom_nay"), ("L3", "L2", "L3−L2 (thời tiết)"), ("L2", "L1", "L2−L1 (chất ô nhiễm)")):
        dd, lo, hi = M.boot_mae_diff(bl, np.abs(y - p[a]), ep if b is None else np.abs(y - p[b])); r[f"d_{nm}"], r[f"lo_{nm}"], r[f"hi_{nm}"] = dd, lo, hi
    yb = y >= 201
    for nm, sc in (("hom_nay", tex.AQI.to_numpy()), ("L3", p["L3"])):
        m = M.alert_metrics(yb, sc >= 201); r[f"recall_{nm}@201"], r[f"precision_{nm}@201"] = m["recall"], m["precision"]
    return r, p
rows = [{"bien_the": "đủ 8 TP (gốc)", **fit3(tr, te)[0]}]
for c in CITIES:
    rows.append({"bien_the": f"bỏ {c}", **fit3(tr[tr.City != c].reset_index(drop=True), te[te.City != c].reset_index(drop=True))[0]})
for nm, cs in (("bỏ Delhi+Gurugram+Lucknow (3 TP nặng)", ["Delhi", "Gurugram", "Lucknow"]), ("chỉ Delhi+Gurugram+Lucknow", [c for c in CITIES if c not in ("Delhi", "Gurugram", "Lucknow")]),
               ("chỉ 3 TP phía nam (Bengaluru, Chennai, Hyderabad)", [c for c in CITIES if c not in ("Bengaluru", "Chennai", "Hyderabad")])):
    rows.append({"bien_the": nm, **fit3(tr[~tr.City.isin(cs)].reset_index(drop=True), te[~te.City.isin(cs)].reset_index(drop=True))[0]})
S3 = pd.DataFrame(rows).set_index("bien_the"); save(S3.round(4), "S03_leave_one_city_out_model.csv"); print(S3.round(2).to_string())
# ---------- S03b: huấn luyện 7 TP → dự đoán TP bị bỏ (chuyển giao). One-hot gặp TP lạ = toàn 0 = mức tham chiếu (Delhi; nếu bỏ Delhi thì không có hệ số Delhi riêng)
rows = []
for c in CITIES:
    trx, tex = tr[tr.City != c].reset_index(drop=True), te[te.City == c].reset_index(drop=True); y = tex.y.to_numpy()
    p_out = fit_predict(trx, tex, M.LEVELS["L3"], ALPHA["L3"]); p_in = pt[pt.City == c]["pred_Ridge L3"].to_numpy(); bl = M.calendar_blocks(tex.Date_target)
    dd, lo, hi = M.boot_mae_diff(bl, np.abs(y - p_out), np.abs(y - tex.AQI.to_numpy()))
    rows.append({"City": c, "n_test": len(tex), "MAE_hom_nay": np.abs(y - tex.AQI.to_numpy()).mean(), "MAE_L3 (TP có trong train)": np.abs(y - p_in).mean(), "MAE_L3 (TP KHÔNG có trong train)": np.abs(y - p_out).mean(),
                 "d (không có trong train) − hôm nay": dd, "lo": lo, "hi": hi, "bias (không có trong train)": (p_out - y).mean()})
S3b = pd.DataFrame(rows).set_index("City"); save(S3b.round(4), "S03_train_without_city_predict_city.csv"); print(S3b.round(2).to_string())
# ---------- S03c: EDA gộp — bỏ từng TP
rows = [{"bien_the": "đủ 8 TP", **{k: v for k, v in eda_metrics(win).items() if k in ("n_ngay_co_AQI", "n_ngay_nang", "ratio_PM25_trung_vi_cac_TP", "ratio_cua_2_median_gop", "spearman_PM2.5", "spearman_NO2", "spearman_CO", "pct_ngay_nang_thang_10_2", "TP_du_ngay_nang")}}]
for c in CITIES: rows.append({"bien_the": f"bỏ {c}", **{k: v for k, v in eda_metrics(win[win.City != c]).items() if k in rows[0]}})
S3c = pd.DataFrame(rows).set_index("bien_the"); S3c["% ngày nặng của 8 TP nằm ở TP bị bỏ"] = [np.nan] + [d[(d.City == c)].poor.sum() / d.poor.sum() * 100 for c in CITIES]; save(S3c.round(4), "S03_leave_one_city_out_eda.csv"); print(S3c.round(3).to_string())

# ---------- S04a: mô hình — bỏ từng mùa khỏi TEST (mô hình giữ nguyên) và khỏi TRAIN (đánh giá trên test đầy đủ)
season = lambda s: np.select([s.dt.month.isin([12, 1, 2]), s.dt.month.isin([3, 4, 5]), s.dt.month.isin([6, 7, 8, 9])], ["Đông (12–2)", "Hè (3–5)", "Mưa (6–9)"], "Sau mưa (10–11)")
te_s, tr_s = season(te.Date_target), season(tr.Date_target); rows = []; base_p = fit3(tr, te)[1]
for sname in ["Đông (12–2)", "Hè (3–5)", "Mưa (6–9)", "Sau mưa (10–11)"]:
    mk = te_s != sname
    if mk.sum() < len(te):
        tex = te[mk].reset_index(drop=True); y = tex.y.to_numpy(); bl = M.calendar_blocks(tex.Date_target); p3, pp = base_p["L3"][mk], tex.AQI.to_numpy(); dd, lo, hi = M.boot_mae_diff(bl, np.abs(y - p3), np.abs(y - pp)); d2, l2, h2 = M.boot_mae_diff(bl, np.abs(y - p3), np.abs(y - base_p["L2"][mk]))
        rows.append({"bien_the": f"TEST bỏ mùa {sname}", "n_train": len(tr), "n_test": len(tex), "ngay_nang_test": int((y >= 201).sum()), "MAE_hom_nay": np.abs(y - pp).mean(), "MAE_L3": np.abs(y - p3).mean(), "d_L3−hom_nay": dd, "lo": lo, "hi": hi, "d_L3−L2": d2, "lo2": l2, "hi2": h2})
    r, _ = fit3(tr[tr_s != sname].reset_index(drop=True), te)
    rows.append({"bien_the": f"TRAIN bỏ mùa {sname}", "n_train": r["n_train"], "n_test": r["n_test"], "ngay_nang_test": r["ngay_nang_test"], "MAE_hom_nay": r["MAE_hom_nay"], "MAE_L3": r["MAE_L3"], "d_L3−hom_nay": r["d_L3−hom_nay"], "lo": r["lo_L3−hom_nay"], "hi": r["hi_L3−hom_nay"],
                 "d_L3−L2": r["d_L3−L2 (thời tiết)"], "lo2": r["lo_L3−L2 (thời tiết)"], "hi2": r["hi_L3−L2 (thời tiết)"]})
S4 = pd.DataFrame(rows).set_index("bien_the"); save(S4.round(4), "S04_leave_one_season_out_model.csv"); print(S4.round(2).to_string())
# ---------- S04b: EDA — thứ hạng TP trong từng mùa; bỏ từng mùa
dd_ = d.assign(mua=season(d.Date)); sh = (dd_.groupby(["mua", "City"]).poor.mean() * 100).unstack("City")[CITIES]; n_ = dd_.groupby(["mua", "City"]).poor.sum().unstack("City")[CITIES]
sh.loc["CẢ NĂM"] = d.groupby("City").poor.mean().reindex(CITIES) * 100
for sname in ["Đông (12–2)", "Hè (3–5)", "Mưa (6–9)", "Sau mưa (10–11)"]: sh.loc[f"bỏ mùa {sname}"] = dd_[dd_.mua != sname].groupby("City").poor.mean().reindex(CITIES) * 100
sh.loc["bỏ tháng 10–2"] = d[~d.month.isin([10, 11, 12, 1, 2])].groupby("City").poor.mean().reindex(CITIES) * 100
sh["thu_hang"] = [">".join(sh.loc[i, CITIES].sort_values(ascending=False).index[:5]) for i in sh.index]; sh["3_TP_cao_nhat_la_Delhi_Lucknow_Gurugram"] = [set(sh.loc[i, CITIES].astype(float).nlargest(3).index) == {"Delhi", "Lucknow", "Gurugram"} for i in sh.index]
save(sh.round(2), "S04_share_by_season.csv"); save(n_, "S04_heavy_days_by_season.csv"); print(sh.round(1).to_string()); print(n_.to_string())
# ratio PM2.5 theo mùa (trong từng TP đủ ≥30 ngày nặng và ≥30 ngày còn lại trong mùa đó)
rows = []
for sname, g in dd_.groupby("mua"):
    for c in CITIES:
        x = g[g.City == c]; h, o = x[x.poor]["PM2.5"].dropna(), x[~x.poor]["PM2.5"].dropna()
        rows.append({"mua": sname, "City": c, "n_nang": len(h), "n_conlai": len(o), "ratio_PM25": h.median() / o.median() if len(h) >= 30 and len(o) >= 30 else np.nan})
rs = pd.DataFrame(rows); save(rs.round(3), "S04_pm25_ratio_by_season.csv", index=False); print(rs.pivot(index="City", columns="mua", values="ratio_PM25").reindex(CITIES).round(2).to_string())
# tương quan độ ẩm–AQI (đã bỏ mùa theo tháng) trong từng mùa
ew, ww, _, _ = C.load_with_weather(verbose=False); a = C.add_anomalies(ww.dropna(subset=["AQI"]), ["AQI"] + C.WX); a["mua"] = season(a.Date)
hs = pd.DataFrame({s: {c: g[g.City == c].AQI_a.corr(g[g.City == c].humidity_mean_a, method="spearman") for c in CITIES} for s, g in a.groupby("mua")}); hs["cả năm"] = [a[a.City == c].AQI_a.corr(a[a.City == c].humidity_mean_a, method="spearman") for c in CITIES]
save(hs.round(3), "S04_humidity_rho_by_season.csv"); print(hs.round(2).to_string())
