"""V05–V07 [Q02] as_of có chống leakage END-TO-END (raw → clean → feature) không?

Phần 0: assert bản vector hoá contextual_ratio == bản gốc; wrapper == pipeline tác giả == baseline.
Phần A: cắt RAW ở ngày t → làm sạch lại → make_features(as_of=t) → so với bản đầy đủ (mọi dòng ≤ t và riêng dòng Date == t).
Phần B: perturb dữ liệu SAU t (thêm đỉnh tương lai) → giá trị ≤ t có đổi không.
Chạy: python v02_asof.py
"""
from da_clean import *
import model_utils as M

raw8 = load_raw()
base = pd.read_csv(CLEAN, parse_dates=["Date"])
full_clean, full_ev = clean_all(raw8, fast=True)
for c in POLLUTANTS + ["AQI"]:
    assert eqnan(full_clean[c], base[c], 1e-9).all(), c
assert (full_clean.suspect_sensor_error.values == base.suspect_sensor_error.values).all()
print("Phần 0: wrapper DA tái lập đúng baseline (dung sai 1e-9)")

full_feat = M.make_features()                        # đúng như NB06 c6: từ bảng sạch baseline
L3 = M.LEVELS["L3"]
VALS = POLLUTANTS + ["AQI"]
USABLE = ["PM2.5", "NO2", "CO", "SO2", "O3"]

CUTS = {
    "2018-12-01": "NB06 c6 (ngày tác giả thử)", "2019-11-15": "NB06 c6 (ngày tác giả thử)", "2020-01-10": "NB06 c6 (ngày tác giả thử)",
    "2019-06-30": "ranh train/test (TRAIN_END)", "2020-02-29": "ranh test/holdout (TEST_END)",
    "2017-07-08": "ngay sau điểm nghi lỗi Bengaluru 07–08/07/2017", "2017-07-09": "ngày nghi lỗi Gurugram 09/07/2017",
    "2017-07-30": "ngày nghi lỗi Gurugram 30/07/2017", "2017-08-29": "ngày nghi lỗi Gurugram 29/08/2017 (PM2.5 950)",
    "2017-08-30": "Gurugram 30/08/2017 (PM2.5 643,7, AQI 891: điểm tác giả ghi 'chưa xử lý')", "2018-02-06": "ngày nghi lỗi Jaipur 06/02/2018",
    "2017-11-09": "đỉnh mùa đông 2017 (top AQI Delhi)", "2018-06-15": "cụm bụi 14–16/06/2018",
}
# thêm ngày nằm GIỮA một chuỗi flatline CO và giữa một khoảng thiếu được nội suy (trong khoảng chung)
rw = raw8.set_index(["City", "Date"])
bc = base.set_index(["City", "Date"])
found = {}
for c in CITIES:
    r = raw8[(raw8.City == c) & (raw8.Date >= "2017-06-14")].reset_index(drop=True)
    b = base[(base.City == c) & (base.Date >= "2017-06-14")].reset_index(drop=True)
    for p in ["CO", "PM2.5", "NO2", "SO2", "O3"]:
        fl = (r[p] == 0) & b[p].isna()                                            # 0 trong raw, NaN sau làm sạch = flatline
        it = r[p].isna() & b[p].notna()                                           # thiếu trong raw, có giá trị = nội suy
        for kind, m in (("flatline", fl), ("nội suy", it)):
            if m.any() and (kind, p) not in found:
                i = int(np.flatnonzero(m.to_numpy())[0]); run = 1
                while i + run < len(m) and m.iloc[i + run]: run += 1
                if run >= 2:
                    found[(kind, p)] = (r.Date.iloc[i], c, run)
for (kind, p), (dt, c, run) in found.items():
    CUTS.setdefault(dt.strftime("%Y-%m-%d"), f"ngày đầu của chuỗi {kind} {p} ở {c} (dài {run} ngày)")

summ, detail = [], []
for cut_s, why in sorted(CUTS.items()):
    cut = pd.Timestamp(cut_s)
    cc, ev = clean_all(raw8[raw8.Date <= cut], fast=True)
    fb = full_clean[full_clean.Date <= cut].reset_index(drop=True)
    assert len(cc) == len(fb) and (cc.City.values == fb.City.values).all() and (cc.Date.values == fb.Date.values).all()
    n_val = 0; n_flag = 0; per = {}
    for col in VALS:
        e = eqnan(cc[col], fb[col], 1e-9)
        if (~e).any():
            per[col] = int((~e).sum()); n_val += per[col]
            for i in np.flatnonzero(~e.to_numpy()):
                city, dt = cc.City[i], cc.Date[i]; rv = rw.loc[(city, dt), col]
                a, b_ = cc[col][i], fb[col][i]
                wm_full = bool(fb[f"{col}_was_missing"][i]); sus_cut = bool(cc.suspect_sensor_error[i]); sus_full = bool(fb.suspect_sensor_error[i])
                if rv == 0 and (a != a) != (b_ != b_): path = "flatline: chuỗi số 0 vắt qua t (≥3 ngày chỉ khi thấy tương lai, hoặc ngược lại)"
                elif rv != rv: path = "nội suy: khoảng thiếu vắt qua t, đầu mút phải nằm sau t"
                elif sus_cut != sus_full: path = "luật nghi lỗi: top-5 toàn chuỗi/cửa sổ căn giữa đổi theo dữ liệu sau t"
                else: path = "khác"
                detail.append({"cut": cut_s, "city": city, "date": dt.date(), "column": col, "raw": rv, "clean_cat_tai_t": a, "clean_day_du": b_,
                               "cach_t_ngay": (cut - dt).days, "duong_di": path})
    for col in [c for c in cc.columns if c.endswith("_is_outlier") or c.endswith("_was_missing") or c in ("suspect_sensor_error",)]:
        n_flag += int((cc[col].astype(bool).values != fb[col].astype(bool).values).sum())
    # ---- đặc trưng
    cf = features_from(cc, as_of=cut, tag="cut")
    ff = full_feat[full_feat.Date <= cut]
    k = ["City", "Date"]
    mrg = cf[k + L3 + ["AQI", "y"]].merge(ff[k + L3 + ["AQI", "y"]], on=k, suffixes=("_cut", "_full"), validate="1:1")
    assert len(mrg) == len(cf) == len(ff)
    inwin = mrg.Date >= "2017-06-14"
    feat_all = sum(int((~eqnan(mrg[f + "_cut"], mrg[f + "_full"], 1e-9))[inwin.values].sum()) for f in L3)
    rows_all = int(pd.concat([~eqnan(mrg[f + "_cut"], mrg[f + "_full"], 1e-9) for f in L3], axis=1).any(axis=1)[inwin.values].sum())
    at = (mrg.Date == cut).values
    feat_at = {f: int((~eqnan(mrg[f + "_cut"], mrg[f + "_full"], 1e-9))[at].sum()) for f in L3}
    aqi_at = int((~eqnan(mrg.AQI_cut, mrg.AQI_full, 1e-9))[at].sum())
    lt = (mrg.Date < cut).values & inwin.values
    y_diff = int((~eqnan(mrg.y_cut, mrg.y_full, 1e-9))[lt].sum())
    keep_cut = (mrg.AQI_cut.notna() & mrg.y_cut.notna())[lt]; keep_full = (mrg.AQI_full.notna() & mrg.y_full.notna())[lt]
    summ.append({"cut": cut_s, "ly_do_chon": why, "o_gia_tri_doi_(11 chat+AQI, moi ngay<=t)": n_val, "theo_cot": str(per), "o_co_doi(_is_outlier/_was_missing/suspect)": n_flag,
                 "NB06_test_tai_Date==t: o_feature_L3_doi": sum(feat_at.values()), "feature_doi_tai_t": str({k_: v for k_, v in feat_at.items() if v}), "AQI_tai_t_doi": aqi_at,
                 "moi_dong<=t_trong_khoang_chung: o_feature_L3_doi": feat_all, "so_dong_co_feature_doi": rows_all, "nhan_y_doi(Date<t)": y_diff,
                 "dong_giu_lai_cut": int(keep_cut.sum()), "dong_giu_lai_full": int(keep_full.sum())})
summ = pd.DataFrame(summ); detail = pd.DataFrame(detail)
save(summ, "V05_asof_cut_summary.csv", index=False); save(detail, "V05_asof_cut_cell_changes.csv", index=False)
print(summ.drop(columns=["ly_do_chon"]).to_string())
print(detail.groupby(["duong_di", "column"]).size())

# ---------------- Phần B: perturb tương lai
pert = []
for cut_s, city, what in [("2018-12-01", "Gurugram", "PM2.5 và AQI ×6 trong 6 ngày tháng 7/2019 (đỉnh giả trái mùa sau t)"),
                          ("2018-12-01", "Jaipur", "PM2.5 và AQI ×6 trong 6 ngày tháng 7/2019 (đỉnh giả trái mùa sau t)"),
                          ("2019-11-15", "Delhi", "PM2.5 và AQI ×3 trong 6 ngày tháng 12/2019 (đỉnh mùa đông lớn hơn sau t)")]:
    cut = pd.Timestamp(cut_s); r2 = raw8.copy()
    days = pd.date_range("2019-07-10", periods=6) if "7/2019" in what else pd.date_range("2019-12-20", periods=6)
    m = (r2.City == city) & r2.Date.isin(days)
    f = 6 if "×6" in what else 3
    r2.loc[m, ["PM2.5", "AQI"]] = r2.loc[m, ["PM2.5", "AQI"]] * f
    pc, _ = clean_all(r2, fast=True)
    a = pc[(pc.Date <= cut)].reset_index(drop=True); b = full_clean[full_clean.Date <= cut].reset_index(drop=True)
    ch = []
    for col in VALS:
        e = eqnan(a[col], b[col], 1e-9)
        for i in np.flatnonzero(~e.to_numpy()):
            ch.append(f"{a.City[i]} {a.Date[i].date()} {col}: {b[col][i]}→{a[col][i]}")
    pf = features_from(pc, tag="pert"); k = ["City", "Date"]
    mm = pf[pf.Date <= cut][k + L3 + ["AQI", "y"]].merge(full_feat[full_feat.Date <= cut][k + L3 + ["AQI", "y"]], on=k, suffixes=("_p", "_f"))
    nfe = sum(int((~eqnan(mm[x + "_p"], mm[x + "_f"], 1e-9)).sum()) for x in L3 + ["AQI"])
    pert.append({"t": cut_s, "thanh_pho_bi_perturb": city, "perturb_SAU_t": what, "o_sach_<=t_bi_doi": len(ch), "chi_tiet": "; ".join(ch),
                 "o_feature_L3+AQI_<=t_bi_doi": nfe})
pert = pd.DataFrame(pert); save(pert, "V06_future_perturbation.csv", index=False); print(pert.to_string())
