"""V01–V04 [Q01] Tái tạo pipeline làm sạch từ raw (trong bộ nhớ, không ghi đè) và cân đối dữ liệu.
Chạy: python v01_pipeline.py
"""
from da_common import *
import pipeline as P
from utils import flag_flatline_zeros, POLLUTANT_COLS

raw_all = pd.read_csv(RAW, parse_dates=["Date"])
raw = raw_all[raw_all.City.isin(CITIES)].copy()
rows = []
def rec(crit, expected, actual, note=""):
    ok = (expected == actual) if not isinstance(expected, float) else abs(expected - actual) < 1e-9
    rows.append({"tieu_chi": crit, "expected": expected, "actual": actual, "diff": (actual - expected) if isinstance(actual, (int, float, np.integer, np.floating)) and isinstance(expected, (int, float)) else "", "khop": bool(ok), "ghi_chu": note})

rec("raw: số dòng 26 TP", 29531, len(raw_all)); rec("raw: số thành phố", 26, raw_all.City.nunique()); rec("raw: số dòng 8 TP", 14056, len(raw))
rec("raw: trùng (City,Date)", 0, int(raw.duplicated(["City", "Date"]).sum()))
gaps = sum((g.Date.max() - g.Date.min()).days + 1 - g.Date.nunique() for _, g in raw.groupby("City"))
rec("raw: ngày bị đứt", 0, int(gaps))
rec("raw: giá trị âm (12 chất + AQI)", 0, int((raw[POLLUTANT_COLS + ["AQI"]] < 0).sum().sum()))
miss_raw = int(raw[POLLUTANTS + ["AQI"]].isna().sum().sum())
rec("raw: ô thiếu 11 chất + AQI", 16953, miss_raw, f"{miss_raw / (len(raw) * 12) * 100:.2f}% (log ghi 10,05%)")

# ---- chạy lại pipeline từ raw
frames, evid, flat_tot, flat_by = {}, [], 0, {}
for c in CITIES:
    frames[c], ev = P.clean_city(c, str(RAW)); evid.append(ev)
    r = raw[raw.City == c].sort_values("Date").reset_index(drop=True)
    _, fl = flag_flatline_zeros(r, cols=POLLUTANTS, min_run=3)
    for k, v in fl.items(): flat_by[k] = flat_by.get(k, 0) + v
evid = pd.concat(evid, ignore_index=True)
merged = P.merge_cities(list(frames.values()))
base = pd.read_csv(CLEAN, parse_dates=["Date"])

rec("clean: shape", "(14056, 40)", str(merged.shape)); rec("baseline CSV: shape", "(14056, 40)", str(base.shape))
rec("clean: cột trùng thứ tự baseline", True, list(merged.columns) == list(base.columns))
rec("clean: trùng (City,Date)", 0, int(merged.duplicated(["City", "Date"]).sum()))
rec("clean: liên tục ngày từng TP", True, all((g.Date.max() - g.Date.min()).days + 1 == len(g) for _, g in merged.groupby("City")))
rec("clean: số cờ _was_missing", 12, sum(c.endswith("_was_missing") for c in merged.columns))
rec("clean: số cờ _is_outlier", 11, sum(c.endswith("_is_outlier") for c in merged.columns))

# ---- so từng ô với bảng sạch đã commit (đọc CSV), dung sai 0 và 1e-9
cell = []
for col in merged.columns:
    a, b = merged[col], base[col]
    if col == "pm25_gt_pm10_flag":
        a = a.astype(object).where(a.notna(), np.nan); b = b.astype(object).where(b.notna(), np.nan)
        a = a.map(lambda v: v if v != v else bool(v)); b = b.map(lambda v: v if v != v else (str(v) == "True"))
    e0, e9 = eqnan(a, b, 0.0), eqnan(a, b, 1e-9)
    nanmis = int((pd.Series(a).isna().to_numpy() != pd.Series(b).isna().to_numpy()).sum())
    maxabs = float((a.astype(float) - b.astype(float)).abs().max()) if col in POLLUTANTS + ["AQI"] else np.nan
    cell.append({"cot": col, "dtype_tu_pipeline": str(merged[col].dtype), "dtype_sau_doc_CSV": str(base[col].dtype), "n_o": len(a),
                 "o_khac_tuyet_doi": int((~e0).sum()), "o_khac_dung_sai_1e-9": int((~e9).sum()), "lech_NaN": nanmis, "max_abs_diff": maxabs})
cell = pd.DataFrame(cell)
save(cell, "V01_cell_diff_vs_baseline.csv", index=False)
rec("so từng ô: tổng ô khác (dung sai 1e-9)", 0, int(cell["o_khac_dung_sai_1e-9"].sum()))
rec("so từng ô: tổng ô lệch NaN", 0, int(cell.lech_NaN.sum()))
rec("so từng ô: ô khác bit-level (float làm tròn)", 0, int(cell.o_khac_tuyet_doi.sum()),
    f"max |diff| = {cell.max_abs_diff.max():.2e}; chỉ do số học dấu phẩy động khác phiên bản pandas/numpy")

# ---- tái đếm các con số của cleaning_log
rec("flatline 0→NaN (11 chất, ≥3 ngày)", 2169, int(sum(flat_by.values())), str(dict(sorted(flat_by.items(), key=lambda kv: -kv[1]))))
was = {p: merged[f"{p}_was_missing"] for p in POLLUTANTS + ["AQI"]}
n_imp = int(sum((was[p] & merged[p].notna()).sum() for p in POLLUTANTS))
rec("ô nội suy còn giá trị trong bảng cuối (was_missing & notna)", 3329, n_imp)
rec("điểm được xét (suspect_points)", 93, len(evid))
sus = evid[evid.action == "đặt NaN"]
rec("ô nghi lỗi đặt NaN", 41, len(sus), str(sus.column.value_counts().to_dict()))
rec("ngày nghi lỗi (suspect_sensor_error)", 24, int(merged.suspect_sensor_error.sum()))
rec("số TP có ngày nghi lỗi", 7, int(merged[merged.suspect_sensor_error].City.nunique()))
n_out = int(merged[[f"{p}_is_outlier" for p in POLLUTANTS]].sum().sum())
rec("ô cờ IQR theo tháng", 6656, n_out); rec("PM2.5 bị cờ IQR", 531, int(merged["PM2.5_is_outlier"].sum()))
rec("cờ PM2.5 > 1,2×PM10", 139, int(merged.pm25_gt_pm10_flag.fillna(False).astype(bool).sum()))
rec("AQI thiếu (bảng cuối)", 836, int(merged.AQI.isna().sum()), "log bước 5 ghi 836 'dòng'")
rec("AQI có mà thiếu Bucket hoặc ngược lại", 0, int((merged.AQI.isna() != merged.AQI_Bucket.isna()).sum()))
miss_fin = int(merged[POLLUTANTS + ["AQI"]].isna().sum().sum())
rec("clean: ô thiếu 11 chất + AQI", 15832, miss_fin, f"{miss_fin / (len(merged) * 12) * 100:.2f}% (log ghi 9,39%)")

# ---- cân đối: phân rã 41 ô nghi lỗi theo trạng thái trước khi đặt NaN
mi = merged.set_index(["City", "Date"])
rr = raw.set_index(["City", "Date"])
dec = []
for _, r in sus.iterrows():
    k = (r.city, pd.Timestamp(r.date)); wm = bool(mi.loc[k, f"{r.column}_was_missing"]); rawv = rr.loc[k, r.column]
    dec.append({"city": r.city, "date": r.date, "column": r.column, "value_original_report": r.value_original, "raw_value": rawv,
                "was_missing_flag": wm, "loai": "giá trị NỘI SUY bị đặt NaN" if wm else "giá trị THẬT bị đặt NaN"})
dec = pd.DataFrame(dec); save(dec, "V01_suspect_41_decomposition.csv", index=False)
n_real = int((~dec.was_missing_flag).sum()); n_interp = int(dec.was_missing_flag.sum())
rec("41 ô nghi lỗi: số ô là giá trị thật (→ NaN mới)", 39, n_real, "log §1 cộng +39")
rec("41 ô nghi lỗi: số ô vốn thiếu rồi được nội suy rồi bị xoá lại", 2, n_interp, "không tạo NaN mới so với raw; làm giảm số ô 'đã nội suy' còn lại")
n_interp_gross = n_imp + n_interp
rec("cân đối A (log §1): 16953 + 2169 − 3329 + 39", 15832, miss_raw + int(sum(flat_by.values())) - n_imp + n_real)
rec("cân đối B (gộp): raw + flatline − nội suy GỘP + 41", 15832, miss_raw + int(sum(flat_by.values())) - n_interp_gross + len(sus), f"nội suy gộp = {n_interp_gross} (3329 + {n_interp})")
late = int(sum((~was[p] & merged[p].isna()).sum() for p in POLLUTANTS + ["AQI"]))
rec("ô ~was_missing & NaN (NaN thêm sau)", 39, late)

# ---- cleaning_summary: 104 hàng, đếm False
summ = pd.read_csv(ROOT / "reports" / "cleaning_summary_8cities.csv")
rec("summary: số hàng", 104, len(summ))
f = summ[~summ.dung_lam_bien_mo_hinh.astype(bool)]
rec("summary: số hàng dung_lam_bien_mo_hinh=False", 11, len(f), f"Xylene {int((f.column=='Xylene').sum())} + PM10 Lucknow {int(((f.column=='PM10')&(f.city=='Lucknow')).sum())} + kept≥60% {int((f.status=='kept').sum())}")
rec("summary: False KHÔNG tính Xylene", 3, int((f.column != "Xylene").sum()), "; ".join(f[f.column != "Xylene"].apply(lambda r: f"{r.city}/{r.column} {r.pct_missing_final}%", axis=1)))
rec("summary: tổng n_imputed", 3329, int(summ.n_imputed.sum())); rec("summary: tổng n_flatline_to_nan", 2169, int(summ.n_flatline_to_nan.sum()))
rec("summary: tổng n_nan_added_later", 39, int(summ.n_nan_added_later.sum())); rec("summary: tổng n_outlier_flagged", 6656, int(summ.n_outlier_flagged.sum()))
k = summ[summ.status == "kept"]
bal = (k.n_missing_final == k.n_missing_before + k.n_flatline_to_nan - k.n_imputed + k.n_nan_added_later)
rec("summary: hàng kept cân đối", int(len(k)), int(bal.sum()))
# so summary tái lập (từ raw + merged tái lập) với file commit
re = []
for c in CITIES:
    r = raw[raw.City == c].sort_values("Date").reset_index(drop=True); _, fl = flag_flatline_zeros(r, cols=POLLUTANTS + ["Xylene"], min_run=3)
    m = merged[merged.City == c]
    for col in POLLUTANTS + ["AQI"]:
        if c == "Lucknow" and col == "PM10": continue
        w = m[f"{col}_was_missing"]
        re.append({"city": c, "column": col, "n_missing_before": int(r[col].isna().sum()), "n_flatline_to_nan": int(fl.get(col, 0)), "n_imputed": int((w & m[col].notna()).sum()),
                   "n_nan_added_later": int((~w & m[col].isna()).sum()), "n_missing_final": int(m[col].isna().sum())})
re = pd.DataFrame(re).merge(k, on=["city", "column"], suffixes=("_da", "_commit"))
nd = sum(int((re[f"{x}_da"] != re[f"{x}_commit"]).sum()) for x in ["n_missing_before", "n_flatline_to_nan", "n_imputed", "n_nan_added_later", "n_missing_final"])
rec("summary: số ô đếm khác giữa DA và file commit (95 hàng kept × 5 cột)", 0, nd)

# ---- suspect report so với file commit
sp = pd.read_csv(ROOT / "reports" / "suspect_points_8cities.csv")
mine = evid[sp.columns].sort_values(["city", "column", "date"]).reset_index(drop=True)
mine["date"] = pd.to_datetime(mine.date).dt.strftime("%Y-%m-%d"); sp["date"] = pd.to_datetime(sp.date).dt.strftime("%Y-%m-%d")
same = all(eqnan(mine[c], sp[c], 1e-9).all() for c in sp.columns)
rec("suspect_points: 93 dòng trùng từng ô với file commit", True, bool(same))

# ---- dtype sau đọc CSV
bool_cols = [c for c in base.columns if c.endswith("_was_missing") or c.endswith("_is_outlier")] + ["suspect_sensor_error"]
rec("dtype CSV: 24 cờ bool đọc lại thành bool", 24, int(sum(base[c].dtype == bool for c in bool_cols)))
rec("dtype CSV: pm25_gt_pm10_flag", "object/str (True/False/NaN)", str(base.pm25_gt_pm10_flag.dtype), "boolean nullable mất kiểu khi lưu CSV; downstream phải tự ép kiểu")

res = pd.DataFrame(rows); save(res, "V01_pipeline_reproduction.csv", index=False)
print(res.to_string())
merged.to_csv(SCRATCH / "air_quality_8cities_repro.csv", index=False)
print("sha256 baseline:", sha256(CLEAN)); print("sha256 repro   :", sha256(SCRATCH / "air_quality_8cities_repro.csv"))
