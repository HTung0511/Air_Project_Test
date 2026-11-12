# RA-DEC-03 — Rà soát HANDOFF chuẩn bị DA, chưa nghiệm thu Dev

Ngày 11/11/2026 · AI-2 RA · Phạm vi: protocol và công cụ chuẩn bị, không chạy lại phân tích thay DA.

**Quyết định: chấp nhận hồ sơ chuẩn bị có điều kiện; chưa duyệt nguyên trạng protocol v1.0 để nghiệm thu bản sửa.** DA chỉ cần bổ sung mục Sửa đổi trước khi xem số Dev; không làm lại toàn bộ baseline, không dựng lại dự án. F01/F02 vẫn mở, chưa có code Dev trong hồ sơ được xét.

## 1. Nguồn đã kiểm

- Protocol: [`e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61`](https://github.com/HTung0511/Air_Project_Test/blob/e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61/Air-Project-main/reports/ra/round2/da_verification_protocol.md).
- HANDOFF và bằng chứng chuẩn bị: [`13e93ae12c483f01a573ee51ef9562a315e45068`](https://github.com/HTung0511/Air_Project_Test/tree/13e93ae12c483f01a573ee51ef9562a315e45068/Air-Project-main/reports/ra/round2).
- RA đã đọc protocol, reproduction_log (gồm8 deviations), verification_results; rà các script as-of, cohort, metric, weather, baseline và I/O trọng yếu. Không mặc định mọi phép thử mới đã có đầy đủ runner nối với API Dev chưa tồn tại.

## 2. Những kiểm tra nhỏ RA đã thực hiện

Các mục dưới là audit trực tiếp của RA trên snapshot, không phải benchmark mới hoặc xác nhận kết quả Dev.

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Không sửa code/dữ liệu vòng1 | Xác nhận diff snapshot | `git diff --stat 0dfc715 13e93ae -- Air-Project-main ':!Air-Project-main/reports/ra/round2'` rỗng | Không suy từ lời HANDOFF mà đã kiểm git. |
| Artifact manifest | 47 file hiện diện khớp bytes/SHA256;0 mismatch | `R2_B08_artifact_sha256.csv` so file lấy từ git snapshot | Hai raw fixture không commit đã được khai báo; RA chưa tái tạo/hash hai file đó. Không coi là mất dữ liệu. |
| 327 dòng đối chiếu baseline | Các chênh lệch ghi trong CSV nằm trong tolerance từng dòng | `R2_B05_baseline_vs_v11.csv` | Đây là kiểm tính nhất quán artifact, không chạy lại 327 metric. `khớp` là trong dung sai, không phải bằng tuyệt đối. |
| Cohort tham chiếu | RA đối chiếu trực tiếp raw bằng stdlib:8668 khóa và y/AQI(t) khớp bảng DA | `R2_C01_ref_cohort_keys.csv` và `city_day.csv` | Kiểm khóa/ngày kế tiếp/giá trị hữu hạn>0; không huấn luyện mô hình. Không dùng count này làm điều kiện cứng cho mọi fixture. |
| Ý nghĩa helper as-of | Rà mã và thử nhỏ3 run0/NaN: phù hợp chính sách snapshot đã duyệt | `r2_ref_asof.py:asof_value`, các chuỗi [A,0,0,0,B], [A,0,0,NaN,0,B], [A,0,0,0,NaN,NaN,B] | Không kiểm toàn14 fixture/67 hàng trên code Dev. Test viết tay và self-check không thay phép thử Dev. |

Đối chứng 63 ô/57 hàng ở vòng2 và 64 ô/57 hàng walk-forward vòng1 có **định nghĩa tham chiếu khác nhau** (raw-label/suspect policy mới so với tái chạy cleaner cũ). Không bắt chúng bằng nhau hoặc xem chênh1 ô là lỗi nếu không so đúng estimand; DA phải giữ cách gọi riêng.

## 3. Trả lời hai câu hỏi của DA

### DA-Q1 — Chuỗi0: ĐỒNG Ý, nhưng phải giữ đầy đủ nghĩa snapshot

Cách hiểu trong **mã và kỳ vọng** của DA phù hợp RA-DEC-02:

- Hàng feature của ngày0 thứ1/thứ2 đã phát hành giữ nguyên0 khi ngày3 xuất hiện.
- Khi dựng **hàng ngày3**, cả run đã quan sát trong prefix≤ngày3 được mask; zero ngày1/2 không làm nguồn forward-fill của ngày3 hoặc ngày sau khi run đã được nhận diện.
- Tại NaN sau run0 chưa đủ3, một zero vẫn hợp lệ có thể làm nguồn forward-fill trong giới hạn2 ngày. Không biến chính sách thành “mọi zero đều không được fill”.
- Không nội suy/backward-fill, không nối run qua NaN/TP/ngày lịch thiếu. AQI không áp flatline này.

Nên giữ ví dụ [A,0,0,0,NaN,NaN,B] để phân biệt hai cách triển khai. Không cần đổi 67 kỳ vọng chỉ vì câu tóm tắt ngắn; bổ sung mô tả đầy đủ vào protocol.

### DA-Q2 — Raw thiếu ngày lịch: ĐỒNG Ý CHẤP NHẬN REJECT RÕ RÀNG

Trong vòng sửa này, có thể chọn một trong hai contract được Dev công bố **trước phép thử**:

1. Hỗ trợ gap: lag/target/ffill theo lịch, không shift nhầm qua gap; hoặc
2. Chỉ hỗ trợ chuỗi ngày liên tục: validate và dừng với lỗi rõ TP/ngày thiếu trước khi tạo feature/mẫu sai.

Cách2 được đánh “đạt xử lý đầu vào ngoài contract bằng từ chối rõ ràng”, **không gọi là đạt hỗ trợ gap**. Nếu gặp KeyError ngoài ý muốn, lỗi im lặng, nối sai run hoặc shift nhầm ngày thì vẫn fail. NaN có sẵn trên dòng ngày hợp lệ là tình huống khác: không được dùng contract reject gap để bỏ kiểm xử lý NaN. Không yêu cầu mở rộng code chỉ để hỗ trợ raw tổng hợp thiếu3 dòng nếu không cần cho dataset hiện tại.

## 4. Các sửa cục bộ bắt buộc trước khi nghiệm thu Dev

### AM-01 — Theo dõi đúng đường I/O và output scratch (T1.8)

**Rủi ro có căn cứ mã:** `iotrace/sitecustomize.py` chỉ ghi đường dẫn dưới `DA_IO_ROOT`; output Dev dự kiến ở scratch ngoài root có thể bị bỏ sót. Hook còn chỉ giữ lần mở đầu theo `(path,read/write)` và summary có thể thay hash bằng chuỗi “đọc lại file vừa ghi”. Không đủ để khẳng định mọi lần đọc đúng artifact mới.

DA sửa cục bộ instrumentation/runner để:

- Ghi các input/output thực tế liên quan dưới cả repo-copy và output-root/scratch được cấu hình. Ghi rõ giới hạn instrumentation, không tuyên bố trace mọi process ngoài Python.
- Với các CSV/raw/cache trọng yếu, lưu đường dẫn resolved + hash tại lần đọc có ý nghĩa; không dedup làm mất lần đọc sau khi file đã thay. Không cần băm mọi file thư viện liên tục.
- Manifest theo run: file nào được sinh, file nào NB05/NB06 thực sự đọc. Xét **path và hash**, không chỉ hash: baseline và output mới có thể giống byte.
- NB05/NB06 không bắt buộc đọc merged weather nếu thiết kế không dùng nó. NB05 phải đọc bảng AQ/weather đúng run; NB06 có thể đọc raw AQ và daily weather mới theo pipeline causal. Không ép NB06 quay lại bảng AQ hồi cứu để qua T1.8.

Đánh fail khi downstream thật sự đọc stale output trái contract, không đánh fail chỉ vì không đọc một artifact không cần thiết. Nếu trace bỏ sót do root thì là thiếu bằng chứng của phép đo, không mặc định mã Dev đã sai.

### AM-02 — So metric chưa làm tròn, không fail do định dạng (DA-04)

Protocol nói so số notebook in ra trong1e-6; NB06 hiện có các bảng làm tròn để hiển thị. **Không thể áp1e-6 lên số in1–4 chữ số rồi kết luận mô hình sai.**

- Ưu tiên bảng biến/dataframe hoặc export numeric chưa làm tròn, cùng khóa/split, để so1e-6. Nếu sai khác phải tách nguyên nhân môi trường, feature, nhãn, protocol và làm tròn.
- Với số chỉ hiển thị: dùng nửa đơn vị chữ số cuối được in + epsilon, ghi rõ đó là kiểm presentation rounding, không chứng nhận full-precision.
- Counts/key/nhãn/threshold nguyên so đúng tuyệt đối; không áp tolerance numeric của MAE vào confusion counts.
- Giữ v1.1 đối chiếu trong dung sai gốc; không bắt baseline đã round phải chính xác đến1e-6. Không cần chạy lại baseline chỉ để đổi cách gọi “khớp”.

### AM-03 — Tách feature-only, eligibility và invalid-input (T2.2/T2.3/T2.5)

- So feature tại khóa đã định trước, **không chỉ intersection các mẫu còn nhãn** sau khi cắt/perturb raw; nếu builder chỉ trả hàng có y, sẽ mất hàngt khi cắt tại t. Cần điểm vào feature-only hoặc cách xuất feature trước lọc y, không vá mã Dev trong kiểm nghiệm.
- Expected y/eligibility thay đổi khi AQI(t+1) thay không phải leakage feature; báo riêng, như RA-DEC-02.
- Mutation tương lai toànNaN/0 hoặc weather+10 có thể kích hoạt validate khác; báo rejection và phân biệt thử robustness với causal invariance. Phải có ít nhất mutation tương lai vẫn hợp lệ trong miền dữ liệu để kiểm feature, không xem mọi lần reject là bằng chứng no-leakage.
- T2.5 sửa feature test/holdout rồi kiểm tham số đã fit trên train; không để thay label/cohort/alpha-selection là biến nhiễu. Protocol không yêu cầu chạy hàng chục grid-search cho mỗi mutation.

### AM-04 — Chốt deviations thành amendment minh bạch, không tự nới tolerance

- Tính tie bằng số nguyên: chấp nhận **nếu assert precision đầu vào và đúng24 giờ** trước tính. Bản script hiện có assert precision cho5 mean; giữ kiểm này và không mở rộng sang cache tùy ý có precision khác.
- Chấp nhận hai phía round tại tie cho **đối chiếu kỳ vọng độc lập T1.4** ở5 mean; không đồng nghĩa cho5 cột được lệch baseline. **T1.5 chỉ3 cột** temp/pressure/wind, điều kiện tie và0,01+epsilon vẫn giữ.
- Tách reject-gap như mục3 vào amendment chính thức. Trước đó chỉ là deviation đề xuất, chưa là protocol đã RA duyệt.
- Các thay đổi môi trường vẽ, lọc trace và control cũ lỗi cú pháp được ghi là lịch sử baseline, không dùng để chỉnh acceptance Dev theo metric đã thấy.

DA chỉ cập nhật mục Sửa đổi cuối protocol (v1.1 hoặc amendment có version/SHA), giữ nguyên v1.0 và thời điểm khóa. Gửi diff và xác nhận chưa xem metric Dev. Không cần sửa lại các artifact baseline đã đúng; chỉ chạy lại các phép kiểm trực tiếp bị sửa instrumentation/assertion khi cần.

## 5. Kiểm soát khối lượng và thời gian — giảm công việc lặp

RA ghi nhận chính yêu cầu bàn giao chi tiết có thể làm vòng sửa phình to. Điều chỉnh tổ chức, **không giảm tính trung thực**:

1. **Không chạy lại baseline/walk-forward mã cũ:** đã có hồ sơ tái lập và hash. Chỉ chạy baseline ở lock Dev mới khi thật sự cần tách môi trường; nếu lock giống baseline đã kiểm thì tham chiếu hash, không dựng lại vô ích.
2. **Gate A — F02:** cài lock, cache đủ offline, cache âm tính và kiểm paths/content. Fail rõ thì báo sớm cho Dev; không chạy01→06 đầy đủ mỗi lần cache test fail.
3. **Gate B — F01:** fixture nhỏ + raw cohort + cutoff/perturb hợp lệ ở các mốc rủi ro. Nếu fail thì giữ counterexample tối giản, báo Dev, chưa chạy mọi mô hình A–D.
4. **Gate C — regression cuối:** sau GateA/B đạt mới chạy chuỗi hoàn chỉnh và metric A–D/CI đã chốt **một lần trên SHA ứng viên**. Chỉ tái chạy phần bị ảnh hưởng nếu Dev sửa tiếp, và ghi SHA tương ứng.
5. Walk-forward đầy đủ chỉ trên ứng viên cuối khi nhanh; nếu >6giây/lần dựng, dùng tập thay thế đã khóa trong protocol, ghi phạm vi coverage chưa kiểm. Không nói đạt mọi1113 ngày khi mới kiểm subset. Không thêm mốc/test ngoài danh sách chỉ để kéo dài vòng sửa, trừ khi có counterexample mới quan trọng.
6. Giữ A–D như protocol nhưng không cần train D: D là kiểm kê các khóa/nhãn khác. Nếu B và C thực tế cùng cohort/nhãn/feature/config thì tái sử dụng cùng run và ghi hash, không train hai lần chỉ vì tên bảng khác. Không tái sử dụng kết quả khi hai thiết kế khác thật.
7. HANDOFF tiếp theo tập trung một bảng ngắn: mã việc, SHA, pass/fail/blocked, artifact và lỗi còn mở. Chi tiết nằm trong log; không cần sao lại toàn bộ lịch sử trong mọi tin nhắn.

## 6. Trạng thái sau RA review

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| Ba việc chuẩn bị | Chấp nhận có điều kiện | Snapshot13e93ae, audit mục2 | Không phủ định công việc đã làm, không yêu cầu làm lại. |
| Chính sách chuỗi0 | Xác nhận | Mục3; helper DA phù hợp ở các ca nhỏ RA kiểm | Không phải Dev đã đạt. |
| Reject raw thiếu ngày | Chấp nhận theo contract | Mục3 | Phân biệt fail rõ ràng có chủ đích với lỗi ngẫu nhiên. |
| Protocol v1.0 | Cần amendment trước kiểm Dev | AM-01…04 | Chỉ sửa cục bộ; không mở thêm nghiên cứu. |
| DA-05 bảng BA | Có thể bàn giao ngay | Bảng trích vòng1 trong13e93ae | Không gọi là số sau sửa. |
| Mã Dev / F01 / F02 | Chưa nghiệm thu | Không có SHA Dev trong bộ hồ sơ xét | Các số tốt của baseline/self-check không thay kết quả bản sửa. |

**Tin nhắn chuyển DA:** RA đã kiểm hồ sơ chuẩn bị và chấp nhận có điều kiện; không chạy lại baseline cũ. Xác nhận hai câu hỏi theo mục3, bổ sung AM-01…04 trước kiểm Dev, gửi SHA amendment. Sau đó làm GateA→B→C khi có SHA Dev. Chỉ các mục chưa có bằng chứng tiếp tục ghi❓; không dùng ACK này để đóng F01/F02.
