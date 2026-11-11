"""DA — bọc pipeline của tác giả để chạy trên raw đã CẮT/ĐỔI trong bộ nhớ (không sửa src, không ghi baseline).

fast_ratio: bản vector hoá của gap_utils.contextual_ratio (đã assert trùng từng giá trị với bản gốc, xem v02 phần 0);
chỉ dùng để tăng tốc khi phải làm sạch lại hàng nghìn lần. Logic, ngưỡng, thứ tự bước giữ nguyên của pipeline.py.
"""
from da_common import *
import pipeline as P, utils as U, gap_utils as G
from numpy.lib.stride_tricks import sliding_window_view

_ORIG_RATIO = G.contextual_ratio


def fast_ratio(s, window=15, min_periods=5):
    vals = s.to_numpy(dtype=float); n = len(vals); half = window // 2
    pad = np.concatenate([np.full(half, np.nan), vals, np.full(half, np.nan)])
    W = sliding_window_view(pad, window).copy(); W[:, half] = np.nan
    cnt = (~np.isnan(W)).sum(1)
    med = np.full(n, np.nan); ok = cnt > 0
    med[ok] = np.nanmedian(W[ok], axis=1)
    o = np.full(n, np.nan)
    good = (cnt >= min_periods - 1) & ~np.isnan(vals) & (med > 0)
    o[good] = vals[good] / med[good]
    return pd.Series(o, index=s.index)


def load_raw():
    r = pd.read_csv(RAW); r["Date"] = pd.to_datetime(r["Date"])
    return r[r.City.isin(CITIES)].sort_values(["City", "Date"]).reset_index(drop=True)


def clean_city_df(city_df, city, max_gap=14, flat_run=3, suspect="current", fast=True, top=5):
    """Như pipeline.clean_city nhưng nhận DataFrame (đã cắt/đổi) và cho đổi tham số để thử độ nhạy.
    suspect: 'current' (đặt NaN như tác giả) | 'flag_only' (chỉ gắn cờ, giữ giá trị) | 'none' (không chạy luật)."""
    P.contextual_ratio = fast_ratio if fast else _ORIG_RATIO
    d = city_df.sort_values("Date").reset_index(drop=True)
    d, _ = U.impute_time_series(d, city, drop_cols=["Xylene"], verbose=False, max_short_gap=max_gap, flatline_min_run=flat_run)
    d = d.drop(columns=[c for c in d.columns if c.startswith("Xylene")])
    no_gas = not any(d[g].notna().any() for g in P.GASES if g in d.columns)
    if suspect == "none" or len(d) == 0 or no_gas:
        # no_gas: chuỗi chưa có chất nào (vd Jaipur 14–18/06/2017 khi cắt raw) -> pipeline.investigate của tác giả ném KeyError
        # (R rỗng có RangeIndex). Không chạy được luật nghi lỗi => coi như không có điểm nghi lỗi. Ghi ở NEW-002.
        d["suspect_sensor_error"] = False; ev = pd.DataFrame()
    else:
        dd = d.set_index("Date").copy()
        r25 = P.investigate(dd, "PM2.5", top=top)
        sus = [t for t in r25.loc[r25.suggestion.str.startswith("NGHI"), "date"]] if len(r25) else []
        rq = P.investigate(dd, "AQI", top=top, skip_pm25=sus, extra_dates=sus)
        res = pd.concat([r25, rq], ignore_index=True)
        is_sus = res.suggestion.str.startswith("NGHI") if len(res) else pd.Series([], dtype=bool)
        dd["suspect_sensor_error"] = False
        for _, r in res[is_sus].iterrows():
            if suspect == "current":
                dd.loc[r.date, r.column] = np.nan
                if r.column == "AQI": dd.loc[r.date, "AQI_Bucket"] = np.nan
            dd.loc[r.date, "suspect_sensor_error"] = True
        ev = res.assign(action=np.where(is_sus, "đặt NaN", "giữ nguyên")); ev.insert(0, "city", city)
        d = dd.reset_index()
    d = U.flag_outliers_iqr(d, cols=POLLUTANTS)
    return d, ev


def clean_all(raw8, **kw):
    frames, evs = [], []
    for c in CITIES:
        f, e = clean_city_df(raw8[raw8.City == c], c, **kw); frames.append(f); evs.append(e)
    return P.merge_cities(frames), (pd.concat(evs, ignore_index=True) if any(len(e) for e in evs) else pd.DataFrame())


def features_from(clean_df, mask_interp=True, as_of=None, tag="tmp"):
    """model_utils.make_features trên một bảng sạch khác (ghi CSV tạm ở scratch rồi trỏ eda_utils.DATA sang đó)."""
    import eda_utils as E, model_utils as M
    p = SCRATCH / f"clean_{tag}_{os.getpid()}.csv"; clean_df.to_csv(p, index=False)
    old = E.DATA; E.DATA = p
    try:
        return M.make_features(mask_interp=mask_interp, as_of=as_of)
    finally:
        E.DATA = old; p.unlink(missing_ok=True)


def dataset_from(clean_df, mask_interp=True, tag="tmp"):
    import eda_utils as E, model_utils as M
    p = SCRATCH / f"clean_{tag}_{os.getpid()}.csv"; clean_df.to_csv(p, index=False)
    old = E.DATA; E.DATA = p
    try:
        return M.build_dataset(mask_interp=mask_interp, verbose=False)
    finally:
        E.DATA = old; p.unlink(missing_ok=True)
