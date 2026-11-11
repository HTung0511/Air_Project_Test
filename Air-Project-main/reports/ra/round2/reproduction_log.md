# Nhật ký tái lập vòng 2 của DA

Phiên bản 1.0 (giai đoạn chuẩn bị) · 11/11/2026 · Người lập: AI-3 DA.

File này ghi những gì DA **đã chạy trước khi có bản sửa của Dev**: môi trường, baseline trên mã cũ, và bộ công cụ kiểm. Chưa có phép thử nào trên mã Dev. Kết quả kiểm bản sửa sẽ nằm ở [`verification_results.md`](verification_results.md).

## 1. Định danh

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Giao thức kiểm chứng | [`da_verification_protocol.md`](da_verification_protocol.md) v1.0, commit `e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61` | `git log -1 --format=%H -- Air-Project-main/reports/ra/round2/da_verification_protocol.md` | Commit lúc 17:17 UTC ngày 11/11/2026, trước mọi lần chạy trong file này. Đã có trên remote (`git ls-remote origin arena/b5aacef3-air-project-test`). |
| Mã Dev | Chưa có | `git ls-remote origin` chỉ có `main` và ba nhánh BA, RA, DA | Nhánh `arena/5cb21c04-air-project-test` chưa xuất hiện trên remote lúc viết file này. |
| Mã và dữ liệu baseline | `git archive` của `0dfc715` (bản `base`, có script DA vòng 1) và `ccd0a63` (bản `chainA`, `chainB`) | [`R2_B01_manifest_baseline.csv`](evidence/R2_B01_manifest_baseline.csv): 57 file, SHA-256 từng file | Ba tree `src`, `data`, `notebooks` giống nhau ở cả hai commit. Manifest của checkout trùng manifest của bản `base`. |
| Dữ liệu raw | `data/raw/city_day.csv`, sha256 `0d84b21c3e4878bbad8df362f2ab05f61ad959538dddf5918e714077ed3c1847` | cùng file manifest | 8 file cache thời tiết cũng nằm trong manifest. |
| Script DA vòng 2 | `reports/ra/round2/evidence/scripts/`, SHA-256 từng file trong [`R2_B08_artifact_sha256.csv`](evidence/R2_B08_artifact_sha256.csv) | cùng file | SHA commit của script là commit chứa file này; DA ghi SHA đó trong HANDOFF. |

## 2. Môi trường

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Hệ thống | Python 3.11.2, Debian 12, Linux 6.1 x86_64, 2 CPU | `python -VV`, `uname -a` | |
| Gói đã cài | 63 gói; ghim numpy 2.4.6, pandas 3.1.1, scipy 1.17.1, scikit-learn 1.9.1, statsmodels 0.15.0, matplotlib 3.11.2, seaborn 0.13.2, nbclient 0.11.0, nbformat 5.11.1, ipykernel 7.4.0, requests 2.34.2, pillow 13.0.0 | [`R2_B01_pip_freeze_venv_da.txt`](evidence/R2_B01_pip_freeze_venv_da.txt) | `pip install` exit 0; `pip check` không báo xung đột. Đây là đúng bộ phiên bản của vòng 1. |
| Khác với môi trường tác giả | Metadata notebook ghi Python 3.12.3 và 3.14.7; `Requirements.txt` không ghim phiên bản | notebook metadata; `Requirements.txt` | Chênh lệch do môi trường được báo riêng, không gộp vào ảnh hưởng của bản sửa. |
| Mạng | Không tới được `archive-api.open-meteo.com:443` | [`R2_B02_chain_io_summary.csv`](evidence/R2_B02_chain_io_summary.csv), bước `A_04_weather_merge_goc`: 10 lần thử kết nối, đều lỗi | API thật ở trạng thái ⛔ blocked trên máy DA. |
| Môi trường bản sửa (`.venv-dev`) | Chưa tạo | — | Chờ file lock của Dev. |

## 3. Lệnh đã chạy

Ký hiệu: `PY` = `/home/user/.venv-da/bin/python`; `B` = bản `base` (`…/scratch/base/Air-Project-main`); `A` = bản `chainA`; `E1` = `reports/ra/evidence` (v1.1, chỉ đọc); `OUT` = thư mục kết quả ở scratch. Các script `r2_*` chạy với thư mục làm việc là `reports/ra/round2/evidence/scripts`, biến `PYTHONDONTWRITEBYTECODE=1`.

| # | Lệnh | Exit | Thời gian | Kết quả |
|---|---|---|---|---|
| 1 | `r2_manifest.py B <out.csv> baseline_0dfc715` | 0 | dưới 1 s | 57 file |
| 2 | `r2_run_nb.sh PY A 01_cleaning.ipynb <log> A_01_cleaning noblock` | 0 | 15 s | 11/11 ô |
| 3 | như trên, `02_cleaning_evidence.ipynb` | 0 | 7 s | 12/12 ô |
| 4 | như trên, `03_eda.ipynb` | 0 | 6 s | 13/13 ô |
| 5 | như trên, `04_weather_merge.ipynb` (bản gốc, mạng không chặn) | 1 | 53 s | 3/16 ô; 10 lần thử mạng, `SSLError` |
| 6 | `make_offline_nb04.py A` (script vòng 1), rồi `r2_run_nb.sh … 04_weather_merge_offline.ipynb … block` | 1 | 3 s | 15/16 ô; ô 29 `SyntaxError` trên Python 3.11; hai file processed đã được ghi trước ô lỗi |
| 7 | `r2_run_nb.sh … 05_weather_correlation.ipynb … block` trên `A` | 0 | 15 s | 10/10 ô |
| 8 | `r2_run_nb.sh … 06_predict_aqi.ipynb … block` trên `A` | 0 | 23 s | 26/26 ô |
| 9 | bước 7 và 8 trên `chainB` (dữ liệu processed đã commit) | 0; 0 | 15 s; 23 s | 10/10; 26/26 ô |
| 10 | `compare_nb_outputs.py <notebook gốc> <notebook chạy lại> <out.csv> 0.005` × 8 (script vòng 1) | 0 | — | 8 file `R_0X_*` |
| 11 | `v02b_walkforward.py 0 2` và `1 2` chạy song song trong `B`, rồi `v02b_walkforward.py merge` | 0; 0; 0 | 919 s; 923 s; 2 s | 4 file `V07_walkforward_*` trong scratch |
| 12 | `r2_baseline.py B OUT E1` | 0 | 8 s | `R2_B03_*`, `R2_B04_*`, `R2_B05_*` |
| 13 | `r2_ref_cohort.py B/data/raw/city_day.csv OUT/R2_B03_baseline_cohort_keys.csv B/data/processed/air_quality_8cities.csv OUT` | 0 | dưới 1 s | `R2_C01…C04` |
| 14 | `r2_ba_extract.py E1 OUT` | 0 | 1 s | `R2_BA01…BA03` |
| 15 | `r2_weather_check.py B/data/raw/weather B/…/weather_daily_8cities.csv B/…/air_quality_8cities_weather.csv B/…/air_quality_8cities.csv B/…/weather_daily_8cities.csv OUT baseline_commit` | 0 | 1 s | 70/70 tiêu chí |
| 16 | như 15 với ba bảng processed của `A`, đối chiếu file đã commit, nhãn `chay_lai_offline` | 0 | 2 s | 72/72 tiêu chí |
| 17 | `r2_nb04_negative.py PY <bản sao> 04_weather_merge_offline.ipynb <work> <out.csv>` | 0 | 194 s | 1 ca đối chứng và 8 ca cache hỏng |
| 18 | `r2_ref_asof.py fixture B/data/raw/city_day.csv OUT` | 0 | 9 s | 14 ca biên, 67 hàng kỳ vọng |
| 19 | `r2_ref_asof.py ref B/data/raw/city_day.csv OUT/R2_C05_ref_asof_features.csv.gz` | 0 | 1 s | 14.056 hàng |
| 20 | `r2_ref_asof.py diff OUT/R2_C05_… OUT/R2_B03_baseline_features_L3.csv.gz OUT/R2_B03_baseline_cohort_keys.csv OUT` | 0 | dưới 1 s | `R2_C06_*` |

Sau khi script ở dạng cuối, DA chạy lại các lệnh 12–16, 19, 20 vào một thư mục tạm: 24 file CSV trùng từng byte với bản trong `evidence/`, 2 file `.gz` trùng nội dung sau giải nén. Lệnh 18 chạy hai lần cho ba file trùng từng byte.

Log: [`logs/R2_B02_run_chain.log`](evidence/logs/R2_B02_run_chain.log) (lệnh 2–9), [`logs/R2_B07_walkforward_status.log`](evidence/logs/R2_B07_walkforward_status.log) (lệnh 11).

## 4. Baseline trên mã cũ có tái lập được không

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Output notebook so với vòng 1 | 8/8 file so sánh trùng từng byte với `R_0X_*` của v1.1 | [`R2_B07_rerun_vs_v11_files.csv`](evidence/R2_B07_rerun_vs_v11_files.csv) | Cùng môi trường, cùng mã, cùng kết luận như vòng 1. |
| Walk-forward mã cũ (Q02 vòng 1) | 3 file CSV trùng từng byte; file `.gz` trùng nội dung sau giải nén | cùng file | 57/8.912 hàng có đặc trưng khác khi dựng theo thời gian thực; 64 ô; tất cả ở train. Đây là hiện trạng F01 của mã cũ. |
| Metric baseline bằng bộ tính độc lập của DA | 327/327 giá trị khớp v1.1; lệch lớn nhất 4,88e-04 | [`R2_B05_baseline_vs_v11.csv`](evidence/R2_B05_baseline_vs_v11.csv); [`R2_B04_baseline_metrics.csv`](evidence/R2_B04_baseline_metrics.csv) | Mẫu 5.741 / 1.947 / 975. MAE test: persistence 23,47; Ridge L3 19,52. Bộ tính này (`r2_protocol.py`) sẽ được dùng nguyên trạng cho mã Dev. |
| File NB05 và NB06 thật sự đọc | Chỉ `air_quality_8cities.csv` và `weather_daily_8cities.csv`; không đọc bảng gộp `air_quality_8cities_weather.csv` | [`R2_B02_chain_io_summary.csv`](evidence/R2_B02_chain_io_summary.csv) | Chuỗi `A` đọc file vừa dựng lại (sha256 `f6b033a2…`, `2c906e61…`); chuỗi `B` đọc file đã commit (`38653221…`, `45f3579a…`). Hai bộ này khác byte nhưng khớp giá trị ở 1e-9. |
| Thời tiết: cache và bảng đã commit | 70/70 tiêu chí | [`R2_W01_baseline_commit_checks.csv`](evidence/R2_W01_baseline_commit_checks.csv) | 8 × 48.384 giờ, đủ 24 giờ mỗi ngày, có BLH; bảng ngày 16.128 hàng; bảng gộp 14.056 × 54; khóa duy nhất; 40 cột chất lượng không khí trùng bảng sạch; 0 ô thời tiết thiếu. |
| Thời tiết: bảng dựng lại so với file đã commit | 852 ô khác (`temp_mean` 335, `pressure_mean` 348, `wind_speed_mean` 169); chênh lớn nhất 0,01; 0 ô vi phạm quy tắc dung sai | [`R2_W02_chay_lai_offline_daily_vs_committed.csv`](evidence/R2_W02_chay_lai_offline_daily_vs_committed.csv) | Lặp lại đúng kết quả Q04 vòng 1. Mọi ô lệch nằm đúng biên làm tròn x,xx5. |
| Thử âm tính trên NB04 cũ (bản offline của DA) | 8/8 ca cache hỏng: exit 1, không file processed nào bị ghi, không cache nào bị ghi đè. Ca đối chứng: exit 1 (15/16 ô, `SyntaxError`) | [`R2_B06_nb04_negative_baseline_offline.csv`](evidence/R2_B06_nb04_negative_baseline_offline.csv) | Ba ca (cache cụt 24 giờ cuối, đổi tên cột, cache kết thúc sớm) dừng bằng `ConnectionError` sau 5 lần thử mạng: mã cũ chuyển sang gọi API thay vì nêu lỗi của cache. |

## 5. Tham chiếu DA dựng sẵn cho bước nghiệm thu

Các bảng dưới đây là **đối chứng của DA**, không phải kết quả của mã Dev và không phải điều kiện đạt.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Tập mẫu `C_new` dựng từ raw, không dùng `src/` | 8.668 mẫu: train 5.746, test 1.947, holdout 975; ngày nặng 1.436 / 389 / 18 | [`R2_C04_raw_aqi_and_cohort_checks.csv`](evidence/R2_C04_raw_aqi_and_cohort_checks.csv); [`R2_C01_ref_cohort_keys.csv`](evidence/R2_C01_ref_cohort_keys.csv); [`R2_C02_cohort_counts_split_city_season.csv`](evidence/R2_C02_cohort_counts_split_city_season.csv) | Raw: 14.056 dòng, 0 khóa trùng, 0 ngày lịch thiếu. Trong khoảng: 174 AQI trống, 42 AQI trên 500 (lớn nhất 891, giữ nguyên). |
| `C_new` so với tập mẫu cũ | Thêm 5 khóa, bớt 0; 8.663 khóa chung có cùng nhãn, cùng AQI(t), cùng split | [`R2_C03_cohort_key_diff.csv`](evidence/R2_C03_cohort_key_diff.csv) | 5 khóa thêm đều ở train: Bengaluru 08/07/2017; Gurugram 08/07/2017 và 29/07/2017; Jaipur 05/02/2018 và 06/02/2018. Bảng sạch đã xóa AQI ở ngày t (2 khóa) hoặc ngày t+1 (3 khóa). |
| Đặc trưng "as-of t" theo cách DA đọc RA-DEC-02 | 14.056 hàng × 9 đặc trưng | [`R2_C05_ref_asof_features.csv.gz`](evidence/R2_C05_ref_asof_features.csv.gz); [`r2_ref_asof.py`](evidence/scripts/r2_ref_asof.py) | Quy tắc ghi ở đầu script. |
| Tham chiếu so với đặc trưng L3 của mã cũ, trên 8.663 khóa cũ | 63 ô khác ở 57 hàng; tất cả ở train; 0 ở test và holdout | [`R2_C06_ref_vs_baseline_feature_diff_summary.csv`](evidence/R2_C06_ref_vs_baseline_feature_diff_summary.csv); [`…_cells.csv`](evidence/R2_C06_ref_vs_baseline_feature_diff_cells.csv) | `co_0` 35 ô; `aqi_wk` 22; `aqi_2` 4; `aqi_1` 2; `pm25_0`, `no2_0`, `so2_0`, `o3_0`, `aqi_0` 0 ô. Đây là cỡ thay đổi DA dự đoán, không phải ngưỡng nghiệm thu. |
| Ca biên có kỳ vọng viết tay (T2.4) | 14 ca, 67 hàng; 67/67 khớp bản tham chiếu; 0 hàng đổi khi cắt raw ở chính ngày của hàng | [`R2_F01_fixture_expected.csv`](evidence/R2_F01_fixture_expected.csv) | Hai file raw ca biên không commit (mỗi file 2,5 MB); tạo lại bằng lệnh 18, SHA-256 trong [`R2_B08_artifact_sha256.csv`](evidence/R2_B08_artifact_sha256.csv). |

## 6. Sai khác với giao thức (mục 12 của giao thức)

| Điều khoản | Sai khác | Lý do và cách xử lý | Thời điểm |
|---|---|---|---|
| Mục 1, cách lấy baseline | Bản `base` lấy từ `0dfc715` thay vì `ccd0a63` | Cần script DA vòng 1, chỉ có từ `0dfc715`. Tree `src`, `data`, `notebooks` giống hệt. | Trước mọi kết quả. |
| Mục 9, cách chạy notebook | Lần chạy thử đầu có đặt `MPLBACKEND=Agg`; đã bỏ | Biến này làm đổi cột so sánh hình so với vòng 1. Chuỗi được chạy lại không có biến này; kết quả trong hồ sơ là của lần chạy lại. | Sau khi thấy file so sánh baseline; không liên quan mã Dev. |
| Mục 9, theo dõi I/O | Bộ tóm tắt I/O được sửa hai lỗi lọc | Bản đầu bỏ sót sự kiện của kernel và liệt kê một file giả `notebooks/<>`. Bản tóm tắt trong hồ sơ do bản đã sửa tạo ra. | Trước khi dùng kết quả I/O. |
| T1.4 | Khi so với giá trị DA tự tính, ô nằm đúng biên x,xx5 được nhận cả hai chiều làm tròn ở **cả năm** cột trung bình | Ở ô đúng biên, hai cách làm tròn đều là kết quả hợp lệ của phép tính; script không đoán được thư viện chọn chiều nào. Quy tắc ba cột của T1.5 (so với file đã commit) giữ nguyên như đã khóa. | Sau khi thấy kết quả trên dữ liệu **cũ**; trước mọi kết quả của Dev. |
| T1.5, cách nhận ô đúng biên | Dùng số học nguyên (tổng 24 giờ theo đơn vị 0,01, chia dư 24 bằng 12) thay cho điều kiện số thực `≤ 1e-6` | Chặt hơn và không phụ thuộc sai số dấu phẩy động. | Trước mọi kết quả của Dev. |
| T2.4, ca "sát ngày lịch bị thiếu" | Tách thành bộ ca biên thứ hai, có xóa 3 dòng raw | Raw thật không thiếu ngày lịch nào, nên ca này chỉ tạo được bằng cách xóa dòng. Bộ chính giữ đủ 14.056 dòng của 8 thành phố. Nếu mã Dev từ chối raw thiếu ngày một cách rõ ràng, DA báo đúng như vậy, không tính là trượt. | Trước mọi kết quả của Dev. |
| T2.4, nội dung kỳ vọng | Kỳ vọng viết theo cách DA đọc RA-DEC-02: ngày 1–2 của chuỗi 0 giữ số 0; từ ngày 3 để trống; số 0 đã mask không làm nguồn điền; đếm theo ngày lịch | Đây là diễn giải của DA. Nếu RA đọc khác, DA sửa bảng kỳ vọng bằng mục "Sửa đổi" của giao thức trước khi chạy mã Dev. | Trước mọi kết quả của Dev. |
| T1.6, ca đối chứng | Ca đối chứng (cache nguyên vẹn) của mã cũ cho exit 1 | Lỗi cú pháp Python 3.11 đã biết từ vòng 1. Với mã Dev, ca này phải exit 0. | Kết quả baseline. |

## 7. Việc chưa làm

- Mọi phép thử trên mã Dev (T1.1–T1.8, T2.1–T2.7, DA-03, DA-04): chờ SHA 40 ký tự của Dev.
- Chạy mã baseline trong môi trường bản sửa: chờ file lock của Dev.
- Chạy điểm vào của Dev trên hai file raw ca biên và trên raw bị cắt: phụ thuộc giao diện Dev công bố.

## 8. Hồ sơ vòng 1 và baseline có bị đụng tới không

`git status --short` chỉ liệt kê đường dẫn dưới `Air-Project-main/reports/ra/round2/`. `git diff --stat 0dfc715 HEAD -- Air-Project-main ':!Air-Project-main/reports/ra/round2'` rỗng. Manifest của `data/`, `src/`, `notebooks/` trong checkout sau khi làm việc trùng manifest trước khi làm việc. Mọi lần chạy notebook và script vòng 1 diễn ra trong bản sao ở scratch.
