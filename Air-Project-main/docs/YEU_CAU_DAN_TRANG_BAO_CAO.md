# Yêu cầu biên tập, dàn trang và chèn hình báo cáo

## 1. Phạm vi và nguồn chuẩn

Tên đề tài: **Phân tích ô nhiễm không khí theo thời gian tại tám thành phố ở Ấn Độ**.

- Trường Đại học CMC — Khoa CNTT&TT.
- Học phần: Nhập môn Khoa học dữ liệu; mã học phần INFO3020; lớp25IT.
- Giảng viên: Phạm Ngọc Đông.
- Git nhóm: https://github.com/MTuan1510/Air-Project
- Bản thảo Google Docs: https://docs.google.com/document/d/1wAbxQIyuAgvuOMF_tc4D4TDIjEG6Hsomi5yVfylp11o/edit
- Khung nội dung theo PDF rubric học phần, không lấy ví dụ CNN/MNIST của mẫu TTNT làm yêu cầu chuyên môn.

Mục tiêu: nội dung đầy đủ, giải thích phương pháp và kết quả có chiều sâu. Hướng tới khoảng40 trang tổng thể sau dàn trang là ngân sách tham khảo, không phải bắt buộc làm đủ bằng giãn chữ, lặp hình hoặc sáng tác nội dung. Không chạy lại notebook, không mở thêm phân tích hoặc sửa mô hình.

## 2. Bảo toàn bản thảo

**Phương án RA đề xuất để người dùng chọn:** tạo bản sao Google Docs rồi dàn trang, tên gợi ý “Báo cáo — Ô nhiễm không khí tám thành phố — BẢN DÀN TRANG v1”. Giữ nguyên Doc gốc để đối chiếu. Chưa được mô tả lựa chọn này là quyết định đã được người dùng xác nhận nếu chưa nhận trả lời.

Không tạo nhiều bản song song không cần thiết. Bàn giao link bản sao và ghi rõ bản nào là bản dàn trang chính. Không đổi quyền chia sẻ công khai nếu người dùng chưa yêu cầu.

## 3. Thông tin nhóm đã được xác nhận

| Thành viên | MSSV | Thành phố | Công việc bổ sung |
|---|---|---|---|
| Dương Minh Tuấn — Trưởng nhóm | BIT250370 | Delhi, Gurugram | Notebook05: tương quan giữa các biến và AQI |
| Trần Hoàng Tùng | BIT250381 | Chennai, Hyderabad | Notebook06: dự báo; viết báo cáo; làm slide |
| Lưu Văn Lịch | BIT250211 | Lucknow, Jaipur | Cùng Phạm Tuấn Mạnh thực hiện Notebook04: bổ sung thời tiết |
| Phạm Tuấn Mạnh | BIT252923 | Bengaluru, Amritsar | Cùng Lưu Văn Lịch thực hiện Notebook04: bổ sung thời tiết |

Nhận xét: thái độ hợp tác tốt, hoàn thành phần việc ở mức đáp ứng yêu cầu chung; không tự thêm điểm hoặc tỷ lệ đóng góp. Tháng/năm nộp chưa được xác nhận, để cần bổ sung.

## 4. Cấu trúc đã chốt

- Mở đầu.
- I. Giới thiệu chung:1.1 lý do;1.2 mục tiêu/câu hỏi;1.3 phạm vi;1.4 ý nghĩa/ứng dụng;1.5 quy trình/phân công.
- II. Phân tích bài toán thực tế:2.1 thu thập;2.2 làm sạch/biến đổi;2.3 EDA/trực quan;2.4 mô hình/đánh giá;2.5 đạo đức và trách nhiệm (ngắn, không bắt buộc).
- III. Kết quả:3.1 tiền xử lý;3.2 EDA **gồm thời tiết**;3.3 mô hình;3.4 sản phẩm;3.5 hạn chế;3.6 hướng phát triển.
- Kết luận; tài liệu tham khảo; phụ lục học thuật.

Không thiết kế lại cấu trúc hoặc lược bỏ giải thích quan trọng chỉ để vừa layout. Các ghi chú nội bộ/PR/DA/Dev và phụ lục bàn giao thiết kế không thuộc lời văn bài nộp.

## 5. Biểu đồ và hình nguồn

1. Lấy từ đúng phiên bản Git nhóm được xác nhận. Không tự thay bằng hình ở nhánh Dev/repo Test. Thiếu tệp thì báo, không tạo ảnh biểu đồ bằng AI.
2. Đối chiếu số trong hình với bảng và lời văn. Khác nhau thì ghi vấn đề; không sửa số để khớp bố cục.
3. Giữ dữ liệu, trục, đơn vị, phạm vi ngày, ngưỡng, cỡ mẫu, khoảng bất định, nguồn và chú giải. Không kéo méo hay cắt mất nội dung.
4. Không dùng ảnh sinh để vẽ lại biểu đồ. Nếu cần chất lượng cao hơn, tìm bản SVG/PDF/PNG gốc; không chạy notebook khi chưa được duyệt.
5. Đặt hình cạnh đoạn đọc kết quả; đánh số liên tục và cập nhật toàn bộ lời dẫn/danh mục. Các số hình trong bản thảo là tạm, được đánh lại nhưng không làm sai tham chiếu.
6. Chỉ dẫn22 vị trí không có nghĩa bắt buộc22 hình khác nhau. Không lặp cùng hình để tăng trang. Các sơ đồ quy trình có thể vẽ mới từ nội dung đã xác nhận, nhưng phải phân biệt sơ đồ biên tập với biểu đồ kết quả tính toán.
7. Mỗi hình có tên, nguồn và phạm vi mẫu/thời gian khi cần. Không tự gắn95% CI khi chưa xác định loại khoảng.

## 6. Tệp HTML — làm rõ tình trạng tồn tại và chuyển giao

Tệp **Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html** đã được người dùng đính kèm trong phiên RA và vẫn hiện diện khi kiểm tra tại:

`/tmp/arena-coding-uploads/Canh_bao_o_nhiem_truoc_mot_ngay_Pro_v5.html`

Đây là đường dẫn tạm của **phiên RA**, không phải URL công khai, không bảo đảm truy cập từ phiên AI khác và không chứng minh tệp đã nằm trong Git nhóm/Drive. Không tìm thấy ở các repo hoặc Drive chỉ được báo là **chưa tìm thấy trong nguồn đã kiểm**, không kết luận tệp không tồn tại ở bất kỳ đâu.

Cách tiếp nhận: người dùng đính kèm lại đúng HTML ở phiên thiết kế, hoặc cung cấp nơi lưu bền vững. Commit yêu cầu này KHÔNG bao gồm bản HTML và không có nghĩa đã upload HTML vào Git nhóm.

- Ảnh sản phẩm phải chụp từ HTML thật, không tạo mockup thay ảnh.
- Dùng tên “ứng dụng minh họa/phát lại kết quả trên dữ liệu lịch sử”, không gọi là dự báo trực tuyến.
- Khoảng01/07/2019–29/02/2020 gọi là giai đoạn kiểm thử, không phải toàn bộ mùa đông.
- HTML nguồn từng có câu “chống rò rỉ dữ liệu tuyệt đối”; không dùng câu đó làm kết luận báo cáo. Không sửa riêng ảnh để che khác biệt. Muốn sửa HTML phải phân biệt rõ bản gốc/bản chỉnh và phạm vi được người dùng cho phép.
- Dữ liệu nhúng không tự chứng minh hoàn toàn offline: font/thư viện có thể cần mạng.
- Thiếu HTML ở phiên thiết kế thì tiếp tục dàn các phần khác, ghi ảnh ứng dụng đang chờ; không tái tạo ứng dụng từ trí nhớ.

## 7. Các ranh giới khoa học phải giữ

-8TP là lựa chọn nhóm phục vụ so sánh, không đại diện toàn Ấn Độ/không phải top8.
- Nội suy≤14 ngày là quy ước hồi cứu; không gọi tối ưu hoặc hoàn toàn causal.
-2,82 là trung vị tỷ số PM2.5 ngày nặng/ngày còn lại theo5TP đủ điều kiện;3,26≈137,1/42 là tỷ số gộp8TP. Không gọi là tỷ số mùa.
- Phân biệt ngày lịch và cặp thành phố–ngày; test có1.947 cặp, không phải1.947 ngày lịch của mỗi thành phố.
- Ridge dùng dự báo; OLS dùng diễn giải. SE bền cụm của hệ số khác bootstrap khối của chênh metric.
- L4 dùng thời tiết ngày mai là kịch bản tham chiếu, không phải dự báo hoàn hảo/cận trên toán học.
- Khoảng chứa0: chưa đủ bằng chứng, không kết luận hai phương pháp bằng nhau.
- Không xếp độ lớn tác động từ hệ số khác đơn vị; không suy nhân quả từ tương quan.
- Hiệu năng dự báo lịch sử chịu giới hạn preprocessing; không khẳng định đã loại bỏ mọi leakage. Không trộn metric bản Dev mới chưa tích hợp với kết quả cũ.

## 8. Trích dẫn và bàn giao cuối

Kiểm tra nguồn dữ liệu, thang AQI và tài liệu phương pháp; không tự điền ngày truy cập chưa thực hiện. Không hứa URL đã được kiểm nếu mới sao chép từ bản thảo.

Trước xuất PDF: kiểm mục lục, số bảng/hình, lời dẫn, nguồn, độ nét, ngắt trang, bảng dài và chú thích không tách khỏi ảnh. Chỉ xóa nhãn [CHÈN HÌNH] khi đã xử lý vị trí; phần thiếu phải nằm trong danh sách tồn đọng.

Bàn giao: link Doc dàn trang, PDF nếu đã xuất, và bảng ngắn **Số hình | Tệp nguồn | Vị trí | Vấn đề còn thiếu**. Không nói sẵn sàng nộp nếu còn placeholder hành chính/nguồn hoặc ảnh chưa có.
