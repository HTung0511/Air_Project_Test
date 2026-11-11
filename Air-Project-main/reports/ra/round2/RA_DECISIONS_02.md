# RA-DEC-02 — Chấp nhận ACK Dev; duyệt DEV-Q1–Q3 để triển khai

Ngày: 11/11/2026 · Vai trò: AI-2 RA.
Đọc cùng [RA-DEC-01](RA_DECISIONS_01.md) và [gói giao việc](../AI_REMEDIATION_HANDOFF.md).

## 1. Trạng thái và quyền triển khai

RA chấp nhận ACK Dev do người dùng chuyển lại. Theo ACK, Dev đang ở nhánh phiên `arena/5cb21c04-air-project-test`, HEAD `cd719cf7f8aa43529df953e860f9cc5f45d963ee`, chưa sửa/commit bản sửa và chưa chạy notebook. **Đây chưa phải HANDOFF mã đã hoàn thành.** Các số Dev tự đếm là thông tin sơ bộ, cần log và DA xác minh; không đưa vào báo cáo như kết quả vòng2 đã nghiệm thu.

**Dev được bắt đầu DEV-01 ngay và triển khai DEV-02 theo ba quyết định dưới đây**, không cần chờ thêm lệnh “tiếp tục”. Việc duyệt thiết kế không đồng nghĩa F01/F02 đã đóng. Yêu cầu Python3.11.2 ở RA-DEC-01 tiếp tục áp dụng.

## 2. DEV-Q1 — Dùng AQI raw làm nhãn và tiêu chí giữ mẫu

**Phê duyệt đề xuất**, với contract:

- Một mẫu tại ngày `t` dự đoán `y=AQI_raw(t+1)` theo ngày lịch kế tiếp, không shift nhầm qua ngày bị đứt. Chuỗi phải được kiểm tra khóa City/Date và tính liên tục.
- Giữ mẫu khi AQI raw ở cả `t` và `t+1` có quan sát hợp lệ; Date đầu vào ≥14/06/2017 và Date_target≤01/07/2020, theo phạm vi hiện tại. Chia tập theo **Date_target**, không Date của feature.
- Kiểm giá trị số hữu hạn, AQI>0 để tương thích log; nếu có không hợp lệ phải báo count/ngày/quy tắc, không lặng lẽ drop hoặc thay số. **Không tự cắt AQI ở500** hoặc loại mọi AQI>500: có giá trị như vậy trong bộ dữ liệu hiện hành. Nếu phát hiện vi phạm mới thì gửi RA.
- Không nội suy nhãn, không xóa nhãn theo suspect-rule hồi cứu toàn chuỗi, không xóa AQI chỉ vì PM2.5 nghi lỗi. Đây là đánh giá **AQI được ghi trong raw của snapshot hiện có**, không chứng minh raw là ground truth trạm hay mô phỏng revision thực tế của CPCB.
- Dùng cùng chính sách raw cho AQI(t) và lịch sử AQI tạo feature, chỉ đọc các ngày≤t. Nhãn tương lai chỉ đi vào đường tạo target/evaluation, không đi vào feature, fit preprocessing hoặc chọn mẫu feature-as-of. Việc chỉ đánh giá những ngày có y được báo rõ là giới hạn coverage.

Dev dự kiến 8668 mẫu: train5746/test1947/holdout975, tăng5 mẫu train. **RA chưa xác nhận số này.** Dev lưu bảng khóa mẫu thêm/bớt, AQI gốc, nguyên nhân; DA kiểm độc lập counts và values.

### So sánh bắt buộc để tách tác động

1. Kết quả đường dự báo mới trên cohort raw mới theo protocol này.
2. Đối chiếu mã cũ và mới trên cùng cohort baseline, cùng nhãn khi chúng khớp, với cùng cách CV chọn alpha/ngưỡng và cùng giao thức metric. Nếu có nhãn khác, báo riêng, không gọi là paired cùng outcome.
3. Biến thể nhánh mới bỏ các mẫu train thêm theo diff thực tế (không hard-code “5” trước kiểm chứng) để lượng hóa ảnh hưởng mở rộng cohort train. Đánh giá trên cùng khóa test/holdout, báo n và nhãn; nếu khóa không giống dự kiến thì giải thích.
4. Không tune lại bằng test để khôi phục metric cũ. Alpha mới có thể đổi nếu vẫn chọn bằng CV train đúng protocol; phải báo trước/sau.

**Nhãn/mẫu được RA duyệt ở mức thiết kế. DA-03 không còn chờ lựa chọn chính sách của RA; vẫn phải chờ implementation/SHA Dev để kiểm đúng chính sách.**

## 3. DEV-Q2 — Không dùng suspect-rule hồi cứu trong nhánh dự báo

**Phê duyệt đề xuất:** không dùng top-5 toàn chuỗi hoặc cửa sổ centered15 ngày để xóa/thay đầu vào dự báo. Không cần thiết kế một luật trailing mới trong vòng sửa này.

- Giữ các quan sát pollutant/AQI hợp lệ từ raw; tách xử lý flatline đã duyệt ở Q3. Giữ kiểm tra vật lý/schema xác định trước, ghi rõ mọi masking thực tế.
- Cờ nghi lỗi hồi cứu không làm feature và không lọc mẫu chính. Nếu dùng cho sensitivity thì chỉ gắn nhãn kết quả phân tích, không dùng để tune hay gọi là causal filtering.
- Đường EDA/suspect-rule lịch sử giữ nguyên về hành vi trên full dataset. No-gas/empty guard cho NEW-002 được phép sửa để hàm không lỗi ở đầu chuỗi; thêm test xác nhận full-dataset output không đổi ngoài phần đã khai báo.
- Count “6 ô PM2.5, 4 ô AQI trong khoảng chung” là dự kiến Dev cung cấp, cần diff artifact và DA xác minh.

Chấp nhận việc giữ điểm nghi lỗi chưa được xác minh là một quyết định minh bạch, không khẳng định tất cả điểm được giữ là đúng. Báo độ nhạy thay vì xóa hậu nghiệm để làm test đẹp.

## 4. DEV-Q3 — Flatline có điều kiện tại từng thời điểm as-of

**Phê duyệt chính sách snapshot as-of t**, làm rõ hai lớp:

1. Tại ngày đầu/nhì của một run0, nếu chưa đủ3 quan sát0 liên tiếp đến thời điểm đó, số0 giữ nguyên. Một run không được nối qua ngày mất quan sát hoặc ngày lịch bị thiếu.
2. Khi đã quan sát đủ≥3 ngày0 liên tiếp ở thời điểm t, được mask cả run0 **đã quan sát trong prefix≤t** khi dựng feature của chính thời điểm t. Các zero đã mask không được làm nguồn forward-fill. Không mask bằng cách nhìn ngày>t.
3. **Không sửa ngược bản ghi feature đã phát hành tại t−1/t−2.** Dataset huấn luyện/evaluation phải có mỗi hàng feature(t) đúng snapshot prefix≤t của hàng đó, không lấy snapshot cuối cùng rồi cập nhật lại tất cả hàng lịch sử. Lịch sử quan sát dùng để dựng một hàng hiện tại có thể được đánh giá lại trong prefix hiện tại; đây khác với sửa các hàng dự báo quá khứ.
4. Không nội suy hai đầu hoặc backward-fill. Forward-fill tối đa2 ngày trên cột pollutant sau masking, trong đúng thành phố/ngày liên tục, trước log1p; không kéo qua ranh TP. Phần còn thiếu dùng imputer chỉ fit train. AQI dùng quy tắc feature/lag đã chốt, không tự forward-fill nhãn để giữ mẫu.
5. Chỉ áp flatline lên nhóm cột đã có trong thiết kế được giữ lại; không tự mở rộng sang biến đích AQI hoặc weather. Nêu rõ danh sách cột trong code/log.

### Test bắt buộc

- Run0 dài1/2/3/4 ngày, đầu chuỗi, giữa chuỗi, gap/NaN, chuyển TP, ranh train/test.
- Hàng ngày1/2 không đổi khi thêm ngày3/4 vào raw; hàng ngày3 có masking hợp lệ trong prefix của chính nó. So cả giá trị và missing mask/nguồn forward-fill.
- Với cùng cutoff t, cắt/perturb mọi dữ liệu>t không làm đổi feature(t) ở đường dự báo mới. So tất cả feature L1–L3, không chỉ CO hoặc feature có thay đổi ở vòng1.
- Kiểm y và eligibility riêng: thêm AQI(t+1) có thể làm hàng đủ điều kiện đánh giá nhưng không được thay giá trị feature(t). Không đòi y(t) hoặc số hàng đã có nhãn “bất biến trước tương lai” vì target chưa thể quan sát tại t.

Con số “khoảng50 ô CO” chưa được duyệt như kết quả; phải đo lại sau khi có implementation theo contract này.

## 5. F02 — Đồng ý hướng sửa, bổ sung điều kiện chống lỗi nối pipeline

RA chấp nhận hướng cache-first, BLH bắt buộc, Python3.11.2, output mới ở scratch và cache tải mới không ghi đè file gốc.

- Nếu NB04 mặc định xuất scratch, phải có cấu hình đường dẫn rõ cho NB05/NB06 hoặc lệnh chạy tích hợp trong bản sao. Không để NB04 ghi nơi mới rồi downstream âm thầm đọc CSV baseline cũ và báo đã kiểm toàn chuỗi. DA ghi đường dẫn/hash thực sự đọc ở mỗi bước.
- Cache không hợp lệ offline: dừng rõ ràng; không ghi output hoàn chỉnh giả hoặc dùng partial/stale fallback không công bố. Online mock được đánh riêng với API thật blocked.
- **Duyệt tolerance đề xuất có điều kiện:** mean temp/pressure/wind được lệch≤0,01 cộng epsilon số học nhỏ được khai báo, chỉ khi chứng minh mean chưa làm tròn nằm sát biênx,xx5. Các cột khác numeric dùng1e-9; key/schema/NaN/nhãn/rain_day/wind_dir_8 phải so chính xác theo semantics. Không áp±0,01 cho mọi cột hay confusion counts.
- Tolerance không phải miễn kiểm: báo n ô lệch, maxdiff, vị trí/cột và downstream metrics. Không bắt buộc n lệch đúng852 ở environment mới; mọi sai lệch ngoài điều kiện trên phải giải thích/gửi RA, không tự nới tolerance.
- Assert NB06: giữ invariant và bảng split/retention, thay count cũ một cách có căn cứ. Không thay bằng assert luôn đúng, xóa assert chống leakage, hay hard-code count mới chỉ để qua test. Giá trị thực nghiệm mong đợi phải gắn snapshot/protocol; DA kiểm độc lập.

## 6. Nhánh, PR và đầu ra của Dev

- Đồng ý mở PR Dev nhắm `main`, trên đúng nhánh phiên Dev hiện tại. Không yêu cầu đổi base sang RA hoặc chuyển nhánh. Ghi rõ diff có commit tài liệu kế thừa, tách phần Dev trong mô tả.
- Không merge/đóng PR khác, không coi `git push --dry-run` là bằng chứng PR đã mở.
- NEW-001 và F03–F05 không giao thêm cho Dev; BA/RA xử lý nội dung. Dev chỉ báo các điểm tài liệu cần đồng bộ do API/code mình đổi.
- Đầu ra: `dev_change_log.md` anchorD01…, protocol nhãn/feature tham chiếu quyết định này, test/log, file lock environment, count/diff trước-sau, các path output/scratch và SHA/PR thật.
- Trước regression cuối, đọc hết các cell NB06 đang sửa và những đoạn downstream NB03/NB05 bị ảnh hưởng bởi cấu hình đường dẫn/API. Không cần đọc lại toàn bộ archive để bắt đầu DEV-01.
- Bàn giao “sẵn sàng DA kiểm” sau test; không tự ghi “RA nghiệm thu đạt”. Chưa chạy gì thì báo đúng chưa chạy, không gọi các phép đếm sơ bộ là benchmark vòng2.

## 7. Tin nhắn chuyển DA — bổ sung RA-DEC-01

**DA được bắt đầu chuẩn bị ngay theo RA-DEC-01.** Người dùng chưa chuyển phản hồi trước đó không làm thay đổi quyền bắt đầu đã cấp. Đọc RA-DEC-02 này và đưa Q1–Q3/tolerance vào protocol trước khi xem metric mới.

- Chính sách nhãn/mẫu đã được RA duyệt: AQI raw, eligibility như mục2; suspect-rule không đi vào nhánh dự báo; flatline snapshot as-of như mục4.
- DA-03 chuyển từ “chờ RA chọn chính sách” sang **“đã có protocol thiết kế, chờ code/SHA Dev để kiểm”**. Kiểm cả feature causality và sample/target semantics, không chỉ test snapshot.
- Không dựa vào các count Dev đếm để tự đánh pass; dựng lại độc lập, xuất cohort diff và kiểm5 mẫu dự kiến bằng khóa thật.
- Báo nhãn raw như quan sát trong snapshot, không gọi ground truth không lỗi hoặc dữ liệu thời gian thực có chứng nhận phát hành.
- Không thay hồ sơ vòng1; tất cả trạng thái F01/F02 vẫn chờ kết quả vòng2 và quyết định nghiệm thu RA.

## 8. Trạng thái sau quyết định

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| ACK Dev | Chấp nhận | ACK được người dùng chuyển | Chưa có commit sửa mã. |
| DEV-Q1 | Duyệt thiết kế | Mục2 | Nhãn/cohort cần DA kiểm sau implementation. |
| DEV-Q2 | Duyệt thiết kế | Mục3 | Không dùng suspect hồi cứu cho forecast. |
| DEV-Q3 | Duyệt thiết kế | Mục4 | Feature snapshot bất biến theo ngày phát hành. |
| DEV-01/DEV-02 | Cho phép triển khai | Mục1–6 | Dev gửi HANDOFF với SHA/test/log. |
| DA chuẩn bị | Cho phép bắt đầu | RA-DEC-01 và mục7 | Không cần chờ thêm tin nhắn bắt đầu. |
| F01/F02 nghiệm thu | Chưa đóng | Chưa có hồ sơ thực nghiệm vòng2 | Không biến duyệt protocol thành kết quả đã kiểm. |
