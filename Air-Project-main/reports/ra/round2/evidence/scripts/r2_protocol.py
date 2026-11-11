"""DA vòng 2 — bộ máy tính metric theo giao thức đã khóa (da_verification_protocol.md, mục 4–8).

ĐỘC LẬP với src/ của dự án (cũ lẫn mới): chỉ dùng numpy, pandas, scikit-learn. Đầu vào là một bảng mẫu có các cột
  City, Date, Date_target, AQI (= AQI ngày t), y (= AQI ngày t+1), và các cột đặc trưng.
Nhờ vậy cùng một bộ máy chấm được cả bảng đặc trưng của mã cũ và của mã Dev.

Cấu trúc mô hình chép theo mô tả của NB06 baseline: điền trung vị (kèm cột báo thiếu) -> chuẩn hóa -> one-hot thành phố
(bỏ mức đầu) -> Ridge trên log(y). Việc bộ máy này tái lập đúng số vòng 1 được kiểm ở r2_baseline.py.
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CITIES = ["Delhi", "Gurugram", "Lucknow", "Jaipur", "Bengaluru", "Amritsar", "Chennai", "Hyderabad"]
TRAIN_END, TEST_START, TEST_END, HOLD_START, HOLD_END = (pd.Timestamp(x) for x in
                                                         ("2019-06-30", "2019-07-01", "2020-02-29", "2020-03-01", "2020-07-01"))
COMMON_START = pd.Timestamp("2017-06-14")
ALPHAS = [0.1, 1, 10, 30, 100, 300]
HGB_GRID = [dict(max_depth=d, max_iter=n, learning_rate=0.05, min_samples_leaf=40) for d in (2, 3) for n in (100, 200)]
N_SPLITS, GAP_ROWS = 4, 16
THR_GRID = np.arange(80, 301, 1)
POOR = 201
PERSIST, CITY_MEAN, CLIM = "Ngày mai = hôm nay", "Trung bình theo thành phố", "Trung vị cùng tháng (khí hậu)"
MAE_PAIRS = [("Ridge L1", PERSIST), ("Ridge L2", "Ridge L1"), ("Ridge L3", "Ridge L2"), ("Ridge L3", PERSIST)]


def season_of(month):
    return ("Đông (12-2)" if month in (12, 1, 2) else "Hè (3-5)" if month in (3, 4, 5) else "Mưa (6-9)" if month in (6, 7, 8, 9) else "Sau mưa (10-11)")


def assign_split(date_target):
    dt = pd.to_datetime(pd.Series(date_target)).reset_index(drop=True)
    return pd.Series(np.select([dt <= TRAIN_END, (dt >= TEST_START) & (dt <= TEST_END), (dt >= HOLD_START) & (dt <= HOLD_END)],
                               ["train", "test", "holdout"], default="ngoài phạm vi"))


def prepare(ds):
    """Sắp theo (Date_target, City theo chữ cái), gán split theo Date_target, thêm y_log."""
    d = ds.copy()
    d["City"] = d.City.astype(str)
    d["Date"], d["Date_target"] = pd.to_datetime(d.Date), pd.to_datetime(d.Date_target)
    assert (d.Date_target - d.Date == pd.Timedelta(days=1)).all(), "Date_target phải là ngày lịch kế tiếp của Date"
    assert not d.duplicated(["City", "Date"]).any(), "khóa (City, Date) bị trùng"
    assert np.isfinite(d.y).all() and (d.y > 0).all() and np.isfinite(d.AQI).all() and (d.AQI > 0).all(), "AQI/y không hợp lệ"
    d = d.sort_values(["Date_target", "City"]).reset_index(drop=True)
    d["split"] = assign_split(d.Date_target).to_numpy()
    d["y_log"] = np.log(d.y)
    return d


def make_pipe(feats, model="ridge", alpha=1.0, seed=42, **kw):
    num = Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)), ("sc", StandardScaler())])
    cat = OneHotEncoder(categories=[CITIES], drop="first", handle_unknown="ignore", sparse_output=False)
    prep = ColumnTransformer([("num", num, list(feats)), ("city", cat, ["City"])], verbose_feature_names_out=False)
    m = Ridge(alpha=alpha) if model == "ridge" else HistGradientBoostingRegressor(random_state=seed, **kw)
    return Pipeline([("prep", prep), ("model", m)])


def cv_folds(tr):
    return list(TimeSeriesSplit(n_splits=N_SPLITS, gap=GAP_ROWS).split(tr))


def _fit_pred(fit, new, feats, **mk):
    m = make_pipe(feats, **mk).fit(fit[feats + ["City"]], fit.y_log)
    return np.exp(m.predict(new[feats + ["City"]]))


def cv_mae(tr, feats, **mk):
    return float(np.mean([np.mean(np.abs(tr.iloc[b].y.to_numpy() - _fit_pred(tr.iloc[a], tr.iloc[b], feats, **mk))) for a, b in cv_folds(tr)]))


def oof(tr, feats, **mk):
    idx, pred = [], []
    for a, b in cv_folds(tr):
        idx.append(b); pred.append(_fit_pred(tr.iloc[a], tr.iloc[b], feats, **mk))
    return np.concatenate(idx), np.concatenate(pred)


def baselines(fit, new):
    cf, cn = fit.City.astype(str), new.City.astype(str)
    mean_city, med_city = fit.groupby(cf).y.mean(), fit.groupby(cf).y.median()
    clim = fit.groupby([cf, fit.Date_target.dt.month]).y.median()
    return {CITY_MEAN: cn.map(mean_city).to_numpy(float),
            CLIM: np.array([clim.get((c, m), med_city[c]) for c, m in zip(cn, new.Date_target.dt.month)], float),
            PERSIST: new.AQI.to_numpy(float)}


def counts(y_true, flag):
    y, f = np.asarray(y_true, bool), np.asarray(flag, bool)
    return int((y & f).sum()), int((~y & f).sum()), int((y & ~f).sum()), int((~y & ~f).sum())


def alert_row(y_true, flag):
    tp, fp, fn, tn = counts(y_true, flag)
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "recall": tp / (tp + fn) if tp + fn else np.nan,
            "precision": tp / (tp + fp) if tp + fp else np.nan, "F1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else np.nan}


def f_beta(y_true, flag, beta=2.0):
    tp, fp, fn, _ = counts(y_true, flag)
    den = (1 + beta ** 2) * tp + beta ** 2 * fn + fp
    return (1 + beta ** 2) * tp / den if den else 0.0


def best_threshold(y_true, score):
    vals = np.array([f_beta(y_true, score >= t) for t in THR_GRID])
    return float(THR_GRID[int(np.argmax(vals))])                      # hòa -> ngưỡng nhỏ hơn


def reg_row(y, p, poor=POOR):
    y, p = np.asarray(y, float), np.asarray(p, float); h = y >= poor
    sst = ((y - y.mean()) ** 2).sum()
    return {"n": len(y), "ngay_nang": int(h.sum()), "MAE": float(np.mean(np.abs(y - p))), "RMSE": float(np.sqrt(np.mean((y - p) ** 2))),
            "R2": float(1 - ((y - p) ** 2).sum() / sst) if sst > 0 else np.nan,
            "MAE_ngay_nang": float(np.mean(np.abs(y[h] - p[h]))) if h.any() else np.nan,
            "MAE_con_lai": float(np.mean(np.abs(y[~h] - p[~h]))) if (~h).any() else np.nan}


def blocks_of(date_target, days=14):
    dt = pd.Series(pd.to_datetime(date_target)).reset_index(drop=True)
    return ((dt - dt.min()).dt.days // days).to_numpy()


def block_boot(blocks, S, stat, B=4000, seed=0):
    """Bootstrap theo khối trên các đại lượng cộng được theo dòng. Trả (ước lượng, lo, hi) 95% phân vị."""
    S = np.asarray(S, float)
    ub, inv = np.unique(np.asarray(blocks), return_inverse=True)
    nb = len(ub)
    agg = np.zeros((nb, S.shape[1])); np.add.at(agg, inv, S)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, nb, (B, nb))
    cnt = np.zeros((B, nb)); np.add.at(cnt, (np.arange(B)[:, None], idx), 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        boot = stat(cnt @ agg); point = stat(agg.sum(0, keepdims=True))[0]
    boot = boot[np.isfinite(boot)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return float(point), float(lo), float(hi), nb


def mae_diff(blocks, err_a, err_b):
    S = np.column_stack([err_a, err_b, np.ones(len(err_a))])
    return block_boot(blocks, S, lambda s: (s[:, 0] - s[:, 1]) / s[:, 2])


def alert_diff(blocks, y_true, fa, fb, metric):
    y = np.asarray(y_true, bool); cols = []
    for f in (np.asarray(fa, bool), np.asarray(fb, bool)):
        cols += [y & f, ~y & f, y & ~f]

    def one(tp, fp, fn):
        return tp / (tp + fn) if metric == "recall" else tp / (tp + fp) if metric == "precision" else 2 * tp / (2 * tp + fp + fn)
    return block_boot(blocks, np.column_stack(cols).astype(float), lambda s: one(s[:, 0], s[:, 1], s[:, 2]) - one(s[:, 3], s[:, 4], s[:, 5]))


def verdict(lo, hi):
    return "tách khỏi 0" if (lo > 0 or hi < 0) else "chưa tách được"


def run(ds, levels, tag, hgb_level=None, train_keys=None):
    """Chạy trọn giao thức trên bảng `ds`. levels: dict tên mức -> danh sách đặc trưng (ví dụ {"L1": [...], "L2": [...], "L3": [...]}).
    train_keys: nếu cho (tập (City, Date)), chỉ giữ các dòng train thuộc tập này (thiết kế C).
    Trả dict các DataFrame: split, alpha, metrics, alerts, paired_mae, paired_alert, predictions."""
    d = prepare(ds)
    if train_keys is not None:
        k = pd.MultiIndex.from_frame(d[["City", "Date"]]).isin(train_keys)
        d = d[(d.split != "train") | k].reset_index(drop=True)
    tr = d[d.split == "train"].reset_index(drop=True)
    ev = {"test": d[d.split == "test"].reset_index(drop=True), "holdout": d[d.split == "holdout"].reset_index(drop=True)}
    out = {"split": pd.DataFrame([{"bo": tag, "tap": s, "n": int((d.split == s).sum()), "ngay_nang_y>=201": int(((d.split == s) & (d.y >= POOR)).sum()),
                                   "Date_target_tu": d.Date_target[d.split == s].min(), "Date_target_den": d.Date_target[d.split == s].max()}
                                  for s in ("train", "test", "holdout", "ngoài phạm vi") if (d.split == s).any()])}
    # ---- alpha và ngưỡng: chỉ trên train
    arows, alpha, thr = [], {}, {}
    ytr = (tr.y >= POOR).to_numpy()
    for lv, feats in levels.items():
        cv = {a: cv_mae(tr, feats, alpha=a) for a in ALPHAS}
        alpha[lv] = min(cv, key=lambda a: cv[a])                       # hòa -> alpha nhỏ hơn (thứ tự lưới tăng dần)
        idx, p = oof(tr, feats, alpha=alpha[lv])
        thr[f"Ridge {lv}"] = best_threshold(ytr[idx], p)
        arows.append({"bo": tag, "mo_hinh": f"Ridge {lv}", "alpha": alpha[lv], "nguong_F2": thr[f"Ridge {lv}"], "n_OOF": len(idx),
                      **{f"cvMAE_alpha_{a}": cv[a] for a in ALPHAS}})
    idx0 = np.concatenate([b for _, b in cv_folds(tr)])
    thr[PERSIST] = best_threshold(ytr[idx0], tr.AQI.to_numpy()[idx0])
    arows.append({"bo": tag, "mo_hinh": PERSIST, "alpha": np.nan, "nguong_F2": thr[PERSIST], "n_OOF": len(idx0)})
    best_hgb = None
    if hgb_level:
        cvh = [cv_mae(tr, levels[hgb_level], model="hgb", **kw) for kw in HGB_GRID]
        best_hgb = HGB_GRID[int(np.argmin(cvh))]
        arows.append({"bo": tag, "mo_hinh": f"HGB {hgb_level}", "alpha": np.nan, "nguong_F2": np.nan, "n_OOF": np.nan, "ghi_chu": str(best_hgb)})
    out["alpha"] = pd.DataFrame(arows)
    # ---- dự đoán và chỉ số
    mrows, alrows, pm, pa, preds = [], [], [], [], []
    for sname, e in ev.items():
        if not len(e):
            continue
        P = baselines(tr, e)
        for lv, feats in levels.items():
            P[f"Ridge {lv}"] = _fit_pred(tr, e, feats, alpha=alpha[lv])
        if hgb_level:
            P[f"HGB {hgb_level}"] = _fit_pred(tr, e, levels[hgb_level], model="hgb", **best_hgb)
        y = e.y.to_numpy(float); yb = y >= POOR
        for k, p in P.items():
            mrows.append({"bo": tag, "tap": sname, "mo_hinh": k, **reg_row(y, p)})
        for k in [PERSIST] + [f"Ridge {lv}" for lv in levels]:
            for lab, t in (("201", POOR), ("F2", thr[k])):
                alrows.append({"bo": tag, "tap": sname, "mo_hinh": k, "loai_nguong": lab, "nguong": t, **alert_row(yb, P[k] >= t)})
        for days in (14, 7, 28):
            bl = blocks_of(e.Date_target, days)
            for a, b in MAE_PAIRS:
                if a in P and b in P:
                    dlt, lo, hi, nb = mae_diff(bl, np.abs(y - P[a]), np.abs(y - P[b]))
                    pm.append({"bo": tag, "tap": sname, "khoi_ngay": days, "so_khoi": nb, "A": a, "B": b, "dMAE": dlt, "lo": lo, "hi": hi, "ket_luan": verdict(lo, hi)})
            if "Ridge L3" in P and sname == "test":
                for lab in ("201", "F2"):
                    fa, fb = P["Ridge L3"] >= (POOR if lab == "201" else thr["Ridge L3"]), P[PERSIST] >= (POOR if lab == "201" else thr[PERSIST])
                    for met in ("recall", "precision", "F1"):
                        dlt, lo, hi, nb = alert_diff(bl, yb, fa, fb, met)
                        pa.append({"bo": tag, "tap": sname, "khoi_ngay": days, "so_khoi": nb, "A": f"Ridge L3 @{lab}", "B": f"{PERSIST} @{lab}", "chi_so": met,
                                   "delta": dlt, "lo": lo, "hi": hi, "ket_luan": verdict(lo, hi)})
        preds.append(e[["City", "Date", "Date_target", "split", "AQI", "y"]].assign(**{f"pred_{k}": v for k, v in P.items()}))
    out.update(metrics=pd.DataFrame(mrows), alerts=pd.DataFrame(alrows), paired_mae=pd.DataFrame(pm), paired_alert=pd.DataFrame(pa),
               predictions=pd.concat(preds, ignore_index=True) if preds else pd.DataFrame(), thresholds=thr, alphas=alpha)
    return out


def compare_codes(pred_old, pred_new, thr_old=None, thr_new=None, models=(PERSIST, "Ridge L1", "Ridge L2", "Ridge L3")):
    """Thiết kế B: mã mới so với mã cũ trên CÙNG khóa và CÙNG nhãn. pred_*: bảng predictions của run(). Trả bảng hiệu MAE + số dòng đổi cờ."""
    key = ["City", "Date"]
    m = pred_old.merge(pred_new, on=key, suffixes=("_old", "_new"), validate="1:1")
    same = m[np.isclose(m.y_old, m.y_new, rtol=0, atol=0)]
    rows = []
    for sname, e in same.groupby("split_old"):
        y = e.y_old.to_numpy(float)
        for days in (14, 7, 28):
            bl = blocks_of(e.Date_target_old, days)
            for k in models:
                a, b = e[f"pred_{k}_new"].to_numpy(float), e[f"pred_{k}_old"].to_numpy(float)
                dlt, lo, hi, nb = mae_diff(bl, np.abs(y - a), np.abs(y - b))
                r = {"tap": sname, "khoi_ngay": days, "so_khoi": nb, "mo_hinh": k, "n_cung_khoa_cung_nhan": len(e), "MAE_moi": float(np.mean(np.abs(y - a))),
                     "MAE_cu": float(np.mean(np.abs(y - b))), "dMAE_moi_tru_cu": dlt, "lo": lo, "hi": hi, "ket_luan": verdict(lo, hi),
                     "so_dong_doi_co_@201": int(((a >= POOR) != (b >= POOR)).sum())}
                if thr_old and thr_new:
                    r["so_dong_doi_co_@F2"] = int(((a >= thr_new[k]) != (b >= thr_old[k])).sum())
                rows.append(r)
    info = {"n_khoa_chung": len(m), "n_nhan_khac": int(len(m) - len(same)), "n_chi_o_cu": int(len(pred_old) - len(m)), "n_chi_o_moi": int(len(pred_new) - len(m))}
    return pd.DataFrame(rows), info
