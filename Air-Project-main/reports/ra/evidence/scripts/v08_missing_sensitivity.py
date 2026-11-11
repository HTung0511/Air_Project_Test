"""V08 + V09 [Q03] Bảng thiếu dữ liệu theo TP×cột qua từng bước; độ dài khối thiếu; coverage theo năm/tháng;
độ nhạy ngưỡng flatline 2/3/5/7, max_gap 0/7/14/30/60, luật nghi lỗi current/flag_only/none lên: số ô, EDA, mô hình.
Chạy: python v08_missing_sensitivity.py
"""
from da_model import *
from da_eda import *
import utils as U

raw8 = load_raw(); base = pd.read_csv(CLEAN, parse_dates=["Date"])
COLS = [c for c in POLLUTANTS if c != "Xylene"] + ["AQI"] if "Xylene" in POLLUTANTS else POLLUTANTS + ["AQI"]
RAWCOLS = ["PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene", "AQI"]

# ---------------- V08a: bảng thiếu theo bước (dùng các bước của pipeline với tham số gốc)
def runs(isna):
    """độ dài các khối True liên tiếp"""
    v = np.asarray(isna, bool); 
    if not v.any(): return np.array([], int)
    d = np.diff(np.concatenate([[0], v.astype(int), [0]])); return np.flatnonzero(d == -1) - np.flatnonzero(d == 1)

rows = []
for c in CITIES:
    r0 = raw8[raw8.City == c].sort_values("Date").reset_index(drop=True); b = base[base.City == c].sort_values("Date").reset_index(drop=True); n = len(r0)
    for col in RAWCOLS:
        x = {"City": c, "cot": col, "n_ngay": n, "raw_thieu": int(r0[col].isna().sum()), "raw_thieu_%": r0[col].isna().mean() * 100, "raw_bang_0": int((r0[col] == 0).sum())}
        if col == "Xylene":
            x.update({"ghi_chu": "cột bị loại khỏi bảng sạch"}); rows.append(x); continue
        fl = int(((r0[col] == 0) & (b[col].isna() | b[f"{col}_was_missing"])).sum()) if col in ("CO", "NOx", "Benzene", "Toluene") else 0
        x["flatline_0→NaN"] = fl; x["sau_flatline_thieu"] = x["raw_thieu"] + fl
        x["noi_suy_con_lai (was_missing & có giá trị)"] = int((b[f"{col}_was_missing"] & b[col].notna()).sum())
        x["bi_xoa_do_nghi_loi (raw có, sạch NaN, không phải flatline)"] = int((r0[col].notna() & (r0[col] != 0 if col in ("CO", "NOx", "Benzene", "Toluene") else True) & b[col].isna()).sum())
        x["cuoi_thieu"] = int(b[col].isna().sum()); x["cuoi_thieu_%"] = b[col].isna().mean() * 100
        rl = runs(b[col].isna()); rr = runs(r0[col].isna())
        x["so_khoi_thieu_raw"], x["khoi_raw_median"], x["khoi_raw_max"] = len(rr), float(np.median(rr)) if len(rr) else 0, int(rr.max()) if len(rr) else 0
        x["khoi_raw_1-3"], x["khoi_raw_4-14"], x["khoi_raw_15-60"], x["khoi_raw_>60"] = int((rr <= 3).sum()), int(((rr > 3) & (rr <= 14)).sum()), int(((rr > 14) & (rr <= 60)).sum()), int((rr > 60).sum())
        x["so_khoi_thieu_cuoi"], x["khoi_cuoi_max"] = len(rl), int(rl.max()) if len(rl) else 0
        x["o_thieu_dau_chuoi (trước giá trị thật đầu tiên)"] = int(r0[col].notna().idxmax()) if r0[col].notna().any() else n
        x["co_che"] = "thiếu 100%: không nhận diện được cơ chế" if x["raw_thieu"] == n else ("thiếu ≥80%: gần như không đo" if x["raw_thieu_%"] >= 80 else "")
        rows.append(x)
mt = pd.DataFrame(rows); save(mt.round(3), "V08_missing_by_city_column.csv", index=False)
tot = mt[mt.cot != "Xylene"][["raw_thieu", "flatline_0→NaN", "noi_suy_con_lai (was_missing & có giá trị)", "bi_xoa_do_nghi_loi (raw có, sạch NaN, không phải flatline)", "cuoi_thieu"]].sum()
print("Tổng (11 chất + AQI):", tot.to_dict()); print(mt[mt.co_che != ""][["City", "cot", "raw_thieu_%", "co_che"]].dropna().to_string())
print(mt.groupby("cot")[["raw_thieu", "flatline_0→NaN", "cuoi_thieu", "khoi_raw_1-3", "khoi_raw_4-14", "khoi_raw_15-60", "khoi_raw_>60", "khoi_raw_max"]].sum().to_string())
# coverage theo năm và theo tháng (AQI và PM2.5; % ngày có giá trị trong bảng sạch)
b = base.assign(year=base.Date.dt.year, month=base.Date.dt.month)
cov = []
for col in ["AQI", "PM2.5", "NO2", "CO", "SO2", "O3", "PM10"]:
    for key in ("year", "month"):
        t = (b.groupby(["City", key])[col].apply(lambda s: s.notna().mean() * 100)).unstack(key).reindex(CITIES).round(1); t.insert(0, "theo", key); t.insert(0, "cot", col); cov.append(t.reset_index())
cov = pd.concat(cov, ignore_index=True); save(cov, "V08_coverage_by_year_month.csv", index=False)
nrow = b.groupby(["City", "year"]).size().unstack("year").reindex(CITIES); print("Số ngày theo năm:\n", nrow.to_string())
print(cov[(cov.cot == "AQI") & (cov.theo == "year")].drop(columns=["cot", "theo"]).dropna(axis=1, how="all").to_string())
print(cov[(cov.cot == "AQI") & (cov.theo == "month")].drop(columns=["cot", "theo"]).dropna(axis=1, how="all").to_string())

# ---------------- V09: độ nhạy
CONFIGS = [("baseline (flat 3, gap 14, xoá nghi lỗi)", {}),
           ("flatline ≥2", dict(flat_run=2)), ("flatline ≥5", dict(flat_run=5)), ("flatline ≥7", dict(flat_run=7)),
           ("max_gap 0 (không nội suy)", dict(max_gap=0)), ("max_gap 7", dict(max_gap=7)), ("max_gap 30", dict(max_gap=30)), ("max_gap 60", dict(max_gap=60)),
           ("nghi lỗi: chỉ gắn cờ (flag-only)", dict(suspect="flag_only")), ("nghi lỗi: không chạy luật (giữ điểm)", dict(suspect="none"))]
ds0 = M.build_dataset(verbose=False); key0 = set(zip(ds0.City.astype(str), ds0.Date))
A0 = None; out_rows = []; eda_rows = []
for name, kw in CONFIGS:
    cc, ev = clean_all(raw8, **kw)
    cc = cc.sort_values(["City", "Date"]).reset_index(drop=True); bb = base.sort_values(["City", "Date"]).reset_index(drop=True)
    r = {"cau_hinh": name}
    val = [c for c in bb.columns if c in RAWCOLS]
    r["o_gia_tri_khac_baseline"] = int(sum((~eqnan(cc[c], bb[c], 1e-9)).sum() for c in val)); r["trong_do_AQI"] = int((~eqnan(cc["AQI"], bb["AQI"], 1e-9)).sum())
    r["o_thieu_cuoi"] = int(cc[val].isna().sum().sum()); r["o_noi_suy_con_lai"] = int(sum((cc[f"{c}_was_missing"] & cc[c].notna()).sum() for c in val if f"{c}_was_missing" in cc))
    r0 = raw8.sort_values(["City", "Date"]).reset_index(drop=True)
    r["o_flatline"] = int(sum(((r0[c] == 0) & (cc[c].isna() | cc[f"{c}_was_missing"])).sum() for c in ("CO", "NOx", "Benzene", "Toluene")))
    r["o_nghi_loi_bi_xoa"] = int((ev.action == "đặt NaN").sum()) if len(ev) and kw.get("suspect", "current") == "current" else 0
    r["ngay_gan_co_nghi_loi"] = int(cc.suspect_sensor_error.astype(bool).sum()); r["o_IQR"] = int(cc[[c for c in cc.columns if c.endswith("_is_outlier")]].sum().sum())
    # EDA
    e, win, s_, e_ = prep(cc); em = eda_metrics(win); em["cau_hinh"] = name; eda_rows.append(em)
    for k in ("n_ngay_co_AQI", "n_ngay_nang", "pct_Delhi", "pct_Lucknow", "pct_Gurugram", "ratio_PM25_trung_vi_cac_TP", "spearman_PM2.5", "pct_ngay_nang_thang_10_2", "thu_hang"): r["EDA_" + k] = em[k]
    # mô hình: toàn mẫu của biến thể, và cùng mẫu với baseline
    for mi, tag in ((True, "mask"), (False, "khong_mask")):
        d = dataset_from(cc, mask_interp=mi, tag="sens")
        R = run_protocol(d, levels=("L1", "L2", "L3"), thresholds=False)
        tt, md = R["test_tab"], R["mdiff"].set_index(["A", "B"])
        r[f"{tag}_n_train/test"] = f"{len(R['tr'])}/{len(R['te'])}"; r[f"{tag}_alpha"] = str(R["best_alpha"])
        for k, nm in [(PERSIST, "hom_nay"), ("Ridge L1", "L1"), ("Ridge L2", "L2"), ("Ridge L3", "L3")]: r[f"{tag}_MAE_{nm}"] = tt.loc[k, "MAE"]
        for (a_, b_), nm in [(("Ridge L3", PERSIST), "L3−hom_nay"), (("Ridge L3", "Ridge L2"), "L3−L2")]:
            r[f"{tag}_d_{nm}"] = f"{md.loc[(a_, b_), 'dMAE']:.2f} [{md.loc[(a_, b_), 'lo']:.2f}; {md.loc[(a_, b_), 'hi']:.2f}]"
        te = R["te"]; y = te.y.to_numpy() >= 201
        for nm, sc in (("hom_nay", te.AQI.to_numpy()), ("L3", R["pred_te"]["Ridge L3"])):
            m = M.alert_metrics(y, sc >= 201); r[f"{tag}_{nm}@201_recall"], r[f"{tag}_{nm}@201_precision"] = m["recall"], m["precision"]
        if mi:
            same = np.array([(c, dte) in key0 for c, dte in zip(te.City.astype(str), te.Date)])
            r["mask_cung_mau_n_test"] = int(same.sum()); r["mask_cung_mau_MAE_hom_nay"] = M.mae(te.y[same], te.AQI[same]); r["mask_cung_mau_MAE_L3"] = M.mae(te.y[same], R["pred_te"]["Ridge L3"][same])
    out_rows.append(r); print(name, "xong", flush=True)
sens = pd.DataFrame(out_rows); save(sens.round(4), "V09_cleaning_sensitivity.csv", index=False); save(pd.DataFrame(eda_rows).set_index("cau_hinh").round(4), "V09_cleaning_sensitivity_eda_detail.csv")
pd.set_option("display.width", 400)
print(sens.set_index("cau_hinh").T.to_string())
