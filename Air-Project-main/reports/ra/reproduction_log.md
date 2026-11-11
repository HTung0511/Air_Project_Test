# Nhật ký tái lập — DA → RA

Ngày 11/11/2026 · phiên bản 1.1 (đính chính truy vết commit) · người chạy: AI-3 Data Analyst
Đọc cùng [verification_results.md](verification_results.md) (kết quả từng phép kiểm) và [supplementary_analysis.md](supplementary_analysis.md) (phân tích bổ sung).
Tài liệu này chỉ ghi **cái gì đã chạy, ở đâu, ra sao**. Không có kết luận về phương pháp.

## 1. Phiên bản code và dữ liệu đầu vào

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Commit đã chạy | `ccd0a63757d862c50735a9745864c5e2ef4c3c0e`, nhánh `arena/b5aacef3-air-project-test` | `git log` | `open_questions.md` ghi đầu vào là commit `1a4f5a56…`. Đó là commit cha trực tiếp của `ccd0a63`. Lịch sử: `b8aba4b` (tác giả tải lên) → `deb8864` (checklist BA) → `1a4f5a5` (bàn giao BA→RA) → `ccd0a63` (RA). |
| Khác biệt `1a4f5a5` → `ccd0a63` | 2 file: `reports/ra/notebook_review.md`, `reports/ra/open_questions.md`; 163 dòng thêm | `git diff --stat 1a4f5a5 ccd0a63` | `src/`, `data/`, notebook không đổi. Kết quả chạy trên `ccd0a63` áp dụng cho đầu vào `1a4f5a5`. |
| Khác biệt `b8aba4b` → `ccd0a63` | 8 file tài liệu, 1.576 dòng thêm; `src/`, `data/`, notebook không đổi | `git diff --stat b8aba4b ccd0a63` | Code và dữ liệu DA chạy giống bản tác giả tải lên. |
| Đính chính so với phiên bản 1.0 | Phiên bản 1.0 ghi commit `1a4f5a56…` "không có trong repo" | `git rev-parse --is-shallow-repository` trả `true` lúc đó | Sai do bản clone nông. Đã sửa ở phiên bản 1.1 sau `git fetch --unshallow`. Xem [NEW-005](verification_results.md#NEW-005). |
| `data/raw/city_day.csv` | sha256 `0d84b21c3e4878bb…` | `sha256sum` | 29.531 dòng, 26 thành phố. Không sửa. |
| `data/processed/air_quality_8cities.csv` | `38653221fda73fed…` | như trên | Bảng sạch đã commit (baseline). |
| `data/processed/air_quality_8cities_weather.csv` | `2729117038eabafe…` | như trên | Baseline. |
| `data/processed/weather_daily_8cities.csv` | `45f3579a222c55c0…` | như trên | Baseline. |
| `reports/cleaning_summary_8cities.csv`, `suspect_points_8cities.csv` | `a66719dcc94c92bb…`, `33f5814c09c904c7…` | như trên | Baseline. |
| 8 file cache thời tiết `data/raw/weather/openmeteo_<tp>_hourly.csv.gz` | amritsar `43317b47…`, bengaluru `a3832c8e…`, chennai `6e64ca15…`, delhi `4aad409d…`, gurugram `444cba0e…`, hyderabad `482b19ce…`, jaipur `dd32d11f…`, lucknow `c9f452a4…` | [V10_weather_cache_checks.csv](evidence/V10_weather_cache_checks.csv) | Mỗi file 48.384 dòng giờ. |
| Trạng thái baseline sau khi DA chạy xong | Không file nào đã commit bị đổi | `git status --short` chỉ còn file mới trong `reports/ra/` | Mọi lần chạy lại notebook đều làm trong bản sao ngoài repo (`/home/user/scratch/`). |

## 2. Môi trường

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Hệ điều hành, phần cứng | Linux 6.1.158, 2 CPU, khoảng 3–4 GB RAM | `uname -sr`, `nproc` | Sandbox không có trình duyệt. |
| Python | 3.11.2 (venv `/home/user/.venv-da`) | `python --version` | Metadata notebook của tác giả ghi 3.12.3 (NB01–03) và 3.14.7 (NB04–06). |
| Thư viện | numpy 2.4.6, pandas 3.1.1, scipy 1.17.1, scikit-learn 1.9.1, statsmodels 0.15.0, matplotlib 3.11.2, seaborn 0.13.2, nbclient 0.11.0, nbformat 5.11.1, ipykernel 7.4.0, requests 2.34.2, pillow 13.0.0 | `pip freeze` | `Requirements.txt` không ghim phiên bản, không ghi phiên bản Python, và ghi `statsmodels` hai lần. DA không biết tác giả dùng phiên bản thư viện nào. |
| Lệnh cài | `python3 -m venv .venv-da && .venv-da/bin/pip install numpy pandas matplotlib seaborn scipy scikit-learn statsmodels nbformat nbclient ipykernel requests` | — | Cài ngày 11/11/2026, bản mới nhất lúc đó. |
| Mạng | Chỉ ra được GitHub, npm, PyPI. `archive-api.open-meteo.com:443` bị chặn (`SSL_ERROR_SYSCALL`) | `curl`, `weather_utils.smoke_test()` | Mọi bước cần gọi API Open-Meteo ghi **blocked**. |
| Seed | Mọi script DA dùng `seed=0` (`numpy.random.default_rng(0)`). Hàm của tác giả giữ seed mặc định của họ (0). Riêng V19 chạy thêm seed 0–9 để đo độ nhạy. | đầu mỗi script | Bootstrap: B = 4.000 cho mô hình và tương quan, B = 2.000 cho 15 phép so sánh (bằng mặc định của tác giả). |

## 3. Chạy lại 6 notebook

Lệnh: `python evidence/scripts/run_notebook.py <thư mục bản sao> <notebook> [timeout]`, sau đó `python evidence/scripts/compare_nb_outputs.py <gốc> <đã chạy> <csv> 0.005`.
Bản sao A (`scratch/repro`) chạy NB01 → NB06 nối tiếp, nên NB05–06 dùng dữ liệu vừa sinh lại. Bản sao B (`scratch/repro_b`) giữ dữ liệu đã commit và chỉ chạy NB05–06.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| `01_cleaning.ipynb` | ✅ exit 0, 18,3 s, 11/11 ô code | [R_01](evidence/R_01_cleaning_output_diff.csv) | 839 con số trong output khớp bản lưu. |
| `02_cleaning_evidence.ipynb` | ✅ exit 0, 11,1 s, 12/12 ô | [R_02](evidence/R_02_cleaning_evidence_output_diff.csv) | 1.761 con số khớp. |
| `03_eda.ipynb` | ✅ exit 0, 8,8 s, 13/13 ô | [R_03](evidence/R_03_eda_output_diff.csv) | 543 con số khớp. |
| `04_weather_merge.ipynb` nguyên bản | ⛔ blocked: dừng ở ô c6 (gọi API), mới chạy 3/16 ô | traceback `SSLError` | Notebook luôn thử mạng trước khi đọc cache, nên không chạy offline được nếu không sửa. |
| `04_weather_merge.ipynb` bản offline (bỏ bước thử mạng, đọc cache) | ⚠️ 15/16 ô chạy; ô code cuối (cell 29) báo `SyntaxError` trên Python 3.11 | [R_04](evidence/R_04_weather_merge_offline_output_diff.csv), `scripts/make_offline_nb04.py` | Hai file CSV thời tiết vẫn được ghi ra trước ô lỗi. Notebook gốc được commit **không có output nào**, nên không có gì để so. Xem [NEW-003](verification_results.md#NEW-003). |
| `05_weather_correlation.ipynb`, dữ liệu đã commit | ✅ exit 0, 22,5 s | [R_05 committed](evidence/R_05_weather_correlation_output_diff_committed_data.csv) | 10/10 ô khớp, 314 con số. |
| `06_predict_aqi.ipynb`, dữ liệu đã commit | ✅ exit 0, 52,0 s, mọi `assert` qua | [R_06 committed](evidence/R_06_predict_aqi_output_diff_committed_data.csv) | 26/26 ô khớp, 1.017 con số. |
| `05`, dữ liệu sinh lại ở đây | ⚠️ lệch nhỏ: 3 con số CI ở ô c10 đổi | [R_05](evidence/R_05_weather_correlation_output_diff.csv) | Gurugram H1 cận trên 41,8 → 42,1; Jaipur H1 7,7 → 7,2 và 0,447 → 0,386. Không kết luận nào đổi. |
| `06`, dữ liệu sinh lại ở đây | ⚠️ 5 lệch nhỏ (≤ 0,06) và 1 lệch lớn ở ô c32 | [R_06](evidence/R_06_predict_aqi_output_diff.csv) | HistGradientBoosting L3 ở ngưỡng 201: TP 388 → 387, FP 34 → 35. Số của Ridge không đổi. Nguyên nhân ở [V11](verification_results.md#V11). |

Phân loại dùng trong các file `R_*`: **khớp** (mọi con số bằng nhau trong sai số tương đối 0,5%), **lệch nhỏ** (chênh ≤ 0,06 tuyệt đối và không đổi kết luận), **lệch lớn** (đổi một số đếm hoặc một kết luận). Ảnh PNG không so theo hash vì luôn khác giữa các phiên bản matplotlib.

## 4. Script kiểm chứng của DA

Mọi script nằm ở `reports/ra/evidence/scripts/`, chạy tại thư mục đó bằng `/home/user/.venv-da/bin/python <script>`. Tất cả exit 0. Script chỉ đọc `src/` và `data/`; kết quả ghi vào `reports/ra/evidence/`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| `v01_pipeline.py` (Q01) | exit 0, 20 s | `V01_*.csv` (3 file) | Chạy `src/pipeline.py` từ raw rồi so từng ô với bảng sạch đã commit. |
| `v02_asof.py` (Q02) | exit 0, 48 s | `V05_*.csv`, `V06_*.csv` | Cắt raw ở 17 ngày; nhiễu dữ liệu sau ngày cắt. Lần chạy đầu gặp `KeyError` trong `pipeline.investigate` ([NEW-002](verification_results.md#NEW-002)); DA vòng qua trong `da_clean.py`, không sửa `src/`. |
| `v02b_walkforward.py 0 2`, `… 1 2`, `… merge` (Q02) | exit 0 (log kết thúc bằng `DONE 0`, `DONE 1`); thời gian chạy hai nửa **không được ghi lại**; `merge` 2,6 s | `V07_walkforward_*.csv(.gz)` | Làm sạch lại từ raw cắt ở **mỗi** ngày t của khoảng chung 14/06/2017–01/07/2020. Đây là script nặng nhất; chạy nền thành hai tiến trình song song. |
| `v07c_realtime_model.py` (Q02) | exit 0, 5,8 s | `V07_realtime_variant_metrics.csv` | Huấn luyện lại mô hình trên đặc trưng "thời gian thực". |
| `v08_missing_sensitivity.py` (Q03) | exit 0, 1 phút 55 s | `V08_*.csv`, `V09_*.csv` | 10 cấu hình làm sạch. |
| `v04_weather.py` (Q04) | exit 0, 10 s | `V10_*.csv`, `V11_*.csv` | Chỉ dùng cache offline. |
| `v14_eda.py [ngưỡng]` (Q05) | exit 0, khoảng 11 s | `V14_*` … `V17_*`; với ngưỡng 151: `S01_V14…_thr151.csv` | |
| `v18_corr.py` (Q06) | exit 0, 1 phút 24 s | `V18_*.csv`, `V19_*.csv` | |
| `v20_model.py` (Q07) | exit 0, 11,9 s | `V20_*` … `V24_*` | |
| `v25_docs.py` (Q08, Q09) | exit 0, dưới 1 s | `V25_*.csv`, `V26_*.csv` | Chỉ kiểm kê file và đếm chuỗi. |
| `s01_threshold.py`, `s02_city_season.py`, `s05_interp_simulation.py`, `s06_block_holdout.py` | exit 0; 6 s, 4 s, 14 s, 3 s | `S01_*` … `S06_*` | Phân tích bổ sung. |
| Thư viện dùng chung | `da_common.py`, `da_clean.py`, `da_model.py`, `da_eda.py` | — | `da_clean.py` là bản viết lại pipeline có tham số (để thử ngưỡng); với tham số mặc định nó cho bảng trùng baseline ở sai số 1e-9. `da_model.py` gọi lại hàm của `src/model_utils.py`. |

## 5. Phần bị chặn hoặc chưa làm

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Tải lại thời tiết từ Open-Meteo, `smoke_test()` | ⛔ blocked | lỗi SSL ở trên | Không kiểm được cache có trùng dữ liệu API hiện tại không. |
| Kiểm tra giờ phát hành AQI (CPCB) và ERA5 trong ngày | ⛔ blocked | không có mạng, repo không có tài liệu về giờ phát hành | Ảnh hưởng câu hỏi "dùng được trong vận hành thật không" của Q07. |
| Báo cáo, slide, biên bản vấn đáp, thời lượng demo | ⛔ không có trong repo | [V25](verification_results.md#V25) | Cần tác giả cung cấp. |
| Đọc và đánh giá nhãn, chú thích của cả 15 hình | ⚠️ mới xem 2/15 hình bằng mắt; 15/15 được đo kích thước và dpi | [V25](verification_results.md#V25) | |
| Anchor V02–V04, V12–V13 | Không dùng | — | Số bị bỏ trống do đổi kế hoạch giữa chừng; không có kết quả nào bị ẩn dưới các số đó. |

## 6. Ghi chú vận hành

- So sánh file CSV sinh lại bằng hash là quá chặt: bảng sạch sinh lại có 680 ô khác ở mức bit (chênh lớn nhất 1,14e-13) nhưng 0 ô khác ở sai số 1e-9. DA dùng so sánh số có dung sai.
- `pm25_gt_pm10_flag` là kiểu boolean có NaN trong pipeline nhưng thành `object` sau khi đọc lại CSV. Ai dùng cột này phải tự ép kiểu.
- Import `src/` từ repo sẽ tạo `src/__pycache__/`. Script DA đã tắt ghi bytecode; thư mục này không có trong bản bàn giao.
- Không có credential hay bản sao dữ liệu lớn nào được lưu. File lớn nhất trong `evidence/` là `V07_walkforward_realtime_features.csv.gz` (0,96 MB); cả thư mục khoảng 2 MB.
