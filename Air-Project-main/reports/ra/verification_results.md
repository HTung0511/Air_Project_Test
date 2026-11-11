# Kết quả kiểm chứng — DA → RA

Ngày 11/11/2026 · phiên bản 1.0 · người chạy: AI-3 Data Analyst · commit `ccd0a63`
Trả lời hợp đồng trong [open_questions.md](open_questions.md). Môi trường, lệnh và hash ở [reproduction_log.md](reproduction_log.md). Phân tích bổ sung ở [supplementary_analysis.md](supplementary_analysis.md).

DA chỉ báo số đo được. Mọi đánh giá phương pháp và quyết định cuối thuộc về RA; thay đổi checklist thuộc về BA.

**Cách đọc cột Kết quả.** ✅ pass: số của DA bằng số kỳ vọng. ⚠️ partial: tái lập được nhưng có điều kiện, có chênh lệch, hoặc chỉ kiểm được một phần. ❌ fail: số của DA khác điều tài liệu khẳng định. ⛔ blocked: không chạy được trong môi trường này.
**Đường dẫn.** File bằng chứng nằm trong `evidence/`; script trong `evidence/scripts/`. "NB" là notebook, "c" là số ô.

## Tóm tắt theo câu hỏi

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Q01 / P0 — tái tạo pipeline | ✅ pass | [V01](#V01) | 0 ô khác bảng sạch đã commit; mọi số đếm trong log làm sạch khớp. |
| Q02 / P0 — `as_of` và rò rỉ | ⚠️ partial | [V05](#V05), [V06](#V06), [V07](#V07) | Bước làm sạch có dùng dữ liệu sau ngày t. Ảnh hưởng đo được: 40 dòng train, 0 dòng test, 0 dòng holdout; số liệu mô hình đổi ở chữ số thập phân thứ ba. |
| Q03 / P0 — thiếu dữ liệu, ngưỡng, luật nghi lỗi | ⚠️ partial | [V08](#V08), [V09](#V09), [S05](supplementary_analysis.md#S05) | 10 cấu hình làm sạch không đổi thứ hạng thành phố và kết luận mô hình. Sai số nội suy đo bằng giả lập là 23–37% trung vị PM2.5 cho khoảng 1–14 ngày. |
| Q05 / P0 — ba phát hiện EDA | ⚠️ partial | [V14](#V14)–[V17](#V17) | Số của tác giả tái lập đúng. Ba nhóm thành phố bền; thứ hạng trong nhóm không bền; số 51% của Delhi phụ thuộc cửa sổ thời gian (51–65%). Cặp "2,8× / 137 so với 42" không cùng một phép tính. |
| Q04 / P1 — thời tiết | ⚠️ partial | [V10](#V10), [V11](#V11) | Phần offline đạt. Bảng ngày sinh lại lệch 852 ô ở chữ số thập phân thứ hai. Phần gọi API bị chặn. |
| Q06 / P1 — tương quan và giả thuyết | ⚠️ partial | [V18](#V18), [V19](#V19) | 32/48 và 3/1/11 tái lập đúng. Kết luận 15 phép so sánh không đổi theo cách hiệu chỉnh 3 hay 15. Bỏ giai đoạn COVID làm 7–9 trong 48 hệ số đổi trạng thái ý nghĩa. |
| Q07 / P1 — dự báo và cảnh báo | ⚠️ partial | [V20](#V20)–[V24](#V24) | Số trên tập test tái lập đúng. Trên holdout, mô hình **chưa tách** khỏi "ngày mai = hôm nay". Giờ phát hành dữ liệu thật không kiểm được. |
| Q08 / P2 — bản nộp, đạo đức, trình bày | ⛔ blocked phần lớn | [V25](#V25) | 15/15 hình có mặt. Không có báo cáo, slide, biên bản, mục quyền riêng tư, khai báo AI, danh mục tài liệu tham khảo trong repo. |
| Q09 / P2 — đối chiếu checklist | ✅ đã đối chiếu, chờ BA | [V26](#V26) | DA xác nhận các điểm lệch RA nêu và bổ sung chi tiết. |
| Vấn đề mới | 5 mục | [NEW-001](#NEW-001) … [NEW-005](#NEW-005) | **Cần RA đánh giá bổ sung.** |

---

<a id="V01"></a>
## V01 — [Q01] Tái tạo pipeline làm sạch từ raw và cân đối số ô

Nguồn gốc: `src/pipeline.py`, `src/utils.py`, `src/gap_utils.py`; NB01. Script: `v01_pipeline.py`. Bảng đầy đủ 46 dòng expected/actual: [V01_pipeline_reproduction.csv](evidence/V01_pipeline_reproduction.csv).

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.3, CK-2.4 / Q01 — raw và lọc 8 thành phố | ✅ pass | V01_pipeline_reproduction.csv dòng 0–6 | 29.531 dòng, 26 thành phố → 14.056 dòng. 0 cặp (City, Date) trùng, 0 ngày đứt, 0 giá trị âm. Ô thiếu raw 16.953 (10,05%). |
| CK-2.12, CK-4.7 / Q01 — so từng ô với bảng sạch đã commit | ✅ pass | [V01_cell_diff_vs_baseline.csv](evidence/V01_cell_diff_vs_baseline.csv) | Kích thước 14056×40, cùng thứ tự cột. 0 ô khác ở sai số 1e-9, 0 ô lệch NaN. 680 ô khác ở mức bit (lớn nhất 1,14e-13), do số học dấu phẩy động. |
| CK-2.7, CK-2.8, CK-2.10 / Q01 — cờ và kiểu dữ liệu | ⚠️ partial | dòng 12–13, 44–45 | 12 cờ `_was_missing`, 11 cờ `_is_outlier`: khớp. 24 cờ bool đọc lại đúng kiểu. `pm25_gt_pm10_flag` đọc lại thành `object`, không còn là boolean. |
| CK-2.5, CK-2.6 / Q01 — flatline và nội suy | ✅ pass | dòng 17–18 | Flatline 0 → NaN: 2.169 ô (Benzene 646, Toluene 615, CO 540, NOx 368). Ô nội suy còn giá trị: 3.329. |
| CK-2.9 / Q01 — luật nghi lỗi | ✅ pass | dòng 19–22; [V01_suspect_41_decomposition.csv](evidence/V01_suspect_41_decomposition.csv) | 93 điểm được xét, 41 ô đặt NaN (PM2.5 22, AQI 19), 24 ngày, 7 thành phố. 93 dòng trùng từng ô với `suspect_points_8cities.csv`. |
| CK-2.8, CK-2.10 / Q01 — cờ IQR và tỉ lệ PM2.5/PM10 | ✅ pass | dòng 23–25 | 6.656 ô cờ IQR (PM2.5 531); 139 cờ PM2.5 > 1,2×PM10. |
| CK-2.14 / Q01 — cân đối số ô thiếu | ✅ pass | dòng 28–33 | Cuối cùng 15.832 ô thiếu (9,39%); AQI thiếu 836. Trong 41 ô nghi lỗi: 39 là giá trị thật bị xoá (NaN mới), 2 là ô vốn thiếu, đã nội suy rồi bị xoá lại. Cân đối: 16.953 + 2.169 − 3.329 + 39 = 15.832. Không cộng 41 như 41 NaN mới. |
| CK-2.13, CK-2.14 / Q01 — `cleaning_summary_8cities.csv` | ✅ pass | dòng 34–42 | 104 hàng. 11 hàng `dung_lam_bien_mo_hinh=False`: 8 là Xylene (đã bỏ cột) và 3 là cột thật (Gurugram NH3 92,9%; Lucknow PM10 100%; Chennai PM10 84,5%). Tổng nội suy, flatline, NaN thêm, IQR đều khớp. |

<a id="V05"></a>
## V05 — [Q02] Cắt raw ở ngày t rồi làm sạch lại, so với bản đầy đủ

Nguồn gốc: NB06 c6; `model_utils.make_features(as_of=)`; `pipeline.apply_suspect_rule`; `utils.impute_time_series`. Script: `v02_asof.py`.

Bối cảnh đo được: `make_features(as_of=)` cắt **bảng đã làm sạch**, không cắt raw. Phép kiểm của tác giả vì vậy không thấy được việc bước làm sạch có dùng dữ liệu tương lai hay không. DA cắt raw ở 17 ngày (3 ngày notebook dùng, cộng các ngày sát điểm nghi lỗi, biên flatline, biên khoảng thiếu, ranh train/test), chạy lại toàn bộ làm sạch, rồi so mọi ô có ngày ≤ t.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.13 / Q02 — giá trị đã làm sạch (11 chất + AQI) tại ngày ≤ t giống bản đầy đủ | ❌ fail | [V05_asof_cut_summary.csv](evidence/V05_asof_cut_summary.csv), [V05_asof_cut_cell_changes.csv](evidence/V05_asof_cut_cell_changes.csv) | Kỳ vọng 0 ô đổi. Thực tế 96 ô đổi qua 17 lần cắt. 12 lần cắt từ 14/06/2017 đến 15/09/2018 có 1–30 ô đổi; 5 lần cắt từ 01/12/2018 trở đi có 0 ô đổi. |
| Q02 — đường đi gây đổi | — | cột `duong_di` | 63 ô: khoảng thiếu vắt qua t, đầu mút phải nằm sau t (nội suy). 27 ô: chuỗi số 0 vắt qua t, chỉ đủ 3 ngày khi thấy tương lai (flatline). 4 ô: luật nghi lỗi chọn top-5 toàn chuỗi và cửa sổ căn giữa nên đổi theo dữ liệu sau t. 2 ô: khác. |
| CK-3.10, CK-3.13 / Q02 — đặc trưng L3 của dòng `Date == t` (đúng phép kiểm của NB06) | ⚠️ partial | cột `NB06_test_tai_Date==t` | 16/17 lần cắt: 0 ô đổi. 1 lần cắt (30/07/2017): 1 ô đổi (`co_0`). |
| CK-3.13 / Q02 — AQI tại t, nhãn y, số dòng giữ lại | ✅ pass | cột `AQI_tai_t_doi`, `nhan_y_doi`, `dong_giu_lai_*` | 0 thay đổi ở cả 17 lần cắt. |
| CK-4.6 / Q02 — 3 ngày notebook đã thử | ✅ pass | 3 dòng tương ứng trong bảng tóm tắt | Ba ngày NB06 c6 đã thử là 01/12/2018, 15/11/2019, 10/01/2020. Cả ba cho 0 ô đổi, khớp kết quả notebook. Cả ba nằm sau ngày cuối cùng có ô đổi (15/09/2018). |

<a id="V06"></a>
## V06 — [Q02] Nhiễu dữ liệu sau ngày t

Script: `v02_asof.py` phần B.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.13 / Q02 — thêm đỉnh giả sau t, ô sạch ≤ t có đổi không | ⚠️ partial | [V06_future_perturbation.csv](evidence/V06_future_perturbation.csv) | 3 kịch bản: nhân 6 lần PM2.5 và AQI trong 6 ngày tháng 7/2019 ở Gurugram và Jaipur (t = 01/12/2018); nhân 3 lần trong 6 ngày tháng 12/2019 ở Delhi (t = 15/11/2019). Cả 3: 0 ô sạch đổi, 0 ô đặc trưng L3 và AQI đổi. |
| Giới hạn của phép thử | — | — | Chỉ 3 kịch bản, và đỉnh giả cách t từ 1 đến 7 tháng. Phép thử này **không** phủ trường hợp dữ liệu ngay sau t thay đổi; trường hợp đó đã cho thấy có ảnh hưởng ở V05. Không dùng V06 làm bằng chứng rằng pipeline là nhân quả. |

<a id="V07"></a>
## V07 — [Q02] Walk-forward: làm sạch lại ở mọi ngày t và biến thể "thời gian thực"

Script: `v02b_walkforward.py`, `v07c_realtime_model.py`. Với mỗi ngày t trong khoảng chung, DA cắt raw ở t, làm sạch, lấy đặc trưng của dòng `Date == t`. Ghép lại thành bảng đặc trưng "thời gian thực" rồi so với bảng của tác giả.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.13 / Q02 — số dòng (thành phố, ngày) có ít nhất 1 đặc trưng L3 khác | ❌ fail so với "giống hệt" | [V07_walkforward_feature_diff.csv](evidence/V07_walkforward_feature_diff.csv), [V07_walkforward_feature_diff_cells.csv](evidence/V07_walkforward_feature_diff_cells.csv) | 57/8.912 dòng (0,64%). Trong mẫu mô hình: 40/8.663, **tất cả thuộc train**. Test 0/1.947. Holdout 0/975. |
| Q02 — theo đặc trưng | — | như trên | `co_0` 50 ô (chênh lớn nhất 0,875), `aqi_wk` 5 ô (0,36), `pm25_0` 2 ô (2,39). `AQI`, `aqi_0`, `aqi_1` mỗi cột 2 ô và `aqi_2` 1 ô: bản của tác giả có giá trị, bản thời gian thực là NaN. 14 đặc trưng thời tiết và mùa: 0 ô. |
| CK-2.9 / Q02 — quyết định của luật nghi lỗi theo thời gian | ⚠️ partial | [V07_walkforward_suspect_decisions.csv](evidence/V07_walkforward_suspect_decisions.csv) | 49 ô từng bị cờ. 41 ô vẫn là nghi lỗi ở bản cuối. 8 ô **bị xoá ở thời gian thực nhưng được giữ ở bản cuối**, trong đó 4 ô nằm trong khoảng chung: Bengaluru 01/05/2018 AQI 352 (bị cờ 5 ngày); Gurugram 14/07/2017 AQI 497 và PM2.5 723,2 (2 ngày); Gurugram 16/07/2017 PM2.5 812,5 (40 ngày). Độ trễ từ sự kiện đến khi bị cờ: 0–4 ngày trong khoảng chung. |
| CK-3.13, CK-4.6 / Q02 — mô hình trên đặc trưng thời gian thực, cùng giao thức | ✅ pass (kết luận không đổi) | [V07_realtime_variant_metrics.csv](evidence/V07_realtime_variant_metrics.csv) | Train 5.740 thay vì 5.741 (mất dòng Bengaluru 01/05/2018). Alpha không đổi. MAE test L3 19,517 so với 19,519; L2 20,915 so với 20,919. L3 − hôm nay: −3,949 [−5,41; −2,56] so với −3,947 [−5,40; −2,56]. Holdout L3 13,779 so với 13,783. Recall và precision cảnh báo giống nhau đến 4 chữ số. Ngưỡng F2 của L1 đổi 169 → 170. |
| Phạm vi còn hở | — | — | Walk-forward dùng raw **như đã công bố**; không mô phỏng được việc CPCB sửa số liệu sau khi phát hành. Thời tiết lấy từ ERA5 đã hoàn chỉnh. |

<a id="V08"></a>
## V08 — [Q03] Bảng thiếu dữ liệu 8 thành phố × cột, độ dài khối, độ phủ theo năm tháng

Nguồn gốc: NB02 c28, c30; `utils.impute_time_series`. Script: `v08_missing_sensitivity.py`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.5, CK-2.6 / Q03 — thiếu ở raw, sau flatline, sau nội suy và luật nghi lỗi | ✅ đã lập | [V08_missing_by_city_column.csv](evidence/V08_missing_by_city_column.csv) | Mỗi dòng một cặp (thành phố, cột): số ô thiếu ở từng bước, số khối và độ dài khối, số ô thiếu ở đầu chuỗi. |
| CK-2.13, CK-5.2 / Q03 — cột gần như không có dữ liệu | — | cột `co_che` | Lucknow PM10 thiếu 100%; Gurugram NH3 92,9%; Chennai PM10 85,0%. DA ghi cột thiếu 100% là "không nhận diện được cơ chế" và hai cột thiếu ≥ 80% là "gần như không đo". DA không gán MAR hay MNAR cho cột nào. |
| Q03 — độ dài khối AQI thiếu ở raw | — | cột `khoi_raw_*` | 110 khối 1–3 ngày; 24 khối 4–14 ngày; 7 khối 15–60 ngày; 4 khối trên 60 ngày (dài nhất 411 ngày). |
| CK-3.1, CK-5.6 / Q03 — độ phủ theo năm, tháng | ✅ đã lập | [V08_coverage_by_year_month.csv](evidence/V08_coverage_by_year_month.csv) | Gurugram: AQI có 0% năm 2015 và 64,8% năm 2016. Đây là lý do khoảng chung bắt đầu từ 2017. |
| Q03 — độ dài khoảng thực sự được nội suy | — | [S05_actual_interpolated_gap_lengths.csv](evidence/S05_actual_interpolated_gap_lengths.csv) | 3.329 ô: 14% thuộc khoảng 1 ngày, 24% thuộc 2–3 ngày, 30% thuộc 4–7 ngày, 32% thuộc 8–14 ngày. Không có khoảng nào trên 14 ngày. |

<a id="V09"></a>
## V09 — [Q03] Độ nhạy theo ngưỡng flatline, `max_gap`, luật nghi lỗi

Script: `v08_missing_sensitivity.py`. 10 cấu hình, mỗi cấu hình làm sạch lại từ raw, tính lại EDA và chạy lại mô hình với cùng giao thức. AQI không bao giờ được điền.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.5 / Q03 — flatline ≥ 2, 5, 7 ngày (gốc: 3) | ✅ kết luận không đổi | [V09_cleaning_sensitivity.csv](evidence/V09_cleaning_sensitivity.csv) | Số ô đổi so với gốc: 179, 309, 384; không ô AQI nào đổi. MAE L3: 19,519; 19,519; 19,521 (gốc 19,519). |
| CK-2.6 / Q03 — `max_gap` 0, 7, 30, 60 ngày (gốc: 14) | ✅ kết luận không đổi | như trên | Số ô đổi: 3.334; 1.053; 1.101; 2.580. Ô thiếu cuối: 19.162; 16.885; 14.731; 13.252. Tỉ số PM2.5: 2,816; 2,830; 2,855; 2,923. Spearman PM2.5–AQI 0,907–0,904. MAE L3 (có che ô nội suy): 19,514; 19,519; 19,519; 19,519. |
| Q03 — vì sao `max_gap` gần như không tác động đến mô hình | — | cột "không che ô nội suy" | Mô hình chính đặt ô nội suy về NaN trước khi tạo đặc trưng, nên đổi `max_gap` không vào được mô hình. Đây **không** phải bằng chứng rằng nội suy chính xác. Khi bỏ che, MAE L3 nằm trong 19,45–19,57. Sai số nội suy đo trực tiếp ở [S05](supplementary_analysis.md#S05). |
| CK-2.9 / Q03 — luật nghi lỗi: hiện tại, chỉ gắn cờ, không áp dụng | ✅ kết luận không đổi | như trên | 41 ô khác. Khi giữ các điểm nghi lỗi: 8.738 ngày có AQI (gốc 8.734), 1.853 ngày nặng (gốc 1.850), Gurugram 46,36% (gốc 46,26%), MAE L3 19,530. |
| CK-3.7 / Q03 — thứ hạng 8 thành phố và số của Delhi | ✅ pass | [V09_cleaning_sensitivity_eda_detail.csv](evidence/V09_cleaning_sensitivity_eda_detail.csv) | Thứ hạng giống nhau ở cả 10 cấu hình. Delhi 51,04% ở cả 10. |
| CK-3.15 / Q03 — hiệu MAE và cảnh báo | ✅ pass | V09_cleaning_sensitivity.csv | L3 − hôm nay nằm trong −3,94 đến −3,95 với CI [−5,41; −2,56] ở mọi cấu hình có che. L3 ở ngưỡng 201: recall 0,8895, precision 0,8964, không đổi. |
| Điểm đổi đáng ghi | ⚠️ | cột alpha | Alpha của L2 nhảy từ 0,1 lên 30 ở hai cấu hình (flatline ≥ 7 và `max_gap` 0). MAE L2 gần như không đổi, tức mặt sai số theo alpha phẳng. |

<a id="V10"></a>
## V10 — [Q04] Cache thời tiết theo giờ

Nguồn gốc: NB04 c6–27; `src/weather_utils.py`. Script: `v04_weather.py`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.2 / Q04 — 8 file cache, lưới giờ, trùng, trống | ✅ pass | [V10_weather_cache_checks.csv](evidence/V10_weather_cache_checks.csv), [V10_weather_pipeline_checks.csv](evidence/V10_weather_pipeline_checks.csv) | 8 file × 48.384 giờ = 387.072 dòng, đúng bằng số giờ lịch 25/12/2014–01/07/2020. 0 giờ trùng, 0 ô trống ở 6 biến lõi và BLH. BLH có đủ ở 8 file (NB05, NB06 dùng `blh_mean`). |
| CK-2.2 / Q04 — múi giờ | ✅ pass (kiểm gián tiếp) | dòng "giờ nóng nhất" | Giờ nóng nhất trung bình là 14h ở cả 8 thành phố. Nếu chuỗi là UTC, đỉnh sẽ rơi vào 8–9h. |
| CK-2.2 / Q04 — toạ độ lưới và metadata | ✅ pass | dòng 10–12 | Delhi (28,5; 77,25) và Gurugram (28,5; 77,0) là hai ô lưới khác nhau. Lệch toạ độ tối đa 0,12°. `Metadata.json` khớp toạ độ trong cache. |
| CK-2.2 / Q04 — tải lại từ API, `smoke_test()` | ⛔ blocked | [reproduction_log.md](reproduction_log.md) mục 5 | Máy chạy không ra được `archive-api.open-meteo.com`. Không kiểm được cache có trùng dữ liệu API hiện nay. |
| CK-4.7 / Q04 — NB04 chạy offline | ❌ fail | NB04 c6 | Notebook luôn gọi mạng trước khi đọc cache; khi không có mạng thì dừng ở ô c6. |

<a id="V11"></a>
## V11 — [Q04] Bảng thời tiết theo ngày và bảng gộp

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.15 / Q04 — bảng ngày: số hàng, đủ 24 giờ mỗi ngày, giới hạn vật lý | ✅ pass | V10_weather_pipeline_checks.csv dòng 13–21 | 16.128 hàng (8 × 2.016 ngày). Mỗi ngày đủ 24 giờ. 0 ô trống, 0 vi phạm `check_ranges`. |
| CK-2.15 / Q04 — sinh lại từ cache so với file đã commit | ⚠️ partial (lệch nhỏ) | [V11_weather_daily_independent_recompute.csv](evidence/V11_weather_daily_independent_recompute.csv) | 852/193.536 ô số khác (0,44%), chênh lớn nhất 0,01. Ở các cột `temp_mean` 335, `pressure_mean` 348, `wind_speed_mean` 169. Cả 852 ô có trung bình chưa làm tròn nằm đúng biên x,xx5; phiên bản numpy/pandas khác nhau làm tròn lên hoặc xuống. Cột min, max, tổng, u, v, BLH, `rain_day`, `wind_dir_8` không lệch. |
| Q04 — DA tự tính lại mean, min, max, tổng mưa, u, v | ✅ pass | như trên | Lệch tối đa 0,01 so với file đã commit, cùng nguyên nhân. Dấu u/v và hướng gió 8 phương nhất quán. |
| CK-2.15 / Q04 — bảng gộp | ✅ pass | V10_weather_pipeline_checks.csv | 14056×54; 0 ô thời tiết thiếu; 40 cột chất lượng không khí trùng từng ô với bảng sạch. |
| Hệ quả ở hạ nguồn | ⚠️ | [reproduction_log.md](reproduction_log.md) mục 3 | Chạy NB05, NB06 trên bảng sinh lại làm 3 con số CI và 1 ô ma trận nhầm lẫn của HistGradientBoosting đổi. Ridge không đổi. Xem [NEW-004](#NEW-004). |

<a id="V14"></a>
## V14 — [Q05] Phát hiện "ở đâu": tỉ lệ ngày nặng theo thành phố

Nguồn gốc: NB03 phần A, c42–43; `eda_utils.load`. Script: `v14_eda.py`. "Ngày nặng" là ngày AQI ≥ 201. Mẫu số là số ngày **có AQI** của thành phố trong cửa sổ.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.1, CK-3.4 / Q05 — tái lập số của tác giả (khoảng chung 14/06/2017–01/07/2020) | ✅ pass | [V14_eda_share_by_window.csv](evidence/V14_eda_share_by_window.csv) | 8.734 ngày có AQI, 1.850 ngày nặng. Delhi 564/1.105 = 51,0%; Lucknow 516/1.111 = 46,4%; Gurugram 495/1.070 = 46,3%; Amritsar 117/1.029 = 11,4%; Jaipur 121/1.093 = 11,1%; Chennai 34/1.110 = 3,1%; Bengaluru 2/1.108 = 0,2%; Hyderabad 1/1.108 = 0,1%. |
| CK-3.4, CK-5.6 / Q05 — số 51% của Delhi theo cửa sổ | ⚠️ partial | như trên, 6 cửa sổ | Toàn chuỗi: 65,1%. Trước 01/03/2020 (mốc holdout trong code): 56,6%. Trước 25/03/2020 (ngày phong toả toàn quốc): 55,6%. Chỉ ngày cả 8 thành phố cùng có AQI (964 ngày): 52,2%. Ba năm tròn 01/07/2017–30/06/2020: 51,8%. |
| CK-3.7 / Q05 — thứ hạng theo cửa sổ | ⚠️ partial | cột `thu_hang` | Delhi đứng đầu ở cả 6 cửa sổ. Vị trí 2 và 3 đổi: Lucknow trên Gurugram ở 3 cửa sổ, Gurugram trên Lucknow ở 3 cửa sổ (toàn chuỗi, trước 01/03/2020, trước 25/03/2020). |
| CK-3.7, CK-5.3 / Q05 — bỏ ngẫu nhiên 10% × 200 lần | ✅ pass | [V14_eda_drop10_x200.csv](evidence/V14_eda_drop10_x200.csv) | Delhi 49,3–53,1%, khớp số tác giả. Tỉ lệ số lần giữ nguyên hạng: Delhi và Chennai 100%; Lucknow và Gurugram 59%; Amritsar và Jaipur 76%; Bengaluru và Hyderabad 93%. Tức **3 cặp** đổi chỗ, đúng như CK-3.7 liệt kê. |
| CK-3.7 / Q05 — bootstrap khối lịch chung 7, 14, 28 ngày | ⚠️ partial | [V14_eda_block_bootstrap.csv](evidence/V14_eda_block_bootstrap.csv), [V14_eda_block_bootstrap_rank.csv](evidence/V14_eda_block_bootstrap_rank.csv) | CI 95% của Delhi: [44,1; 57,7], [41,8; 59,8], [38,8; 62,9]. Ba nhóm (cao, giữa, thấp) giữ nguyên ở ≥ 99,95% số lần. Thứ hạng đầy đủ 1–8 chỉ giữ ở khoảng 20% số lần. |
| Q05 — hiệu giữa các thành phố (điểm phần trăm) | — | V14_eda_block_bootstrap_rank.csv | Delhi − Gurugram 4,8: CI [0,3; 9,2] với khối 7 ngày, [−0,9; 10,3] với 14 ngày, [−2,4; 11,4] với 28 ngày. Delhi − Lucknow 4,6 [0,9; 8,3] với 28 ngày. Với khối 7 ngày: Lucknow − Gurugram 0,2 [−4,5; 4,8]; Amritsar − Jaipur 0,3 [−2,9; 3,3]; Bengaluru − Hyderabad 0,1 [−0,2; 0,4]. |
| Q05 — bản chỉ gắn cờ điểm nghi lỗi | ✅ pass | [V09](#V09) | Gurugram 46,36% thay vì 46,26%; các thành phố khác không đổi ở 1 chữ số thập phân. |

<a id="V15"></a>
## V15 — [Q05] Phát hiện "khi nào": mùa đỉnh

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.2, CK-3.5 / Q05 — tháng đỉnh và mức chênh | ✅ pass | [V15_eda_month_median.csv](evidence/V15_eda_month_median.csv), [V15_eda_peak_months.csv](evidence/V15_eda_peak_months.csv) | Delhi: trung vị tháng 12 là 376, tháng 8 là 98. Tháng đỉnh: Delhi 12; Gurugram, Lucknow, Jaipur, Amritsar 11. |
| CK-3.5 / Q05 — ngày nặng tập trung vào mùa nào | ✅ pass | [V15_eda_heavy_days_by_month.csv](evidence/V15_eda_heavy_days_by_month.csv), [V15_eda_aqi_days_by_month.csv](evidence/V15_eda_aqi_days_by_month.csv) | 73,2% ngày nặng rơi vào tháng 10–2; 35,2% vào tháng 11–12. Tỉ lệ ngày tháng 11–12 là ngày nặng: Delhi 96,2%, Lucknow 96,2%, Gurugram 89,0%, Jaipur 29,0%. |
| CK-3.5 / Q05 — độ bền của tháng đỉnh | ⚠️ partial | [V15_eda_peak_month_by_season_year.csv](evidence/V15_eda_peak_month_by_season_year.csv), [V15_eda_peak_month_bootstrap.csv](evidence/V15_eda_peak_month_bootstrap.csv) | Xác suất bootstrap tháng đỉnh thuộc {11, 12, 1}: Lucknow 100%, Delhi 99,8%, Gurugram 99,0%, Jaipur 86,2%, Amritsar 86,0%, Bengaluru 45,0%. Khoảng chung chỉ có 3 mùa đông. |
| Điểm lệch khỏi mô tả chung | ⚠️ | V15_eda_heavy_days_by_month.csv | Gurugram có 46 ngày nặng trong tháng 6. Toàn chuỗi (không phải khoảng chung) thì tháng 10–2 chiếm 63,4% chứ không phải 73,2%. |

<a id="V16"></a>
## V16 — [Q05] Phát hiện "chất nào": PM2.5

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.6 / Q05 — tỉ số trung vị PM2.5 ngày nặng / ngày còn lại, từng thành phố | ✅ pass | [V16_eda_pollutant_by_city.csv](evidence/V16_eda_pollutant_by_city.csv) | Delhi 2,99 [2,49; 3,63]; Gurugram 2,47 [2,14; 2,93]; Lucknow 3,13 [2,48; 3,60]; Jaipur 2,06 [1,88; 2,29]; Amritsar 2,82 [2,48; 3,28]. Trung vị của 5 tỉ số: 2,82 [2,42; 3,17]. Khớp "2,1–3,1×, trung vị 2,8×". |
| CK-3.6 / Q05 — "137 so với 42 µg/m³" | ❌ fail về cách ghép số | [V16_eda_pollutant_summary.csv](evidence/V16_eda_pollutant_summary.csv) | 137,1 và 42,0 là hai trung vị **gộp cả 8 thành phố**. Tỉ số của chúng là 3,26, không phải 2,8. Số 2,8 là trung vị của 5 tỉ số tính riêng từng thành phố. CK-3.6 đặt hai con số cạnh nhau như cùng một phép tính. |
| CK-3.6 / Q05 — Spearman với AQI | ✅ pass | như trên | PM2.5 0,91 (gộp); theo thành phố 0,69 (Chennai) đến 0,96. NO2 0,52; CO 0,48. |
| Q05 — các chất khác và trường hợp ngược | — | như trên | Tỉ số trung vị (cùng cách tính): NO2 1,66; CO 1,62; SO2 1,09; O3 1,06. Có 225/1.850 ngày nặng mà PM2.5 dưới 91 µg/m³. |
| Q05 — cách gọi tên | — | — | Các tỉ số trên so nồng độ giữa hai nhóm ngày. Chúng không đo phần đóng góp của PM2.5 vào AQI; dữ liệu không có chỉ số con từng chất. |

<a id="V17"></a>
## V17 — [Q05] Độ phủ của 26 thành phố trong raw

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.1, CK-3.4 / Q05 — 8 thành phố được chọn đứng ở đâu theo số ngày có AQI | ✅ đã lập | [V17_coverage_26_cities.csv](evidence/V17_coverage_26_cities.csv) | 8 thành phố được chọn xếp hạng 1, 2, 3, 4, 5, 7, 10, 11 trong 26. |
| Q05 — thành phố có độ phủ tương đương nhưng không được chọn | — | như trên | Patna: hạng 6, 1.459 ngày có AQI, 53,5% ngày ≥ 201. Ahmedabad: hạng 8, 1.334 ngày, 81,9% ngày ≥ 201. Visakhapatnam: hạng 9, 1.171 ngày. Thiruvananthapuram: hạng 12, 1.052 ngày. |
| Giới hạn | — | — | Bảng chỉ cho biết độ phủ. Quy tắc chọn 8 thành phố không có trong repo; cần tác giả hoặc BA xác nhận. DA không suy ra lý do chọn. |

<a id="V18"></a>
## V18 — [Q06] 48 hệ số tương quan thời tiết–AQI

Nguồn gốc: NB05 c5; `corr_utils.add_anomalies`, `boot_corr`, `corr_table`, `bh_adjust`. Script: `v18_corr.py`. Bảng 48 dòng có rho thô, rho sau khi bỏ mùa, CI 95% chưa hiệu chỉnh, p bootstrap, q theo Benjamini–Hochberg, n, số khối: [V18_corr_48_coefficients.csv](evidence/V18_corr_48_coefficients.csv).

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.8 / Q06 — tái lập 48 hệ số và "32/48" | ✅ pass | V18_corr_48_coefficients.csv | 32/48 có q < 0,05. Ma trận rho sau khi bỏ mùa trùng bảng NB05 c5 ở 2 chữ số. Mỗi hệ số dùng 1.029–1.111 ngày, 83–84 khối. 18/48 hệ số đổi dấu khi bỏ mùa. Trung vị trị tuyệt đối của rho trên **5 thành phố đủ ngày nặng**: độ ẩm 0,33; nhiệt độ 0,23; mưa 0,17; áp suất 0,16; lớp biên 0,10; gió 0,09 (khớp số tác giả, lớp biên lệch 0,01 do làm tròn). Trên cả 8 thành phố: 0,32; 0,22; 0,17; 0,13; 0,08; 0,10. |
| CK-3.8 / Q06 — q < 0,05 so với "CI 95% loại trừ 0" | ⚠️ partial | cột `q_BH<0.05`, `CI95_loai_0` | 33/48 có CI 95% chưa hiệu chỉnh loại trừ 0; 32/48 có q < 0,05. Ô lệch: Bengaluru–mưa, rho −0,087, CI [−0,170; −0,003], p 0,039, q 0,057. Notebook viết "32/48 hệ số có khoảng tin cậy loại trừ 0 sau hiệu chỉnh FDR": tiêu chí thật là q, không phải CI. Với Bonferroni cho 48 phép thử: 24/48. |
| Q06 — độ phân giải của p bootstrap | ⚠️ | log script | B = 4.000 nên p nhỏ nhất có thể là 0,0005. 24/48 hệ số chạm sàn này. |
| Q06 — xếp hạng lại trong mỗi lần bootstrap so với cách xấp xỉ giữ hạng cố định của tác giả | ✅ pass | cột `rerank_*` | Với B = 1.000 và xếp hạng lại: vẫn 32/48 có q < 0,05 và 33/48 có CI loại trừ 0. Biên CI lệch tối đa 0,014. 0 hệ số đổi kết luận. |
| CK-3.8 / Q06 — khối 7 và 28 ngày (gốc 14) | ✅ pass | [V18_corr_sensitivity_summary.csv](evidence/V18_corr_sensitivity_summary.csv) | Khối 7 ngày: 33/48 (thêm Bengaluru–mưa). Khối 28 ngày: 32/48, cùng 32 ô. |
| CK-3.8 / Q06 — bỏ mùa theo tuần thay vì theo tháng | ⚠️ partial | như trên | Vẫn 32/48 nhưng 6 ô đổi trạng thái (3 mất, 3 thêm) và 1 ô đổi dấu. Chênh rho lớn nhất 0,17. Delhi–nhiệt độ tăng từ 0,23 lên 0,41; Delhi–áp suất từ −0,16 xuống −0,29. |
| CK-3.15 / Q06 — bỏ giai đoạn COVID | ⚠️ partial | như trên | Trước 01/03/2020: 31/48; 9 ô đổi trạng thái (5 mất, 4 thêm); 3 ô đổi dấu. Trước 25/03/2020: 33/48; 7 ô đổi trạng thái; 2 ô đổi dấu. Năm ô mất ý nghĩa khi cắt ở 01/03/2020: Delhi–áp suất, Lucknow–nhiệt độ, Lucknow–lớp biên, Lucknow–áp suất, Jaipur–áp suất. Bốn ô thêm ý nghĩa: Lucknow–gió, Bengaluru–mưa, Bengaluru–áp suất, Chennai–gió. |
| CK-3.8 / Q06 — độ ẩm | ✅ pass | như trên | Âm ở cả 8 thành phố và q < 0,05 ở cả 8, trong **cả 6 biến thể**. |
| CK-3.8 / Q06 — lớp biên ở Delhi | ✅ pass | như trên | 0,08 [−0,03; 0,19]; CI chứa 0 ở cả 6 biến thể (từ −0,02 đến 0,08). |
| Q06 — suy luận gộp có giữ phụ thuộc cùng ngày giữa các thành phố | ✅ đã tính | [V18_corr_pooled_median_common_blocks.csv](evidence/V18_corr_pooled_median_common_blocks.csv) | Trung vị rho của 5 thành phố, bootstrap khối lịch chung 14 ngày: nhiệt độ 0,23 [0,13; 0,33]; độ ẩm −0,33 [−0,40; −0,22]; gió −0,09 [−0,15; −0,03]; lớp biên 0,10 [0,02; 0,19]; mưa −0,17 [−0,23; −0,12]; áp suất −0,16 [−0,26; −0,08]. 48 hệ số riêng từng thành phố không cần xử lý này. |

<a id="V19"></a>
## V19 — [Q06] 3 giả thuyết × 5 thành phố

Nguồn gốc: NB05 c10; `corr_utils.tertile_in_strata`, `compare_groups`, `boot_median_diff`. Script: `v18_corr.py`. Hiệu ứng là hiệu hai trung vị của AQI đã bỏ mùa (điểm AQI), nhóm bất lợi trừ nhóm thuận lợi.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.8 / Q06 — tái lập bảng 15 phép so sánh | ✅ pass | [V19_hypothesis_tests_summary.csv](evidence/V19_hypothesis_tests_summary.csv) | 3 ủng hộ, 1 ngược chiều, 11 chưa đủ bằng chứng. Delhi H1 (gió yếu) 30,0 [9,6; 50,2]; Jaipur H3 (không mưa) 17,2 [7,0; 30,0]; Amritsar H3 16,0 [3,5; 27,8]; Jaipur H2 (lớp biên thấp) −25,0 [−41,3; −11,0]. Trùng số tác giả. |
| CK-3.8 / Q06 — họ phép thử 15 (notebook) so với 3 mỗi thành phố (checklist) | ✅ kết luận không đổi | cột kết luận "family15" và "family3/TP" | CI 99,67% (chia 15) và CI 98,33% (chia 3) cho cùng kết luận ở cả 15 phép: 3 / 1 / 11. Lựa chọn họ phép thử không ảnh hưởng kết quả. Checklist và phụ lục ghi "Bonferroni cho 3 tests, α = 0,05/3"; notebook dùng 15. |
| Q06 — nếu không hiệu chỉnh (CI 95%) | — | cột kết luận "không hiệu chỉnh" | 7 ủng hộ, 2 ngược chiều, 6 chưa đủ. Bốn phép thêm vào "ủng hộ" là Delhi H3, Lucknow H3, Gurugram H1, Gurugram H3; phép thêm vào "ngược chiều" là Lucknow H2. Dòng này để tham khảo, không phải kết quả chính. |
| Q06 — độ ổn định theo seed 0–9 | ✅ pass | [V19_hypothesis_tests_all_runs.csv](evidence/V19_hypothesis_tests_all_runs.csv) | Cả 15 phép giữ nguyên kết luận ở 10/10 seed. |
| Q06 — khối 7 và 28 ngày | ✅ pass | V19_hypothesis_tests_summary.csv | Cả 15 phép giữ nguyên kết luận. |
| CK-3.15 / Q06 — bỏ giai đoạn COVID | ✅ pass | [V19_hypothesis_tests_drop_covid.csv](evidence/V19_hypothesis_tests_drop_covid.csv) | Trước 01/03/2020 và trước 25/03/2020: cả 15 phép giữ nguyên kết luận. |
| Q06 — độ chính xác của đuôi CI | ⚠️ | log script | Với B = 2.000, mỗi đuôi của CI 99,67% dựa trên khoảng 3,3 mẫu bootstrap. Biên CI vì thế dao động theo seed (xem cột "seed 0–9: biên"), dù kết luận không đổi. |
| Q06 — p Mann–Whitney | — | cột `p_MW` | Có trong bảng để đối chiếu. 11/15 phép có p < 0,05 theo Mann–Whitney, so với 4/15 có CI bootstrap khối (đã hiệu chỉnh) loại trừ 0. DA không dùng nó để kết luận vì nó giả định các ngày độc lập. |
| Q06 — H2 (lớp biên thấp → AQI cao hơn) | — | bảng tóm tắt | Hiệu ứng âm ở cả 5 thành phố (−5,5 đến −25,0), tức ngược chiều dự đoán; chỉ Jaipur có CI loại trừ 0. |

<a id="V20"></a>
## V20 — [Q07] Chia tập, cross-validation, nguồn gốc của các lựa chọn

Nguồn gốc: NB06 c9, c10; `src/model_utils.py`. Script: `v20_model.py`.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.10 / Q07 — kích thước 3 tập và số ngày nặng | ✅ pass | [V20_model_split_checks.csv](evidence/V20_model_split_checks.csv), [V20_model_split_by_city.csv](evidence/V20_model_split_by_city.csv) | Train 5.741, test 1.947, holdout 975. Ngày nặng: 1.432, 389, 18. Ngày được dự đoán: train đến 30/06/2019; test 01/07/2019–29/02/2020; holdout 01/03/2020–01/07/2020. |
| CK-3.13 / Q07 — mọi lựa chọn chỉ dùng train | ✅ pass | V20_model_split_checks.csv dòng 8–10 | Alpha (L1 10, L2 0,1, L3 30, L4 10) và tham số HistGradientBoosting chọn bằng CV trong train. Ngưỡng F2 chọn trên dự đoán out-of-fold của train (4.592 dòng, 1.193 ngày nặng): hôm nay 160, L3 166. Imputer, scaler, encoder nằm trong `Pipeline`, fit trên train. |
| CK-3.10 / Q07 — ranh giới từng fold và khoảng cách thực tế | ⚠️ partial | [V20_model_cv_folds.csv](evidence/V20_model_cv_folds.csv) | Khoảng cách giữa fit và val là 16 **dòng**, tương đương 2–3 **ngày lịch** (vì 8 thành phố). Đặc trưng `aqi_wk` nhìn lùi 7 ngày. Ở cả 4 fold, AQI của những ngày cuối phần fit nằm trong cửa sổ đặc trưng của các dòng val đầu tiên. Đây là dùng quá khứ làm đặc trưng, không phải dùng tương lai; nhưng khoảng cách không tách hẳn hai phần như tên gọi gợi ý. |
| CK-3.9 / Q07 — có hồi quy với CO, NO2 trong X | ⚠️ partial | `model_utils.POLL_FEATS`; [V21](#V21) | Mức L2 thêm `pm25_0`, `no2_0`, `co_0`, `so2_0`, `o3_0`. Biến đích là **AQI ngày mai**, không phải PM2.5 cùng ngày như tên tiêu chí; checklist ghi "PM2.5 (hoặc AQI)". DA có MAE, RMSE, R²; DA không xuất bảng hệ số hồi quy. |
| Q07 — đặc trưng của test lấy từ ngày thuộc train | — | V20_model_split_checks.csv dòng 7 | 8 dòng test của ngày đầu dùng AQI ngày 30/06/2019. Bình thường với dự báo một bước. |

<a id="V21"></a>
## V21 — [Q07] Sai số hồi quy trên tập test

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.11, CK-3.12 / Q07 — MAE của 3 baseline và 5 mô hình | ✅ pass | [V21_model_test_metrics.csv](evidence/V21_model_test_metrics.csv), [V21_model_test_predictions.csv](evidence/V21_model_test_predictions.csv) | n = 1.947. Trung bình thành phố 64,47; trung vị cùng tháng 43,41; ngày mai = hôm nay 23,47; Ridge L1 22,94; L2 20,92; L3 19,52; L4 (cận trên, dùng thời tiết ngày mai) 19,08; HistGradientBoosting L3 18,03. Lệch so với số tác giả ≤ 0,005. File có thêm RMSE và R². |
| CK-3.12, CK-3.15, CK-3.16 / Q07 — hiệu MAE cùng mẫu, CI bootstrap khối lịch 14 ngày | ✅ pass | [V21_model_paired_mae_diff.csv](evidence/V21_model_paired_mae_diff.csv) | L3 − hôm nay −3,95 [−5,40; −2,56]. L3 − L2 (thêm thời tiết) −1,40 [−1,93; −0,93]. HGB − L3 −1,49 [−2,21; −0,70]. L1 − hôm nay −0,53 [−1,19; 0,08]: chưa tách khỏi 0. |
| Q07 — "23,5 so với 19,5" và "thời tiết khoảng −1,4" | ✅ pass | như trên | Khớp. |
| CK-3.14 / Q07 — sai số trên ngày nặng | ⚠️ | V21_model_test_metrics.csv | MAE của L3 là 39,77 trên ngày nặng và 14,46 trên ngày còn lại. Độ chệch của L3 trên ngày nặng là −21,69 (dự đoán thấp hơn thực tế). |

<a id="V22"></a>
## V22 — [Q07] Cảnh báo ngày nặng trên tập test

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.14 / Q07 — ma trận nhầm lẫn, ngưỡng 201 | ✅ pass | [V22_model_alerts_test.csv](evidence/V22_model_alerts_test.csv) | 389 ngày nặng / 1.947. Hôm nay: TP 333, FP 59, FN 56; recall 0,856, precision 0,850. Ridge L3: TP 346, FP 40, FN 43; recall 0,890, precision 0,896. |
| CK-3.14 / Q07 — ngưỡng F2 | ✅ pass | như trên | Hôm nay ở 160: recall 0,961, precision 0,723. L3 ở 166: recall 0,969, precision 0,769 (TP 377, FP 113, FN 12). |
| CK-3.14 / Q07 — hiệu cùng mẫu | ⚠️ partial | [V22_model_alert_paired_diff.csv](evidence/V22_model_alert_paired_diff.csv) | Ở ngưỡng 201: recall +0,033 [0,003; 0,068], precision +0,047 [0,033; 0,065]. Ở ngưỡng F2: recall +0,008 [−0,010; 0,029], **chưa tách khỏi 0**; precision +0,046 [0,024; 0,074]. |

<a id="V23"></a>
## V23 — [Q07] Phân rã theo thành phố, mùa, tháng, ngày nặng

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.14, CK-3.15 / Q07 — L3 − hôm nay theo thành phố | ⚠️ partial | [V23_model_by_city.csv](evidence/V23_model_by_city.csv) | Delhi −7,40; Gurugram −7,03; Lucknow −6,44; Amritsar −4,62; Jaipur −1,20 [−3,21; 0,47], chưa tách khỏi 0. Chi tiết và nguyên nhân ở [S02](supplementary_analysis.md#S02). |
| CK-3.15 / Q07 — theo mùa | ✅ đã lập | [V23_model_by_season.csv](evidence/V23_model_by_season.csv), [V23_model_by_month.csv](evidence/V23_model_by_month.csv), [V23_model_by_city_season.csv](evidence/V23_model_by_city_season.csv) | Tháng 7–9: −1,17. Tháng 12–2: −6,05. Tập test không có tháng 3–6. |
| CK-3.15 / Q07 — ngày nặng so với ngày còn lại | ✅ đã lập | [V23_model_by_heavy.csv](evidence/V23_model_by_heavy.csv) | Xem V21. |

<a id="V24"></a>
## V24 — [Q07] Holdout (ngày được dự đoán từ 01/03/2020)

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.11, CK-3.12 / Q07 — MAE trên holdout | ✅ đã lập | [V24_model_holdout_metrics.csv](evidence/V24_model_holdout_metrics.csv) | n = 975, 18 ngày nặng. Hôm nay 14,80; L1 14,09; L2 13,88; L3 13,78; L4 13,68; HGB 13,51. |
| CK-3.15 / Q07 — hiệu cùng mẫu | ❌ không tách khỏi baseline | [V24_model_holdout_paired_diff.csv](evidence/V24_model_holdout_paired_diff.csv) | L3 − hôm nay −1,02 [−2,70; 0,48]. Từ 25/03/2020: −0,37 [−2,16; 1,37]. Trên holdout, mô hình **chưa** cho thấy tốt hơn "ngày mai = hôm nay". |
| CK-3.14 / Q07 — cảnh báo trên holdout | ⚠️ partial | [V24_model_holdout_by_period.csv](evidence/V24_model_holdout_by_period.csv), [S06](supplementary_analysis.md#S06) | Chỉ 18 ngày nặng. Ở ngưỡng 201: hôm nay bắt 5/18, L3 bắt 6/18. Mẫu quá nhỏ để kết luận. |
| Q07 — tên gọi mốc thời gian | — | — | 01/03/2020 là mốc cắt trong code. Phong toả toàn quốc bắt đầu 25/03/2020. DA báo riêng hai mốc ở mọi bảng. |
| Q07 — dữ liệu "hôm nay" có sẵn lúc phát tin không | ⛔ blocked | — | Repo không có tài liệu về giờ CPCB công bố AQI ngày và độ trễ của ERA5; máy chạy không ra mạng. Mọi con số ở V21–V24 là đánh giá **hồi cứu** trên dữ liệu đã hoàn chỉnh. |
| Q07 — tập test đã bị nhìn nhiều lần | — | NB06 | Tác giả đã chạy phân tích độ nhạy trên test (bỏ Gurugram, bỏ biến mùa). DA cũng dùng test cho các phân tích bổ sung. Không lựa chọn mô hình nào của DA dựa trên test. |

<a id="V25"></a>
## V25 — [Q08] Kiểm kê hình và tài liệu nộp

Script: `v25_docs.py`. DA chỉ kiểm sự có mặt và đo thuộc tính file. DA không chấm chất lượng trình bày.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-3.3 / Q08 — 15 hình (6 EDA, 4 tương quan, 5 mô hình) | ✅ pass | [V25_figures_inventory.csv](evidence/V25_figures_inventory.csv) | Đủ 15/15. Tất cả 150 dpi, 1.200–1.875 px chiều rộng, 67–347 kB. Thư mục còn 6 hình khác; 5 trong số đó là hình cũ 130 dpi. |
| CK-3.3 / Q08 — nhãn, chú thích, nguồn, n trên hình | ⚠️ partial | `eda_01_poor_share_city.png`, `model_02_mae_by_model.png` | DA mới xem 2/15 hình. Cả hai có tiêu đề nêu kết luận, nhãn trục, dòng nguồn và n. Số n trên hình (8.734 ngày; 1.947 cặp) bằng số DA tính ở V14 và V21. 13 hình còn lại chưa xem bằng mắt. |
| CK-4.1, CK-4.2 / Q08 — báo cáo, slide, biên bản | ⛔ không có | [V25_documents_inventory.csv](evidence/V25_documents_inventory.csv) | 0 file PDF, PPTX, DOCX; 0 file tên báo cáo; 0 biên bản vấn đáp; 0 file LICENSE. |
| CK-4.4, CK-4.5 / Q08 — quyền riêng tư, thiên lệch | ⛔ không có | như trên | Chuỗi "quyền riêng tư / privacy": 0 file. Chuỗi "thiên lệch / bias": 0 file (ngoài checklist). |
| CK-4.3 / Q08 — khai báo dùng AI | ❌ thiếu | NB06, ô markdown cuối | Xuất hiện đúng 1 lần, trong câu của tác giả: "Chưa làm ở đây: model card một trang, mục 'khai báo AI' trong README và ethics checklist đầy đủ". |
| CK-2.1, CK-4.3 / Q08 — nguồn, giấy phép, ngày truy cập | ⚠️ partial | như trên | Giấy phép và URL nguồn có ở `Data_dictionary.md`, `Metadata.json`, `README.md`. "Ngày truy cập": 0 file. Mục tài liệu tham khảo: 0 file. Yêu cầu ≥ 5 nguồn ngoài: không tìm thấy danh sách. |
| CK-5.1–CK-5.10 / Q08 — vấn đáp, demo dưới 5 phút | ⛔ blocked | — | Không có bản ghi nào. Notebook chứa nội dung trả lời, nhưng năng lực trả lời của từng thành viên không kiểm được từ repo. |
| CK-1.1–CK-1.6 / Q08 | Không kiểm | — | Thuộc phần đặt bài toán; DA không được giao phép đo nào. |

<a id="V26"></a>
## V26 — [Q09] Đối chiếu checklist của BA

Script: `v25_docs.py`. Bảng: [V26_checklist_crosscheck.csv](evidence/V26_checklist_crosscheck.csv). Các dòng dưới là dữ kiện để BA quyết định; DA không sửa checklist.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Q09 — số tiêu chí | ❌ lệch | V26 dòng 0, 2 | Checklist có 54 mã duy nhất: P1 6, P2 15, P3 16, P4 7, P5 10. `BAN_GIAO_BA-RA.md` ghi "50 tiêu chí" ở 2 chỗ. |
| Q09 — mức B/K | — | V26 dòng 1 | P1 4B + 2K; P2 12B + 3K; P3 12B + 4K; P4 5B + 2K; P5 3B + 1K và 6 mã không ghi mức. |
| Q09 — công thức ngưỡng của P3 | ❌ lệch | checklist dòng 145–147 | Công thức ghi "PASS 6/8 B" và "8/8 B". P3 có 12 mã mức B trong 16 mã. Công thức của P2 ("x/12 B") khớp số mã B của P2. |
| Q09 — "2069 ngày" | ❌ lệch | V26 dòng 4–5; [V01](#V01) | Checklist có 1 chỗ ghi 2069 và 2 chỗ ghi 2169. Số đo được là 2.169, và đơn vị là **ô**, không phải ngày. |
| Q09 — "3 cặp" | ❌ lệch trong CK-5.3 | V26 dòng 6–7; [V14](#V14) | CK-5.3 viết "3 cặp" nhưng liệt kê 2. CK-3.7 liệt kê đủ 3 (thêm Bengaluru↔Hyderabad). Số đo: cả 3 cặp đều có lúc đổi chỗ (giữ hạng 59%, 76%, 93%). |
| Q09 — Bonferroni | ❌ lệch | CK-3.8, phụ lục A; [V19](#V19) | Checklist: "3 tests, α = 0,05/3". Notebook: 15 phép. Kết luận giống nhau theo cả hai cách. |
| Q09 — "2,8× (137 so với 42)" | ❌ lệch | CK-3.6; [V16](#V16) | Hai con số thuộc hai phép tính khác nhau; 137/42 = 3,26. |
| Q09 — "feature phải giống hệt" | ⚠️ | CK-3.13; [V05](#V05), [V07](#V07) | Đúng với phép kiểm của notebook (cắt bảng sạch). Không đúng khi cắt raw: 57 dòng khác, tất cả trước 12/2018. |
| Q09 — gán MAR/MNAR | ⚠️ | CK-5.2; [V08](#V08) | Checklist gán sẵn: Xylene và PM10 Lucknow là MNAR, NH3 Gurugram là MAR. Với cột thiếu 100% hoặc gần 100%, dữ liệu không có thông tin để phân biệt các cơ chế. |
| Q09 — `False` trong bảng tóm tắt có gồm Xylene không | ✅ đã làm rõ | [V01](#V01) | 11 hàng `False` = 8 Xylene + 3 cột thật. |
| Q09 — CI so với BH | ✅ đã làm rõ | [V18](#V18) | 33 theo CI, 32 theo q. |
| Q09 — ngưỡng thiếu ở raw hay ở bảng cuối | ✅ đã làm rõ | [V01](#V01) | Toàn bảng: raw 10,05%, bảng cuối 9,39%. Ví dụ một cột: Chennai PM10 thiếu 85,0% ở raw và 84,5% ở bảng cuối. Checklist cần nói rõ ngưỡng áp cho con số nào. |
| Q09 — tên file hoa/thường | ✅ pass | V26 dòng 11–12 | Checklist dùng `Requirements.txt`, `Data_dictionary.md`, `Metadata.json`, đúng với tên file thật. |
| Q09 — nhánh ghi trong checklist | ⚠️ | V26 dòng 13 | Checklist ghi `arena/ad184e76-air-project-test`. Nhánh DA chạy là `arena/b5aacef3-air-project-test`. |
| Q09 — AQI ngày mai thay cho PM2.5 cùng ngày; miễn phân tích theo giờ | Không kiểm được | — | Đây là quyết định về đề bài của BA. Dữ kiện liên quan: `city_day.csv` chỉ có số liệu theo ngày. |

---

## Vấn đề mới ngoài danh sách của RA

Tất cả các mục dưới đây **cần RA đánh giá bổ sung**.

<a id="NEW-001"></a>
### NEW-001 — Log làm sạch dẫn chứng một notebook không còn trên đường chạy

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.14, CK-4.7 | ❌ | `reports/cleaning_log_8cities.md` bước 11; `notebooks/archive/README.md` | Log viết "10 phép assert ở notebook 07". Notebook 07 hiện là `notebooks/archive/07_merge_8_cities.ipynb`, đã bị thay bằng `01_cleaning.ipynb`. Tái hiện: `grep -n "notebook 07" reports/cleaning_log_8cities.md`. Ảnh hưởng: người đọc log không tìm thấy bằng chứng được dẫn. Không ảnh hưởng số liệu. |

<a id="NEW-002"></a>
### NEW-002 — `pipeline.investigate` lỗi khi chuỗi không có số liệu khí

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.9; ngoài checklist về độ bền code | ❌ | `src/pipeline.py` dòng 60 | Khi một thành phố chưa có giá trị nào ở các cột khí (Jaipur, raw cắt ở 14/06/2017), hàm ném `KeyError`. Tái hiện: chạy `P.apply_suspect_rule` trên Jaipur cắt đến 14/06/2017. Không xảy ra với dữ liệu đầy đủ, nên không ảnh hưởng bảng đã commit. Ảnh hưởng nếu pipeline được chạy tăng dần theo ngày. DA vòng qua trong `da_clean.py`, không sửa `src/`. |

<a id="NEW-003"></a>
### NEW-003 — NB04 cần Python ≥ 3.12, không chạy offline, và được commit không có output

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.2, CK-4.7, CK-5.9 | ❌ | NB04 cell 29; `Requirements.txt` | (1) Ô code cuối dùng dấu nháy kép lồng trong f-string, chỉ hợp lệ từ Python 3.12; trên 3.11 báo `SyntaxError`. (2) `Requirements.txt` không ghi phiên bản Python và không ghim phiên bản thư viện. (3) Notebook được commit với 16 ô code và 0 output, nên không có gì để đối chiếu. (4) Không chạy được khi không có mạng. Tái hiện: `python -c "import ast, json; …"` trên cell 29 với Python 3.11, hoặc `run_notebook.py`. |

<a id="NEW-004"></a>
### NEW-004 — Kết quả phụ thuộc phiên bản thư viện qua bước làm tròn

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-2.15, CK-4.7 | ⚠️ | [V11](#V11); [R_06](evidence/R_06_predict_aqi_output_diff.csv) | Bảng thời tiết ngày làm tròn 2 chữ số; 852 ô nằm đúng biên nên khác nhau giữa các phiên bản. Hệ quả: 1 ô ma trận nhầm lẫn của HistGradientBoosting đổi (TP 388 → 387), 3 biên CI ở NB05 đổi. Ridge và mọi kết luận không đổi. Phạm vi: bất kỳ ai sinh lại dữ liệu trên môi trường khác sẽ không khớp từng ô với file đã commit. |

<a id="NEW-005"></a>
### NEW-005 — Commit đầu vào ghi trong hợp đồng không có trong repo

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Ngoài checklist (truy vết) | ⚠️ | `open_questions.md` dòng 3; `git cat-file -t 1a4f5a56…` | Hợp đồng ghi đầu vào là commit `1a4f5a56f2c3937dfe812b5036634c69c8496897`. Repo chỉ có `b8aba4b` và `ccd0a63`. DA chạy trên `ccd0a63`. Giữa hai commit có trong repo, `src/`, `data/` và notebook không đổi. DA không xác nhận được `1a4f5a56` có cùng nội dung hay không. |
