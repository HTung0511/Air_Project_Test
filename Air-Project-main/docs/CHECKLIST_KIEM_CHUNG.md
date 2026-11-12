# CHECKLIST KIỂM CHỨNG ĐO ĐƯỢC — MÔN KHOA HỌC DỮ LIỆU (INFO3020)
### Dùng làm thước đo cho toàn bộ dây chuyền: Thu thập → Làm sạch → EDA → Mô hình → Báo cáo → Vấn đáp

**Vai trò:** Business Analyst (BA) | **Ngày phát hành:** 11/11/2026 | **Branch:** `arena/ad184e76-air-project-test`
**Đồ án áp dụng:** #6 — Phân tích mức độ ô nhiễm không khí theo thời gian — *Air Quality Data in India (CPCB/Kaggle)*
**Nguồn tham chiếu chính:** `ngữ cảnh.txt` (Ma trận nội dung kiểm tra + Rubric + Yêu cầu chọn chủ đề + Nội dung báo cáo)
**Tệp dữ liệu gốc:** `data/raw/city_day.csv` (29.531 dòng, 26 thành phố, 01/01/2015→01/07/2020) + `data/raw/weather/` (Open-Meteo ERA5)
**Phạm vi đã duyệt:** 8 thành phố — Delhi, Gurugram, Lucknow, Jaipur, Bengaluru, Amritsar, Chennai, Hyderabad → `data/processed/air_quality_8cities.csv` (14.056 dòng × 40 cột) và `air_quality_8cities_weather.csv` (14.056 × 54)

---

## 0. Cách đọc checklist này

| Ký hiệu | Ý nghĩa |
|---|---|
| **ID** | Mã kiểm chứng, ví dụ `CK-2.3` = Phần 2, mục 3 |
| **Tiêu chí** | Điều phải làm / phải có |
| **Đo được =** | Công thức, ngưỡng, hoặc lệnh kiểm tra tự động — **Pass/Fail nhị phân** |
| **Bằng chứng (Artifact)** | File/tệp phải tồn tại, đường dẫn cụ thể trong repo |
| **Mức** | B = Bắt buộc (không đạt = rớt phần); K = Khuyến nghị cho mức Giỏi |
| **Trọng số** | Liên kết tới điểm tối đa của Phần trong Ma trận (tổng 10 điểm) |

> **Nguyên tắc BA:** Mọi tiêu chí đều phải trả lời được 3 câu hỏi: *Kiểm tra bằng gì? Ngưỡng bao nhiêu? File nào chứng minh?* Nếu không đo được → không đưa vào checklist.

> **Quy ước Fail nhanh:** Bất kỳ `B` nào = FAIL → Phần đó tối đa chỉ đạt mức **Yếu (0–4.9)** dù các mục khác đạt.

---

## 1. Ma trận tổng quan — 5 Phần thi

| Phần | CLO | Cấp độ | Tên phần (theo đề cương) | Điểm tối đa | Trọng số | Ánh xạ tới báo cáo | Pipeline phụ trách |
|---|---|---|---|---|---|---|---|
| **P1** | CLO1 | C2 Hiểu | Tổng quan & Đặt bài toán | **1.0** | 10% | Chương 1: Giới thiệu chung | `README.md`, `Data_dictionary.md`, `Metadata.json`, notebooks ô markdown đầu |
| **P2** | CLO2 | C3 Vận dụng | Thu thập & Tiền xử lý | **2.5** | 25% | Chương 2a–2b | `src/pipeline.py`, `src/utils.py`, `src/gap_utils.py`, `notebooks/01_cleaning.ipynb`, `02_cleaning_evidence.ipynb` |
| **P3** | CLO3 | C3 Vận dụng | EDA, Trực quan & Mô hình | **3.5** | 35% | Chương 2c–2d | `src/eda_utils.py`, `corr_utils.py`, `model_utils.py`, `notebooks/03_eda.ipynb`, `05_weather_correlation.ipynb`, `06_predict_aqi.ipynb` |
| **P4** | CLO4 | C3 Vận dụng | Đạo đức dữ liệu & Báo cáo | **1.0** | 10% | Chương 2e + Hình thức báo cáo | Toàn repo + file báo cáo PDF/MD, `reports/` |
| **P5** | CLO1–4 | C3 Vận dụng | Vấn đáp & Bảo vệ | **2.0** | 20% | Bảo vệ trực tiếp | Toàn bộ mã nguồn + báo cáo + bộ câu hỏi W8 |

**Thang Rubric chung (áp cho từng Phần và Tổng):**

| Xếp loại | Điểm/10 | % yêu cầu checklist đạt | Diễn giải |
|---|---|---|---|
| **Giỏi** | 8.5–10.0 | 85–100% tiêu chí (100% B) | Complete lifecycle, chính xác, có kiểm chứng |
| **Khá** | 7.0–8.4 | 70–84% | Các bước chính xác, kết quả khả thi |
| **Trung bình** | 5.0–6.9 | 50–69% | Làm được cơ bản, còn sai sót/chưa tối ưu |
| **Yếu** | 0.0–4.9 | <50% hoặc FAIL 1 B | Quy trình không hoàn thiện / mã lỗi không chạy |

---

## 2. P1 — TỔNG QUAN & ĐẶT BÀI TOÁN (1.0đ — 10%)

> **Mục tiêu đo:** Giám khảo đọc 5 phút phải trả lời được: *Vì sao chọn đề tài này? Bài toán dạng gì? Mục tiêu đo bằng gì? Vòng đời nào?*

| ID | Tiêu chí | Đo được = PASS khi | Bằng chứng | Mức | Liên kết CLO |
|---|---|---|---|---|---|
| **CK-1.1** | **Lý do chọn đề tài — thực tiễn, có số liệu** | Báo cáo Chương 1 nêu ≥3 con số thực tế (ví dụ: Delhi AQI trung vị 205, 51% ngày ≥201; mùa đông ô nhiễm gấp 3× mùa hè) + trích nguồn CPCB/Kaggle với URL và ngày truy cập. Kiểm: `grep -c "CPCB\|Kaggle\|rohanrao" README.md` ≥1 và có ≥3 con số %/ngưỡng | `README.md` §1, `reports/cleaning_log_8cities.md` dòng đầu, slide mở đầu | B | CLO1 |
| **CK-1.2** | **Vòng đời Khoa học Dữ liệu được nêu & tuân thủ** | Liệt kê ≥6 giai đoạn vòng đời (ví dụ CRISP-DM hoặc OSEMN: Thu thập → Làm sạch → EDA → Mô hình → Đánh giá → Triển khai/Đạo đức) và **map** mỗi giai đoạn tới notebook/file cụ thể trong repo. Kiểm: có bảng 2 cột `Giai đoạn | File thực hiện` với 6 dòng | `README.md` §3, §4 (bảng thứ tự notebook) | B | CLO1 |
| **CK-1.3** | **Câu hỏi nghiên cứu chính + 3 câu phụ đo được** | Câu hỏi chính ở dạng đo được: *"Ô nhiễm nặng (AQI≥201) tập trung ở thành phố/mùa nào trong 8 TP giai đoạn 2015–2020?"* + 3 câu phụ: (1) Xu hướng theo năm (so cùng tháng 1–6), (2) Chất nào cao nhất khi AQI nặng, (3) 2020 thấp do lockdown hay mùa? Kiểm: tồn tại file/string `AQI >= 201` hoặc `AQI_Bucket` trong EDA | `notebooks/03_eda.ipynb` ô “Câu hỏi nghiên cứu”, `src/eda_utils.py` hằng `POOR_AQI=201` | B | CLO1 |
| **CK-1.4** | **Xác định dạng bài toán phân tích** | Ghi rõ **dạng chính = Hồi quy** (dự đoán AQI ngày mai — biến liên tục) + **dạng phụ = Phân loại/Cảnh báo** (AQI≥201: Poor trở lên) + **dạng mô tả = Phân tích chuỗi thời gian theo mùa/giờ**. Mỗi dạng có *biến mục tiêu (y)* và *đơn vị đo (MAE/R² cho hồi quy, Precision/Recall cho cảnh báo)*. Kiểm: có bảng 3 dòng `Dạng | y | Metric` | `notebooks/06_predict_aqi.ipynb`, `src/model_utils.py` | B | CLO1 |
| **CK-1.5** | **Mục tiêu, phạm vi, giới hạn được lượng hoá** | Phạm vi: 8 TP, 14.056 dòng, khoảng chung 14/06/2017–01/07/2020 (1.114 ngày/TP) + 26 TP gốc để tham chiếu. Giới hạn: nêu ≥4 giới hạn (chuỗi dài ngắn khác nhau, PM10 thiếu 100% Lucknow, thời tiết là dữ liệu mô hình ERA5 0.25°, 2020 có lockdown). Kiểm: `reports/cleaning_log_8cities.md` §3 Hạn chế có ≥4 dòng bảng | `Data_dictionary.md` §2–3, `Metadata.json` | K | CLO1 |
| **CK-1.6** | **Ý nghĩa & ứng dụng thực tế** | Nêu ≥2 nhóm người dùng (cơ quan môi trường, người dân) + ≥2 hành động cụ thể dựa trên phát hiện (ví dụ: ưu tiên cảnh báo tháng 11–12 ở Delhi/Lucknow; giảm đốt rơm rạ). Kiểm: có đoạn `Ứng dụng/Cảnh báo` ≥100 từ | `README.md` §1, báo cáo Chương 1 | K | CLO1 |

**Ngưỡng đạt P1:**
- **Bắt buộc:** CK-1.1 → 1.4 = 4/4 PASS → tối thiểu Trung bình.
- **Giỏi:** 6/6 PASS + trích dẫn đầy đủ (ngày, URL, nguồn CPCB + Open-Meteo CC BY 4.0).

---

## 3. P2 — THU THẬP & TIỀN XỬ LÝ (2.5đ — 25%)

> **Mục tiêu đo:** Từ `city_day.csv` thô → `air_quality_8cities.csv` sạch có thể tái tạo 100% bằng 1 lệnh; mọi ô bị sửa đều có cờ.

### 3.1 Thu thập (CLO2 — Kỹ thuật thu thập)

| ID | Tiêu chí | Đo được = PASS khi | Bằng chứng | Mức |
|---|---|---|---|---|
| **CK-2.1** | **Nguồn chính được mô tả đầy đủ (5W1H)** | `Metadata.json` chứa đủ 6 trường: `source`, `source_url`, `original_source` (CPCB), `collection_method`, `data_file`, `number_of_rows/date_range/fields/missing_pct`. Kiểm: `python -c "import json; d=json.load(open('Metadata.json')); assert all(k in d for k in ['source','source_url','data_file','fields'])"` | `Metadata.json`, `Data_dictionary.md` §1, `data/raw/city_day.csv` (29.531 dòng) | B |
| **CK-2.2** | **Nguồn thứ hai (thời tiết) có provenance riêng** | `Metadata.json.weather_source` có `source` (Open-Meteo ERA5), `source_url`, `license` (CC BY 4.0), `locations` (8 TP × lat/lon/grid_elev), `raw_files` (8 file `.csv.gz`), `temporal_range`. Kiểm: `data/raw/weather/` chứa 8 file `openmeteo_*.csv.gz` mỗi file ~48.384 dòng giờ. Lệnh: `ls data/raw/weather/*.gz | wc -l` == 8 | `src/weather_utils.py`, `notebooks/04_weather_merge.ipynb`, `Data_dictionary.md` §3 | B |
| **CK-2.3** | **Cấu trúc & định dạng được kiểm chứng** | `01_cleaning.ipynb` Bước 0 chạy `assert` cho: 0 trùng (City,Date), 0 đứt ngày (mỗi TP liên tục), 0 giá trị âm, `AQI_Bucket` khớp thang CPCB (6 nhãn), định dạng CSV/JSON/SQL/API/Scraping được liệt kê. Kiểm: notebook chạy `Restart & Run All` không lỗi assert | `notebooks/01_cleaning.ipynb` Bước 0, `src/utils.py: audit()`, `validity_checks()` | B |
| **CK-2.4** | **Thu thập bằng Pandas — code chạy được** | Dùng `pd.read_csv`, `pd.to_datetime`, `pd.merge`, `pd.concat`, `pd.Categorical` trong `src/` (không chỉ thao tác thủ công Excel). Kiểm: `grep -r "pd.read_csv\|pd.merge\|pd.concat" src/ | wc -l` ≥5 và `pip install -r Requirements.txt` + `python -m py_compile src/*.py` pass | `src/*.py`, `Requirements.txt` (pandas, numpy, requests) | B |

### 3.2 Tiền xử lý — Làm sạch & Biến đổi (CLO2)

| ID | Tiêu chí | Đo được = PASS khi | Bằng chứng | Mức |
|---|---|---|---|---|
| **CK-2.5** | **Xử lý khuyết thiếu — flatline 0 → NaN** | Chuỗi 0 liên tiếp ≥3 ngày ở CO/NOx/Benzene/Toluene → NaN; đếm = 2.169 ô (Benzene 646, Toluene 615, CO 540, NOx 368). Kiểm: `src/utils.py: flag_flatline_zeros(min_run=3)` tồn tại và `reports/cleaning_summary_8cities.csv` cột `n_flatline_to_nan` tổng = 2169 | `src/utils.py`, `src/pipeline.py`, `reports/cleaning_log_8cities.md` Bước 1 | B |
| **CK-2.6** | **Xử lý khuyết thiếu — nội suy khoảng ngắn** | Nội suy tuyến tính theo thời gian **chỉ** khoảng thiếu ≤14 ngày nằm giữa 2 giá trị thật; `AQI` **không** nội suy; khoảng dài giữ NaN. Số ô nội suy = 3.329. Kiểm: hàm `_interpolate_short_gaps(max_gap=14)` dùng `interpolate(method='time', limit_area='inside')` + logic `run_len > max_gap → NaN`; `cleaning_summary` cột `n_imputed` tổng = 3329 | `src/utils.py:_interpolate_short_gaps`, `src/gap_utils.py:interpolate_short_gaps`, `pipeline.py:clean_city` | B |
| **CK-2.7** | **Cờ vết missing (`_was_missing`) đầy đủ** | Mỗi cột chất + AQI có cột `<col>_was_missing` (bool): True nếu ô thiếu gốc hoặc flatline. Kiểm: `air_quality_8cities.csv` có 12 cột `*_was_missing`; `assert merged[[f'{p}_was_missing' for p in POLLUTANTS+['AQI']]].dtypes.eq(bool).all()` | `data/processed/air_quality_8cities.csv` (40 cột), `Data_dictionary.md` §2 | B |
| **CK-2.8** | **Xử lý outliers — chỉ đánh dấu, không xoá** | IQR ×1.5 **tính riêng theo tháng dương lịch** (không toàn chuỗi); gắn cờ `<col>_is_outlier`, giữ nguyên giá trị. Tổng 6.656 ô bị cờ. Kiểm: `src/utils.py:flag_outliers_iqr` có `groupby month`; `air_quality_8cities.csv` có 11 cột `*_is_outlier` (bool) | `src/utils.py`, `reports/cleaning_summary_8cities.csv` cột `n_outlier_flagged` | B |
| **CK-2.9** | **Điểm nghi lỗi cảm biến — luật minh bạch** | Luật 4 bằng chứng (gap_vs_neighbors, mùa đông 10–2, chất khác cùng tăng, PM2.5/PM10 >1.5) áp cho top-5 PM2.5 & top-5 AQI mỗi TP (93 điểm xét → 41 ô nghi lỗi/24 ngày → NaN + cờ `suspect_sensor_error`). Kiểm: `reports/suspect_points_8cities.csv` có 93 dòng với cột `suggestion/action`; `pipeline.py:investigate/run_rule/apply_suspect_rule` | `src/pipeline.py`, `reports/suspect_points_8cities.csv` | B |
| **CK-2.10** | **Nhất quán PM2.5–PM10 — gắn cờ logic** | `pm25_gt_pm10_flag` = True khi PM2.5 >1.2×PM10 (vô lý vì PM10 gồm PM2.5); NA khi thiếu 1 trong 2; 139 dòng bị cờ. Kiểm: `merged['pm25_gt_pm10_flag'].sum()` == 139 | `src/pipeline.py:merge_cities`, `Data_dictionary.md` §2 | B |
| **CK-2.11** | **Chuẩn hoá & biến đổi — chưa scale/encode trong file sạch** | File `air_quality_8cities.csv` giữ đơn vị gốc (PM2.5 µg/m³, CO mg/m³), **không** StandardScaler/OneHotEncoder; việc scale/encode để sau khi chia train/test trong Pipeline (tránh rò rỉ). Kiểm: `air_quality_8cities.csv` không có cột `*_scaled` và `src/model_utils.py` chứa `ColumnTransformer` + `StandardScaler` fit trên train | `src/model_utils.py`, `Data_dictionary.md` §2 Quy tắc làm sạch | B |
| **CK-2.12** | **Tích hợp dữ liệu — gộp đúng chuẩn** | `merge_cities()` dùng `pd.concat` + `pd.Categorical(categories=CITIES)` + `sort_values([City,Date])`; giữ tất cả ngày mỗi TP (không cắt khoảng chung ở bước này); schema đồng nhất 40 cột; bỏ Xylene ở cả 8 TP. Kiểm: 10 `assert` trong `01_cleaning` pass (số dòng khớp raw, không trùng khoá, không còn Xylene, `assert_frame_equal` khi dựng lại) | `src/pipeline.py:merge_cities`, `notebooks/01_cleaning.ipynb` Bước 5–6 | B |
| **CK-2.13** | **Bỏ cột có thiếu ≥60% khỏi mô hình** | Quy ước `dung_lam_bien_mo_hinh=True` khi thiếu <60%; 3 cột vi phạm: PM10 Lucknow 100%, PM10 Chennai 84.5%, NH3 Gurugram 92.9%. Kiểm: `cleaning_summary_8cities.csv` cột `dung_lam_bien_mo_hinh` có đúng 3 dòng False ở 3 cặp trên | `reports/cleaning_summary_8cities.csv`, `Data_dictionary.md` §2 | K |
| **CK-2.14** | **Có nhật ký làm sạch đo được** | `cleaning_log_8cities.md` có ≥17 bước với bảng `Phát hiện | Hành động | Ảnh hưởng | Lý do & kiểm chứng`; `cleaning_summary_8cities.csv` có đủ cột `n_days, n_missing_before/after, n_flatline_to_nan, n_imputed, pct_missing_final`. Kiểm: `wc -l reports/cleaning_summary_8cities.csv` == 105 (8 TP ×13 cột incl. Xylene/AQI + header) và `grep -c "Bước" reports/cleaning_log_8cities.md` ≥10 | `reports/cleaning_log_8cities.md`, `reports/cleaning_summary_8cities.csv` | K |
| **CK-2.15** | **Thời tiết — gộp theo ngày đúng múi giờ** | Open-Meteo API `timezone=Asia/Kolkata`; gộp 24 giờ→1 ngày (mean/min/max/sum); hướng gió 360°→ `wind_u/wind_v` (tránh lỗi 359°≈1°); mưa skew 7.1 giữ nguyên + cờ `rain_day`. Kiểm: `data/processed/weather_daily_8cities.csv` 16.128 dòng (8×2016 ngày), mỗi ngày đủ 24 giờ; `air_quality_8cities_weather.csv` 14.056×54, 0 dòng thiếu thời tiết | `src/weather_utils.py:hourly_to_daily`, `notebooks/04_weather_merge.ipynb` | K |

**Ngưỡng đạt P2 (2.5đ):**
- **Yếu (<50%):** FAIL ≥1 trong CK-2.1→2.4 hoặc CK-2.5→2.12 → mã lỗi hoặc không tái tạo được.
- **Trung bình (50–69%):** PASS 8/12 B (thu thập đủ, làm sạch cơ bản nhưng thiếu cờ hoặc thiếu assert).
- **Khá (70–84%):** PASS 10/12 B + có handling cho flatline, interpolation, outlier.
- **Giỏi (85–100%):** PASS 12/12 B + CK-2.13→2.15 PASS + chạy lại `01_cleaning` từ raw ra **khớp từng ô** (`assert_frame_equal`).

**Lệnh kiểm nhanh P2:**
```bash
python -c "import pandas as pd; m=pd.read_csv('Air-Project-main/data/processed/air_quality_8cities.csv', parse_dates=['Date']); assert m.shape==(14056,40); assert m.duplicated(['City','Date']).sum()==0; print('P2 shape OK')"
ls Air-Project-main/data/raw/weather/openmeteo_*_hourly.csv.gz | wc -l  # expect 8
ls Air-Project-main/reports/suspect_points_8cities.csv Air-Project-main/reports/cleaning_summary_8cities.csv
```

---

## 4. P3 — EDA, TRỰC QUAN & MÔ HÌNH (3.5đ — 35%)

> **Mục tiêu đo:** Mỗi phát hiện phải gắn 1 biểu đồ có tiêu đề kết luận + nguồn + cỡ mẫu; mỗi mô hình phải có baseline + chia theo thời gian + báo cáo metric.

### 4.1 EDA & Trực quan — Data Storytelling (CLO3)

| ID | Tiêu chí | Đo được = PASS khi | Bằng chứng | Mức |
|---|---|---|---|---|
| **CK-3.1** | **Thống kê mô tả 4 họ (W6) theo khoảng chung** | Bảng `four_families()` cho AQI trong `win` (14/06/2017–01/07/2020): đủ `n, mean, median, std, iqr, skew, spearman_PM2.5` cho 8 TP. Kiểm: `notebooks/03_eda.ipynb` có bảng A1 với 8 dòng ×7 cột, sắp theo median giảm dần (Delhi 205 → Bengaluru 81) | `src/eda_utils.py:four_families`, `notebooks/03_eda.ipynb` §A1 | B |
| **CK-3.2** | **Phân tích chuỗi thời gian — mùa & giờ trong ngày** | (Theo đề bài gốc: *trực quan mức độ ô nhiễm theo mùa, theo khung giờ*). Với dữ liệu **ngày**: có heatmap City×Month (AQI trung vị) + biểu đồ trend City×Year (chỉ tháng 1–6 để tránh lệch mùa). Kiểm: `reports/figures/eda_02_heatmap_city_month.png` và `eda_03_trend_city_year.png` tồn tại; với dữ liệu giờ (nếu có) có biểu đồ theo khung giờ 0–23 | `notebooks/03_eda.ipynb` §B1–B2, `reports/figures/eda_*.png` | B |
| **CK-3.3** | **5 biểu đồ EDA đạt chuẩn W7 (tick trước khi push)** | Mỗi biểu đồ có: (1) tiêu đề là **kết luận có con số** (không phải “AQI theo TP”), (2) trục có nhãn+đơn vị, (3) cột bắt đầu từ 0, sắp theo giá trị, (4) 1 màu nhấn + còn lại trung tính, (5) nhãn trực tiếp (bỏ legend nếu 1 nhóm), (6) cỡ mẫu + ngày + nguồn ở footer (`provenance()`), (7) không dùng tròn/3D/trục kép. Kiểm: 6 file `eda_00_sample_size.png` → `eda_05_aqi_distribution.png` tồn tại và mỗi file <500KB, dpi 150 | `src/eda_utils.py:finish_chart/provenance/save_fig`, `notebooks/03_eda.ipynb` §Chuẩn biểu đồ W7 | B |
| **CK-3.4** | **Phát hiện “Ở đâu” (A) có số + confounder + hạn chế** | Bảng Phát hiện Phần A: Delhi 51.0%, Lucknow 46.4%, Gurugram 46.3% vs Amritsar 11.4%, Jaipur 11.1% vs Chennai 3.1%, Bengaluru 0.2% (gấp 4–4.6×); nêu confounder (vị trí trạm, quy mô đô thị) + hạn chế (khoảng chung 3 năm, COVID từ 03/2020). Kiểm: có bảng 3 cột `Phát hiện | Biểu đồ | Confounder | Hạn chế` ≥3 dòng | `notebooks/03_eda.ipynb` §Phát hiện A, B, C | B |
| **CK-3.5** | **Phát hiện “Khi nào” (B) — mùa & xu hướng năm** | B1: trung vị tháng 11–12 cao nhất, 7–9 thấp nhất (ví dụ Delhi 376 tháng 12 vs 98 tháng 8; Amritsar 76% ngày nặng rơi vào 10–12). B2: so năm chỉ dùng tháng 1–6 + bảng `n_tbl` để loại ô thưa (Jaipur 2017 chỉ 11 ngày). Kiểm: heatmap + trend chart + bảng `n_tbl` tồn tại | `notebooks/03_eda.ipynb` §B0–B3, `reports/figures/aqi_season_lucknow_jaipur.png` | B |
| **CK-3.6** | **Phát hiện “Chất nào” (C) — tương quan & tỉ lệ** | C0: Spearman PM2.5–AQI 0.91 vs NO2 0.52, CO 0.48 (ghi chú AQI tính từ max chỉ số con → tương quan cao một phần do công thức). C1: PM2.5 trung vị ngày nặng gấp 2.1–3.1× ngày thường (trung vị 5 TP =2.8×, 137 vs 42 µg/m³); chỉ xét TP có ≥100 ngày nặng. Kiểm: bảng C0 + C1 + biểu đồ `eda_04_pm25_aqi.png` | `notebooks/03_eda.ipynb` §C0–C2 | B |
| **CK-3.7** | **Kiểm tra độ nhạy & cỡ mẫu** | (a) `eda_00_sample_size.png`: 8 TP đủ dòng (1.029–1.111/1.114 ngày chung). (b) Bỏ ngẫu nhiên 10% dòng ×200 lần, kiểm thứ hạng: 3 cặp hay đổi chỗ (Lucknow↔Gurugram, Amritsar↔Jaipur, Bengaluru↔Hyderabad) → kết luận chia nhóm thay vì xếp hạng. Kiểm: notebook có đoạn `bootstrap sensitivity` với `n_iter=200` | `notebooks/03_eda.ipynb` §Kiểm tra độ nhạy | K |
| **CK-3.8** | **Tương quan thời tiết–AQI đã khử mùa** | `05_weather_correlation.ipynb`: (1) So tương quan thô vs sau khi bỏ chu kỳ mùa (anomaly `*_a` = giá trị – median City×Month), (2) 3 giả thuyết nêu trước + Bonferroni cho 3 tests (gió yếu/lớp biên thấp/không mưa → AQI cao hơn), (3) Độ ẩm (khám phá) với `humidity_deciles` + `poor_share_by_humidity`. Kiểm: 4 file `corr_01_raw_vs_adjusted.png` → `corr_04_poor_share_by_humidity.png` + bảng `corr_table` với bootstrap theo khối 14 ngày + FDR | `src/corr_utils.py:add_anomalies/spearman_by_city/boot_corr`, `notebooks/05_weather_correlation.ipynb` | K |

### 4.2 Feature Engineering & Mô hình hoá (CLO3 — Scikit-learn)

| ID | Tiêu chí | Đo được = PASS khi | Bằng chứng | Mức |
|---|---|---|---|---|
| **CK-3.9** | **Yêu cầu đề bài: Hồi quy PM2.5 từ CO, NO2 (và các khí khác)** | Có mô hình hồi quy với `y = PM2.5` (hoặc AQI) và `X` chứa CO, NO2 (và NO, NOx, SO2, O3, Benzene, Toluene). Báo cáo hệ số/hồi quy + R²/MAE/RMSE. Kiểm: `src/model_utils.py` hoặc notebook có `Ridge`/`LinearRegression` với `POLL_FEATS` chứa `no2_0, co_0` và `feat_label` ghi rõ | `src/model_utils.py: POLL_FEATS`, `notebooks/06_predict_aqi.ipynb` § feature levels | B |
| **CK-3.10** | **Chia train/test theo thời gian (không random)** | `TRAIN_END=2019-06-30`, `TEST_START=2019-07-01`, `TEST_END=2020-02-29`, `LOCK_START=2020-03-01` (COVID tách riêng). `TimeSeriesSplit(n_splits=4, gap=16)`. Mọi `fit` chỉ trên train. Kiểm: `src/model_utils.py` có `TRAIN_END/TEST_START/LOCK_START/TS_SPLITS/GAP_ROWS` và không có `train_test_split(shuffle=True)` cho phần chính | `src/model_utils.py`, `notebooks/06_predict_aqi.ipynb` § split | B |
| **CK-3.11** | **3 baseline trước mô hình chính** | Baseline: (1) Trung bình theo TP, (2) Trung vị cùng tháng (khí hậu), (3) “Ngày mai = hôm nay” (persistence). Mô hình chính phải thắng baseline trên MAE/R² (test). Kiểm: `model_utils.py:baseline_preds` + notebook có bảng so `MAE_by_model` | `src/model_utils.py:baseline_preds/r2`, `reports/figures/model_02_mae_by_model.png` | B |
| **CK-3.12** | **3 mức đặc trưng (L1→L3) + Ridge + cây để so sánh** | L1: chỉ AQI quá khứ (`aqi_0,1,2,wk` + `doy_sin/cos`), L2: + chất ô nhiễm (`pm25_0,no2_0,co_0,so2_0,o3_0`), L3: + thời tiết đến hôm nay (`temp_mean, humidity_mean, wind_speed_mean, wind_u/v, blh_mean, precip_log, pressure_dev`). Mô hình chính Ridge (tuyến tính, diễn giải hệ số) + so `HistGradientBoostingRegressor`. Kiểm: `src/model_utils.py: LEVELS/L1/L2/L3` + `LEVEL_NAME` + `make_features()` | `src/model_utils.py`, `notebooks/06_predict_aqi.ipynb` | B |
| **CK-3.13** | **Chặn rò rỉ dữ liệu (leakage)** | (1) Ô đã nội suy (`_was_missing=True`) bị đặt lại NaN khi làm feature → điền lùi tối đa 2 ngày (chỉ quá khứ), còn thiếu điền median train trong Pipeline. (2) Scaler/Imputer/Encoder fit **chỉ** trên train (`ColumnTransformer` trong `Pipeline`). (3) Kiểm tra rò rỉ bằng `as_of` (cắt dữ liệu sau 1 ngày, so feature của ngày đó giữa bản cắt vs đầy đủ — phải giống hệt). Kiểm: `model_utils.py:make_features(mask_interp=True, as_of=...)` + `build_dataset` | `src/model_utils.py`, `notebooks/06_predict_aqi.ipynb` § leak check | B |
| **CK-3.14** | **Đánh giá đa metric + chẩn đoán phần dư** | Báo cáo: MAE, R² (hồi quy) + Precision/Recall cho cảnh báo AQI≥201. Có `model_01_residual_diagnostics.png` (phần dư vs dự đoán, QQ-plot) + `model_05_humidity_recheck.png`. Kiểm: 5 file `model_01`→`model_05` tồn tại; notebook có `r2()/baseline_preds()` | `reports/figures/model_*.png`, `src/model_utils.py` | B |
| **CK-3.15** | **Bootstrap theo khối + kiểm tra độ nhạy** | (1) Bootstrap theo khối 14 ngày (`block_id`) cho CI của hiệu ứng/median diff. (2) Kiểm tra độ nhạy: bỏ `_was_missing`, đổi ngưỡng 14 ngày, đổi L1/L2/L3. Kiểm: `corr_utils.py:block_id/boot_median_diff/boot_corr`, `model_utils.py:block_id` + notebook có đoạn sensitivity | `src/corr_utils.py`, `src/model_utils.py`, `notebooks/05_06` § sensitivity | K |
| **CK-3.16** | **Tránh “cận trên giả” (thời tiết ngày mai)** | Mô hình chính chỉ dùng thời tiết đến hết hôm nay; nếu thử thời tiết ngày mai thì gắn nhãn rõ **“Cận trên: dự báo hoàn hảo”** (L4). Ghi chú: Delhi/Gurugram thời tiết trùng 0.95–0.999 nên không coi là 2 quan sát độc lập. Kiểm: `LEVELS["L4"]` có `_next` + `LEVEL_NAME["L4"]` chứa “Cận trên” | `src/model_utils.py: LEVELS/L4`, `Data_dictionary.md` §3 (hạn chế 12) | K |

**Ngưỡng đạt P3 (3.5đ):**
- **Yếu:** Thiếu CK-3.1→3.3 (không có thống kê/biểu đồ) hoặc CK-3.9→3.10 (không có hồi quy/chia sai).
- **Trung bình:** PASS 6/8 B (có EDA cơ bản + mô hình chạy nhưng biểu đồ chưa đủ chuẩn).
- **Khá:** PASS 8/8 B + model thắng baseline (MAE thấp hơn persistence).
- **Giỏi:** PASS 8/8 B + CK-3.7/3.8 + CK-3.15/3.16 + mỗi phát hiện có biểu đồ + confounder + hạn chế.

**Lệnh kiểm nhanh P3:**
```bash
ls Air-Project-main/reports/figures/eda_*.png Air-Project-main/reports/figures/corr_*.png Air-Project-main/reports/figures/model_*.png | wc -l  # expect 6+4+5=15
python -c "import pandas as pd; d=pd.read_csv('Air-Project-main/data/processed/air_quality_8cities.csv'); print(d.shape, d.City.unique())"
jupyter nbconvert --to notebook --execute Air-Project-main/notebooks/03_eda.ipynb --output /tmp/test_eda.ipynb  # smoke test
```

---

## 5. P4 — ĐẠO ĐỨC DỮ LIỆU & BÁO CÁO (1.0đ — 10%)

> **Mục tiêu đo:** Báo cáo không vi phạm liêm chính; mọi hạn chế/thiên kiến được nêu trung thực; trích dẫn đầy đủ.

| ID | Tiêu chí | Đo được = PASS khi | Bằng chứng | Mức |
|---|---|---|---|---|
| **CK-4.1** | **Báo cáo đúng cấu trúc đề cương (7 mục)** | Báo cáo có đủ: 1. Giới thiệu chung (lý do, mục tiêu, ý nghĩa) 2. Phân tích bài toán (a thu thập, b làm sạch, c EDA, d mô hình, e đạo đức) 3. Kết quả (a sản phẩm/giao diện, b hạn chế, c hướng phát triển) + Tài liệu tham khảo. Kiểm: `grep -c "^## \|^# \|^1\.\|^2\.\|^3\."` báo cáo ≥7 section | File báo cáo PDF/MD (ví dụ `reports/BAO_CAO.md` hoặc `reports/`) | B |
| **CK-4.2** | **Hình thức: không lỗi chính tả, định dạng nhất quán** | Dùng template CMC (font, heading, đánh số hình/bảng, header/footer), mục lục tự động, số trang, caption cho mỗi hình/bảng (ví dụ “Hình 1: …”). Kiểm: chạy `aspell` hoặc đọc soát 1 lượt; 0 lỗi chính tả ở tóm tắt + kết luận | File báo cáo | B |
| **CK-4.3** | **Trích dẫn nguồn & AI minh bạch** | (1) CPCB/Kaggle + Open-Meteo CC BY 4.0 được trích đúng (tác giả, năm, URL, giấy phép) ở footer mỗi biểu đồ (`provenance()`). (2) Khai báo sử dụng AI (nếu dùng ChatGPT/Copilot để viết code/văn): ghi rõ *phần nào do AI hỗ trợ, đã kiểm chứng thế nào*. Kiểm: `grep -i "open-meteo\|cpcb\|kaggle\|weather data by" reports/cleaning_log_8cities.md` ≥2 và có đoạn “AI” hoặc “trích dẫn” | `Data_dictionary.md`, `Metadata.json`, `reports/cleaning_log_8cities.md`, footer biểu đồ | B |
| **CK-4.4** | **Bảo mật & quyền riêng tư — đánh giá rủi ro** | Nêu rõ: dữ liệu CPCB là **tổng hợp công khai theo thành phố/ngày** (không có PII); không cần ẩn danh hoá dòng người; thời tiết là dữ liệu mô hình lưới 0.25°. Nếu có dữ liệu nhạy cảm giả định, mô tả biện pháp ẩn danh/khử định danh. Kiểm: có đoạn “Bảo mật/Quyền riêng tư” ≥50 từ trong báo cáo Chương 2e | Báo cáo §2e, `Data_dictionary.md` §3 Known limitations | B |
| **CK-4.5** | **Thiên kiến (bias) & công bằng — nêu ≥3 bias** | Liệt kê ≥3 bias: (1) Bias chọn mẫu: 8 TP được chọn vì độ phủ AQI cao → không đại diện 26 TP; (2) Bias thời gian: chuỗi dài ngắn khác nhau, 2020 có lockdown; (3) Bias đo lường: PM10 thiếu 100% Lucknow, thời tiết ERA5 không phải đo tại trạm, दिल्ली/Gurugram trùng nhau; (4) Bias nhãn: AQI_Bucket lệch nếu AQI nội suy (đã không nội suy). Mỗi bias có *tác động tới kết luận* + *cách giảm thiểu*. Kiểm: có bảng `Bias | Tác động | Giảm thiểu` ≥3 dòng | Báo cáo §2e, `reports/cleaning_log_8cities.md` §3 Hạn chế (15 dòng) | B |
| **CK-4.6** | **AI có trách nhiệm — không bịa số, không rò rỉ tương lai** | Cam kết: không bịa số cho khoảng thiếu >14 ngày (giữ NaN), không dùng tương lai khi dự đoán (mask_interp + as_of check), không coi tương quan là nhân quả (dùng “có liên quan”). Mỗi biểu đồ/kết luận có *hạn chế* đi kèm. Kiểm: `grep -i "không kết luận.*nguyên nhân\|có liên quan\|chỉ nói.*liên quan" notebooks/03_eda.ipynb` ≥2 | `notebooks/03_eda.ipynb` (cảnh báo B, C), `notebooks/05_weather_correlation.ipynb` (thô vs khử mùa), `notebooks/06_predict_aqi.ipynb` (leak) | K |
| **CK-4.7** | **Tái tạo được (reproducibility)** | `Requirements.txt` liệt kê đủ version (pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, statsmodels, jupyter, requests); `README.md` có lệnh cài + thứ tự chạy 01→06; mỗi notebook chạy `Restart & Run All` từ thư mục `notebooks/` không lỗi. Kiểm: `pip install -r Requirements.txt` + `jupyter nbconvert --execute` pass cho 01,03,04 | `Requirements.txt`, `README.md` §4 Hướng dẫn | K |

**Ngưỡng đạt P4:**
- **Yếu:** Sai kết cấu/định dạng, thiếu trích dẫn, hoặc vi phạm liêm chính (bịa số, không ghi nguồn).
- **Trung bình:** Đúng kết cấu, còn 1–2 lỗi trình bày, trích dẫn cơ bản đủ.
- **Khá:** Đúng định dạng, ≤2 lỗi chính tả, trích dẫn AI/nguồn đầy đủ.
- **Giỏi:** Chuẩn cấu trúc, trình bày đẹp mạch lạc, 0 lỗi chính tả, trích dẫn Gold + AI minh bạch.

---

## 6. P5 — VẤN ĐÁP & BẢO VỆ (2.0đ — 20%)

> **Mục tiêu đo:** Mỗi thành viên trả lời được ≥80% câu hỏi bảo vệ; demo sống pipeline chạy từ raw → figure trong <5 phút.

### 6.1 Bộ câu hỏi vấn đáp đã công bố (W8) — phải trả lời được

| ID | Câu hỏi | Đo được = PASS khi trả lời đúng | Bằng chứng chuẩn bị |
|---|---|---|---|
| **CK-5.1** | **Vì sao xử lý missing theo cách đó? (flatline→NaN, nội suy ≤14 ngày, AQI không nội suy)** | Giải thích: flatline 0 ≥3 ngày là cảm biến treo (2069 ngày, ví dụ Bengaluru NOx 0 suốt 207 ngày); nội suy >14 ngày là bịa số (đã sửa lỗi pandas `limit=14`); AQI là biến kết quả — điền là tạo kết quả giả. Kiểm miệng: nêu được 2 con số + chỉ vào `reports/cleaning_summary_8cities.csv` | `reports/cleaning_log_8cities.md` Bước 1–5, `src/utils.py` |
| **CK-5.2** | **Cơ chế thiếu của cột X (MAR/MCAR/MNAR)? Bằng chứng?** | Phân biệt: Xylene thiếu 100% 4/8 TP → MNAR (cảm biến chưa lắp); PM10 Lucknow 100% → MNAR; NH3 Gurugram 92.9% khối lớn → MAR theo thời gian (Date). Bằng chứng: `block_ratio` trong `diagnose_missing()` + biểu đồ `missing_pattern_*`. Trả lời đúng ≥2 cột | `src/utils.py:diagnose_missing`, `notebooks/02_cleaning_evidence.ipynb`, `reports/cleaning_log` Bước 4 |
| **CK-5.3** | **Nếu xoá ngẫu nhiên 10% dòng, kết luận có đổi không?** | Trả lời: thứ hạng theo % ngày nặng **đổi** ở 3 cặp gần nhau (Lucknow↔Gurugram 46.4 vs 46.3, Amritsar↔Jaipur 11.4 vs 11.1) nên báo cáo **chia nhóm** thay vì xếp hạng 1–8. Kiểm: chạy lại bootstrap 200 lần. Trả lời đúng có kèm con số | `notebooks/03_eda.ipynb` §Kiểm tra độ nhạy | 
| **CK-5.4** | **Biểu đồ này có thể đánh lừa người đọc vội ở chỗ nào?** | Chỉ ra ≥2 rủi ro: (1) trục không từ 0 phóng đại chênh lệch, (2) gộp 8 TP trộn lẫn khác biệt TP, (3) PM2.5–AQI 0.91 một phần do cách tính AQI (max chỉ số con), (4) 2020 thấp hơn 2019 bị nhầm là do lockdown trong khi mùa + xu hướng cũng góp phần. Trả lời đúng ≥2 | `notebooks/03_eda.ipynb` Lưu ý A/B/C, `notebooks/05` § thô vs khử mùa |
| **CK-5.5** | **Confounder hợp lý cho quan hệ vừa mô tả là gì? (câu quyết định điểm diễn giải)** | Nêu ≥1 confounder cho mỗi phát hiện: A (vị trí trạm, quy mô đô thị), B (thời tiết mùa đông: gió yếu, BLH thấp, đốt rơm rạ/Diwali), C (AQI lấy max → PM2.5 cao là hệ quả công thức). Trả lời đúng ≥2 | `notebooks/03_eda.ipynb` Phát hiện A/B/C (cột Confounder) |
| **CK-5.6** | **Câu hỏi riêng đề tài: vì sao khoảng chung? ngưỡng 201? tháng 1–6 khi so năm? PM10/NH3 không dùng?** | (1) Khoảng chung 14/06/2017–01/07/2020 để so giữa TP (chuỗi dài ngắn khác nhau). (2) 201 = ngưỡng Poor CPCB. (3) So năm chỉ tháng 1–6 để tránh lệch mùa + loại 2020 H2 (lockdown). (4) PM10/NH3 thiếu ≥60% → không dùng làm biến. Trả lời đúng ≥3/4 | `src/eda_utils.py: POOR_AQI, load(win)`, `Data_dictionary.md` §2 |

### 6.2 Kỹ năng trình bày & bảo vệ

| ID | Tiêu chí | Đo được = PASS khi | Mức |
|---|---|---|---|
| **CK-5.7** | **Nói rõ, tự tin, đúng thuật ngữ CSDL** | Dùng đúng: interpolation, flatline, IQR, MAR/MCAR, Spearman, leakage, TimeSeriesSplit, MAE/R², bootstrap theo khối, Bonferroni/FDR. Không nói “làm sạch cho đẹp” mà nói “đặt NaN, giữ cờ, nội suy ≤14 ngày”. Kiểm: giám khảo tick ≥8/10 thuật ngữ | B |
| **CK-5.8** | **Data Storytelling — mỗi ý gắn 1 biểu đồ** | 5 phát hiện chính (P1.2.1) mỗi ý có 1 biểu đồ minh hoạ + tiêu đề kết luận có số + nguồn + cỡ mẫu. Không đọc slide mà kể chuyện: “Ở đâu → Khi nào → Do chất nào → Liên quan thời tiết → Dự đoán được không”. Kiểm: slide/báo cáo có ≥5 hình với tiêu đề kết luận | B |
| **CK-5.9** | **Demo sống — pipeline chạy <5 phút** | Mở `notebooks/01_cleaning.ipynb` → `Kernel → Restart & Run All` → ra `air_quality_8cities.csv` 14.056×40 + 10 assert pass trước mặt hội đồng. Hoặc `python -c "from src.pipeline import clean_city; ..."` Kiểm: demo không lỗi, đúng số dòng | K |
| **CK-5.10** | **Giải thích mã nguồn & lựa chọn thuật toán** | Mở `src/pipeline.py`/`model_utils.py` giải thích tại chỗ: vì sao Ridge (diễn giải hệ số) trước HistGBR, vì sao log(1+x) cho PM2.5/precip, vì sao không dùng thời tiết ngày mai. Trả lời đúng ≥2/3 câu hỏi code | B |

**Ngưỡng đạt P5:**
- **Yếu:** Nói nhỏ/không tự tin, không trả lời được câu cơ bản (CK-5.1, 5.7 FAIL).
- **Trung bình:** Trả lời được 1/2 câu, còn ngập ngừng, sai thuật ngữ.
- **Khá:** Trả lời đúng 2/3 câu, nói rõ, đúng thuật ngữ, có storytelling.
- **Giỏi:** Trả lời đúng **tất cả** 6 câu W8 + demo sống + giải thích được hạn chế/nghiệp vụ.

---

## 7. Tổng hợp điểm & ngưỡng

| Phần | Điểm | Số B | Số K | Công thức tính điểm Phần |
|---|---|---|---|---|
| P1 Tổng quan | 1.0 | 4 | 2 | `điểm = 1.0 × (PASS_B/4) × (0.8 + 0.2×PASS_K/2)`; FAIL 1 B → tối đa 0.4 |
| P2 Thu thập & Tiền xử lý | 2.5 | 12 | 3 | `2.5 × (PASS_B/12) × (0.85 + 0.15×PASS_K/3)`; FAIL P2 → P3 không tính |
| P3 EDA & Mô hình | 3.5 | 8 | 4 | `3.5 × (PASS_B/8) × (0.85 + 0.15×PASS_K/4)`; model phải thắng baseline |
| P4 Đạo đức & Báo cáo | 1.0 | 5 | 2 | `1.0 × (PASS_B/5) × (0.8 + 0.2×PASS_K/2)` |
| P5 Vấn đáp | 2.0 | 4* | 6* | `2.0 × (câu trả lời đúng /6) × hệ số trình bày (0.7–1.0)` |
| **TỔNG** | **10.0** | **33** | **17** | **Giỏi khi tổng ≥8.5 và không có Phần nào Yếu** |

> **Quy tắc làm tròn:** Điểm từng Phần làm tròn 0.1; tổng làm tròn 0.1 theo quy định CMC.

---

## 8. Traceability — Từ yêu cầu đề cương → Checklist → File

| Yêu cầu đề cương | Checklist ID | File kiểm chứng | Lệnh kiểm tự động |
|---|---|---|---|
| Lý do chọn đề tài, vòng đời | CK-1.1, 1.2 | `README.md`, `Metadata.json` | `grep -c "CPCB" README.md` |
| Nguồn: CSV/JSON/SQL/API/Scraping | CK-2.1→2.4 | `Metadata.json`, `src/weather_utils.py` | `ls data/raw/weather/*.gz \| wc -l` |
| Làm sạch: khuyết, nhiễu, outliers | CK-2.5→2.10 | `src/utils.py`, `src/pipeline.py` | `python -m py_compile src/*.py` |
| Chuẩn hoá, biến đổi, tích hợp Pandas | CK-2.11→2.13 | `src/pipeline.py:merge_cities` | `pd.read_csv(...).shape == (14056,40)` |
| Thống kê mô tả, Matplotlib/Seaborn, Storytelling | CK-3.1→3.8 | `src/eda_utils.py`, `reports/figures/eda_*.png` | `ls reports/figures/eda_*.png \| wc -l` == 6 |
| Feature Engineering, Scikit-learn Hồi quy/Phân loại | CK-3.9→3.16 | `src/model_utils.py`, `reports/figures/model_*.png` | `grep -c "Ridge\|HistGradient" src/model_utils.py` ≥2 |
| Đạo đức, bảo mật, bias, AI có trách nhiệm | CK-4.1→4.7 | `reports/cleaning_log_8cities.md` §3, báo cáo §2e | `grep -c "Bias\|bias" báo_cáo.md` ≥3 |
| Vấn đáp: mã nguồn, thuật toán, đánh giá | CK-5.1→5.10 | Toàn repo + demo | `jupyter nbconvert --execute` pass |

---

## 9. Hướng dẫn vận hành — Ai làm gì, khi nào

| Giai đoạn | Người phụ trách | Checklist phải PASS trước khi sang bước sau |
|---|---|---|
| **Thu thập** (Tuần 1) | Nhóm trưởng | CK-2.1→2.4 (có raw + weather + Metadata) |
| **Làm sạch** (Tuần 2) | 2 thành viên, mỗi người 4 TP | CK-2.5→2.12 + 10 assert trong `01_cleaning` |
| **EDA** (Tuần 3) | 2 thành viên Phần A/B + C | CK-3.1→3.8 + CK-4.3 (trích dẫn) |
| **Mô hình** (Tuần 4) | 1–2 thành viên | CK-3.9→3.16 + CK-4.6 (không rò rỉ) |
| **Báo cáo** (Tuần 5) | Cả nhóm | CK-4.1→4.7 + CK-1.1→1.6 |
| **Luyện vấn đáp** (Tuần 5–6) | Cả nhóm, mỗi người phải trả lời được 6 câu | CK-5.1→5.10 |

**Gate cứng (không PASS không được nộp):**
1. `01_cleaning.ipynb` chạy `Restart & Run All` không lỗi assert.
2. `air_quality_8cities.csv` = 14.056 dòng, 40 cột, 0 trùng (City,Date).
3. Mỗi phát hiện trong báo cáo có 1 biểu đồ + 1 confounder + 1 hạn chế.
4. File báo cáo có mục Đạo đức + trích dẫn CPCB & Open-Meteo + khai báo AI.

---

## 10. Phụ lục — Từ điển ngưỡng & lệnh kiểm nhanh

### A. Ngưỡng số học đã chốt cho đồ án này

| Tham số | Giá trị | Lý do | Checklist |
|---|---|---|---|
| Flatline 0 → NaN | ≥3 ngày liên tiếp | Cảm biến treo, đổi 2/5/7 ngày chỉ lệch ±15% | CK-2.5 |
| Nội suy tối đa | ≤14 ngày | Vượt là bịa số cho khối dài; đã sửa lỗi `limit=14` của pandas | CK-2.6 |
| Cột bỏ khỏi mô hình | thiếu ≥60% | PM10 Lucknow 100%, Chennai 84.5%, NH3 Gurugram 92.9% | CK-2.13 |
| Outlier | IQR ×1.5 **theo tháng** | Tránh gắn nhầm đỉnh mùa đông thành outlier | CK-2.8 |
| AQI nặng | ≥201 (Poor) | Thang CPCB, dùng chung cho cả nhóm | CK-3.1 |
| Khoảng chung | 14/06/2017–01/07/2020 | Ngày muộn nhất mọi TP đều có dữ liệu → ngày sớm nhất có TP hết dữ liệu | CK-3.1 |
| Chia train/test | train ≤30/06/2019, test 01/07/2019–29/02/2020 | Giữ trọn 1 mùa đông trong test; tách COVID từ 01/03/2020 | CK-3.10 |
| Bootstrap khối | 14 ngày | Ngày kề nhau không độc lập | CK-3.15 |
| Bonferroni | α=0.05/3 | 3 giả thuyết nêu trước | CK-3.8 |

### B. Lệnh kiểm nhanh toàn dây chuyền (copy-paste)

```bash
# P1: metadata + readme
cat Air-Project-main/Metadata.json | python -m json.tool | head -n 30
grep -c "CPCB\|Kaggle" Air-Project-main/README.md

# P2: raw → processed
ls -lh Air-Project-main/data/raw/city_day.csv Air-Project-main/data/raw/weather/*.gz
python -c "import pandas as pd; m=pd.read_csv('Air-Project-main/data/processed/air_quality_8cities.csv'); print(m.shape); assert m.shape==(14056,40); print('OK')"
cat Air-Project-main/reports/cleaning_summary_8cities.csv | wc -l
cat Air-Project-main/reports/suspect_points_8cities.csv | wc -l

# P3: figures
ls Air-Project-main/reports/figures/*.png | wc -l
ls Air-Project-main/reports/figures/eda_*.png Air-Project-main/reports/figures/corr_*.png Air-Project-main/reports/figures/model_*.png

# P4: báo cáo
ls Air-Project-main/reports/*.md Air-Project-main/reports/*.csv
grep -i "open-meteo\|CC BY" Air-Project-main/Data_dictionary.md | head

# P5: notebook smoke test
python -m py_compile Air-Project-main/src/*.py && echo "src/*.py OK"
```

### C. Định nghĩa “Đo được” cho giám khảo

Một tiêu chí được gọi là **đo được** khi có **công thức nhị phân**: ví dụ *“File X tồn tại và có N dòng”*, *“MAE_test < MAE_baseline”*, *“Tiêu đề chứa con số”*, *“assert pass”*. Nếu tiêu chí chỉ ghi “làm tốt”, “trình bày đẹp” mà không có ngưỡng → phải bổ sung ngưỡng (như CK-3.3 liệt kê 7 dấu hiệu của biểu đồ đạt chuẩn).

---

> **Cam kết BA:** Checklist này là *single source of truth* cho dây chuyền. Mọi thay đổi ngưỡng (ví dụ đổi 14 ngày → 60 ngày) phải được ghi vào `reports/cleaning_log_8cities.md` kèm lý do và chạy lại kiểm chứng. Không có ngoại lệ “làm cho xong”.

— *Hết checklist. In ra A4, dán lên tường phòng họp, tick từng ô trước khi nộp.*
