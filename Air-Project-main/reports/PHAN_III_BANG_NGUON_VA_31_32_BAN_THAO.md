# PHẦN III. KẾT QUẢ THỰC HIỆN — BẢNG NGUỒN VÀ BẢN THẢO 3.1–3.2 (BẢN SỬA 13/11/2026)

> **Hướng dùng:** Bảng nguồn (§A) là bản đồ trước khi viết đoạn. Mọi số trong §B (3.1–3.2) đều trỏ về bảng nguồn; số thuộc 3.3–3.4 (mô hình, HTML) **chưa trích làm bằng chứng** khi chưa đối chiếu `notebooks/06_predict_aqi.ipynb` và `model_*.png` của nhóm nộp. HTML chỉ là lớp trình bày, không thay bảng tính toán. Chỉ đối chiếu file/bảng hiện có; không chạy lại notebook.

---

## A. Bảng nguồn kết quả ngắn (3.1–3.4) — đúng cấu trúc đã chốt

| Mục báo cáo | Bảng/hình nguồn (đường dẫn cụ thể) | Phiên bản / Notebook & dữ liệu tương ứng | Số liệu định dùng (chỉ số chính) | Điểm cần đối chiếu trước khi chốt số |
|---|---|---|---|---|
| **3.1 Thu thập & tiền xử lý — tổng quan** | `reports/cleaning_log_8cities.md` §1 *Tổng quan kết quả* (bảng 3 dòng); `Data_dictionary.md` §1–2; `Metadata.json` *missing_pct_by_column*; `data/raw/city_day.csv` (29.531 dòng, 26 TP) → `data/processed/air_quality_8cities.csv` (14.056 dòng) | `notebooks/01_cleaning.ipynb` + `src/pipeline.py`/`src/utils.py`/`src/gap_utils.py` — commit nhóm nộp [Cần đối chiếu: `c4c75f6` hiện tại có phải bản nộp chính thức?] | 29.531 dòng gốc → **14.056 dòng** cho 8 TP, **0** dòng trùng (City,Date), **0** đứt ngày, **0** giá trị âm. 16 cột → **40 cột** (11 chất + AQI + AQI_Bucket + 12 cờ `_was_missing` + 11 cờ `_is_outlier` + 2 cờ khác + khóa). Ô thiếu (11 chất + AQI): **16.953 (10,05%) → 15.832 (9,39%)**. Công thức đối chiếu (phạm vi **11 chất + AQI**): **16.953 + 2.169 (chuỗi 0 treo → NaN) − 3.329 (tạo giá trị ước lượng cho khoảng thiếu ≤14 ngày) + 39 (nghi lỗi → NaN) = 15.832** — quy tắc nghi lỗi xử lý **41 ô** nhưng số ô thiếu tăng thêm thực tế là **39 ô** do một số ô đã thiếu trước bước này | Xác nhận 14.056 không đổi sau các bước; `cleaning_summary_8cities.csv` có **105 dòng văn bản = 104 bản ghi + 1 dòng tiêu đề** (8 TP ×13 cột =104 bản ghi) |
| **3.1 Tiền xử lý — bảng tổng hợp quy tắc** | `reports/cleaning_log_8cities.md` §2 Bước 1–11 và §3 Hạn chế; `reports/cleaning_summary_8cities.csv` (105 dòng văn bản =104 bản ghi +1 tiêu đề); `reports/suspect_points_8cities.csv` (94 dòng văn bản =93 bản ghi +1 tiêu đề) | `notebooks/02_cleaning_evidence.ipynb` + `src/utils.py:flag_flatline_zeros`, `_interpolate_short_gaps` | Tóm tắt: chuỗi 0 treo ≥3 ngày → NaN **2.169 ô**; bỏ Xylene + PM10 Lucknow; chỉ tạo giá trị ước lượng cho khoảng thiếu **≤14 ngày** **3.329 ô**; giữ NaN khối dài **9 cặp ≥20%** (7.733 ô, ≥60% không dùng làm biến); AQI thiếu **836 dòng** giữ NaN; IQR×1,5 theo tháng **6.656 ô** chỉ gắn cờ; **93 bản ghi** điều tra → **41 ô trên 24 ngày** đặt NaN (52 giữ lại); 139 ngày PM2.5>1,2×PM10 chỉ gắn cờ | Đối chiếu ngưỡng flatline 3 ngày, k=1,5, top-5 mỗi TP có phải quy ước nhóm nộp? |
| **3.1 Thời tiết (nguồn thứ hai)** | `reports/cleaning_log_8cities.md` Bước 12–17; `Data_dictionary.md` §3; `Metadata.json` §weather_source; `data/raw/weather/openmeteo_*_hourly.csv.gz` (48.384 dòng giờ/TP); `data/processed/weather_daily_8cities.csv` (16.128 dòng); `data/processed/air_quality_8cities_weather.csv` (14.056×54) | `notebooks/04_weather_merge.ipynb` + `src/weather_utils.py` — Open-Meteo ERA5, múi `Asia/Kolkata`, CC BY 4.0 | **387.072 dòng giờ** (8×48.384) → **16.128 ngày-thành phố** → ghép trái giữ nguyên 14.056 dòng, **0 dòng thiếu thời tiết**, `assert_frame_equal` với bảng cũ. Tọa độ lưới lệch ≤0,12°; **chuỗi thời tiết của hai thành phố Delhi–Gurugram tương quan cao (r≈0,95 với mưa →0,999 với nhiệt độ)** → cần thận trọng khi coi là bằng chứng không gian độc lập | Đối chiếu 8 tọa độ yêu cầu vs. ô lưới ERA5 thực dùng, độ cao ô lưới, giấy phép CC BY 4.0 |
| **3.2 EDA — Ở đâu (không gian)** | `reports/figures/eda_00_sample_size.png`; `eda_01_poor_share_city.png`; `eda_05_aqi_distribution.png`; bảng A1 trong `notebooks/03_eda.ipynb` §A1 (khoảng chung) | `notebooks/03_eda.ipynb` Phần A + `src/eda_utils.py` (khoảng chung 14/06/2017–01/07/2020, ngưỡng Poor =201, palette #D55E00) | **n** trên 1.114 ngày chung: Amritsar 1.029 → Lucknow 1.111 (thiếu 7,6% vs ~1%). **Median AQI:** Delhi 205, Lucknow 188, Gurugram 188, Jaipur 122, Amritsar 104, Hyderabad 89, Chennai 87, Bengaluru 81. **% ngày ≥201:** Delhi **51,0%**, Lucknow **46,4%**, Gurugram **46,3%** (≈½ số ngày) gấp **4,1–4,6 lần** Amritsar 11,4% / Jaipur 11,1%; ba thành phố phía Nam được khảo sát có tỷ lệ ngày AQI ≥201 thấp trong khoảng quan sát (Chennai 3,1%, Bengaluru 0,2%, Hyderabad 0,1%) | Đối chiếu định nghĩa Poor ≥201 (CPCB) và khoảng chung; kiểm bảng A1 n vs. % (Amritsar/Gurugram thưa hơn). Nhóm thay vì xếp hạng 1–8 do độ nhạy |
| **3.2 EDA — Khi nào (thời gian)** | `reports/figures/eda_02_heatmap_city_month.png`; `eda_03_trend_city_year.png`; `aqi_monthly_lucknow_jaipur.png` (tài liệu cũ) | `notebooks/03_eda.ipynb` Phần B (§B1–B3), bảng B0 (tháng 1–6 so năm, kèm n) | **Mùa:** Delhi/Gurugram/Lucknow/Jaipur/Amritsar **đỉnh tháng 11–12, đáy tháng 7–9**; Amritsar: median **T11=209 gấp 3,1 lần T8=66**, **89/117 ngày (76%)** ≥201 rơi T10–12; **Bengaluru có biên độ trung vị theo tháng nhỏ hơn ví dụ thành phố phía Bắc được so sánh** (63–102, 1,6 lần, 2 ngày ≥201). **Năm (T1–6):** B3 chẩn đoán 2020 vs 2019 tách 1/1–24/3 và 25/3–30/6 để kiểm lockdown 25/3/2020 — chỉ nêu “có liên quan” | Đối chiếu định nghĩa mùa Đông (12–2)/Hè/Mưa/Sau mưa trong `eda_utils.py`; xác nhận chỉ dùng tháng 1–6 khi so năm và loại 2020 H2; không gọi lockdown là nguyên nhân |
| **3.2 EDA — Chất nào (tỷ số ngày nặng / ngày thường)** | `reports/figures/eda_04_pm25_aqi.png`; bảng C0 (Spearman), bảng C1 (tỷ số trung vị) trong `notebooks/03_eda.ipynb` Phần C | `notebooks/03_eda.ipynb` Phần C + `Data_dictionary.md` (đơn vị) | **C0 Spearman (khoảng chung, gộp 8 TP):** PM2.5 **0,91**, NO2 0,52, CO 0,48, SO2 0,38, O3 0,34; giữa các chất 0,17–0,50. **C1 (≥201 vs. ngày thường, 5 TP ≥100 ngày nặng): trên năm thành phố đủ điều kiện của phép so sánh, trung vị các tỷ số PM2.5 giữa nhóm ngày AQI ≥201 và nhóm ngày còn lại là 2,82. Khi gộp dữ liệu của tám thành phố, trung vị PM2.5 của hai nhóm lần lượt là 137,1 và 42,0 µg/m³, tương ứng tỷ số khoảng 3,26. Đây là cách tổng hợp khác với trung vị tỷ số theo thành phố.** PM10/Chennai không dùng trong phép so sánh cụ thể này (thiếu 84,5%) — phân biệt với xóa cột khỏi toàn bộ dữ liệu | **Đính chính:** 2,82 và 3,26 là **tỷ số nồng độ PM2.5 giữa ngày nặng/ngày thường**, không phải tỷ số mùa đông/mùa mưa. **Tạm bỏ khoảng [2,42;3,17] khỏi đoạn chính** cho đến khi xác định đúng loại khoảng từ V16. Đối chiếu loại khoảng DA trước khi gắn nhãn 95% CI; ghi confounder cách tính AQI (max chỉ số con) và mùa |
| **3.2 EDA — Thời tiết–AQI (bổ sung vào 3.2)** | `reports/figures/corr_01_raw_vs_adjusted.png` (thô vs. khử mùa); `corr_02_hypothesis_tests.png` (15 so sánh, Bonferroni); `corr_03_humidity_deciles.png`; `corr_04_poor_share_by_humidity.png` | `notebooks/05_weather_correlation.ipynb` + `src/corr_utils.py` (`add_anomalies` median City×Month, `block_id` 14 ngày, `boot_median_diff`, `bh_adjust`) | **Thô vs. khử mùa:** Delhi nhiệt độ **−0,52→+0,23**, áp suất **+0,63→−0,16**, BLH **−0,38→+0,08 (KTC chứa 0)**; độ ẩm giữ chiều âm 8/8 TP (−0,14→−0,48). **Family 15 (3 giả thuyết ×5 TP):** **3 ủng hộ** (gió yếu Delhi; không mưa Jaipur/Amritsar), **1 ngược chiều** (BLH thấp đi cùng AQI thấp hơn ở Jaipur), **11 chưa đủ bằng chứng** (KTC chứa 0). Count tổng **32/48 sau BH** vs. **33/48 theo CI danh nghĩa** [V18] là **hai family/tiêu chí khác nhau — không cộng mẫu số** | Chỉ trích count khi có bảng V18/V19 kèm tiêu chí (Bonferroni vs. BH-FDR); p-value công thức quá lạc quan so với bootstrap theo khối |
| **3.3 Mô hình & đánh giá (mở rộng)** | `reports/figures/model_01_residual_diagnostics.png` … `model_05_humidity_recheck.png` | `notebooks/06_predict_aqi.ipynb` + `src/model_utils.py` (TRAIN_END 30/06/2019, giai đoạn kiểm thử 01/07/2019–29/02/2020, LOCKDOWN từ 01/03/2020, Levels L1–L4, Ridge/HGB, TimeSeriesSplit 4×gap 16, block 14 ngày) — **phiên bản nhóm nộp** | **Bằng chứng DA vòng trước (KHÔNG phải số Dev mới):** test L3 **MAE 19,52 vs. persistence 23,47**; giai đoạn giữ lại cuối L3 **13,78 vs. 14,80 chênh −1,02 [−2,70;0,48] chưa đủ bằng chứng**. Chỉ dùng nếu khớp phiên bản notebook nhóm nộp và công khai hạn chế preprocessing | **Không lấy HTML làm nguồn chuẩn**; F01 chưa hoàn tất, không tuyên bố loại bỏ hoàn toàn leakage; kịch bản sử dụng thời tiết ngày mai gọi là **kịch bản tham chiếu sử dụng thông tin thời tiết ngày mai** (không gọi “cận trên L4”) |
| **3.4 Sản phẩm minh họa** | `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` + `docs/GOI_BO_SUNG_BAO_CAO.md` §2 | Phiên bản HTML v5 hiện tại (bản sao Test) — chưa phải bản nhóm nộp đã nghiệm thu | **Tính năng:** chọn (TP, ngày) xem AQI hôm nay→dự báo mai qua L1→L3; toàn cảnh giai đoạn kiểm thử; kéo ngưỡng cảnh báo (166/160 vs. 201 chuẩn); bảng hệ số Ridge trên log(AQI). Số trên HTML (MAE 19,52 −16,8% v.v.) là **lớp trình bày** | **Phải sửa trước khi trích:** đổi mọi “mùa đông (01/07/2019–29/02/2020)” → **“giai đoạn kiểm thử (01/07/2019–29/02/2020)”**; xóa tuyên bố **“chống rò rỉ dữ liệu tuyệt đối”**; ghi rõ là **phát lại kết quả trên dữ liệu lịch sử, chưa khẳng định dự báo trực tuyến**; Dev cache/đặc trưng gốc là hướng phát triển chưa tích hợp |

*Ghi chú đếm file: `cleaning_summary_8cities.csv` có **105 dòng văn bản gồm 104 bản ghi + 1 dòng tiêu đề** (8 TP ×13 cột =104 bản ghi); `suspect_points_8cities.csv` có **94 dòng văn bản gồm 93 bản ghi + 1 dòng tiêu đề** (không suy từ 94 dòng văn bản thành 94 bản ghi).*

---

## B. Bản thảo 3.1. Kết quả thu thập và tiền xử lý (bản rút gọn)

### Câu hỏi của mục

Tập dữ liệu sau thu thập có đủ và được chuẩn hóa ở mức nào để so sánh 8 thành phố theo thời gian, và những quy tắc làm sạch nào để lại dấu vết cho các bước sau?

### Quy mô và cấu trúc

Trên 8 thành phố được chọn, tập làm việc giữ nguyên **14.056 dòng** (mỗi dòng một cặp City–Date, không trùng khóa, không đứt ngày) và **0 giá trị âm**; `AQI_Bucket` khớp thang CPCB. Số cột tăng từ **16 → 40** (11 chất được giữ + AQI + AQI_Bucket + 12 cờ `_was_missing` + 11 cờ `_is_outlier` + `pm25_gt_pm10_flag` + `suspect_sensor_error` + khóa). Ô thiếu của 11 chất + AQI chuyển từ **16.953 (10,05%) → 15.832 (9,39%)** theo công thức đối chiếu (phạm vi 11 chất + AQI): **16.953 + 2.169 (chuỗi 0 treo → NaN) − 3.329 (tạo giá trị ước lượng cho khoảng thiếu ≤14 ngày) + 39 (nghi lỗi → NaN) = 15.832** — quy tắc nghi lỗi xử lý 41 ô nhưng số ô thiếu tăng thêm thực tế là 39 ô do một số ô đã thiếu trước bước này. Chỉ một số ô tại 24 ngày bị xử lý, không phải toàn bộ ngày bị xóa.

Dẫn chứng: bảng tổng quan §1 `cleaning_log_8cities.md`; bảng chi tiết `cleaning_summary_8cities.csv` (105 dòng văn bản =104 bản ghi +1 tiêu đề); bảng truy vết `suspect_points_8cities.csv` (94 dòng văn bản =93 bản ghi +1 tiêu đề).

### Bảng tổng hợp ảnh hưởng của các quy tắc làm sạch

| Quy tắc | Ngưỡng/định nghĩa | Số ô/dòng bị ảnh hưởng chính | Cách lưu vết |
|---|---|---|---|
| Chuỗi 0 treo | ≥3 ngày liên tiếp =0 | **2.169 ô** | `_was_missing` |
| Loại cột | Xylene toàn bộ; PM10 Lucknow | 4.234 ô Xylene + 2.009 ô PM10 rỗng | `status=dropped` |
| Tạo giá trị ước lượng cho khoảng thiếu ngắn | ≤14 ngày, nằm giữa hai giá trị thật, tuyến tính theo thời gian | **3.329 ô** | `_was_missing` |
| Giữ NaN khối dài | >14 ngày; 9 cặp thiếu ≥20% | **7.733 ô** giữ NaN (≥60% không dùng làm biến) | giữ NaN |
| AQI thiếu | không tạo giá trị ước lượng | **836 dòng** | giữ NaN |
| Ngoại lai | IQR×1,5 theo tháng | **6.656 ô** (PM2.5 531 ngày) | `_is_outlier` chỉ gắn cờ |
| Nghi lỗi cảm biến | top-5 PM2.5/AQI mỗi TP + tiêu chí PM2.5>1,5×PM10 | **41 ô trên 24 ngày** (trong `suspect_points_8cities.csv` 93 bản ghi, 52 giữ lại) | `suspect_sensor_error` |
| Nhất quán PM2.5–PM10 | PM2.5>1,2×PM10 | 139 ngày | `pm25_gt_pm10_flag` |

*Ghi chú: Lịch sử sửa lỗi `interpolate(limit=14)` cũ, ví dụ Bengaluru NOx =0 suốt 207 ngày, và toàn bộ 15 rủi ro được chuyển sang **Phụ lục — Ghi chú biên tập** để giữ 3.1 gọn.*

### Kết quả tích hợp thời tiết

Từ **387.072 dòng giờ** (8 TP ×48.384) gộp thành **16.128 ngày-thành phố** với 14 cột thời tiết (ERA5 lưới 0,25°, múi Asia/Kolkata, 25/12/2014–01/07/2020), ghép trái giữ nguyên **14.056 dòng**, **0 dòng thiếu thời tiết** và `assert_frame_equal` với bảng không thời tiết. Tọa độ lưới lệch ≤0,12°; chuỗi thời tiết của hai thành phố Delhi–Gurugram tương quan cao (r≈0,95 với mưa →0,999 với nhiệt độ) nên cần thận trọng khi coi là bằng chứng không gian độc lập.

### Hạn chế quan trọng cần mang sang diễn giải

Ô được tạo giá trị ước lượng đã **dùng giá trị của các ngày sau** (phương pháp hồi cứu) nên không mặc nhiên phù hợp cho dự báo thời gian thực; chuỗi các thành phố dài ngắn khác nhau (Gurugram từ 27/11/2015, Amritsar từ 27/02/2017, Jaipur từ 14/06/2017) nên chỉ so sánh trong khoảng chung 14/06/2017–01/07/2020; thời tiết là dữ liệu mô hình lưới và thời tiết “ngày mai” trong dữ liệu là số tái phân tích đã xảy ra (kịch bản tham chiếu sử dụng thông tin thời tiết ngày mai chỉ để tham chiếu).

---

## C. Bản thảo 3.2. Kết quả EDA và các phát hiện chính

> Mỗi phát hiện theo mạch **Câu hỏi → Biểu đồ → Số liệu → Diễn giải → Giới hạn** và gắn một hình `reports/figures/eda_*`/`corr_*` với chân hình `provenance()` (nguồn + cỡ mẫu + khoảng ngày).

### C1. Ở đâu ô nhiễm nặng tập trung?

**Câu hỏi:** Trong khoảng chung 14/06/2017–01/07/2020, tần suất ngày AQI ≥201 phân bố thế nào?

**Biểu đồ:** `eda_01_poor_share_city.png` + `eda_05_aqi_distribution.png` + `eda_00_sample_size.png`.

**Số liệu:** Trên 1.114 ngày chung, n có AQI =1.029 (Amritsar)→1.111 (Lucknow); median AQI Delhi 205/Lucknow 188/Gurugram 188/Jaipur 122/Amritsar 104/Hyderabad 89/Chennai 87/Bengaluru 81. Tỷ lệ ≥201: Delhi **51,0%**, Lucknow **46,4%**, Gurugram **46,3%** (≈½ số ngày) gấp 4,1–4,6× Amritsar 11,4%/Jaipur 11,1%; ba thành phố phía Nam được khảo sát có tỷ lệ ngày AQI ≥201 thấp trong khoảng quan sát (Chennai 3,1%, Bengaluru 0,2%, Hyderabad 0,1%).

**Diễn giải:** Ba TP đồng bằng Bắc Ấn tạo nhóm rất nặng tách biệt; nhóm phía Nam thấp hơn rõ rệt. Median ít bị kéo bởi đuôi cực đoan hơn mean.

**Giới hạn:** Amritsar thiếu 7,6% nên kém chắc hơn; độ nhạy xóa 10%×200 cho thấy Lucknow↔Gurugram, Amritsar↔Jaipur, Bengaluru↔Hyderabad hay đổi chỗ → báo cáo chia nhóm thay vì xếp hạng 1–8. Confounder: số/vị trí trạm trong trung bình TP (dữ liệu không có vị trí trạm).

### C2. Khi nào ô nhiễm đạt đỉnh trong năm và có xu hướng theo năm không?

**Câu hỏi:** Biến động theo tháng/mùa và theo năm có hình thái gì?

**Biểu đồ:** `eda_02_heatmap_city_month.png` + `eda_03_trend_city_year.png`.

**Số liệu:** 5 TP Delhi/Gurugram/Lucknow/Jaipur/Amritsar chung mẫu hình đỉnh T11–12 đáy T7–9 (Amritsar T11 median 209 gấp 3,1×T8 66; 89/117 ngày (76%) ≥201 rơi T10–12). Bengaluru có biên độ trung vị theo tháng nhỏ hơn ví dụ thành phố phía Bắc được so sánh (63–102, 1,6×, 2 ngày ≥201). Năm chỉ dùng T1–6, tách 1/1–24/3 vs 25/3–30/6 để chẩn đoán lockdown 25/3/2020.

**Diễn giải:** Mùa cao điểm tập trung cuối thu–đầu đông ở Bắc/Tây Bắc; miền Nam dao động mùa yếu hơn. Xu hướng năm đọc kèm bảng n (Jaipur T1–6/2017 chỉ 11 ngày).

**Giới hạn:** Thời tiết/mùa vụ (gió, BLH, đốt rơm Punjab, Diwali) là confounder chưa có trong EDA này; chỉ nêu “có liên quan” với lockdown.

### C3. Khi AQI nặng, chất nào tăng mạnh nhất so với chính nó?

**Câu hỏi:** Chất nào đi cùng AQI chặt nhất và tăng nhiều nhất vào ngày ≥201?

**Biểu đồ:** `eda_04_pm25_aqi.png` + bảng C0/C1.

**Số liệu:** Gộp 8 TP, Spearman PM2.5–AQI **0,91** (NO2 0,52/CO 0,48/SO2 0,38/O3 0,34). Trên 5 TP đủ điều kiện (≥100 ngày nặng), **trung vị các tỷ số PM2.5 giữa nhóm ngày AQI ≥201 và nhóm ngày còn lại là 2,82**. Khi gộp dữ liệu của tám thành phố, trung vị PM2.5 của hai nhóm lần lượt là **137,1 và 42,0 µg/m³, tương ứng tỷ số khoảng 3,26. Đây là cách tổng hợp khác với trung vị tỷ số theo thành phố.** NO2 1,7×, CO 1,6×, SO2/O3 ~1,1×; 73,2% ngày nặng rơi T10–2; 12,2% (225/1.850) ngày nặng có PM2.5 <91 µg/m³.

**Diễn giải:** PM2.5 vừa tương quan hạng cao nhất vừa có biên độ tăng lớn nhất, trong khi SO2/O3 gần như không đổi. AQI lấy chỉ số con lớn nhất nên tương quan cao của PM2.5 một phần là hệ quả công thức.

**Giới hạn:** PM10 ở Chennai không dùng trong phép so sánh cụ thể này (thiếu 84,5%) — phân biệt với xóa cột khỏi toàn bộ dữ liệu. Khoảng [2,42;3,17] tạm bỏ khỏi đoạn chính cho đến khi xác định đúng loại khoảng từ V16; chỉ ~33% ngày dựng lại AQI từ các chất khớp ≤10 điểm nên chỉ nói “chất nào ở mức cao nhất so với chính nó”.

### C4. Thời tiết–AQI: bỏ chu kỳ mùa làm tương quan đổi hẳn (bổ sung vào 3.2)

**Câu hỏi:** Sau khi khử mùa vụ, thời tiết còn đi cùng AQI ở mức nào?

**Biểu đồ:** `corr_01_raw_vs_adjusted.png` (thô vs. khử mùa) + `corr_02_hypothesis_tests.png` (15 so sánh) + `corr_03_humidity_deciles.png` + `corr_04_poor_share_by_humidity.png`.

**Số liệu:** Delhi: nhiệt độ **−0,52→+0,23**, áp suất **+0,63→−0,16**, BLH **−0,38→+0,08 (KTC chứa 0)** khi chỉ so các ngày trong cùng tháng; độ ẩm giữ chiều âm **8/8 TP (−0,14→−0,48)**. Family 15 (3 giả thuyết ×5 TP): **3 ủng hộ** (gió yếu Delhi; không mưa Jaipur/Amritsar), **1 ngược chiều** (BLH thấp đi cùng AQI thấp hơn ở Jaipur), **11 chưa đủ bằng chứng** (KTC chứa 0). Count tổng **32/48 sau BH** vs. **33/48 theo CI danh nghĩa** là hai family/tiêu chí khác nhau — không cộng mẫu số.

**Diễn giải:** Tương quan thô chủ yếu phản ánh mùa; chỉ độ ẩm nhất quán giữ chiều âm sau khử mùa. Gió/BLH yếu hơn kỳ vọng.

**Giới hạn:** Khử mùa bằng median City×Month còn sót chu kỳ trong tháng; p-value công thức quá lạc quan so với bootstrap theo khối, nên kết luận dựa vào KTC theo khối. Chỉ nói “có liên quan/đi cùng”, không suy nhân quả.

---

## Phụ lục — Ghi chú biên tập (chuyển khỏi 3.1 để rút gọn)

- Lịch sử sửa lỗi `interpolate(limit=14)` cũ (1.316 ô ở 6 TP), ví dụ Bengaluru NOx =0 suốt 207 ngày trước đó còn 6,48, và kiểm nhạy đổi ngưỡng flatline 2/5/7 ngày.
- Danh sách 9 cặp thiếu ≥20%, chi tiết AQI thiếu 0,5%→13,6%, và 15 rủi ro đầy đủ từ `cleaning_log` §3.

---

**Ghi chú cho bước tiếp theo (3.3–3.4):** Bằng chứng dự báo (`model_01`–`model_05`, `06_predict_aqi.ipynb`) sẽ trình bày riêng, tuân thủ: không lấy số trên HTML làm chuẩn, chỉ trích 32/48 hay 15 (3/1/11) khi có bảng V18/V19 kèm tiêu chí; số MAE 19,52/23,47 thuộc đường trước sửa, không phải kết quả Dev mới; mọi kịch bản dùng thời tiết ngày mai gọi là **kịch bản tham chiếu sử dụng thông tin thời tiết ngày mai**.
