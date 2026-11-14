# BÀN GIAO DÀN TRANG — Báo cáo phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ (Nhóm 25IT)

Vai trò thực hiện: Data Visualization Specialist + Information Designer.
Phạm vi: thiết kế, dàn trang, chèn hình, dựng bảng, đánh số hình/bảng, heading. **Không thay đổi kết quả nghiên cứu, không chạy lại notebook, không dùng ảnh tạo bằng AI.**

| Vòng | Ngày | Nội dung |
|---|---|---|
| v1 | 13/11/2026 | Dàn trang lần đầu: 20 hình, 3 bảng native, đánh số lại Bảng 1–10, gắn heading, gỡ chỉ dẫn biên tập |
| **v2** | 13/11/2026 | Theo phản hồi RA: sửa số baseline test, chuyển 5 hình mô hình về đúng tiểu mục và bỏ §3.3.7, chuyển **7 bảng dạng danh sách thành bảng native**, phân loại lại 4 khác biệt hình–văn bản, **sửa lỗi chú thích Hình 2–5 bị ảnh chèn xen** |
| **v4** | 14/11/2026 | **Rút gọn chú thích theo chuẩn học thuật cho bản nộp**: bỏ tên tệp PNG, đường dẫn kho, commit, lịch sử dàn trang và câu “cần nhóm xác nhận” khỏi mọi chú thích/ghi chú; thêm **ghi chú chung** xác nhận bảng và biểu đồ do nhóm thực hiện; nguồn ngoài dẫn bằng số tham khảo; toàn bộ truy vết chi tiết chỉ còn trong hồ sơ này |
| **v3** | 13–14/11/2026 | Chốt bảng & biểu đồ (không thêm hình); **kiểm tra khả năng đọc thực tế** của ảnh và chú thích bằng đo đạc + xem ảnh; vẽ lại **Hình 1 khổ hẹp** vì bản v1 chữ chỉ ~3 pt khi in ở 450 pt; thêm **keepWithNext** giữ ảnh liền chú thích và tên bảng liền bảng; **giải quyết khoảng [2,42; 3,17]** bằng đối chiếu Notebook 03; đối chiếu dấu `*` đơn vị; kiểm tra nguồn tham khảo trong phạm vi mạng của phiên; bàn giao thêm **bản Word** trên Drive |

---

## 1. Sản phẩm bàn giao

| Hạng mục | Nội dung |
|---|---|
| Bản dàn trang (Google Docs) | https://docs.google.com/document/d/1vxuomPCYI7acP9ZBFy7miLHwqLAK652Oc4lDjUliBIA/edit — “Báo cáo — Phân tích ô nhiễm không khí 8 TP Ấn Độ — Nhóm 25IT — BẢN DÀN TRANG v1” (nội dung đã ở vòng v2; tên tệp giữ nguyên để không vỡ liên kết) |
| Bản gốc đối chiếu | https://docs.google.com/document/d/1wAbxQIyuAgvuOMF_tc4D4TDIjEG6Hsomi5yVfylp11o/edit (không chỉnh sửa) |
| PDF | Không xuất (nhóm xác nhận không cần) |
| Bản Word (.docx) | Tệp “Báo cáo … BẢN DÀN TRANG (bản Word).docx” trên Drive, id `1ccLSOBhK1phBKmo4sHRVDejHTHRoIDQR` — xuất từ bản Docs sau vòng v4, để nộp/đọc offline; bản vòng v3 đổi tên thành “…(bản Word, vòng v3).docx” (id `1BoNSJmOanFmnAE8gQ22OpsLNK9jLoF5H`); bản chính vẫn là Google Docs |
| .docx | Chỉ xuất để **kiểm tra bố cục nội bộ** bằng script (đếm ảnh/bảng/đoạn, phát hiện ảnh chèn xen). Giao file nếu nhóm cần |
| Payload tái lập | `deliverables/layout_assets/`: `gen_batches.py` + `batches.txt` (20 hình vòng v1), `gen_tables.py` + `tables_payload.json` (Bảng 2/5/7), **`tables_native_v2.json` (7 bảng chuyển từ danh sách, kèm vị trí và khổ cột cuối cùng)**, **`fix_figures_2_3_4_5.json` (payload dựng lại khối Hình 2–5)**, `make_flow_diagram.py` (Hình 1) |

## 2. Nguồn hình — một nguồn duy nhất, dùng nhất quán

- Kho **`HTung0511/Air_Project_Test`**, nhánh **`main`**, commit **`c4c75f65c7fb39f843d397bec0ef6c54fd15c29e`**, thư mục `Air-Project-main/reports/figures/` (21 PNG; đã dùng 19). SHA-256 từng tệp đã đối chiếu khớp blob của commit.
- Ảnh nhúng bằng URL công khai ghim theo commit: `https://raw.githubusercontent.com/HTung0511/Air_Project_Test/c4c75f65.../Air-Project-main/reports/figures/<tên>.png`. **Từ vòng v4, chuỗi tên tệp + kho + nhánh + commit chỉ ghi trong hồ sơ này (bảng mục 3); chú thích trong bản nộp rút gọn theo mục 17.**
- **Hình 1** là sơ đồ vẽ lại từ nội dung §1.5 (không có số liệu mới). Vòng v3 vẽ lại **bản v2 khổ hẹp**: `deliverables/layout_assets/so_do_quy_trinh.png` (3200×616 px, dpi 400), Drive id `1iju2jG7Cb82wf-2vixwT0RaABNjyqI3W` (công khai “bất kỳ ai có liên kết – người đọc”); bản v1 (5331×765 px, Drive id `1H4MHzXLcSVLr9DURzsAfeqL9bHWLLUr8`) giữ trong repo (`so_do_quy_trinh_v1.png`) và trên Drive làm đối chiếu. Lý do vẽ lại ở mục 14.
- **Không dùng**: hình/kết quả của PR #3 (`arena/b5aacef3`) và PR #4 – vòng Dev (`arena/5cb21c04`); không gom hình từ nhiều nhánh; không ảnh AI; không thay hình bản Dev/Test.
- Kích thước: mọi ảnh **rộng 450 pt** (khổ A4 trừ lề ≈451 pt), chiều cao suy từ **aspect ratio gốc của từng tệp** → không kéo méo, không cắt mất trục/đơn vị/khoảng bất định/đường ngưỡng/cỡ mẫu. Đã kiểm lại bằng bản xuất: 20/20 ảnh đúng 450 pt và đúng tỷ lệ gốc (6,9565 · 2,2 · 1,5 · 3,25 · 1,8571 · 1,7778 · 1,7778 · 1,6667 · 2,0833 · 1,875 · 2,1739 · 2,5 · 1,6129 · 2,6136 · 1,9792 · 2,0408 · 1,4375 · 1,9 · 1,7857 · 2,3958).

## 3. Bảng bàn giao hình (Số hình | Tệp nguồn | Vị trí | Vấn đề còn thiếu)

| Số hình | Tệp nguồn | Vị trí trong báo cáo | Vấn đề còn thiếu / ghi chú |
|---|---|---|---|
| Hình 1 | `so_do_quy_trinh.png` **v2** (vẽ lại từ §1.5, khổ hẹp) | §1.5 Quy trình thực hiện và phân công | Bản v2: chữ trong sơ đồ ≈7 pt hiệu dụng khi in ở 450 pt (bản v1 chỉ ≈3 pt, không đọc được — đo ở mục 14). Không phải kết quả phân tích; giữ ghi chú phân biệt xử lý hồi cứu với yêu cầu kiểm soát thông tin theo thời điểm của nhánh dự báo |
| Hình 2 | `missing_after_cleaning_8cities.png` | §2.2.8 Các kiểm tra sau xử lý | Đã dựng lại ở vòng v2 (xem mục 10) |
| Hình 3 | `missing_pattern_lucknow_jaipur.png` | §2.2.8 | Chỉ dẫn gốc muốn “hình minh họa nội suy/ngoại lai có đoạn thời gian, đường quan sát và đường ước lượng”; **không tệp nào trong `reports/figures/` đúng dạng đó** → dùng hai hình gần nhất (Hình 4, 5) và nói rõ trong chú thích. Muốn đúng yêu cầu phải sinh hình mới từ notebook (ngoài phạm vi) |
| Hình 4 | `fill_strategies_lucknow_jaipur.png` | §2.2.8 | Nhãn (D) trong hình là nội suy **≤1 ngày**. Theo RA: **không dùng hình làm bằng chứng trực tiếp cho quy tắc 14 ngày** → chú thích đã viết lại: bốn cấu hình là minh họa so sánh chiến lược điền của Notebook 02 trên hai thành phố ví dụ, quy tắc pipeline (≤14 ngày, `Data_dictionary.md`) nêu riêng. Giữ hình vì vẫn giúp giải thích mục “xử lý thiếu” |
| Hình 5 | `outliers_pm25_lucknow_jaipur.png` | §2.2.8 | Đã dựng lại ở vòng v2 |
| Hình 6 | `eda_00_sample_size.png` | §3.2.1 Khác biệt giữa các thành phố | — |
| Hình 7 | `eda_01_poor_share_city.png` | §3.2.1 | — |
| Hình 8 | `eda_05_aqi_distribution.png` | §3.2.1 | — |
| Hình 9 | `eda_02_heatmap_city_month.png` | §3.2.2 Biến động theo thời gian | — |
| Hình 10 | `eda_03_trend_city_year.png` | §3.2.2 | — |
| Hình 11 | `eda_04_pm25_aqi.png` | §3.2.3 Các chất nổi bật trong ngày AQI cao | **Đã đối chiếu nguồn (mục 15)**: hình **không vẽ khoảng nào**; cạnh thanh 2,82 là năm chấm xám = tỷ số riêng từng thành phố (2,06–3,13). Chú thích đã viết lại theo đúng bằng chứng; cặp số [2,42; 3,17] của bản thảo không khớp hình và bảng nguồn → báo nhóm, Bảng 7 giữ nguyên |
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
- **MỤC LỤC — còn 1 thao tác tay, không thể làm qua API**: bộ API Google Docs mà phiên này dùng **không có request chèn mục lục** (vòng v3 đã rà lại toàn bộ danh sách request một lần nữa: chỉ có heading/named style/bảng/hình/section break/header/footer, không có `insertTableOfContents`). Mục lục phải sinh trong giao diện để **số trang tự cập nhật**: mở bản dàn trang → đặt con trỏ ở trang sau bìa → `Insert → Table of contents` (chọn dạng có số trang). Danh sách 72 heading đã sẵn nên mục lục sẽ hiện đủ 3 cấp. Nếu nhóm muốn, tôi có thể dựng một **mục lục tĩnh** (liệt kê 72 mục, không có số trang) làm phương án in tạm — nhưng nó sẽ lệch ngay khi nội dung dịch chuyển, nên không khuyến nghị.

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
| Hình 11: khoảng [2,42; 3,17] | **Đã đối chiếu xong ở vòng v3**: hình không vẽ khoảng; dải thật là 2,06–3,13 (chấm theo thành phố) | Chú thích viết lại theo bằng chứng (mã + bảng đầu ra Notebook 03 + xem trực tiếp hình); cặp số bản thảo được báo là không khớp nguồn; Bảng 7 không thêm khoảng |

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
4. **Tài liệu tham khảo**: xem trạng thái từng nguồn ở mục 16; phần nhóm tự kiểm tra (Kaggle, CPCB, Open-Meteo, scikit-learn, tài liệu nội bộ) vẫn chờ, và ngày truy cập vẫn chưa ghi.
5. **Dấu `*` sau đơn vị nồng độ**: đã đối chiếu mọi nguồn hiện có (mục 15) — không có chú giải ở đâu; Bảng 2 giữ nguyên dấu `*` kèm ghi chú “cần nhóm xác nhận”, không tự quy đổi đơn vị.
6. **Hình minh họa nội suy/ngoại lai** đúng dạng “đoạn thời gian + đường quan sát + đường ước lượng” không có trong `reports/figures/` → nếu cần đúng chỉ dẫn gốc thì phải sinh hình mới từ notebook (ngoài phạm vi dàn trang).
7. **Hai tệp hình chưa dùng** `aqi_monthly_lucknow_jaipur.png`, `aqi_season_lucknow_jaipur.png`: theo chốt của nhóm ở vòng v3 — **giữ nguyên không chèn**, không thêm hình chỉ để dùng hết tệp.
8. **Hyperlink cho URL tham chiếu**: toàn bộ URL trong báo cáo hiện là chữ thường (kiểm tra bản xuất: 0 liên kết). Sau khi nhóm xác nhận nguồn, tôi có thể gắn hyperlink cho 7 mục tham khảo và các URL trong chú thích nếu nhóm muốn.

## 13. Kiểm chứng bố cục vòng v2 (đo bằng script trên bản xuất .docx, không đếm bằng mắt)

- **416 khối nội dung**, chỉ số cuối 91.039 sau vòng v3 (khớp `get_document_end_index`; phần tăng 325 ký tự đúng bằng hai câu chú thích đã viết lại ở Hình 1 và Hình 11, các bảng dịch đúng bằng số đó và không dịch chỗ nào khác).
- **20 ảnh**, mỗi ảnh một đoạn riêng, rộng 450 pt, đúng aspect ratio gốc; **0 đoạn vừa chữ vừa ảnh**.
- **11 bảng native** (10 bảng đánh số + bảng thành viên); phần còn lại là chữ chỉnh sửa được — không trang nào bị biến thành ảnh.
- Chú thích **Hình 1 → Hình 20** đúng thứ tự, mỗi số một lần, luôn nằm **dưới** hình, canh giữa, nghiêng 9 pt, kèm nguồn tệp + kho + nhánh + commit.
- **Bảng 1 → Bảng 10** đúng thứ tự xuất hiện; tên bảng **trên** bảng; mỗi bảng có dòng “Nguồn …” giữ từ bản thảo.
- **72 heading** (7/17/48), không nhảy cấp; §3.3 chạy 3.3.1–3.3.6; Hình 16–20 nằm trong §3.3.1, §3.3.2 (2 hình), §3.3.3, §3.3.4.
- **0** chỉ dẫn `[CHÈN …]`, **0** lần còn “3.3.7”, **0** lần còn “Khi dàn bảng”, **0** lần còn cặp số cũ “60,5 và 55,8”; đúng **2** ghi chú “[CHỜ NGUỒN ẢNH ỨNG DỤNG]”; còn **2** chỗ “[Cần bổ sung]” ở bìa (chờ nhóm).
- Chỉ số dùng cho mọi thao tác sửa đều lấy từ `find_text` ngay trước khi sửa; các phép xoá/chèn trong một lô luôn theo thứ tự chỉ số giảm dần; mô hình chỉ số nội bộ được kiểm bằng 6 mốc neo khớp tuyệt đối.
- Vòng v3: **20/20 đoạn chứa ảnh** và **10/10 đoạn tên bảng** đã bật `keepWithNext` (đo bằng bản xuất: ảnh không rơi xuống cuối trang rời chú thích; tên bảng không rời bảng).
- Vòng v3: kiểm tra khả năng đọc thực tế bằng đo glyph + xem ảnh (mục 14); Hình 1 đã vẽ lại khổ hẹp và thay tại chỗ bằng `deleteContentRange` + `insertInlineImage` đúng 1 chỉ số, không dịch phần còn lại.
- Vòng v4: sau khi rút gọn, bản xuất .docx còn **0** lần xuất hiện của `.png`, `commit c4c75f6`, `HTung0511`, `Data_dictionary.md`, “cần nhóm xác nhận”, “[2,42; 3,17]”; đủ 20 chú thích Hình 1→20, 11 bảng, 20 ảnh, 72 heading; chỉ số cuối 87.115 (giảm 3.924 ký tự truy vết).

## 14. Khả năng đọc thực tế của ảnh và chú thích (vòng v3 — đo đạc + xem ảnh, không chỉ cấu trúc XML)

**Cách đo.** Với mỗi PNG nguồn: đọc kích thước pixel; suy khổ inch từ `dpi` trong mã sinh hình (notebook/`src/*_utils.py`); tính **cỡ chữ hiệu dụng khi ảnh hiển thị 450 pt** = cỡ chữ gốc × 6,25 / khổ inch. Kiểm chứng ngược bằng cách đo **chiều cao glyph thật** trong PNG (phân tích thành phần liên thông trên ảnh nhị phân, `deliverables/layout_assets/legibility_metrics.json`): chữ tiếng Việt có dấu tách thành nhiều thành phần nên phân vị 50 thiên thấp; **phân vị 90 ≈ cỡ chữ nền** của hình. Sau đó xem trực tiếp ảnh ở đúng khổ hiển thị (bản 600 px = 450 pt ở 96 dpi) để xác nhận bằng mắt.

| Số hình | Tệp | W px | DPI tại 450 pt | Chữ nền p90 (pt hiệu dụng) | Cỡ giữa p50 | Nhận xét |
|---|---|---|---|---|---|---|
| Hình 1 (v1 cũ) | so_do_quy_trinh v1 | 5331 | 853 | **3,24** | 2,43 | **Không đọc được** → đã vẽ lại (xem dưới) |
| Hình 1 (v2 hiện tại) | so_do_quy_trinh v2 | 3200 | 512 | **6,56** (nhãn hộp ≈7,0) | 4,82 | Đọc được ở 100 % |
| Hình 2 | missing_after_cleaning_8cities | 1650 | 264 | 6,36 | 5,24 | Ổn |
| Hình 3 | missing_pattern_lucknow_jaipur | 1560 | 250 | 6,33 | 4,75 | Ổn |
| Hình 4 | fill_strategies_lucknow_jaipur | 1690 | 270 | 5,11 | 4,38 | Nhỏ nhất nhóm nghiên cứu — phóng to khi in |
| Hình 5 | outliers_pm25_lucknow_jaipur | 1690 | 270 | 4,75 | 4,75 | Nhỏ — phóng to khi in |
| Hình 6 | eda_00_sample_size | 1200 | 192 | 8,74 | 6,69 | Tốt |
| Hình 7 | eda_01_poor_share_city | 1200 | 192 | 8,74 | 6,69 | Tốt |
| Hình 8 | eda_05_aqi_distribution | 1200 | 192 | 8,74 | 6,69 | Tốt |
| Hình 9 | eda_02_heatmap_city_month | 1500 | 240 | 7,00 | 5,76 | Ổn |
| Hình 10 | eda_03_trend_city_year | 1350 | 216 | 7,77 | 5,94 | Ổn |
| Hình 11 | eda_04_pm25_aqi | 1500 | 240 | 7,00 | 5,35 | Ổn |
| Hình 12 | corr_01_raw_vs_adjusted | 1875 | 300 | 5,27 | 4,12 | Nhỏ — phóng to khi in |
| Hình 13 | corr_02_hypothesis_tests | 1500 | 240 | 6,58 | 4,94 | Ổn |
| Hình 14 | corr_03_humidity_deciles | 1725 | 276 | 6,08 | 4,29 | Nhỏ — phóng to khi in |
| Hình 15 | corr_04_poor_share_by_humidity | 1425 | 228 | 7,36 | 5,63 | Ổn |
| Hình 16 | model_02_mae_by_model | 1500 | 240 | 7,00 | 4,94 | Ổn |
| Hình 17 | model_01_residual_diagnostics | 1725 | 276 | 5,73 | 3,94 | Nhỏ — phóng to khi in |
| Hình 18 | model_03_mae_by_city | 1425 | 228 | 7,36 | 5,63 | Ổn |
| Hình 19 | model_04_precision_recall | 1500 | 240 | 6,58 | 4,53 | Ổn |
| Hình 20 | model_05_humidity_recheck | 1725 | 276 | 5,73 | 4,65 | Ổn |

**Kết luận và xử lý trong phạm vi cho phép (không sinh hình mới từ notebook, không sửa hình nghiên cứu):**

1. **Hình 1 buộc phải vẽ lại**: bản v1 có khổ 17,77 inch nên chữ 9 pt trong mã chỉ còn ≈3,2 pt khi in ở 450 pt — sơ đồ vô dụng trên giấy. Bản v2 giữ **nguyên nội dung, màu, ghi chú**, chỉ thu khổ về 8,0 inch (dpi 400) và ngắt dòng nhãn; chữ nhãn ≈7,0 pt, ghi chú ≈6,3 pt hiệu dụng. Đã thay ảnh trong Docs tại đúng 1 chỉ số (xoá phần tử ảnh cũ, chèn ảnh mới 450 × 86,6 pt vào đoạn giữa canh giữa sẵn có); chú thích Hình 1 cập nhật tên tệp v2.
2. **19 hình nghiên cứu giữ nguyên** (chốt của nhóm). Độ phân giải nguồn 192–300 DPI tại 450 pt là đủ nét để phóng to trên màn hình; chữ nền trong hình ở mức 4,7–8,7 pt hiệu dụng — đọc được khi xem 100–200 % trên màn hình, **nhỏ khi in 100 %**. Bốn hình nhỏ chữ nhất (Hình 4, 12, 14, 17) được nêu tên để người đọc/phòng in biết cần phóng to; **không** tự đổi khổ ảnh vì khổ 450 pt là tiêu chí nghiệm thu và lề trang chỉ còn 3,6 pt dư.
3. **Chú thích đã gánh phần số liệu**: mọi chú thích 9 pt nghiêng đều chép lại các con số then chốt của hình (đo kiểm: đủ 20/20), nên việc đọc hiểu không phụ thuộc vào chữ nhỏ trong hình. Chú thích dài nhất nay là Hình 11 (~860 ký tự ≈ 9 dòng ở khổ 450 pt) vì mang thêm bảng tỷ số theo thành phố — chấp nhận đổi độ dài lấy tính tự chứng minh; nếu nhóm muốn ngắn hơn, có thể chuyển phần tỷ số xuống ghi chú Bảng 7.
4. **Giữ liền khối khi sang trang**: bật `keepWithNext` cho 20 đoạn chứa ảnh (ảnh không rời chú thích) và 10 đoạn tên bảng (tên không rời bảng). Trước vòng v3 cả 30 đoạn này đều chưa có thuộc tính này.

## 15. Đối chiếu hai điểm treo còn lại — chỉ dùng nguồn hiện có, không chạy notebook

**(a) Khoảng “[2,42; 3,17]” cạnh 2,82 ở Hình 11.** Ba lớp bằng chứng cùng nói một kết luận:
- Mã sinh hình (Notebook 03, ô vẽ `eda_04_pm25_aqi`): khung phải vẽ thanh = **trung vị tỷ số của 5 thành phố**, chấm xám = **tỷ số riêng từng thành phố**, chữ cạnh thanh = giá trị trung vị; **không có** `axvspan`/errorbar/annotation khoảng nào.
- Bảng đầu ra của Notebook 03 (ô tính `ratio`): PM2.5 theo thành phố = Jaipur 2,06; Gurugram 2,47; Amritsar 2,82; Delhi 2,99; Lucknow 3,13; trung vị 2,82.
- Xem trực tiếp PNG: chỉ có thanh, chấm và nhãn “2,8 lần”; không có ngoặc khoảng.

⇒ Chú thích Hình 11 đã viết lại đúng bằng chứng: dải cạnh thanh 2,82 là **khoảng trải theo thành phố 2,06–3,13**, không phải khoảng tin cậy; cặp số **[2,42; 3,17] của bản thảo không khớp hình lẫn bảng nguồn** — nêu thẳng trong chú thích để nhóm xác nhận trước khi dùng lại. Bảng 7 giữ nguyên (không thêm khoảng). Đây là báo cáo khác biệt, không phải tự sửa số liệu.

**(b) Dấu `*` sau đơn vị (µg/m³ \*, ppb \*, mg/m³ \*) trong `Data_dictionary.md` mục 1.** Đã quét toàn bộ nguồn hiện có: chính `Data_dictionary.md` (bảng mục 1 và toàn bộ văn bản quanh đó), `docs/`, `README.md`, mã notebook — **không nơi nào có chú giải cho dấu `*`**. Kết luận: không thể giải nghĩa từ nguồn hiện có; Bảng 2 tiếp tục chép nguyên dấu `*` kèm ghi chú “cần nhóm xác nhận”, không suy diễn, không quy đổi đơn vị.

## 16. Trạng thái kiểm tra nguồn tham khảo (vòng v3)

| Mục | Nguồn | Trạng thái từ phiên này |
|---|---|---|
| [1] | Kaggle — Air Quality Data in India | Ngoài phạm vi mạng của phiên → chờ nhóm mở link, ghi ngày truy cập |
| [2] | CPCB — National Air Quality Index | Như trên |
| [3] | Open-Meteo — Historical Weather API | Như trên |
| [4] | GitHub — MTuan1510/Air-Project | **Đã kiểm tra bằng GitHub API**: kho tồn tại, nhánh mặc định `main`, đủ 6 notebook 01–06 như mô tả ✓ |
| [5], [6] | scikit-learn (Ridge, TimeSeriesSplit) | Ngoài phạm vi mạng của phiên → chờ nhóm |
| [7] | Tài liệu học phần INFO3020 (nội bộ) | Nhóm tự đối chiếu bản giảng viên phát |

Ghi chú thêm: (i) toàn bộ URL trong báo cáo hiện là **chữ thường, chưa gắn hyperlink** (bản xuất có 0 liên kết) — tôi có thể gắn sau khi nhóm xác nhận; (ii) ghi chú cuối danh mục của bản thảo (“chưa ghi ngày truy cập…”) vẫn đúng và được giữ nguyên; (iii) các URL kho/commit trong chú thích hình (HTung0511/Air_Project_Test @ c4c75f6) đã kiểm chứng từ vòng v1 bằng chính phép chèn ảnh thành công từ URL ghim commit đó.

## 17. Chính sách chú thích vòng v4 — bản nộp gọn, truy vết nằm ở hồ sơ

**Nguyên tắc áp dụng cho bản nộp (Google Docs/Word):**

1. **Ghi chú chung** (in nghiêng, đoạn thường, đặt ngay đầu Phần II — phần đầu tiên có bảng và hình của nhóm): *“Các bảng và biểu đồ trong báo cáo do nhóm thực hiện từ bộ dữ liệu nghiên cứu, trừ trường hợp có ghi chú khác.”* Nếu nhóm muốn đặt ở đầu Phần III như gợi ý ban đầu, chỉ cần cắt–dán một đoạn; nội dung không đổi.
2. **Hình nhóm tự tạo (cả 20 hình hiện có)**: chú thích = số hình + tên mô tả + phạm vi/đơn vị/ngưỡng/cỡ mẫu khi cần; **không** còn tên tệp PNG, đường dẫn kho, nhánh, commit, URL Drive, hay mô tả lịch sử dàn trang.
3. **Hình lấy nguyên từ bên ngoài**: dẫn nguồn ngắn bằng số tham khảo (hiện không có hình nào thuộc loại này; ảnh ứng dụng sắp chèn là sản phẩm của nhóm nên cũng theo mục 2).
4. **Nguồn dữ liệu và phương pháp**: dẫn ngắn trong nội dung bằng số tham khảo ([1] Kaggle/CPCB, [3] Open-Meteo, [4] kho dự án, …); danh mục tham khảo tập trung cuối bài; từ điển dữ liệu được nhắc bằng cụm “từ điển dữ liệu của kho dự án [4]” thay vì tên tệp.
5. **Giữ nguyên mọi thông tin giúp đọc đúng hình**: đơn vị, trục, chú giải, khoảng thời gian, ngưỡng (201, IQR×1,5, F2/166/160…), cỡ mẫu (n = 8.734; 1.947 cặp test; 5.741 cặp train…), và các cảnh báo diễn giải (test ≠ validation; dải chấm 2,06–3,13 không phải khoảng tin cậy; hai điểm vận hành khác ngưỡng; tiêu chí sắp xếp của Hình 18…).
6. **Ghi chú dưới bảng**: bỏ tên tệp CSV/PNG và câu “cần nhóm xác nhận”; giữ nội dung diễn giải cách đọc bảng; nguồn ghi ngắn dạng “sổ tay tổng hợp của quy trình làm sạch trong hồ sơ dự án [4]”, “bảng kết quả của Notebook 06 [4]”.
7. **Chỗ chờ ảnh ứng dụng**: còn hai ghi chú ngắn dạng “[Chờ ảnh ứng dụng] …” mô tả màn hình/tình huống cần chụp; khi có ảnh thật sẽ thay bằng chú thích số hình + tên giao diện, không kèm tên tệp HTML.

**Nơi lưu truy vết đầy đủ (không nằm trong bản nộp):** bảng mục 3 của hồ sơ này (số hình ↔ tên tệp ↔ vị trí ↔ ghi chú), các payload trong `deliverables/layout_assets/` (URL ghim commit, kích thước, khổ cột bảng), mục 14–16 (đo khả năng đọc, đối chiếu nguồn). Nhóm cần đối chiếu ảnh gốc với kho thì dùng bảng mục 3; giảng viên đọc bản nộp không thấy bất kỳ chuỗi kỹ thuật nào.
