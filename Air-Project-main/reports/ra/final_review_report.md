# Đánh giá mức sẵn sàng kỹ thuật của dự án — RA sau kiểm chứng DA

**Cập nhật:** 11/11/2026 · **Phạm vi mới theo yêu cầu:** chỉ xét nội dung dự án và các vấn đề kỹ thuật chính cần sửa.

## 1. Phạm vi và quyết định

**Bỏ Phần 4 — Đạo đức dữ liệu & Báo cáo và Phần 5 — Vấn đáp & Bảo vệ khỏi đánh giá hiện hành.** Không chấm slide, hình thức trình bày, bản báo cáo nộp, vấn đáp hay demo của từng thành viên; không tính việc những phần này chưa làm là lỗi của dự án. Đây là tạm loại khỏi phạm vi, **không chuyển thành “đạt”** và không tự sửa rubric BA.

Vẫn xét tính đúng đắn và khả năng chạy của **sản phẩm kỹ thuật**: leakage, môi trường Python, dependency, cache, phép tính và đánh giá ngoài mẫu. Những vấn đề này vẫn ảnh hưởng dự án dù một số từng được xếp ở Phần 4. Không chấm điểm hoặc dùng lại tổng trạng thái 54 tiêu chí của phiên bản trước.

**Kết luận: dự án đủ nền tảng kỹ thuật để tiếp tục hoàn thiện, nhưng chưa đủ điều kiện chốt là một pipeline dự báo đã được kiểm chứng hoàn chỉnh.** Dữ liệu sạch, EDA và kết quả test chính đã được DA tái lập; hai điểm ưu tiên cao còn mở là preprocessing dùng tương lai và NB04 chưa chạy trọn vẹn trong môi trường DA. Đây không phải kết luận “dự án sai toàn bộ”. [V01], [V05], [V07], [V10], [V21], [NEW-003]

### Đính chính phạm vi theo người phụ trách dự án

**Nguồn yêu cầu:** người dùng xác nhận trong trao đổi ngày 11/11/2026; đây là thông tin đầu vào về đề bài/quyết định thiết kế, **không phải kết quả thực nghiệm mới của DA**.

- Dự án ban đầu phân tích mức ô nhiễm và so sánh các thành phố. Giáo viên yêu cầu bổ sung khí tượng (mưa, gió, nhiệt độ…) và dự báo để có thêm chiều phân tích. **Hai phần này nằm trong yêu cầu dự án, không phải tự ý mở rộng hay khái quát quá rộng.**
- Theo nhóm, 8 thành phố được chọn vì các chuỗi có khoảng thời gian gần nhau và dữ liệu tương đối đầy đủ; nhiều thành phố còn lại thiếu nhiều dữ liệu quan trắc. Ghi nhận đây là **lý do lựa chọn do tác giả cung cấp**, không tiếp tục để trạng thái “chưa có lý do”. Coverage thực tế đã có trong [V17]; bảng này không chứng minh mọi thành phố ngoài mẫu đều thiếu hơn, cũng không phải đánh giá đầy đủ số trạm khí tượng. AQI lấy qua Kaggle/CPCB, còn khí tượng trong pipeline hiện tại là Open-Meteo/ERA5, không nên gọi toàn bộ là quan trắc khí tượng từ Kaggle. [V10], [V17]
- **Giữ ngưỡng nội suy ≤14 ngày** như quyết định thiết kế thống nhất của nhóm để quy trình trôi chảy và logic; không yêu cầu đổi ngưỡng để dự án được công nhận. Tách lý do thực hành này khỏi khẳng định “14 ngày là lựa chọn duy nhất/tối ưu về khoa học”: DA đã thử các ngưỡng khác và chúng vẫn chạy được; sensitivity không chứng minh tính duy nhất. Không cần thêm thí nghiệm nếu chỉ trình bày trung thực đây là ngưỡng dự án đã chọn. [V09], [S05]

**Đã chốt phạm vi dự báo theo README và đính chính của người dùng:** [`Air-Project-main/README.md`](../../README.md) §4 xác định NB05 phân tích tương quan thời tiết–AQI và NB06 **dự đoán AQI ngày mai, cảnh báo AQI ≥201**. Không có yêu cầu bổ sung mô hình dự báo khí hậu/thời tiết riêng trong phạm vi đã mô tả. Rút câu hỏi lựa chọn A/B và không giao DA xây thêm mô hình nhiệt độ/mưa/gió. Phần mô hình DA đã kiểm đúng loại biến đích này; việc khắc phục F01–F02 vẫn cần thiết. [V20], [V21]

Mạch nội dung chính theo README:

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| NB01–02 — làm sạch và bằng chứng làm sạch | Phạm vi đã xác định | README §4; [V01], [V08], [V09] | Dựng bảng 8 TP và giải thích quyết định missing/outlier. |
| NB03 — EDA | Phạm vi đã xác định | README §4; [V14], [V15], [V16] | Ở đâu, khi nào, chất nào; kiểm tra độ nhạy. |
| NB04 — tích hợp khí tượng | Phạm vi đã xác định | README §4; [V10], [V11] | Thời tiết Open-Meteo/ERA5 theo ngày, ghép với bảng AQ. |
| NB05 — liên hệ khí tượng–AQI | Phạm vi đã xác định | README §4; [V18], [V19] | Tương quan thô/khử mùa, giả thuyết gió/lớp biên/mưa và độ ẩm khám phá; không đồng nhất tương quan với nhân quả. |
| NB06 — dự báo AQI/cảnh báo | Phạm vi đã xác định | README §4; [V20], [V21], [V22] | AQI ngày mai, cảnh báo ≥201; baseline, L1–L3, đánh giá và sensitivity. Không phải dự báo khí hậu. |

Từ đây, F03 chỉ là **cách diễn giải độ tin cậy của kết quả**, không phản đối việc thêm khí tượng/dự báo. Khả năng cảnh báo vận hành thật vẫn là bước riêng, không áp đặt hệ thống production cho đồ án. [V21], [V24]

**Nguồn đánh giá:** bộ DA tại PR #3, commit `0dfc71568d439b3b2e9dae9a9093f23bcf379969`: `verification_results.md` v1.1, `supplementary_analysis.md` v1.0 và bằng chứng đi kèm. RA đọc hồ sơ/CSV/script, không chạy lại phân tích thay DA. Mọi link V/S được ghim vào snapshot DA này; không có kết quả kiểm chứng mới trong lần thu hẹp phạm vi.

### Bối cảnh từ tài liệu giữa kỳ do nhóm cung cấp

RA đã đọc nội dung văn bản của toàn bộ **18 trang** tệp `Giua_ky_INFO3020_O_nhiem_khong_khi_8_thanh_pho.pdf` đính kèm. Tài liệu được dùng để hiểu tiến trình và những giải thích nhóm đã có, **không chấm hình thức slide/vấn đáp** và không thay bằng chứng thực nghiệm DA. Chưa nghiệm thu bằng mắt từng biểu đồ nhúng trong PDF.

- **Trang 2–3:** đã nêu câu hỏi nghiên cứu, đối tượng sử dụng, định nghĩa AQI≥201 trên số ngày có AQI và khoảng chung giữa thành phố. Không tiếp tục đặt lại những câu hỏi này như thể nhóm chưa xác định.
- **Trang 4, 14–15:** đã giải thích flatline, Xylene, nội suy ≤14 ngày, không điền AQI, điểm nghi lỗi và ngoại lai chỉ gắn cờ. Các quyết định có lý do được trình bày; F05 chỉ bổ sung cách diễn đạt mức chắc chắn, không yêu cầu nhóm giải thích lại từ đầu. Số đếm hiện hành đối chiếu ở [V01], [V08], [V09].
- **Trang 11:** đã ghi rõ “2,8 lần” là **trung vị 5 thành phố**. Không gán lỗi ghép 2,8 với 137/42 cho trang này; F04 nhắm đúng các câu ghép sai trong tài liệu hiện hành đã được DA chỉ ra, không sửa hàng loạt những chỗ vốn đúng. [V16]
- **Trang 12, 16–17:** nhóm đã nhận diện thứ hạng trong nhóm không bền, giới hạn do mùa/công thức AQI/PM10 thiếu, điểm nghi lỗi chưa đối chiếu và không gán toàn bộ giảm AQI cho phong tỏa. Đây là những giới hạn đã được nhóm thừa nhận, không phải tất cả là phát hiện mới của RA. Kết quả tái lập/sensitivity hiện hành ở [V14], [V15], [V16].
- **Trang 12:** dự báo AQI ngày mai còn là bước tiếp theo, dự kiến train 2015–2019/test 2020. Đây là kế hoạch giữa kỳ, không phải cấu hình mô hình cuối. Dùng [V20] để xác nhận chia tập hiện hành (train đến 30/06/2019, test 01/07/2019–29/02/2020, holdout từ 01/03/2020); chỉ cần giải thích quá trình cập nhật, không tự coi khác kế hoạch là lỗi.
- Các câu “không có thời tiết” và các dẫn chiếu notebook cũ trong tài liệu này được hiểu theo **snapshot EDA giữa kỳ**, không dùng để phủ định phần khí tượng đã bổ sung sau đó theo README. Căn cứ kiểm chứng tích hợp hiện hành là [V10], [V11], và liên hệ khí tượng–AQI là [V18], [V19].

Từ nay, trước khi hỏi thêm, RA đối chiếu cả README, tài liệu giữa kỳ và hồ sơ DA; chỉ hỏi khi có khoảng trống ảnh hưởng quyết định kỹ thuật mà các nguồn này chưa trả lời. Hai việc sửa mã F01–F02 không được đóng chỉ nhờ có bài thuyết trình; bằng chứng kỹ thuật vẫn là [V05], [V07], [V10], [NEW-003].

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
| **P1 / F03 — Diễn giải kết quả dự báo theo đúng phép đánh giá** | ⚠️ Bổ sung giải thích, không phải mở rộng sai phạm vi | [V21], [V22], [V24], [S01], [S06] | Holdout: hiệu MAE −1,02 [−2,70; 0,48], chưa tách khỏi baseline; không có nghĩa mô hình vô ích. Ở nhãn ≥301, recall L3 kém baseline. Không chọn lại mô hình/ngưỡng theo test để làm đẹp kết quả; không bắt buộc thắng holdout mới được công nhận kết quả test. |
| **P1 / F04 — Hai lỗi diễn giải số học/thống kê** | ⚠️ Cần sửa ngay, không cần chạy lại EDA toàn bộ | [V16], [V18], [V19] | 2,82 là median của 5 tỷ số TP; 137,1/42,0 là tỷ số gộp 3,26, không cùng phép tính. 32/48 là q_BH<0,05, không phải CI95% đã FDR; CI95% chưa hiệu chỉnh loại 0 là 33/48. Nêu rõ Bonferroni trên 15 so sánh, không 3 toàn bảng. |
| **P1 / F05 — Phạm vi mẫu, cơ chế thiếu và ngưỡng phải nói đúng** | ⚠️ Có bằng chứng mô tả, chưa đủ để khẳng định cơ chế/đại diện | [V08], [V14], [V17], [V26], [S05] | Lý do chọn 8 TP đã được tác giả cung cấp ở mục 1; không còn yêu cầu xác nhận lại động cơ chọn mẫu. Giữ 14 ngày là ngưỡng dự án. Phần viết bổ sung cần nêu coverage/cửa sổ, tránh gán chắc MAR/MNAR và tránh nói ngưỡng duy nhất/tối ưu; chỉ yêu cầu DA sửa benchmark nếu dùng S05 để khẳng định tối ưu. |
| **F06 — Biến đích và phạm vi phân tích** | ✅ Đã làm rõ, đóng câu hỏi phạm vi | README §4; [V20], [V21], [V22] | Phân tích khí tượng–AQI và dự báo AQI ngày mai/cảnh báo ≥201 là đúng mạch dự án. Không yêu cầu thêm dự báo khí hậu hoặc tự áp thêm bài toán PM2.5/giờ ngoài phạm vi đã thống nhất. Đây là đóng câu hỏi yêu cầu, không có nghĩa mọi kiểm tra kỹ thuật mô hình đã đạt. |

### Tiêu chí đóng từng vấn đề

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| F01 — Dev sửa, DA xác minh | Cần thực hiện | [V05], [V07] | Có pipeline dự báo causal riêng; phép cắt/perturb raw sau t không làm đổi đầu vào dự báo đã công bố tại t. Nhãn đánh giá và chính sách revision được mô tả rõ. Đối chiếu metric trên cùng mẫu và giải thích mọi thay đổi mẫu. Biến thể V07 hiện giữ y baseline và có guard DA nên chưa phải bằng chứng src đã sửa. |
| F02 — Dev sửa, DA xác minh | Cần thực hiện | [V10], [V11], [NEW-003], [NEW-004] | Môi trường sạch có Python/dependency chốt; cache có đủ thì không buộc gọi mạng; NB04 chạy xong, 01→06 không lỗi, shape/key/NaN đạt. Weather sai khác phải nằm trong tolerance có lý do; không đòi bitwise bằng nhau vô điều kiện. |
| F03 — RA/người viết nội dung bổ sung diễn giải | Cần thực hiện | [V21], [V22], [V24], [S01] | Kết luận phân biệt test/holdout, MAE/recall, ngưỡng201/F2/301 và nghiên cứu hồi cứu/vận hành thật; giữ cả kết quả âm. Không cần ép mọi thử nghiệm thành đạt. |
| F04 — Người viết nội dung sửa, RA rà soát | Cần thực hiện | [V16], [V18], [V19] | Mỗi tỷ số ghi đúng tập và cách gộp; chú thích q/CI/family đúng phép kiểm. Không thay số DA để khớp câu cũ. |
| F05 — Người viết nội dung bổ sung căn cứ thiết kế | Cần thực hiện | [V08], [V14], [V17], [S05] | Ghi lý do chọn mẫu theo giải thích của nhóm, minh họa bằng coverage hiện có; giữ 14 ngày và giải thích là lựa chọn thực hành. Cơ chế thiếu ghi là giả thuyết chưa nhận diện. Chỉ cần DA tính lại benchmark nếu muốn khẳng định ngưỡng tối ưu, không yêu cầu thử ngưỡng mới để đổi thiết kế. |
| F06 — Đã đóng theo README/người dùng | Không còn việc bổ sung mô hình thời tiết | README §4; [V20], [V21], [V22] | Giữ mục tiêu AQI ngày mai và cảnh báo ≥201; tập trung sửa F01–F02 và bổ sung diễn giải F03–F05. |

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
- **Chưa nên chốt “pipeline dự báo hoàn chỉnh”:** ưu tiên F01–F02; F03–F05 bổ sung kết luận/cơ sở phương pháp; F06 đã đóng theo README và đính chính của người dùng. [V05], [V07], [V10], [V16], [V18], [V24], [V26]
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
