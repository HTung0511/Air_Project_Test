"""DA vòng 2 — DA-05: trích bảng V16 / V18 / V19 cho BA từ bằng chứng v1.1 (vòng 1), kèm tính lại các con số dẫn xuất.

Đây là TRÍCH XUẤT số vòng 1 trên dữ liệu baseline, không phải kết quả kiểm bản sửa vòng 2.
Dùng: python r2_ba_extract.py <thư mục evidence v1.1> <thư mục out>
Ghi 3 CSV gọn (R2_BA01…03) và in các đoạn bảng markdown để dán vào ba_evidence_extract.md.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
vn = lambda x, nd=2: f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")
VAR = {"temp_mean": "nhiệt độ", "humidity_mean": "độ ẩm", "wind_speed_mean": "tốc độ gió", "blh_mean": "lớp biên", "precip_sum": "mưa", "pressure_mean": "áp suất"}
HN = {"H1": "H1 gió yếu", "H2": "H2 lớp biên thấp", "H3": "H3 không mưa"}
md = []

# ------------------------------------------------------------------ BA01: tỉ số PM2.5 (V16)
c = pd.read_csv(src / "V16_eda_pollutant_by_city.csv"); s = pd.read_csv(src / "V16_eda_pollutant_summary.csv", index_col=0)
ci_col = [k for k in c.columns if k.startswith("Unnamed") or "CI95" in k][-1]
t = c[["City", "n_ngay_AQI", "n_nang", "du_100_ngay_nang", "PM2.5_n_nang/n_conlai", "PM2.5_median_nang", "PM2.5_median_conlai", "PM2.5_ratio"]].copy()
t["CI95_ratio (khối 14 ngày)"] = c[ci_col]
assert np.allclose(t["PM2.5_median_nang"] / t["PM2.5_median_conlai"], t["PM2.5_ratio"], atol=5e-4), "ratio từng TP không bằng median nặng / median còn lại"
five = t[t.du_100_ngay_nang]
med5 = float(five["PM2.5_ratio"].median()); pooled = float(s.loc["PM2.5", "median_gop_nang"] / s.loc["PM2.5", "median_gop_conlai"])
assert len(five) == 5 and abs(med5 - s.loc["PM2.5", "trung_vi_cua_ratio_cac_TP_du_ngay_nang"]) < 5e-4 and abs(pooled - s.loc["PM2.5", "ratio_cua_2_median_gop"]) < 5e-4
t.to_csv(out / "R2_BA01_pm25_ratio_by_city.csv", index=False)
md.append("### BA01\n\n| Thành phố | Ngày có AQI | Ngày nặng | PM2.5: n nặng / n còn lại | Trung vị ngày nặng (µg/m³) | Trung vị ngày còn lại (µg/m³) | Tỉ số | CI 95% của tỉ số | Có trong \"5 thành phố\" |\n|---|---|---|---|---|---|---|---|---|")
for _, r in t.iterrows():
    ci = r["CI95_ratio (khối 14 ngày)"]
    ci = "—" if pd.isna(ci) else ci.replace(".", ",")
    md.append(f"| {r.City} | {vn(r.n_ngay_AQI, 0)} | {vn(r.n_nang, 0)} | {r['PM2.5_n_nang/n_conlai']} | {vn(r['PM2.5_median_nang'])} | {vn(r['PM2.5_median_conlai'])} | {vn(r['PM2.5_ratio'])} | {ci} | {'có' if r.du_100_ngay_nang else 'không (dưới 100 ngày nặng)'} |")
md.append(f"\nmed5 = {vn(med5)} ; CI = {s.loc['PM2.5'].iloc[-1]} ; 5 TP = {', '.join(five.City)} ; min–max 5 TP = {vn(five['PM2.5_ratio'].min())}–{vn(five['PM2.5_ratio'].max())}")
md.append(f"gộp: {vn(s.loc['PM2.5', 'median_gop_nang'], 3)} / {vn(s.loc['PM2.5', 'median_gop_conlai'], 3)} = {vn(pooled)} ; n cặp gộp = {int(s.loc['PM2.5', 'n_cap_gop'])}")
md.append("các chất khác (trung vị 5 tỉ số | tỉ số gộp): " + "; ".join(f"{k} {vn(s.loc[k].iloc[0])} | {vn(s.loc[k, 'ratio_cua_2_median_gop'])}" for k in s.index))

# ------------------------------------------------------------------ BA02: 48 hệ số (V18)
d = pd.read_csv(src / "V18_corr_48_coefficients.csv")
k = d[["City", "var", "n", "so_khoi_14_ngay", "rho_tho", "rho", "lo", "hi", "p_boot", "p_fdr", "q_BH<0.05", "CI95_loai_0 (chưa hiệu chỉnh)", "p_bonf48<0.05", "doi_dau_tho→bo_mua"]].copy()
k.columns = ["City", "bien", "n", "so_khoi_14_ngay", "rho_tho", "rho_bo_mua", "CI95_lo (chưa hiệu chỉnh)", "CI95_hi (chưa hiệu chỉnh)", "p_bootstrap", "q_BH", "q_BH<0.05", "CI95_loai_0",
             "p_Bonferroni48<0.05", "doi_dau_khi_bo_mua"]
assert bool((k["q_BH<0.05"] == (k.q_BH < 0.05)).all()) and bool((k.CI95_loai_0 == ((k.iloc[:, 6] > 0) | (k.iloc[:, 7] < 0))).all())
nq, nci, nbonf, nsign = int(k["q_BH<0.05"].sum()), int(k.CI95_loai_0.sum()), int(k["p_Bonferroni48<0.05"].sum()), int(k.doi_dau_khi_bo_mua.sum())
k.to_csv(out / "R2_BA02_corr_48_q_ci.csv", index=False)
md.append(f"\n### BA02\n\nq<0,05: {nq}/48 ; CI95 loại 0: {nci}/48 ; Bonferroni48: {nbonf}/48 ; đổi dấu: {nsign}/48 ; p sàn 0,0005: {int((k.p_bootstrap <= 0.0005).sum())}/48")
x = pd.crosstab(k["q_BH<0.05"], k.CI95_loai_0)
md.append(f"chéo: q<0,05 & CI loại 0 = {x.loc[True, True]}; q<0,05 & CI chứa 0 = {x.loc[True, False]}; q≥0,05 & CI loại 0 = {x.loc[False, True]}; q≥0,05 & CI chứa 0 = {x.loc[False, False]}")
for _, r in k[k["q_BH<0.05"] != k.CI95_loai_0].iterrows():
    md.append(f"ô lệch: {r.City} – {VAR[r.bien]}: rho {vn(r.rho_bo_mua, 3)} [{vn(r.iloc[6], 3)}; {vn(r.iloc[7], 3)}], p {vn(r.p_bootstrap, 3)}, q {vn(r.q_BH, 3)}")
md.append("\n| Thành phố | " + " | ".join(VAR.values()) + " |\n|---|" + "---|" * len(VAR))
for city, g in k.groupby("City", sort=False):
    g = g.set_index("bien")
    v2 = lambda x: vn(x, 3) if abs(x) < 0.005 else vn(x)                 # tránh in "−0,00" cho biên CI sát 0
    cell = lambda v: f"{v2(g.loc[v, 'rho_bo_mua'])} [{v2(g.loc[v].iloc[5])}; {v2(g.loc[v].iloc[6])}]; q {('< 0,001' if g.loc[v, 'q_BH'] < 0.001 else vn(g.loc[v, 'q_BH'], 3))}" + ("" if g.loc[v, "q_BH<0.05"] else " ✗")
    md.append(f"| {city} | " + " | ".join(cell(v) for v in VAR) + " |")
bycity = k.groupby("City", sort=False).agg(q=("q_BH<0.05", "sum"), ci=("CI95_loai_0", "sum")); byvar = k.groupby("bien", sort=False).agg(q=("q_BH<0.05", "sum"), ci=("CI95_loai_0", "sum"))
md.append("theo TP (q<0,05 / CI loại 0, trên 6): " + "; ".join(f"{i} {r.q}/{r.ci}" for i, r in bycity.iterrows()))
md.append("theo biến (q<0,05 / CI loại 0, trên 8): " + "; ".join(f"{VAR[i]} {r.q}/{r.ci}" for i, r in byvar.iterrows()))

# ------------------------------------------------------------------ BA03: 15 phép so sánh (V19)
h = pd.read_csv(src / "V19_hypothesis_tests_summary.csv")
g = pd.DataFrame({"City": h.City, "H": h.H, "n_bat_loi": h.n_batloi, "n_thuan_loi": h.n_thuanloi, "so_khoi_14_ngay": h.so_khoi, "hieu_ung_diem_AQI": h.hieu_ung,
                  "CI_family15_lo (99,67%)": h["lo|family15 (99,67%)"], "CI_family15_hi (99,67%)": h["hi|family15 (99,67%)"], "KL_family15": h["KL|family15 (99,67%)"],
                  "CI_family3_lo (98,33%)": h["lo|family3/TP (98,33%)"], "CI_family3_hi (98,33%)": h["hi|family3/TP (98,33%)"], "KL_family3": h["KL|family3/TP (98,33%)"],
                  "CI95_lo (không hiệu chỉnh)": h["lo|không hiệu chỉnh (95%)"], "CI95_hi (không hiệu chỉnh)": h["hi|không hiệu chỉnh (95%)"], "KL_khong_hieu_chinh": h["KL|không hiệu chỉnh (95%)"],
                  "p_MannWhitney": h.p_MW})
assert len(g) == 15
g.to_csv(out / "R2_BA03_hypothesis_family15.csv", index=False)
tally = lambda col: " / ".join(str(int((g[col] == v).sum())) for v in ("ủng hộ", "ngược chiều dự đoán", "chưa đủ bằng chứng"))
md.append(f"\n### BA03\n\nủng hộ / ngược chiều / chưa đủ: family15 = {tally('KL_family15')} ; family3 = {tally('KL_family3')} ; không hiệu chỉnh = {tally('KL_khong_hieu_chinh')}")
md.append(f"số phép có kết luận khác nhau giữa family15 và family3: {int((g.KL_family15 != g.KL_family3).sum())} ; p_MW<0,05: {int((g.p_MannWhitney < 0.05).sum())}/15 ; alpha mỗi phép: 0,05/15 = {0.05/15:.5f} -> CI {100*(1-0.05/15):.2f}%; 0,05/3 -> CI {100*(1-0.05/3):.2f}%")
md.append("\n| Thành phố | Giả thuyết | n bất lợi / thuận lợi | Hiệu ứng (điểm AQI) | CI 99,67% (họ 15) | Kết luận (họ 15) | CI 98,33% (họ 3) | Kết luận (họ 3) | CI 95% không hiệu chỉnh | Kết luận nếu không hiệu chỉnh |\n|---|---|---|---|---|---|---|---|---|---|")
for _, r in g.iterrows():
    md.append(f"| {r.City} | {HN[r.H]} | {r.n_bat_loi} / {r.n_thuan_loi} | {vn(r.hieu_ung_diem_AQI, 1)} | [{vn(r.iloc[6], 1)}; {vn(r.iloc[7], 1)}] | {r.KL_family15} | [{vn(r.iloc[9], 1)}; {vn(r.iloc[10], 1)}] | {r.KL_family3} | [{vn(r.iloc[12], 1)}; {vn(r.iloc[13], 1)}] | {r.KL_khong_hieu_chinh} |")
(out / "ba_tables.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))
