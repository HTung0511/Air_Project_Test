# PHẦN II. PHÂN TÍCH BÀI TOÁN THỰC TẾ
### (Bản thảo phương pháp — phiên bản nhóm nộp)

> **Phạm vi chương:** Chương này chỉ trình bày **thiết kế, quy tắc, lý do lựa chọn và cách đánh giá** đã được áp dụng trong phiên bản nhóm nộp. Mọi **số liệu trước–sau làm sạch, tần suất/phân bố, hệ số tương quan, kết quả kiểm định và độ đo hiệu năng mô hình** được để sang **Phần III** nhằm tránh lặp. Thang đo, ngưỡng và công thức được nêu là quy ước phương pháp; số dòng/ô bị ảnh hưởng cụ thể sẽ trình bày ở Phần III kèm bảng nguồn `cleaning_summary_8cities.csv`.
>
> **Căn cứ phương pháp:** `Data_dictionary.md`, `Metadata.json`, `reports/cleaning_log_8cities.md` (§1–3), `src/pipeline.py`/`src/utils.py`/`src/weather_utils.py`/`src/eda_utils.py`/`src/corr_utils.py`/`src/model_utils.py` và các notebook `01_cleaning`, `02_cleaning_evidence`, `03_eda`, `04_weather_merge`, `05_weather_correlation`, `06_predict_aqi` **của nhóm nộp** [Cần đối chiếu commit nhóm nộp chính thức]. Các cải tiến đề xuất trên **bản sao thử nghiệm (Test)** — ví dụ: đọc cache offline, dựng đặc trưng trực tiếp từ dữ liệu gốc — là **hướng phát triển, chưa phải phương pháp đã thực hiện** và không được mô tả như chức năng nhóm đã triển khai. Kiểm chứng F01/F02 và PR #4 (Dev) chưa đóng nên báo cáo **không tuyên bố đã loại bỏ hoàn toàn leakage**.
>
> **Quy ước thuật ngữ:** *ô* = một giá trị của một cột trong một ngày; *dòng* = một ngày của một thành phố. Toàn bộ thao tác làm sạch giữ nguyên số dòng và có cờ truy vết.

---

## 2.1. Thu thập dữ liệu

### 2.1.1. Nguồn chính: quan trắc chất lượng không khí

Nguồn chính là bộ dữ liệu **Air Quality Data in India (2015–2020) — `city_day.csv`** chia sẻ trên **Kaggle** (`rohanrao/air-quality-data-in-india`), nguồn gốc **Central Pollution Control Board (CPCB), Government of India** (Metadata.json §source). Dữ liệu ở dạng **CSV**, mỗi dòng là một cặp **(City, Date)** theo ngày. Các trường gốc gồm: `City` (text), `Date` (date), 11 chất ô nhiễm (`PM2.5`, `PM10`, `NO`, `NO2`, `NOx`, `NH3`, `CO`, `SO2`, `O3`, `Benzene`, `Toluene`, `Xylene`), cùng `AQI` (chỉ số tổng hợp) và `AQI_Bucket` (nhãn phân loại theo thang CPCB: Good/Satisfactory/Moderate/Poor/Very Poor/Severe). Đơn vị các chất giữ nguyên theo nguồn (µg/m³ hoặc mg/m³/ppb tùy chất) và được ghi trong `Data_dictionary.md` §1; thang AQI không có đơn vị.

Về quy mô nguồn, tệp gốc chứa 29.531 dòng, 26 thành phố, từ 01/01/2015 đến 01/07/2020. Nghiên cứu chọn **8 thành phố** để phân tích sâu: **Delhi, Gurugram, Lucknow, Jaipur, Bengaluru, Amritsar, Chennai, Hyderabad** — tiêu chí lựa chọn là **khoảng thời gian quan sát tương đối đồng nhất và độ phủ AQI tương đối đầy đủ hơn các phương án khác được cân nhắc, phục vụ khả năng so sánh nội bộ** (`GOI_BO_SUNG_BAO_CAO.md` §1; `Metadata.json` §selected_cities_for_deep_analysis). Tiêu chí này **không được diễn giải như bằng chứng đại diện toàn Ấn Độ hay xếp hạng ô nhiễm nhất**. Sau khi giới hạn 8 thành phố, tập làm việc có **14.056 dòng** (mỗi thành phố một chuỗi liên tục theo ngày, không trùng khóa, không đứt ngày) [Cần đối chiếu `cleaning_log_8cities.md` §Tổng quan]. Tệp gốc được giữ nguyên tại `data/raw/city_day.csv`, không chỉnh sửa.

Tỷ lệ thiếu ban đầu khác nhau giữa các cột (ví dụ: Xylene thiếu nặng, AQI thiếu ở mức trung bình) được ghi đầy đủ trong `Metadata.json` §missing_pct_by_column và `Data_dictionary.md` §1; chi tiết theo từng cặp (thành phố, cột) được lưu trong `reports/cleaning_summary_8cities.csv`. AQI_Bucket thiếu đồng bộ với AQI; không có bản ghi trùng lặp (City, Date) và không có giá trị âm theo kiểm tra ban đầu.

### 2.1.2. Nguồn thứ hai: thời tiết tái phân tích ERA5 qua Open-Meteo

Nhằm bổ sung biến giải thích cho phân tích tương quan và thử mở rộng dự báo, nhóm thu thập **thời tiết theo giờ** qua **Open-Meteo Historical Weather API** (dữ liệu tái phân tích **ERA5** của ECMWF/Copernicus), giấy phép **CC BY 4.0**, ghi công *Weather data by Open-Meteo.com* (`Data_dictionary.md` §3; `Metadata.json` §weather_source). Mỗi thành phố được yêu cầu theo **một điểm tọa độ trung tâm** (ví dụ: Delhi 28,61°N 77,21°E) và API trả về giá trị trên **ô lưới 0,25° (~25 km)** gần nhất; tọa độ ô lưới thực dùng, độ cao ô lưới và độ lệch so với tọa độ yêu cầu được liệt kê trong `Data_dictionary.md` §3.

Khoảng thời gian yêu cầu là **25/12/2014–01/07/2020** theo múi giờ **Asia/Kolkata (UTC+5:30)** nhằm có đủ 7 ngày đệm trước 01/01/2015 để tạo biến trễ về sau; bảng chính vẫn xét từ 01/01/2015 (và từng thành phố bắt đầu muộn hơn theo thực tế quan trắc). Đơn vị: nhiệt độ °C, gió m/s, mưa mm, áp suất hPa, chiều cao lớp biên (BLH) m. Việc tải và lưu vết được thực hiện bằng `src/weather_utils.py` và `notebooks/04_weather_merge.ipynb`; bản tải về giữ nguyên tại `data/raw/weather/openmeteo_<thành phố>_hourly.csv.gz` (mỗi thành phố 48.384 dòng giờ) và không sửa đổi.

**Lưu ý thiết kế nguồn:** Đây là **dữ liệu mô hình tái phân tích, không phải số đo tại trạm**. Giá trị là trung bình trên ô lưới quanh điểm yêu cầu. Hai thành phố **Delhi và Gurugram ở hai ô lưới sát nhau** nên chuỗi thời tiết theo ngày gần như trùng nhau (tương quan theo ngày ở mức rất cao giữa 0,95 với mưa đến 0,999 với nhiệt độ — `Data_dictionary.md` §3 Known limitations); thiết kế phân tích do đó **không coi hai thành phố này là hai quan sát thời tiết độc lập** khi gộp.

### 2.1.3. Tích hợp và lưu trữ

Từ dữ liệu giờ, nhóm gộp thành **ngày** (trung bình/ngày, min/max/tổng mưa) và tạo các biến dẫn xuất như thành phần gió Đông–Bắc (`wind_u`, `wind_v`), `rain_day` (mưa ≥1 mm), `blh_mean/min` [Cần đối chiếu danh sách 14 cột thời tiết cuối cùng trong `Data_dictionary.md` §3]. Hai bảng phái sinh được lưu tại `data/processed/`:

- `weather_daily_8cities.csv` (8 thành phố × 2.016 ngày = 16.128 dòng, 16 cột) — thời tiết theo ngày đầy đủ;
- `air_quality_8cities_weather.csv` (14.056 dòng × 54 cột = 40 cột chất lượng không khí giữ nguyên + 14 cột thời tiết) — bảng gộp trái theo (City, Date), **không dòng nào thiếu thời tiết** và **không sửa đổi các cột gốc** (`assert_frame_equal` giữa bảng cũ và mới).

Mọi bảng đều kèm **provenance** (nguồn, giấy phép, khoảng thời gian, tọa độ) trong `Metadata.json` và `Data_dictionary.md`; biểu đồ sau này ghi nguồn ở chân hình.

---

## 2.2. Làm sạch và biến đổi dữ liệu

### 2.2.1. Nguyên tắc chung

Toàn bộ làm sạch 8 thành phố được thực hiện bằng **một pipeline thống nhất** (`notebooks/01_cleaning.ipynb`; code ở `src/pipeline.py`, `src/utils.py`, `src/gap_utils.py`; bằng chứng ở `02_cleaning_evidence.ipynb`). Nguyên tắc:

- **Không xóa dòng** (không làm đứt chuỗi thời gian); mọi can thiệp có **cờ truy vết**: `<cột>_was_missing` (ô thiếu gốc hoặc flatline), `<cột>_is_outlier`, `pm25_gt_pm10_flag`, `suspect_sensor_error`.
- **Không scale/encode** ở giai đoạn này (để dành cho pipeline mô hình sau khi chia train/test).
- **Không nội suy AQI/AQI_Bucket** — AQI là biến kết quả, điền là tạo kết quả giả.
- Tệp thô không bị sửa; chạy lại từ thô cho ra cùng bảng gộp (kiểm bằng `assert`).

### 2.2.2. Xử lý chuỗi số 0 treo (flatline)

Với các chất ô nhiễm, chuỗi **giá trị đúng 0 liên tiếp ≥3 ngày** được coi là **nghi treo cảm biến** (không phải nồng độ thật) và **chuyển thành NaN** (`src/utils.py:flag_flatline_zeros`). Lý do: nồng độ khí thực tế hiếm khi đứng yên tuyệt đối ở 0 nhiều ngày liền; giữ lại sẽ kéo trung bình xuống giả. Ngưỡng 3 ngày là quy ước thực hành; notebook bằng chứng có thử độ nhạy đổi ngưỡng 2/5/7 ngày để tham chiếu [Cần đối chiếu kết quả thử trong `02_cleaning_evidence.ipynb` nếu trích].

### 2.2.3. Loại cột và quy ước dùng làm biến

- **Bỏ Xylene ở cả 8 thành phố** để schema đồng nhất, do thiếu gần như hoàn toàn ở 4/8 thành phố (và mức cao ở các thành phố còn lại) — không so sánh được giữa các thành phố.
- **PM10 ở Lucknow để NaN toàn bộ** (thiếu 100% trong nguồn) và không dùng làm biến; các cột khác thiếu ≥60% trong một thành phố **không dùng làm biến mô hình** theo quy ước nhóm (ví dụ: PM10 Chennai, NH3 Gurugram) — cột `dung_lam_bien_mo_hinh` trong `cleaning_summary_8cities.csv`.

### 2.2.4. Nội suy khoảng thiếu ngắn và giữ NaN khoảng dài

Đối với 11 chất ô nhiễm, **khoảng thiếu nằm giữa hai giá trị thật và có độ dài ≤14 ngày** được **nội suy tuyến tính theo thời gian** (`_interpolate_short_gaps`, `limit_area='inside'`). Ngưỡng **14 ngày** được dùng như **quy ước thực hành cho phân tích hồi cứu, không phải tối ưu duy nhất**; nội suy tuyến tính chỉ hợp lý cho khoảng ngắn và có thể làm trơn biến động, ảnh hưởng thống kê đợt ngắn hạn (`GOI_BO_SUNG_BAO_CAO.md` §1).

Thiết kế có **sửa lỗi hàm cũ** `interpolate(limit=14)` của pandas — hàm này vốn điền 14 ngày đầu của khoảng dài rồi mới dừng, tức vẫn bịa số cho khoảng >14 ngày; bản sửa trả các ô vượt ngưỡng về NaN toàn khoảng. **Khoảng thiếu >14 ngày được giữ nguyên NaN** và giữ cờ `_was_missing`. Lý do: thiếu theo khối thời gian (cảm biến chưa lắp/ngừng hoạt động) gần **MAR theo thời gian** hơn là MCAR; nội suy xuyên khối dài là bịa số. AQI không nằm trong danh sách nội suy.

> **Hạn chế thiết kế cần lưu ý (sẽ phân tích ở Phần III):** Ô nội suy trong bước này **sử dụng giá trị của các ngày sau** (nội suy hồi cứu). Do đó **quy trình hồi cứu không mặc nhiên phù hợp cho dự báo tại thời điểm thực tế**; mọi mô hình dự báo cần xử lý riêng các ô này (xem §2.4) và báo cáo không tuyên bố pipeline hồi cứu đã sạch leakage cho bài toán dự báo.

### 2.2.5. Đánh dấu ngoại lai và điểm nghi lỗi cảm biến

- **Ngoại lai:** IQR với hệ số **k=1,5** **tính riêng theo tháng dương lịch** (không tính trên toàn chuỗi để tránh nhầm mùa ô nhiễm cao thành ngoại lai). Kết quả **chỉ đánh dấu** (`_is_outlier`), **không sửa/xóa giá trị**; không áp dụng cho AQI.
- **Nghi lỗi cảm biến:** Áp dụng **cùng một luật cho cả 8 thành phố**, chỉ xét **top 5 điểm lớn nhất của PM2.5 và của AQI** mỗi thành phố: đỉnh cô lập, trái mùa, các chất khác không tăng theo, hoặc PM2.5 >1,5×PM10 được gắn `suspect_sensor_error = True`, **đặt NaN và không nội suy**; giá trị gốc được lưu trong `reports/suspect_points_8cities.csv` để khôi phục. Nhãn là “nghi lỗi”, **chưa đối chiếu được nguồn CPCB**.

### 2.2.6. Kiểm tra logic và gộp bảng

- **Nhất quán PM2.5–PM10:** gắn cờ `pm25_gt_pm10_flag` khi PM2.5 >1,2×PM10 (vô lý vì PM10 đã gồm PM2.5); chỉ đánh dấu.
- **Gộp 8 thành phố:** `pd.concat`, không scale/không mã hóa; kiểm bằng 10 `assert` (số dòng khớp thô, giá trị giống từng tệp thành phố, chuỗi ngày liên tục).

### 2.2.7. Biến đổi thời tiết và ghép bảng

Các bước 12–17 trong `cleaning_log_8cities.md` mô tả: yêu cầu API theo **Asia/Kolkata**, gộp 24 giờ thành ngày, tính `wind_u/v` từ tốc độ + hướng (không dùng độ thô 0°/360° trực tiếp trong hồi quy), tạo `precip_sum`/`rain_day`/`blh_mean` v.v., giữ nguyên bảng không thời tiết và xuất `air_quality_8cities_weather.csv` qua **ghép trái** theo (City, Date). Biến đổi như `log1p(precip_sum)` được **để dành cho giai đoạn mô hình sau khi chia train/test** để tránh rò rỉ.

Toàn bộ hạn chế phương pháp (chuỗi dài ngắn khác nhau, mất Xylene, PM10 Chennai, Delhi–Gurugram trùng thời tiết, thời tiết “ngày mai” là số đã xảy ra) được liệt kê trong `cleaning_log_8cities.md` §3 **Hạn chế** và sẽ được đối chiếu khi diễn giải ở Phần III.

---

## 2.3. EDA và trực quan hóa dữ liệu — gồm Data Storytelling

### 2.3.1. Mục tiêu và phạm vi EDA

EDA được thiết kế để trả lời ba cụm câu hỏi mô tả, với **khoảng chung 14/06/2017–01/07/2020** cho so sánh giữa các thành phố và **tháng 1–6 khi so sánh theo năm** (tránh lệch mùa và loại nửa cuối 2020 có phong tỏa) [Cần đối chiếu quy ước khoảng chung/ lọc năm trong `src/eda_utils.py:load()` và `notebooks/03_eda.ipynb`]:

- **Ở đâu ô nhiễm nặng hơn?** — tần suất và mức độ ngày có AQI ≥201 (ngưỡng Poor theo thang CPCB).
- **Khi nào ô nhiễm cao?** — biến động theo tháng/mùa và theo năm.
- **Do chất nào?** — quan hệ giữa các chất ô nhiễm và AQI, đặc biệt PM2.5.

Ngưỡng **AQI ≥201** được dùng thống nhất như định nghĩa “ngày ô nhiễm nặng” cho EDA và về sau cho bài toán cảnh báo; thang CPCB (Good/Satisfactory/Moderate/Poor/Very Poor/Severe) được dùng cho màu sắc tham chiếu.

### 2.3.2. Phương pháp thống kê mô tả

Thiết kế EDA sử dụng thống kê mô tả phù hợp với phân bố lệch: **trung vị, IQR, tỷ lệ ngày ≥201**, cùng **Spearman** cho tương quan chất–AQI (thay vì Pearson trên phân bố lệch). PM2.5–AQI được xem xét riêng do AQI được tính theo nguyên tắc **max chỉ số con**, nên tương quan cao một phần là hệ quả công thức — ghi chú này được đưa vào diễn giải.

Mọi biểu đồ tuân thủ quy ước trong `src/eda_utils.py`: palette an toàn mù màu (một màu nhấn #D55E00, còn lại trung tính), tiêu đề là **câu kết luận có số**, chân hình ghi **nguồn (CPCB qua Kaggle), cỡ mẫu n, khoảng ngày**.

### 2.3.3. Bộ trực quan hóa và Data Storytelling

Bộ hình EDA (6 hình chính trong `reports/figures/eda_*.png`) được thiết kế theo mạch kể chuyện **“Ở đâu → Khi nào → Do chất nào”**, mỗi phát hiện gắn **một biểu đồ**:

- `eda_00_sample_size` — độ dài chuỗi mỗi thành phố (minh họa khác biệt chuỗi);
- `eda_01_poor_share_city` — tỷ lệ ngày ≥201 theo thành phố (so sánh không gian);
- `eda_02_heatmap_city_month` — heatmap City×Month (mùa vụ);
- `eda_03_trend_city_year` — xu hướng City×Year (năm);
- `eda_04_pm25_aqi` — quan hệ PM2.5–AQI (thành phần);
- `eda_05_aqi_distribution` — phân bố AQI (hình thái phân bố).

Mỗi hình có **ghi chú confounder** tiềm ẩn: vị trí/trọng số trạm trong trung bình thành phố, quy mô đô thị, sự kiện **Diwali**, **đốt rơm rạ Punjab**, và cách tính AQI — nhằm tránh suy diễn vội. Thiết kế cũng lưu ý rủi ro trực quan gây hiểu lầm: trục không từ 0, gộp 8 TP trộn lẫn khác biệt, và tác động của nửa cuối 2020 (phong tỏa) lên xu hướng.

### 2.3.4. Kiểm tra độ nhạy và tính vững

EDA có **kiểm tra độ nhạy** theo thiết kế: đổi **khoảng chung** (ví dụ: so sánh toàn chuỗi vs. khoảng chung), **loại giai đoạn phong tỏa COVID-19**, và thử **xếp hạng nhóm thay vì xếp hạng 1–8** khi các tỷ lệ gần nhau — để đánh giá độ vững của thứ hạng và tỷ số mùa. Hai cách tổng hợp **tỷ số mùa** trả lời hai câu hỏi khác nhau và được phân biệt trong thiết kế: (i) trung vị tỷ số mùa cao/mùa mưa **trên các thành phố trong phép tính tương ứng** và (ii) tỷ số của **số liệu gộp 8 thành phố**; định nghĩa mùa, tập thành phố và loại khoảng sẽ được đối chiếu trước khi trích dẫn ở Phần III (`GOI_BO_SUNG_BAO_CAO.md` §1).

---

## 2.4. Mô hình hóa và đánh giá — đặc trưng, huấn luyện, chia tập, baseline và độ đo

> Bài toán **dự báo AQI ngày kế tiếp** là **phần mở rộng**, không lấn át trọng tâm phân tích. Thiết kế dưới đây mô tả **phiên bản nhóm nộp** trong `notebooks/06_predict_aqi.ipynb` và `src/model_utils.py`; các cải tiến đề xuất trên bản Test (đọc cache offline, dựng đặc trưng từ dữ liệu gốc) **không được mô tả như phương pháp đã thực hiện**.

### 2.4.1. Khung bài toán và chia tập theo thời gian

- **Đơn vị quan sát:** một dòng = **(thành phố, ngày hôm nay t)**; **mục tiêu** = **AQI của ngày t+1** (`aqi_next`); mọi đặc trưng **chỉ dùng thông tin đến hết ngày t** theo nguyên tắc thiết kế.
- **Chia theo thời gian (theo ngày được dự đoán):** **train** = ngày được dự đoán đến hết **30/06/2019**; **giai đoạn kiểm thử** = **01/07/2019–29/02/2020** (cửa sổ kiểm thử độc lập — báo cáo thống nhất gọi là *giai đoạn kiểm thử*, không gọi “mùa đông”); **lockdown** = từ **01/03/2020** tách riêng, **không dùng để lựa chọn mô hình** (`TRAIN_END`, `TEST_START/END`, `LOCK_START` trong `model_utils.py`).
- **Lý do Ridge trước cây:** Ridge (hồi quy tuyến tính có chuẩn hóa L2) được chọn làm mô hình chính để **diễn giải hệ số** và làm baseline mạnh, so sánh thêm với cây (HistGradientBoosting) [Cần đối chiếu lý do lựa chọn Ridge/cây trong notebook 06 nhóm nộp].
- **Cross-validation nội bộ:** **TimeSeriesSplit** (4 lần chia) với **gap** 16 dòng (~2 ngày × 8 thành phố) giữa train/validation trong mỗi lần chia, tôn trọng thứ tự thời gian.

### 2.4.2. Đặc trưng

Đặc trưng được nhóm thành **4 mức** để đo đóng góp biên:

- **L1 (lịch sử AQI + mùa):** `aqi_0, aqi_1, aqi_2, aqi_wk` (log AQI hôm nay/hôm qua/hôm kia/trung bình 7 ngày trước) + `doy_sin/cos` (ngày trong năm của **ngày được dự đoán**, biết trước).
- **L2 (L1 + chất ô nhiễm hôm nay):** `pm25_0, no2_0, co_0, so2_0, o3_0` ở dạng **log(1 + nồng độ)**; chỉ các chất đủ dữ liệu ở cả 8 TP (`USABLE`) được dùng.
- **L3 (L2 + thời tiết đến hết hôm nay):** `temp_mean, humidity_mean, pressure_dev, d_pressure, wind_speed_mean, wind_u, wind_v, blh_mean, precip_log` (trong đó `pressure_dev` = lệch so với trung bình 30 ngày trước của chính thành phố, chỉ nhìn quá khứ; `precip_log = log1p(precip_sum)`).
- **L4 (cận trên):** L3 **+ thời tiết ngày mai** (`*_next`) — **chỉ để tham chiếu** và được gắn nhãn **“Cận trên: dự báo thời tiết hoàn hảo”** (do thời tiết “ngày mai” trong dữ liệu là số tái phân tích đã xảy ra, không phải dự báo thời tiết có sai số).

Biến phân loại **City** được mã hóa **OneHot** (Delhi làm mức tham chiếu) và đưa vào Pipeline.

### 2.4.3. Xử lý dữ liệu thiếu và chuẩn hóa — thiết kế chống rò rỉ ở mức pipeline

- **Ô chất ô nhiễm đã nội suy ở bước làm sạch** được **đặt lại NaN** khi dựng đặc trưng (do nội suy đã dùng giá trị tương lai), sau đó **điền lùi tối đa 2 ngày chỉ dùng quá khứ** (`ffill limit=2` theo City), phần còn thiếu được **điền trung vị của tập huấn luyện trong Pipeline** kèm cột báo thiếu (`SimpleImputer(add_indicator=True)`) [Cần đối chiếu đoạn `make_features(mask_interp=True)` trong phiên bản nhóm nộp].
- **Mọi thành phần có học tham số** (imputer, scaler, encoder, mô hình) nằm **trong `Pipeline`/`ColumnTransformer` và chỉ fit trên train**; scaler là `StandardScaler`.
- **Phép kiểm `as_of`** (cắt dữ liệu sau một ngày và so sánh đặc trưng của ngày đó giữa bản cắt và bản đầy đủ) **được đề xuất** để thử rò rỉ trực tiếp, nhưng **kiểm chứng F01 chưa hoàn tất** trong phạm vi dừng; do đó báo cáo **không tuyên bố mô hình đã “chống rò rỉ tuyệt đối”**.

### 2.4.4. Baseline và độ đo

**Ba baseline** học trên train và dự đoán cho tập mới:

- Trung bình theo thành phố;
- Trung vị cùng thành phố & cùng tháng của ngày được dự đoán (khí hậu);
- **Persistence “Ngày mai = hôm nay”** (sao chép AQI hôm nay) — baseline quán tính mạnh do AQI tự tương quan cao.

**Độ đo:**

- **Hồi quy:** **MAE** (điểm AQI, càng thấp càng tốt) là độ đo chính, kèm **R²**; dự đoán trên **log(AQI)** rồi biến đổi ngược `exp` về điểm AQI.
- **Cảnh báo nhị phân (AQI ≥201):** **Precision/Recall** (và F-score) ở hai chế độ vận hành: **ngưỡng chuẩn 201** và **ngưỡng ưu tiên không bỏ sót** (chọn bằng **F2** trên train-OOF, recall nặng gấp đôi precision).
- **Diễn giải hệ số:** OLS trên log(AQI) ngày mai với **sai số chuẩn bền theo cụm khối 14 ngày** (khử phương sai thay đổi, Breusch-Pagan), diễn giải theo *“đi cùng với”*, giữ các biến khác không đổi, kèm khoảng giá trị đã quan sát.

### 2.4.5. Chẩn đoán và kiểm tra độ nhạy

Thiết kế bao gồm:

- **Chẩn đoán phần dư:** phần dư vs. dự đoán, **QQ-plot**; kiểm tra phương sai thay đổi.
- **Bootstrap theo khối 14 ngày** (`block_id` theo City–Year–khối) cho **khoảng tin cậy** của hiệu ứng (trung vị nhóm bất lợi – thuận lợi) và của ΔMAE giữa các mức; **hiệu chỉnh đa kiểm định** (Bonferroni cho family 15 giả thuyết nêu trước; FDR Benjamini-Hochberg cho bảng tương quan).
- **Kiểm tra độ nhạy:** bỏ cờ `_was_missing`, đổi ngưỡng nội suy, so sánh L1/L2/L3 và so sánh khi **không dùng thời tiết ngày mai** vs. **cận trên** có thời tiết ngày mai.

---

## 2.5. Đạo đức dữ liệu và sử dụng kết quả có trách nhiệm

*Mục này ngắn gọn, theo rubric là không bắt buộc nhưng được trình bày để đáp ứng liêm chính học thuật.*

**Bảo mật & quyền riêng tư:** Dữ liệu CPCB là **tổng hợp công khai theo thành phố/ngày**, không chứa thông tin định danh cá nhân (PII); không cần ẩn danh hóa dòng người. Thời tiết là dữ liệu mô hình lưới 0,25°, không nhạy cảm. Báo cáo trích nguồn và giấy phép (Kaggle/CPCB; Open-Meteo CC BY 4.0) ở chân mỗi biểu đồ qua `provenance()`.

**Thiên kiến (bias) & công bằng:** Thiết kế ghi nhận ít nhất ba thiên kiến:

- **Bias chọn mẫu:** 8 TP được chọn vì độ phủ AQI tương đối đầy đủ → không đại diện cho 26 TP và không suy diễn toàn Ấn Độ;
- **Bias thời gian:** chuỗi dài ngắn khác nhau và nửa cuối 2020 có phong tỏa; so sánh theo năm chỉ dùng tháng 1–6 và tách lockdown;
- **Bias đo lường:** Xylene/PM10/NH3 thiếu nặng ở một số TP, thời tiết là mô hình lưới (Delhi–Gurugram trùng nhau), AQI là max chỉ số con nên tương quan PM2.5–AQI mang tính cấu trúc.

**AI có trách nhiệm & sử dụng kết quả:** Nhóm **không bịa số** cho khoảng thiếu >14 ngày (giữ NaN), **không dùng tương lai khi dự đoán** ở mức thiết kế pipeline (mask_interp + chỉ fit trên train), và **không coi tương quan là nhân quả** (chỉ nói “có liên quan/đi cùng với 95% KTC”). Mỗi biểu đồ/kết luận kèm ghi chú hạn chế; AQI ≥201 chỉ dùng cho phân tích, **không thay thế tư vấn y tế hay quyết định quản lý**.

**Tái tạo được:** `Requirements.txt` liệt kê phiên bản thư viện (pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, statsmodels, jupyter, requests); `README.md` §4 nêu thứ tự chạy 01→06; mỗi notebook chạy *Restart & Run All* từ `notebooks/` không lỗi trên bản nhóm nộp [Cần đối chiếu phiên bản `Requirements.txt` nhóm nộp].

---

**Ghi chú cho Phần III:** Các bảng **trước–sau làm sạch** (16.953 → 15.832 ô thiếu, 2.169 ô flatline, 1.316 ô sửa lỗi limit, 24 ngày nghi lỗi…), **heatmap, tỷ lệ ≥201, hệ số Spearman thô vs. khử mùa, p-value hiệu chỉnh, ΔMAE/R²/Precision/Recall và chẩn đoán phần dư** sẽ được trình bày đầy đủ ở Phần III kèm hình `reports/figures/eda_*`, `corr_*`, `model_*` và trích dẫn bảng nguồn. Phần II không lặp các số này.
