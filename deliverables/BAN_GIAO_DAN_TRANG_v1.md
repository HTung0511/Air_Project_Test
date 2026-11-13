# BÀN GIAO DÀN TRANG — Báo cáo phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ (Nhóm 25IT)

Vai trò thực hiện: Data Visualization Specialist + Information Designer.
Phạm vi: thiết kế, dàn trang, chèn hình, dựng bảng, đánh số hình/bảng, heading. **Không thay đổi kết quả nghiên cứu, không chạy lại notebook, không dùng ảnh tạo bằng AI.**

| Vòng | Ngày | Nội dung |
|---|---|---|
| v1 | 13/11/2026 | Dàn trang lần đầu: 20 hình, 3 bảng native, đánh số lại Bảng 1–10, gắn heading, gỡ chỉ dẫn biên tập |
| **v2** | 13/11/2026 | Theo phản hồi RA: sửa số baseline test, chuyển 5 hình mô hình về đúng tiểu mục và bỏ §3.3.7, chuyển **7 bảng dạng danh sách thành bảng native**, phân loại lại 4 khác biệt hình–văn bản, **sửa lỗi chú thích Hình 2–5 bị ảnh chèn xen** |

---

## 1. Sản phẩm bàn giao

| Hạng mục | Nội dung |
|---|---|
| Bản dàn trang (Google Docs) | https://docs.google.com/document/d/1vxuomPCYI7acP9ZBFy7miLHwqLAK652Oc4lDjUliBIA/edit — “Báo cáo — Phân tích ô nhiễm không khí 8 TP Ấn Độ — Nhóm 25IT — BẢN DÀN TRANG v1” (nội dung đã ở vòng v2; tên tệp giữ nguyên để không vỡ liên kết) |
| Bản gốc đối chiếu | https://docs.google.com/document/d/1wAbxQIyuAgvuOMF_tc4D4TDIjEG6Hsomi5yVfylp11o/edit (không chỉnh sửa) |
| PDF | Không xuất (yêu cầu đã bãi bỏ) |
| .docx | Chỉ xuất để **kiểm tra bố cục nội bộ** bằng script (đếm ảnh/bảng/đoạn, phát hiện ảnh chèn xen). Giao file nếu nhóm cần |
| Payload tái lập | `deliverables/layout_assets/`: `gen_batches.py` + `batches.txt` (20 hình vòng v1), `gen_tables.py` + `tables_payload.json` (Bảng 2/5/7), **`tables_native_v2.json` (7 bảng chuyển từ danh sách, kèm vị trí và khổ cột cuối cùng)**, **`fix_figures_2_3_4_5.json` (payload dựng lại khối Hình 2–5)**, `make_flow_diagram.py` (Hình 1) |

## 2. Nguồn hình — một nguồn duy nhất, dùng nhất quán

- Kho **`HTung0511/Air_Project_Test`**, nhánh **`main`**, commit **`c4c75f65c7fb39f843d397bec0ef6c54fd15c29e`**, thư mục `Air-Project-main/reports/figures/` (21 PNG; đã dùng 19). SHA-256 từng tệp đã đối chiếu khớp blob của commit.
- Ảnh nhúng bằng URL công khai ghim theo commit: `https://raw.githubusercontent.com/HTung0511/Air_Project_Test/c4c75f65.../Air-Project-main/reports/figures/<tên>.png`; mỗi chú thích ghi tên tệp + kho + nhánh + commit.
- **Hình 1** là sơ đồ vẽ lại từ nội dung §1.5 (không có số liệu mới): `deliverables/layout_assets/so_do_quy_trinh.png` (5331×765 px), tải lên Drive id `1H4MHzXLcSVLr9DURzsAfeqL9bHWLLUr8` (chia sẻ “bất kỳ ai có liên kết – người đọc”) vì API Docs chỉ nhận URL công khai.
- **Không dùng**: hình/kết quả của PR #3 (`arena/b5aacef3`) và PR #4 – vòng Dev (`arena/5cb21c04`); không gom hình từ nhiều nhánh; không ảnh AI; không thay hình bản Dev/Test.
- Kích thước: mọi ảnh **rộng 450 pt** (khổ A4 trừ lề ≈451 pt), chiều cao suy từ **aspect ratio gốc của từng tệp** → không kéo méo, không cắt mất trục/đơn vị/khoảng bất định/đường ngưỡng/cỡ mẫu. Đã kiểm lại bằng bản xuất: 20/20 ảnh đúng 450 pt và đúng tỷ lệ gốc (6,9565 · 2,2 · 1,5 · 3,25 · 1,8571 · 1,7778 · 1,7778 · 1,6667 · 2,0833 · 1,875 · 2,1739 · 2,5 · 1,6129 · 2,6136 · 1,9792 · 2,0408 · 1,4375 · 1,9 · 1,7857 · 2,3958).

## 3. Bảng bàn giao hình (Số hình | Tệp nguồn | Vị trí | Vấn đề còn thiếu)

| Số hình | Tệp nguồn | Vị trí trong báo cáo | Vấn đề còn thiếu / ghi chú |
|---|---|---|---|
| Hình 1 | `so_do_quy_trinh.png` (vẽ lại từ §1.5) | §1.5 Quy trình thực hiện và phân công | Không phải kết quả phân tích; giữ ghi chú phân biệt xử lý hồi cứu với yêu cầu kiểm soát thông tin theo thời điểm của nhánh dự báo |
| Hình 2 | `missing_after_cleaning_8cities.png` | §2.2.8 Các kiểm tra sau xử lý | Đã dựng lại ở vòng v2 (xem mục 10) |
| Hình 3 | `missing_pattern_lucknow_jaipur.png` | §2.2.8 | Chỉ dẫn gốc muốn “hình minh họa nội suy/ngoại lai có đoạn thời gian, đường quan sát và đường ước lượng”; **không tệp nào trong `reports/figures/` đúng dạng đó** → dùng hai hình gần nhất (Hình 4, 5) và nói rõ trong chú thích. Muốn đúng yêu cầu phải sinh hình mới từ notebook (ngoài phạm vi) |
| Hình 4 | `fill_strategies_lucknow_jaipur.png` | §2.2.8 | Nhãn (D) trong hình là nội suy **≤1 ngày**. Theo RA: **không dùng hình làm bằng chứng trực tiếp cho quy tắc 14 ngày** → chú thích đã viết lại: bốn cấu hình là minh họa so sánh chiến lược điền của Notebook 02 trên hai thành phố ví dụ, quy tắc pipeline (≤14 ngày, `Data_dictionary.md`) nêu riêng. Giữ hình vì vẫn giúp giải thích mục “xử lý thiếu” |
| Hình 5 | `outliers_pm25_lucknow_jaipur.png` | §2.2.8 | Đã dựng lại ở vòng v2 |
| Hình 6 | `eda_00_sample_size.png` | §3.2.1 Khác biệt giữa các thành phố | — |
| Hình 7 | `eda_01_poor_share_city.png` | §3.2.1 | — |
| Hình 8 | `eda_05_aqi_distribution.png` | §3.2.1 | — |
| Hình 9 | `eda_02_heatmap_city_month.png` | §3.2.2 Biến động theo thời gian | — |
| Hình 10 | `eda_03_trend_city_year.png` | §3.2.2 | — |
| Hình 11 | `eda_04_pm25_aqi.png` | §3.2.3 Các chất nổi bật trong ngày AQI cao | Khoảng **[2,42; 3,17]** cạnh 2,82: **giữ nguyên hình gốc**, chú thích đã ghi “loại khoảng chưa được xác nhận trong hồ sơ phân tích nên không đọc là khoảng tin cậy 95%”; Bảng 7 chưa đưa khoảng này vào, cần nhóm xác nhận (tin cậy hay phân vị) |
| Hình 12 | `corr_01_raw_vs_adjusted.png` | §3.2.4 Thời tiết–AQI trước và sau điều chỉnh mùa vụ | — |
| Hình 13 | `corr_02_hypothesis_tests.png` | §3.2.4 | — |
| Hình 14 | `corr_03_humidity_deciles.png` | §3.2.4 | — |
| Hình 15 | `corr_04_poor_share_by_humidity.png` | §3.2.4 | — |
| **Hình 16** | `model_02_mae_by_model.png` | **§3.3.1 Hiệu năng hồi quy** (ngay sau Bảng 9) | **Đã chuyển về cạnh đoạn phân tích theo RA.** Hai cột đối chứng 64,5 và 43,4 **không còn bị coi là xung đột**: đó là MAE **test** làm tròn của 64,47 và 43,41; chú thích đã ghi rõ và tách khỏi 60,49/55,82 (validation) |
| **Hình 17** | `model_01_residual_diagnostics.png` | **§3.3.2 Chẩn đoán và độ ổn định** | Đã chuyển về phần chẩn đoán; **đổi số từ Hình 16 → Hình 17** |
| **Hình 18** | `model_03_mae_by_city.png` | **§3.3.2** (cạnh câu “MAE của L3 giảm cùng chiều ở tám thành phố”) | Thứ tự thành phố xếp theo **số ngày AQI ≥201 trong tập test** — theo RA **không phải lỗi**; tiêu chí đã ghi trong chú thích và bổ sung một câu “khác thứ tự xếp theo trung vị AQI ở Hình 6–Hình 8 vì tiêu chí sắp xếp khác nhau” |
| **Hình 19** | `model_04_precision_recall.png` | **§3.3.3 Kết quả cảnh báo** | Hai cặp số là **hai điểm vận hành khác ngưỡng**, không mâu thuẫn: chú thích ghi rõ điểm mở = ngưỡng 201 (precision ≈0,90 L3 / ≈0,85 persistence) và điểm đặc = ngưỡng chọn theo quy tắc F2 trên validation của train (166 cho L3, 160 cho persistence; hình hiển thị ≈77% và 72%) |
| **Hình 20** | `model_05_humidity_recheck.png` | **§3.3.4 Diễn giải liên hệ có điều kiện** (cạnh hệ số độ ẩm của OLS) | Đã chuyển về đúng đoạn; số không đổi |
| *(chưa có số)* | **Chờ ảnh chụp thật** từ `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` — ảnh tổng quan sản phẩm | §1.4, giữ ghi chú “[CHỜ NGUỒN ẢNH ỨNG DỤNG — ẢNH TỔNG QUAN SẢN PHẨM]” | RA sẽ đính kèm HTML ở phiên thiết kế để chụp thật; không thay bằng ảnh mô phỏng/AI. Khi chụp: thấy rõ vùng chọn thành phố, ngày, kết quả; mô tả là **phát lại lịch sử** |
| *(chưa có số)* | **Chờ ảnh chụp thật** — 4 khung (a) tổng quan, (b) Delhi 24/01/2020, (c) đồ thị toàn kỳ + thanh kéo ngưỡng, (d) màn hình mẫu ít/giới hạn | §3.4.4 (4 chỉ dẫn đã hợp nhất thành 1 ghi chú) | Như trên; ghi chú giữ hai ràng buộc: không so hai ngưỡng như hai mô hình độc lập; 1.947 là tổng số cặp toàn test, không phải chiều dài ngày lịch của mỗi đường |

**Hai tệp hình chưa dùng** (bản thảo không có chỉ dẫn chèn): `aqi_monthly_lucknow_jaipur.png`, `aqi_season_lucknow_jaipur.png`. Nếu muốn dùng cần chỉ định vị trí, khi đó phải đánh số lại dãy hình.

## 4. Bảng — nay **10/10 bảng đánh số đều là bảng native chỉnh sửa được**

| Số bảng | Tên | Vị trí | Kích thước | Nguồn số liệu |
|---|---|---|---|---|
| Bảng 1 | Vai trò các nhóm biến trong nghiên cứu | §2.1.3 | 6×2 | **Mới chuyển từ danh sách** (5 gạch đầu dòng) |
| Bảng 2 | Từ điển biến thiết yếu của bảng phân tích | §2.1.4 | 15×5 | `Data_dictionary.md` mục 1 và 3; ghi chú chất lượng từ §2; ghim hàng tiêu đề |
| Bảng 3 | Tổng hợp kết quả xử lý dữ liệu chất lượng không khí | §3.1 | 7×2 | **Mới chuyển từ danh sách** (6 gạch đầu dòng có dấu •); ghim hàng tiêu đề |
| Bảng 4 | Đơn vị cần phân biệt khi báo kết quả làm sạch | §3.1 | 5×2 | **Mới chuyển từ danh sách** (4 mục thuật ngữ) |
| Bảng 5 | Số dòng và số cột của hai nguồn dữ liệu và của bảng ghép | §3.1.3 | 4×4 | Đối chiếu trực tiếp 3 tệp CSV: `air_quality_8cities.csv` 14.056×40; `weather_daily_8cities.csv` 16.128×16; `air_quality_8cities_weather.csv` 14.056×54 |
| Bảng 6 | Trung vị AQI và tỷ lệ ngày có AQI ≥201 trong khoảng chung | §3.2.1 | 9×3 | **Mới chuyển từ danh sách** (8 thành phố × 2 số); ghim hàng tiêu đề |
| Bảng 7 | Hai cách tổng hợp tỷ số PM2.5 | §3.2.3 | 3×5 | §3.2.3: 2,82 (trung vị tỷ số của 5 thành phố đủ điều kiện) và ≈3,26 = 137,1/42,0 (gộp 8 thành phố); không thêm khoảng tin cậy chưa rõ loại |
| Bảng 8 | Tóm tắt family 15 giả thuyết trong phân tích thời tiết | §3.2.4 | 4×3 | **Mới chuyển từ danh sách** (3 nhóm kết quả: 3 / 1 / 11) |
| Bảng 9 | MAE kiểm thử theo mức đặc trưng, thang điểm AQI | §3.3.1 | 8×2 | **Mới chuyển từ danh sách và bổ sung 2 dòng đối chứng** theo số RA xác nhận: baseline trung bình theo thành phố **64,47**, baseline trung vị cùng tháng **43,41**, persistence 23,47, Ridge L1 ≈22,94, L2 ≈20,92, L3 19,52, L4 ≈19,08 → khớp 7 cột của Hình 16; ghim hàng tiêu đề |
| Bảng 10 | Các kịch bản minh họa | §3.4 | 5×3 | **Mới chuyển từ danh sách** (4 kịch bản, tách cột STT / thành phố–ngày / tình huống) |
| *(không đánh số)* | Bảng phân công thành viên ở trang bìa | Trang bìa | 5×4 | Có sẵn trong bản thảo, giữ nguyên |

Định dạng thống nhất: tên bảng **in đậm 10 pt ở trên** bảng; chữ trong bảng 8,5–9 pt; khổ cột cố định **tổng 450 pt**; hàng tiêu đề tô nền `rgb(0.93,0.94,0.96)` + căn giữa dọc; **ghim hàng tiêu đề** lặp lại khi sang trang cho các bảng ≥7 dòng (Bảng 2, 3, 6, 9); ghi chú “Nguồn …” **nghiêng 8,5–9 pt ở dưới** bảng, giữ nguyên văn bản thảo; đoạn đệm kỹ thuật trước mỗi bảng thu về 1 pt để không tạo khoảng trắng thừa.

Nội dung ô chép **nguyên văn** bản thảo, chỉ tách theo cột (không viết lại, không đổi chữ số). Hai ngoại lệ có chủ đích, đều ghi trong mục 9: (i) Bảng 9 thêm 2 dòng đối chứng theo số RA xác nhận; (ii) ghi chú Bảng 6 chuyển câu chỉ dẫn “Khi dàn bảng, sắp các thành phố cùng một thứ tự trên hình và bảng” thành mô tả thực tế về tiêu chí sắp xếp.

## 5. Đánh số bảng theo thứ tự xuất hiện (đã áp dụng từ v1, giữ nguyên)

Bản thảo đánh số không theo thứ tự xuất hiện (4 → 1 → 5 → 6 → 7 → 2 → 3). Đã đánh số lại thành **Bảng 1 → Bảng 10**: Bảng 4→1; *(mới)*→2; Bảng 1→3; Bảng 5→4; *(mới)*→5; Bảng 6→6; *(mới)*→7; Bảng 7→8; Bảng 2→9; Bảng 3→10. Các chỗ dẫn chiếu đã sửa theo: “Nguồn Bảng 3:”, “Nguồn Bảng 9:”, “Nguồn Bảng 10:”, ghi chú §3.1.3 trỏ về Bảng 3, câu “Cần đọc Bảng 6 theo hai chiều” giữ nguyên vì số không đổi. Kiểm tra lại ở vòng v2: thứ tự xuất hiện trong thân bài là 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 — không có số nào nhảy cóc hay xuất hiện trước lần đầu định nghĩa.

## 6. Hình mô hình đã về cạnh đoạn phân tích; §3.3.7 đã gỡ

Theo RA, §3.3.7 “Các hình cần đặt cạnh kết quả mô hình” là chỉ dẫn biên tập, không phải mục nghiên cứu → **đã xoá tiêu đề và toàn bộ khối hình ở đó**, chuyển 5 hình về đúng tiểu mục và **đánh lại số đồng bộ**:

| Tiểu mục | Hình sau khi chuyển | Số cũ → số mới |
|---|---|---|
| §3.3.1 Hiệu năng hồi quy | `model_02_mae_by_model.png` — ngay sau Bảng 9 | Hình 17 → **Hình 16** |
| §3.3.2 Chẩn đoán và độ ổn định | `model_01_residual_diagnostics.png` (cạnh đoạn phần dư/Breusch–Pagan) | Hình 16 → **Hình 17** |
| §3.3.2 Chẩn đoán và độ ổn định | `model_03_mae_by_city.png` (cạnh câu MAE giảm ở tám thành phố) | Hình 18 → **Hình 18** |
| §3.3.3 Kết quả cảnh báo | `model_04_precision_recall.png` (cạnh đoạn recall/precision hai ngưỡng) | Hình 19 → **Hình 19** |
| §3.3.4 Diễn giải liên hệ có điều kiện | `model_05_humidity_recheck.png` (cạnh hệ số độ ẩm OLS) | Hình 20 → **Hình 20** |

Dãy Hình 1–15 không đổi. Không có chỗ nào trong thân bài dẫn chiếu “Hình 16–20” nên việc đổi số không phải sửa câu nào khác; các dòng “Nguồn minh họa: …” của §3.3.2/§3.3.3/§3.3.4 vẫn đứng **sau** hình tương ứng. §3.3 nay chạy 3.3.1 → 3.3.6 rồi sang §3.4.

## 7. Heading và mục lục tự động

- Bản thảo gốc **không có heading style nào** → không thể sinh mục lục. Đã gắn **72 tiêu đề** (vòng v2 còn 72 vì bỏ §3.3.7): **7 Heading 1** (MỞ ĐẦU, PHẦN I–III, KẾT LUẬN, TÀI LIỆU THAM KHẢO, PHỤ LỤC), **17 Heading 2**, **48 Heading 3**; không có chỗ nào nhảy cấp.
- Ba style đã định nghĩa lại khớp typography báo cáo: **Times New Roman, in đậm, màu đen**, 15/14/13 pt, `keepWithNext`, giãn dòng 115%, khoảng cách trên/dưới 18-8 / 15-6 / 11-4 pt.
- **MỤC LỤC — còn 1 thao tác tay, không thể làm qua API**: bộ API Google Docs mà phiên này dùng **không có request chèn mục lục** (đã kiểm tra toàn bộ danh sách công cụ: chỉ có heading/named style/bảng/hình/section break, không có `insertTableOfContents`). Mục lục phải sinh trong giao diện để **số trang tự cập nhật**: mở bản dàn trang → đặt con trỏ ở trang sau bìa → `Insert → Table of contents` (chọn dạng có số trang). Danh sách 72 heading đã sẵn nên mục lục sẽ hiện đủ 3 cấp. Nếu nhóm muốn, tôi có thể dựng một **mục lục tĩnh** (liệt kê 72 mục, không có số trang) làm phương án in tạm — nhưng nó sẽ lệch ngay khi nội dung dịch chuyển, nên không khuyến nghị.

## 8. Chỉ dẫn biên tập đã gỡ khỏi bản nộp

- **26 chỉ dẫn `[CHÈN …]`**: xử lý hết, kiểm lại bằng tìm kiếm → **0 chỉ dẫn còn lại**.
- **Phụ lục B “DANH MỤC HÌNH NGUỒN CHO DÀN TRANG”**: đã xoá (tự ghi “phục vụ AI dàn trang”; dãy “Hình 1–15” cũ mâu thuẫn dãy Hình 1–20; thông tin nguồn tệp nay nằm trong từng chú thích).
- **Phụ lục C “NGUYÊN TẮC BÀN GIAO THIẾT KẾ”**: đã xoá (chính phụ lục ghi “cần bỏ khỏi bản nộp cuối”).
- **Tiêu đề §3.3.7**: đã xoá (mục 6).
- **Câu chỉ dẫn “Khi dàn bảng, sắp các thành phố cùng một thứ tự trên hình và bảng”** trong ghi chú Bảng 6: thay bằng mô tả thực tế (bảng giảm dần theo trung vị AQI; Hình 18 xếp theo số ngày AQI ≥201 trong test; mỗi nơi ghi tiêu chí của mình).
- **4 chỉ dẫn ảnh ứng dụng ở §3.4.4**: hợp nhất thành **1 ghi chú** (a)–(d) để không lặp và không tăng trang.
- **Chỉ dẫn hình trùng ở §3.1.3** (chèn lại `missing_after_cleaning_8cities.png`): thay bằng **dẫn chiếu** về Hình 2/Hình 3 ở §2.2.8 và Bảng 3.
- **Phụ lục A** giữ nguyên, nay là danh sách dài mà Bảng 2 dẫn chiếu tới.
- Dọn các đoạn trống thừa sau khi xoá chỉ dẫn; đoạn đệm trước mỗi bảng thu về 1 pt.

## 9. Số liệu và khác biệt hình–văn bản: xử lý theo đối chiếu RA với Notebook 06

**(a) Đã sửa — lỗi biên soạn trong lời văn (không phải lỗi hình).** Đoạn §3.3.1 trước đây viết hai baseline test “khoảng 60,5 và 55,8” là **nhầm tập đánh giá**. Đã thay đúng câu RA yêu cầu:

> “Trên tập kiểm thử, baseline trung bình theo thành phố có MAE 64,47; baseline trung vị cùng tháng có MAE 43,41; persistence đạt 23,47.”

| Phương pháp | MAE validation | MAE test |
|---|---|---|
| Trung bình theo thành phố | 60,49 | **64,47** |
| Trung vị cùng tháng | 55,82 | **43,41** |
| Persistence | 25,93 | **23,47** |
| Ridge L3 | 22,33 | **19,52** |

Hình 16 (`model_02_mae_by_model.png`) hiển thị 64,5 và 43,4 → **đúng**, chỉ là làm tròn của 64,47 và 43,41. Ghi chú dưới hình và ghi chú Bảng 9 đều đã tách rõ test với validation để người đọc sau không lặp lại nhầm lẫn. Không chạy lại notebook.

**(b) Bốn khác biệt đã báo ở v1 — phân loại lại, không còn gọi là “xung đột”:**

| Hạng mục | Kết luận sau rà soát | Việc đã làm |
|---|---|---|
| Hình 4: nhãn nội suy ≤1 ngày vs quy tắc pipeline ≤14 ngày | Không dùng hình làm bằng chứng trực tiếp cho quy tắc 14 ngày | Viết lại chú thích: bốn cấu hình là minh họa so sánh chiến lược điền của Notebook 02 trên hai thành phố ví dụ; quy tắc ≤14 ngày nêu riêng theo `Data_dictionary.md`. Giữ hình vì vẫn phục vụ mục “xử lý thiếu” |
| Hình 18: thứ tự thành phố khác nhóm hình EDA | **Không phải lỗi** — tiêu chí sắp xếp khác nhau | Ghi tiêu chí trong chú thích (số ngày AQI ≥201 trong tập test) và nói rõ khác Hình 6–8 vì tiêu chí khác nhau; không ép mọi biểu đồ cùng thứ tự |
| Hình 19: precision 77%/72% so với 0,90/0,85 | **Hai điểm vận hành khác ngưỡng**, không phải số mâu thuẫn | Chú thích ghi ngưỡng cạnh từng kết quả: 201 → ≈0,90 (L3) và ≈0,85 (persistence); F2 (166/160) → ≈77% và 72%. §3.3.3 vốn đã gắn nhãn ngưỡng cho từng cặp số nên không sửa lời văn |
| Hình 11: khoảng [2,42; 3,17] | Loại khoảng chưa xác nhận | **Giữ nguyên hình gốc**; chú thích ghi rõ loại khoảng chưa được xác nhận, **không gọi là khoảng tin cậy 95%**; Bảng 7 không đưa khoảng này vào |

**(c) Không tự sửa bất kỳ số liệu/kết quả nào khác.** Các số trong lời văn, bảng và chú thích đều lấy từ bản thảo, `Data_dictionary.md`, 3 tệp CSV trong `data/processed/` hoặc từ đối chiếu RA ở trên.

## 10. Lỗi bố cục phát hiện và sửa ở vòng v2 (ảnh chèn xen vào chú thích)

Khi kiểm tra cấu trúc bằng bản xuất .docx, phát hiện **hai khối hình bị hỏng từ đợt chèn v1**: ảnh của Hình 3 nằm **giữa** chú thích Hình 2, và ảnh của Hình 5 nằm **giữa** chú thích Hình 4, khiến mỗi chú thích bị cắt đôi và phần đuôi bị dồn vào đoạn chứa chú thích hình kế tiếp (ví dụ đoạn sau Hình 3 chứa cả phần còn lại của chú thích Hình 2). Nguyên nhân: chỉ số chèn cho “hình thứ hai của cùng một chỉ dẫn” trong `gen_batches.py` lệch, cùng loại lỗi từng làm Hình 15 rơi vào giữa chú thích Hình 14 (đã sửa ở v1).

Cách sửa: xoá cả hai khối `[ảnh Hình 2 + chú thích vỡ + đoạn dồn]` và dựng lại **toàn bộ 4 hình** theo đúng mẫu đã kiểm chứng (mỗi ảnh một đoạn riêng canh giữa, chú thích ngay dưới, nghiêng 9 pt, trên 4 pt / dưới 10 pt), đồng thời cập nhật chú thích Hình 4 theo mục 9(b). Payload lưu tại `deliverables/layout_assets/fix_figures_2_3_4_5.json`.

Kiểm lại sau sửa: **0 đoạn văn nào vừa chứa chữ vừa chứa ảnh**; 20/20 ảnh mỗi ảnh một đoạn; chú thích Hình 1→20 xuất hiện đúng thứ tự tăng dần, mỗi số một lần, đoạn nào cũng kết thúc bằng “…nhánh main, commit c4c75f6.”

## 11. Sự cố công cụ trong lúc làm và cách khắc phục (ghi lại để lần sau không lặp)

Lần đầu chuyển 7 bảng danh sách sang bảng native, tôi gửi **7 lệnh tạo bảng liên tiếp** trong cùng một lượt. Lệnh tạo bảng của connector dùng **ảnh chụp tài liệu cũ** (thiếu đúng phép xoá cuối cùng của lô xoá trước đó, lệch +451 chỉ số), nên **6/7 bảng rơi vào giữa đoạn văn** (cắt đôi chữ, ví dụ “…tám thành phố đ” | “ược tổng hợp…”). Chỉ Bảng 1 — lệnh cuối cùng — đúng chỗ.

Phát hiện nhờ kiểm tra cấu trúc bằng bản xuất .docx (không phải nhìn bằng mắt trên Docs). Xử lý: (1) xoá 6 bảng lệch **kèm ký tự xuống dòng** để nối liền lại các đoạn văn bị cắt; (2) xuất bản, dựng lại mô hình chỉ số, kiểm chứng bằng `find_text`; (3) chèn lại **từng bảng một**, mỗi lần `find_text` lại tiêu đề bảng để lấy mốc tươi (bảng đặt tại `chỉ_số_cuối_tiêu_đề + 1`), và xác nhận bảng đầu tiên rơi đúng ô dự đoán trước khi làm tiếp; (4) định dạng cả 6 bảng và thu nhỏ đoạn đệm. Kết quả kiểm tra cuối: 11/11 bảng đúng vị trí, tiêu đề ở trên, ghi chú ở dưới, không đoạn văn nào bị cắt.

## 12. Phần còn thiếu / cần nhóm bổ sung

1. **5 ảnh ứng dụng**: cần tệp HTML `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html`. RA sẽ đính kèm ở phiên thiết kế để chụp ảnh thật (việc không tìm thấy trên Git/Drive không có nghĩa tệp không tồn tại). Hai ghi chú giữ chỗ đang nằm ở §1.4 và §3.4.4.
2. **Thời gian trên bìa**: vẫn là “Hà Nội, tháng [Cần bổ sung] năm [Cần bổ sung]”. Tôi **không tự điền** vì không biết tháng/năm nộp thực tế — cho tôi tháng/năm, tôi điền bằng một lệnh thay chữ (2 chỗ).
3. **Mục lục tự động**: cần 1 thao tác tay trong giao diện Docs (mục 7) — API không có lệnh chèn mục lục.
4. **Tài liệu tham khảo**: bản thảo tự ghi “chưa ghi ngày truy cập vì chưa xác nhận lượt truy cập thực tế” → **chưa thể gọi là hoàn tất**; cần nhóm kiểm tra từng đường dẫn (Kaggle, CPCB, Open-Meteo, GitHub dự án, tài liệu scikit-learn) và điền ngày truy cập.
5. **Dấu `*` sau đơn vị nồng độ** trong `Data_dictionary.md` mục 1 (µg/m³ \*, ppb \*, mg/m³ \*) không có chú giải → Bảng 2 chép nguyên dấu `*` kèm ghi chú “cần nhóm xác nhận”, không tự quy đổi đơn vị.
6. **Loại khoảng [2,42; 3,17]** ở Hình 11 (tin cậy hay phân vị) — cần xác nhận để bổ sung vào Bảng 7.
7. **Hình minh họa nội suy/ngoại lai** đúng dạng “đoạn thời gian + đường quan sát + đường ước lượng” không có trong `reports/figures/` → nếu cần đúng chỉ dẫn gốc thì phải sinh hình mới từ notebook (ngoài phạm vi dàn trang).
8. **Hai tệp hình chưa dùng**: `aqi_monthly_lucknow_jaipur.png`, `aqi_season_lucknow_jaipur.png`.

## 13. Kiểm chứng bố cục vòng v2 (đo bằng script trên bản xuất .docx, không đếm bằng mắt)

- **416 khối nội dung**, chỉ số cuối 90.714 (khớp `get_document_end_index`).
- **20 ảnh**, mỗi ảnh một đoạn riêng, rộng 450 pt, đúng aspect ratio gốc; **0 đoạn vừa chữ vừa ảnh**.
- **11 bảng native** (10 bảng đánh số + bảng thành viên); phần còn lại là chữ chỉnh sửa được — không trang nào bị biến thành ảnh.
- Chú thích **Hình 1 → Hình 20** đúng thứ tự, mỗi số một lần, luôn nằm **dưới** hình, canh giữa, nghiêng 9 pt, kèm nguồn tệp + kho + nhánh + commit.
- **Bảng 1 → Bảng 10** đúng thứ tự xuất hiện; tên bảng **trên** bảng; mỗi bảng có dòng “Nguồn …” giữ từ bản thảo.
- **72 heading** (7/17/48), không nhảy cấp; §3.3 chạy 3.3.1–3.3.6; Hình 16–20 nằm trong §3.3.1, §3.3.2 (2 hình), §3.3.3, §3.3.4.
- **0** chỉ dẫn `[CHÈN …]`, **0** lần còn “3.3.7”, **0** lần còn “Khi dàn bảng”, **0** lần còn cặp số cũ “60,5 và 55,8”; đúng **2** ghi chú “[CHỜ NGUỒN ẢNH ỨNG DỤNG]”; còn **2** chỗ “[Cần bổ sung]” ở bìa (chờ nhóm).
- Chỉ số dùng cho mọi thao tác sửa đều lấy từ `find_text` ngay trước khi sửa; các phép xoá/chèn trong một lô luôn theo thứ tự chỉ số giảm dần; mô hình chỉ số nội bộ được kiểm bằng 6 mốc neo khớp tuyệt đối.
