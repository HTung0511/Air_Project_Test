# Đánh giá notebook — RA giai đoạn 1

Ngày: 11/11/2026 · Vai trò: Research Analyst · **Sơ bộ, chưa phải nghiệm thu cuối**.

## 1. Phạm vi và nguyên tắc bằng chứng

Snapshot đầu vào: `1a4f5a56f2c3937dfe812b5036634c69c8496897`, nhánh `arena/8afd3d48-air-project-test`.
Nguồn BA: [checklist gốc](../../../CHECKLIST_KIEM_CHUNG.md), [brief bàn giao](../../../BAN_GIAO_BA-RA.md). Giữ nguyên cả hai file. Yêu cầu hiện tại của người dùng (tick từng tiêu chí, RA không tự làm DA) được ưu tiên hơn brief cũ nói “không tick”.

Không tìm thấy `checklist_verification.md`, `review_priority.md`, `red_flags.md`; không tự giả định chúng tồn tại. Dùng checklist gốc và ưu tiên RQ2 + RQ3 trong brief §2: **02 → 01 → 03 → 04 → 05 → 06** (thứ tự đọc, không phải thứ tự thực thi). Đã đọc cell source/output lưu của 6 notebook chính và mã hỗ trợ liên quan. Archive không nằm trong pipeline chuẩn theo README; chưa đánh giá từng notebook archive.

`NBxx cN` = notebook mang tiền tố xx trong [`../../notebooks/`](../../notebooks/), **cell index 0-based trong JSON**. Tất cả đường dẫn source khác tính từ `Air-Project-main/`, trừ tài liệu BA ở root repository. Output và hình có sẵn là **bằng chứng tác giả lưu**, không phải DA đã reproduce. RA không chạy notebook, huấn luyện, tải API hoặc thay đổi pipeline/dữ liệu trong lượt này. Không thấy `reproduction_log.md`, `verification_results.md`, `supplementary_analysis.md`: chưa đủ đầu vào cho giai đoạn 2.

✅ chỉ xác nhận đủ bằng chứng tĩnh cho tiêu chí nội dung/thiết kế; ⚠️ có một phần nhưng thiếu kiểm chứng hoặc thiếu điều kiện; ❌ có bằng chứng trực tiếp vi phạm; ❓ không có bằng chứng để quyết định. Không suy “không thấy” thành “không đạt”. Không tính điểm nghiệm thu từ bảng sơ bộ.

## 2. Kết luận sơ bộ theo notebook

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| 02 — cơ sở quyết định missing/outlier (ưu tiên RQ2) | ⚠️ Đạt một phần | c3 audit, c28 block_ratio, c30 suspect | Mô tả pattern khá rõ; không nhận diện chắc MAR/MNAR từ pattern; hai thành phố ví dụ không thay sensitivity 8 TP. Q03. |
| 01 — pipeline làm sạch | ⚠️ Đạt một phần | c3 audit, c7 clean_city; pipeline, utils, gap_utils | Có provenance và assert; heuristic xóa đỉnh cần kiểm độ nhạy và causality của preprocessing. Q01–Q03. |
| 03 — EDA (ưu tiên RQ3) | ⚠️ Đạt một phần | bảng phát hiện A/B/C, c43 tổng hợp | Dùng khoảng chung, chia nhóm, tránh nhân quả là phù hợp; xóa ngẫu nhiên 10% chưa kiểm missing có cấu trúc. Q05. |
| 04 — weather merge | ⚠️ Đạt một phần | c10/12/25 assert, execution_count=null cho toàn bộ code cell | Thiết kế merge/giờ/ngày có kiểm soát; không có output lưu để xác nhận lần chạy. Q04. |
| 05 — correlation | ⚠️ Đạt một phần | c5 bảng raw/anomaly/FDR; c10 bảng 15 so sánh | Trừ median City×Month không đồng nghĩa loại hết mùa/confounding; câu “CI loại 0 sau FDR” không đúng cách mã hiệu chỉnh p-value. Q06. |
| 06 — forecasting | ⚠️ Đạt một phần | c6 as_of; c25 kết quả test; c52–55 sensitivity | Có baseline, tách thời gian và ngưỡng validation; as_of chỉ kiểm feature từ bảng sạch cố định. Chưa chứng minh triển khai thời gian thực. Q02/Q07. |

## 3. Đối chiếu từng tiêu chí BA

BA brief ghi “50 tiêu chí”, nhưng checklist thực tế có **54 ID riêng**: P1=6, P2=15, P3=16, P4=7, P5=10. Không tự sửa trọng số/điểm BA.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| CK-1.1 — Lý do chọn đề tài — thực tiễn, có số liệu | ⚠️ Đạt một phần | README §1–2; NB03 c43 | Có lý do và nguồn; chưa có chương mở đầu đủ số liệu, URL kèm ngày truy cập. |
| CK-1.2 — Vòng đời Khoa học Dữ liệu được nêu & tuân thủ | ⚠️ Đạt một phần | README §4 | Có bảng 6 notebook; chưa map rõ đủ vòng đời gồm đánh giá/triển khai/đạo đức. |
| CK-1.3 — Câu hỏi nghiên cứu chính + 3 câu phụ đo được | ✅ Đạt | NB03 phần câu hỏi; NB05 c1 | Có câu hỏi chính và các phân tích phụ đo được; chỉ xác nhận nội dung. |
| CK-1.4 — Xác định dạng bài toán phân tích | ⚠️ Đạt một phần | NB06 c1, c4 | Có y và metric hồi quy/cảnh báo; chưa có bảng ba dạng đúng yêu cầu BA. |
| CK-1.5 — Mục tiêu, phạm vi, giới hạn được lượng hoá | ⚠️ Đạt một phần | Data_dictionary; cleaning_log §3; NB03 c43 | Phạm vi và hạn chế được nêu; số liệu còn chờ Q01 tái lập. |
| CK-1.6 — Ý nghĩa & ứng dụng thực tế | ⚠️ Đạt một phần | NB05 c1; NB06 phần cảnh báo | Có người dân/cơ quan môi trường và ứng dụng; chưa đủ đoạn ứng dụng ≥100 từ theo BA. |
| CK-2.1 — Nguồn chính được mô tả đầy đủ (5W1H) | ✅ Đạt | Metadata.json các trường nguồn/fields/missing_pct_by_column | Đủ mô tả nguồn tĩnh; không xác nhận độ chính xác bằng tải lại. |
| CK-2.2 — Nguồn thứ hai (thời tiết) có provenance riêng | ⚠️ Đạt một phần | Metadata.weather_source; data/raw/weather/; NB04 c6–10 | Có 8 cache và provenance; NB04 không có output lưu, còn Q04. |
| CK-2.3 — Cấu trúc & định dạng được kiểm chứng | ⚠️ Đạt một phần | NB01 c3, phần assert cuối | Có audit/output lưu; c3 chủ yếu in kiểm tra, không thay được Run All hiện tại (Q01). |
| CK-2.4 — Thu thập bằng Pandas — code chạy được | ⚠️ Đạt một phần | src/*.py; Requirements.txt | Có Pandas trong mã; chưa cài và chạy trong vai RA (Q01). |
| CK-2.5 — Xử lý khuyết thiếu — flatline 0 → NaN | ⚠️ Đạt một phần | utils.flag_flatline_zeros; NB01 c7; cleaning_log bước 1 | Heuristic được triển khai; số ô và độ nhạy chờ Q01/Q03; không khẳng định mọi chuỗi 0 là cảm biến treo. |
| CK-2.6 — Xử lý khuyết thiếu — nội suy khoảng ngắn | ⚠️ Đạt một phần | utils._interpolate_short_gaps; gap_utils.interpolate_short_gaps | Logic giới hạn cả block và không điền AQI có trong mã; 14 ngày chưa được xác thực khoa học (Q03). |
| CK-2.7 — Cờ vết missing (`_was_missing`) đầy đủ | ⚠️ Đạt một phần | utils.impute_time_series; pipeline.merge_cities | Có 12 cờ; cờ được tạo trước suspect-rule nên không phải dấu vết đầy đủ mọi thay đổi (Q01/Q02). |
| CK-2.8 — Xử lý outliers — chỉ đánh dấu, không xoá | ⚠️ Đạt một phần | utils.flag_outliers_iqr; pipeline.clean_city | IQR theo tháng chỉ gắn cờ; phân biệt với suspect-rule có đặt NaN; số ô chờ Q01. |
| CK-2.9 — Điểm nghi lỗi cảm biến — luật minh bạch | ⚠️ Đạt một phần | pipeline.investigate/run_rule; suspect_points_8cities.csv | Luật minh bạch nhưng top-5 toàn chuỗi và cửa sổ tương lai; chưa xác minh lỗi thật (Q02/Q03). |
| CK-2.10 — Nhất quán PM2.5–PM10 — gắn cờ logic | ⚠️ Đạt một phần | pipeline.merge_cities, PM_RATIO=1.2 | Có True/NA và luật; số 139 chờ Q01; tỷ lệ không tự chứng minh lỗi trạm. |
| CK-2.11 — Chuẩn hoá & biến đổi — chưa scale/encode trong file sạch | ✅ Đạt | pipeline.merge_cities; model_utils.make_pipe | Mã tách dữ liệu đơn vị gốc khỏi scaler/encoder của mô hình; xác nhận thiết kế. |
| CK-2.12 — Tích hợp dữ liệu — gộp đúng chuẩn | ⚠️ Đạt một phần | pipeline.merge_cities; NB01 phần gộp/assert | Có concat/category/sort/schema; cần đối chiếu từng ô từ raw (Q01). |
| CK-2.13 — Bỏ cột có thiếu ≥60% khỏi mô hình | ⚠️ Đạt một phần | NB01 summary; model_utils.POLL_FEATS | Không dùng PM10/NH3 trong mô hình; BA cần tách hàng Xylene đã bỏ khỏi phép đếm đúng 3 False (Q01/Q09). |
| CK-2.14 — Có nhật ký làm sạch đo được | ⚠️ Đạt một phần | cleaning_log §2; cleaning_summary_8cities.csv | Có log 17 bước và bảng summary; số dòng/cân đối chờ Q01; không dùng grep số chữ Bước để thay kiểm nội dung. |
| CK-2.15 — Thời tiết — gộp theo ngày đúng múi giờ | ⚠️ Đạt một phần | NB04 c10–25; weather_utils | Có timezone/aggregate/merge assert; chưa chứng minh lần chạy từ cache (Q04). |
| CK-3.1 — Thống kê mô tả 4 họ (W6) theo khoảng chung | ⚠️ Đạt một phần | eda_utils.four_families; NB03 A1 | Có bảng thống kê và output; số liệu chờ Q05. |
| CK-3.2 — Phân tích chuỗi thời gian — mùa & giờ trong ngày | ⚠️ Đạt một phần | NB03 B1–B2; figures/eda_02*, eda_03* | Có mùa/tháng và cùng kỳ năm; AQI theo giờ không thể suy từ dữ liệu ngày. BA xác nhận scope (Q09). |
| CK-3.3 — 5 biểu đồ EDA đạt chuẩn W7 (tick trước khi push) | ⚠️ Đạt một phần | NB03 mã biểu đồ; eda_utils.finish_chart/save_fig | Có cấu trúc biểu đồ và 6 PNG; chưa nghiệm thu mắt thường toàn bộ nhãn/dpi/kích thước (Q08). |
| CK-3.4 — Phát hiện “Ở đâu” (A) có số + confounder + hạn chế | ⚠️ Đạt một phần | NB03 bảng phát hiện A/B/C và c43 | Có số, confounder, hạn chế; chưa xác nhận robustness độc lập; tương quan PM2.5–AQI không phải đóng góp nhân quả (Q05). |
| CK-3.5 — Phát hiện “Khi nào” (B) — mùa & xu hướng năm | ⚠️ Đạt một phần | NB03 bảng phát hiện A/B/C và c43 | Có số, confounder, hạn chế; chưa xác nhận robustness độc lập; tương quan PM2.5–AQI không phải đóng góp nhân quả (Q05). |
| CK-3.6 — Phát hiện “Chất nào” (C) — tương quan & tỉ lệ | ⚠️ Đạt một phần | NB03 bảng phát hiện A/B/C và c43 | Có số, confounder, hạn chế; chưa xác nhận robustness độc lập; tương quan PM2.5–AQI không phải đóng góp nhân quả (Q05). |
| CK-3.7 — Kiểm tra độ nhạy & cỡ mẫu | ⚠️ Đạt một phần | NB03 phần độ nhạy, c43 | Có bỏ 10% dòng ×200; không phải bootstrap khối, không bảo đảm độ bền trước missing có cấu trúc (Q05). |
| CK-3.8 — Tương quan thời tiết–AQI đã khử mùa | ⚠️ Đạt một phần | NB05 c5, c10; corr_utils | Có anomaly/Bonferroni/FDR; residual mùa và family 15 so sánh cần kiểm; FDR p-value không hiệu chỉnh CI 95% (Q06). |
| CK-3.9 — Yêu cầu đề bài: Hồi quy PM2.5 từ CO, NO2 (và các khí khác) | ⚠️ Đạt một phần | model_utils.POLL_FEATS; NB06 | Có AQI ngày mai từ CO/NO2 và chất khác; không phải PM2.5 cùng ngày. BA cho phép hoặc AQI nhưng rubric gốc cần xác nhận Q09. |
| CK-3.10 — Chia train/test theo thời gian (không random) | ⚠️ Đạt một phần | model_utils.TRAIN_END/time_cv; NB06 c9 | Chia theo target date; gap=16 là dòng không phải đúng 2 ngày khi thiếu dòng; kiểm từng fold Q07. |
| CK-3.11 — 3 baseline trước mô hình chính | ⚠️ Đạt một phần | model_utils.baseline_preds; NB06 c25 | Output lưu: persistence MAE 23,5 vs Ridge L3 19,5; chưa được DA tái lập (Q07). |
| CK-3.12 — 3 mức đặc trưng (L1→L3) + Ridge + cây để so sánh | ✅ Đạt | model_utils.LEVELS/make_pipe; NB06 c4 | Có L1–L3, Ridge và HistGBR trong thiết kế. Không đồng nghĩa hiệu quả đã xác nhận. |
| CK-3.13 — Chặn rò rỉ dữ liệu (leakage) | ⚠️ Đạt một phần | model_utils.make_features; NB06 c6; pipeline.run_rule | Mask nội suy và train-only Pipeline hợp lý, nhưng as_of cắt sau dữ liệu sạch nên chưa kiểm leakage end-to-end (Q02). |
| CK-3.14 — Đánh giá đa metric + chẩn đoán phần dư | ⚠️ Đạt một phần | NB06 phần C/E/F; figures/model_01*–05* | Có metrics/chẩn đoán/output lưu; cần tái lập và phân tầng ngày nặng Q07. |
| CK-3.15 — Bootstrap theo khối + kiểm tra độ nhạy | ⚠️ Đạt một phần | corr_utils.block_id; model_utils.calendar_blocks; NB06 c52–55 | Có bootstrap và ablation; mask_interp True/False không phải thử max_gap 14→30/60; còn Q03/Q06. |
| CK-3.16 — Tránh “cận trên giả” (thời tiết ngày mai) | ✅ Đạt | model_utils.LEVELS/LEVEL_NAME; NB06 c4, c28 | L4 gắn nhãn cận trên; L3 không có _next; đã cảnh báo Delhi/Gurugram không độc lập. ERA5 hôm nay vẫn cần xét độ trễ thực tế Q07. |
| CK-4.1 — Báo cáo đúng cấu trúc đề cương (7 mục) | ❓ Không đủ bằng chứng | reports/; README | Không thấy bản báo cáo nộp đủ 7 mục; không dùng notebook thay báo cáo cuối của nhóm (Q08). |
| CK-4.2 — Hình thức: không lỗi chính tả, định dạng nhất quán | ❓ Không đủ bằng chứng | Không có bản nộp/slide template CMC | Chưa kiểm được font, mục lục, số trang, chính tả bản nộp (Q08). |
| CK-4.3 — Trích dẫn nguồn & AI minh bạch | ⚠️ Đạt một phần | Metadata; các hàm provenance/finish_chart | Có ghi nguồn và license thời tiết; chưa thấy khai báo AI đầy đủ và bibliography đáp ứng BA (Q08). |
| CK-4.4 — Bảo mật & quyền riêng tư — đánh giá rủi ro | ❓ Không đủ bằng chứng | Metadata và Data_dictionary | Nguồn tổng hợp city/day; chưa thấy mục quyền riêng tư ≥50 từ của bản báo cáo yêu cầu (Q08). |
| CK-4.5 — Thiên kiến (bias) & công bằng — nêu ≥3 bias | ⚠️ Đạt một phần | cleaning_log §3; NB03 c43; NB06 hạn chế | Nhiều bias được nêu; chưa có quy tắc chọn 8/26 được chứng minh hoặc bảng đầy đủ trong bản nộp (Q05/Q08). |
| CK-4.6 — AI có trách nhiệm — không bịa số, không rò rỉ tương lai | ⚠️ Đạt một phần | NB05 quy ước; NB06 c6; model_utils | Có giới hạn diễn giải và chống leakage; chưa khóa được toàn chuỗi (Q02). |
| CK-4.7 — Tái tạo được (reproducibility) | ⚠️ Đạt một phần | Requirements.txt; README §4; NB04 | Requirements không pin version và statsmodels lặp; NB04 chưa lưu output, chưa có Run All hiện tại (Q01/Q04). |
| CK-5.1 — Vì sao xử lý missing theo cách đó? (flatline→NaN, nội suy ≤14 ngày, AQI không nội suy) | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |
| CK-5.2 — Cơ chế thiếu của cột X (MAR/MCAR/MNAR)? Bằng chứng? | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |
| CK-5.3 — Nếu xoá ngẫu nhiên 10% dòng, kết luận có đổi không? | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |
| CK-5.4 — Biểu đồ này có thể đánh lừa người đọc vội ở chỗ nào? | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |
| CK-5.5 — Confounder hợp lý cho quan hệ vừa mô tả là gì? (câu quyết định điểm diễn giải) | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |
| CK-5.6 — Câu hỏi riêng đề tài: vì sao khoảng chung? ngưỡng 201? tháng 1–6 khi so năm? PM10/NH3 không dùng? | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |
| CK-5.7 — Nói rõ, tự tin, đúng thuật ngữ CSDL | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |
| CK-5.8 — Data Storytelling — mỗi ý gắn 1 biểu đồ | ⚠️ Đạt một phần | NB03 c43; NB05–06 các biểu đồ | Có mạch kể chuyện và phát hiện gắn hình; chưa có slide/bằng chứng thuyết trình Q08. |
| CK-5.9 — Demo sống — pipeline chạy <5 phút | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |
| CK-5.10 — Giải thích mã nguồn & lựa chọn thuật toán | ❓ Không đủ bằng chứng | NB03 bộ câu vấn đáp; source; chưa có biên bản/demo | Có tài liệu chuẩn bị không chứng minh thành viên trả lời đúng hoặc demo <5 phút. CK-5.2 còn cần BA sửa suy diễn cơ chế thiếu (Q08/Q09). |

## 4. Phản biện methodology và red flags gửi DA/BA

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| RF01 — as_of chưa bao trùm raw → clean | ⚠️ Đạt một phần | model_utils.make_features đọc bảng sạch trước rồi cắt; pipeline.investigate dùng nlargest(top=5); gap_utils.contextual_ratio dùng rolling center=True | Mẫu chọn top-5 và quyết định đặt NaN có thể đổi khi xuất hiện tương lai. Cả nhãn AQI có thể bị tác động. Cờ _was_missing tạo trước suspect-rule. Đây là rủi ro có căn cứ mã, **chưa định lượng leakage**. Q02, chặn tuyên bố “không leakage”. |
| RF02 — cơ chế thiếu không thể suy ra chỉ từ block_ratio | ⚠️ Đạt một phần | BA CK-5.2; NB02 c28; NB03 bộ vấn đáp | Thiếu 100% có thể là thiếu cấu trúc/không đo, không tự động MNAR. MAR liên quan phân phối missing có điều kiện trên biến quan sát; pattern thời gian không chứng minh MAR, cũng không loại trừ MNAR. Q03/Q09. |
| RF03 — loại đỉnh làm thay đổi outcome | ⚠️ Đạt một phần | pipeline.investigate/apply_suspect_rule; NB02 c30 | Mùa 10–2 chung cho cả 8 TP có thể xóa sự kiện mùa khác ở miền Nam. AQI bị xóa vì PM2.5 nghi lỗi không chứng minh AQI sai (có thể do chất khác). So raw/flag-only/current; giữ giá trị gốc. Q03/Q05. |
| RF04 — median subtraction chưa là điều chỉnh confounding đầy đủ | ⚠️ Đạt một phần | corr_utils.add_anomalies; NB05 c5 | Vẫn còn trend năm, mùa trong tháng, dị phương sai, phát thải và sai số trạm. Không diễn giải hệ số sau anomaly như ảnh hưởng nhân quả. Q06. |
| RF05 — multiple testing và bootstrap | ⚠️ Đạt một phần | corr_utils.compare_groups/boot_corr/corr_table; NB05 c10 | 3 giả thuyết ×5 TP =15 so sánh; cần nêu family 3 trong mỗi TP hay 15 toàn bảng. BH chạy trên p_boot, CI vẫn percentile 95%, không phải CI đã FDR. boot_corr giữ rank toàn mẫu là xấp xỉ. Q06. |
| RF06 — tính sẵn có thực tế và shift phân phối | ⚠️ Đạt một phần | model_utils.WEATHER_FEATS/LOCK_START; NB06 c7/c49 | ERA5 tái phân tích và AQI tổng hợp cuối ngày chưa chắc sẵn lúc phát cảnh báo; ngày 01/03 là mốc holdout, không đồng nhất ngày bắt đầu phong tỏa 25/03. Q07. |
| RF07 — tính tái tạo và tài liệu BA chưa nhất quán | ⚠️ Đạt một phần | Requirements; BA CK-5.1 vs CK-2.5; CK-3.15; README | 2069 “ngày” vs 2169 “ô”; 50 vs 54 ID; model_utils dùng calendar_blocks chứ không phải định nghĩa block_id riêng. Brief viết Reports/Data nhưng repo dùng reports/data. Ngưỡng 14/60% là lựa chọn đồ án, chưa là chuẩn khoa học. Q09. |

## 5. Bias, tác động và giảm thiểu đề xuất

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Chọn 8/26 thành phố | ⚠️ Đạt một phần | README danh sách; brief RQ1 | Không đại diện Ấn Độ. DA lập bảng coverage 26 TP và quy tắc chọn; RA chỉ khái quát trong 8 TP. |
| Chuỗi dài/ngắn, mùa và COVID | ⚠️ Đạt một phần | NB03 c43; model_utils split | Khoảng chung giảm lệch thời gian, không giải quyết thiếu AQI có hệ thống. DA thử common/pre-COVID/cùng kỳ và báo n. |
| PM10/NH3 thiếu nhiều và nhãn AQI tổng hợp | ⚠️ Đạt một phần | NB03 c42–43 | Không xác định chất “đóng góp” chỉ bằng corr; báo rõ danh sách chất bị loại và mẫu thực tế mỗi thống kê. |
| ERA5 lưới và Delhi/Gurugram gần nhau | ⚠️ Đạt một phần | cleaning_log §3; NB06 c52 | Sai số đo, phụ thuộc không gian. Giữ block ngày chung giữa TP, thử bỏ Gurugram; không coi hai kết quả là hai kiểm chứng độc lập. |
| Complete-case AQI(t), AQI(t+1) | ⚠️ Đạt một phần | model_utils.build_dataset; NB06 hạn chế | Loại ngày thiếu có thể làm sai số đẹp hơn. DA báo retention theo TP/mùa và kiểm ảnh hưởng chọn mẫu; không nội suy nhãn để “sửa”. |

## 6. Quyết định bàn giao

**Chuyển Bước 3 cho DA**, ưu tiên Q01 → Q02 → Q03/Q05 → Q04/Q06/Q07; Q08/Q09 cần chủ tài liệu/BA. Chưa đủ cơ sở khẳng định các số 51%, 2,8× hay MAE 19,5 là kết quả kiểm chứng độc lập; chúng hiện là kết quả lưu của tác giả.

Chưa phát hành `final_review_report.md`. Khi DA trả kết quả, RA đối chiếu từng Q/CK, xét vấn đề mới, và mọi kết luận cuối phải dẫn `verification_results.md#V…` hoặc `supplementary_analysis.md#S…`; không chỉ dẫn notebook hoặc báo cáo sơ bộ này. Không lấy nghiên cứu ngoài chưa kiểm tra làm bằng chứng thay DA.
