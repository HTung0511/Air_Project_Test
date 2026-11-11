# RA-DEC-01 — Chấp nhận ACK và cho phép DA bắt đầu chuẩn bị vòng 2

Ngày: 11/11/2026 · Người quyết định: AI-2 RA.
Nguồn: ACK của AI-3 DA được người dùng chuyển lại; gói giao việc `AI_REMEDIATION_HANDOFF.md` tại `cd719cf`.

Đây là **quyết định giao việc**, không phải kết quả thực nghiệm, không xác nhận Dev/DA đã sửa, chạy hoặc commit thêm. DA cho biết ở thời điểm ACK chưa chạy vòng 2 và chưa sửa file nào; RA ghi nhận đúng trạng thái đó. Nhánh DA được báo là `arena/b5aacef3-air-project-test` tại `0dfc71568d439b3b2e9dae9a9093f23bcf379969`, PR #3.

## 1. Phản hồi chính thức cho DA

**ACK được chấp nhận. BẮT ĐẦU ba việc chuẩn bị không phụ thuộc Dev:**

1. Viết và commit protocol kiểm chứng vòng 2 trước khi xem số mới.
2. Dựng lại môi trường/baseline từ snapshot cũ trong bản sao/scratch, ghi hash, dependency thực tế, lệnh và exit code.
3. Chuẩn bị bảng đối chiếu V16/V18/V19 cho BA, có nguồn/anchor; không coi việc trích xuất số vòng 1 là kết quả kiểm vòng 2.

Không cần chờ thêm tin nhắn “bắt đầu”. Không phải chạy bản sửa khi Dev chưa bàn giao; không tự khắc phục mã Dev trong bản sao rồi báo bản chính đã đạt.

## 2. Quyết định về Python

**Python 3.11 phải nằm trong phạm vi hỗ trợ/kiểm thử của bản sửa vòng 2**, do môi trường DA hiện có Python 3.11.2. Giao Dev sửa f-string NB04 cho tương thích và chọn dependency cài được/chạy được trên môi trường này; không chốt chỉ Python≥3.12 rồi xem blocker phía DA là lỗi DA.

Đây là yêu cầu tương thích RA đặt ra, **chưa phải chứng nhận toàn bộ mã/dependency đã hỗ trợ Python 3.11.2**. Dev và DA phải ghi phiên bản Python đầy đủ, lock dependency đã kiểm; nếu resolver, wheel hoặc lỗi môi trường khác chặn thì gửi traceback để RA xét, không tự báo pass. Không giả định package mới nhất luôn hỗ trợ 3.11.2.

Có thể hỗ trợ thêm Python khác; xác nhận tối thiểu trên 3.11.2 trong môi trường DA. Nếu thực sự không thể đáp ứng, Dev phải nêu nguyên nhân và đề xuất môi trường kiểm thay thế để RA phê duyệt trước khi thay phạm vi. Không đòi DA cài Python khác khi phiên đó không cho phép.

## 3. Quyết định về nhánh và hồ sơ

**Đồng ý DA dùng nhánh phiên hiện tại và cập nhật PR #3**; không tạo/chuyển sang nhánh khác. Lưu hồ sơ mới tại `Air-Project-main/reports/ra/round2/`; snapshot cũ vẫn ghim tại `0dfc715`.

- Giữ nguyên ba tài liệu và bằng chứng DA v1.1/v1.0 của vòng 1; không sửa lịch sử để biến chúng thành kết quả vòng 2.
- Tên đề nghị: `da_verification_protocol.md`, `reproduction_log.md`, `verification_results.md`, `ba_evidence_extract.md`, và `evidence/` trong thư mục vòng 2.
- Không ghi đè file `RA_DECISIONS_01.md` hoặc hồ sơ RA/BA/Dev. Đọc bản ghim để tham khảo; không bắt buộc merge nhánh RA vào DA.
- Lấy code Dev ra bản sao ngoài checkout làm việc chính, ghi SHA chính xác và base tương ứng. Không đổi nhánh phiên hoặc merge thay đổi vai khác để chạy.
- Protocol có thể commit trước. Khi chạy kiểm cuối, ghi cả SHA protocol, SHA code Dev, SHA script và SHA artifact/hồ sơ; không dùng cụm “bản mới nhất” thay SHA.
- Không merge/đóng PR. Nếu PR #3 thay trạng thái trước khi DA đẩy hồ sơ, báo RA/người điều phối và tuân theo trạng thái nhánh thực tế của phiên.

## 4. Protocol chuẩn bị được chấp nhận về nguyên tắc

Giữ kế hoạch DA đã nêu: split theo target date; train đến 30/06/2019, test 01/07/2019–29/02/2020, holdout từ 01/03/2020 đến cuối dữ liệu; ba baseline, Ridge L1–L3; MAE/RMSE/R²; confusion counts, recall/precision/F1 ở ngưỡng201 và F2 chọn trên train/OOF; paired CI bootstrap khối lịch chung giữa TP, B=4000, seed0, khối14 ngày và độ nhạy7/28.

Điều kiện ghi vào protocol:

- Test cũ đã mở; không tune bằng kết quả test/holdout để tăng metric.
- Khóa cách chọn alpha/ngưỡng theo train/OOF; không nhất thiết ép alpha mới bằng alpha cũ nếu preprocessing/nhãn đã thay, nhưng phải báo phương pháp và giá trị trước/sau.
- Cùng nhãn/cùng cohort cho so sánh paired khi có thể; nếu nhãn/estimand đổi, báo riêng tác động và không diễn giải như cùng phép đo.
- Tách kiểm cache offline/mock khỏi kiểm API thật; mạng bị chặn chỉ là blocked phần API.
- Khôi phục baseline với environment mới có thể lệch số học; báo diff/tolerance và phân biệt với tác động bản sửa.
- Bản thân protocol viết xong chưa đồng nghĩa đã kiểm chứng F01/F02; anchor kết quả chỉ được đánh pass khi có lệnh/log/artifact thực.

RA sẽ rà soát bản protocol khi DA gửi commit; việc cho phép bắt đầu không phê duyệt trước mọi chi tiết chưa được viết.

## 5. Những việc vẫn phải chờ

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| DA-01 / NB04 sửa | Chờ Dev bàn giao | Chưa có SHA Dev trong ACK | Chỉ chạy nghiệm thu bản sửa sau khi có commit cụ thể; chuẩn bị test được làm ngay. |
| DA-02 / causal features | Chờ Dev bàn giao | Chưa có SHA Dev trong ACK | Không dùng wrapper vòng1 để đóng mã vòng2 chưa được sửa. |
| DA-03 / nhãn và cohort | Chờ protocol Dev và RA duyệt | Chưa có protocol nhãn mới | Cho phép chuẩn bị cấu trúc đối chiếu, chưa khóa nhãn thay nhóm. |
| DA-04 / regression bản sửa | Chờ Dev và quyết định nhãn | Theo các hàng trên | Baseline cũ có thể dựng ngay, không gọi đó là kiểm bản sửa. |
| F01/F02 | Chưa nghiệm thu | Chưa có kết quả vòng2 | Không đổi trạng thái thành đóng chỉ vì nhận ACK. |

## 6. Bàn giao tiếp theo để RA xem

DA gửi **HANDOFF chuẩn bị**, không cần chờ đủ mọi phép kiểm:

- SHA commit và link PR/file protocol;
- môi trường dựng lại được hay blocked, log cài/chạy baseline và hash;
- bảng trích V16/V18/V19 cho BA;
- trạng thái từng DA-01…05: đã chuẩn bị/đã chạy/chờ/blocked;
- xác nhận hồ sơ vòng1 và baseline không bị sửa;
- vấn đề mới cần RA quyết định, nếu có.

Dev nhận kèm quyết định này với gói giao việc: xác nhận tương thích Python3.11, gửi SHA bản sửa và protocol nhãn/mẫu. BA có thể nhận bảng trích và sửa phần nội dung song song, nhưng số cuối sau sửa phải chờ DA.
