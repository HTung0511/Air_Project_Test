"""V14–V17 [Q05] Ba phát hiện EDA (ở đâu / khi nào / chất nào): tái tính có tử/mẫu, các cửa sổ thời gian, bỏ 10%×200,
bootstrap khối lịch 7/14/28 ngày (khối chung giữa các TP), xác suất đổi hạng, coverage 26 TP. Ngưỡng `poor` đổi được (S01 dùng 151).
Chạy: python v14_eda.py [poor=201]
"""
from da_eda import *
POOR = int(sys.argv[1]) if len(sys.argv) > 1 else 201
TAG = "" if POOR == 201 else f"_thr{POOR}"; PRE = "V" if POOR == 201 else "S01_V"
base = pd.read_csv(CLEAN, parse_dates=["Date"]); e, win, START, END = prep(base, POOR)
GROUPS = {"cao": ["Delhi", "Lucknow", "Gurugram"], "giữa": ["Amritsar", "Jaipur"], "thấp": ["Chennai", "Bengaluru", "Hyderabad"]}
print(f"Ngưỡng ngày nặng: AQI ≥ {POOR} | khoảng chung {START.date()} → {END.date()} | {len(win)} dòng, {int(win.AQI.notna().sum())} ngày có AQI")

# ---------- V14a: tử/mẫu theo các cửa sổ
alld = pd.date_range(START, END); piv = win.pivot(index="Date", columns="City", values="AQI").reindex(alld)
complete_days = piv.dropna().index
WINS = {"toàn chuỗi mỗi TP (2015–2020, độ dài khác nhau)": e,
        f"khoảng chung {START:%d/%m/%Y}–{END:%d/%m/%Y} (NB03)": win,
        "khoảng chung, trước 01/03/2020 (mốc holdout của code)": win[win.Date < "2020-03-01"],
        "khoảng chung, trước 25/03/2020 (ngày phong toả toàn quốc)": win[win.Date < "2020-03-25"],
        "khoảng chung, chỉ ngày cả 8 TP cùng có AQI": win[win.Date.isin(complete_days)],
        "khoảng chung, 3 năm tròn 01/07/2017–30/06/2020 (mỗi tháng lịch đúng 3 lần)": win[(win.Date >= "2017-07-01") & (win.Date <= "2020-06-30")]}
rows = []
for nm, d in WINS.items():
    m = eda_metrics(d); r = {"cua_so": nm, "tu": d.Date.min().date(), "den": d.Date.max().date(), "n_ngay_co_AQI": m["n_ngay_co_AQI"], "n_ngay_nang": m["n_ngay_nang"]}
    for c in CITIES: r[c] = f"{m[f'nang_{c}']}/{m[f'n_{c}']} = {m[f'pct_{c}']:.1f}%"
    r["thu_hang"] = m["thu_hang"]; r["ratio_PM25_trung_vi_TP"] = m["ratio_PM25_trung_vi_cac_TP"]; r["TP_tinh_ratio"] = m["TP_du_ngay_nang"]
    r["ratio_2_median_gop"] = m["ratio_cua_2_median_gop"]; r["PM25_median_nang/conlai_gop"] = f"{m['PM25_median_nang_gop']:.1f}/{m['PM25_median_conlai_gop']:.1f}"
    r["spearman_PM2.5"] = m["spearman_PM2.5"]; r["pct_ngay_nang_T10-2"] = m["pct_ngay_nang_thang_10_2"]; r["Delhi_median_T12/T8"] = f"{m['Delhi_median_T12']:.0f}/{m['Delhi_median_T8']:.0f}"
    rows.append(r)
wt = pd.DataFrame(rows); save(wt.round(4), f"{PRE}14_eda_share_by_window{TAG}.csv", index=False); print(wt.T.to_string())

# ---------- V14b: bỏ 10% × 200 (đúng NB03 c8, seed 42)
share = lambda d: d.dropna(subset=["AQI"]).groupby("City").poor.mean().reindex(CITIES) * 100
rng = np.random.default_rng(42); b0 = share(win)
runs = pd.DataFrame([share(win.sample(frac=0.9, random_state=int(rng.integers(1e9)))) for _ in range(200)])
stable = (runs.rank(axis=1, ascending=False) == b0.rank(ascending=False)).mean() * 100
d10 = pd.DataFrame({"pct_goc": b0, "nho_nhat": runs.min(), "lon_nhat": runs.max(), "thu_hang_giu_nguyen_%": stable}).sort_values("pct_goc", ascending=False)
save(d10.round(2), f"{PRE}14_eda_drop10_x200{TAG}.csv"); print(d10.round(1).to_string())

# ---------- V14c: bootstrap khối lịch chung 7/14/28 ngày (B=4000, seed 0)
d = win.dropna(subset=["AQI"]).copy(); ci = {c: i for i, c in enumerate(CITIES)}
def group_of(sh):   # nhóm theo ngưỡng cố định của giá trị gốc? -> dùng thứ tự: 3 TP cao nhất / 2 giữa / 3 thấp
    order = np.argsort(-sh, axis=1); return order
boot_rows, rank_rows = [], []
for L in (7, 14, 28):
    blk = ((d.Date - START).dt.days // L).to_numpy(); nb = blk.max() + 1
    H = np.zeros((nb, 8)); N = np.zeros((nb, 8)); cidx = d.City.map(ci).to_numpy()
    np.add.at(H, (blk, cidx), d.poor.to_numpy(float)); np.add.at(N, (blk, cidx), 1.0)
    rng = np.random.default_rng(0); B = 4000; idx = rng.integers(0, nb, (B, nb)); cnt = np.zeros((B, nb)); np.add.at(cnt, (np.arange(B)[:, None], idx), 1)
    sh = (cnt @ H) / (cnt @ N) * 100; base_sh = H.sum(0) / N.sum(0) * 100
    lo, hi = np.percentile(sh, [2.5, 97.5], axis=0); order = np.argsort(-sh, axis=1); base_order = np.argsort(-base_sh)
    rank = np.argsort(order, axis=1); base_rank = np.argsort(base_order)
    top3 = np.array([set(o[:3]) == {ci[c] for c in GROUPS["cao"]} for o in order]).mean() * 100
    mid2 = np.array([set(o[3:5]) == {ci[c] for c in GROUPS["giữa"]} for o in order]).mean() * 100
    low3 = np.array([set(o[5:]) == {ci[c] for c in GROUPS["thấp"]} for o in order]).mean() * 100
    for c in CITIES:
        j = ci[c]; boot_rows.append({"do_dai_khoi_ngay": L, "so_khoi": int(nb), "City": c, "pct": base_sh[j], "CI95_lo": lo[j], "CI95_hi": hi[j], "hang_goc": int(base_rank[j]) + 1,
                                     "P(giu_hang)_%": (rank[:, j] == base_rank[j]).mean() * 100, "P(hang_1)_%": (rank[:, j] == 0).mean() * 100})
    pairs = [("Delhi", "Lucknow"), ("Delhi", "Gurugram"), ("Lucknow", "Gurugram"), ("Amritsar", "Jaipur"), ("Jaipur", "Chennai"), ("Gurugram", "Amritsar"), ("Bengaluru", "Hyderabad"), ("Chennai", "Bengaluru")]
    r = {"do_dai_khoi_ngay": L, "so_khoi": int(nb), "P(3 TP cao nhất = Delhi,Lucknow,Gurugram)_%": top3, "P(2 TP giữa = Amritsar,Jaipur)_%": mid2, "P(3 TP thấp = Chennai,Bengaluru,Hyderabad)_%": low3,
         "P(giữ nguyên toàn bộ thứ hạng)_%": (order == base_order).all(axis=1).mean() * 100}
    for a, b in pairs:
        df_ = sh[:, ci[a]] - sh[:, ci[b]]; l2, h2 = np.percentile(df_, [2.5, 97.5]); r[f"{a}−{b} (điểm %)"] = f"{base_sh[ci[a]] - base_sh[ci[b]]:.1f} [{l2:.1f}; {h2:.1f}] P(>0)={np.mean(df_ > 0) * 100:.0f}%"
    rank_rows.append(r)
bt = pd.DataFrame(boot_rows); rk = pd.DataFrame(rank_rows); save(bt.round(3), f"{PRE}14_eda_block_bootstrap{TAG}.csv", index=False); save(rk.round(2), f"{PRE}14_eda_block_bootstrap_rank{TAG}.csv", index=False)
print(bt.pivot(index="City", columns="do_dai_khoi_ngay", values=["CI95_lo", "CI95_hi", "P(giu_hang)_%"]).reindex(CITIES).round(1).to_string()); print(rk.T.to_string())

# ---------- V15: khi nào (mùa)
mt = month_table(win); pk = pd.DataFrame({"thang_dinh (median cao nhất)": mt.idxmax(axis=1), "median_dinh": mt.max(axis=1), "thang_thap_nhat": mt.idxmin(axis=1), "median_thap": mt.min(axis=1), "ti_so_dinh/thap": mt.max(axis=1) / mt.min(axis=1),
                               "2 thang cao nhat": [",".join(map(str, mt.loc[c].sort_values(ascending=False).index[:2])) for c in mt.index]})
hm = d[d.poor].groupby(["City", "month"]).size().unstack("month", fill_value=0).reindex(CITIES).reindex(columns=range(1, 13), fill_value=0).fillna(0).astype(int)
nm_ = d.groupby(["City", "month"]).size().unstack("month", fill_value=0).reindex(CITIES)
pk["ngay_nang"] = hm.sum(1); pk["%_ngay_nang_T10-12"] = hm[[10, 11, 12]].sum(1) / hm.sum(1) * 100; pk["%_ngay_nang_T11-12"] = hm[[11, 12]].sum(1) / hm.sum(1) * 100; pk["%_ngay_nang_T10-2"] = hm[[10, 11, 12, 1, 2]].sum(1) / hm.sum(1) * 100
pk["%_ngay_T11-12_la_nang"] = hm[[11, 12]].sum(1) / nm_[[11, 12]].sum(1) * 100; pk["%_ngay_T7-9_la_nang"] = hm[[7, 8, 9]].sum(1) / nm_[[7, 8, 9]].sum(1) * 100
save(mt.round(1), f"{PRE}15_eda_month_median{TAG}.csv"); save(pk.round(2), f"{PRE}15_eda_peak_months{TAG}.csv"); save(hm, f"{PRE}15_eda_heavy_days_by_month{TAG}.csv"); save(nm_, f"{PRE}15_eda_aqi_days_by_month{TAG}.csv")
print(mt.round(0).to_string()); print(pk.round(1).to_string()); print("ngày nặng theo tháng:\n", hm.to_string()); print("tổng theo tháng:", hm.sum().to_dict(), "| % T11–12:", round(hm[[11, 12]].sum().sum() / hm.sum().sum() * 100, 1), "| % T10–2:", round(hm[[10, 11, 12, 1, 2]].sum().sum() / hm.sum().sum() * 100, 1))
# mỗi năm riêng: tháng đỉnh của Delhi/Lucknow/Gurugram
yy = d.assign(season_year=np.where(d.month >= 7, d.year, d.year - 1))
pm_y = yy.groupby(["City", "season_year", "month"]).AQI.median().reset_index()
pky = pm_y.loc[pm_y.groupby(["City", "season_year"]).AQI.idxmax()].pivot(index="City", columns="season_year", values="month").reindex(CITIES); save(pky, f"{PRE}15_eda_peak_month_by_season_year{TAG}.csv")
print("tháng đỉnh theo từng năm-mùa (07→06):\n", pky.to_string())
# bootstrap khối 14 ngày: xác suất tháng đỉnh thuộc {11,12,1}
blk = ((d.Date - START).dt.days // 14).to_numpy(); nb = blk.max() + 1; rng = np.random.default_rng(0); res = {c: [] for c in CITIES}
groups = [d[blk == k] for k in range(nb)]
for _ in range(500):
    s = pd.concat([groups[k] for k in rng.integers(0, nb, nb)]); t = s.pivot_table(index="City", columns="month", values="AQI", aggfunc="median").reindex(CITIES)
    for c in CITIES: res[c].append(int(t.loc[c].idxmax()))
pb = pd.DataFrame({c: pd.Series(v).value_counts(normalize=True).mul(100).round(1) for c, v in res.items()}).T.reindex(columns=range(1, 13)).fillna(0)
pb["P(đỉnh ∈ {11,12})_%"] = pb[[11, 12]].sum(1); pb["P(đỉnh ∈ {11,12,1})_%"] = pb[[11, 12, 1]].sum(1); save(pb, f"{PRE}15_eda_peak_month_bootstrap{TAG}.csv"); print(pb.to_string())

# ---------- V16: chất nào
big = [c for c in CITIES if int(d[d.City == c].poor.sum()) >= 100]
rows = []
for c in CITIES:
    x = d[d.City == c]; r = {"City": c, "n_ngay_AQI": len(x), "n_nang": int(x.poor.sum()), "du_100_ngay_nang": c in big}
    for p in USABLE:
        hv, ot = x[x.poor][p].dropna(), x[~x.poor][p].dropna()
        r[f"{p}_n_nang/n_conlai"] = f"{len(hv)}/{len(ot)}"; r[f"{p}_median_nang"], r[f"{p}_median_conlai"] = hv.median(), ot.median()
        r[f"{p}_ratio"] = hv.median() / ot.median() if len(hv) and len(ot) else np.nan
        r[f"{p}_spearman_AQI"] = x[p].corr(x.AQI, method="spearman"); r[f"{p}_n_cap"] = int(x[p].notna().sum()); r[f"{p}_noi_suy_%"] = (x[f"{p}_was_missing"] & x[p].notna()).mean() * 100
    rows.append(r)
pt = pd.DataFrame(rows).set_index("City"); save(pt.round(4), f"{PRE}16_eda_pollutant_by_city{TAG}.csv")
rr = pt.loc[big, [f"{p}_ratio" for p in USABLE]]; print("ratio trung vị ngày nặng / ngày còn lại, theo TP:\n", rr.round(2).to_string()); print("trung vị giữa các TP:", rr.median().round(2).to_dict())
pooled = {p: (d[d.poor][p].median(), d[~d.poor][p].median()) for p in USABLE}
summ = pd.DataFrame({"trung_vi_cua_ratio_cac_TP_du_ngay_nang": rr.median().values, "min_TP": rr.min().values, "max_TP": rr.max().values,
                     "median_gop_nang": [pooled[p][0] for p in USABLE], "median_gop_conlai": [pooled[p][1] for p in USABLE], "ratio_cua_2_median_gop": [pooled[p][0] / pooled[p][1] for p in USABLE],
                     "spearman_gop_8TP": [d[p].corr(d.AQI, method="spearman") for p in USABLE], "spearman_min_TP": [pt[f"{p}_spearman_AQI"].min() for p in USABLE], "spearman_max_TP": [pt[f"{p}_spearman_AQI"].max() for p in USABLE],
                     "spearman_trung_vi_TP": [pt[f"{p}_spearman_AQI"].median() for p in USABLE], "n_cap_gop": [int(d[p].notna().sum()) for p in USABLE]}, index=USABLE)
# bootstrap khối 14 ngày cho ratio PM2.5 từng TP và trung vị các TP
rng = np.random.default_rng(0); bs = []
for _ in range(1000):
    s = pd.concat([groups[k] for k in rng.integers(0, nb, nb)]); g = s.groupby(["City", "poor"])["PM2.5"].median().unstack("poor")
    bs.append((g[True] / g[False]).reindex(big))
bs = pd.DataFrame(bs); summ.loc["PM2.5", "CI95_trung_vi_ratio (khối 14 ngày)"] = f"[{np.percentile(bs.median(axis=1), 2.5):.2f}; {np.percentile(bs.median(axis=1), 97.5):.2f}]"
for c in big: pt.loc[c, "PM2.5_ratio_CI95"] = f"[{np.percentile(bs[c].dropna(), 2.5):.2f}; {np.percentile(bs[c].dropna(), 97.5):.2f}]"
save(summ.round(4), f"{PRE}16_eda_pollutant_summary{TAG}.csv"); save(pt.round(4), f"{PRE}16_eda_pollutant_by_city{TAG}.csv"); print(summ.round(2).T.to_string()); print(pt.loc[big, ["PM2.5_n_nang/n_conlai", "PM2.5_median_nang", "PM2.5_median_conlai", "PM2.5_ratio", "PM2.5_ratio_CI95"]].to_string())
print(pt[[f"{p}_spearman_AQI" for p in USABLE]].round(2).to_string())
low = d[d.poor & (d["PM2.5"] < 91)]; print(f"ngày nặng mà PM2.5 < 91: {len(low)}/{int(d.poor.sum())}; ngày nặng thiếu PM2.5: {int((d.poor & d['PM2.5'].isna()).sum())}")

if POOR == 201:
    # ---------- V17: coverage 26 TP từ raw
    raw = pd.read_csv(RAW, parse_dates=["Date"]); g = raw.groupby("City")
    cv = pd.DataFrame({"n_dong": g.size(), "tu": g.Date.min().dt.date, "den": g.Date.max().dt.date, "AQI_co_%": g.AQI.apply(lambda s: s.notna().mean() * 100), "n_ngay_co_AQI": g.AQI.count(),
                       "PM2.5_co_%": g["PM2.5"].apply(lambda s: s.notna().mean() * 100), "AQI_median": g.AQI.median(), "%_ngay_AQI>=201": g.AQI.apply(lambda s: (s.dropna() >= 201).mean() * 100)})
    w = raw[(raw.Date >= START) & (raw.Date <= END)].groupby("City"); cv["n_dong_trong_khoang_chung"] = w.size(); cv["n_AQI_trong_khoang_chung"] = w.AQI.count(); cv["phu_khoang_chung_%"] = cv.n_AQI_trong_khoang_chung / len(alld) * 100
    cv["duoc_chon_8TP"] = cv.index.isin(CITIES); cv = cv.sort_values("n_ngay_co_AQI", ascending=False); cv["hang_theo_n_ngay_co_AQI"] = range(1, len(cv) + 1)
    save(cv.round(2), "V17_coverage_26_cities.csv"); print(cv.round(1).to_string())
