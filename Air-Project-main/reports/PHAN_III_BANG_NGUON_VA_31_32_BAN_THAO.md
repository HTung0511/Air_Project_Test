# PHẦN III. KẾT QUẢ THỰC HIỆN — BẢNG NGUỒN VÀ BẢN THẢO 3.1–3.4 (BẢN SỬA 13/11/2026 — BỔ SUNG 3.3–3.4)

> **Hướng dùng:** Bảng nguồn (§A) là bản đồ trước khi viết đoạn. Mọi số trong §B–D (3.1–3.4) đều trỏ về bảng nguồn; HTML chỉ là lớp trình bày cho 3.4, không thay bảng tính toán. Chỉ đối chiếu file/bảng hiện có; không chạy lại notebook.

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
| **3.2 EDA — Thời tiết–AQI** | `reports/figures/corr_01_raw_vs_adjusted.png`; `corr_02_hypothesis_tests.png`; `corr_03_humidity_deciles.png`; `corr_04_poor_share_by_humidity.png` | `notebooks/05_weather_correlation.ipynb` + `src/corr_utils.py` (điều chỉnh = anomaly lấy giá trị trừ trung vị City×Month, bootstrap khối 14 ngày, Bonferroni/BH-FDR) | **Trước vs. sau điều chỉnh mùa vụ:** ví dụ Delhi nhiệt độ **−0,52→+0,23**, áp suất **+0,63→−0,16**, BLH **−0,38→+0,08 (KTC chứa 0)**; độ ẩm giữ chiều âm 8/8 TP (−0,14→−0,48). **Nhóm kiểm định nêu trước (family 15 = 3 giả thuyết ×5 TP):** 3 ủng hộ, 1 ngược chiều, 11 chưa đủ bằng chứng (Bonferroni trên family này). **Trên 48 cặp quan hệ thời tiết–AQI:** trong 48 cặp được xét, **32 cặp đạt tiêu chí sau hiệu chỉnh BH-FDR**, trong khi **33 cặp có khoảng tin cậy danh nghĩa không chứa 0** — hai cách đánh giá không hoàn toàn tương đương | Family 15 và 48 cặp là **hai nhóm kiểm định khác nhau** với tiêu chí hiệu chỉnh tương ứng; chỉ nêu count khi có bảng V18/V19 kèm tiêu chí. Thao tác điều chỉnh được mô tả đúng là *anomaly = giá trị − trung vị City×Month* rồi tính tương quan trên anomaly, không đồng nghĩa chỉ tính tương quan giữa các ngày cùng tháng |
| **3.3 Mô hình & đánh giá (mở rộng)** | `reports/figures/model_01_residual_diagnostics.png`; `model_02_mae_by_model.png`; `model_03_mae_by_city.png`; `model_04_precision_recall.png`; `model_05_humidity_recheck.png` + bảng MAE/R²/Precision/Recall trong `notebooks/06_predict_aqi.ipynb` | `notebooks/06_predict_aqi.ipynb` + `src/model_utils.py` (TRAIN_END 30/06/2019, giai đoạn kiểm thử 01/07/2019–29/02/2020, LOCKDOWN từ 01/03/2020, Levels L1–L4, Ridge chính vs. HGB so sánh, TimeSeriesSplit 4×gap 16, bootstrap khối 14 ngày) — **phiên bản nhóm nộp** | Trên giai đoạn kiểm thử (1.947 cặp TP-ngày, 389 ngày nặng): **baseline persistence (ngày mai = hôm nay) MAE 23,47; Ridge L3 (AQI lịch sử + chất ô nhiễm + thời tiết đến hết hôm nay) MAE 19,52, giảm 3,95 điểm (−16,8%) với KTC bootstrap khối không chứa 0**. Đóng góp biên: L1→L2 −2,0; L2→L3 −1,4 [−1,9;−0,9]; kịch bản tham chiếu dùng thời tiết ngày mai chỉ −0,43. **Giai đoạn giữ lại cuối** (không dùng chọn ngưỡng): L3 13,78 vs. 14,80 chênh −1,02 [−2,70;0,48] chưa đủ bằng chứng — thuộc **đường trước sửa**, không phải số Dev mới, chỉ dùng khi khớp phiên bản notebook nhóm nộp | **Không lấy HTML làm nguồn chuẩn** cho 3.3; mọi scaler/imputer chỉ fit trên train; số giai đoạn giữ lại cuối thuộc đường trước sửa, cần công khai hạn chế preprocessing |
| **3.4 Sản phẩm minh họa** | `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` (title, lead, 4 tab, biểu đồ MAE/Precision/Recall, bảng hệ số) + `docs/GOI_BO_SUNG_BAO_CAO.md` §2 | Phiên bản HTML v5 hiện tại (bản sao Test) — chưa phải bản nhóm nộp đã nghiệm thu | **Tính năng:** chọn (TP, ngày) xem AQI hôm nay→dự báo mai qua L1→L3; toàn cảnh giai đoạn kiểm thử; kéo ngưỡng cảnh báo (166/160 vs. 201 chuẩn); bảng hệ số Ridge trên log(AQI). Số trên HTML là **lớp trình bày**, trùng đường trước sửa | **Phải sửa trước khi trích:** đổi mọi “mùa đông (01/07/2019–29/02/2020)” → **“giai đoạn kiểm thử (01/07/2019–29/02/2020)”**; xóa tuyên bố **“chống rò rỉ dữ liệu tuyệt đối”**; ghi rõ là **phát lại kết quả trên dữ liệu lịch sử, chưa khẳng định dự báo trực tuyến** |

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

*Ghi chú: Lịch sử sửa lỗi `interpolate(limit=14)` cũ và toàn bộ 15 rủi ro được chuyển sang **Phụ lục — Ghi chú biên tập** để giữ 3.1 gọn.*

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

### C4. Mối liên hệ thời tiết–AQI trước và sau điều chỉnh mùa vụ

**Câu hỏi:** Sau khi điều chỉnh mùa vụ, thời tiết còn đi cùng AQI ở mức nào?

**Biểu đồ:** `corr_01_raw_vs_adjusted.png` (trước vs. sau điều chỉnh) + `corr_02_hypothesis_tests.png` (nhóm kiểm định nêu trước) + `corr_03_humidity_deciles.png` + `corr_04_poor_share_by_humidity.png`.

**Số liệu:** Ví dụ Delhi, nhiệt độ chuyển từ **−0,52 thành +0,23**, áp suất từ **+0,63 thành −0,16**, BLH từ **−0,38 thành +0,08 (KTC chứa 0)** sau điều chỉnh; **sự thay đổi về dấu và độ lớn của một số hệ số sau điều chỉnh cho thấy mùa vụ có thể ảnh hưởng đáng kể đến tương quan quan sát được.** Độ ẩm giữ chiều âm **8/8 TP (−0,14→−0,48)**. Nhóm kiểm định nêu trước gồm **15 so sánh (3 giả thuyết ×5 TP)**: **3 ủng hộ** (gió yếu Delhi; không mưa Jaipur/Amritsar), **1 ngược chiều** (BLH thấp đi cùng AQI thấp hơn ở Jaipur), **11 chưa đủ bằng chứng** (KTC chứa 0, Bonferroni trên nhóm này). Trên **48 cặp quan hệ thời tiết–AQI** được xét tổng thể, **trong 48 cặp được xét, 32 cặp đạt tiêu chí sau hiệu chỉnh BH-FDR, trong khi 33 cặp có khoảng tin cậy danh nghĩa không chứa 0. Hai cách đánh giá không hoàn toàn tương đương.**

**Thao tác điều chỉnh:** Với mỗi cột thời tiết và AQI, nhóm tính **anomaly = giá trị − trung vị City×Month** (trung vị của cùng thành phố, cùng tháng dương lịch trên toàn bộ chuỗi), sau đó tính **Spearman trên các anomaly**; thao tác này điều chỉnh mức nền theo mùa chứ không đồng nghĩa chỉ tính tương quan giữa các ngày cùng tháng.

**Diễn giải:** Chỉ độ ẩm nhất quán giữ chiều âm sau điều chỉnh; gió/BLH yếu hơn kỳ vọng ban đầu.

**Giới hạn:** Khử mùa bằng trung vị City×Month còn sót chu kỳ trong tháng; do dữ liệu có phụ thuộc theo thời gian, kết quả từ công thức giả định các quan sát độc lập cần được diễn giải thận trọng; phân tích sử dụng thêm **bootstrap theo khối 14 ngày** để đánh giá độ bất định. Chỉ nói “có liên quan/đi cùng”, không suy nhân quả.

---

## D. Bản thảo 3.3. Kết quả mô hình hóa và đánh giá

> Bài toán dự báo AQI ngày mai là **phần mở rộng**, không lấn át trọng tâm phân tích. Nguồn chuẩn cho mọi số dưới đây là **bảng kết quả trong `notebooks/06_predict_aqi.ipynb` và hình `model_*.png`** của phiên bản nhóm nộp; HTML chỉ dùng cho 3.4. Chỉ đối chiếu file/bảng hiện có; không chạy lại phân tích. Các số thuộc đường trước sửa được nêu kèm chú thích phiên bản, không trộn với số của bản sửa Dev chưa tích hợp.

### D0. Thiết kế đánh giá và độ mạnh của baseline

**Câu hỏi:** Với dữ liệu lịch sử, việc dự báo AQI ngày mai khó đến đâu nếu chỉ sao chép hôm nay?

**Bảng/biểu đồ:** Bảng kiểm tra tập `06_predict_aqi.ipynb` §0 *Setup* + `src/model_utils.py` (TRAIN_END 30/06/2019; giai đoạn kiểm thử 01/07/2019–29/02/2020; LOCKDOWN từ 01/03/2020 tách riêng; TimeSeriesSplit 4 lần × gap 16 dòng).

**Số liệu:** Tập kiểm thử có **1.947 cặp (thành phố, ngày)** với **389 ngày nặng** (AQI ≥201); lockdown chỉ **18 ngày nặng**. Tỷ lệ ngày nặng giảm dần: **24,9% (train) →20,0% (kiểm thử) →1,8% (lockdown)**. Trên kiểm thử, ba baseline trên thang điểm AQI: **trung bình theo thành phố MAE 60,5**, **trung vị cùng tháng (khí hậu) 55,8**, **ngày mai = hôm nay (persistence) 23,47** (R² 0,86). Mô hình chính là **Ridge trên log(AQI)** với 4 mức đặc trưng (L1 lịch sử AQI + mùa; L2 + chất ô nhiễm; L3 + thời tiết đến hết hôm nay; L4 kịch bản tham chiếu dùng thời tiết ngày mai); mọi scaler/imputer chỉ fit trên train; ô đã tạo giá trị ước lượng ở bước làm sạch được đặt lại NaN rồi điền lùi 2 ngày trước khi đưa vào Pipeline.

**Diễn giải:** Persistence là baseline rất mạnh do tự tương quan ngày liền kề cao; hai baseline trung bình/khí hậu gần như vô dụng cho dự báo 1 ngày. Mọi so sánh hiệu năng phải đọc kèm baseline này.

**Giới hạn:** Ba TP phía Nam có <30 ngày nặng trên kiểm thử nên không đánh giá được cảnh báo ở đó; lockdown quá ít ngày nặng nên chỉ dùng để xem sai số, không tính recall/precision.

### D1. Chẩn đoán mô hình trên thang log

**Câu hỏi:** Thang log(AQI) có cải thiện giả thiết hồi quy tuyến tính không?

**Biểu đồ:** `model_01_residual_diagnostics.png` (phần dư vs. dự đoán, QQ-plot, Breusch-Pagan).

**Số liệu:** Mô hình trên **AQI thô** cho phần dư cong và dự đoán AQI âm (đến −150, vô lý). Trên **log(AQI)**, đám mây phần dư quanh 0, Spearman(phần dư, giá trị khớp) từ **0,23 → −0,03** (hết dạng phễu); **Breusch-Pagan LM giảm từ 409 → 311** nhưng vẫn bác bỏ phương sai đều (phương sai còn khác theo TP/mùa).

**Diễn giải:** Log làm tuyến tính và ổn định phương sai rõ rệt, nhưng phương sai chưa đều hoàn toàn.

**Giới hạn:** Hệ số không chệch nhưng sai số chuẩn mặc định sai; mọi khoảng tin cậy và kiểm định ở D3–D4 dùng **sai số chuẩn bền theo cụm khối 14 ngày**, không dùng p-value mặc định.

### D2. Hiệu năng trên giai đoạn kiểm thử — giảm sai số điểm AQI

**Câu hỏi:** Thêm chất ô nhiễm và thời tiết giảm MAE bao nhiêu so với persistence, và đóng góp biên của thời tiết là bao nhiêu?

**Biểu đồ:** `model_02_mae_by_model.png` (MAE theo mức) + bảng MAE/R² trong notebook + bảng hiệu số bootstrap khối.

**Số liệu (phiên bản nhóm nộp, đường trước sửa — ghi rõ phiên bản):** Trên 1.947 ngày kiểm thử, **Ridge L3 (đủ 3 mức) MAE 19,52 so với persistence 23,47, giảm 3,95 điểm (−16,8%) với KTC bootstrap theo khối 14 ngày không chứa 0; R² 0,86 →0,91, RMSE 37,6 →30,2**. Đóng góp biên: **L1 (chỉ lịch sử AQI) → persistence −0,53 [−1,2;+0,1] chưa tách khỏi 0**; **L1→L2 (thêm chất ô nhiễm) −2,0**; **L2→L3 (thêm thời tiết) −1,4 [−1,9;−0,9]** (khoảng 7% MAE của L2). **Kịch bản tham chiếu sử dụng thông tin thời tiết ngày mai chỉ giảm thêm 0,43 [−0,62;−0,26] so với L3**.

**Diễn giải:** Phần lớn lợi thế so với persistence đến từ chất ô nhiễm và thời tiết, không phải xử lý lịch sử AQI khéo hơn; đóng góp riêng của thời tiết khiêm tốn nhưng có bằng chứng tách khỏi 0 trên độ đo MAE.

**Giới hạn:** Nếu chỉ lấy số trên HTML (MAE 19,52 …) mà không đối chiếu notebook thì đó là **lớp trình bày trùng đường trước sửa**; giai đoạn giữ lại cuối (01/03–01/07/2020) có **L3 13,78 vs. 14,80 chênh −1,02 [−2,70;0,48] chưa đủ bằng chứng** — số này cũng thuộc đường trước sửa và không được gọi là ước lượng sạch leakage đã xác nhận.

### D3. Sai số theo thành phố và độ nhạy

**Câu hỏi:** Lợi thế của L3 có nhất quán giữa các thành phố và vững trước các lựa chọn tiền xử lý không?

**Biểu đồ:** `model_03_mae_by_city.png` + bảng độ nhạy (bỏ 10% train ×100 lần; bỏ Gurugram; giữ ô đã tạo giá trị ước lượng; tách hai giai đoạn kiểm thử).

**Số liệu:** Giảm MAE cùng chiều ở **8/8 TP (7%→22%)**, lớn nhất ở nhóm rất nặng (Delhi 20%, Lucknow 22%, Gurugram 19%). **Độ nhạy:** bỏ 10% train → hiệu số L3−L1 dao động −3,52→−3,30 và L3−persistence −4,02→−3,81; **bỏ Gurugram** L3 vẫn hơn persistence **3,36 [2,11;4,63]**; **giữ ô đã tạo giá trị ước lượng** MAE đổi **0,01 (L2) và 0,03 (L3)** trên 1,1% dòng bị ảnh hưởng; **tách giai đoạn kiểm thử** cho thấy lợi thế lớn hơn trong mùa ô nhiễm cao (28,2→22,1 giảm 21%) so với mùa mưa/sau mưa (20,7→18,0 giảm 13%).

**Diễn giải:** Kết luận không phụ thuộc vài dòng cá biệt và không do đếm Delhi–Gurugram hai lần (chuỗi thời tiết tương quan cao đã được kiểm bằng bỏ Gurugram). Rò rỉ nhẹ từ ô đã tạo giá trị ước lượng không làm đẹp kết quả.

**Giới hạn:** So sánh MAE tuyệt đối giữa miền Nam (AQI nền thấp) và miền Bắc là khập khiễng; nên đọC **mức giảm so với baseline của chính TP**.

### D4. Bài toán cảnh báo AQI ≥201 — Precision/Recall

**Câu hỏi:** Với cùng quy tắc chọn ngưỡng, mô hình có báo đúng hơn persistence ở mức recall tương đương không?

**Biểu đồ:** `model_04_precision_recall.png` (đường PR) + bảng cảnh báo (ngưỡng 201 và ngưỡng chọn bằng F2 trên train-OOF) + bảng theo nhóm TP.

**Số liệu:** Trên 389 ngày nặng kiểm thử, **ở cùng ngưỡng 201**: L3 **recall 0,89 vs. 0,86 (+0,033 [0,003;0,068])**, **precision 0,90 vs. 0,85 (+0,047 [0,033;0,065])**, F1 +0,040 [0,027;0,055] (bỏ sót 43 vs. 56; báo nhầm 40 vs. 59). **Khi cả hai được chọn ngưỡng cùng quy tắc F2 (L3 ngưỡng 166, persistence 160)**: **recall 96,9% vs. 96,1% chênh +0,008 [−0,010;+0,029] không tách khỏi 0**, **precision hơn +0,046 [0,024;0,074]** (báo nhầm 113 vs. 143). So với “nghĩa đen” ngưỡng 201, ngưỡng chọn bắt thêm 11 điểm % nhưng báo đúng thấp hơn 8 điểm % — là hai điểm vận hành khác nhau trên cùng đường cong PR, không phải “hơn mọi mặt”.

**Theo nhóm TP (W12):** **Delhi/Gurugram/Lucknow (341 ngày nặng) recall 0,99 precision 0,82** ở ngưỡng chọn; **Jaipur/Amritsar (38 ngày) recall 0,84 (thấp hơn persistence 0,89) precision 0,49**; **Bengaluru/Chennai/Hyderabad (10 ngày) không đủ (<30) để đánh giá cảnh báo**.

**Diễn giải:** Trên tổng thể, L3 hơn persistence ở cả recall/precision khi cùng ngưỡng 201, và hơn về precision khi so công bằng cùng quy tắc chọn ngưỡng; phần riêng của thời tiết **không tách khỏi 0** cho F1 cảnh báo.

**Giới hạn:** Đường PR của L3 nằm trên persistence ở hầu hết 0,6–0,95 nhưng chụm lại ở recall >0,97; chọn ngưỡng là quyết định chính sách (đánh đổi bỏ sót vs. báo thừa), không phải của mô hình. **Không nên nói mô hình dùng được cho cả 8 TP** ở bài toán cảnh báo do mẫu miền Nam quá nhỏ.

### D5. Diễn giải hệ số và kiểm tra lại theo giai đoạn

**Câu hỏi:** Từng yếu tố hôm nay “đi cùng” với AQI ngày mai thế nào khi giữ các biến khác không đổi?

**Biểu đồ:** Bảng hệ số OLS trên log(AQI) ngày mai (5.118 dòng train đủ đặc trưng) + `model_05_humidity_recheck.png` (tỷ lệ ngày nặng theo nhóm ẩm, train vs. kiểm thử).

**Số liệu:** Trên train, **độ ẩm +10 điểm % đi cùng AQI mai −1,2% [−2,0;−0,3], gió +1 m/s −1,9% [−3,0;−0,8], mưa 10 mm vs. 0 mm −9,2% [−11,7;−6,5]** (đều loại trừ 0 với SE bền khối); gió Đông +1 m/s +1,8% [1,3;2,2]; **nhiệt độ, BLH, áp suất không tách khỏi 0** sau khi đã giữ AQI/chất ô nhiễm (BLH +0,1% [−0,5;+0,7] mỗi 100 m). Độ ẩm giữ chiều âm ở **9/10 trường hợp train/kiểm thử** (ngoại lệ Lucknow kiểm thử −0,01), và **tỷ lệ ngày nặng nhóm ẩm thấp > nhóm ẩm cao** ở Delhi/Gurugram/Lucknow cả hai giai đoạn (Delhi +18 điểm % train lẫn kiểm thử) **nhưng KTC chênh lệch chứa 0 ở 5/6 trường hợp (chỉ Delhi train tách khỏi 0)**.

**Diễn giải:** Độ ẩm là biến thời tiết có chiều âm nhất quán nhất; mưa rửa trôi có độ lớn lớn nhất trong các hệ số thời tiết; BLH không ủng hộ trực giác “nén sát mặt đất” sau khi đã giữ các biến khác.

**Giới hạn:** Hệ số là **có điều kiện** theo AQI hôm nay/chất ô nhiễm và chỉ trong khoảng đã quan sát; **chỉ nói về chiều và khoảng, không nói độ lớn tuyệt đối** cho nhiệt độ/áp suất do phụ thuộc cách khử mùa. Độ ẩm cao có thể đại diện cho mưa/sương/mây.

---

## D. Bản thảo 3.4. Trình bày sản phẩm ứng dụng — giao diện, tính năng và kịch bản minh họa

> HTML là **ứng dụng minh họa/phát lại kết quả trên dữ liệu lịch sử** (giai đoạn kiểm thử 01/07/2019–29/02/2020), chưa khẳng định dự báo trực tuyến. Số liệu trong HTML là lớp trình bày; nguồn chuẩn cho hiệu năng là bảng/biểu đồ trong notebook.

### D4.1. Giao diện và tính năng chính

Ứng dụng một tệp `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` gồm:

- **Thanh tiêu đề và chỉ số tổng quan:** tóm tắt MAE theo mức (thông tin từ notebook), không dùng làm nguồn chuẩn; nhấn mạnh mô hình Ridge trên log(AQI) chỉ dùng dữ liệu **đến hết hôm nay (t)** để dự báo **ngày mai (t+1)**.
- **Tab 1 — Xem một ngày & giải phẫu dự báo:** chọn nhanh 4 tình huống minh họa (bắt đúng/bỏ sót/báo nhầm/khóa miền Nam), chọn (TP, ngày), hiển thị hai ngưỡng vận hành (**ngưỡng chuẩn 201** và **ngưỡng ưu tiên không bỏ sót** L3 ≥166 / persistence ≥160 chọn bằng F2 trên train), thang CPCB, số đo chất ô nhiễm hôm nay (màu theo mốc CPCB riêng từng chất) + thời tiết hôm nay, và bảng **dịch chuyển dự báo qua 3 mức**: baseline → L1 (+24 điểm ví dụ Delhi 24/01/2020) → L2 (+5) → L3 (+16) với sai số so với thực tế.
- **Tab 2 — Toàn cảnh giai đoạn kiểm thử:** đường AQI thực tế ngày mai (xám) vs. dự báo L3 (xanh) trên 1.947 ngày, điểm **○ báo nhầm (FP)** / **✕ bỏ sót (FN)**; rê chuột soi từng ngày, bấm để mở Tab 1; kéo thử ngưỡng cảnh báo để cảm nhận đánh đổi Precision/Recall.
- **Tab 3 — Thời tiết giúp được gì:** diễn giải MAE biên (−2,0 khi thêm chất; −1,4 khi thêm thời tiết) và bảng hệ số Ridge với KTC 95% bền khối.
- **Tab 4 — Giới hạn & phạm vi:** nêu không thay thế tư vấn y tế, không dùng cho miền Nam do mẫu cảnh báo quá nhỏ, và ghi chú **phát lại trên dữ liệu lịch sử**.

Thiết kế giao diện dùng **Be Vietnam Pro**, sáng/tối, một màu nhấn, nhãn trực tiếp, không legend thừa; toàn bộ dữ liệu được nhúng **offline** trong HTML (không gọi API).

### D4.2. Kịch bản minh họa (4 tình huống mặc định)

| # | Kịch bản | Ý minh họa | Kết quả mô hình vs. persistence |
|---|---|---|---|
| 1 | **Bắt đúng** Delhi 24/01/2020 (AQI hôm nay 155 → mai thực tế 251) | Hạ ngưỡng tránh bỏ sót | L3 đoán **200 ≥166 báo đúng (TP, sai 51)**, persistence 155 <160 bỏ sót (sai 96); L2 +5 và L3 +16 cho thấy đóng góp chất ô nhiễm + thời tiết |
| 2 | **Điểm mù đột biến** Delhi 10/07/2019 | Tăng vọt đột ngột không có tiền triệu | Cả hai bỏ sót — minh họa đuôi phải nặng của QQ-plot |
| 3 | **Báo nhầm** Jaipur 03/11/2019 | AQI hạ nhiệt sau đỉnh | L3 báo thừa khi ngưỡng hạ — minh họa đánh đổi precision |
| 4 | **Khóa miền Nam** Bengaluru 20/12/2019 (AQI hôm nay 91 → mai 94) | Mẫu cảnh báo quá nhỏ | Không dùng % recall/precision; chỉ xem sai số điểm |

Mọi tình huống đều **phát lại** trên dữ liệu lịch sử; bấm điểm trên Tab 2 để liên kết sang chi tiết Tab 1.

### D4.3. Giới hạn và hướng phát triển của sản phẩm

**Giới hạn:** Một tệp tĩnh, không dự báo trực tuyến, không có API thời tiết trực tiếp; ngưỡng cảnh báo chọn trên train có thể hơi “dễ” do tỷ lệ ngày nặng giảm dần 24,9%→20,0%→1,8%; không đánh giá cảnh báo cho miền Nam; phụ thuộc vào chất lượng dữ liệu CPCB và không có thông tin nguồn phát thải.

**Hướng phát triển (chưa phải chức năng đã nghiệm thu):** Đề xuất trên bản sao thử nghiệm về đọc cache offline và dựng đặc trưng trực tiếp từ dữ liệu gốc được ghi nhận ở lớp biên tập, không đưa vào lời văn bài nộp; việc xác minh toàn bộ và tích hợp vào bản chính chưa hoàn tất nên báo cáo không mô tả như chức năng đã triển khai.

---

## Phụ lục — Ghi chú biên tập (chuyển khỏi 3.1 để rút gọn)

- Lịch sử sửa lỗi `interpolate(limit=14)` cũ (1.316 ô ở 6 TP), ví dụ Bengaluru NOx =0 suốt 207 ngày trước đó còn 6,48, và kiểm nhạy đổi ngưỡng flatline 2/5/7 ngày.
- Danh sách 9 cặp thiếu ≥20%, chi tiết AQI thiếu 0,5%→13,6%, và 15 rủi ro đầy đủ từ `cleaning_log` §3.

---

**Ghi chú cho biên tập tổng thể:** Khi ghép Phần I–III, giữ thống nhất **“giai đoạn kiểm thử (01/07/2019–29/02/2020)”**, **“kịch bản tham chiếu sử dụng thông tin thời tiết ngày mai”**, và **“tạo giá trị ước lượng tại khoảng thiếu”**; mọi ghi chú kiểm toán/PR/F01 chỉ giữ ở lớp biên tập, không đưa vào lời văn bài nộp.
