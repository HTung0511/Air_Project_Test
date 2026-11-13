# BÀN GIAO DÀN TRANG — Báo cáo phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ (Nhóm 25IT)

Vai trò thực hiện: Data Visualization Specialist + Information Designer.
Phạm vi: thiết kế, dàn trang, chèn hình, dựng bảng, đánh số hình/bảng, heading. **Không thay đổi kết quả nghiên cứu, không chạy lại notebook, không dùng ảnh tạo bằng AI.**
Ngày dàn trang: 13/11/2026.

---

## 1. Sản phẩm bàn giao

| Hạng mục | Nội dung |
|---|---|
| Bản dàn trang (Google Docs) | https://docs.google.com/document/d/1vxuomPCYI7acP9ZBFy7miLHwqLAK652Oc4lDjUliBIA/edit — tên tệp: “Báo cáo — Phân tích ô nhiễm không khí 8 TP Ấn Độ — Nhóm 25IT — BẢN DÀN TRANG v1” |
| Bản gốc dùng để đối chiếu | https://docs.google.com/document/d/1wAbxQIyuAgvuOMF_tc4D4TDIjEG6Hsomi5yVfylp11o/edit (không chỉnh sửa) |
| PDF | Không xuất (theo yêu cầu đã cập nhật) |
| .docx | Chỉ xuất để **kiểm tra bố cục nội bộ** (mở lại xem hình/bảng/ngắt trang có dịch chuyển). Sẽ bàn giao file nếu nhóm yêu cầu |
| Script tái lập được | `deliverables/layout_assets/gen_batches.py` (payload 20 hình + 3 ghi chú), `gen_tables.py` (3 bảng native), `make_flow_diagram.py` (Hình 1), `batches.txt` (7 lô request đã áp dụng) |

## 2. Nguồn hình — MỘT nguồn duy nhất, dùng nhất quán

- Kho: **`HTung0511/Air_Project_Test`**, nhánh **`main`**, commit **`c4c75f65c7fb39f843d397bec0ef6c54fd15c29e`**.
- Thư mục hình: `Air-Project-main/reports/figures/` (21 tệp PNG; đã dùng 19 tệp). Đã kiểm SHA-256 từng tệp khớp đúng blob của commit trên.
- Ảnh nhúng trong Docs bằng URL công khai ghim theo commit: `https://raw.githubusercontent.com/HTung0511/Air_Project_Test/c4c75f65.../Air-Project-main/reports/figures/<tên>.png`. Mỗi chú thích đều ghi tên tệp + kho + nhánh + commit.
- **Hình 1 (sơ đồ quy trình)** là tệp vẽ lại từ nội dung §1.5 (không chứa số liệu mới): `deliverables/layout_assets/so_do_quy_trinh.png` (5331×765 px), đã tải lên Drive (id `1H4MHzXLcSVLr9DURzsAfeqL9bHWLLUr8`, chia sẻ “bất kỳ ai có liên kết – người đọc”) vì API Docs chỉ nhận URL công khai. Chú thích ghi rõ đây là sơ đồ dàn trang, không phải kết quả phân tích.
- **Không dùng**: hình/kết quả của PR #3 (`arena/b5aacef3`) và PR #4 – vòng Dev (`arena/5cb21c04`); không gom hình từ nhiều nhánh; không ảnh AI; không thay hình bản Dev/Test.
- Kích thước: mọi ảnh đặt **rộng 450 pt** (khổ A4 trừ lề ≈ 451 pt), chiều cao suy ra từ **aspect ratio gốc của từng tệp** → không kéo méo, không cắt mất thông tin. Trục, đơn vị, khoảng tin cậy, đường ngưỡng, cỡ mẫu, nguồn giữ nguyên như hình gốc; chỉ mô tả lại trong chú thích.

## 3. Bảng bàn giao hình (Số hình | Tệp nguồn | Vị trí trong báo cáo | Vấn đề còn thiếu)

| Số hình | Tệp nguồn | Vị trí trong báo cáo | Vấn đề còn thiếu |
|---|---|---|---|
| Hình 1 | `so_do_quy_trinh.png` (vẽ lại từ §1.5; Drive `1H4MHzXLcSVLr9DURzsAfeqL9bHWLLUr8`) | §1.5 Quy trình thực hiện và phân công nhiệm vụ | Không phải kết quả phân tích; đã giữ ghi chú phân biệt xử lý hồi cứu với yêu cầu kiểm soát thông tin theo thời điểm của nhánh dự báo |
| Hình 2 | `missing_after_cleaning_8cities.png` | §2.2.8 Các kiểm tra sau xử lý | — |
| Hình 3 | `missing_pattern_lucknow_jaipur.png` | §2.2.8 | Chỉ dẫn gốc ở đây yêu cầu “hình minh họa nội suy/ngoại lai có đoạn thời gian, đường quan sát và đường ước lượng”; **không tệp nào trong `reports/figures/` đúng dạng đó** → đã dùng hai hình gần nhất (Hình 4, Hình 5) và nói rõ trong chú thích. Muốn đúng yêu cầu thì phải sinh hình mới từ notebook (ngoài phạm vi) |
| Hình 4 | `fill_strategies_lucknow_jaipur.png` | §2.2.8 | Nhãn (D) trong hình là nội suy khoảng **≤1 ngày**, trong khi quy tắc pipeline là **≤14 ngày** (`Data_dictionary.md`) → đã ghi chú khác biệt trong chú thích, không sửa hình |
| Hình 5 | `outliers_pm25_lucknow_jaipur.png` | §2.2.8 | — |
| Hình 6 | `eda_00_sample_size.png` | §3.2.1 Khác biệt giữa các thành phố | Thứ tự thành phố khác Hình 18 (xem mục 9.3) |
| Hình 7 | `eda_01_poor_share_city.png` | §3.2.1 | Như trên |
| Hình 8 | `eda_05_aqi_distribution.png` | §3.2.1 | — |
| Hình 9 | `eda_02_heatmap_city_month.png` | §3.2.2 Biến động theo thời gian | — |
| Hình 10 | `eda_03_trend_city_year.png` | §3.2.2 | — |
| Hình 11 | `eda_04_pm25_aqi.png` | §3.2.3 Các chất nổi bật trong ngày AQI cao | Trong hình có khoảng **[2,42; 3,17]** cạnh giá trị 2,82 nhưng **không ghi loại khoảng**; §3.2.3 không nêu khoảng này → chưa đưa vào Bảng 7, cần nhóm xác nhận (tin cậy hay phân vị) |
| Hình 12 | `corr_01_raw_vs_adjusted.png` | §3.2.4 Thời tiết–AQI trước và sau điều chỉnh mùa vụ | — |
| Hình 13 | `corr_02_hypothesis_tests.png` | §3.2.4 | — |
| Hình 14 | `corr_03_humidity_deciles.png` | §3.2.4 | — |
| Hình 15 | `corr_04_poor_share_by_humidity.png` | §3.2.4 | — |
| Hình 16 | `model_01_residual_diagnostics.png` | §3.3.7 | Chỉ dẫn gốc gợi ý “đặt cạnh phần 3.3.2” — xem mục 8.9 |
| Hình 17 | `model_02_mae_by_model.png` | §3.3.7 | **XUNG ĐỘT số**: hình hiển thị 64,5 và 43,4 cho hai cột đối chứng, văn bản §3.3.1 nêu ≈60,5 và ≈55,8 (đã ghi chú ngay trong chú thích Hình 17); chỉ dẫn gốc gợi ý “đặt ngay sau Bảng 9” |
| Hình 18 | `model_03_mae_by_city.png` | §3.3.7 | Thành phố xếp theo số ngày AQI ≥201 trong tập test (khác thứ tự ở Hình 6/7/8) — tiêu chí sắp xếp đã ghi trong chú thích |
| Hình 19 | `model_04_precision_recall.png` | §3.3.7 | **XUNG ĐỘT số**: 77%/72% (ngưỡng chọn theo quy tắc F2) khác ≈0,90/0,85 trong văn bản (ngưỡng 201) — hai cặp số thuộc hai ngưỡng khác nhau |
| Hình 20 | `model_05_humidity_recheck.png` | §3.3.7 | — |
| *(chưa có số)* | **Chờ ảnh chụp thật từ tệp HTML** `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` — ảnh tổng quan sản phẩm | §1.4 (giữ ghi chú “[CHỜ NGUỒN ẢNH ỨNG DỤNG — ẢNH TỔNG QUAN SẢN PHẨM]”) | Tệp HTML chưa có trong kho Git đã xác nhận lẫn Drive → chưa chèn ảnh; không thay bằng ảnh mô phỏng/AI. Khi có tệp: chụp rõ vùng chọn thành phố, ngày, kết quả |
| *(chưa có số)* | **Chờ ảnh chụp thật từ tệp HTML** — 4 khung (a) tổng quan, (b) Delhi 24/01/2020, (c) đồ thị toàn kỳ + thanh kéo ngưỡng, (d) màn hình mẫu ít/giới hạn | §3.4.4 (4 chỉ dẫn đã **hợp nhất thành 1 ghi chú** (a)–(d)) | Như trên; ghi chú giữ nguyên hai ràng buộc: không so hai ngưỡng như hai mô hình độc lập; 1.947 là tổng số cặp toàn test, không phải chiều dài ngày lịch của mỗi đường |

**Hai tệp hình KHÔNG được dùng** (bản thảo không có chỉ dẫn chèn, nên không tự đặt vào): `aqi_monthly_lucknow_jaipur.png`, `aqi_season_lucknow_jaipur.png`. Nếu nhóm muốn dùng, cần chỉ định vị trí và khi đó phải đánh số lại dãy hình.

## 4. Ba bảng mới dựng (bảng native, chỉnh sửa được — không phải ảnh)

| Số bảng | Nội dung | Vị trí | Nguồn số liệu |
|---|---|---|---|
| Bảng 2 | Từ điển biến thiết yếu: 15 dòng × 5 cột (Tên biến/nhóm biến – Ý nghĩa – Đơn vị – Vai trò – Lưu ý chất lượng) | §2.1.4 | `Data_dictionary.md` mục 1 và mục 3; ghi chú chất lượng lấy từ §2 của cùng tệp. Danh sách dài không lặp lại ở thân bài — dẫn chiếu Phụ lục A + `Data_dictionary.md` |
| Bảng 5 | Số dòng và số cột của hai nguồn và của bảng ghép: 4 dòng × 4 cột | §3.1.3 | Đối chiếu trực tiếp trên tệp CSV phiên bản nhóm nộp: `air_quality_8cities.csv` 14.056×40; `weather_daily_8cities.csv` 16.128×16; `air_quality_8cities_weather.csv` 14.056×54. Ghi chú nêu rõ **đọc riêng số dòng và số cột, không phải phép cộng số dòng** |
| Bảng 7 | Hai cách tổng hợp tỷ số PM2.5: 3 dòng × 5 cột | §3.2.3 | §3.2.3 của báo cáo: **2,82 = trung vị các tỷ số PM2.5 tính theo 5 thành phố đủ điều kiện**; **≈3,26 = 137,1/42,0 từ trung vị gộp 8 thành phố**; cả hai so **ngày AQI ≥201 với ngày còn lại**, không phải tỷ số mùa. Không thêm khoảng tin cậy chưa rõ loại |

Định dạng bảng: tiêu đề **ở trên** bảng (in đậm 10 pt), ghi chú nguồn/quy ước **ở dưới** (nghiêng 8,5 pt), chữ trong bảng 8,5–9 pt, khổ cột cố định tổng 450 pt, hàng tiêu đề tô nền và **ghim lặp lại** khi sang trang (Bảng 2).

## 5. Đánh số lại dãy bảng theo thứ tự xuất hiện (đã đối chiếu toàn bộ)

Bản thảo đánh số bảng không theo thứ tự xuất hiện (4 → 1 → 5 → 6 → 7 → 2 → 3). Sau khi thêm 3 bảng mới, đã đánh số lại thành **Bảng 1 → Bảng 10** đúng thứ tự xuất hiện:

| Số cũ | Số mới | Tên bảng |
|---|---|---|
| Bảng 4 | **Bảng 1** | Vai trò các nhóm biến trong nghiên cứu |
| *(mới)* | **Bảng 2** | Từ điển biến thiết yếu của bảng phân tích |
| Bảng 1 | **Bảng 3** | Tổng hợp kết quả xử lý dữ liệu chất lượng không khí |
| Bảng 5 | **Bảng 4** | Đơn vị cần phân biệt khi báo kết quả làm sạch |
| *(mới)* | **Bảng 5** | Số dòng và số cột của hai nguồn dữ liệu và của bảng ghép |
| Bảng 6 | **Bảng 6** | Trung vị AQI và tỷ lệ ngày có AQI ≥201 trong khoảng chung (giữ nguyên số) |
| *(mới)* | **Bảng 7** | Hai cách tổng hợp tỷ số PM2.5 |
| Bảng 7 | **Bảng 8** | Tóm tắt family 15 giả thuyết trong phân tích thời tiết |
| Bảng 2 | **Bảng 9** | MAE kiểm thử theo mức đặc trưng, thang điểm AQI |
| Bảng 3 | **Bảng 10** | Các kịch bản minh họa |

Các chỗ dẫn chiếu đã sửa theo (mỗi chuỗi thay đúng 1 lần, đã kiểm): dòng “Nguồn Bảng 3:” (nguồn Bảng 1 cũ), “Nguồn Bảng 9:” (Bảng 2 cũ), “Nguồn Bảng 10:” (Bảng 3 cũ), ghi chú dẫn chiếu ở §3.1.3 trỏ về Bảng 3, và câu “Cần đọc Bảng 6 theo hai chiều” giữ nguyên vì số không đổi.

## 6. Heading và mục lục tự động

- Bản thảo **không có heading style nào** (toàn bộ tiêu đề là chữ thường cùng cỡ với thân bài) → không thể tạo mục lục tự động.
- Đã gắn **73 tiêu đề**: 7 Heading 1 (MỞ ĐẦU, PHẦN I–III, KẾT LUẬN, TÀI LIỆU THAM KHẢO, PHỤ LỤC), 17 Heading 2, 49 Heading 3; không có chỗ nào nhảy cấp (ví dụ H1 → H3).
- Đã định nghĩa lại 3 style cho khớp typography của báo cáo: **Times New Roman, in đậm, màu đen**, cỡ 15/14/13 pt, `keepWithNext`, khoảng cách trên/dưới 18-8 / 15-6 / 11-4 pt, giãn dòng 115%.
- **Còn một thao tác tay** (API Docs không có lệnh chèn mục lục): mở bản dàn trang, đặt con trỏ ở trang sau bìa, `Insert → Table of contents`. Mục lục sẽ tự sinh từ 73 heading trên.

## 7. Chỉ dẫn biên tập đã gỡ khỏi bản nộp

- **26 chỉ dẫn `[CHÈN …]`**: đã xử lý hết, kiểm tra lại bằng tìm kiếm → **0 chỉ dẫn còn lại**.
- **Phụ lục B “DANH MỤC HÌNH NGUỒN CHO DÀN TRANG”**: đã xoá. Lý do: tự ghi “Danh mục này phục vụ AI dàn trang”, và dãy số “Hình 1–15” cũ **mâu thuẫn** với dãy Hình 1–20 mới; thông tin nguồn tệp nay đã nằm trong từng chú thích hình.
- **Phụ lục C “NGUYÊN TẮC BÀN GIAO THIẾT KẾ”**: đã xoá (chính phụ lục này ghi “cần bỏ khỏi bản nộp cuối”).
- **4 chỉ dẫn ảnh ứng dụng ở §3.4.4**: hợp nhất thành **1 ghi chú** liệt kê (a)–(d), không lặp lại 4 lần để tránh tăng trang.
- **Chỉ dẫn hình trùng ở §3.1.3** (yêu cầu chèn lại `missing_after_cleaning_8cities.png`): thay bằng **dẫn chiếu** về Hình 2/Hình 3 ở §2.2.8 và Bảng 3 — không chèn trùng hình.
- **Phụ lục A** (các nhóm biến và tệp nguồn) được **giữ nguyên** và nay đóng vai trò danh sách dài mà Bảng 2 dẫn chiếu tới.
- Dọn 3 đoạn trống thừa còn lại sau khi xoá chỉ dẫn ở §3.4.4; đoạn đệm trước mỗi bảng mới thu về 1 pt.

## 8. Phần còn thiếu / cần nhóm bổ sung hoặc quyết định

1. **5 ảnh ứng dụng**: cần tệp HTML `Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html` (không có trong `HTung0511/Air_Project_Test` ở mọi nhánh đã duyệt, cũng không có trên Drive). Khi nhận tệp, gửi kèm để chụp thật và mô tả là **phát lại lịch sử**.
2. **Trang bìa**: “Hà Nội, tháng [Cần bổ sung] năm [Cần bổ sung]” — chưa điền vì không tự đặt thời gian nộp.
3. **Danh mục tài liệu tham khảo**: bản thảo tự ghi “chưa ghi ngày truy cập vì chưa xác nhận lượt truy cập thực tế” → cần nhóm kiểm tra đường dẫn và điền ngày truy cập.
4. **Dấu `*` sau đơn vị nồng độ** trong `Data_dictionary.md` mục 1 (µg/m³ \*, ppb \*, mg/m³ \*) **không có chú giải** trong tệp nguồn → Bảng 2 chép nguyên dấu `*` và ghi chú “cần nhóm xác nhận”, không tự quy đổi đơn vị.
5. **Khoảng [2,42; 3,17]** cạnh 2,82 trong Hình 11 không ghi loại khoảng (xem mục 3).
6. **Hình minh họa nội suy/ngoại lai** đúng dạng “đường quan sát + đường ước lượng” không tồn tại trong `reports/figures/` (xem Hình 3, mục 3).
7. **Mục lục tự động**: cần một thao tác tay (mục 6).
8. **Hai tệp hình chưa dùng**: `aqi_monthly_lucknow_jaipur.png`, `aqi_season_lucknow_jaipur.png` (mục 3).
9. **Vị trí 5 hình mô hình**: hiện nằm ở §3.3.7 (đúng vị trí chỉ dẫn trong bản thảo), trong khi nội dung chỉ dẫn gợi ý đặt Hình 17 ngay sau Bảng 9 (§3.3.1) và Hình 16 cạnh §3.3.2. Nếu nhóm muốn rời hình, **dãy Hình 16–20 sẽ phải đánh số lại**; cần quyết định trước khi nộp. Ngoài ra tiêu đề §3.3.7 “Các hình cần đặt cạnh kết quả mô hình” mang tính chỉ dẫn — việc đổi tiêu đề là thay đổi nội dung của nhóm nên chưa tự sửa.

## 9. Mâu thuẫn giữa hình và văn bản (CHỈ BÁO CÁO, không tự sửa số)

1. **Hình 17 (`model_02_mae_by_model.png`) vs §3.3.1**: hai cột đối chứng đầu trong hình là **64,5** và **43,4**, văn bản nêu **≈60,5** và **≈55,8**. Năm cột còn lại khớp nhau (23,47 / 22,94 / 20,92 / 19,52 / 19,08). Đã ghi lưu ý đối chiếu ngay trong chú thích Hình 17; nhóm cần kiểm lại bảng nguồn trước khi diễn giải.
2. **Hình 19 (`model_04_precision_recall.png`) vs văn bản**: hình nêu 77%/72% tại điểm chọn theo quy tắc F2, văn bản nêu ≈0,90/0,85 tại ngưỡng 201 → hai cặp số thuộc **hai ngưỡng kích hoạt khác nhau**, không phải một đại lượng.
3. **Thứ tự thành phố không nhất quán giữa các hình**: Hình 6/7/8 xếp theo một trật tự, Hình 18 xếp theo số ngày AQI ≥201 trong tập test. Không sửa thứ tự trong hình; tiêu chí sắp xếp của từng hình đã ghi trong chú thích.
4. **Nhãn nội suy ở Hình 4** (≤1 ngày) khác quy tắc pipeline (≤14 ngày) — đã ghi chú, không sửa hình.

## 10. Kiểm chứng bố cục đã thực hiện

Xuất bản dàn trang ra `.docx` rồi phân tích cấu trúc bằng script (không đếm bằng mắt):

- 440 khối nội dung; **20 ảnh** nhúng (đúng bằng số Hình 1–20); **4 bảng native** (bảng thành viên có sẵn + 3 bảng mới) — phần còn lại là chữ chỉnh sửa được, không có trang nào bị biến thành ảnh.
- **0 chỉ dẫn `[CHÈN …]`** còn lại; đúng **2 ghi chú “[CHỜ NGUỒN ẢNH ỨNG DỤNG]”** ở §1.4 và §3.4.4.
- Dãy **Hình 1 → Hình 20** xuất hiện đúng thứ tự tăng dần, mỗi số đúng một lần; tên hình nằm **dưới** hình, canh giữa, nghiêng 9 pt, kèm nguồn tệp + kho + nhánh + commit.
- Dãy **Bảng 1 → Bảng 10** xuất hiện đúng thứ tự tăng dần; tên bảng nằm **trên** bảng; mỗi bảng có dòng “Nguồn …” giữ nguyên từ bản thảo.
- **73 heading** đúng cấp (7/17/49), không nhảy cấp.
- Chỉ số vị trí dùng để chèn đều lấy từ `find_text` ngay trước khi sửa (không dùng offset tự tính), và được kiểm lại bằng 4 mốc neo khớp tuyệt đối sau khi chèn.
