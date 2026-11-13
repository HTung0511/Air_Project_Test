# BÁO CÁO MÔN HỌC KHOA HỌC DỮ LIỆU
## Phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ

**Học phần:** Khoa học dữ liệu — Mã học phần: INFO3020 [Cần đối chiếu mã chính thức trên đề cương/sổ tay sinh viên]  
**Lớp:** [Cần bổ sung]  
**Giảng viên hướng dẫn:** [Cần bổ sung]  
**Nhóm thực hiện:** [Cần bổ sung — số thành viên và danh sách theo biên bản nộp chính thức; không mặc định số lượng]  
**Thời gian thực hiện:** [Cần bổ sung]  
**Repository:** [Cần bổ sung]

---

## Mục lục

1. [Mở đầu](#mở-đầu)
2. [Phần I. Giới thiệu chung](#phần-i-giới-thiệu-chung)
3. [Phần II. Phân tích bài toán thực tế](#phần-ii-phân-tích-bài-toán-thực-tế)
4. [Phần III. Kết quả thực hiện](#phần-iii-kết-quả-thực-hiện)
5. [Kết luận](#kết-luận)
6. [Tài liệu tham khảo](#tài-liệu-tham-khảo)
7. [Phụ lục](#phụ-lục)

---

## Mở đầu

Báo cáo trình bày kết quả đồ án môn Khoa học dữ liệu với đề tài **Phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ**. Dữ liệu chính là chuỗi quan trắc theo ngày từ Central Pollution Control Board (CPCB) Ấn Độ qua Kaggle (`city_day.csv`, 01/01/2015–01/07/2020), kết hợp nguồn thứ hai là dữ liệu thời tiết tái phân tích ERA5 qua Open-Meteo Historical Weather API (25/12/2014–01/07/2020, theo giờ, gộp theo ngày). Trên 8 thành phố, báo cáo thực hiện trọn vòng đời khoa học dữ liệu: thu thập và tiền xử lý, phân tích khám phá (EDA) và trực quan hóa — gồm Data Storytelling — mô hình hóa và đánh giá, cùng thảo luận về đạo đức dữ liệu và sử dụng kết quả có trách nhiệm.

Trọng tâm là **phân tích mô tả theo thời gian**: ô nhiễm nặng ở đâu, khi nào và do chất nào, với thời tiết được xem xét như nhóm biến giải thích có liên quan. Bài toán **dự báo chỉ số chất lượng không khí (AQI) ngày kế tiếp** được đặt ở vị trí **phần mở rộng**, phục vụ minh họa khả năng vận dụng mô hình vào kịch bản cảnh báo, không lấn át trọng tâm phân tích.

Báo cáo được tổ chức theo cấu trúc đã thống nhất, đối chiếu rubric học phần. **Phần II** trình bày phương pháp; **Phần III** trình bày kết quả; hai phần không lặp số liệu. Sản phẩm đi kèm là tệp HTML `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` — được gọi thống nhất là **ứng dụng minh họa/phát lại kết quả trên dữ liệu lịch sử** (giai đoạn kiểm thử 01/07/2019–29/02/2020), chưa khẳng định dự báo trực tuyến.

---

## Phần I. Giới thiệu chung

### 1.1. Lý do chọn đề tài

Ô nhiễm không khí là vấn đề môi trường — sức khỏe cộng đồng có tính thời sự cao, đặc biệt tại các đô thị có mật độ dân cư lớn và hoạt động giao thông, công nghiệp, đốt phụ phẩm nông nghiệp theo mùa. Ấn Độ có hệ thống quan trắc quốc gia do CPCB vận hành, với dữ liệu theo ngày được chia sẻ qua Kaggle (bộ *Air Quality Data in India*, 2015–2020). Sự sẵn có của chuỗi thời gian dài, đa thành phố, đa chất ô nhiễm, cùng khả năng bổ sung biến thời tiết từ nguồn mở ERA5/Open-Meteo, tạo điều kiện thuận lợi để thực hành trọn vòng đời khoa học dữ liệu: từ làm sạch dữ liệu khuyết và nhiễu cảm biến, đến EDA theo không gian–thời gian–thành phần chất, phân tích tương quan có kiểm soát mùa vụ, và thử nghiệm mô hình dự báo ngắn hạn.

Về mặt học thuật, đề tài cho phép vận dụng đồng thời các kỹ thuật cốt lõi của học phần: xử lý dữ liệu khuyết theo khối thời gian, phát hiện ngoại lai theo tháng, trực quan hóa chuỗi thời gian và phân bố, kỹ thuật đặc trưng trễ (lag) và biến mùa vụ, mô hình hồi quy có chuẩn hóa (Ridge) so sánh với các baseline quán tính, cùng đánh giá bằng bootstrap theo khối thời gian.

Lựa chọn tám thành phố — **Delhi, Gurugram, Lucknow, Jaipur, Bengaluru, Amritsar, Chennai, Hyderabad** — được thực hiện theo tiêu chí của nhóm: **khoảng thời gian quan sát tương đối đồng nhất và độ phủ dữ liệu AQI tương đối đầy đủ hơn các phương án khác được cân nhắc, phục vụ khả năng so sánh trong bộ dữ liệu**. Đây là lựa chọn phục vụ so sánh nội bộ, không phải bằng chứng rằng tám thành phố đại diện cho toàn bộ Ấn Độ hay là tám thành phố ô nhiễm nhất.

### 1.2. Mục tiêu nghiên cứu và câu hỏi phân tích

**Mục tiêu chung** là mô tả, so sánh và diễn giải có kiểm chứng thực trạng ô nhiễm không khí theo thời gian tại tám thành phố, trên cơ sở dữ liệu CPCB đã được làm sạch thống nhất, có bổ sung biến thời tiết ERA5 để phân tích liên quan và thử nghiệm mở rộng dự báo AQI ngày kế tiếp ở mức minh họa.

**Mục tiêu cụ thể:**

1. **Chuẩn hóa dữ liệu phục vụ phân tích hồi cứu:** xây dựng pipeline làm sạch thống nhất cho 8 thành phố (xử lý chuỗi số 0 treo ≥3 ngày, tạo giá trị ước lượng cho khoảng thiếu ≤14 ngày, không tạo giá trị ước lượng cho AQI, đánh dấu ngoại lai IQR theo tháng và điểm nghi lỗi cảm biến), giữ nguyên số dòng (14.056) và lưu vết bằng các cờ `_was_missing`, `_is_outlier`.
2. **Trả lời ba câu hỏi mô tả cốt lõi bằng EDA có kiểm tra độ nhạy:** (a) Ô nhiễm nặng tập trung ở đâu? (b) Khi nào trong năm/chu kỳ quan sát? (c) Do chất nào đóng góp chính vào AQI?
3. **Phân tích mối liên hệ thời tiết–AQI có kiểm soát mùa vụ:** so sánh tương quan trước và sau điều chỉnh mùa vụ (anomaly theo trung vị City×Month), kiểm định theo nhóm giả thuyết đã nêu trước với hiệu chỉnh đa kiểm định (Bonferroni/FDR), diễn giải theo từng thành phố và không suy diễn nhân quả.
4. **Thử nghiệm mở rộng dự báo AQI ngày mai ở mức minh họa:** bài toán hồi quy (MAE, R²) và bài toán cảnh báo nhị phân (AQI ≥201, Precision/Recall), huấn luyện Ridge trên log(AQI) với đặc trưng lịch sử AQI, nồng độ chất hôm nay và thời tiết đến hết hôm nay; so sánh với 3 baseline, chia tập theo thời gian, chẩn đoán phần dư và bootstrap theo khối 14 ngày.

**Câu hỏi phân tích:**

- **CQ1 (Không gian):** Trong khoảng chung 14/06/2017–01/07/2020, mức độ và tần suất ngày ô nhiễm nặng (AQI ≥201, ngưỡng Poor theo thang CPCB) phân bố thế nào giữa 8 thành phố? Thứ hạng có vững khi thay đổi cách tổng hợp hay khi loại giai đoạn giữ lại cuối?
- **CQ2 (Thời gian):** Biến động theo tháng/mùa và theo năm có hình thái gì? So sánh năm cần lưu ý gì khi chỉ dùng tháng 1–6 và loại nửa cuối 2020?
- **CQ3 (Thành phần):** Chất ô nhiễm nào có tương quan mạnh nhất với AQI, và mối quan hệ PM2.5–AQI (Spearman ≈0,91 trong EDA) cần được diễn giải thế nào khi AQI được tính theo nguyên tắc max chỉ số con?
- **CQ4 (Thời tiết):** Sau khi điều chỉnh mùa vụ, các biến gió, mưa, độ ẩm, áp suất, chiều cao lớp biên (BLH) còn đi cùng với AQI ngày hôm sau ở mức nào?
- **CQ5 (Dự báo — mở rộng):** Với đặc trưng chỉ đến hết hôm nay, mô hình Ridge cải thiện MAE và Precision/Recall cho cảnh báo ≥201 ra sao so với baseline? Kịch bản sử dụng thông tin thời tiết ngày mai chỉ được gọi là **kịch bản tham chiếu sử dụng thông tin thời tiết ngày mai**.

Về **dạng bài toán**, báo cáo thực hiện: (i) phân tích mô tả và trực quan hóa; (ii) phân tích tương quan có kiểm định; (iii) hồi quy dự báo AQI và (iv) phân loại nhị phân cho cảnh báo AQI ≥201.

### 1.3. Phạm vi thực hiện

**Không gian và thời gian:** 8 thành phố nêu trên; mỗi thành phố là trung bình các trạm trong địa giới hành chính theo dữ liệu CPCB. Nguồn gốc 01/01/2015–01/07/2020, nhưng độ dài chuỗi khác nhau (Delhi, Bengaluru, Chennai, Lucknow từ 01/2015; Gurugram từ 27/11/2015; Amritsar từ 27/02/2017; Jaipur từ 14/06/2017). Để so sánh giữa các thành phố, báo cáo sử dụng **khoảng chung 14/06/2017–01/07/2020**; khi so theo năm chỉ dùng tháng 1–6. Dữ liệu kết thúc 01/07/2020 nên có chứa giai đoạn giữ lại cuối (tháng 3–7/2020) với tỷ lệ cặp có AQI ≥201 rất thấp.

**Dữ liệu và biến:** Nguồn chính `city_day.csv` (Kaggle/rohanrao/air-quality-data-in-india, nguồn gốc CPCB), 29.531 dòng, 26 thành phố; sau khi chọn 8 thành phố còn **14.056 dòng**. 16 cột gốc gồm 11 chất (PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene; Xylene đã bỏ), AQI và AQI_Bucket. Nguồn thứ hai: thời tiết ERA5 qua Open-Meteo, 8 điểm tọa độ, theo giờ, gộp thành ngày với 14 cột: `temp_mean/min/max`, `humidity_mean`, `pressure_mean`, `wind_speed_mean/max`, `wind_u/v`, `wind_dir_8`, `precip_sum`, `rain_day`, `blh_mean/min`. Đây là **dữ liệu mô hình trên lưới 0,25° (~25 km), không phải số đo tại trạm**; Delhi và Gurugram ở hai ô lưới sát nhau nên chuỗi thời tiết tương quan cao (r≈0,95 với mưa →0,999 với nhiệt độ). Thời tiết không có giá trị thiếu.

**Phương pháp (tóm tắt; chi tiết ở Phần II–III):** Làm sạch thống nhất cho 8 thành phố với cờ truy vết (chuỗi 0 treo, khoảng thiếu ngắn/dài, ngoại lai theo tháng, điểm nghi lỗi); EDA theo mạch Ở đâu/Khi nào/Những chất nào nổi bật với kiểm tra độ nhạy; phân tích thời tiết–AQI trước và sau điều chỉnh mùa vụ; mô hình Ridge trên log(AQI) so với baseline, chia theo thời gian với kiểm định bằng bootstrap theo khối. Kết quả làm sạch chi tiết xem 3.1; lịch sử sửa mã chỉ giữ trong ghi chú nội bộ.

**Ngoài phạm vi:** Không suy diễn nhân quả thời tiết “gây” ô nhiễm; không khẳng định dự báo vận hành thời gian thực; không thay thế tư vấn y tế; không tối ưu ngưỡng mới trong phạm vi báo cáo.

### 1.4. Ý nghĩa và ứng dụng thực tế của sản phẩm

**Ý nghĩa khoa học:** Cung cấp nghiên cứu trường hợp có thể tái tạo về phân tích ô nhiễm theo thời gian trên dữ liệu mở, minh họa xử lý thiếu theo khối, chuỗi 0 treo, ngoại lai theo mùa và khác biệt độ dài chuỗi.

**Ý nghĩa xã hội và giáo dục:** Kết quả EDA giúp hình dung bức tranh so sánh giữa các thành phố và tính mùa vụ, nâng cao nhận thức về giai đoạn nguy cơ cao; đáp ứng rubric về complete lifecycle và Data Storytelling.

**Ứng dụng minh họa — tệp HTML:** Là **ứng dụng minh họa/phát lại kết quả trên dữ liệu lịch sử** (giai đoạn kiểm thử 01/07/2019–29/02/2020), cho phép chọn (thành phố, ngày) xem ngữ cảnh hôm nay→dự báo mai qua L1→L3, quan sát toàn cảnh giai đoạn kiểm thử với điểm báo đúng/báo nhầm/bỏ sót, thử đổi ngưỡng cảnh báo để cảm nhận đánh đổi Precision–Recall, và đọc diễn giải hệ số cùng khoảng tin cậy: hệ số OLS dùng sai số chuẩn bền theo cụm khối 14 ngày, các chênh lệch MAE/Precision/Recall dùng bootstrap theo khối 14 ngày. Ứng dụng nêu rõ là phát lại trên dữ liệu lịch sử, chưa khẳng định dự báo trực tuyến.

### 1.5. Quy trình thực hiện và phân công nhiệm vụ

Quy trình gồm 6 notebook chạy tuần tự:

1. **Thu thập:** tải `city_day.csv` và thời tiết theo giờ qua Open-Meteo; lưu bản gốc tại `data/raw/` và `data/raw/weather/*.gz`.
2. **Làm sạch và biến đổi:** `01_cleaning` + `02_cleaning_evidence` thực hiện pipeline thống nhất, xuất `air_quality_8cities.csv` (14.056×40) và các báo cáo `cleaning_summary_8cities.csv`, `suspect_points_8cities.csv`.
3. **Hợp nhất thời tiết:** `04_weather_merge` chuẩn hóa múi Asia/Kolkata, gộp 24 giờ thành ngày, tính `wind_u/v`, `precip_sum`, `rain_day`, `blh_mean`, ghép trái thành `air_quality_8cities_weather.csv` (14.056×54).
4. **EDA và trực quan hóa:** `03_eda` thực hiện Ở đâu/Khi nào/Chất nào, kèm kiểm tra độ nhạy và ghi chú confounder.
5. **Mô hình hóa và đánh giá:** `05_weather_correlation` (tương quan trước vs. sau điều chỉnh) và `06_predict_aqi` (Ridge L1→L3, 3 baseline, TimeSeriesSplit, bootstrap khối).
6. **Trình bày sản phẩm và báo cáo:** tổng hợp biểu đồ `reports/figures/` (15 hình: 6 EDA + 4 corr + 5 model), hoàn thiện báo cáo và minh họa HTML.

Công cụ: Python (pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, statsmodels), Jupyter Notebook, Git.

**Phân công:** Nhóm 4 thành viên; bảng chi tiết để trống để đối chiếu biên bản chính thức:

| Thành viên | Phụ trách chính | Sản phẩm |
|---|---|---|
| [Cần bổ sung — Thành viên 1] | Thu thập & làm sạch | `01_cleaning`, `pipeline.py`, `utils.py` |
| [Cần bổ sung — Thành viên 2] | EDA & Data Storytelling | `03_eda`, `eda_*.png` |
| [Cần bổ sung — Thành viên 3] | Thời tiết & tương quan | `04_weather_merge`, `05_weather_correlation` |
| [Cần bổ sung — Thành viên 4] | Mô hình & HTML | `06_predict_aqi`, `model_utils.py`, `*.html` |
| Tất cả | Viết báo cáo & thuyết trình | Báo cáo, slide |

---

## Phần II. Phân tích bài toán thực tế

### 2.1. Thu thập dữ liệu

**Nguồn chính:** Bộ *Air Quality Data in India (2015–2020) — city_day.csv* trên Kaggle (nguồn gốc CPCB), dạng CSV, mỗi dòng một cặp (City, Date). Trường gồm City, Date, 11 chất ô nhiễm (Xylene đã bỏ trong phân tích), AQI và AQI_Bucket (Good/Satisfactory/Moderate/Poor/Very Poor/Severe). Tệp gốc 29.531 dòng, 26 thành phố, từ 01/01/2015 đến 01/07/2020; sau khi chọn 8 thành phố còn **14.056 dòng** (mỗi thành phố một chuỗi liên tục, không trùng khóa, không đứt ngày, không giá trị âm). Tệp gốc giữ nguyên tại `data/raw/city_day.csv`.

**Nguồn thứ hai:** Thời tiết theo giờ qua Open-Meteo Historical Weather API (ERA5, CC BY 4.0, ghi công *Weather data by Open-Meteo.com*), mỗi thành phố một điểm tọa độ trung tâm, ô lưới 0,25° gần nhất, 25/12/2014–01/07/2020 múi Asia/Kolkata. Bản tải về giữ nguyên tại `data/raw/weather/*.gz` (48.384 dòng giờ mỗi thành phố). **Đây là dữ liệu mô hình tái phân tích, không phải đo tại trạm**; Delhi–Gurugram tương quan thời tiết rất cao.

**Tích hợp:** Từ giờ gộp thành ngày (trung bình/min/max/tổng mưa) với 14 cột thời tiết, lưu `weather_daily_8cities.csv` (16.128 dòng) và `air_quality_8cities_weather.csv` (14.056×54), ghép trái theo (City, Date), 0 dòng thiếu thời tiết, các cột cũ giữ nguyên.

### 2.2. Làm sạch và biến đổi dữ liệu

**Nguyên tắc:** Một pipeline thống nhất cho 8 TP (`01_cleaning`; code `pipeline.py`, `utils.py`, `gap_utils.py`; bằng chứng `02_cleaning_evidence`), không xóa dòng, mọi can thiệp có cờ truy vết, không scale/encode ở giai đoạn này, không tạo giá trị ước lượng cho AQI.

**Chuỗi 0 treo:** Chuỗi giá trị đúng 0 liên tiếp ≥3 ngày → NaN (2.169 ô).

**Loại cột và ngưỡng dùng làm biến:** Bỏ Xylene toàn bộ; PM10 Lucknow để NaN; các cột thiếu ≥60% không dùng làm biến trong phép so sánh/mô hình cụ thể (chi tiết số ô xem 3.1).

**Khoảng thiếu và ngoại lai:** Chỉ khoảng thiếu nằm giữa hai giá trị thật và ≤14 ngày được tạo giá trị ước lượng tuyến tính theo thời gian; khoảng dài hơn giữ NaN. Ngưỡng 14 ngày là quy ước thực hành cho phân tích hồi cứu; ngoại lai IQR theo tháng chỉ gắn cờ; điểm nghi lỗi được gắn nhãn và lưu giá trị gốc để khôi phục. Kết quả định lượng xem 3.1.

**Thời tiết:** Chuẩn hóa múi giờ, gộp 24 giờ → ngày, tính `wind_u/v` từ tốc độ+hướng, thêm `rain_day`, `blh_mean`, ghép trái; biến đổi `log1p(precip_sum)` để dành cho mô hình sau chia train/test.

### 2.3. EDA và trực quan hóa dữ liệu — gồm Data Storytelling

**Mục tiêu:** Trả lời Ở đâu/Khi nào/Những chất nào nổi bật, với khoảng chung 14/06/2017–01/07/2020 và tháng 1–6 khi so năm; ngưỡng AQI ≥201 định nghĩa ngày nặng. Thống kê mô tả dùng median/IQR/tỷ lệ ≥201 và Spearman; mỗi phát hiện gắn một biểu đồ với tiêu đề kết luận có số, trục rõ nhãn, chân hình ghi nguồn và cỡ mẫu.

**Bộ trực quan:** 6 hình `eda_00`–`eda_05` theo mạch Ở đâu → Khi nào → Do chất nào, kèm ghi chú confounder (vị trí trạm, Diwali, đốt rơm Punjab, cách tính AQI). Kiểm tra độ nhạy đổi khoảng chung, loại giai đoạn giữ lại cuối và thử xếp hạng nhóm thay vì 1–8.

### 2.4. Mô hình hóa và đánh giá

**Khung bài toán:** Một dòng = (thành phố, ngày hôm nay t); mục tiêu = AQI ngày t+1 theo thiết kế đầu vào dự kiến (chỉ dùng thông tin đến hết t). Chia theo thời gian: train đến 30/06/2019; giai đoạn kiểm thử 01/07/2019–29/02/2020; giai đoạn giữ lại cuối tháng 3–7/2020 tách riêng. **Ridge trên log(AQI) dùng cho dự báo; OLS trên log(AQI) phục vụ diễn giải hệ số**, so sánh thêm HGB làm tham chiếu.

**Đặc trưng:** L1 lịch sử AQI + mùa (aqi_0/1/2/wk + doy_sin/cos); L2 + chất ô nhiễm (log1p); L3 + thời tiết đến hết hôm nay (pressure_dev, d_pressure, wind_u/v, precip_log…); L4 kịch bản tham chiếu dùng thời tiết ngày mai chỉ để tham chiếu.

**Xử lý thiếu và chuẩn hóa:** Ô đã tạo giá trị ước lượng ở bước làm sạch được đặt lại NaN rồi điền lùi 2 ngày trước khi vào Pipeline; mọi imputer/scaler/encoder chỉ fit trên train trong Pipeline/ColumnTransformer.

**Baseline và độ đo:** 3 baseline (trung bình theo TP, trung vị cùng tháng, persistence “ngày mai = hôm nay”); MAE (chính) và R² cho hồi quy (dự đoán trên log rồi biến đổi ngược về điểm AQI); Precision/Recall (F2 chọn ngưỡng trên train-OOF) cho cảnh báo ≥201; hệ số OLS với sai số chuẩn bền theo cụm khối 14 ngày phục vụ diễn giải.

**Chẩn đoán:** Phần dư vs. dự đoán, QQ-plot, Breusch-Pagan; bootstrap khối 14 ngày cho KTC hiệu ứng và ΔMAE; hiệu chỉnh Bonferroni (family 15) và BH-FDR (48 cặp).

### 2.5. Đạo đức dữ liệu và sử dụng kết quả có trách nhiệm

Dữ liệu CPCB là tổng hợp công khai theo thành phố/ngày, không có PII; thời tiết là mô hình lưới. Nhóm công khai nguồn/giấy phép ở chân mỗi hình. Thiên kiến được ghi nhận: chọn mẫu 8/26, chuỗi dài ngắn khác nhau và giai đoạn giữ lại cuối, đo lường (thiếu Xylene/PM10/NH3, thời tiết lưới, AQI = max chỉ số con). Nhóm không tạo giá trị ước lượng cho khoảng thiếu >14 ngày; với bài toán dự báo, thiết kế đầu vào dự kiến chỉ dùng thông tin đến hết hôm nay và mọi scaler/imputer chỉ fit trên train, tuy nhiên quy trình làm sạch hồi cứu có bước tạo giá trị ước lượng đã dùng quan sát sau — giới hạn này được nêu rõ ở 3.1 và 3.5. Nhóm không coi tương quan là nhân quả; mỗi biểu đồ/kết luận kèm hạn chế; AQI ≥201 chỉ dùng cho phân tích, không thay thế tư vấn y tế.

---

## Phần III. Kết quả thực hiện

### 3.1. Kết quả thu thập và tiền xử lý

**Quy mô và cấu trúc:** Trên 8 thành phố, tập làm việc giữ nguyên **14.056 dòng** và 0 giá trị âm; số cột 16→40 (11 chất + AQI + AQI_Bucket + 12 cờ `_was_missing` + 11 cờ `_is_outlier` + `pm25_gt_pm10_flag` + `suspect_sensor_error`). Ô thiếu 11 chất + AQI từ **16.953 (10,05%) → 15.832 (9,39%)** theo 16.953 + 2.169 − 3.329 + 39 = 15.832 (quy tắc nghi lỗi xử lý 41 ô nhưng tăng thêm thực tế 39 ô do một số ô đã thiếu trước). Chỉ một số ô tại 24 ngày bị xử lý.

**Bảng tổng hợp:**

| Quy tắc | Ngưỡng | Số ô/dòng | Lưu vết |
|---|---|---|---|
| Chuỗi 0 treo | ≥3 ngày =0 | 2.169 ô | `_was_missing` |
| Loại cột | Xylene toàn bộ; PM10 Lucknow | 4.234 + 2.009 rỗng | `status=dropped` |
| Khoảng thiếu ngắn | ≤14 ngày, tuyến tính | 3.329 ô | `_was_missing` |
| Giữ NaN khối dài | >14 ngày; 9 cặp ≥20% | 7.733 ô (≥60% không dùng làm biến) | giữ NaN |
| AQI thiếu | không ước lượng | 836 dòng | giữ NaN |
| Ngoại lai | IQR×1,5 theo tháng | 6.656 ô | `_is_outlier` |
| Nghi lỗi | top-5 mỗi TP + PM2.5>1,5×PM10 | 41 ô trên 24 ngày (93 bản ghi, 52 giữ lại) | `suspect_sensor_error` |
| PM2.5>1,2×PM10 | nhất quán | 139 ngày | `pm25_gt_pm10_flag` |

**Thời tiết:** 387.072 dòng giờ → 16.128 ngày-thành phố → ghép trái giữ nguyên 14.056 dòng, 0 thiếu thời tiết; chuỗi Delhi–Gurugram tương quan cao nên thận trọng khi coi là bằng chứng không gian độc lập.

**Hạn chế chính:** Ô ước lượng đã dùng giá trị ngày sau (hồi cứu) nên không mặc nhiên phù hợp dự báo thời gian thực; chuỗi dài ngắn khác nhau nên chỉ so trong khoảng chung; thời tiết là mô hình lưới.

**Bảng 1.** Tổng quan trước–sau làm sạch (ô thiếu 11 chất + AQI: 16.953 → 15.832; chi tiết `cleaning_log_8cities.md` §1 và `cleaning_summary_8cities.csv`).  
**Hình 1.** Cỡ mẫu theo thành phố trên khoảng chung (n có AQI 1.029→1.111/1.114) — `reports/figures/eda_00_sample_size.png`. *Nguồn: CPCB qua Kaggle; n và khoảng ngày ghi ở chân hình.*

### 3.2. Kết quả EDA và các phát hiện chính

#### 3.2.1. Ở đâu ô nhiễm nặng tập trung?

**Số liệu:** Trên 1.114 cặp thành phố–ngày chung, n có AQI 1.029 (Amritsar)→1.111 (Lucknow); median AQI Delhi 205/Lucknow 188/Gurugram 188/Jaipur 122/Amritsar 104/Hyderabad 89/Chennai 87/Bengaluru 81. Tỷ lệ cặp có AQI ≥201: Delhi **51,0%**, Lucknow **46,4%**, Gurugram **46,3%** gấp 4,1–4,6× Amritsar 11,4%/Jaipur 11,1%; ba TP phía Nam được khảo sát có tỷ lệ thấp trong khoảng quan sát (Chennai 3,1%, Bengaluru 0,2%, Hyderabad 0,1%).

**Diễn giải:** Ba TP đồng bằng Bắc Ấn tạo nhóm rất nặng tách biệt; nhóm phía Nam thấp hơn rõ rệt.

**Giới hạn:** Amritsar thiếu 7,6%; độ nhạy xóa 10%×200 cho thấy 3 cặp gần nhau hay đổi chỗ → chia nhóm thay vì xếp hạng 1–8.

**Hình 2.** Tỷ lệ cặp thành phố–ngày có AQI ≥201 theo thành phố (`eda_01_poor_share_city.png`).  
**Hình 3.** Phân bố AQI theo thành phố (`eda_05_aqi_distribution.png`). *Nguồn: CPCB qua Kaggle; khoảng chung 14/06/2017–01/07/2020.*

#### 3.2.2. Khi nào ô nhiễm đạt đỉnh?

**Số liệu:** 5 TP Bắc/Tây Bắc chung mẫu hình đỉnh T11–12 đáy T7–9 (Amritsar T11 median 209 gấp 3,1×T8 66; 89/117 cặp có AQI ≥201 rơi T10–12). Bengaluru có biên độ trung vị theo tháng nhỏ hơn ví dụ TP phía Bắc được so sánh (63–102, 1,6×, 2 cặp ≥201). Năm chỉ dùng T1–6, tách 1/1–24/3 vs 25/3–30/6 để chẩn đoán 2020.

**Giới hạn:** Thời tiết/mùa vụ là confounder; chỉ nêu “có liên quan” với 2020.

**Hình 4.** Heatmap City×Month — trung vị AQI theo tháng (`eda_02_heatmap_city_month.png`).  
**Hình 5.** Xu hướng City×Year trên tháng 1–6 (`eda_03_trend_city_year.png`). *Nguồn: CPCB qua Kaggle.*

#### 3.2.3. Chất nào tăng mạnh nhất?

**Số liệu:** Gộp 8 TP, Spearman PM2.5–AQI **0,91** (NO2 0,52/CO 0,48/SO2 0,38/O3 0,34). Trên 5 TP đủ điều kiện (≥100 cặp có AQI ≥201), **trung vị các tỷ số PM2.5 giữa nhóm cặp có AQI ≥201 và nhóm còn lại là 2,82**. Khi gộp 8 TP, trung vị PM2.5 hai nhóm là **137,1 và 42,0 µg/m³, tỷ số ≈3,26** — hai cách tổng hợp khác nhau. NO2 1,7×, CO 1,6×, SO2/O3 ~1,1×; 73,2% cặp có AQI ≥201 rơi T10–2.

**Giới hạn:** PM10 Chennai không dùng trong phép so sánh cụ thể (thiếu 84,5%); AQI = max chỉ số con nên tương quan cao một phần là hệ quả công thức.

**Hình 6.** Quan hệ PM2.5–AQI (`eda_04_pm25_aqi.png`) và bảng Spearman C0/C1. *Nguồn: CPCB qua Kaggle.*

#### 3.2.4. Mối liên hệ thời tiết–AQI trước và sau điều chỉnh mùa vụ

**Số liệu:** Thao tác điều chỉnh: anomaly = giá trị − trung vị City×Month, rồi tính Spearman trên anomaly. Ví dụ Delhi nhiệt độ −0,52→+0,23, áp suất +0,63→−0,16, BLH −0,38→+0,08 (KTC chứa 0); sự thay đổi về dấu/độ lớn sau điều chỉnh cho thấy mùa vụ có thể ảnh hưởng đáng kể. Độ ẩm giữ chiều âm 8/8 TP (−0,14→−0,48). Nhóm 15 so sánh nêu trước (3 giả thuyết ×5 TP): 3 ủng hộ, 1 ngược chiều, 11 chưa đủ bằng chứng (Bonferroni). Trên 48 cặp quan hệ, trong 48 cặp được xét, 32 đạt sau BH-FDR, trong khi 33 có KTC danh nghĩa không chứa 0 — hai cách đánh giá không hoàn toàn tương đương.

**Giới hạn:** Khử mùa bằng City×Month còn sót chu kỳ trong tháng; do phụ thuộc theo thời gian, kết quả cần diễn giải thận trọng và dùng bootstrap khối 14 ngày; chỉ nói “có liên quan”.

**Hình 7.** Tương quan thời tiết–AQI trước và sau điều chỉnh mùa vụ (`corr_01_raw_vs_adjusted.png`).  
**Hình 8.** Kiểm định nhóm 15 so sánh nêu trước (Bonferroni) (`corr_02_hypothesis_tests.png`).  
**Hình 9–10.** Độ ẩm deciles và tỷ lệ cặp có AQI ≥201 theo nhóm ẩm (`corr_03_humidity_deciles.png`, `corr_04_poor_share_by_humidity.png`). *Nguồn: CPCB qua Kaggle + Open-Meteo ERA5.*

### 3.3. Kết quả mô hình hóa và đánh giá

> Phần mở rộng, rút gọn; chi tiết độ nhạy xem Phụ lục. Nguồn chuẩn là bảng kết quả trong `notebooks/06_predict_aqi.ipynb` và hình `model_*.png`; số trên HTML chỉ là lớp trình bày.

**Thiết kế đánh giá:** Giai đoạn kiểm thử 01/07/2019–29/02/2020 có **1.947 cặp thành phố–ngày, trong đó 389 cặp có AQI ≥201**; giai đoạn giữ lại cuối (tháng 3–7/2020) chỉ 18 cặp có AQI ≥201 và được tách riêng. Tỷ lệ cặp có AQI ≥201: 24,9% (train) →20,0% (kiểm thử) →1,8% (giữ lại cuối). Baseline persistence (ngày mai = hôm nay) MAE **23,47** (R² 0,86); hai baseline trung bình/khí hậu có MAE cao hơn đáng kể trong tập kiểm thử (60,5 và 55,8).

**Chẩn đoán thang log:** Biến đổi log cải thiện hình dạng phần dư quan sát được, nhưng kiểm định Breusch-Pagan vẫn cho thấy phương sai thay đổi (LM 409→311); khoảng tin cậy hệ số dùng sai số chuẩn bền theo cụm khối 14 ngày, còn KTC chênh lệch MAE/Precision/Recall dùng bootstrap khối.

**Hiệu năng kiểm thử:** Trên 1.947 cặp của giai đoạn kiểm thử, Ridge L3 (đủ 3 mức) MAE **19,52 so với 23,47, giảm 3,95 điểm (−16,8%) với KTC bootstrap khối không chứa 0; R² 0,86→0,91**. Đóng góp biên: ΔMAE = MAE(L1)−MAE(persistence) = **−0,53 [−1,2;+0,1] chưa tách khỏi 0**; MAE(L2)−MAE(L1)=**−2,0**; MAE(L3)−MAE(L2)=**−1,4 [−1,9;−0,9]**; kịch bản tham chiếu dùng thời tiết ngày mai có **ΔMAE(L4−L3) ≈ −0,43, KTC [−0,62;−0,26]**.

Kết quả này thuộc thực nghiệm trên dữ liệu lịch sử và cần được diễn giải cùng hạn chế của quy trình tiền xử lý; mức cải thiện chưa được xác nhận ổn định ở giai đoạn giữ lại cuối (tháng 3–7/2020 có L3 13,78 vs. 14,80 chênh −1,02 [−2,70;0,48] chưa đủ bằng chứng).

**Theo thành phố:** Giảm MAE cùng chiều ở 8/8 TP (7%→22%), lớn nhất nhóm rất nặng (Delhi 20%, Lucknow 22%, Gurugram 19%). Kết quả đã được kiểm tra độ nhạy; chi tiết xem Phụ lục. Các phép thử không loại trừ mọi nguồn phụ thuộc tương lai.

**Cảnh báo AQI ≥201:** Trên 389 cặp có AQI ≥201, ở cùng ngưỡng 201 L3 recall 0,89 vs. 0,86 (+0,033 [0,003;0,068]), precision 0,90 vs. 0,85 (+0,047 [0,033;0,065]); khi cả hai chọn ngưỡng cùng quy tắc F2 (L3 166, persistence 160) recall 96,9% vs. 96,1% không tách, precision hơn +0,046 [0,024;0,074]. Theo nhóm: Delhi/Gurugram/Lucknow (341 cặp) recall 0,99 precision 0,82; Jaipur/Amritsar (38 cặp) recall 0,84 thấp hơn và precision 0,49; miền Nam (10 cặp) không đủ để đánh giá.

**Diễn giải hệ số (OLS diễn giải, tách biệt Ridge dự báo):** Độ ẩm +10 điểm % đi cùng AQI mai −1,2% [−2,0;−0,3], gió +1 m/s −1,9% [−3,0;−0,8]; trong mô hình diễn giải, ngày có lượng mưa 10 mm so với không mưa đi cùng AQI ngày kế tiếp thấp hơn khoảng 9,2% khi giữ các biến khác không đổi. Nhiệt độ, BLH, áp suất không tách khỏi 0 sau khi giữ AQI/chất ô nhiễm.

**Hình 11.** Chẩn đoán phần dư và QQ-plot trên thang log (`model_01_residual_diagnostics.png`).  
**Hình 12.** MAE theo mức đặc trưng L1→L3 và persistence (`model_02_mae_by_model.png`).  
**Hình 13.** MAE theo thành phố (`model_03_mae_by_city.png`).  
**Hình 14.** Đường Precision–Recall (`model_04_precision_recall.png`). *Nguồn: bảng kết quả `06_predict_aqi.ipynb`.*

### 3.4. Trình bày sản phẩm ứng dụng

Ứng dụng một tệp HTML gồm 4 tab: **(1) Xem một ngày & giải phẫu dự báo** — chọn nhanh 4 tình huống, chọn (TP, ngày), hiển thị hai ngưỡng (chuẩn 201 và ưu tiên không bỏ sót 166/160), thang CPCB, số đo chất ô nhiễm + thời tiết hôm nay và bảng dịch chuyển dự báo qua L1→L3; **(2) Toàn cảnh giai đoạn kiểm thử** — đường AQI thực tế mai vs. dự báo L3 trên 1.947 cặp, điểm báo nhầm/bỏ sót, kéo thử ngưỡng; **(3) Thời tiết giúp được gì** — MAE biên và bảng hệ số OLS diễn giải với KTC bền khối; **(4) Giới hạn & phạm vi** — nêu phát lại trên dữ liệu lịch sử.

**Kịch bản minh họa:**

| # | Kịch bản | Kết quả |
|---|---|---|
| 1 | Bắt đúng Delhi 24/01/2020 (155→251) | L3 200 ≥166 báo đúng, persistence bỏ sót; dự báo thay đổi khi so sánh mô hình với tập đặc trưng khác nhau |
| 2 | Điểm mù Delhi 10/07/2019 | Đợt tăng đột ngột mà cả hai phương pháp bỏ sót trong ví dụ |
| 3 | Báo nhầm Jaipur 03/11/2019 | Báo thừa khi ngưỡng hạ |
| 4 | Khóa miền Nam Bengaluru 20/12/2019 | Mẫu cảnh báo quá nhỏ, chỉ xem sai số điểm |

**Giới hạn sản phẩm:** Tệp tĩnh, phát lại lịch sử, không dự báo trực tuyến; dữ liệu minh họa được nhúng trong tệp, không cần gọi API để lấy các bản ghi này (cần kiểm tra thư viện/font bên ngoài trước khi khẳng định hoàn toàn offline); ngưỡng chọn trên train có thể hơi dễ do tỷ lệ cặp có AQI ≥201 giảm dần; không đánh giá cảnh báo cho miền Nam.

**Hình 15.** Giao diện ứng dụng minh họa/phát lại trên dữ liệu lịch sử (`Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html`) — ảnh chụp cần khớp phiên bản HTML thực tế; nếu HTML chưa sửa cách gọi “mùa đông” hay “chống rò rỉ tuyệt đối”, không mô tả như đã sửa. *Dữ liệu minh họa được nhúng trong tệp.*

### 3.5. Những hạn chế

- **Phạm vi:** 8 TP chọn vì độ phủ/tính đồng nhất, không đại diện 26 TP hay toàn Ấn Độ; chuỗi dài ngắn khác nhau nên chỉ so trong khoảng chung.
- **Đo lường và thiếu:** Xylene/PM10 Lucknow và các cặp thiếu nặng không dùng trong phép so sánh cụ thể; dữ liệu thiếu có xu hướng tập trung thành khối thời gian, bộ dữ liệu hiện có chưa cho phép xác định đầy đủ cơ chế thiếu; chuỗi 0 treo/ngoại lai/nghi lỗi được gắn cờ nhưng chưa đối chiếu CPCB.
- **Thời tiết:** Dữ liệu mô hình lưới 0,25°, Delhi–Gurugram tương quan cao; thời tiết ngày mai là tái phân tích, chỉ dùng cho kịch bản tham chiếu.
- **Mô hình:** Thiết kế đầu vào dự kiến đến hết hôm nay với scaler/imputer chỉ fit trên train; các kiểm tra độ nhạy không loại trừ mọi nguồn phụ thuộc tương lai; lợi thế chưa xác nhận ở giai đoạn giữ lại cuối; miền Nam không đủ mẫu cảnh báo.

### 3.6. Hướng phát triển

- Đối chiếu đỉnh nghi lỗi với nguồn CPCB; thử bổ sung Xylene/PM10 ở TP có dữ liệu trong phép riêng.
- Củng cố quy trình kiểm soát phụ thuộc thời gian cho dự báo; thử các cách khử mùa khác và kiểm theo TP riêng.
- Hiệu chuẩn ngưỡng cảnh báo theo chi phí bỏ sót/báo thừa địa phương; đánh giá trên nhiều cửa sổ thời gian.
- Hoàn thiện sản phẩm minh họa để khớp lời văn báo cáo và kiểm tra thư viện/font trước khi khẳng định chế độ offline hoàn toàn.

---

## Kết luận

Báo cáo thực hiện trọn vòng đời khoa học dữ liệu cho phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ trên dữ liệu CPCB 2015–2020, với thời tiết ERA5 là nguồn bổ sung.

Về **hiện trạng**, trong khoảng chung, ba TP đồng bằng Bắc Ấn có khoảng một nửa số cặp có AQI ≥201, cao hơn rõ rệt so với ba TP phía Nam được khảo sát; mùa cao điểm tập trung tháng 11–12 ở Bắc/Tây Bắc; khi AQI nặng, trung vị tỷ số PM2.5 giữa nhóm cặp có AQI ≥201 và nhóm còn lại là 2,82 (gộp 8 TP là 137,1 vs. 42,0, tỷ số ≈3,26).

Về **thời tiết–AQI**, sau điều chỉnh mùa vụ, độ ẩm giữ chiều âm nhất quán; nhóm 15 kiểm định nêu trước có 3 ủng hộ, 1 ngược chiều; trên 48 cặp, hai cách đánh giá cho 32 và 33 cặp đạt tiêu chí, không hoàn toàn tương đương.

Về **mô hình (mở rộng)**, trên giai đoạn kiểm thử, Ridge L3 giảm MAE so với persistence (−16,8%) với đóng góp biên của thời tiết −1,4 điểm so với chỉ dùng chất ô nhiễm. Ở cảnh báo AQI ≥201, khi so công bằng cùng quy tắc chọn ngưỡng, mô hình có precision cao hơn, nhưng không đánh giá được cho miền Nam do mẫu quá nhỏ và mức cải thiện chưa được xác nhận ở giai đoạn giữ lại cuối.

Ứng dụng là minh họa/phát lại trên dữ liệu lịch sử, chưa khẳng định dự báo trực tuyến. Các hạn chế về đại diện, đo lường, thiếu theo khối, dữ liệu lưới và phụ thuộc tương lai đã được nêu, cùng hướng phát triển tập trung vào đối chiếu nguồn, củng cố pipeline và hiệu chuẩn cảnh báo theo bối cảnh địa phương.

---

## Tài liệu tham khảo

> Mọi số liệu trong nội dung đều trỏ đến bảng/hình cụ thể nêu trong ngoặc; danh mục dưới đây chỉ liệt kê nguồn gốc và phương pháp, không thay thế trích dẫn tại chỗ.

1. **Central Pollution Control Board (CPCB), Government of India.** Dữ liệu quan trắc chất lượng không khí theo ngày — nguồn gốc của `city_day.csv`. [Cần bổ sung URL CPCB và ngày truy cập thực tế kiểm tra].

2. **Rohan Rao.** *Air Quality Data in India* (2015–2020) — `city_day.csv`. Kaggle. https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india [Cần kiểm tra URL và ngày truy cập thực tế; đối chiếu `Metadata.json`].

3. **National Air Quality Index — Thang AQI CPCB.** Ngưỡng phân loại Good (0–50), Satisfactory (51–100), Moderate (101–200), Poor (201–300), Very Poor (301–400), Severe (>400). [Cần bổ sung văn bản CPCB quy định thang và ngưỡng 201].

4. **Open-Meteo Historical Weather API.** Dữ liệu thời tiết theo giờ, tái phân tích **ERA5 (ECMWF/Copernicus)**, giấy phép **CC BY 4.0**, ghi công *Weather data by Open-Meteo.com*. https://open-meteo.com/en/docs/historical-weather-api [Cần kiểm tra URL, giấy phép và ngày truy cập; đối chiếu `Data_dictionary.md` §3 và `Metadata.json` §weather_source].

5. **Copernicus Climate Data Store / ECMWF ERA5.** Dữ liệu tái phân tích khí quyển trên lưới 0,25°. [Cần bổ sung trích dẫn ERA5 và ngày truy cập].

6. **Rubric học phần Khoa học dữ liệu (INFO3020).** Ma trận nội dung kiểm tra và yêu cầu báo cáo (Phần 1–4). [Cần bổ sung tên giảng viên, năm và bản PDF rubric đính kèm: `Mau_Rubric_danh_gia_Bai_tap_lon.pdf`].

7. **Phương pháp thống kê:** Spearman rank correlation; Mann-Whitney U; hiệu chỉnh đa kiểm định Bonferroni và Benjamini–Hochberg (FDR); bootstrap theo khối thời gian 14 ngày; hồi quy Ridge (L2), OLS với sai số chuẩn bền theo cụm (cluster-robust), kiểm định Breusch-Pagan. [Cần bổ sung trích dẫn sách/giáo trình cụ thể cho từng phương pháp nếu rubric yêu cầu].

*Ghi chú trích dẫn tại chỗ:* Mỗi bảng/hình trong Phần III đều ghi nguồn (CPCB qua Kaggle; Open-Meteo ERA5) và cỡ mẫu/khoảng ngày ở chân hình; số liệu suy ra (ví dụ MAE, Precision/Recall) trỏ đến bảng/hình trong `notebooks/03_eda`, `05_weather_correlation`, `06_predict_aqi` tương ứng, không chỉ liệt kê chung ở cuối.

---

## Phụ lục

### Phụ lục A. Từ điển dữ liệu và provenance

Từ điển 16 cột gốc và 40 cột sau làm sạch, thông tin nguồn CPCB/Kaggle và Open-Meteo ERA5 (tọa độ, lưới 0,25°, CC BY 4.0), và log làm sạch tổng hợp xem `Data_dictionary.md`, `Metadata.json` và `cleaning_log_8cities.md`. Chi tiết định lượng theo từng cặp (thành phố, cột) xem `cleaning_summary_8cities.csv` (105 dòng văn bản =104 bản ghi +1 tiêu đề) và `suspect_points_8cities.csv` (94 dòng văn bản =93 bản ghi +1 tiêu đề).

*Bảng nguồn chi tiết, checklist biên tập nội bộ và lịch sử sửa `limit=14` được lưu riêng trong `PHAN_III_BANG_NGUON_VA_31_32_BAN_THAO.md` — không thuộc phụ lục bài nộp.*

### Phụ lục B. Chi tiết độ nhạy mô hình

| Phép thử | Thiết kế | Kết quả |
|---|---|---|
| Bỏ 10% train ×100 | Lặp, tính lại ΔMAE | L3−L1 −3,52→−3,30; L3−persistence −4,02→−3,81 |
| Loại Gurugram | Bỏ toàn bộ cặp Gurugram | L3 vẫn hơn 3,36 [2,11;4,63] |
| Giữ ô ước lượng | Không đặt lại NaN | MAE đổi 0,01 (L2)/0,03 (L3) trên 1,1% cặp |
| Tách giai đoạn | Mùa cao điểm vs. thấp | Giảm 21% (28,2→22,1) vs. 13% (20,7→18,0) |

*Ghi chú: Thống nhất thuật ngữ “giai đoạn kiểm thử (01/07/2019–29/02/2020)”, “kịch bản tham chiếu sử dụng thông tin thời tiết ngày mai”, “tạo giá trị ước lượng tại khoảng thiếu”, “cặp thành phố–ngày”, “giai đoạn giữ lại cuối (tháng 3–7/2020)”.*

