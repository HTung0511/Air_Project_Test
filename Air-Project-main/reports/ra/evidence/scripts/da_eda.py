"""DA — tính lại các con số EDA chính của notebook 03 trên một bảng sạch bất kỳ (đúng công thức NB03 c8/c14/c35/c38)."""
from da_common import *
USABLE = ["PM2.5", "NO2", "CO", "SO2", "O3"]


def prep(clean_df, poor=201):
    e = clean_df.copy(); e["Date"] = pd.to_datetime(e["Date"]); e["City"] = e.City.astype(str)
    e["year"], e["month"] = e.Date.dt.year, e.Date.dt.month; e["poor"] = e.AQI >= poor
    start = e.groupby("City").Date.min().max(); end = e.groupby("City").Date.max().min()
    return e, e[(e.Date >= start) & (e.Date <= end)].copy(), start, end


def eda_metrics(d, min_heavy=100):
    """d: bảng đã có cột poor (bool), đã cắt theo cửa sổ mong muốn. Trả dict số liệu chính (mẫu = ngày có AQI)."""
    d = d.dropna(subset=["AQI"]); g = d.groupby("City")
    r = {"n_ngay_co_AQI": len(d), "n_ngay_nang": int(d.poor.sum())}
    share = g.poor.mean() * 100; n = g.size(); h = g.poor.sum()
    for c in CITIES:
        r[f"pct_{c}"] = share.get(c, np.nan); r[f"n_{c}"] = int(n.get(c, 0)); r[f"nang_{c}"] = int(h.get(c, 0))
    r["thu_hang"] = ">".join(share.reindex(CITIES).sort_values(ascending=False).index)
    big = [c for c in CITIES if h.get(c, 0) >= min_heavy]; r["TP_du_ngay_nang"] = ",".join(big)
    rat = {c: d[(d.City == c) & d.poor]["PM2.5"].median() / d[(d.City == c) & ~d.poor]["PM2.5"].median() for c in big}
    for c in big: r[f"ratio_PM25_{c}"] = rat[c]
    r["ratio_PM25_trung_vi_cac_TP"] = float(np.median(list(rat.values()))) if rat else np.nan
    pm = d.groupby("poor")["PM2.5"].median(); r["PM25_median_nang_gop"], r["PM25_median_conlai_gop"] = pm.get(True, np.nan), pm.get(False, np.nan)
    r["ratio_cua_2_median_gop"] = r["PM25_median_nang_gop"] / r["PM25_median_conlai_gop"]
    co = d[USABLE + ["AQI"]].corr(method="spearman")["AQI"]
    for p in USABLE: r[f"spearman_{p}"] = co[p]; r[f"n_cap_{p}"] = int(d[p].notna().sum())
    r["pct_ngay_nang_thang_10_2"] = d[d.poor].month.isin([10, 11, 12, 1, 2]).mean() * 100 if d.poor.any() else np.nan
    r["nang_PM25_duoi_91"] = int((d.poor & (d["PM2.5"] < 91)).sum())
    dl = d[d.City == "Delhi"].groupby("month").AQI.median()
    r["Delhi_median_T12"], r["Delhi_median_T8"] = dl.get(12, np.nan), dl.get(8, np.nan)
    return r


def month_table(d):
    d = d.dropna(subset=["AQI"])
    return d.pivot_table(index="City", columns="month", values="AQI", aggfunc="median").reindex(CITIES)
