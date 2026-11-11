"""DA — bản sao GIAO THỨC mô hình của notebook 06 (không sửa src/): mọi fit / chọn alpha / chọn ngưỡng chỉ trên train (OOF),
test chỉ để báo cáo. Dùng lại nguyên hàm của tác giả trong src/model_utils.py; ở đây chỉ gom thành hàm để chạy lại trên các biến thể
(bảng sạch khác, ngưỡng AQI khác, bỏ thành phố/mùa, đặc trưng thời gian thực).
"""
from da_clean import *
import model_utils as M

ALPHAS = [0.1, 1, 10, 30, 100, 300]                      # đúng lưới của NB06 c10
HGB_GRID = [dict(max_depth=d, max_iter=n, learning_rate=0.05, min_samples_leaf=40) for d in (2, 3) for n in (100, 200)]
PERSIST = "Ngày mai = hôm nay"; BASES = ["Trung bình theo thành phố", "Trung vị cùng tháng (khí hậu)", PERSIST]


def splits(ds):
    return (ds[ds.split == "train"].reset_index(drop=True), ds[ds.split == "test"].reset_index(drop=True), ds[ds.split == "lockdown"].reset_index(drop=True))


def choose_alpha(tr, levels):
    cv = {lv: {a: M.cv_score(tr, M.LEVELS[lv], lambda a=a, f=M.LEVELS[lv]: M.make_pipe(f, "ridge", alpha=a)) for a in ALPHAS} for lv in levels}
    return {lv: min(v, key=lambda a: v[a][0]) for lv, v in cv.items()}, cv


def choose_hgb(tr, lv="L3"):
    cv = [M.cv_score(tr, M.LEVELS[lv], lambda kw=kw, f=M.LEVELS[lv]: M.make_pipe(f, "hgb", **kw)) for kw in HGB_GRID]
    return HGB_GRID[int(np.argmin([m for m, _ in cv]))], cv


def fit_predict(tr, new, feats, alpha, model="ridge", **kw):
    m = M.make_pipe(feats, model, alpha=alpha, **kw) if model == "ridge" else M.make_pipe(feats, "hgb", **kw)
    m.fit(tr[feats + ["City"]], tr.y_log)
    return np.exp(m.predict(new[feats + ["City"]]))


def score_row(d, p, poor):
    y = d.y.to_numpy(float); h = y >= poor
    return {"n": len(y), "ngay_nang": int(h.sum()), "MAE": M.mae(y, p), "RMSE": M.rmse(y, p), "R2": M.r2(y, p) if len(y) > 1 else np.nan,
            "MAE_ngay_nang": M.mae(y[h], p[h]) if h.any() else np.nan, "MAE_con_lai": M.mae(y[~h], p[~h]) if (~h).any() else np.nan}


def alert_row(y_true, flag, blocks=None, B=4000):
    m = M.alert_metrics(y_true, flag)
    r = {"recall": m["recall"], "precision": m["precision"], "F1": m["F1"], "TP": m["TP"], "FP": m["FP"], "FN": m["FN"], "TN": m["TN"]}
    if blocks is not None and m["TP"] > 0:
        for met in ("recall", "precision"):
            _, lo, hi = M.boot_alert_ci(blocks, y_true, flag, met, B=B); r[f"{met}_lo"], r[f"{met}_hi"] = lo, hi
    return r


def run_protocol(ds, poor=201, levels=("L1", "L2", "L3", "L4"), hgb=False, B=4000, alphas=None, thresholds=True, block_days=14):
    """Trả dict: best_alpha, test_tab, lock_tab, mdiff, thr, alert_tab, pred_te, pred_lk, te, lk, tr."""
    ds = ds.copy(); ds["y_poor"] = ds.y >= poor; ds["today_poor"] = ds.AQI >= poor
    tr, te, lk = splits(ds)
    out = {"tr": tr, "te": te, "lk": lk, "poor": poor}
    if alphas is None: alphas, out["cv_ridge"] = choose_alpha(tr, levels)
    out["best_alpha"] = alphas
    pred_te, pred_lk = dict(M.baseline_preds(tr, te)), dict(M.baseline_preds(tr, lk)) if len(lk) else {}
    for lv in levels:
        f = M.LEVELS[lv]
        m = M.make_pipe(f, "ridge", alpha=alphas[lv]).fit(tr[f + ["City"]], tr.y_log)
        pred_te[f"Ridge {lv}"] = np.exp(m.predict(te[f + ["City"]]))
        if len(lk): pred_lk[f"Ridge {lv}"] = np.exp(m.predict(lk[f + ["City"]]))
    if hgb:
        kw, out["cv_hgb"] = choose_hgb(tr, "L3"); out["best_hgb"] = kw
        m = M.make_pipe(M.LEVELS["L3"], "hgb", **kw).fit(tr[M.LEVELS["L3"] + ["City"]], tr.y_log)
        pred_te["HGB L3"] = np.exp(m.predict(te[M.LEVELS["L3"] + ["City"]]))
        if len(lk): pred_lk["HGB L3"] = np.exp(m.predict(lk[M.LEVELS["L3"] + ["City"]]))
    out["pred_te"], out["pred_lk"] = pred_te, pred_lk
    out["test_tab"] = pd.DataFrame({k: score_row(te, p, poor) for k, p in pred_te.items()}).T
    if len(lk): out["lock_tab"] = pd.DataFrame({k: score_row(lk, p, poor) for k, p in pred_lk.items()}).T
    bl = M.calendar_blocks(te.Date_target, days=block_days); out["blocks"] = bl
    err = lambda k: np.abs(te.y.to_numpy() - pred_te[k])
    pairs = [(f"Ridge {levels[0]}", PERSIST)] + [(f"Ridge {b}", f"Ridge {a}") for a, b in zip(levels[:-1], levels[1:])]
    if "L3" in levels: pairs.append(("Ridge L3", PERSIST))
    if hgb: pairs.append(("HGB L3", "Ridge L3"))
    out["mdiff"] = pd.DataFrame([{"A": a, "B": b, **dict(zip(("dMAE", "lo", "hi"), M.boot_mae_diff(bl, err(a), err(b), B=B)))} for a, b in pairs])
    if thresholds:
        y_tr, y_te = tr.y_poor.to_numpy(), te.y_poor.to_numpy()
        oof = {lv: M.oof_predict(tr, M.LEVELS[lv], lambda f=M.LEVELS[lv], lv=lv: M.make_pipe(f, "ridge", alpha=alphas[lv])) for lv in levels}
        idx = oof[levels[0]][0]
        # best_threshold của tác giả: so y_true với score >= t; y_true ở đây theo ngưỡng `poor`
        thr = {f"Ridge {lv}": M.best_threshold(y_tr[idx], oof[lv][1])[0] for lv in levels}
        thr[PERSIST] = M.best_threshold(y_tr[idx], tr.AQI.to_numpy()[idx])[0]
        out["thr"] = thr; out["n_oof"], out["oof_heavy"] = len(idx), int(y_tr[idx].sum())
        rows = {}
        for k in [PERSIST] + [f"Ridge {lv}" for lv in levels]:
            sc = te.AQI.to_numpy() if k == PERSIST else pred_te[k]
            rows[f"{k} @{poor}"] = {"nguong": poor, **alert_row(y_te, sc >= poor, bl, B)}
            rows[f"{k} @F2"] = {"nguong": thr[k], **alert_row(y_te, sc >= thr[k], bl, B)}
        out["alert_tab"] = pd.DataFrame(rows).T
    return out
