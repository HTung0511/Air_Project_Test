"""S05 [Q03] Giả lập che khối: lấy các đoạn có GIÁ TRỊ THẬT liên tục (không phải ô nội suy, không flatline), che L ngày liên tiếp,
nội suy tuyến tính theo thời gian giữa hai đầu mút thật (đúng cách utils.impute_time_series làm với khoảng ≤ max_gap), so với giá trị thật.
Giao thức định trước: L ∈ {1,3,7,14,30,60}; mỗi (TP, chất, L) lấy ngẫu nhiên tối đa 300 vị trí bắt đầu (seed 0); chỉ số: MAE, sai số tương đối
= MAE / trung vị của chất tại TP, bias; so với 2 cách thay thế đơn giản (giữ giá trị cuối; trung vị cùng TP-tháng) để có mốc.
Hạn chế của giả lập: khoảng thiếu thật không ngẫu nhiên (trạm hỏng có thể trùng sự kiện), và chỉ che ở nơi chuỗi đang đầy đủ.
"""
from da_common import *
base = pd.read_csv(CLEAN, parse_dates=["Date"]); COLS = ["PM2.5", "NO2", "CO", "SO2", "O3", "PM10", "NO"]; LS = [1, 3, 7, 14, 30, 60]
season = lambda m: np.select([np.isin(m, [12, 1, 2]), np.isin(m, [3, 4, 5]), np.isin(m, [6, 7, 8, 9])], ["Đông (12–2)", "Hè (3–5)", "Mưa (6–9)"], "Sau mưa (10–11)")
rng = np.random.default_rng(0); rows = []
for c in CITIES:
    g = base[base.City == c].sort_values("Date").reset_index(drop=True); mon = g.Date.dt.month.to_numpy()
    for col in COLS:
        v = g[col].where(~g[f"{col}_was_missing"]).to_numpy(float); ok = ~np.isnan(v)
        if ok.sum() < 200: continue
        med = np.nanmedian(v); clim = pd.Series(v).groupby(mon).transform("median").to_numpy()
        cs = np.concatenate([[0], np.cumsum(ok)])
        for L in LS:
            n = len(v) - L - 1
            if n <= 0: continue
            starts = np.arange(1, n + 1); full = (cs[starts + L + 1] - cs[starts - 1]) == L + 2          # v[i-1 .. i+L] đều thật
            cand = starts[full]
            if len(cand) == 0: continue
            pick = rng.choice(cand, size=min(300, len(cand)), replace=False)
            for i in pick:
                a, b = v[i - 1], v[i + L]; truth = v[i:i + L]; w = np.arange(1, L + 1) / (L + 1); interp = a + (b - a) * w
                rows.append({"City": c, "cot": col, "L": L, "mua": str(season(mon[i + L // 2])), "median_cot": med, "mae_noi_suy": np.abs(interp - truth).mean(), "bias_noi_suy": (interp - truth).mean(),
                             "mae_giu_gia_tri_cuoi": np.abs(a - truth).mean(), "mae_trung_vi_thang": np.abs(clim[i:i + L] - truth).mean(), "mae_o_giua_khoi": abs(interp[L // 2] - truth[L // 2]), "truth_mean": truth.mean()})
S = pd.DataFrame(rows); S["rel"] = S.mae_noi_suy / S.median_cot * 100
def agg(keys):
    g = S.groupby(keys); return pd.DataFrame({"so_khoi_gia_lap": g.size(), "MAE_noi_suy": g.mae_noi_suy.mean(), "MAE/trung_vi_%": g.rel.mean(), "bias": g.bias_noi_suy.mean(), "MAE_giu_gia_tri_cuoi": g.mae_giu_gia_tri_cuoi.mean(),
                                      "MAE_trung_vi_thang": g.mae_trung_vi_thang.mean(), "MAE_o_giua_khoi": g.mae_o_giua_khoi.mean(), "noi_suy_tot_hon_trung_vi_thang": g.mae_noi_suy.mean() < g.mae_trung_vi_thang.mean()})
byL = agg(["cot", "L"]); byC = agg(["cot", "City", "L"]); byS = agg(["cot", "mua", "L"])
save(byL.round(3), "S05_interp_sim_by_length.csv"); save(byC.round(3), "S05_interp_sim_by_city.csv"); save(byS.round(3), "S05_interp_sim_by_season.csv")
pd.set_option("display.width", 250)
print(byL["MAE/trung_vi_%"].unstack("L").round(1).to_string()); print("PM2.5 (µg/m³):\n", byL.loc["PM2.5"].round(2).to_string())
print("PM2.5 theo TP, MAE/trung vị %:\n", byC.loc["PM2.5"]["MAE/trung_vi_%"].unstack("L").reindex(CITIES).round(1).to_string()); print("PM2.5 theo mùa, MAE (µg/m³):\n", byS.loc["PM2.5"]["MAE_noi_suy"].unstack("L").round(1).to_string())
print("nội suy tốt hơn trung vị tháng? (theo chất × L):\n", byL["noi_suy_tot_hon_trung_vi_thang"].unstack("L").to_string())
# phân bố độ dài khoảng thực sự được nội suy trong bảng sạch
rows = []
for c in CITIES:
    g = base[base.City == c].sort_values("Date")
    for col in COLS + ["NOx", "NH3", "Benzene", "Toluene"]:
        f = (g[f"{col}_was_missing"] & g[col].notna()).to_numpy(); dd = np.diff(np.concatenate([[0], f.astype(int), [0]])); ln = np.flatnonzero(dd == -1) - np.flatnonzero(dd == 1)
        for x in ln: rows.append({"City": c, "cot": col, "do_dai": int(x)})
G = pd.DataFrame(rows); G["nhom"] = pd.cut(G.do_dai, [0, 1, 3, 7, 14, 1000], labels=["1", "2–3", "4–7", "8–14", ">14"])
t = G.groupby("nhom", observed=False).agg(so_khoang=("do_dai", "size"), so_o=("do_dai", "sum")); t["%_o"] = t.so_o / t.so_o.sum() * 100; save(t.round(2), "S05_actual_interpolated_gap_lengths.csv"); print(t.round(1).to_string(), "| tổng ô:", int(t.so_o.sum()), "| dài nhất:", int(G.do_dai.max()))
