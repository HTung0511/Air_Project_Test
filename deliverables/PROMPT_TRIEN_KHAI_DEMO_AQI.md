# Prompt triển khai bản demo AQI đầy đủ

## Vai trò và mục tiêu

Bạn là nhóm thiết kế và phát triển ứng dụng dữ liệu. Hãy xây dựng **một demo tương tác hoàn chỉnh hỗ trợ thuyết trình** về dự án dự báo AQI ngày hôm sau cho tám thành phố. Demo phải trực quan, dễ hiểu, thao tác mượt, có bản sắc thị giác sạch và nhẹ; được phép sáng tạo thiết kế. Đây không phải bộ slide hay báo cáo nhiều chữ. Người thuyết trình diễn giải bằng lời; đồ họa, số liệu và ví dụ hỗ trợ câu chuyện.

Dùng hồ sơ nội dung dự án, mã nguồn/báo cáo và `QUAN_LY_Y_TUONG_DEMO.md` làm cơ sở. File quản lý lưu nguồn từng ý tưởng và điều kiện áp dụng. Phân loại **ưu tiên** và **tham khảo** ở đó là hướng dẫn cho một bản đầy đủ, không phải yêu cầu nhồi tất cả lên một màn hình. Không cần tham khảo hay giả định có demo hiện tại.

## Trải nghiệm và thiết kế

- Giữ **hai lớp nội dung**: màn hình chính ngắn gọn, trực quan cho lúc thuyết trình; lớp chi tiết mở khi cần để giải thích số liệu, phương pháp và hạn chế. Khi đóng chi tiết, giữ nguyên thành phố/ngày/ngữ cảnh.
- Trục thời gian là trung tâm: kéo/chọn ngày và có các mốc hoặc nút chọn nhanh ca tiêu biểu đã kiểm chứng. Cho chọn ngày tự do. Phân biệt rõ ngày đầu vào **t**, ngày dự báo **t+1** và kỳ đánh giá theo ngày đích; không tự nhảy qua ngày thiếu mà không thông báo.
- Thêm **mini map trên nền bản đồ Ấn Độ với đúng 8 chấm tròn**, mỗi chấm đại diện một thành phố trong phạm vi dữ liệu dự án. Dùng vị trí địa lý đã kiểm chứng, đặt tên hoặc nhãn dễ nhận biết; nếu chấm gần nhau thì xử lý để vẫn chọn được chính xác.
- Người dùng **bấm vào chấm để chọn thành phố**: chấm được chọn nổi bật bằng màu và thêm viền hoặc kích thước khác biệt để không phụ thuộc riêng vào màu. Đồng bộ hai chiều với bộ chọn thành phố và timeline: đổi thành phố trên bản đồ cập nhật nội dung ứng với ngày/giai đoạn đang chọn nếu có dữ liệu; đổi ngày hoặc giai đoạn trên timeline cập nhật dữ liệu của bản đồ và thành phố đang xem. Nếu không có dữ liệu cho tổ hợp đã chọn, giữ ngữ cảnh và hiển thị trạng thái thiếu thay vì tự đổi ngày hoặc dùng số cũ.
- Chú giải rõ loại giá trị trên bản đồ (AQI quan sát ngày t, dự báo t+1 hay thực tế t+1), ngày và thang màu khi dùng. Tách cách biểu thị **được chọn** khỏi cách biểu thị **mức AQI** để không gây nhầm lẫn. Mặc định có thể dùng AQI quan sát tại t; chỉ hiện thực tế t+1 sau khi người dùng mở đối chiếu, không để màu bản đồ tiết lộ kết quả trước đó. Thành phố thiếu giá trị cần nhãn riêng, không tô như AQI bằng 0. Các chấm là dữ liệu theo thành phố, không suy rộng thành vùng ô nhiễm liên tục hoặc bản đồ đo trực tiếp. Có bộ chọn thay thế, hỗ trợ bàn phím; ưu tiên bản đồ nhẹ có thể dùng offline, chỉ xác nhận offline sau kiểm thử.
- Luồng kể chuyện chính: chọn thành phố và ngày → xem dự báo t+1 cùng ngữ cảnh cần thiết → tùy chọn mở thực tế và baseline để đối chiếu. Có thể cho hiện ngay thay vì bắt buộc chờ. Khi ẩn thực tế, không để nhãn, màu, mốc hay thống kê vô tình tiết lộ kết quả của ca.
- So sánh dự báo, thực tế và baseline rõ ràng, có thể thử thước hai làn như Y27 thay cho biểu đồ Y03, không mặc định vẽ cả hai. Giữ đúng tỷ lệ, phân vai ngưỡng, xử lý các điểm vượt trục và nêu giá trị thật.
- Sau khi có thực tế, dùng nhãn tiếng Việt ngắn cho đúng một trong bốn trường hợp: báo đúng, bỏ sót, báo nhầm, không cảnh báo đúng. Trong chi tiết có thể dùng ma trận 2×2 giải thích. Không kết luận đúng/sai khi thiếu thông tin cần thiết.
- Dải AQI lịch sử ngắn đến t và phần t+1 mở sau có thể giúp kể chuyện. Sử dụng chuỗi dữ liệu thật, hiển thị khoảng trống thật; không xem bốn biến trễ là chuỗi bảy ngày, không nói AQI được nội suy nếu chưa kiểm chứng.
- Thể hiện thành quả dự án bằng sơ đồ pipeline gọn và bảng/biểu đồ MAE theo mô hình ở lớp chi tiết. Thêm thông tin giải thích hạn chế, cỡ mẫu và ngưỡng theo đúng phạm vi. Chuẩn bị kịch bản báo đúng → bỏ sót → báo nhầm cùng chọn tự do; chọn ca từ dữ liệu đã kiểm tra, nói rõ ca minh họa không đại diện toàn tập.
- Có thể làm ghi chú lời nói và checklist trước trình chiếu thành tài liệu riêng. Thiết kế để đọc được trên máy chiếu và màn hình nhỏ, hỗ trợ bàn phím, nhãn không chỉ dựa vào màu, giảm chuyển động. Hướng tới chạy offline, nhưng chỉ xác nhận sau khi kiểm thử thực tế.

## Dữ liệu, chế độ và tính chính xác

1. **Giữ test và thêm holdout để đối chiếu**, có nhãn rõ, không thay dữ liệu test hay gộp kết quả. Đây là phát lại hồi cứu, không phải vận hành thời gian thực. Không dùng holdout để chọn mô hình.
2. Artifact ứng viên: [`R2_B04_baseline_predictions.csv` tại commit DA 13e93ae](https://github.com/HTung0511/Air_Project_Test/blob/13e93ae12c483f01a573ee51ef9562a315e45068/Air-Project-main/reports/ra/round2/evidence/R2_B04_baseline_predictions.csv). Kiểm tra trước đây thấy 1.947 cặp test, 975 cặp holdout; MAE Ridge L3/baseline lần lượt khoảng 19,52/23,47 và 13,78/14,80. Trước khi sử dụng cần đối chiếu nguồn gốc, cột, ngày đích, split, phiên bản pipeline và nguồn test; không mặc định file có sẵn trên nhánh hiện tại. Không tự tạo dự báo thay thế dữ liệu thiếu.
3. Đối soát số dòng, phạm vi ngày, giá trị, MAE, TP/FP/FN theo cấu hình và nguồn đã chọn; ghi commit, phương pháp và kết quả kiểm. Khớp artifact không chứng minh tái lập toàn bộ pipeline hay hết rò rỉ dữ liệu.
4. Test cho thấy MAE L3 cải thiện so với baseline. Ở holdout, chênh lệch quan sát được nhỏ hơn và khoảng tin cậy chứa 0: diễn đạt **chưa đủ bằng chứng về lợi thế**, không khẳng định tương đương hay không có lợi thế. Trước khi đưa CI cụ thể lên giao diện, đối chiếu phương pháp/phiên bản vì script cho [−2,80; +0,50], báo cáo RA cho [−2,70; +0,48]. Nêu cỡ mẫu và giai đoạn. Không gọi toàn bộ holdout từ 01/03 là phong tỏa.
5. Phân biệt ngưỡng trên dự báo và ngưỡng ngày nặng thực tế. Trong chế độ ưu tiên recall, ngưỡng mô hình 166, baseline 160; thực tế nặng ≥201. Nếu dùng chế độ so sánh cùng ngưỡng 201, ghi rõ cấu hình và tính lại tương ứng. Không điều chỉnh ngưỡng theo test/holdout để làm đẹp kết quả.
6. Quyết định cảnh báo dựa trên **giá trị gốc**, không làm tròn trước. Hiển thị đủ số thập phân gần ngưỡng để tránh trường hợp 165,973826 được hiện thành 166 nhưng lại không báo. Nếu thiếu dự báo, không hiển thị số 0 hay giữ kết quả cũ; nếu có dự báo nhưng thiếu thực tế, có thể hiện dự báo với nhãn chưa đối chiếu. Chỉ nêu lý do thiếu khi đã kiểm chứng.
7. Không tuyên bố pipeline đã hết leakage; nêu hạn chế F01 đúng trạng thái báo cáo. Không diễn giải chênh lệch giữa các mô hình Ridge được fit riêng như đóng góp nhân quả của thời tiết hay chất ô nhiễm. Không gán thống kê nhóm thành phố cho từng thành phố. Không xem CI của MAE là khoảng dự báo từng ngày.

## Ưu tiên và tham khảo

Dùng mục **Phân loại tổng hợp cho bản demo đầy đủ** trong file quản lý làm danh sách chi tiết Y01–Y45. Thực hiện nhóm ưu tiên ở lớp giao diện hoặc tài liệu hỗ trợ phù hợp, sau khi đối soát dữ liệu. Các ý ở nhóm tham khảo có thể chọn thêm nếu làm rõ câu chuyện, không gây quá tải và đáp ứng caveat; không cần triển khai tất cả. Nếu một phần ưu tiên chưa đủ dữ liệu/phương pháp, đánh dấu rõ hạn chế thay vì bịa số hoặc khẳng định đã hoàn thành.

## Bàn giao và kiểm thử

- Bàn giao ứng dụng chạy được, mã nguồn, hướng dẫn chạy và nguồn dữ liệu/phiên bản; giải thích rõ tính năng nào đã làm, phần nào chưa đủ bằng chứng hoặc cần hoàn thiện.
- Kiểm thử chuyển thành phố/ngày và test/holdout; mốc tiêu biểu, ẩn/mở thực tế, bốn trạng thái, giá trị gần ngưỡng, giá trị vượt thang, ngày thiếu và việc giữ ngữ cảnh khi mở chi tiết. Kiểm tra truy cập bàn phím, màn hình trình chiếu và offline nếu có yêu cầu.
- Đối chiếu các số tổng hợp và các ví dụ thực tế với nguồn đã chốt. Báo kết quả kiểm thử thật, không khẳng định hiệu năng hay độ chính xác khi chưa đo.
- Giữ trải nghiệm cân bằng và thẩm mỹ: bản đầy đủ về nội dung và chức năng cần thiết, nhưng màn hình chính vẫn thoáng và phục vụ lời thuyết trình.
