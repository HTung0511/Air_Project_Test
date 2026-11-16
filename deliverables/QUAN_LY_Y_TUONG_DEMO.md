# Quản lý ý tưởng cải tiến demo AQI

**Ngày rà soát:** 13/11/2026  
**Đầu vào:** `mistral4.txt`, `qwen3.8.txt`, `muse-spark-1.3.txt`, `seed-2.1.txt`, `gemini-4-argon.txt`, `qwen3.8-max.txt`, `gemini4-carbon.txt`, `ernie-5.5.txt`, `deepseek-v4.1.txt`, `mimo-v2.6.txt`, `mistral-large4.txt`, `minimax-m3-1.txt`, `inkling-2.txt`, `haiku-5.5.txt`, `argon-high.txt` và `sonnet-5.5.txt` do người dùng cung cấp. Tên nguồn bên dưới dựa trên tên tệp, không xác nhận danh tính mô hình.  
**Phạm vi:** Đánh giá đề xuất, chưa triển khai và chưa phê duyệt thay người dùng. Đánh giá thiết kế dưới đây là định hướng, không phải kết luận về giao diện thực tế.

## Nguyên tắc đã thống nhất

- Ứng dụng tương tác hỗ trợ thuyết trình, không phải slide hoặc báo cáo dài.
- Màn hình chính ngắn gọn; chi tiết, phương pháp và giới hạn nằm ở lớp mở rộng.
- Trục thời gian tương tác và chọn các mốc tiêu biểu là trải nghiệm trung tâm.
- Phát lại dữ liệu lịch sử; phân biệt ngày đầu vào t, ngày đích t+1, dự báo và thực tế.
- Nhẹ, dễ thao tác, không tự tạo số liệu. Giữ trung thực về hạn chế và rò rỉ dữ liệu.

## Sổ ý tưởng tổng hợp

| Mã | Ý tưởng | Nguồn | Vị trí | Đánh giá / điều kiện | Trạng thái |
|---|---|---|---|---|---|
| Y01 | Trục thời gian t → t+1; ghi rõ test/holdout và ngày không có dữ liệu | Mistral 1; Qwen 1; Muse 1; Seed 3, 4 | Chính | Nên giữ gọn; phân kỳ theo ngày đích. Chỉ cho phát lại ngày thực sự có dự báo. Không bắt buộc thêm vùng train nếu gây rối. | Nên thử, chờ duyệt |
| Y02 | Dấu mốc hoặc nút chọn nhanh ca báo đúng, bỏ sót, báo nhầm | Mistral 2, 5; Qwen 3; Muse 1; Seed 3 | Chính | Chọn ít ca; cập nhật khi đổi thành phố và ngưỡng, nêu đây là ví dụ, không đại diện toàn bộ. Cần dữ liệu từng ngày và quy tắc chọn rõ. | Nên thử, cần kiểm chứng dữ liệu |
| Y03 | Thẻ so sánh dự báo, thực tế, baseline trên cùng trục AQI | Mistral 3; Qwen 2; Muse 2; Seed 2 | Chính | Trực quan, đúng trọng tâm. Nhãn rõ và phân biệt dự báo với giá trị quan sát sau đó; chỉ hiển thị trạng thái đang xảy ra, không bắt buộc bốn ô cùng lúc. Kiểm tra giá trị vượt phạm vi trục. | Nên thử, chờ duyệt |
| Y04 | Nút mở kết quả thực tế sau khi trình bày dự báo | Qwen 2; Muse 3; Seed 5 | Chính, tùy chọn | Hỗ trợ diễn thuyết và tránh nhầm biết trước tương lai; thêm một bước thao tác. Nên cho phép mở ngay hoặc bật/tắt chế độ này. | Nên thử, chờ duyệt |
| Y05 | Thanh AQI ngắn thể hiện diễn biến những ngày quanh ngày chọn | Mistral 4; Seed 4 | Chính hoặc chi tiết | Có thể giúp thấy xu hướng trước một ca đột biến; chỉ thêm nếu không chật. Chưa xác nhận quy tắc diễn giải cờ chất lượng; không gọi AQI là nội suy khi dự án không nội suy AQI. | Cần kiểm chứng / thử thiết kế |
| Y06 | Bảng kết quả test và holdout, ngưỡng và giới hạn | Mistral 6, 7; Qwen 4; Muse 5; Seed 6, 7 | Chi tiết | Giữ bảng ngắn; tách test/holdout, nêu KTC khi phù hợp; không khẳng định chống rò rỉ tuyệt đối. Thông số nhóm thành phố và ngưỡng phải ghi phạm vi rõ. | Nên thử, chờ duyệt |
| Y07 | Ghi chú lời nói cho từng tình huống | Mistral 5; Qwen 3; Muse 5; Seed 8 | Tài liệu riêng | 2–3 câu mỗi ca, không đưa thành chữ dài lên màn hình. Có thể dùng file ngoài thay vì ứng dụng ẩn; phím tắt không đảm bảo giấu nội dung khỏi máy chiếu. | Nên thử, chờ duyệt |
| Y08 | Tóm tắt pipeline và thành tựu dự án | Qwen 8; Mistral 7 | Chi tiết | Một sơ đồ ngắn là đủ; không chuyển ứng dụng thành slide. Mỗi tuyên bố kiểm chứng có nguồn, trạng thái chưa hoàn thành phải hiển thị trung thực. | Cân nhắc |
| Y09 | Bộ chọn thành phố dạng hồ sơ / thẻ nhỏ | Qwen 6 | Chính | Có thể đẹp hơn dropdown nhưng tám thẻ dễ chiếm không gian; quyết định sau khi xem màn hình thực và thử kích thước máy chiếu. | Cân nhắc |
| Y10 | Đặt tình huống đang chọn trong phân bố sai số test | Qwen 7 | Chi tiết | Có giá trị chuyên môn nhưng dễ khó hiểu, cần định nghĩa mẫu, thang và dữ liệu; không đưa lên màn hình chính mặc định. | Để sau / cần kiểm chứng |
| Y11 | Giải thích đóng góp từng đặc trưng vào dự báo | Qwen 5 | Chi tiết | Rủi ro diễn giải nhân quả hoặc đóng góp sai do chuẩn hóa/biến đổi log và giá trị thiếu. Chỉ xem xét khi có mô hình, phép tính và kiểm định được xác minh. | Không ưu tiên / cần kiểm chứng |
| Y12 | Offline, hỗ trợ bàn phím, giảm chuyển động và không phụ thuộc màu | Cả tám | Nền tảng | Là yêu cầu chất lượng, không nhất thiết là một tính năng hiển thị. Chỉ khẳng định chạy mượt hoặc offline sau khi thử. | Yêu cầu nền đã thống nhất |

## Bổ sung từ Muse Spark và Seed

| Mã | Ý tưởng | Nguồn | Đánh giá / điều kiện | Trạng thái |
|---|---|---|---|---|
| Y13 | Nhãn kết quả tiếng Việt cho đủ bốn trường hợp | Muse 4; Seed 1 | Hiển thị duy nhất trạng thái đang xảy ra: báo đúng, bỏ sót, báo nhầm hoặc không cảnh báo đúng. Nếu thiếu dự báo hoặc thực tế, báo thiếu dữ liệu; không kết luận đúng/sai. Phân biệt bằng chữ và hình, không chỉ màu. | Nên thử, chờ duyệt |
| Y14 | Ngăn chi tiết giữ nguyên thành phố và ngày đang xem | Muse 5; Seed 6, 7 | Có thể mở/đóng và trở về đúng vị trí; cần thử trên màn hình nhỏ. Không mặc định chấp nhận ngăn năm tab và nhiều chú thích vì dễ tái tạo cảm giác quá tải. | Nên thử, chờ duyệt |
| Y15 | Tự phát / tự tiết lộ theo kịch bản | Seed 5 | Có thể hỗ trợ tập dượt, nhưng mất quyền chủ động, gây lộ kết quả trước lời nói và thêm phức tạp. Ưu tiên nút thủ công Y04; chưa cần thêm chế độ tự phát. | Không ưu tiên |
| Y16 | Toàn bộ ngày hiển thị chấm kết quả trên timeline | Seed 3 | Có thể cho ngữ cảnh nhưng hàng trăm dấu khó đọc khi chiếu, có nguy cơ tiết lộ kết quả trước khi mở thực tế và cần dữ liệu ngày đầy đủ. Ưu tiên vài mốc Y02; nếu thử phải có lựa chọn ẩn outcome. | Để sau / cần kiểm chứng |
| Y17 | Trợ giúp ⓘ tại chỗ | Seed 7 | Có thể làm rõ ngưỡng nhưng không nên giấu thông tin thiết yếu chỉ trong tooltip; hỗ trợ bấm, bàn phím và cảm ứng. Tối giản số biểu tượng. | Cân nhắc |

### Nhận xét riêng hai bài mới

- **Muse Spark:** ủng hộ rõ nhất luồng ba ca → so sánh → mở kết quả; phần ngăn chi tiết giữ ngữ cảnh đáng thử. Không coi câu “giảm 80% nguy cơ nhầm” là kết quả đo được: tài liệu không đưa phép đo. Các con số trong ví dụ về thước cần coi là minh họa trừ khi được xác minh.
- **Seed:** cách gọi bốn trạng thái và phân biệt hai ngày có ích. Tuy nhiên không chấp nhận ý “test dùng chọn mô hình”: dự án chọn trên train/CV, test để đánh giá. Holdout vẫn dùng để đánh giá bổ sung, không dùng để chọn mô hình; tránh nói “không dùng để đánh giá”. Dùng nhãn holdout thay vì gọi toàn bộ từ 01/03 là phong tỏa.
- **Seed — sparkline:** `aqi_0`, `aqi_1`, `aqi_2`, `aqi_wk` không phải bảy giá trị AQI theo ngày; muốn vẽ 7 ngày cần chuỗi thực tế và xử lý các ngày thiếu. Không khẳng định AQI được nội suy.
- **Cả hai:** đặt 160, 166 và 201 cùng một thước có thể gây nhầm hoặc chồng chữ vì gần nhau; nếu dùng cần phân vai rõ ngưỡng dự báo và ngưỡng ngày nặng thực tế, thử trước khi chốt. Các tuyên bố “giảm 80% thời gian” hay lợi ích số hóa khác là ước đoán, không có bằng chứng thử nghiệm.
- **Nút tiết lộ thực tế:** nếu đang ẩn, dấu mốc, nhãn và trạng thái không nên vô tình tiết lộ outcome; cho phép hiện ngay khi người thuyết trình muốn.

## Bổ sung từ Gemini Argon và Qwen Max

| Mã | Ý tưởng | Nguồn | Đánh giá / điều kiện | Trạng thái |
|---|---|---|---|---|
| Y18 | Ngữ cảnh cỡ mẫu cảnh báo theo nhóm thành phố | Gemini 4; Qwen Max 6 | Chỉ hiện thông báo ngắn khi thật cần và đặt bảng ở lớp chi tiết. Phải ghi đây là kết quả gộp nhóm test ở ngưỡng nào; không gán recall/precision nhóm thành kết quả riêng từng thành phố. Dưới 30 là quy ước thận trọng của dự án, không phải luật thống kê phổ quát. | Cân nhắc, cần kiểm chứng |
| Y19 | Bậc thang MAE baseline → L1 → L2 → L3 | Gemini 5 | Biểu đồ nhỏ ở lớp chi tiết giúp giải thích thành quả của các bước bổ sung thông tin. Số liệu tổng hợp test cần đối chiếu; MAE giảm không chứng minh thời tiết tạo thêm lợi thế cảnh báo hay quan hệ nhân quả. Không nhầm đây là giải thích nhân quả cho một ca cụ thể. | Nên thử ở lớp chi tiết, chờ duyệt |
| Y20 | Lược đồ SVG vị trí 8 thành phố thay bộ chọn thông thường | Qwen Max 7 | Có thể tạo bản sắc thị giác nếu thực sự giúp chọn nhanh. Cần tọa độ kiểm chứng, nhãn “vị trí tương đối”, xử lý chồng lấn và hỗ trợ bàn phím; không suy luận vị trí địa lý là nguyên nhân ô nhiễm. Tránh tô màu outcome khi đang giấu kết quả. | Để sau / thử nghiệm thiết kế |
| Y21 | Đánh dấu ca hụt đỉnh đột ngột | Qwen Max 8 | Chọn ca đã được kiểm chứng hoặc định nghĩa quy tắc định lượng rõ và nêu đây là quy ước demo, không phải phát hiện riêng của dự án. Không khẳng định nguyên nhân tăng đột ngột nếu chưa có bằng chứng. | Cần kiểm chứng |
| Y22 | Bảng bằng chứng test/holdout kèm KTC | Qwen Max 5; Gemini 6 | Gộp với Y06, chỉ mở khi hỏi sâu; giữ số dòng vừa đủ, kèm nhãn giai đoạn, nguồn và mẫu. Không dùng câu “test chỉ mở một lần” như sự thật nếu báo cáo nói test đã được khám phá nhiều lần. | Nên thử ở lớp chi tiết, chờ duyệt |

### Nhận xét riêng hai bài

- **Gemini Argon:** sơ đồ bậc thang các mức đặc trưng là bổ sung hữu ích để phô diễn phần nghiên cứu, nếu chỉ đặt trong lớp chi tiết. Badge theo nhóm thành phố có giá trị khi giải thích hạn chế mẫu nhưng có nguy cơ làm người xem tưởng thống kê của nhóm là thống kê của từng thành phố.
- **Qwen Max:** đề xuất tách vai trò các ngưỡng và báo thiếu dữ liệu là phù hợp. Lược đồ thành phố là phương án sáng tạo có thể thử, không phải yêu cầu bắt buộc. Ngày thiếu dự báo có thể do nhiều lý do; chỉ nêu lý do cụ thể khi đã xác minh, nếu không chỉ ghi “không có kết quả phát lại”.
- Cả hai chưa xem demo hiện tại; nhận xét là ý tưởng dựa trên mô tả, không phải kết quả kiểm thử giao diện. Khẳng định về nguồn, kích thước file, tốc độ hay chạy mượt trong các bài cần xác minh độc lập.
- Không xem dự báo trên train như dự báo kiểm thử ngoài mẫu. Con số 8.663 trong đề xuất Gemini là số cặp dữ liệu đủ điều kiện qua các tập, không chứng minh đã có 8.663 dự báo độc lập từng ngày.
- F2 với beta=2 tăng trọng số recall so với precision trong phép tính F-score; không tự diễn dịch thành “chi phí bỏ sót gấp đôi báo nhầm” nếu không có phân tích chi phí riêng. KTC chứa 0 nghĩa là chưa đủ bằng chứng phân biệt khác 0, không chứng minh chắc chắn không có hiệu ứng.
- Trường hợp bị đặt cờ nghi lỗi một chất không tự động chứng minh ngày đó không thể dự báo AQI: cần kiểm tra đặc trưng, cách điền thiếu và kết quả thực tế trước khi gắn nhãn.

## Bổ sung từ Gemini Carbon và Ernie

| Mã | Ý tưởng | Nguồn | Đánh giá / điều kiện | Trạng thái |
|---|---|---|---|---|
| Y23 | Ma trận 2×2 giải thích vì sao báo đúng, bỏ sót hoặc báo nhầm | Ernie 04 | Khi người trình bày cần giải thích, mở lớp chi tiết và tô đúng một ô của ca đang chọn; mặc định chỉ hiện một nhãn kết quả ngắn (Y13). Phân biệt ngưỡng cảnh báo trên dự báo với AQI thực tế ≥ 201. | Nên thử trong lớp chi tiết, chờ duyệt |
| Y24 | So sánh L1 → L2 → L3 cho ngày đang chọn | Gemini Carbon 5 | Có thể minh họa các mô hình thay đổi dự báo thế nào; cần dự báo từng mức cùng snapshot và kiểm tra nguồn. Đây là các mô hình được fit riêng: chênh lệch dự báo không chứng minh đóng góp nhân quả hay giải thích chính xác từng đặc trưng; không giả định L3 luôn gần thực tế hơn. Khác với Y19 là MAE tổng hợp trên test. | Để sau / cần kiểm chứng |
| Y25 | Hai chế độ ngưỡng đã định sẵn, thay vì thanh kéo tự do | Gemini Carbon 8 | Tùy chọn ở lớp chi tiết: mô hình/baseline 166/160 hoặc cùng 201. Đổi ngưỡng phải cập nhật nhãn, kết quả và mốc tình huống theo dữ liệu gốc; không chọn lại ngưỡng từ test để làm đẹp. So sánh hai chế độ cần ghi rõ mẫu và đánh đổi. | Cân nhắc, cần kiểm chứng dữ liệu |
| Y26 | Phân biệt trạng thái dự báo thiếu và thực tế thiếu | Ernie 07 | Nếu chỉ thiếu thực tế nhưng có dự báo hợp lệ, vẫn có thể hiển thị dự báo/cảnh báo với nhãn “chưa có thực tế để đối chiếu”, không đưa kết luận đúng/sai. Nếu thiếu dự báo, không giữ kết quả cũ và không hiển thị số 0. Chỉ áp dụng trường hợp có dữ liệu hỗ trợ, không giả định snapshot hiện tại có đủ. | Nên thử, cần kiểm chứng |

### Nhận xét riêng hai bài

- **Gemini Carbon:** thiết kế mở kết quả theo hai nhịp nhưng có thể tắt là phù hợp buổi thuyết trình. Tuy nhiên không nên suy ra một ngày thiếu dự báo là do điểm nghi lỗi cảm biến nếu chưa đối chiếu nguyên nhân thực. Gợi ý ngưỡng khóa sẵn đáng cân nhắc hơn thanh kéo tùy ý, nhưng không bắt buộc đưa lên màn hình chính.
- **Ernie:** điểm đáng giữ là “một màn hình, một kết luận”; phân biệt màu cho kết quả cảnh báo với màu phân loại chất lượng không khí. Một cảnh báo đúng không có nghĩa không khí tốt, và so sánh hơn baseline ở một ngày không chứng minh hơn trên toàn tập.
- **Cả hai:** chưa xem demo hiện tại theo báo cáo của họ; các tuyên bố về bố cục chỉ là đề xuất. Đảm bảo trục thời gian thể hiện khoảng cách lịch thực nếu có ngày thiếu, không nối qua khoảng trống như thể có dữ liệu.
- Không tự quy nguyên nhân một ca tăng AQI cho phát thải bất thường, thời tiết hoặc sự kiện nếu không có bằng chứng. Không gán một ca là “hụt đỉnh” chỉ từ một ngưỡng mới chưa được chốt.

## Bổ sung từ DeepSeek, MiMo và Mistral Large

| Mã | Ý tưởng | Nguồn | Đánh giá / điều kiện | Trạng thái |
|---|---|---|---|---|
| Y27 | Thước quyết định hai làn: dự báo/ngưỡng 166 và thực tế/mốc 201 | DeepSeek I1 | Hai làn cùng một thang AQI, nhãn và kiểu đánh dấu riêng có thể giúp giải thích vai trò hai ngưỡng mà không nhồi ba vạch cạnh nhau. Baseline 160 có thể để trong chi tiết, nhưng so sánh nếu có phải ghi ngưỡng riêng. Tránh trục phóng sai lệch hoặc biểu đồ chật trên máy chiếu. Đây là phương án thiết kế thay thế Y03, không phải thêm biểu đồ thứ hai. | Nên thử bản phác, cần dữ liệu kiểm chứng |
| Y28 | Hai cách kể một ca: dự báo trước hoặc thực tế trước | DeepSeek I2; MiMo Y3 | Dự báo trước + mở thực tế phù hợp luồng chính Y04. Thực tế trước là tùy chọn kể ngược cho một ca đã xảy ra; không dùng đồng thời nếu muốn giữ bất ngờ. Công bố cách chọn ca khi phù hợp và không ngụ ý ca được chọn đại diện toàn tập. Không khóa mũi tên đổi ngày cho đến khi mở thực tế. | Cân nhắc, cần thử người dùng |
| Y29 | Lý do ngày thiếu kết quả, có bằng chứng | DeepSeek I3; MiMo Y4 | Bổ sung Y26: chỉ nêu lý do cụ thể nếu có cờ/lý do được QA từ đúng pipeline; nếu không ghi “không có kết quả phát lại”. Phân biệt dự báo không được xuất với thực tế thiếu; thiếu nhãn t+1 không chứng minh không thể dự báo tại t. Không tự nhảy ngày mà không thông báo. | Nên thử trạng thái chung; lý do cần kiểm chứng |
| Y30 | Dải bất định theo từng ngày | DeepSeek I4 | Chỉ xem xét nếu có phương pháp và artifact phù hợp được xác minh, hiệu chuẩn trên train/validation và kiểm tra độ phủ; không dùng CI của MAE làm khoảng dự báo. Một dải giao ngưỡng không tự tạo quyết định “lưỡng lự” nếu dự án chưa định nghĩa chính sách. | Không ưu tiên / nghiên cứu thêm |
| Y31 | Dải sai số điển hình quanh dự báo | MiMo Y5; Mistral Large ID-5 | Rủi ro bị hiểu là khoảng dự báo, dùng kết quả test để hiệu chỉnh trình bày. Đặc biệt không chọn MAE nhóm “ngày nặng” hay “ngày thường” dựa vào AQI thực tế ngày mai như thể biết tại thời điểm t. Nếu cần, chỉ trình bày thống kê đã xác minh ở lớp chi tiết với phạm vi rõ. | Không ưu tiên |
| Y32 | Panel tín hiệu đầu vào ngày t để thảo luận ca sai | Mistral Large ID-2 | Nếu có đúng snapshot và đầu vào thực sự dùng sau mask/imputation, có thể hiển thị tối đa vài thông tin trong chi tiết, gắn nhãn số quan trắc/nội suy/điền thiếu rõ ràng. Không coi các biến hiển thị là nguyên nhân hay giải thích đầy đủ dự báo; percentile train cần tính và kiểm chứng riêng. | Để sau / cần kiểm chứng |
| Y33 | Bộ chọn thành phố với 8 sparkline | MiMo Y2 | Có thể cung cấp bối cảnh nhưng tám đồ thị nhỏ tốn không gian và khó đọc khi chiếu; số ngày nặng phải xác minh theo thành phố và tập. Không thay bộ chọn gọn cho đến khi thử thực tế. | Không ưu tiên / thử thiết kế nếu cần |

### Nhận xét riêng ba bài

- **DeepSeek:** thước hai làn có thể giải quyết tốt nhầm lẫn ngưỡng vận hành và mốc thực tế, trong khi vẫn thay thế chứ không bổ sung thêm một khối. Phương án khóa phím tiến ngày cho đến khi mở thực tế không phù hợp thao tác linh hoạt; ưu tiên cho phép bỏ qua. Cần lưu ý đoạn giải thích của bài về việc “mô hình chỉ chạy khi có AQI t+1” không nên diễn giải thành yêu cầu vận hành: bộ đánh giá hồi cứu có thể lọc do thiếu nhãn, nhưng nhãn không phải đầu vào dự báo.
- **MiMo:** cách kể ngược từ thực tế đến dự báo có thể hữu ích khi phân tích một ca sai; nhưng khác mục tiêu giấu đáp án, nên chỉ là tùy chọn. “Vùng thường trúng” lấy từ sai số test không phải khoảng dự báo được hiệu chuẩn và dễ gây hiểu nhầm; chưa nên đưa lên màn hình chính.
- **Mistral Large:** panel điều tra có thể giúp thảo luận, nhưng đọc header CSV không đủ chứng minh các con số bách phân vị hay giá trị đúng như mô hình đã sử dụng. Dải ±MAE theo nhãn nặng/thường vừa dễ bị hiểu nhầm, vừa sử dụng phân loại theo thực tế tương lai nếu áp trước khi đối chiếu: không nên dùng như độ bất định dự báo. MAE holdout thấp hơn test không tự chứng minh nguyên nhân là AQI nền thấp.
- Không đồng nhất “test được dùng khám phá ngưỡng” với rò rỉ vào đầu vào mô hình: đó là nguy cơ thiên lệch lựa chọn theo test; nếu trình bày so sánh ngưỡng cố định phải ghi rõ cách chọn và phạm vi đánh giá.
- DeepSeek báo có artifact V21 ở commit bằng chứng; hai bài khác không thấy trên các nhánh đã xem. Đây là các báo cáo khác phạm vi tìm kiếm, không tự chứng minh không tồn tại ở nơi khác; cần tự kiểm tra và chốt nguồn demo.

## Bổ sung từ MiniMax, Inkling và Haiku

| Mã | Ý tưởng | Nguồn | Đánh giá / điều kiện | Trạng thái |
|---|---|---|---|---|
| Y34 | Đồ họa đơn vị cho các ca cảnh báo trên tập test | Inkling Y1 | Có thể trình bày trực quan số bắt đúng/bỏ sót và báo nhầm trong lớp chi tiết. 389 là **cặp thành phố–ngày nặng**, không phải 389 ngày lịch; báo nhầm thuộc các cặp không nặng nên cần nhóm và mẫu số riêng. Không buộc vẽ 389 chấm nếu khó đọc; nhảy tới từng ca chỉ khi có dữ liệu từng ngày đã QA. | Cân nhắc ở lớp chi tiết / cần kiểm chứng |
| Y35 | Checklist trước buổi trình chiếu | Inkling Y4 | Kiểm tra offline, tải dữ liệu, thao tác, thiết bị chiếu và ca dự phòng trước buổi. Nên là checklist ngắn/file riêng thay vì dựng một chế độ ứng dụng mới. Một ô tick không tự chứng minh đạt tương phản hoặc tiếp cận; cần kiểm thử thực tế. | Nên thử, chờ duyệt |
| Y36 | Hiển thị sai lệch dự báo − thực tế của một ca | MiniMax I2 | Một nhãn chênh lệch có dấu có thể giúp nói dự báo cao/thấp bao nhiêu; chỉ hiện khi đã mở kết quả và có đủ số liệu. Không nhầm sai lệch một ca với MAE hay thiên lệch trung bình toàn tập, không cần thêm kim nếu đã có Y03/Y27. | Cân nhắc / thử cùng Y03 |
| Y37 | Câu chuyện tuần tự ba ca + chọn ngày tự do | Haiku ID-03 | Có thể viết như kịch bản thuyết trình thay vì thêm màn hình: báo đúng → bỏ sót → báo nhầm, sau đó khán giả tùy chọn ngày. Chọn ca từ artifact có nguồn và kiểm tra theo ngưỡng; nói rõ không đại diện toàn tập. Không gọi hiệu ứng “khóa dự báo” là bằng chứng chống rò rỉ đầu-cuối. | Nên thử, cần kiểm chứng |
| Y38 | Chế độ bình chọn khán giả trước khi mở kết quả | Haiku ID-02 | Thêm tương tác nhưng dễ tốn thời gian và biến demo thành trò chơi; nếu người trình bày muốn có thể hỏi miệng một lần, không cần xây chức năng thu bình chọn. | Không ưu tiên |
| Y39 | Dải kết quả theo tháng và so sánh baseline | MiniMax I4; Inkling Y2 | Có thể trình bày khác biệt theo tháng hoặc đường sai số cộng dồn trong chi tiết, nhưng cần artifact và cách tính theo thành phố–ngày đã đối chiếu. MAE theo tháng là hồi quy, không phải kiểm định cảnh báo; CI chứa 0 không chứng minh không có lợi ích. Không suy kết quả L3−baseline thành đóng góp riêng của thời tiết L3−L2. | Để sau / cần kiểm chứng |
| Y40 | So sánh hai thử nghiệm mask nội suy trong phần hạn chế | Inkling Y3 | Có thể trình bày như kết quả kiểm tra độ nhạy tĩnh, ghi tên cấu hình, nguồn và phạm vi; không gọi là công tắc “bật/tắt rò rỉ”, không đánh đồng với phép kiểm chứng F01 từ raw hay tuyên bố xử lý xong. | Để sau / cần duyệt câu chữ và nguồn |

### Nhận xét riêng ba bài

- **MiniMax:** ý hiển thị mức lệch của một ca có ích nếu đủ gọn, nhưng không được nói các mô hình “co mọi ngày nặng về trung bình” hay coi chênh lệch trung bình là nguyên nhân của từng lần bỏ sót. Đề xuất dải tháng so L3 với baseline không đủ chứng minh “thời tiết chỉ giúp mùa đông”; so sánh phần riêng thời tiết cần L3−L2 và phân tích phù hợp. Bài ghi `as_of` cắt raw, trong khi báo cáo F01 nói phép thử cắt **bảng đã sạch**.
- **Inkling:** checklist trước trình chiếu là bổ sung thực dụng, không cần thêm nhiều chữ cho khán giả. Đồ họa 389 chấm có thể sinh động nhưng khá dày; nếu dùng phải phân biệt mẫu ngày nặng với mẫu báo nhầm. Công tắc “leakage” dễ gây hiểu lầm vì hai thí nghiệm khác nhau; ưu tiên lời giải thích ngắn ở lớp chi tiết.
- **Haiku:** kịch bản ba ca và nút chọn tự do phù hợp, nhưng không nên gắn nhãn “đủ để xem cảnh báo” cho từng thành phố chỉ dựa vào ngưỡng 30 vốn là quy ước theo nhóm. Phần “khóa dự báo” chỉ là cách trình diễn, không chứng minh no-leakage end-to-end. Ý tính đóng góp Ridge cần chính xác trên thang log(AQI), xử lý intercept, chuẩn hóa và missing; không được nói các đóng góp trực tiếp cộng thành điểm AQI gốc.
- **Nguồn dự báo:** MiniMax báo có V21 tại commit bằng chứng; Inkling và Haiku không tìm thấy trên các nhánh họ xem. Đây không phải bằng chứng rằng file không tồn tại ở nơi khác; tiếp tục cần chốt provenance và QA trước khi dùng.
- **Kiểm tra bổ sung trong checkout:** đọc cột AQI của `air_quality_8cities_weather.csv` trong khoảng 30/06/2019–29/02/2020 thấy ba ngày AQI trống tại Amritsar (26/08/2019, 02/02/2020, 03/02/2020); không thấy ngày trống thành phố khác trong khoảng đó. Đây là kiểm tra dữ liệu, chưa xác nhận đủ mọi điều kiện hay số dòng của bảng dự báo.

## Quyết định của người dùng: chế độ holdout đối chiếu

**Đã chọn ý tưởng:** bổ sung chế độ “Giai đoạn giữ lại cuối (holdout)” để đối chiếu, **không thay thế dữ liệu test**. Đây là quyết định về định hướng demo, chưa phải yêu cầu triển khai ngay.

- Giữ test và holdout là hai chế độ/giai đoạn có nhãn rõ trên cùng trải nghiệm timeline; phát lại từng ngày khi dữ liệu đã được kiểm chứng, không trộn kết quả của hai giai đoạn.
- Nội dung thuyết trình cân bằng: test cho thấy Ridge L3 cải thiện MAE so với baseline; với holdout, chênh lệch MAE quan sát được nhỏ hơn và khoảng tin cậy chứa 0, **chưa đủ bằng chứng về lợi thế**. Không kết luận hai mô hình tương đương hay model chắc chắn không có lợi thế. Nêu rõ cỡ mẫu và phạm vi từng giai đoạn ở lớp chi tiết.
- Artifact ứng viên: [R2_B04_baseline_predictions.csv tại commit DA 13e93ae](https://github.com/HTung0511/Air_Project_Test/blob/13e93ae12c483f01a573ee51ef9562a315e45068/Air-Project-main/reports/ra/round2/evidence/R2_B04_baseline_predictions.csv). Đã kiểm số dòng và MAE tổng hợp; trước khi sử dụng cần QA provenance, split/ngày, cấu hình và sự tương thích với nguồn test, đối chiếu phương pháp và phiên bản khoảng tin cậy holdout (script: [−2,80; +0,50], báo cáo RA: [−2,70; +0,48]). Không gọi toàn bộ holdout là phong tỏa hoặc coi F01 đã đóng.
- Không biến chế độ này thành công cụ chọn mô hình theo holdout; đây là đối chiếu hồi cứu, thực tế t+1 chỉ hiện để so sánh sau dự báo.

## Bổ sung từ Argon High và Sonnet

| Mã | Ý tưởng | Nguồn | Đánh giá / điều kiện | Trạng thái |
|---|---|---|---|---|
| Y41 | Nhãn theo chuyển biến AQI hôm nay → ngày mai | Sonnet Ý-3 | “Bắt đầu nặng”, “tiếp tục nặng”, “hết nặng”, “tiếp tục không nặng” giúp giải thích quán tính baseline. Phân loại dùng thực tế t+1 nên chỉ hiện sau khi mở đối chiếu; thống kê 12/12 và nhóm chuyển biến là phân tích hậu nghiệm của AI, chưa tự đối soát, không khái quát. | Cân nhắc ở chi tiết / cần kiểm chứng |
| Y42 | Đối soát dữ liệu demo với kết quả notebook | Sonnet Ý-5 | Một script kiểm số dòng, phạm vi, MAE và TP/FP/FN, kèm nguồn commit, cấu hình và sai số làm tròn; chỉ phát dấu “đã đối soát” sau khi kiểm thực sự thành công. Khớp số không chứng minh không rò rỉ hay chứng nhận vận hành. | Nên thử khi triển khai |
| Y43 | Ngữ cảnh đầu vào so với cùng thành phố/tháng | Argon IDEA-04 | Có thể bổ sung kiến thức thời tiết, nhưng thống kê City×Month phải có nguồn và cửa sổ tham chiếu rõ; nếu muốn mô phỏng thông tin tại t, chỉ dùng tham chiếu được xác định không nhìn tương lai. Phân biệt trung vị với phân vị/tertile và OLS diễn giải với Ridge dự báo; không xem như nguyên nhân của ca. | Để sau / cần kiểm chứng |
| Y44 | Dải lịch sử đến t với phần t+1 mở khi đối chiếu | Sonnet Ý-2 | Một phương án cụ thể của Y04/Y05: dải AQI ngắn có khoảng trống thật và vùng thực tế mở tùy chọn. Ghi đây chỉ là một phần đầu vào L3, không chứng minh pipeline không rò rỉ. Cần thử xem có chiếm quá nhiều diện tích. | Cân nhắc / thử thiết kế |

### Kiểm tra mới: dữ liệu dự báo holdout từng ngày

Argon báo có file `Air-Project-main/reports/ra/round2/evidence/R2_B04_baseline_predictions.csv` ở commit DA `13e93ae12c483f01a573ee51ef9562a315e45068`. **Mình đã trực tiếp đọc file này qua GitHub API theo đúng commit, không chuyển nhánh**: có 2.922 dòng, gồm 1.947 test và 975 holdout; cột có ngày t, ngày đích, AQI, thực tế và dự báo L1–L4/baseline. Tính từ file: test MAE L3 19,5190, baseline 23,4664; holdout L3 13,7834, baseline 14,8031; số cặp nặng lần lượt 389 và 18.

Kết quả này **cập nhật điểm chưa rõ ở các lượt trước**: đã tìm thấy một artifact có dự báo holdout từng ngày ở commit bằng chứng, không phải trên checkout hiện tại. Chưa xác minh toàn bộ provenance, đối chiếu từng dòng, tương thích phiên bản demo hay phê duyệt làm nguồn chính thức; cần chốt phiên bản pipeline và tình trạng F01 trước khi dùng. Không cần và chưa sao chép file sang nhánh làm việc.

### Nhận xét riêng hai bài

- **Argon High:** hữu ích ở việc chỉ ra artifact holdout để kiểm tra; hai chế độ ngưỡng và so sánh L1–L3 đã có ở Y24/Y25. Tuy nhiên L1, L2 và L3 là các mô hình Ridge được fit riêng với tập đặc trưng khác nhau, không phải một mô hình cập nhật liên tiếp trên cùng tham số; chênh dự báo không chứng minh vai trò nhân quả hoặc cú sốc phát thải của ca. Khoảng chuẩn City×Month tính trên toàn bộ thời gian có thể dùng như mô tả hồi cứu nếu ghi rõ, nhưng không được giả làm ngữ cảnh biết trước tại t.
- **Sonnet:** đề xuất đối soát dữ liệu và hiển thị chính xác gần ngưỡng rất đáng giữ. Ví dụ từ R2 tại Amritsar t=03/01/2020: dự báo **165,973826**, thực tế 221; với ngưỡng 166 không phát cảnh báo. Nếu chỉ hiện “166” sẽ dễ gây nhầm, nên hiển thị đủ số thập phân gần ngưỡng, tính quyết định trên giá trị gốc. Kết quả này là ví dụ đã kiểm trong R2, không thay thế đối soát toàn bộ file.
- Không gọi dải [166,201) là “ngày chưa nặng”: đó là khoảng của **dự báo**, trong khi ngày nặng được xác định theo **thực tế t+1**. Các điểm chuyển biến và số báo nhầm gần ngưỡng do Sonnet tự khám phá trên V21 cần nhóm tái lập; không mặc định là kết luận chính thức.
- Quy ước mẫu nhỏ theo nhóm không cấm hiển thị kết quả của một ca cá lẻ: có thể cho xem kết quả thật nếu có và gắn giới hạn đánh giá tổng thể, không quy hồi hiệu năng cả thành phố từ ca đó.

## Phân loại tổng hợp cho bản demo đầy đủ

Theo yêu cầu người dùng, không giới hạn bản demo vào một bản tối giản: giữ ý tưởng tốt ở nhóm ưu tiên; các ý còn lại để tham khảo. Danh sách dưới đây là **đánh giá ưu tiên của trợ lý**, không xóa các điều kiện và caveat trong từng mục Y ở trên. “Ưu tiên” không có nghĩa được phép đưa dữ liệu chưa xác minh vào như sự thật.

### Ưu tiên — trải nghiệm và nội dung chính

- **Y01, Y02, Y03, Y04, Y13, Y27:** timeline t→t+1, ca tiêu biểu và chọn tự do, so sánh dự báo/thực tế/baseline, mở thực tế tùy chọn và trạng thái kết quả. Y27 là một phương án thể hiện Y03, không bắt buộc thêm biểu đồ trùng.
- **Y06, Y14, Y22, Y23:** lớp chi tiết giữ ngữ cảnh, bảng test/holdout và giới hạn, ma trận giải thích bốn kết quả. Y22 gộp với Y06.
- **Y05, Y44:** dải lịch sử ngắn và vùng t+1 mở sau; có thể đặt ở lớp phù hợp, xử lý ngày thiếu thật.
- **Y08, Y19:** sơ đồ pipeline ngắn và so sánh MAE theo các nhóm mô hình, nhằm thể hiện thành quả nghiên cứu; số liệu phải được đối soát.
- **Y18, Y26, Y29:** giới hạn cỡ mẫu và trạng thái thiếu dữ liệu trung thực, không suy đoán lý do.
- **Y07, Y35, Y37:** kịch bản ba ca, lời dẫn ngắn và checklist trình chiếu dưới dạng tài liệu hỗ trợ, không nhồi vào giao diện.
- **Y12, Y42:** tiếp cận, bàn phím, mục tiêu offline và đối soát dữ liệu là chất lượng nền; chỉ khẳng định đạt sau khi kiểm thử.
- **Chế độ holdout:** người dùng đã chọn thêm để đối chiếu, giữ nguyên test. Điều kiện QA và cách diễn giải nêu ở mục quyết định holdout.
- **Y45 — Mini map AQI:** trên nền bản đồ Ấn Độ hiển thị đúng 8 chấm tròn đại diện 8 thành phố. Bấm chấm để chọn thành phố; chấm được chọn nổi bật bằng màu và thêm viền hoặc kích thước để không phụ thuộc riêng vào màu. Đồng bộ hai chiều với bộ chọn thành phố, timeline và giai đoạn; nếu tổ hợp thành phố/ngày thiếu dữ liệu, giữ lựa chọn và báo thiếu, không tự đổi ngày. Tách dấu hiệu chọn khỏi thang màu AQI; chú giải rõ loại giá trị và ngày, không tiết lộ thực tế t+1 khi đang ẩn. Kiểm chứng tọa độ, thang màu và nguồn; không suy rộng thành vùng ô nhiễm liên tục. Ưu tiên nhẹ, có lựa chọn thay thế, hỗ trợ bàn phím và offline sau kiểm thử.

### Tham khảo — có thể chọn thêm nếu phù hợp

- **Y09, Y17, Y20, Y33:** các phương án chi tiết cho bộ chọn thành phố, bản đồ và trợ giúp; mini map Y45 đã được người dùng chọn, còn hình thức thể hiện cụ thể vẫn có thể tham khảo các ý này.
- **Y10, Y21, Y24, Y25, Y32, Y34, Y36, Y39, Y40, Y41, Y43:** bổ sung phân tích sai số, ca hụt đỉnh, so sánh mô hình/ngưỡng, tín hiệu đầu vào, đồ họa cảnh báo, chênh lệch từng ca, phân tích theo tháng, độ nhạy và chuyển biến; chỉ đưa vào khi có dữ liệu và phương pháp kiểm chứng, tuân thủ caveat từng mục.
- **Y15, Y16, Y28, Y38:** cách kể chuyện và tương tác thay thế; thử nếu tăng giá trị mà không tiết lộ kết quả hay làm rối luồng chính.
- **Y11, Y30, Y31:** giải thích đóng góp đặc trưng và dải bất định/sai số chỉ mang tính nghiên cứu; không triển khai dưới dạng kết luận hay khoảng dự báo nếu chưa có phương pháp, dữ liệu và kiểm định phù hợp.

Bản đầy đủ vẫn cần phân cấp thông tin và nhẹ khi trình chiếu: ưu tiên không đồng nghĩa tất cả đều nằm trên màn hình chính, còn tham khảo không phải tự động đưa vào.

## Các điểm cần kiểm chứng trước khi triển khai

1. **Nguồn dự báo từng ngày:** Mistral cho biết notebook không export CSV trong bản xem; Qwen cho biết có `reports/ra/evidence/V21_model_test_predictions.csv` ở commit `0dfc71568d43`, không có trên main. Hai nhận xét có thể cùng đúng vì khác phiên bản. Checkout hiện tại không có thư mục evidence. Cần xác minh artifact, nguồn và quyền sử dụng; không khẳng định đã kiểm chứng file đó.
2. **Holdout từng ngày:** đã tìm thấy và đọc R2_B04 tại commit DA `13e93ae` (xem mục Argon/Sonnet); kiểm được số dòng và MAE tổng hợp. Cần QA provenance và chốt phiên bản trước khi phát lại; không mặc định có trên main hay coi F01 đã đóng.
3. **Nhãn chất lượng AQI:** dự án nêu không nội suy AQI. Dù CSV có cột `AQI_was_missing` và `suspect_sensor_error`, không suy luận ý nghĩa từng ngày hoặc nói AQI được nội suy mà chưa kiểm tra logic tạo cờ.
4. **Không làm tròn trước khi quyết định cảnh báo:** giữ giá trị dự báo gốc cho phép so sánh với ngưỡng và xác định TP/FP/FN; chỉ làm tròn để hiển thị, đồng thời tránh trường hợp số hiển thị làm người xem hiểu nhầm quyết định ngưỡng.
5. **Phạm vi các mốc và dữ liệu:** 1.947 là số cặp thành phố–ngày, không phải số ngày lịch. Ghi ranh giới theo ngày đích; tránh gọi toàn bộ giai đoạn từ 01/03/2020 là giai đoạn phong tỏa toàn quốc.
6. **Giới hạn thang AQI:** nếu dùng trục 0–500, kiểm tra giá trị lớn hơn 500 và thể hiện không cắt cụt gây hiểu nhầm.
7. **Hiệu năng và thiết bị:** các mục tiêu tốc độ, kích thước, một file HTML là đề xuất kỹ thuật, không phải kết quả kiểm thử. Cần đo và thử offline trên thiết bị thực tế.

## Không nên thêm ngay

- Bản đồ chi tiết nặng, bảng nhiều cột hoặc nhiều chỉ số cùng lúc nếu không hỗ trợ ca đang xem. Mini map Y45 đã được người dùng chọn, cần giữ gọn và đúng phạm vi dữ liệu.
- Nút kéo ngưỡng tùy ý ngay trên màn hình chính nếu chưa giải thích được cách so sánh và nguy cơ chọn kết quả theo test.
- Nhiều hiệu ứng, animation liên tục hoặc ghi chú dài trên giao diện.
- Dữ liệu demo giả được trình bày như dự báo dự án; tuyên bố nhân quả hoặc vận hành thời gian thực.

## Nguồn rà soát

- Mười sáu tài liệu đính kèm: `mistral4.txt`, `qwen3.8.txt`, `muse-spark-1.3.txt`, `seed-2.1.txt`, `gemini-4-argon.txt`, `qwen3.8-max.txt`, `gemini4-carbon.txt`, `ernie-5.5.txt`, `deepseek-v4.1.txt`, `mimo-v2.6.txt`, `mistral-large4.txt`, `minimax-m3-1.txt`, `inkling-2.txt`, `haiku-5.5.txt`, `argon-high.txt`, `sonnet-5.5.txt` (các khẳng định về việc họ đọc nguồn là do chính tác giả tài liệu báo cáo).
- `Air-Project-main/reports/ra/final_review_report.md` — hạn chế F01, kết quả test/holdout.
- `Air-Project-main/src/model_utils.py` — đặc trưng và chia dữ liệu.
- `Air-Project-main/data/processed/air_quality_8cities_weather.csv` — đã kiểm tra tên cột, chưa xác minh ý nghĩa từng giá trị cờ.

## Nhật ký quyết định

| Ngày | Quyết định | Người quyết định | Ghi chú |
|---|---|---|---|
| 13/11/2026 | Đã rà soát hai tài liệu đầu; chưa có lựa chọn tính năng cụ thể | Trợ lý | Chờ người dùng xác nhận ý tưởng muốn phê duyệt. |
| 13/11/2026 | Rà soát thêm Muse Spark và Seed, bổ sung Y13–Y17 | Trợ lý | Các ý tưởng vẫn là khuyến nghị, chưa duyệt triển khai. |
| 13/11/2026 | Rà soát thêm Gemini Argon và Qwen Max, bổ sung Y18–Y22 | Trợ lý | Đề xuất chưa được người dùng duyệt triển khai. |
| 13/11/2026 | Rà soát thêm Gemini Carbon và Ernie, bổ sung Y23–Y26 | Trợ lý | Đề xuất chưa được người dùng duyệt triển khai. |
| 13/11/2026 | Rà soát thêm DeepSeek, MiMo và Mistral Large, bổ sung Y27–Y33 | Trợ lý | Đề xuất chưa được người dùng duyệt triển khai. |
| 13/11/2026 | Rà soát MiniMax, Inkling và Haiku, bổ sung Y34–Y40 | Trợ lý | Chưa duyệt triển khai; đã kiểm tra riêng ba ngày thiếu AQI trong dữ liệu checkout. |
| 13/11/2026 | Rà soát Argon High và Sonnet, bổ sung Y41–Y44; kiểm tra artifact R2_B04 | Trợ lý | Đã xác nhận 1.947 dòng test và 975 dòng holdout tại commit DA; chưa phê duyệt nguồn để triển khai. |
| 13/11/2026 | Chọn bổ sung chế độ holdout đối chiếu, giữ nguyên test | Người dùng | Quyết định ý tưởng; cần QA nguồn và kết quả trước khi triển khai. |
| 13/11/2026 | Yêu cầu bản đầy đủ, phân ý tốt vào ưu tiên và phần còn lại vào tham khảo | Người dùng | Đã phân loại Y01–Y44; giữ điều kiện kiểm chứng và hai lớp thông tin. |
| 13/11/2026 | Bổ sung mini map khu vực ô nhiễm vào demo | Người dùng | Ưu tiên Y45; thể hiện theo dữ liệu thành phố và ngày được kiểm chứng, không suy rộng thành bản đồ ô nhiễm liên tục. |
| 13/11/2026 | Chốt mini map Ấn Độ với 8 chấm tròn có thể chọn, làm nổi bật thành phố và đồng bộ timeline | Người dùng | Bổ sung chi tiết tương tác cho Y45; cần kiểm chứng dữ liệu và tọa độ. |
