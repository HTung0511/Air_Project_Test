# Đánh giá mức sẵn sàng kỹ thuật của dự án — RA sau kiểm chứng DA

**Cập nhật:** 11/11/2026 · **Phạm vi mới theo yêu cầu:** chỉ xét nội dung dự án và các vấn đề kỹ thuật chính cần sửa.

## 1. Phạm vi và quyết định

**Bỏ Phần 4 — Đạo đức dữ liệu & Báo cáo và Phần 5 — Vấn đáp & Bảo vệ khỏi đánh giá hiện hành.** Không chấm slide, hình thức trình bày, bản báo cáo nộp, vấn đáp hay demo của từng thành viên; không tính việc những phần này chưa làm là lỗi của dự án. Đây là tạm loại khỏi phạm vi, **không chuyển thành “đạt”** và không tự sửa rubric BA.

Vẫn xét tính đúng đắn và khả năng chạy của **sản phẩm kỹ thuật**: leakage, môi trường Python, dependency, cache, phép tính và đánh giá ngoài mẫu. Những vấn đề này vẫn ảnh hưởng dự án dù một số từng được xếp ở Phần 4. Không chấm điểm hoặc dùng lại tổng trạng thái 54 tiêu chí của phiên bản trước.

**Kết luận: dự án đủ nền tảng kỹ thuật để tiếp tục hoàn thiện, nhưng chưa đủ điều kiện chốt là một pipeline dự báo đã được kiểm chứng hoàn chỉnh.** Dữ liệu sạch, EDA và kết quả test chính đã được DA tái lập; hai điểm ưu tiên cao còn mở là preprocessing dùng tương lai và NB04 chưa chạy trọn vẹn trong môi trường DA. Đây không phải kết luận “dự án sai toàn bộ”. [V01], [V05], [V07], [V10], [V21], [NEW-003]

Nếu mục tiêu chỉ là **phân tích mô tả hồi cứu trên dữ liệu hiện có**, phần cốt lõi có thể chấp nhận có điều kiện sau sửa các diễn giải số học/thống kê. Nếu mục tiêu gồm **dự báo ngày mai không nhìn tương lai**, phải khắc phục và kiểm lại preprocessing trước khi chốt. Khả năng cảnh báo vận hành thật là bước riêng, chưa nên biến thành điều kiện bắt buộc của đồ án hồi cứu nếu đề không yêu cầu. [V14], [V16], [V18], [V21], [V24]

**Nguồn đánh giá:** bộ DA tại PR #3, commit `0dfc71568d439b3b2e9dae9a9093f23bcf379969`: `verification_results.md` v1.1, `supplementary_analysis.md` v1.0 và bằng chứng đi kèm. RA đọc hồ sơ/CSV/script, không chạy lại phân tích thay DA. Mọi link V/S được ghim vào snapshot DA này; không có kết quả kiểm chứng mới trong lần thu hẹp phạm vi.

## 2. Những phần chính đã làm được

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Dữ liệu sạch và tích hợp | ✅ Đạt trong phép tái lập đã làm | [V01], [V10], [V11] | Bảng sạch 14056×40, không khác ở dung sai 1e-9; merged 14056×54 giữ nguyên 40 cột AQ. Weather sinh lại có chênh nhỏ, xem mục sửa bên dưới. |
| Quy trình missing/outlier có truy vết | ✅ Có triển khai và số đếm kiểm được | [V01], [V08], [V09] | 2169 ô flatline, 3329 ô nội suy, 41 ô nghi lỗi; không điền nhãn AQI. Heuristic chưa tương đương xác minh lỗi thật từ trạm. |
| EDA ở đâu/khi nào/chất nào | ✅ Kết quả chính được tái lập | [V14], [V15], [V16] | Ba nhóm TP và mùa đỉnh có căn cứ; không cần làm lại toàn bộ EDA. Cần sửa tỷ số và giới hạn cửa sổ. |
| Baseline, chia thời gian, L1–L3 | ✅ Thiết kế và kết quả test có bằng chứng | [V20], [V21] | Test n=1947: persistence MAE 23,47; Ridge L3 19,52. Hiệu −3,95 với CI [−5,40; −2,56]. Đạt test không tự chứng minh no-leakage toàn chuỗi. |
| Kiểm tra độ nhạy | ✅ Có thực nghiệm bổ sung | [V09], [V18], [V19], [S06] | Lợi thế MAE L3 trên test giữ với khối 7/14/28 ngày. Các kết quả vẫn có giới hạn do test đã được dùng khám phá nhiều lần. |

## 3. Các vấn đề chính cần sửa — theo thứ tự ưu tiên

P0 = cần xử lý trước khi chốt pipeline dự báo; P1 = cần xử lý để kết luận phân tích đúng; P2 = tăng độ bền hoặc chỉ cần khi mở rộng mục tiêu. Đây là ưu tiên RA đề xuất, không phải điểm thi.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| **P0 / F01 — Preprocessing còn dùng dữ liệu tương lai** | ❌ Chưa đạt tuyên bố no-leakage end-to-end | [V05], [V07] | `as_of` hiện cắt bảng đã sạch, không chứng minh raw→clean causal. Walk-forward có 57/8912 dòng feature khác; 40 trong mẫu mô hình đều ở train. Dev tách preprocessing cho dự báo khỏi làm sạch hồi cứu; DA kiểm lại từ raw cắt tại t, cả feature, nhãn và mẫu giữ lại. |
| **P0 / F02 — NB04 chưa chạy trọn vẹn theo môi trường tái lập** | ❌ Chưa đạt chạy toàn chuỗi trong môi trường DA | [V10], [NEW-003] | NB04 gọi mạng dù có cache; bản offline vướng f-string trên Python 3.11. Chọn Python hỗ trợ hoặc sửa cú pháp, pin dependency và đọc cache trước; DA chạy lại NB04 nguyên bản và chuỗi 01→06 trong môi trường đã chốt. API bị chặn phải ghi riêng, không coi là dữ liệu sai. |
| **P1 / F03 — Kết luận mô hình cần giới hạn theo tập và ngưỡng** | ⚠️ Số test đúng, chưa được phép khái quát rộng | [V21], [V22], [V24], [S01], [S06] | Holdout: hiệu MAE −1,02 [−2,70; 0,48], chưa tách khỏi baseline; không có nghĩa mô hình vô ích. Ở nhãn ≥301, recall L3 kém baseline. Không chọn lại mô hình/ngưỡng theo test để làm đẹp kết quả; không bắt buộc thắng holdout mới được công nhận kết quả test. |
| **P1 / F04 — Hai lỗi diễn giải số học/thống kê** | ⚠️ Cần sửa ngay, không cần chạy lại EDA toàn bộ | [V16], [V18], [V19] | 2,82 là median của 5 tỷ số TP; 137,1/42,0 là tỷ số gộp 3,26, không cùng phép tính. 32/48 là q_BH<0,05, không phải CI95% đã FDR; CI95% chưa hiệu chỉnh loại 0 là 33/48. Nêu rõ Bonferroni trên 15 so sánh, không 3 toàn bảng. |
| **P1 / F05 — Phạm vi mẫu, cơ chế thiếu và ngưỡng phải nói đúng** | ⚠️ Có bằng chứng mô tả, chưa đủ để khẳng định cơ chế/đại diện | [V08], [V14], [V17], [V26], [S05] | Xác nhận lý do chọn 8/26 TP; không suy “top-8 coverage” hoặc đại diện Ấn Độ. Delhi 51% phải kèm cửa sổ chung. Không gán MAR/MNAR từ block_ratio/thiếu 100%; giữ 14 ngày tạm thời, không gọi tối ưu. Nếu dùng S05 để chọn ngưỡng, DA tính benchmark median tháng sau khi loại block được che. |
| **P1 / F06 — Chốt sự phù hợp với đề bài gốc** | ❓ Cần xác nhận phạm vi, không phải lỗi DA | [V20], [V26] | BA/người phụ trách môn xác nhận AQI ngày mai có thay PM2.5 cùng ngày được không, và dữ liệu AQI theo ngày có được miễn yêu cầu theo giờ không. Nếu đề bắt buộc, bổ sung đúng bài toán/dữ liệu; nếu được phép, giữ pipeline hiện có. Chưa đủ bằng chứng để tuyên bố đáp ứng toàn bộ đề thi. |

### Tiêu chí đóng từng vấn đề

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| F01 — Dev sửa, DA xác minh | Cần thực hiện | [V05], [V07] | Có pipeline dự báo causal riêng; phép cắt/perturb raw sau t không làm đổi đầu vào dự báo đã công bố tại t. Nhãn đánh giá và chính sách revision được mô tả rõ. Đối chiếu metric trên cùng mẫu và giải thích mọi thay đổi mẫu. Biến thể V07 hiện giữ y baseline và có guard DA nên chưa phải bằng chứng src đã sửa. |
| F02 — Dev sửa, DA xác minh | Cần thực hiện | [V10], [V11], [NEW-003], [NEW-004] | Môi trường sạch có Python/dependency chốt; cache có đủ thì không buộc gọi mạng; NB04 chạy xong, 01→06 không lỗi, shape/key/NaN đạt. Weather sai khác phải nằm trong tolerance có lý do; không đòi bitwise bằng nhau vô điều kiện. |
| F03 — Chủ notebook/RA cập nhật kết luận | Cần thực hiện | [V21], [V22], [V24], [S01] | Kết luận phân biệt test/holdout, MAE/recall, ngưỡng201/F2/301 và nghiên cứu hồi cứu/vận hành thật; giữ cả kết quả âm. Không cần ép mọi thử nghiệm thành đạt. |
| F04 — Chủ notebook sửa, RA rà soát | Cần thực hiện | [V16], [V18], [V19] | Mỗi tỷ số ghi đúng tập và cách gộp; chú thích q/CI/family đúng phép kiểm. Không thay số DA để khớp câu cũ. |
| F05 — BA/tác giả xác nhận, DA bổ sung nếu chọn ngưỡng | Cần thực hiện | [V08], [V14], [V17], [S05] | Quy tắc chọn mẫu và cửa sổ rõ; cơ chế thiếu ghi là giả thuyết chưa nhận diện; không dùng benchmark chứa block che để tuyên bố ngưỡng tối ưu. Không đòi chứng minh MAR/MNAR bằng dữ liệu hiện có. |
| F06 — BA/người phụ trách phạm vi xác nhận | Cần thực hiện | [V26] | Có quyết định về hai yêu cầu AQI/PM2.5 và ngày/giờ; các khoảng trống phải được bổ sung nếu bắt buộc. Không chấm slide, vấn đáp hay hình thức. |

## 4. Những điểm không nên biến thành công việc làm lại toàn bộ

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Tác động leakage đo được nhỏ | Giữ kết quả, sửa thiết kế/khẳng định | [V07] | Biến thể feature-as-of cho MAE test 19,517 vs 19,519. Điều này giảm lo ngại rằng toàn bộ lợi thế do leakage, nhưng không đóng F01. |
| Chênh weather 0,01 | Sửa tính tái tạo, không bỏ dữ liệu | [V11], [NEW-004] | 852 ô lệch ≤0,01 quanh biên làm tròn; tác động downstream nhỏ trong phép thử DA. Nguyên nhân phiên bản là giải thích phù hợp, chưa có thí nghiệm kiểm soát phiên bản tác giả. |
| `investigate` lỗi khi chưa có khí — NEW-002 | P2 cho batch hiện tại; nâng thành P0 nếu incremental | [NEW-002], [V07] | Full dataset đã chạy được. Khi sửa F01 thành pipeline tăng dần phải thêm no-gas/empty guard và regression test; wrapper DA chưa sửa mã nguồn chính. |
| Log trỏ notebook07 — NEW-001 | Sửa đường dẫn truy xuất kỹ thuật | [NEW-001], [V01] | Trỏ sang notebook01/assert hiện hành; không cần tái phân tích chỉ vì link cũ. |
| Giờ phát hành AQI/ERA5 | Chỉ bắt buộc nếu tuyên bố cảnh báo vận hành | [V24] | Chưa kiểm được timestamp/độ trễ thực tế. Với đồ án hồi cứu, ghi giới hạn; không yêu cầu dựng hệ thống production nếu ngoài đề bài. |
| NEW-005 — lịch sử commit | Đã đóng, không còn công việc | [NEW-005] | Chấp nhận đính chính v1.1 của DA; không dùng lỗi shallow clone để bác kết quả. |

## 5. Chốt phạm vi hiện tại

- **Không cần làm lại từ đầu:** phần dữ liệu, EDA và mô hình test có căn cứ tái lập. [V01], [V14], [V21]
- **Chưa nên chốt “pipeline dự báo hoàn chỉnh”:** ưu tiên F01–F02; F03–F05 sửa kết luận/cơ sở phương pháp, F06 xác nhận đúng đề. [V05], [V07], [V10], [V16], [V18], [V24], [V26]
- **Không lấy phần chưa làm ngoài kỹ thuật làm lý do đánh trượt:** Phần 4–5 và mọi tiêu chí slide/trình bày/vấn đáp được tạm bỏ khỏi kết luận này. Các tài liệu vòng trước chỉ giữ như lịch sử đánh giá, không dùng tổng 54 tiêu chí cũ để kết luận mức sẵn sàng hiện tại.

## Nguồn bằng chứng DA

[V01]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V01
[V05]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V05
[V07]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V07
[V08]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V08
[V09]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V09
[V10]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V10
[V11]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V11
[V14]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V14
[V15]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V15
[V16]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V16
[V17]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V17
[V18]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V18
[V19]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V19
[V20]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V20
[V21]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V21
[V22]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V22
[V24]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V24
[V26]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#V26
[NEW-001]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#NEW-001
[NEW-002]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#NEW-002
[NEW-003]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#NEW-003
[NEW-004]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#NEW-004
[NEW-005]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/verification_results.md#NEW-005
[S01]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/supplementary_analysis.md#S01
[S05]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/supplementary_analysis.md#S05
[S06]: https://github.com/HTung0511/Air_Project_Test/blob/0dfc71568d439b3b2e9dae9a9093f23bcf379969/Air-Project-main/reports/ra/supplementary_analysis.md#S06
