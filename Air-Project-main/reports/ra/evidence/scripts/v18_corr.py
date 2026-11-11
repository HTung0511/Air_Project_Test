"""V18–V19 [Q06] Tương quan thời tiết–AQI: 48 hệ số (rho, CI chưa hiệu chỉnh, p_boot, q_BH, n, số khối), xếp hạng lại mỗi lần bootstrap,
khối 7/14/28 ngày, anomaly tháng/tuần, bỏ giai đoạn COVID; 3 giả thuyết × 5 TP với family 15 / 3 / không hiệu chỉnh và độ nhạy theo seed.
Dùng nguyên hàm src/corr_utils.py. Chạy: python v18_corr.py
"""
from da_common import *
import corr_utils as C
from scipy import stats

eda, win, START, END = C.load_with_weather(verbose=False)
d = win.dropna(subset=["AQI"]).copy(); core, n_heavy = C.core_cities(d); core = sorted(core, key=lambda c: -n_heavy[c]); WX = C.WX
a = C.add_anomalies(d, ["AQI"] + WX)

# ---------- V18a: 48 hệ số đúng cách tác giả
tab = C.corr_table(a)
raw = C.spearman_by_city(d)
tab["rho_tho"] = [raw.loc[c, v] for c, v in zip(tab.City, tab["var"])]
tab["so_khoi_14_ngay"] = [C.block_id(a[a.City == c]).nunique() for c in tab.City]
tab["CI95_loai_0 (chưa hiệu chỉnh)"] = (tab.lo > 0) | (tab.hi < 0); tab["p_boot<0.05"] = tab.p_boot < 0.05; tab["q_BH<0.05"] = tab.p_fdr < 0.05
tab["doi_dau_tho→bo_mua"] = np.sign(tab.rho_tho) != np.sign(tab.rho)
# Bonferroni 48 để so
tab["p_bonf48<0.05"] = (tab.p_boot * 48).clip(upper=1) < 0.05
print(f"q_BH<0,05: {int(tab['q_BH<0.05'].sum())}/48 | CI95 chưa hiệu chỉnh loại 0: {int(tab['CI95_loai_0 (chưa hiệu chỉnh)'].sum())}/48 | p_boot<0,05: {int(tab['p_boot<0.05'].sum())}/48 | Bonferroni-48: {int(tab['p_bonf48<0.05'].sum())}/48")
print("p_boot nhỏ nhất có thể với B=4000:", 2 / 4001, "| số hệ số chạm sàn:", int((tab.p_boot <= 2 / 4001 + 1e-12).sum()))
print("lệch giữa 2 tiêu chí (q<0,05 nhưng CI95 chứa 0, hoặc ngược lại):\n", tab[tab["q_BH<0.05"] != tab["CI95_loai_0 (chưa hiệu chỉnh)"]][["City", "var", "rho", "lo", "hi", "p_boot", "p_fdr"]].round(4).to_string())

# ---------- V18b: xếp hạng lại trong mỗi lần bootstrap (chính xác) so với xấp xỉ hạng cố định
def boot_corr_rerank(x, y, blocks, B=1000, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float); ub, inv = np.unique(np.asarray(blocks), return_inverse=True); nb = len(ub)
    members = [np.flatnonzero(inv == k) for k in range(nb)]; rng = np.random.default_rng(seed); r = np.empty(B)
    for i in range(B):
        ix = np.concatenate([members[k] for k in rng.integers(0, nb, nb)]); r[i] = stats.spearmanr(x[ix], y[ix])[0]
    r = r[np.isfinite(r)]; lo, hi = np.percentile(r, [2.5, 97.5]); p = 2 * min((np.sum(r <= 0) + 1) / (len(r) + 1), (np.sum(r >= 0) + 1) / (len(r) + 1))
    return lo, hi, min(1.0, p)
ex = []
for c, v in zip(tab.City, tab["var"]):
    g = a[a.City == c]; ex.append(boot_corr_rerank(g.AQI_a, g[v + "_a"], C.block_id(g)))
tab["rerank_lo"], tab["rerank_hi"], tab["rerank_p"] = zip(*ex); tab["rerank_q_BH"] = C.bh_adjust(tab.rerank_p.to_numpy())
tab["rerank_CI95_loai_0"] = (tab.rerank_lo > 0) | (tab.rerank_hi < 0)
print(f"xếp hạng lại (B=1000): q_BH<0,05: {int((tab.rerank_q_BH < 0.05).sum())}/48; CI95 loại 0: {int(tab.rerank_CI95_loai_0.sum())}/48; lệch biên CI tối đa so với xấp xỉ: {max((tab.lo - tab.rerank_lo).abs().max(), (tab.hi - tab.rerank_hi).abs().max()):.3f}; "
      f"số hệ số đổi kết luận q<0,05: {int(((tab.rerank_q_BH < 0.05) != tab['q_BH<0.05']).sum())}")

# ---------- V18c: độ nhạy — khối 7/14/28, anomaly tuần, bỏ COVID
def table_variant(dd, base="month", days=14):
    aa = C.add_anomalies(dd, ["AQI"] + WX, base=base).assign(blk=lambda z: C.block_id(z, days=days)); rows = []
    for c in [c for c in C.CITIES if c in aa.City.unique()]:
        g = aa[aa.City == c]
        for v in WX: rows.append({"City": c, "var": v, **C.boot_corr(g.AQI_a, g[v + "_a"], g.blk), "n": len(g)})
    t = pd.DataFrame(rows); t["q"] = C.bh_adjust(t.p_boot.to_numpy()); return t.set_index(["City", "var"])
VAR = {"gốc: tháng, khối 14": table_variant(d), "khối 7 ngày": table_variant(d, days=7), "khối 28 ngày": table_variant(d, days=28), "anomaly theo tuần": table_variant(d, base="week"),
       "trước 01/03/2020": table_variant(d[d.Date < "2020-03-01"]), "trước 25/03/2020": table_variant(d[d.Date < "2020-03-25"])}
sv = []
for nm, t in VAR.items():
    b = VAR["gốc: tháng, khối 14"]
    sv.append({"bien_the": nm, "q<0.05": int((t.q < 0.05).sum()), "CI95_loai_0": int(((t.lo > 0) | (t.hi < 0)).sum()), "doi_dau_so_voi_goc": int((np.sign(t.rho) != np.sign(b.rho)).sum()),
               "mat_y_nghia (gốc q<0.05 → q≥0.05)": int(((b.q < 0.05) & (t.q >= 0.05)).sum()), "them_y_nghia": int(((b.q >= 0.05) & (t.q < 0.05)).sum()), "max|Δrho|": float((t.rho - b.rho).abs().max()),
               "do_am_am_ca_8_TP": bool((t.xs("humidity_mean", level="var").rho < 0).all()), "do_am_q<0.05_so_TP": int((t.xs("humidity_mean", level="var").q < 0.05).sum()),
               "Delhi_temp": round(t.loc[("Delhi", "temp_mean"), "rho"], 3), "Delhi_pressure": round(t.loc[("Delhi", "pressure_mean"), "rho"], 3), "Delhi_blh": f"{t.loc[('Delhi', 'blh_mean'), 'rho']:.2f} [{t.loc[('Delhi', 'blh_mean'), 'lo']:.2f}; {t.loc[('Delhi', 'blh_mean'), 'hi']:.2f}]",
               "cac_o_doi_ket_luan": "; ".join(f"{c}/{v}" for (c, v) in t.index[(b.q < 0.05) != (t.q < 0.05)])})
    for k in ("rho", "lo", "hi", "p_boot", "q"): tab[f"{nm}|{k}"] = [t.loc[(c, v), k] for c, v in zip(tab.City, tab["var"])]
sv = pd.DataFrame(sv); save(tab.round(5), "V18_corr_48_coefficients.csv", index=False); save(sv, "V18_corr_sensitivity_summary.csv", index=False)
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 120); print(sv.T.to_string())
print(tab.pivot(index="City", columns="var", values="rho")[WX].loc[C.CITIES].round(2).to_string()); print(tab.pivot(index="City", columns="var", values="q_BH<0.05")[WX].loc[C.CITIES].to_string())
# suy luận gộp: trung vị rho của 5 TP, bootstrap khối LỊCH CHUNG giữa các TP (giữ phụ thuộc cùng ngày)
aa = a.copy(); aa["cb"] = (aa.Date - START).dt.days // 14; nb = int(aa.cb.max()) + 1; rng = np.random.default_rng(0); B = 1000; idx = rng.integers(0, nb, (B, nb)); cnt = np.zeros((B, nb)); np.add.at(cnt, (np.arange(B)[:, None], idx), 1)
pool = []
for v in WX:
    R = []
    for c in core:
        g = aa[aa.City == c]; rx, ry = stats.rankdata(g.AQI_a), stats.rankdata(g[v + "_a"]); S = np.zeros((nb, 6)); np.add.at(S, g.cb.to_numpy(), np.column_stack([np.ones(len(g)), rx, ry, rx * rx, ry * ry, rx * ry]))
        n, sx, sy, sxx, syy, sxy = (cnt @ S).T; R.append((n * sxy - sx * sy) / np.sqrt((n * sxx - sx ** 2) * (n * syy - sy ** 2)))
    med = np.median(np.array(R), axis=0); base_med = np.median([tab[(tab.City == c) & (tab["var"] == v)].rho.iloc[0] for c in core])
    pool.append({"var": v, "trung_vi_rho_5_TP": base_med, "CI95_lo (khối lịch chung 14 ngày)": np.percentile(med, 2.5), "CI95_hi": np.percentile(med, 97.5), "so_TP_cung_dau": int(sum(np.sign(tab[(tab.City == c) & (tab["var"] == v)].rho.iloc[0]) == np.sign(base_med) for c in core))})
pool = pd.DataFrame(pool); save(pool.round(4), "V18_corr_pooled_median_common_blocks.csv", index=False); print(pool.round(3).to_string())

# ---------- V19: 15 phép so sánh
HYP = ["H1", "H2", "H3"]
def groups_for(x):
    x = x.copy(); x["wind_t"] = C.tertile_in_strata(x, "wind_speed_mean"); x["blh_t"] = C.tertile_in_strata(x, "blh_mean")
    return {"H1": (x[x.wind_t == "thấp"], x[x.wind_t == "cao"]), "H2": (x[x.blh_t == "thấp"], x[x.blh_t == "cao"]), "H3": (x[~x.rain_day], x[x.rain_day])}
def concl(lo, hi): return "ủng hộ" if lo > 0 else "ngược chiều dự đoán" if hi < 0 else "chưa đủ bằng chứng"
def ci(boot, m): al = 0.05 / m; return np.percentile(boot, [100 * al / 2, 100 * (1 - al / 2)])
rows = []
for c in core:
    for days in (14, 7, 28):
        x = a[a.City == c].copy(); x["blk"] = C.block_id(x, days=days); G = groups_for(x)
        for h in HYP:
            g1, g2 = G[h]; x1, b1, x2, b2 = g1.AQI_a.to_numpy(), g1.blk.to_numpy(), g2.AQI_a.to_numpy(), g2.blk.to_numpy()
            seeds = range(10) if days == 14 else [0]
            for s in seeds:
                bt = C.boot_median_diff(x1, b1, x2, b2, B=2000, seed=s); u, p = stats.mannwhitneyu(x1, x2, alternative="two-sided")
                r = {"City": c, "H": h, "khoi_ngay": days, "seed": s, "n_batloi": len(x1), "n_thuanloi": len(x2), "so_khoi": len(np.unique(np.concatenate([b1, b2]))), "hieu_ung": np.median(x1) - np.median(x2), "p_MW": p, "B_hop_le": len(bt)}
                for m, nm in ((15, "family15 (99,67%)"), (3, "family3/TP (98,33%)"), (1, "không hiệu chỉnh (95%)")):
                    lo, hi = ci(bt, m); r[f"lo|{nm}"], r[f"hi|{nm}"], r[f"KL|{nm}"] = lo, hi, concl(lo, hi)
                r["p_boot_2_phia"] = min(1.0, 2 * min((np.sum(bt <= 0) + 1) / (len(bt) + 1), (np.sum(bt >= 0) + 1) / (len(bt) + 1)))
                rows.append(r)
T = pd.DataFrame(rows); save(T.round(4), "V19_hypothesis_tests_all_runs.csv", index=False)
t0 = T[(T.khoi_ngay == 14) & (T.seed == 0)].copy(); t0["q_BH_15 (từ p_boot)"] = C.bh_adjust(t0.p_boot_2_phia.to_numpy()); t0["p_holm_15"] = np.nan
o = np.argsort(t0.p_boot_2_phia.to_numpy()); ph = np.maximum.accumulate((15 - np.arange(15)) * t0.p_boot_2_phia.to_numpy()[o]).clip(max=1); t0.iloc[o, t0.columns.get_loc("p_holm_15")] = ph
exp = {("Delhi", "H1"): (30.0, 9.6, 50.2), ("Jaipur", "H3"): (17.2, 7.0, 30.0), ("Amritsar", "H3"): (16.0, 3.5, 27.8), ("Jaipur", "H2"): (-25.0, -41.3, -11.0)}
t0["tac_gia (hiệu ứng, CI 99,67%)"] = [str(exp.get((c, h), "")) for c, h in zip(t0.City, t0.H)]
sd = T[T.khoi_ngay == 14].groupby(["City", "H"])
t0["seed 0–9: KL family15"] = [dict(sd.get_group((c, h))["KL|family15 (99,67%)"].value_counts()) for c, h in zip(t0.City, t0.H)]
t0["seed 0–9: biên lo family15 min..max"] = [f"{sd.get_group((c, h))['lo|family15 (99,67%)'].min():.1f}..{sd.get_group((c, h))['lo|family15 (99,67%)'].max():.1f}" for c, h in zip(t0.City, t0.H)]
t0["seed 0–9: biên hi family15 min..max"] = [f"{sd.get_group((c, h))['hi|family15 (99,67%)'].min():.1f}..{sd.get_group((c, h))['hi|family15 (99,67%)'].max():.1f}" for c, h in zip(t0.City, t0.H)]
for days in (7, 28):
    tt = T[T.khoi_ngay == days].set_index(["City", "H"]); t0[f"khối {days}: KL family15"] = [tt.loc[(c, h), "KL|family15 (99,67%)"] for c, h in zip(t0.City, t0.H)]
    t0[f"khối {days}: CI family15"] = [f"[{tt.loc[(c, h), 'lo|family15 (99,67%)']:.1f}; {tt.loc[(c, h), 'hi|family15 (99,67%)']:.1f}]" for c, h in zip(t0.City, t0.H)]
save(t0.round(4), "V19_hypothesis_tests_summary.csv", index=False)
show = t0[["City", "H", "n_batloi", "n_thuanloi", "so_khoi", "hieu_ung", "lo|family15 (99,67%)", "hi|family15 (99,67%)", "KL|family15 (99,67%)", "KL|family3/TP (98,33%)", "KL|không hiệu chỉnh (95%)", "p_boot_2_phia", "q_BH_15 (từ p_boot)", "p_MW", "seed 0–9: KL family15", "khối 7: KL family15", "khối 28: KL family15"]]
print(show.round(3).to_string())
for nm in ("family15 (99,67%)", "family3/TP (98,33%)", "không hiệu chỉnh (95%)"): print(nm, t0[f"KL|{nm}"].value_counts().to_dict())
print("mỗi đuôi CI 99,67% với B=2000 dựa trên", 2000 * 0.05 / 15 / 2, "mẫu bootstrap")
# bỏ COVID
rows = []
for nm, dd in (("trước 01/03/2020", d[d.Date < "2020-03-01"]), ("trước 25/03/2020", d[d.Date < "2020-03-25"])):
    ax = C.add_anomalies(dd, ["AQI"] + WX)
    for c in core:
        x = ax[ax.City == c].copy(); x["blk"] = C.block_id(x); G = groups_for(x)
        for h in HYP:
            g1, g2 = G[h]; r = C.compare_groups(g1.AQI_a.to_numpy(), g1.blk.to_numpy(), g2.AQI_a.to_numpy(), g2.blk.to_numpy(), m_tests=15); rows.append({"bien_the": nm, "City": c, "H": h, **r, "KL": concl(r["ci_lo"], r["ci_hi"])})
cv = pd.DataFrame(rows); save(cv.round(4), "V19_hypothesis_tests_drop_covid.csv", index=False)
print(cv.pivot(index=["City", "H"], columns="bien_the", values="KL").assign(goc=t0.set_index(["City", "H"])["KL|family15 (99,67%)"]).to_string())
