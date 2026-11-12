# Nhật ký thay đổi của Dev — vòng sửa 2 (F02, F01, NEW-002)

Ngày 12/11/2026 · Vai trò: AI-4 Dev · Căn cứ: [gói giao việc](../AI_REMEDIATION_HANDOFF.md) mục DEV-01 và DEV-02; RA-DEC-01 (`8c525ab`), [RA-DEC-02](https://github.com/HTung0511/Air_Project_Test/blob/fa34b692efa8d605e39efa13def732fb15e56379/Air-Project-main/reports/ra/round2/RA_DECISIONS_02.md) (`fa34b69`), [RA-DEC-03](https://github.com/HTung0511/Air_Project_Test/blob/8c1a2fb176cc3b26cd612d34a731f0b44e5095d0/Air-Project-main/reports/ra/round2/RA_DECISIONS_03.md) (`8c1a2fb`).

**Trạng thái: sẵn sàng DA kiểm. Chưa được DA xác minh, chưa được RA nghiệm thu.** Mọi con số dưới đây do Dev đo trên máy của Dev. "Đạt" trong tài liệu này nghĩa là phép kiểm của Dev chạy và thoả điều kiện đã ghi, không hơn.

Tài liệu đi kèm: [`dev_label_feature_protocol.md`](dev_label_feature_protocol.md) (nhãn, mẫu, đặc trưng của đường dự báo) và thư mục [`dev_evidence/`](dev_evidence/) (log, mã thoát, bảng).

## 1. Tóm tắt

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| F02: NB04 chạy trọn khi không có mạng, từ 8 cache đã commit | Dev chạy: đạt. 16/16 ô mã, 0 lần thử kết nối, không file nào trong `data/` đổi | `dev_evidence/chains/baseline/chain_summary.json`; [D01](#D01), [D02](#D02) | Mạng bị chặn ở mức socket trong kernel |
| F02: cache thiếu hoặc hỏng thì dừng rõ ràng | Dev chạy: đạt. 8 kiểu hỏng ở mức notebook, thêm các ca ở mức hàm | `dev_evidence/pytest/pytest_full.log`; [D01](#D01) | Không ghi output nào, kể cả output dở |
| F02: lỗi cú pháp ô 29 trên Python 3.11 | Đã sửa; ô chạy được | [D04](#D04) | Chỉ kiểm trên 3.11.2 |
| F02: môi trường ghim | `requirements-lock.txt` cài được trên venv mới; `pip freeze` trùng file lock; `pip check` sạch | `dev_evidence/environment.txt`, `environment_vs_lock.diff`, `pip_check.log`; [D05](#D05) | Là môi trường Dev đã kiểm, không phải môi trường tác giả |
| F02: bảng thời tiết tạo lại so với bản đã commit | 852 ô khác trên 225.792 ô; lệch lớn nhất 0,01; 0 ô ngoài dung sai đã duyệt | `dev_evidence/chains/nb04/nb04_outputs/nb04_vs_committed_cells.csv`; [D03](#D03) | Cả 852 ô nằm đúng biên làm tròn x,xx5 |
| F02: NB05, NB06 đọc đúng bảng thời tiết được chỉ định | Dev chạy: đạt, ở cả hai cấu hình (baseline; output mới của NB04) | `dev_evidence/chains/*/chain_summary.json`, `provenance.jsonl`; [D02](#D02) | Mặc định là baseline; đọc output mới phải nói rõ |
| F02: API Open-Meteo thật | ❓ Không đủ bằng chứng | `dev_evidence/pytest/pytest_full.log` (1 test bỏ qua) | Sandbox chặn `archive-api.open-meteo.com`. Đường online chỉ được kiểm bằng mock |
| F01: NB06 dựng đặc trưng và nhãn từ raw, as-of *t* | Đã sửa; NB06 chạy trọn 27/27 ô mã | `dev_evidence/chains/nb06_only/`; [D06](#D06), [D07](#D07) | Thiết kế theo RA-DEC-02 |
| F01: đặc trưng của ngày *t* không đổi khi cắt hoặc làm nhiễu dữ liệu sau *t* | Dev chạy: 0 ô khác trên 1.114 ngày cắt (276.272 ô) và 47 ngày cắt kèm nhiễu | `dev_evidence/pytest/leakage_walk_forward_all_days.csv`, `leakage_cut_and_perturb_check.csv` | So chính xác, đi từ raw |
| F01: nhãn, mẫu | 8.668 mẫu; thêm 5 mẫu train so với đường cũ, mất 0; test và 03–07/2020 giữ nguyên khoá và nhãn | `dev_evidence/chains/nb06_only/nb06_outputs/nb06_cohort_keys.csv`, `nb06_cohort_diff.csv`; [mục 5](#5-nhãn-mẫu-chia-tập-baseline-có-đổi-không) | **Có đổi nhãn và mẫu**, theo RA-DEC-02 |
| F01: ba phép so bắt buộc | Đã có trong NB06 (Phần I) và trong test | `nb06_path_comparison.csv`, `nb06_path_comparison_paired.csv` | 18/18 khoảng 95% của hiệu MAE chứa 0 |
| NEW-002: `investigate` lỗi khi chuỗi chưa có khí | Đã sửa; kết quả trên dữ liệu đủ trùng bản gốc | [D09](#D09) | |
| Nhánh làm sạch và EDA giữ nguyên | NB01, NB02, NB03, NB05 chạy lại cho output dạng chữ trùng bản đã commit; không file nào trong `data/` đổi | `dev_evidence/compare/*_committed_vs_rerun.md`; [mục 9](#9-tương-thích-với-nhánh-eda-và-cách-quay-lui) | |
| Toàn bộ kiểm thử | 211 ca: 210 đạt, 1 bỏ qua (API thật); mã thoát 0 | `dev_evidence/pytest/pytest_full.log`, `junit.xml`; [D12](#D12) | |

## 2. Commit, nhánh, PR, môi trường

| Mục | Giá trị |
|---|---|
| Nhánh | `arena/5cb21c04-air-project-test`, tách từ `cd719cf7f8aa43529df953e860f9cc5f45d963ee` (commit tài liệu của RA) |
| **Commit mã để DA kiểm** | **`a9757af398ddac2f8536e8019e4eb6b5900b4f75`** |
| Commit tài liệu và bằng chứng | commit chứa file này, nằm ngay sau `a9757af`. Nó chỉ thêm `reports/ra/round2/dev_*`; không đổi `src/`, `notebooks/`, `tools/`, `tests/`, `data/`, `reports/figures/` |
| PR | [#4](https://github.com/HTung0511/Air_Project_Test/pull/4) → `main`. Chưa merge; Dev không tự merge |
| Diff riêng của Dev | [`cd719cf...a9757af`](https://github.com/HTung0511/Air_Project_Test/compare/cd719cf7f8aa43529df953e860f9cc5f45d963ee...a9757af398ddac2f8536e8019e4eb6b5900b4f75): 31 file, +8.152 / −1.204 dòng |
| Môi trường | Python 3.11.2, Linux x86_64, 2 CPU, 3,8 GB RAM; numpy 2.4.6, pandas 3.1.1, scipy 1.17.1, scikit-learn 1.9.1, statsmodels 0.15.0, matplotlib 3.11.2; đủ 66 gói trong `requirements-lock.txt` |

PR #4 so với `main` còn chứa 9 commit tài liệu kế thừa của BA và RA (đến `cd719cf`). Phần của Dev là 6 commit sau đó:

| Commit | Nội dung |
|---|---|
| `b4daa41` | F01, F02, NEW-002: `forecast_utils.py`, `data_paths.py`, `weather_utils.py`, NB04, NB06, môi trường ghim, công cụ, kiểm thử |
| `74f4004` | NB04 và NB06 commit kèm output của một lần chạy trọn; tạo lại 5 hình `model_0x`; test "chạy lại ra đúng output đã commit" |
| `024080d` | Ghi mọi lần che và điền (NB06) và mọi ô thời tiết khác bản đã commit (NB04) thành file output |
| `79c95ed` | `adopt_outputs.py`: cách kernel cắt đoạn `print` không còn bị coi là khác output |
| `75c69dd` | NB06: nói đúng nguồn gốc 81 mẫu dùng CO = 0; gắn hai số đếm vào snapshot |
| `a9757af` | Chỉ thêm test: 8 ca cache hỏng ở mức notebook; 8 ví dụ viết tay theo RA-DEC-02 và RA-DEC-03 |

Tree git ở `a9757af` (lệnh `git rev-parse a9757af:Air-Project-main/<thư mục>`): `src` `e5a4c8b8`, `notebooks` `ae2f28b2`, `tools` `fad8f903`, `tests` `51a7d6c0`, `data` `6e5d738d`, `reports/figures` `ac648ae1`. Tree `data` trùng định danh baseline `6e5d738d` trong giao thức của DA: không file dữ liệu nào bị đổi.

## 3. Cách chạy lại, mã thoát

Một lệnh tạo lại toàn bộ `dev_evidence/` (khoảng 13 phút, cần 300 MB đĩa ngoài repo):

```bash
python3 -m venv /tmp/air-venv && /tmp/air-venv/bin/python -m pip install --upgrade pip==26.3
/tmp/air-venv/bin/python -m pip install -r Air-Project-main/requirements-lock.txt
git fetch --depth 1 origin 13e93ae12c483f01a573ee51ef9562a315e45068   # chỉ cần cho bước đối chiếu với bản tham chiếu của DA
cd Air-Project-main
bash reports/ra/round2/dev_evidence/run_evidence.sh /tmp/air-venv/bin/python /tmp/dev_ev cd719cf
```

Lần chạy của Dev: ngày 12/11/2026, cây làm việc sạch ở `a9757af`, kết quả trong `dev_evidence/`. Mã thoát từng bước nằm ở `dev_evidence/steps.tsv`; **cả 21 bước thoát 0**.

| Bước trong `steps.tsv` | Lệnh (chạy từ `Air-Project-main/`) | Mã thoát | Log |
|---|---|---|---|
| `pip_check` | `python -m pip check` | 0 | `pip_check.log` |
| `pytest` | `python -m pytest -q -rs --durations=15 --junitxml=…` | 0 | `pytest/pytest_full.log` |
| `chain_baseline` | `python tools/run_chain.py --work … --name baseline --notebooks 04,05,06 --weather baseline` | 0 | `chains/baseline.log` |
| `chain_nb04` | như trên, `--weather nb04` | 0 | `chains/nb04.log` |
| `chain_eda` | `--notebooks 01,02,03,05 --weather baseline` | 0 | `chains/eda.log` |
| `chain_nb06_only` | `--notebooks 06 --weather baseline` | 0 | `chains/nb06_only.log` |
| `chain_all6_nb04` | `--notebooks 01,02,03,04,05,06 --weather nb04` | 0 | `chains/all6_nb04.log` |
| `committed_outputs_nb04`, `committed_outputs_nb06` | `python tools/adopt_outputs.py <bản đã chạy> notebooks/<notebook> --check` | 0 | `compare/committed_outputs_*.log` |
| `original_nb06` | `python tools/run_notebook.py <bản giải nén của cd719cf> 06_predict_aqi.ipynb --block-network` | 0 | `orig/original_nb06.log` |
| 8 bước `cmp_*` | `python tools/compare_notebook_outputs.py A B --out …` | 0 | `compare/*.md` |
| `figures` | so 5 hình `model_0x` giữa `cd719cf`, repo và lần chạy lại | 0 | `compare/nb06_figures_old_vs_new.tsv` |
| `da_crosscheck` | `python reports/ra/round2/dev_evidence/crosscheck_da_reference.py …` | 0 | `da_crosscheck/crosscheck_da_reference.log` |
| `determinism` | so từng byte các file output giữa các lần chạy | 0 | `compare/determinism_between_runs.txt` |

Các bước `cmp_*` là công cụ đo, luôn thoát 0; kết quả đọc ở báo cáo `.md`. Các bước còn lại thoát khác 0 khi điều kiện của chúng không thoả.

Chạy riêng từng phần:

```bash
cd Air-Project-main
python -m pytest -q                         # toàn bộ, khoảng 6 phút
python -m pytest -q -m "not notebook"       # bỏ các test chạy notebook thật, khoảng 1,5 phút
python tools/run_chain.py --work /tmp/w --notebooks 04,05,06 --weather nb04    # NB04 -> NB05 -> NB06 trong một bản sao, chặn mạng
```

`tools/run_chain.py` luôn chạy notebook trong một **bản sao** của dự án đặt ở `--work`. Lý do: chạy ngay trong repo thì NB01 ghi đè `data/processed/air_quality_8cities.csv` và mọi notebook ghi đè hình trong `reports/figures/`.

### Ghi chú cho DA khi kiểm

| Việc | Cần biết |
|---|---|
| Output mới nằm ở đâu | Trong thư mục dự án đang chạy, dưới `outputs/nb04/` và `outputs/nb06/`. Không ghi ra ngoài thư mục dự án, trừ khi đặt `AIR_NB04_OUT_DIR` hoặc `AIR_NB06_OUT_DIR` |
| File nào đã được đọc | Notebook in dòng `[đọc] <vai trò>: <đường dẫn> \| sha256 … \| <loại>` cho các file đầu vào chính, và `[ghi] …` cho từng file output. Danh sách đầy đủ: đặt `AIR_PROVENANCE_LOG=<file>` thì mỗi lần đọc và ghi được nối thêm một dòng JSON (vai trò, đường dẫn, sha256, số byte); `run_chain.py` tự đặt biến này và chép kết quả vào `chain_summary.json` |
| T1.8 (NB05, NB06 đọc output của NB04) | **Mặc định NB05 và NB06 đọc bảng thời tiết baseline đã commit**, và in rõ điều đó kèm một dòng `LƯU Ý` nếu có output NB04 mới hơn. Muốn chúng đọc output mới: đặt `AIR_WEATHER_DAILY=<…/outputs/nb04/weather_daily_8cities.csv>` hoặc chạy `tools/run_chain.py --weather nb04`. Trỏ tới file không tồn tại thì dừng với `FileNotFoundError` |
| Bảng ghép `air_quality_8cities_weather.csv` | Không notebook nào đọc file này, ở mã gốc cũng vậy. NB05 đọc bảng sạch và bảng thời tiết theo ngày; NB06 đọc raw và bảng thời tiết theo ngày |
| Thử cắt raw ở mức file | Gọi `forecast_utils.make_forecast_features()`. `build_forecast_dataset()` và NB06 từ chối raw có khoảng chung khác phạm vi đã chốt. Các kiểu nhiễu bị từ chối: protocol mục 7 |
| Số chưa làm tròn | `outputs/nb06/nb06_run_summary.json` (mọi chỉ số), `nb06_predictions.csv` (dự đoán theo khoá), `nb06_snapshot_checks.csv` (181 con số: đo được, giá trị trong phần viết, dung sai) |
| Tên tập | `lockdown` trong mã là holdout 03–07/2020 |

## 4. Các thay đổi

Số ô của notebook đếm từ 0; `id` là mã ô trong file `.ipynb`.

<a id="D01"></a>
### D01 — NB04 đọc cache trước, mặc định offline (F02)

| Mục | Nội dung |
|---|---|
| File, hàm | `src/weather_utils.py`: `network_mode`, `validate_hourly`, `validate_cache`, `cache_status`, `fetch_city`, `fetch_all`, `_download`, `_check_response`, `_save_download`, `smoke_test`, `probe_variable`; lớp lỗi `WeatherError`, `WeatherOfflineError`, `WeatherCacheError`, `WeatherDownloadError`. `notebooks/04_weather_merge.ipynb` ô 2, 5, 6, 7, 8 |
| Trước | Ô 6 gọi `wu.smoke_test()` và `wu.probe_variable(...)`, tức hai lần gọi API, trước khi đọc cache. Không có mạng thì dừng ở đó dù 8 cache có đủ. `fetch_city` coi cache là hợp lệ khi đủ tên cột và ngày đầu, ngày cuối phủ khoảng. `probe_variable` bắt lỗi mạng rồi trả `False`, làm `USE_BLH = False` và lớp biên khí quyển bị bỏ mà không báo. Bản tải mới ghi vào `data/raw/weather/` |
| Sau | Ô 6 gọi `wu.cache_status()` (chỉ đọc file); ô 8 gọi `wu.fetch_all()`. **Cache hợp lệ** khi: đủ cột `time`, 7 biến bắt buộc (gồm `boundary_layer_height`) và 3 cột ô lưới; `time` đọc được và tăng dần; đủ mọi giờ của 25/12/2014–01/07/2020 (48.384 giờ), không giờ trùng, không mốc lệch lưới giờ; biến là số và không có ô trống; ô lưới cố định. Cả 8 cache hợp lệ thì số lần gọi `requests.get` là 0 (`wu.N_API_CALLS`). **Offline là mặc định**: thiếu hoặc hỏng cache thì `WeatherCacheError` liệt kê mọi thành phố có vấn đề, file và tiêu chí hỏng, trước khi làm bất cứ việc gì. **Online** (`AIR_WEATHER_MODE=online`): chỉ tải thành phố không có nguồn hợp lệ, kiểm phản hồi bằng cùng bộ tiêu chí, lưu vào `outputs/weather_downloads/` kèm file `.provenance.json`; file được mở ở chế độ tạo mới nên không bao giờ ghi đè. Lỗi mạng thành `WeatherDownloadError` nêu thành phố, file đích, biến và khoảng thời gian. Lớp biên là biến bắt buộc, xác định từ schema của cache. `probe_variable` không còn biến lỗi mạng thành `False` |
| Lý do | DA V10, V11: NB04 không chạy được khi API bị chặn dù cache đủ; cách kiểm cache cũ để lọt file cụt hoặc trùng giờ |
| Kiểm thử | `tests/test_weather_cache.py` (37 ca). `tests/test_notebooks_integration.py`: `test_nb04_runs_to_the_end_offline_from_cache`; `test_nb04_with_a_broken_cache_stops_clearly_and_writes_nothing` với 8 kiểu hỏng (thiếu 1 cache; thiếu cả 8; cụt 24 giờ cuối; thiếu cột lớp biên; đổi tên một cột bắt buộc; trùng giờ; gzip hỏng; cache kết thúc sớm) |
| Dung sai | Không có. Mọi tiêu chí là so chính xác |
| Chưa làm | API thật: ❓. Đường online chỉ chạy với `requests.get` giả (mock) |
| EDA, quay lui | NB01–NB03 không dùng module này. Quay lui: [mục 9](#9-tương-thích-với-nhánh-eda-và-cách-quay-lui) |

<a id="D02"></a>
### D02 — NB04 không ghi đè baseline; NB05 và NB06 đọc file được chỉ định (F02, RA-DEC-02 mục 5)

| Mục | Nội dung |
|---|---|
| File, hàm | `src/data_paths.py` (mới): `weather_daily_path`, `nb04_out_dir`, `nb06_out_dir`, `check_writable`, `record_input`, `record_output`, `COMMITTED_SHA256`, `save_json`, `save_table`. `src/weather_utils.py`: `save_outputs`, `output_paths`. `src/corr_utils.py`: `WEATHER_FILE`, `load_with_weather`. NB04 ô 26, 27. `tools/run_chain.py` |
| Trước | NB04 ô 27 ghi thẳng `data/processed/air_quality_8cities_weather.csv` và `weather_daily_8cities.csv`, đè lên bản đã commit. NB05 và NB06 đọc đường dẫn cố định |
| Sau | NB04 ghi vào `outputs/nb04/` (thư mục không commit): hai bảng trên, `nb04_manifest.json` (đầu vào, đầu ra, sha256, môi trường), `nb04_vs_committed_cells.csv`, `nb04_vs_committed_summary.csv`. `save_outputs` từ chối ghi vào `data/` trừ khi đặt `AIR_ALLOW_BASELINE_OVERWRITE=1`. NB05 và NB06 mặc định đọc baseline; đọc output mới qua `AIR_WEATHER_DAILY` hoặc `run_chain.py --weather nb04`. Mỗi file đầu vào được in kèm sha256 và một nhãn dựa trên **nội dung**: sha256 của 12 file raw, cache và baseline đã commit được ghim trong `COMMITTED_SHA256`, nên một file nằm ở vị trí baseline nhưng đã bị ghi lại được gọi đúng tên là "nội dung khác bản đã commit" |
| Lý do | Quy tắc chung của gói giao việc: không ghi đè baseline. RA-DEC-02 mục 5: khi chạy chuỗi, bước sau phải thật sự đọc output mới |
| Kiểm thử | `test_weather_cache.py`: `test_save_outputs_refuses_the_baseline_tree`, `test_default_output_dir_is_not_the_baseline`, `test_weather_daily_path_never_falls_back_silently`, `test_record_input_reports_path_hash_and_kind`. `test_snapshot_checks.py`: `test_committed_sha256_registry_matches_the_files_in_the_repo`, `test_kind_of_a_file_depends_on_content_not_only_on_location`. `test_notebooks_integration.py`: `test_nb04_writes_new_outputs_and_leaves_data_untouched`, `test_downstream_notebooks_read_the_new_weather_not_the_baseline`, `test_weather_override_pointing_nowhere_stops_the_notebook` |
| Kết quả đo | Chuỗi `nb04`: NB05 và NB06 đọc `outputs/nb04/weather_daily_8cities.csv`, sha256 `2c906e61…`. Chuỗi `baseline`: cả hai đọc `data/processed/weather_daily_8cities.csv`, sha256 `45f3579a…` |
| Chưa làm | README, `Data_dictionary.md`, `Metadata.json` và nhật ký làm sạch vẫn ghi NB04 tạo file trong `data/processed/` ([mục 10](#10-việc-cần-ba-đồng-bộ-tài-liệu)) |
| EDA, quay lui | Mặc định mọi notebook đọc đúng các file như trước |

<a id="D03"></a>
### D03 — So bảng thời tiết tạo lại với bản đã commit, theo dung sai đã duyệt (F02)

| Mục | Nội dung |
|---|---|
| File, hàm | `src/weather_utils.py`: `compare_daily`, `unrounded_means`; hằng `TOL_MEAN_COLS`, `ROUND_TOL`, `ABS_EPS`, `BOUNDARY_EPS`, `EXACT_COLS`. NB04 ô 27 |
| Trước | Không có phép so. Bảng tạo lại đè lên bảng cũ |
| Sau | NB04 so bảng theo ngày vừa tạo với bản đã commit, lưu **từng ô khác** ra file trước khi `assert`, và chỉ bắt buộc đạt khi cả 8 thành phố được đọc từ cache gốc |
| Dung sai (RA-DEC-02 mục 5) | `temp_mean`, `pressure_mean`, `wind_speed_mean`: một ô được lệch tối đa 0,01 (+1e-9) **chỉ khi** trung bình 24 giờ chưa làm tròn, tính lại từ cache, nằm sát biên x,xx5 (phần lẻ của 100 × trung bình cách 0,5 không quá 1e-6) và cả hai giá trị đều là một cách làm tròn của trung bình đó. Mọi cột số khác: 1e-9. Khoá, tên cột, vị trí NaN, `rain_day`, `wind_dir_8`: chính xác |
| Kết quả đo | 852 ô khác trên 225.792 ô: `temp_mean` 335, `pressure_mean` 348, `wind_speed_mean` 169. Lệch lớn nhất 0,01. 0 ô ngoài dung sai. 11 cột còn lại: 0 ô khác |
| Lý do | DEV-01 mục 7: dung sai phải có lý do và không được che lỗi đơn vị hay lệch ngày. Dev chưa xác định được vì sao môi trường tác giả làm tròn khác ở các ô này; điều đo được là cả 852 ô nằm đúng biên x,xx5 |
| Kiểm thử | `tests/test_weather_tolerance.py` (18 ca): lệch 0,01 ở ô không sát biên là vi phạm; lệch 0,02 tại biên là vi phạm; đổi đơn vị (°C sang K, hPa sang Pa, m/s sang km/h) và lệch một ngày đều bị bắt; các cột khác không có dung sai làm tròn |
| Ảnh hưởng xuống NB05, NB06 | NB05 với bảng thời tiết mới: 3 con số in ra đổi, đều ở giả thuyết H1 (gió yếu so với gió mạnh), các `assert` của NB05 vẫn đạt (chi tiết ở [mục 11](#11-vấn-đề-mới-gửi-ra)). NB06: 181 con số được đối chiếu, 0 con số lệch quá nửa đơn vị của chữ số cuối được in |

<a id="D04"></a>
### D04 — Lỗi cú pháp f-string ở NB04 ô 29 (F02)

| Mục | Nội dung |
|---|---|
| File | `notebooks/04_weather_merge.ipynb` ô 29 (`id 7cbb1821`) |
| Trước | Trong một f-string dùng nháy kép có biểu thức `str(round(skew, 1)).replace(".", ",")`. Lồng cùng loại dấu nháy trong f-string chỉ hợp lệ từ Python 3.12, nên Python 3.11 báo `SyntaxError` |
| Sau | Tính trước `skew_txt = str(round(skew, 1)).replace(".", ",")`, f-string dùng `{skew_txt}`. Chuỗi in ra không đổi |
| Kiểm thử | NB04 chạy trọn 16/16 ô trên Python 3.11.2 (`test_nb04_runs_to_the_end_offline_from_cache`, các chuỗi `baseline`, `nb04`, `all6_nb04`) |
| Chưa làm | Không kiểm được trên Python 3.12–3.14: sandbox chỉ có 3.11.2. Mã không dùng cú pháp riêng của 3.12 trở lên |

<a id="D05"></a>
### D05 — Môi trường ghim (F02, RA-DEC-01)

| Mục | Nội dung |
|---|---|
| File | `Requirements.txt`, `requirements-lock.txt` (mới), `pytest.ini` (mới), `.gitignore` (mới) |
| Trước | `Requirements.txt` có 10 dòng không ghi phiên bản, `statsmodels` lặp hai lần. Không có file lock. Notebook gốc ghi Python 3.14.7; phiên bản thư viện của tác giả không được ghi ở đâu |
| Sau | `Requirements.txt` ghim 12 thư viện dùng trực tiếp. `requirements-lock.txt` ghim đủ 66 gói (kết quả `pip freeze`, Python 3.11.2, pip 26.3). `jupyter` không nằm trong môi trường đã kiểm nên không ghim, chỉ ghi chú cách cài thêm |
| Kiểm thử | Cài file lock vào venv mới: `pip freeze` trùng file lock (`environment_vs_lock.diff`), `pip check` không báo xung đột |
| Đối chứng môi trường | NB06 **gốc** (mã và dữ liệu của `cd719cf`) chạy lại trong môi trường này: 26/26 ô mã, 0 con số khác so với output tác giả đã commit; 5 dòng khác đều là dấu `\` và `/` trong đường dẫn hình (`compare/nb06_author_outputs_vs_original_code_rerun.md`). Vậy các con số đổi ở NB06 mới là do mã và mẫu, không do môi trường |
| Chưa làm | Không tái lập môi trường của tác giả |
| Ghi chú | Phiên bản các thư viện dùng trực tiếp trùng với môi trường baseline ghi ở mục 2 trong giao thức của DA |

<a id="D06"></a>
### D06 — Đường dự báo từ raw: `src/forecast_utils.py` (F01)

| Mục | Nội dung |
|---|---|
| File, hàm | `src/forecast_utils.py` (mới): `prepare_raw`, `raw_value_violations`, `load_raw`, `load_weather_daily`, `trailing_zero_run`, `asof_pollutant`, `make_forecast_features`, `attach_target`, `build_forecast_dataset`, `retention`, `masking_summary`, `masked_cells`, `perturb_after`, `asof_check`, `cohort_diff`, `feature_diff`, `run_protocol`, `compare_paths` |
| Trước | NB06 gọi `model_utils.build_dataset()`, lấy đặc trưng và nhãn từ bảng sạch hồi cứu. Bảng đó được dựng bằng cả chuỗi: nội suy hai đầu, luật nghi lỗi top-5 và cửa sổ 15 ngày lấy tâm, xoá cả chuỗi số 0. `make_features(as_of=t)` cắt bảng **đã** làm sạch, nên phép thử rò rỉ cũ không thấy được việc này |
| Sau | Đặc trưng của ngày *t* được dựng từ raw và thời tiết có ngày ≤ *t*. Nhãn là AQI raw của ngày lịch *t*+1. Không nội suy, không backward-fill, không luật nghi lỗi hồi cứu. Số 0 treo xử lý theo snapshot as-of *t*. Chi tiết và ví dụ: [`dev_label_feature_protocol.md`](dev_label_feature_protocol.md) |
| Không đổi | `src/model_utils.py`: định nghĩa ba mức đặc trưng, `make_pipe`, cách chọn alpha và ngưỡng, bootstrap, hàm vẽ. Cả hai đường dùng chung các hàm này |
| Lý do | DA V05, V07; RA-DEC-02 mục 2–4 |
| Kiểm thử | `tests/test_forecast_flatline.py` (81 ca), `tests/test_forecast_leakage.py` (9 ca), `tests/test_forecast_cohort.py` (20 ca). Nội dung từng nhóm: [D12](#D12) |
| Dung sai | Phép thử cắt và làm nhiễu: so chính xác, NaN bằng NaN. So với đường hồi cứu trên khoá chung: 1e-9 |
| Chưa làm | Xem protocol mục 9 |
| EDA, quay lui | Module mới, không đường nào của EDA import nó. `model_utils.build_dataset()` vẫn chạy như cũ và được NB06 gọi để đối chiếu |

<a id="D07"></a>
### D07 — NB06 dùng đường dự báo (F01)

| Mục | Nội dung |
|---|---|
| File | `notebooks/06_predict_aqi.ipynb`: 60 ô thành 61 ô, 26 ô mã thành 27 |
| Ô mã viết lại | 3 `60ee5880` (in sha256 của ba file đầu vào, so với snapshot); 5 `23317e4a` (dựng dữ liệu bằng `fu.build_forecast_dataset()`, bảng giữ mẫu, đếm lại độc lập từ raw, khoá thêm bớt so với đường cũ, bảng che và điền); 6 `4b6742a3` (kiểm tra rò rỉ đi từ raw); 53 `5bad2128` (so ba biến thể A, B, C); 58 `e084a76b` (đối chiếu con số); 59 `r2f01sum1` (mới: lưu `outputs/nb06/` rồi `chk.finish()`) |
| Ô chữ cập nhật | 0, 1, 4, 7, 11, 16, 19, 25, 35, 41, 42, 50, 56, 57: mô tả nguồn dữ liệu và các con số đổi. Ô 28, 38, 46, 49, 60 đã được đối chiếu với output mới và giữ nguyên |
| Giữ nguyên | Chia theo thời gian; ba mức đặc trưng, mức cận trên và mô hình cây; ba baseline; `TimeSeriesSplit` 4 lần cách 16 dòng; ngưỡng F2 chọn trên dự đoán ngoài mẫu của train; bootstrap khối 14 ngày. Phần G vẫn lặp lại cách làm của NB05 trên bảng sạch hồi cứu, và ghi rõ điều đó tại chỗ |
| Ô bị thay nội dung | Ô 53 cũ so "đặt lại NaN" với "giữ ô nội suy" (`build_dataset(mask_interp=False)`). Đường mới không có ô nội suy nên phép so đó không còn đối tượng; ô này nay chứa ba phép so bắt buộc của RA-DEC-02 |
| Kiểm thử | `test_notebooks_integration.py`: `test_nb06_really_runs_on_the_forecast_path_from_raw` (file đầu tiên được đọc là raw; nhãn trong file dự đoán bằng AQI raw của *t*+1; MAE tính lại từ file dự đoán trùng tóm tắt; khoá mẫu và ô bị che đối chiếu lại với raw bằng pandas thuần), `test_nb06_rerun_reproduces_the_outputs_committed_in_the_notebook`, `test_nb06_forecast_numbers_do_not_depend_on_the_retrospective_table` |

Câu lệnh `assert` của NB06, trước và sau:

| Nhóm | Trước (`cd719cf`) | Sau (`a9757af`) |
|---|---|---|
| Thứ tự thời gian, `Date_target = Date + 1`, mức 1–3 không chứa cột `_next` | 3 câu, ô 6 | giữ nguyên 3 câu |
| Rò rỉ | 2 câu trong vòng lặp 3 ngày cắt, trên bảng đã làm sạch, so bằng `np.allclose` | 6 câu, đi từ raw: bảng đặc trưng không có cột nhãn hay `_next`; nhãn và AQI(*t*) bằng đúng raw; 23 ngày cắt kèm làm nhiễu, 8 thành phố, so chính xác, 0 ô khác; hàng cuối của bản cắt có nhãn và thời tiết ngày mai là NaN |
| Mẫu | 1 câu gắn cứng 5.741 / 1.947 / 975 | 3 câu: bảng giữ mẫu cộng đúng; tổng khớp; tập khoá trùng phép đếm lại độc lập từ raw. Các số 5.746 / 1.947 / 975 chuyển sang đối chiếu snapshot ([D08](#D08)) |
| Che và điền | không có | 4 câu, ô 5 |
| Điều kiện để tiêu đề và phần đọc kết quả còn đúng (dạng phễu, thứ tự các mức, ba thành phố nặng, quan hệ recall và precision, chiều của Phần G) | 6 câu, ô 15, 24, 27, 37, 45 | giữ nguyên 6 câu |
| Mọi ngưỡng chọn trên cùng các dòng validation | 2 câu, ô 30 | giữ nguyên 2 câu |
| Phép so hai đường | 1 câu của phép so "giữ ô nội suy" | 4 câu: biến thể C trùng kết quả chính của notebook (số mẫu, alpha, MAE, ngưỡng); A và B cùng số mẫu |
| Con số trong phần viết | 28 câu ở ô 58, gắn cứng số của đường cũ | 0 câu `assert`; thay bằng 181 con số qua `SnapshotChecks`, lỗi phát ra ở ô mã cuối ([D08](#D08)) |
| Cộng | 43 câu | 28 câu và 181 con số được đối chiếu |

Không câu `assert` chống rò rỉ nào bị bỏ mà không có câu thay thế chặt hơn.

<a id="D08"></a>
### D08 — Con số trong phần viết của NB06 gắn với snapshot đầu vào (F01)

| Mục | Nội dung |
|---|---|
| File, hàm | `src/data_paths.py`: lớp `SnapshotChecks` (`expect`, `expect_values`, `describe`, `table`, `finish`). NB06 ô 3, 58, 59 |
| Trước | Ô 58 có 28 câu `assert` so kết quả với các số viết sẵn trong phần chữ. Đổi đầu vào dù rất ít (ví dụ bảng thời tiết do NB04 tạo lại) thì notebook dừng; muốn chạy tiếp chỉ còn cách sửa số hoặc nới điều kiện |
| Sau | Ô 3 ghi sha256 của ba đầu vào (raw, thời tiết theo ngày, bảng sạch hồi cứu) và so với snapshot. Mỗi con số được đối chiếu khai báo nó phụ thuộc đầu vào nào. **Đầu vào trùng snapshot: con số bắt buộc khớp**, sai thì notebook kết thúc bằng `AssertionError` ở ô mã cuối, sau khi đã lưu bảng "đo được, giá trị trong phần viết". **Đầu vào khác snapshot: con số vẫn được đối chiếu, chỗ lệch được in và lưu, notebook không dừng.** Con số chỉ phụ thuộc raw vẫn bắt buộc khớp khi chỉ bảng thời tiết đổi |
| Dung sai | Số đếm, ngưỡng, alpha: chính xác. Số thực: nửa đơn vị của chữ số cuối được in trong phần viết, cộng sai số số học (ví dụ MAE in hai chữ số thập phân: 0,006) |
| Kết quả đo | Đầu vào đúng snapshot (chuỗi `nb06_only`): 181/181 khớp, cả 181 ở chế độ bắt buộc. Bảng thời tiết của NB04 (chuỗi `nb04`): 181 đối chiếu, 22 bắt buộc, 0 lệch. Cả sáu notebook nối tiếp với thời tiết mới (chuỗi `all6_nb04`, bảng sạch do NB01 vừa ghi lại): 181 đối chiếu, 21 bắt buộc, 0 lệch |
| Kiểm thử | `tests/test_snapshot_checks.py` (12 ca). `test_nb06_stops_when_a_narrative_number_is_stale`: đổi 19,53 thành 19,99 trong notebook thì notebook chạy tới ô cuối rồi dừng với `AssertionError` nêu đúng con số. `test_nb06_with_new_weather_reports_instead_of_pretending` |
| Lý do | DEV-02 mục 7 và quy tắc "không sửa assert để qua": phép đối chiếu phải chặt khi đầu vào đúng, và minh bạch khi đầu vào khác |

<a id="D09"></a>
### D09 — NEW-002: `pipeline.investigate` khi chuỗi chưa có khí hoặc bảng rỗng

| Mục | Nội dung |
|---|---|
| File, hàm | `src/pipeline.py`: `investigate`, hằng `EVIDENCE_COLS` (thêm 8 dòng, bỏ 2 dòng) |
| Trước | Khi chuỗi chưa có khí nào (ví dụ Jaipur nếu raw bị cắt ở 14–18/06/2017), bảng tỉ số của các khí không có chỉ mục ngày nên `R.loc[t]` ném `KeyError`. Khi không có điểm nào để điều tra, hàm trả bảng không có cột, nên bước sau lỗi khi đọc cột `suggestion` |
| Sau | Bảng tỉ số luôn mang chỉ mục ngày (`index=d.index`): không có khí thì kết quả là "0/0 khí cùng tăng". Bảng bằng chứng rỗng vẫn đủ 8 cột |
| Kiểm thử | `tests/test_pipeline_guard.py` (10 ca): Jaipur cắt ở 14, 16, 18/06/2017 không lỗi; trên chuỗi đầy đủ của 8 thành phố, hàm mới trả đúng từng ô như bản sao nguyên văn của hàm gốc; bảng sạch dựng lại trùng bản đã commit trong 1e-9; bảng điểm nghi lỗi trùng bản đã commit sau khi sắp theo khoá |
| EDA, quay lui | Đây là thay đổi duy nhất trong nhánh làm sạch hồi cứu. Kết quả trên dữ liệu thật không đổi |

<a id="D10"></a>
### D10 — Công cụ chạy và so notebook

| File | Việc làm |
|---|---|
| `tests/netguard/sitecustomize.py` | Chặn mọi kết nối ra ngoài máy trong tiến trình kernel (kết nối nội bộ của Jupyter vẫn được), ghi lại từng lần thử |
| `tools/run_notebook.py` | Chạy một notebook bằng nbclient trong một thư mục dự án, ghi bản đã chạy ra nơi khác. Xoá output có sẵn trước khi chạy, để một lần chạy lỗi không còn mang output cũ của các ô chưa chạy tới |
| `tools/run_chain.py` | Chạy một chuỗi notebook trong một bản sao, nối `AIR_WEATHER_DAILY` khi `--weather nb04`. Ghi `chain_summary.json`: commit và trạng thái cây làm việc, từng bước (số ô, thời gian, số lần thử mạng), mọi file đã đọc và ghi kèm sha256, file nào trong `data/` và `reports/` của bản sao bị đổi, và repo gốc có bị đổi không. Thoát 1 nếu có bước lỗi, có file `data/` đổi ngoài dự kiến, hoặc repo gốc bị đổi |
| `tools/compare_notebook_outputs.py` | So output dạng chữ của hai bản notebook đã chạy, theo từng ô; đếm số dòng và số con số khác. Là công cụ đo |
| `tools/adopt_outputs.py` | Chép output của một bản đã chạy vào notebook trong repo, chỉ khi mã nguồn mọi ô trùng nhau. `--check` so output của hai bản |

Kiểm thử: `tests/test_tools.py` (4 ca) và toàn bộ `tests/test_notebooks_integration.py`.

<a id="D11"></a>
### D11 — NB04 và NB06 commit kèm output; tạo lại 5 hình của NB06

| Mục | Nội dung |
|---|---|
| File | `notebooks/04_weather_merge.ipynb`, `notebooks/06_predict_aqi.ipynb`, `reports/figures/model_01…05_*.png` |
| Trước | NB04 của tác giả không có output. NB06 và 5 hình mang kết quả của đường cũ |
| Sau | Cả hai notebook mang output của một lần chạy trọn trong bản sao, môi trường ghim, chặn mạng (NB04: 26 output; NB06: 56 output). 5 hình là hình do lần chạy NB06 đó ghi |
| Kiểm thử | Bước `committed_outputs_nb04`, `committed_outputs_nb06`: chạy lại ở `a9757af` cho output trùng bản trong repo, kể cả ảnh nhúng. Bước `figures`: 5 hình trong repo trùng từng byte với hình do lần chạy lại ghi. Hai test `test_nb04_rerun_…` và `test_nb06_rerun_reproduces_the_outputs_committed_in_the_notebook` |
| So với hình cũ | `model_05` (Phần G) trùng từng điểm ảnh với hình cũ. `model_01`–`model_04` khác từ 0,15% đến 5,9% số điểm ảnh (`compare/nb06_figures_old_vs_new.tsv`). Hai chỗ Dev đã xem bằng mắt: chú thích của hình 1 ghi n = 5.746 thay cho 5.741; tiêu đề hình 4 ghi 78% thay cho 77% báo đúng |
| Chưa làm | 16 hình của NB01–NB03 và NB05 trong repo vẫn là bản của tác giả. Chạy lại trong môi trường này thì 14 hình khác byte (`chains/eda/chain_summary.json`, mục `report_files_rewritten_in_copy`); Dev không so nội dung các hình đó |

<a id="D12"></a>
### D12 — Bộ kiểm thử

211 ca trong `tests/`; `python -m pytest -q` thoát 0 với 210 đạt, 1 bỏ qua.

| File | Số ca | Kiểm điều gì |
|---|---|---|
| `test_weather_cache.py` | 37 (1 bỏ qua) | Cache đủ và chặn mạng: 0 lần gọi. Mặc định offline. Thiếu một cache; liệt kê mọi thành phố lỗi. Cache hỏng theo từng tiêu chí; gzip hỏng; cache rộng hơn khoảng được cắt đúng. Online bằng mock: chỉ tải thành phố thiếu, không ghi đè file gốc hay bản tải cũ, lỗi mạng nêu thành phố, file và biến, phản hồi xấu không được lưu. `probe_variable` không biến lỗi mạng thành `False`. Nơi ghi output; `AIR_WEATHER_DAILY` không quay về baseline. **`test_real_api_smoke` bị bỏ qua: API thật chưa được kiểm** |
| `test_weather_tolerance.py` | 18 | [D03](#D03) |
| `test_pipeline_guard.py` | 10 | [D09](#D09) |
| `test_forecast_flatline.py` | 81 | Chuỗi 0 dài 1–4 ngày ở giữa và đầu chuỗi; số 0 đã che không làm nguồn điền; số 0 chưa che là nguồn hợp lệ; ngày thiếu làm đứt chuỗi; không nội suy, không backward-fill; điền tối đa 2 ngày; hàng cũ không đổi khi thêm ngày. 8 ví dụ viết tay theo RA-DEC-02 và RA-DEC-03. 25 bộ chuỗi ngẫu nhiên so với hai trọng tài độc lập; 25 bộ khác kiểm rằng hàng đã có không đổi khi nối thêm ngày. Raw thật: cả 5 chất khớp trọng tài vòng lặp; CO khớp trọng tài "áp luật hồi cứu lên từng prefix". Ranh thành phố, ranh train và test, ngày lịch thiếu, chuỗi ngắn. Bảng che và điền khớp phép đếm lại từ raw |
| `test_forecast_leakage.py` | 9 | Bảng đặc trưng không có cột của ngày mai. Cắt và làm nhiễu ở 47 ngày: 0 ô khác. Phép làm nhiễu thật sự đổi tương lai và chỉ tương lai. Luật số 0 treo hồi cứu **trượt** cùng phép thử (đối chứng). Cắt ở mọi ngày của khoảng chung: 0 ô khác. Nhãn là AQI raw của ngày lịch kế tiếp và không bao giờ được điền. Đổi AQI ngày mai chỉ đổi nhãn và điều kiện giữ mẫu |
| `test_forecast_cohort.py` | 20 | Khoá, tính liên tục và giá trị của raw. Raw xấu thì dừng kèm số lượng, ngày, quy tắc. Tập mẫu bằng phép đếm lại độc lập. Khoá thêm bớt so với đường cũ được giải thích đủ. Khoá, nhãn và đặc trưng của test và 03–07/2020 trùng đường cũ. Ô nghi lỗi giữ giá trị raw. Imputer và scaler chỉ fit trên train. Các lần chia tôn trọng thời gian. Chạy giao thức trên đường cũ ra lại số của NB06 gốc. Ba phép so cùng mẫu cùng nhãn; hàm so từ chối gọi là "so cặp" khi khoá hoặc nhãn khác |
| `test_snapshot_checks.py` | 12 | [D08](#D08), [D02](#D02) |
| `test_tools.py` | 4 | [D10](#D10) |
| `test_notebooks_integration.py` | 20 | Chạy thật các notebook trong bản sao, chặn mạng: [D01](#D01), [D02](#D02), [D07](#D07), [D08](#D08), [D11](#D11); NB01, NB02, NB03, NB05 chạy lại ra đúng output đã commit |

## 5. Nhãn, mẫu, chia tập, baseline: có đổi không

| Mục | Có đổi? | Chi tiết |
|---|---|---|
| Định nghĩa nhãn | **Có** | Nguồn nhãn là AQI raw của ngày lịch *t*+1, thay cho AQI của bảng sạch hồi cứu. Trên 8.663 khoá chung, không nhãn nào đổi giá trị |
| Tập mẫu | **Có** | 8.663 thành 8.668: thêm 5 mẫu, đều ở train (5.741 thành 5.746; ngày nặng 1.432 thành 1.436); không mất mẫu nào |
| Test và 03–07/2020 | Không | Cùng 1.947 và 975 khoá, cùng nhãn, cùng giá trị đặc trưng |
| Chia tập | Không | Cùng mốc, chia theo ngày được dự đoán |
| Định nghĩa ba mức đặc trưng | Không | Cùng 20 cột |
| Giá trị đặc trưng | **Có**, chỉ ở train | 63 ô trên các khoá chung: `co_0` 35, `aqi_wk` 22, `aqi_2` 4, `aqi_1` 2 |
| Ba baseline | Không đổi cách tính | "Ngày mai = hôm nay" không đổi (MAE test 23,47). Hai baseline học trên train đổi nhẹ vì train thêm 5 mẫu: 64,47 thành 64,54 và 43,41 thành 43,44 |
| Cách chọn alpha và ngưỡng | Không | Alpha chọn được không đổi: 10 / 0,1 / 30 (mức 1 / 2 / 3), 10 (cận trên) |
| Ngưỡng F2 chọn được | **Có** | Mức 1 / 2 / 3: 169 / 165 / 166 thành 170 / 166 / 167. "Hôm nay" vẫn 160; cận trên vẫn 164; mô hình cây mức 3: 164 thành 166 |
| Mô hình cây (chỉ để so) | Lưới không đổi | Ở mức 1, phép chọn trên train nay ra 200 cây thay cho 100; MAE test 23,47 thành 23,00 |

Các thay đổi nhãn và mẫu theo đúng RA-DEC-02 và được nêu ở đầu NB06. Dev không đổi gì để tăng điểm test.

## 6. Con số của NB06 trước và sau

"Trước" là NB06 gốc chạy lại trong môi trường này (trùng output tác giả đã commit). "Sau" là NB06 ở `a9757af` với đầu vào đúng snapshot. Bảng đầy đủ từng dòng: `dev_evidence/compare/nb06_original_code_vs_forecast_path.md`.

| Chỉ số (trên test, trừ dòng cuối) | Trước | Sau |
|---|---|---|
| MAE "ngày mai = hôm nay" | 23,47 | 23,47 |
| MAE Ridge mức 1 / 2 / 3 | 22,94 / 20,92 / 19,52 | 22,93 / 20,92 / 19,53 |
| MAE cận trên (thời tiết ngày mai) | 19,08 | 19,10 |
| MAE mô hình cây mức 3 | 18,03 | 18,09 |
| Mức 3 − "hôm nay" | −3,95 (−5,40; −2,56) | −3,94 (−5,39; −2,56) |
| Mức 3 − mức 2 | −1,40 (−1,93; −0,93) | −1,39 (−1,92; −0,92) |
| Mức 3 − mức 1 | −3,42 (−4,56; −2,30) | −3,40 (−4,54; −2,29) |
| Mức 1 − "hôm nay" | −0,53 (−1,19; 0,08) | −0,54 (−1,20; 0,07) |
| Cây mức 3 − Ridge mức 3 | −1,49 (−2,21; −0,70) | −1,44 (−2,09; −0,73) |
| Mức 3 ở ngưỡng 201: TP / FP / FN | 346 / 40 / 43 | 346 / 40 / 43 |
| Mức 3 ở ngưỡng F2: ngưỡng; TP / FP / FN | 166; 377 / 113 / 12 | 167; 377 / 107 / 12 |
| Precision của mức 3 ở ngưỡng F2 | 0,769 | 0,779 |
| So cùng cách chọn ngưỡng, mức 3 − "hôm nay": precision | +0,046 (0,024; 0,074) | +0,056 (0,035; 0,083) |
| So cùng cách chọn ngưỡng, mức 3 − "hôm nay": recall | +0,008, khoảng chứa 0 | +0,008, khoảng chứa 0 |
| Precision nhóm Jaipur và Amritsar, mức 3 ở ngưỡng F2 | 0,49 | 0,52 |
| MAE 03–07/2020, mức 3 | 13,78 | 13,77 |

Số dòng validation dùng để chọn ngưỡng: 4.592 (1.193 ngày nặng) thành 4.596 (1.196). Các kết luận định tính của NB06 giữ nguyên chiều: mức 3 hơn "hôm nay" và hơn mức 2 với khoảng 95% không chứa 0; ở cảnh báo, lợi thế nằm ở precision chứ không ở recall.

## 7. Kiểm thử đã chạy và chưa chạy

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Kiểm thử đơn vị và tích hợp | 210 đạt, 1 bỏ qua, mã thoát 0 | `dev_evidence/pytest/pytest_full.log`, `junit.xml` | Khoảng 6 phút |
| NB04, NB05, NB06 với thời tiết baseline | 3/3 chạy trọn; 0 lần thử mạng; `data/` không đổi | `dev_evidence/chains/baseline/` | |
| NB04, NB05, NB06 với thời tiết do NB04 tạo | 3/3 chạy trọn; NB05, NB06 đọc đúng file mới | `dev_evidence/chains/nb04/` | |
| NB01, NB02, NB03, NB05 | 4/4 chạy trọn; output dạng chữ trùng bản đã commit | `dev_evidence/chains/eda/`, `compare/*_committed_vs_rerun.md` | Dòng khác còn lại: dấu `\` và `/` trong đường dẫn hình ở NB05, và cảnh báo của matplotlib trên stderr ở NB03; 0 con số khác |
| Cả sáu notebook nối tiếp, thời tiết mới | 6/6 chạy trọn | `dev_evidence/chains/all6_nb04/` | NB01 ghi lại bảng sạch **của bản sao**; repo không đổi |
| Output đã commit trong NB04 và NB06 | Trùng lần chạy lại | `dev_evidence/compare/committed_outputs_*.log` | |
| Đối chiếu sơ bộ với bản tham chiếu DA đã khoá (`13e93ae`) | 26/26 phép so khớp | `dev_evidence/da_crosscheck/crosscheck_da_reference.tsv` | **Do Dev chạy; không thay cho kiểm chứng của DA.** Xem dưới |
| API Open-Meteo thật | ❓ Không đủ bằng chứng | `pytest_full.log`, dòng `SKIPPED` | Bị chặn ở sandbox |
| Python khác 3.11.2; hệ điều hành khác Linux | ❓ Không đủ bằng chứng | — | Không có trong sandbox |
| Chạy notebook bằng giao diện Jupyter | Chưa chạy | — | Chỉ chạy bằng nbclient |

**Về phép đối chiếu sơ bộ.** Sau khi khoá mã ở `75c69dd`, Dev đọc giao thức và công cụ DA đã công bố ở `13e93ae`, rồi chạy chính mã tham chiếu của DA (`r2_ref_asof.py`, `r2_protocol.py`, không import `src/`) để so với mã Dev: 9 đặc trưng trên toàn bộ 14.056 dòng raw; tập khoá, AQI(*t*), nhãn và split; 67 hàng kỳ vọng viết tay của hai bộ ca biên, gồm bộ raw bị xoá dòng; và alpha, ngưỡng, MAE, RMSE, R², số đếm cảnh báo, hiệu MAE kèm khoảng 95% do bộ máy tính metric của DA tính trên bảng mẫu của Dev. Tất cả khớp. Sau khi đọc các tài liệu đó, Dev **chỉ thêm test** (commit `a9757af`); `src/`, notebook và công cụ không đổi. Mục đích là báo sớm nếu hai bên hiểu khác nhau; kết luận thuộc về DA.

## 8. Chưa làm và giới hạn

- **API thật.** Không kiểm được đường tải online với Open-Meteo. Mock chỉ cho biết mã xử lý đúng các phản hồi đã giả lập.
- **Phiên bản Python.** Chỉ kiểm trên 3.11.2.
- **Tài liệu của nhóm chưa được cập nhật** theo các thay đổi ở D02, D05, D07: xem mục 10. Dev không sửa các file đó vì thuộc phần việc của BA.
- **Hình của EDA và NB05** không được tạo lại.
- **`src/model_utils.py` dòng 113** còn cảnh báo `Series.dt.dayofyear` của pandas. File thuộc đường hồi cứu nên Dev không sửa; cảnh báo không ảnh hưởng kết quả.
- **Độ nhạy với các điểm nghi lỗi được giữ lại.** Ngoài phép so B và C, chưa có phân tích riêng.
- **F03, F04, F05** (nội dung, thuộc BA và DA) không nằm trong phần việc của Dev.
- Phiên của Dev không có file PDF bài giữa kỳ và không đọc nó.

## 9. Tương thích với nhánh EDA và cách quay lui

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| File trong `data/` | Không file nào đổi | tree `data` = `6e5d738d` ở cả `cd719cf` và `a9757af` | |
| `01_cleaning`, `02_cleaning_evidence`, `03_eda`, `05_weather_correlation`; `model_utils.py`, `eda_utils.py`, `utils.py`, `gap_utils.py` | Không đổi | `git diff --stat cd719cf a9757af` | |
| `pipeline.py` | Đổi 2 chỗ (D09); kết quả trên dữ liệu thật như cũ | `test_pipeline_guard.py` | |
| `corr_utils.py` | Đường dẫn bảng thời tiết lấy từ `data_paths`; mặc định vẫn là file cũ | D02 | |
| NB01–NB03, NB05 chạy lại | Output dạng chữ và số hình trùng bản đã commit | `test_retrospective_notebooks_still_reproduce_the_committed_outputs` | |
| Bảng sạch do NB01 ghi lại trong bản sao | Khác byte so với bản đã commit; phép kiểm tự động khẳng định mọi ô lệch không quá 1e-9 | `test_retrospective_cleaning_reproduces_committed_table`; `chains/eda/chain_summary.json` | Dev đo tay trên bản sao của chuỗi `eda`: 680 ô số khác, lệch lớn nhất 1,1e-13, tất cả là ô nội suy (cờ `_was_missing`); vị trí NaN và mọi cột không phải số trùng nhau. `pipeline.py` chỉ đổi hai chỗ ở D09 và hàm đó cho kết quả như cũ, nên độ lệch này không do bản sửa. Các bảng NB01 ghi vào `reports/` trùng từng byte |

Quay lui toàn bộ: `git revert` sáu commit của Dev theo thứ tự ngược. Quay lui riêng NB06 và NB04 về bản gốc:

```bash
git checkout cd719cf -- Air-Project-main/notebooks/04_weather_merge.ipynb Air-Project-main/notebooks/06_predict_aqi.ipynb \
    Air-Project-main/reports/figures Air-Project-main/src/weather_utils.py Air-Project-main/src/corr_utils.py Air-Project-main/src/pipeline.py
```

Các file mới (`forecast_utils.py`, `data_paths.py`, `tests/`, `tools/`) không ảnh hưởng đường cũ khi không được import. Không cần quay lui dữ liệu vì không file dữ liệu nào bị đổi.

## 10. Việc cần BA đồng bộ tài liệu

Dev không sửa các file dưới đây. Nội dung nên chờ số đã được DA kiểm.

| File, vị trí | Hiện ghi | Thực tế sau bản sửa |
|---|---|---|
| `README.md` dòng 31; `docs/CHECKLIST_KIEM_CHUNG.md` CK-2.4, CK-4.7 | `pip install -r Requirements.txt`; danh sách thư viện có `jupyter`; lệnh kiểm `jupyter nbconvert --execute` | `Requirements.txt` vẫn cài được và nay ghim 12 thư viện. Muốn đúng môi trường đã kiểm thì cài `requirements-lock.txt` trên Python 3.11.2. `jupyter` và `nbconvert` không nằm trong môi trường đó; notebook được chạy bằng `tools/run_notebook.py` và `tools/run_chain.py` |
| `README.md` dòng 20, 42; `Data_dictionary.md` dòng 57, 78, 79; `Metadata.json` dòng 131, 132; `reports/cleaning_log_8cities.md` dòng 20, 44 | NB04 tạo hai file trong `data/processed/` | NB04 ghi output mới vào `outputs/nb04/`. Hai file trong `data/processed/` là baseline đã commit, không bị ghi đè |
| `README.md` dòng 20 | "12 cột thời tiết" | Bảng ghép có 14 cột thời tiết (các tài liệu khác và NB04 đều ghi 14). Sai khác này có từ trước vòng sửa |
| `README.md` dòng 46 | `05` và `06` cần kết quả của `04`; `04` cần mạng ở lần chạy đầu | `04` không cần mạng khi 8 cache đã có trong repo. `05` và `06` mặc định đọc baseline đã commit. `06` đọc raw, không cần chạy `01` trước |
| `README.md` dòng 35 | Chạy từng notebook bằng *Restart & Run All* | Vẫn chạy được. Nên biết: chạy `01` trong repo sẽ ghi lại `data/processed/air_quality_8cities.csv`. `tools/run_chain.py` chạy trong bản sao |
| `README.md` dòng 44; `docs/CHECKLIST_KIEM_CHUNG.md` CK-3.13, CK-4.6 | Chống rò rỉ bằng `mask_interp` và `make_features(as_of=…)` | NB06 dùng `forecast_utils`: đặc trưng và nhãn từ raw, as-of *t*; phép thử cắt và làm nhiễu đi từ raw |
| Mọi chỗ dẫn số của NB06 | Số của đường cũ | Bảng ở mục 6, sau khi DA kiểm |
| Mọi chỗ dùng hình `model_01`–`model_04` | Hình cũ | Hình đã đổi (D11) |

## 11. Vấn đề mới gửi RA

Dev không sửa các điểm dưới đây vì chúng nằm ở nhánh hồi cứu, ngoài phần việc được giao.

<a id="NEW-R2-001"></a>
**NEW-R2-001 — Hai trong 41 ô "nghi lỗi cảm biến" không phải số đo.** `reports/suspect_points_8cities.csv` có 93 dòng: 41 dòng "đặt NaN" và 52 dòng "giữ nguyên". Ở 2 trong 41 dòng "đặt NaN", raw không có giá trị: PM2.5 của Amritsar ngày 09/05/2017 (`value_original` 850,7) và của Bengaluru ngày 07/07/2017 (256,0). Trong `pipeline.clean_city`, luật nghi lỗi chạy **sau** bước nội suy, nên giá trị bị coi là nghi lỗi rồi bị xoá ở hai ô này là số do nội suy tạo ra, không phải số đo. Ngoài ra `value_original` là giá trị đã làm tròn một chữ số thập phân: ở 39 dòng còn lại nó bằng raw sau khi làm tròn, và chỉ trùng raw từng chữ số ở 22 dòng. Ảnh hưởng: câu "41 ô nghi lỗi (22 PM2.5 + 19 AQI)" ở `reports/cleaning_log_8cities.md` dòng 34 và tên cột `value_original`. Đường dự báo không bị ảnh hưởng. Bằng chứng: `dev_evidence/pytest/suspect_cells_without_raw_observation.csv`, `suspect_cells_observed_vs_interpolated.csv`.

<a id="NEW-R2-002"></a>
**NEW-R2-002 — Ba con số của giả thuyết H1 ở NB05 đổi khi tốc độ gió lệch 0,01.** Với bảng thời tiết do NB04 tạo lại (852 ô lệch tối đa 0,01, D03), bảng kiểm giả thuyết của NB05 đổi ở ba chỗ: cận trên khoảng 99,67% của Gurugram 41,8 thành 42,1; của Jaipur 7,7 thành 7,2; p Mann-Whitney (tham khảo) của Jaipur 0,447 thành 0,386. Hiệu ứng, cỡ nhóm và cả 15 kết luận không đổi. Nguyên nhân có thể là nhóm "gió yếu" và "gió mạnh" chia theo phân vị ba của `wind_speed_mean`, nên lệch 0,01 đủ để vài ngày đổi nhóm; Dev chưa kiểm trực tiếp điều này. Bằng chứng: `dev_evidence/compare/nb05_baseline_weather_vs_nb04_weather.md`.

## 12. Danh mục bằng chứng

Mọi file trong `dev_evidence/` do `run_evidence.sh` tạo ở `a9757af`. Đường dẫn dưới đây tính từ `dev_evidence/`.

| File hoặc thư mục | Nội dung |
|---|---|
| `run_evidence.sh`, `crosscheck_da_reference.py` | Hai script đã chạy; sha256 của chúng ghi trong `environment.txt` |
| `steps.tsv` | Từng bước: lệnh và mã thoát |
| `environment.txt`, `environment_vs_lock.diff`, `pip_check.log` | Commit, trạng thái cây làm việc, tree git, phiên bản, `pip freeze` |
| `pytest/pytest_full.log`, `pytest/junit.xml` | Kết quả 211 ca |
| `pytest/*.csv` | Bảng do test ghi: bảng giữ mẫu, số mẫu hai đường, khoá thêm bớt, đặc trưng khác trên khoá chung, số 0 treo, hai phép thử rò rỉ, ô nghi lỗi, ô thời tiết khác baseline, ba phép so |
| `pytest/chain_*.log`, `pytest/chain_*_summary.json` | Các chuỗi notebook do test chạy |
| `chains/<tên>.log`, `chains/<tên>/chain_summary.json`, `provenance.jsonl` | Năm chuỗi: `baseline`, `nb04`, `eda`, `nb06_only`, `all6_nb04` |
| `chains/nb06_only/nb06_outputs/` | Toàn bộ output của NB06 với đầu vào đúng snapshot: `nb06_run_summary.json`, `nb06_predictions.csv`, `nb06_cohort_keys.csv`, `nb06_cohort_diff.csv`, `nb06_retention.csv`, `nb06_masking_summary.csv`, `nb06_masked_cells.csv`, `nb06_feature_diff_cells.csv`, `nb06_path_comparison*.csv`, `nb06_alerts_test.csv`, `nb06_snapshot_checks.csv` |
| `chains/nb04/nb04_outputs/` | `nb04_manifest.json`, `nb04_vs_committed_cells.csv` (852 ô), `nb04_vs_committed_summary.csv` |
| `chains/nb04/nb06_outputs/`, `chains/all6_nb04/nb06_outputs/` | Các bảng nhỏ của NB06 khi dùng thời tiết mới |
| `compare/*.md`, `compare/*.log` | So output dạng chữ giữa các lần chạy |
| `compare/nb06_figures_old_vs_new.tsv` | 5 hình: sha256 ở `cd719cf`, trong repo, khi chạy lại; số điểm ảnh khác |
| `compare/determinism_between_runs.txt` | Các lần chạy khác nhau cho file output trùng từng byte; sha256 của các output lớn không commit |
| `orig/original_nb06.log` | NB06 gốc chạy lại trong môi trường này |
| `da_crosscheck/` | Đối chiếu sơ bộ với bản tham chiếu của DA |

Không commit: bản sao dự án của từng chuỗi, notebook đã chạy, và hai bảng output lớn của NB04 (`weather_daily_8cities.csv` 1,5 MB, `air_quality_8cities_weather.csv` 4,4 MB). sha256 của chúng nằm trong `compare/determinism_between_runs.txt`; chạy lại `run_evidence.sh` sẽ tạo lại.
