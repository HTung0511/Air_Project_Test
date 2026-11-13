# PHẦN III. KẾT QUẢ THỰC HIỆN — BẢNG NGUỒN VÀ BẢN THẢO 3.1–3.2

> **Hướng dùng:** Bảng nguồn (§A) là bản đồ trước khi viết đoạn. Mọi số trong §B (3.1–3.2) đều có trỏ về bảng nguồn; số thuộc 3.3–3.4 (mô hình, HTML) **chưa trích làm bằng chứng** ở đây khi chưa đối chiếu `notebooks/06_predict_aqi.ipynb` và `model_*.png` của nhóm nộp. HTML chỉ là lớp trình bày, không thay bảng tính toán.

---

## A. Bảng nguồn kết quả ngắn (3.1–3.4)

| Mục báo cáo | Bảng/hình nguồn (đường dẫn cụ thể) | Phiên bản / Notebook & dữ liệu tương ứng | Số liệu định dùng (chỉ số chính) | Điểm cần đối chiếu trước khi chốt số |
|---|---|---|---|---|
| **3.1 Thu thập & tiền xử lý — tổng quan** | `reports/cleaning_log_8cities.md` §1 *Tổng quan kết quả* (bảng 3 dòng); `Data_dictionary.md` §1–2; `Metadata.json` *missing_pct_by_column*; `data/raw/city_day.csv` (29.531 dòng, 26 TP) → `data/processed/air_quality_8cities.csv` (14.056 dòng) | `notebooks/01_cleaning.ipynb` + `src/pipeline.py`/`src/utils.py`/`src/gap_utils.py` — commit nhóm nộp [Cần đối chiếu: `c4c75f6` hiện tại có phải bản nộp chính thức?] | 29.531 dòng gốc → **14.056 dòng** cho 8 TP, **0** dòng trùng (City,Date), **0** đứt ngày, **0** giá trị âm. 16 cột → **40 cột** (11 chất + AQI + AQI_Bucket + 12 cờ `_was_missing` + 11 cờ `_is_outlier` + 2 cờ khác + khóa). Ô thiếu (11 chất + AQI): **16.953 (10,05%) → 15.832 (9,39%)**. Công thức đối chiếu: 16.953 + 2.169 (flatline→NaN) − 3.329 (nội suy) + 39 (nghi lỗi→NaN) = 15.832 | Đối chiếu số dòng khớp `city_day.csv` và `cleaning_summary_8cities.csv` (105 dòng = 8 TP ×13 cột); xác nhận 14.056 không đổi sau các bước |
| **3.1 Tiền xử lý — chi tiết từng quy tắc** | `reports/cleaning_log_8cities.md` §2 *Nhật ký xử lý* Bước 1–11; `reports/cleaning_summary_8cities.csv` (105 dòng, cột `pct_missing_before/after`, `n_flatline_to_nan`, `n_imputed`, `n_outlier_flagged`, `dung_lam_bien_mo_hinh`); `reports/suspect_points_8cities.csv` (94 dòng) | `notebooks/02_cleaning_evidence.ipynb` (bằng chứng Lucknow/Jaipur mở rộng ra 8 TP) + `src/utils.py:flag_flatline_zeros`, `_interpolate_short_gaps` | **Bước 1** flatline ≥3 ngày: **2.169 ô** (Benzene 646, Toluene 615, CO 540, NOx 368; ví dụ Bengaluru NOx =0 suốt 207 ngày). **Bước 2** bỏ Xylene (4 TP thiếu 100%, Gurugram 93%…) + PM10 Lucknow 100% → 4.234 ô Xylene + 2.009 ô PM10 rỗng. **Bước 3** nội suy ≤14 ngày: **3.329 ô**, trong đó **1.316 ô** là sửa lỗi `limit=14` cũ (6 TP bị, Lucknow/Jaipur không). **Bước 4** giữ NaN khối dài: **9 cặp** thiếu ≥20% (Gurugram NH3 92,9%, Chennai PM10 84,5%, Gurugram PM10 52,4%…), **7.733 ô** giữ NaN; ≥60% không dùng làm biến (Gurugram NH3, Chennai PM10). **Bước 5** AQI: 0,5% Delhi →13,6% Gurugram thiếu, **836 dòng** giữ NaN, không nội suy. **Bước 6** outlier IQR×1,5 theo tháng: **6.656 ô** (PM2.5 531 ngày), chỉ gắn cờ. **Bước 7–8** nghi lỗi: **93 điểm** xét → **41 ô** (22 PM2.5+19 AQI) trong **24 ngày** ở 7/8 TP đặt NaN; 52 đỉnh giữ lại + 87 ngày AQI>500 (68 ngày tháng 10–2). **Bước 9–10** chưa quyết: 305 ô +139 ngày PM2.5>1,2×PM10 | Kiểm ngưỡng flatline 3 ngày, `k=1,5`, top 5 PM2.5/AQI mỗi TP có phải quy ước nhóm nộp? Đối chiếu `suspect_points_8cities.csv` với notebook 02; xác nhận `pm25_gt_pm10_flag` 139 dòng |
| **3.1 Thời tiết (nguồn thứ hai)** | `reports/cleaning_log_8cities.md` Bước 12–17; `Data_dictionary.md` §3; `Metadata.json` §weather_source; `data/raw/weather/openmeteo_*_hourly.csv.gz` (48.384 dòng giờ/TP); `data/processed/weather_daily_8cities.csv` (16.128 dòng); `data/processed/air_quality_8cities_weather.csv` (14.056×54) | `notebooks/04_weather_merge.ipynb` + `src/weather_utils.py` — Open-Meteo ERA5, múi `Asia/Kolkata`, CC BY 4.0 | **387.072 dòng giờ** (8×48.384) → **16.128 ngày-thành phố** → ghép trái giữ nguyên 14.056 dòng, **0 dòng thiếu thời tiết**, `assert_frame_equal` với bảng cũ. Tọa độ lưới lệch ≤0,12°; Delhi (28,50°N 77,25°E) và Gurugram (28,50°N 77,00°E) **r≈0,95 (mưa) –0,999 (nhiệt độ)** | Đối chiếu 8 tọa độ yêu cầu vs. ô lưới ERA5 thực dùng, độ cao ô lưới, giấy phép CC BY 4.0; xác nhận không sửa bản gốc `*.gz` |
| **3.2 EDA — Ở đâu (không gian)** | `reports/figures/eda_00_sample_size.png`; `eda_01_poor_share_city.png`; `eda_05_aqi_distribution.png`; bảng A1 trong `notebooks/03_eda.ipynb` §A1 (khoảng chung) | `notebooks/03_eda.ipynb` Phần A + `src/eda_utils.py` (khoảng chung 14/06/2017–01/07/2020, ngưỡng Poor =201, palette #D55E00) | **n** trên 1.114 ngày chung: Amritsar 1.029 → Lucknow 1.111 (thiếu 7,6% vs ~1%). **Median AQI:** Delhi 205, Lucknow 188, Gurugram 188, Jaipur 122, Amritsar 104, Hyderabad 89, Chennai 87, Bengaluru 81. **% ngày ≥201:** Delhi **51,0%**, Lucknow **46,4%**, Gurugram **46,3%** (≈½ số ngày) gấp **4,1–4,6 lần** Amritsar 11,4% / Jaipur 11,1%; Chennai 3,1%, Bengaluru 0,2%, Hyderabad 0,1% | Đối chiếu định nghĩa Poor ≥201 (CPCB) và khoảng chung; kiểm bảng A1 n vs. % (Amritsar/Gurugram thưa hơn). Nhóm thay vì xếp hạng 1–8 do sensitivity |
| **3.2 EDA — Khi nào (thời gian)** | `reports/figures/eda_02_heatmap_city_month.png`; `eda_03_trend_city_year.png`; `aqi_monthly_lucknow_jaipur.png` / `aqi_season_lucknow_jaipur.png` (tài liệu cũ) | `notebooks/03_eda.ipynb` Phần B (§B1–B3), bảng B0 (tháng 1–6 so năm, kèm n) | **Mùa:** Delhi/Gurugram/Lucknow/Jaipur/Amritsar **đỉnh tháng 11–12, đáy tháng 7–9**; Amritsar: median **T11=209 gấp 3,1 lần T8=66**, **89/117 ngày (76%)** ≥201 rơi T10–12; Bengaluru dao động **63–102 (1,6 lần)**, chỉ **2 ngày** ≥201. **Năm (T1–6):** B3 chẩn đoán 2020 vs 2019 tách 1/1–24/3 và 25/3–30/6 để kiểm lockdown 25/3/2020 — chỉ nêu “có liên quan” | Đối chiếu định nghĩa mùa Đông (12–2)/Hè/Mưa/Sau mưa trong `eda_utils.py`; xác nhận chỉ dùng tháng 1–6 khi so năm và loại 2020 H2; không gọi lockdown là nguyên nhân |
| **3.2 EDA — Chất nào** | `reports/figures/eda_04_pm25_aqi.png`; bảng C0 (Spearman), bảng C1 (tỉ số trung vị) trong `notebooks/03_eda.ipynb` Phần C | `notebooks/03_eda.ipynb` Phần C + `Data_dictionary.md` (đơn vị) | **C0 Spearman (khoảng chung, gộp 8 TP):** PM2.5 **0,91**, NO2 0,52, CO 0,48, SO2 0,38, O3 0,34; giữa các chất 0,17–0,50. **C1 (≥201 vs. ngày thường, 5 TP ≥100 ngày nặng):** PM2.5 **trung vị 2,8 lần** (2,1 Jaipur →3,1 Lucknow; **137,1 vs. 42,0 µg/m³ gộp 8 TP**), NO2 1,7 lần, CO 1,6 lần, SO2/O3 ~1,1 lần; **73,2%** ngày nặng rơi T10–2; **12,2%** (225/1.850) ngày nặng có PM2.5 <91 µg/m³ | **GOI bắt buộc:** phân biệt **trung vị tỷ số 5 TP =2,82 [2,42;3,17]** vs. **tỷ số gộp 8 TP =137,1/42≈3,26** (hai câu hỏi khác nhau, không thay thế). Đối chiếu loại khoảng DA (V16) trước khi gắn nhãn 95% CI; ghi confounder cách tính AQI (max chỉ số con) và mùa |
| **3.2 EDA — Độ nhạy & confounder** | `notebooks/03_eda.ipynb` §*Kiểm tra độ nhạy* (xóa ngẫu nhiên 10% dòng ×200 lần) + bảng Phát hiện A/B/C (cột Confounder/Hạn chế) | `src/eda_utils.py:provenance()` (ghi nguồn + cỡ mẫu ở chân hình) | Kết quả: **Lucknow↔Gurugram, Amritsar↔Jaipur, Bengaluru↔Hyderabad hay đổi chỗ** → báo cáo **chia nhóm** thay vì xếp hạng 1–8. Confounder ghi sẵn: vị trí trạm, quy mô đô thị, địa lý, Diwali/đốt rơm Punjab, cách tính AQI | Đối chiếu phương pháp bootstrap nhạy; xác nhận W7–W8 (tiêu đề kết luận có số, trục từ 0, một màu nhấn, chân hình provenance) |
| **3.3 Tương quan thời tiết (trước khi mô hình)** | `reports/figures/corr_01_raw_vs_adjusted.png` (thô vs. khử mùa); `corr_02_hypothesis_tests.png` (15 so sánh, Bonferroni); `corr_03_humidity_deciles.png` + `corr_04_poor_share_by_humidity.png` | `notebooks/05_weather_correlation.ipynb` + `src/corr_utils.py` (`add_anomalies` median City×Month, `block_id` 14 ngày, `boot_median_diff`, `bh_adjust`) | **D1 thô vs. khử mùa:** Delhi nhiệt độ **−0,52→+0,23**, áp suất **+0,63→−0,16**, BLH **−0,38→+0,08 (KTC chứa 0)**; độ ẩm giữ chiều âm 8/8 TP (−0,14→−0,48). **D2 family 15 (3 GT×5 TP):** **3 ủng hộ** (gió yếu Delhi, không mưa Jaipur/Amritsar), **1 ngược** (BLH thấp đi cùng AQI thấp hơn ở Jaipur), **11 chưa đủ bằng chứng** (KTC chứa 0). **Count tổng:** **32/48 sau BH** vs. **33/48 theo CI danh nghĩa** [V18] — hai family khác mẫu số, **không cộng** | Đối chiếu V16/V18/V19 là family/tiêu chí khác nhau; chỉ nêu count khi có bảng nguồn và mô tả tiêu chí (Bonferroni vs. BH-FDR); nhấn p-value công thức quá lạc quan vs. bootstrap theo khối |
| **3.3 Mô hình & đánh giá (mở rộng)** | `reports/figures/model_01_residual_diagnostics.png` … `model_05_humidity_recheck.png` + `05_weather_correlation` §độ nhạy | `notebooks/06_predict_aqi.ipynb` + `src/model_utils.py` (TRAIN_END 30/06/2019, TEST 01/07/2019–29/02/2020 = *giai đoạn kiểm thử*, LOCKDOWN từ 01/03/2020, Levels L1–L4, Ridge/ HGB, TimeSeriesSplit 4×gap 16, block 14 ngày) — **phiên bản nhóm nộp** | **Bằng chứng DA vòng trước (KHÔNG phải số Dev mới):** test L3 **MAE 19,52 vs. persistence 23,47**; giai đoạn giữ lại cuối L3 **13,78 vs. 14,80 chênh −1,02 [−2,70;0,48] chưa đủ bằng chứng**. Trong notebook 06 hiện tại (nhánh Test): MAE “Ngày mai = hôm nay” **23,5 (R² 0,86) → L3 19,5 (R² 0,91) giảm 16,8% (−3,95 [−5,4;−2,6])**, L1→L2 −2,0, L2→L3 −1,4 [−1,9;−0,9]; cận trên L4 chỉ −0,43 | **GOI:** các số 19,52/23,47 và 13,78/14,80 thuộc **đường trước sửa, KHÔNG phải kết quả Dev mới**; chỉ dùng nếu khớp phiên bản notebook nhóm nộp và công khai hạn chế preprocessing, không gọi là “sạch leakage đã xác nhận”. **Chưa lấy HTML làm chuẩn**; F01 chưa hoàn tất, không tuyên bố loại bỏ hoàn toàn leakage |
| **3.4 Sản phẩm minh họa** | `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` (title, lead, tab 1–4, biểu đồ MAE/Precision/Recall) + `docs/GOI_BO_SUNG_BAO_CAO.md` §2 | Phiên bản HTML v5 hiện tại (bản sao Test) — chưa phải bản nhóm nộp đã nghiệm thu | **Tính năng:** chọn (TP, ngày) xem AQI hôm nay→dự báo mai qua L1→L3; toàn cảnh giai đoạn kiểm thử; kéo ngưỡng cảnh báo (166/160 vs. 201 chuẩn); bảng hệ số Ridge trên log(AQI). **Số trên HTML (MAE 19,52 −16,8% v.v.) là lớp trình bày, trùng đường trước sửa** | **Phải sửa trước khi trích:** đổi mọi “mùa đông (01/07/2019–29/02/2020)” → **“giai đoạn kiểm thử (01/07/2019–29/02/2020)”**; xóa tuyên bố **“chống rò rỉ tuyệt đối”**; ghi rõ là **phát lại trên dữ liệu lịch sử, chưa khẳng định dự báo trực tuyến**; Dev cache/đặc trưng gốc là hướng phát triển chưa tích hợp |

---

## B. Bản thảo 3.1. Kết quả thu thập và tiền xử lý

### Câu hỏi của mục

Thu thập có đủ và đáng tin để so sánh 8 thành phố theo thời gian không, và những quy tắc làm sạch nào đã để lại dấu vết có thể truy vết cho các bước sau?

### Bảng/biểu đồ dẫn chứng

- **Bảng tổng quan §1** trong `cleaning_log_8cities.md` (3 dòng: số dòng, số cột, ô thiếu trước–sau).
- **Bảng nhật ký §2** Bước 1–17 và **§3 Hạn chế** (17 bước + 15 dòng rủi ro).
- **Bảng chi tiết** `cleaning_summary_8cities.csv` (105 dòng = 8 TP ×13 cột hiển thị, đầy đủ là 8×13 với 14 cột thống kê mỗi ô).
- **Bảng truy vết** `suspect_points_8cities.csv` (94 dòng, 93 điểm top-5 + 1 điểm lan).
- **Hình minh họa** `missing_pattern_lucknow_jaipur.png`, `missing_after_cleaning_8cities.png`, `outliers_pm25_lucknow_jaipur.png`, `fill_strategies_lucknow_jaipur.png` [Cần đối chiếu tên file nhóm nộp có khớp `reports/figures/` hiện tại?].
- **Nguồn thời tiết:** `Data_dictionary.md` §3, `Metadata.json` §weather_source, `data/processed/weather_daily_8cities.csv` và `air_quality_8cities_weather.csv`.

### Số liệu chính (phiên bản nhóm nộp, đối chiếu với `cleaning_log_8cities.md` §1–2)

Trên **8 thành phố đã chọn**, tập làm việc giữ nguyên **14.056 dòng** (mỗi dòng một cặp City–Date, không trùng khóa, không đứt ngày) và không có giá trị âm; `AQI_Bucket` khớp thang CPCB. Số cột tăng từ **16 → 40** (11 chất được giữ + AQI + AQI_Bucket + 12 cờ `_was_missing` + 11 cờ `_is_outlier` + `pm25_gt_pm10_flag` + `suspect_sensor_error` + khóa). Theo bảng tổng quan, ô thiếu của 11 chất + AQI giảm nhẹ từ **16.953 (10,05%) → 15.832 (9,39%)** do **thêm 2.169 ô NaN** từ chuỗi 0 treo (Bước 1) được bù một phần bởi **3.329 ô nội suy** (Bước 3) và **39 ô nghi lỗi** (Bước 7) chuyển thành NaN.

Ở cấp quy tắc, nhóm áp dụng **một pipeline thống nhất** cho 8 TP: chuỗi **0 liên tiếp ≥3 ngày** → NaN (**2.169 ô**, ví dụ Bengaluru NOx =0 suốt 207 ngày); **bỏ Xylene toàn bộ** và để **PM10 Lucknow = NaN** (Xylene thiếu 100% ở 4/8 TP, Lucknow PM10 100% thiếu); **chỉ nội suy khoảng thiếu ≤14 ngày** nằm giữa hai giá trị thật (**3.329 ô**) đồng thời **sửa lỗi `interpolate(limit=14)` cũ** vốn điền nhầm **1.316 ô** trong khoảng dài ở 6 TP; **giữ NaN** mọi khoảng dài hơn ở **9 cặp (TP,cột) thiếu ≥20%** (nặng nhất Gurugram NH3 92,9%, Chennai PM10 84,5%, Gurugram PM10 52,4% — tổng **7.733 ô** giữ NaN, trong đó ≥60% không dùng làm biến). AQI thiếu **0,5% (Delhi) →13,6% (Gurugram)**, tổng **836 dòng**, được giữ NaN.

Dấu vết cho EDA/mô hình: **6.656 ô** gắn cờ ngoại lai **IQR×1,5 theo tháng** (PM2.5 531 ngày) chỉ để đánh dấu; **93 điểm** top-5 PM2.5/AQI mỗi TP được điều tra, trong đó **41 ô (22 PM2.5+19 AQI) trên 24 ngày** ở 7/8 TP bị đặt NaN với nhãn *nghi lỗi* (ví dụ Amritsar 08/05/2017 PM2.5 868,7 gấp 7,5 lần PM10); 52 đỉnh và 87 ngày AQI>500 (68 ngày tháng 10–2) được giữ lại như đỉnh mùa cao điểm. Kiểm tra logic bổ sung 139 ngày **PM2.5>1,2×PM10** (Chennai 9,0% số ngày kiểm được, Bengaluru 3,4%) chỉ gắn cờ.

Ở nguồn thứ hai, **387.072 dòng giờ** (8 TP ×48.384) được gộp thành **16.128 ngày-thành phố** với 14 cột thời tiết (ERA5 lưới 0,25°, múi Asia/Kolkata, 25/12/2014–01/07/2020) rồi **ghép trái** giữ nguyên 14.056 dòng, **0 dòng thiếu thời tiết**; Delhi và Gurugram gần như trùng chuỗi thời tiết (r≈0,95 với mưa →0,999 với nhiệt độ).

### Diễn giải

Mẫu 8 TP đủ dài và đồng nhất ở mức cho phép để so sánh trong **khoảng chung 14/06/2017–01/07/2020**, nhưng không đại diện cho 26 TP hay cho “8 TP ô nhiễm nhất” (xem 1.1). Việc giữ nguyên số dòng và ghi cờ thay vì xóa giúp mọi thống kê sau này có thể lọc theo `_was_missing`/`_is_outlier`/`suspect_sensor_error` mà không làm đứt chuỗi. Nội suy chỉ khoảng ngắn hạn chế bịa số cho khối thiếu cấu trúc (cảm biến chưa lắp), đồng thời sửa lỗi `limit=14` khiến số ngày được lấp giảm so với bản cũ.

### Giới hạn

Toàn bộ §3 trong `cleaning_log` liệt kê 15 rủi ro cần mang sang diễn giải: chuỗi dài ngắn khác nhau (Gurugram từ 27/11/2015, Amritsar từ 27/02/2017, Jaipur từ 14/06/2017); mất Xylene/PM10 Chennai (84,5%) cho mọi phân tích dùng các cột này; **ô nội suy dùng giá trị tương lai** nên không mặc nhiên phù hợp cho dự báo thời gian thực; không loại trừ MNAR; IQR tính trên toàn chuỗi kể cả test; chưa đối chiếu CPCB nên chỉ gọi *nghi lỗi*; còn vài điểm rải rác (ví dụ Gurugram 30/08/2017) và xu hướng Benzene/Toluene 2015 ở Chennai/Bengaluru bị chi phối bởi năm 2015; thời tiết là mô hình lưới và **Delhi–Gurugram không độc lập**, thời tiết “ngày mai” là số đã xảy ra.

---

## C. Bản thảo 3.2. Kết quả EDA và các phát hiện chính

> Mỗi phát hiện dưới đây theo mạch **Câu hỏi → Biểu đồ → Số liệu → Diễn giải → Giới hạn** và đều gắn một hình trong `reports/figures/eda_*.png` với chân hình `provenance()` (nguồn + cỡ mẫu + khoảng ngày).

### C1. Ở đâu ô nhiễm nặng tập trung?

**Câu hỏi:** Trong khoảng chung 14/06/2017–01/07/2020, tần suất ngày AQI ≥201 phân bố thế nào giữa 8 TP?

**Biểu đồ:** `eda_01_poor_share_city.png` (cột ngang % ngày ≥201, sắp theo giá trị, trục từ 0, một màu nhấn) + `eda_05_aqi_distribution.png` (phân phối AQI) + `eda_00_sample_size.png` (cỡ mẫu).

**Số liệu:** Trên **1.114 ngày** chung, số ngày có AQI dao động **1.029 (Amritsar) →1.111 (Lucknow)**; median AQI: **Delhi 205, Lucknow 188, Gurugram 188, Jaipur 122, Amritsar 104, Hyderabad 89, Chennai 87, Bengaluru 81**. Tỷ lệ ngày **≥201**: **Delhi 51,0%, Lucknow 46,4%, Gurugram 46,3%** (≈½ số ngày) **gấp 4,1–4,6 lần** Amritsar **11,4%** / Jaipur **11,1%**; **Chennai 3,1%, Bengaluru 0,2%, Hyderabad 0,1%** gần như không có ngày nặng.

**Diễn giải:** Ba TP đồng bằng Bắc Ấn (Delhi, Gurugram, Lucknow) tạo nhóm rất nặng tách biệt; miền Nam (Bengaluru/Hyderabad/Chennai) gần như không có ngày vượt ngưỡng Poor. Median ít bị kéo bởi đuôi cực đoan hơn mean, nên được dùng để xếp thứ bậc.

**Giới hạn:** Amritsar thiếu 7,6% và Gurugram ~4% trên khoảng chung nên kém chắc hơn; kiểm tra độ nhạy xóa ngẫu nhiên 10% ×200 lần cho thấy **Lucknow↔Gurugram, Amritsar↔Jaipur, Bengaluru↔Hyderabad hay đổi chỗ**, do đó báo cáo **chia nhóm thay vì xếp hạng 1–8**. Confounder: số/vị trí trạm trong trung bình TP, quy mô đô thị/địa lý (dữ liệu không có vị trí trạm).

### C2. Khi nào ô nhiễm đạt đỉnh trong năm và có xu hướng theo năm không?

**Câu hỏi:** Ô nhiễm theo tháng/mùa và theo năm có hình thái gì, và 2020 có thấp hơn 2019 vì lockdown không?

**Biểu đồ:** `eda_02_heatmap_city_month.png` (heatmap City×Month) + `eda_03_trend_city_year.png` (xu hướng tháng 1–6 theo năm, kèm n).

**Số liệu:** **5 TP** Delhi/Gurugram/Lucknow/Jaipur/Amritsar chung mẫu hình **đỉnh tháng 11–12, đáy tháng 7–9**; ví dụ **Amritsar T11 median 209 gấp 3,1 lần T8=66**, **89/117 ngày (76%) ≥201** của Amritsar rơi T10–12. **Bengaluru gần như không mùa**: median chỉ **63–102 (đỉnh/đáy 1,6 lần)**, **2 ngày** ≥201 trên khoảng chung. Biểu đồ năm giới hạn **tháng 1–6** để tránh lệch mùa và loại 2020 H2.

**Diễn giải:** Mùa cao điểm tập trung cuối thu–đầu đông ở miền Bắc/Tây Bắc; miền Nam dao động mùa yếu. Xu hướng năm cần đọc kèm **bảng n** (ví dụ Jaipur T1–6/2017 chỉ 11 ngày) và phân tách **1/1–24/3 vs. 25/3–30/6** để chẩn đoán lockdown 25/3/2020, nhưng chỉ nêu “có liên quan”.

**Giới hạn:** Thời tiết theo mùa (gió, BLH, đốt rơm Punjab, Diwali) là confounder chưa có trong EDA này; chuỗi dài ngắn khác nhau và ô thưa dữ liệu khiến ô trung bình thiếu tin cậy; 2020 chỉ đến 01/07/2020.

### C3. Khi AQI nặng, chất nào tăng mạnh nhất so với chính nó?

**Câu hỏi:** Chất nào đi cùng AQI chặt nhất và tăng nhiều nhất vào ngày ≥201?

**Biểu đồ:** `eda_04_pm25_aqi.png` (PM2.5 vs. AQI) + bảng **C0** Spearman và **C1** tỉ số trung vị.

**Số liệu:** Trên khoảng chung **gộp 8 TP**, **Spearman PM2.5–AQI =0,91** vượt trội **NO2 0,52 / CO 0,48 / SO2 0,38 / O3 0,34**; tương quan giữa các chất 0,17–0,50. Trên **5 TP có ≥100 ngày nặng**, **trung vị PM2.5 gấp 2,8 lần** ngày thường (**2,1 Jaipur →3,1 Lucknow**; gộp 8 TP **137,1 vs. 42,0 µg/m³**), **NO2 1,7 lần, CO 1,6 lần, SO2/O3 ~1,1 lần**. **73,2%** ngày nặng rơi T10–2; **12,2%** (225/1.850) ngày nặng có PM2.5 <91 µg/m³.

**Diễn giải:** PM2.5 vừa tương quan hạng cao nhất với AQI vừa có biên độ tăng lớn nhất vào ngày nặng, trong khi SO2/O3 gần như không đổi. Do AQI lấy **chỉ số con lớn nhất**, tương quan cao của PM2.5 một phần là hệ quả công thức chọn ngày nặng theo chính AQI, cần thận trọng khi diễn giải “chất đóng góp”.

**Giới hạn — bắt buộc theo `GOI_BO_SUNG_BAO_CAO.md` §1:** Hai cách tổng hợp trả lời hai câu hỏi khác nhau và **không thay thế nhau**: (i) **trung vị tỷ số trên 5 TP =2,82 [2,42;3,17]** và (ii) **tỷ số gộp 8 TP =137,1/42≈3,26**. Không viết “cả 8 TP có trung vị 2,82” và không gắn nhãn 95% CI nếu chưa đối chiếu loại khoảng V16 trong DA. PM10/Chennai và Xylene đã loại nên không có trong so sánh; khi thử dựng lại AQI từ các chất chỉ ~33% ngày khớp ≤10 điểm, nên chỉ nói “chất nào ở mức cao nhất so với chính nó”.

---

**Ghi chú cho bước tiếp theo (3.3–3.4):** Bằng chứng **thời tiết–AQI** (`corr_01`–`corr_04`) và **dự báo** (`model_01`–`model_05`, notebook 06) sẽ được trình bày riêng, tuân thủ: không lấy số trên HTML làm nguồn chuẩn, chỉ trích count **32/48 vs. 33/48** hay family **15 (3/1/11)** khi có bảng V18/V19 kèm tiêu chí Bonferroni/BH; các số MAE 19,52/23,47 và giữ lại cuối 13,78/14,80 thuộc **đường trước sửa, không phải kết quả Dev mới** và không được gọi là ước lượng sạch leakage đã xác nhận.

