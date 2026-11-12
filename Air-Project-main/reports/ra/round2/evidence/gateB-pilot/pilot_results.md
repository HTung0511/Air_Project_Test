# GateB-PILOT — đo chi phí cutoff + smoke fixture (DA, độc lập)

Chạy trên snapshot `a9757af`, tái dùng venv 3.11.2 (không tạo venv mới). Mục tiêu: đo chi phí để lập ngân sách GateB đầy đủ. KHÔNG chạy full 1.113 ngày, KHÔNG 47 ngày × mọi perturb, KHÔNG T2.5 nặng.

## Phương pháp (ghi rõ để không suy "RAM đủ" từ việc chưa OOM)
- Tải raw (`load_raw`) + weather baseline (`load_weather_daily`); GHÉP hành trực tiếp `forecast_utils` (không import `model_utils` hồi cứu).
- Chọn 3 mốc cutoff **MÙ** (chỉ từ raw AQI/Date, trước khi xem output Dev): t1 gần chuỗi số 0 treo (flatline), t2 gần ngày lịch thiếu (gap), t3 bình thường.
- Rebuild cohort (`build_forecast_dataset`), rồi đo `make_forecast_features(as_of=t)` tại 3 mốc.
- Fixture nhỏ: `asof_pollutant` trên 3 dãy ví dụ của protocol (RA-DEC-03 DA-Q1).

## Kết quả đo được
| Hạng mục | Giá trị | Thời gian |
|---|---|---|
| Cohort rebuild | **8.668** (train 5.746 / test 1.947 / lockdown 975) | 0,097 s |
| Cutoff t1 (flatline, 2017-06-16, 5.168 hàng) | build features | 0,046 s |
| Cutoff t2 (gap, 2018-01-01, 6.760 hàng) | build features | 0,049 s |
| Cutoff t3 (normal, 2019-02-01, 9.928 hàng) | build features | 0,053 s |
| Fixture nhỏ (3 dãy) | as-of rule khớp protocol (ngày 1–2 giữ 0, ngày 3 mask; NaN đứt chuỗi) | <0,01 s |

- Chi phí mỗi cutoff **≈ hằng số ~0,05 s** (không tăng theo độ dài lịch sử; ~9 µs/hàng).
- Tổng pilot: **0,34 s** (giới hạn 5 phút). RAM: **không đo chính xác** → không kết luận "đủ" chỉ vì chưa OOM.

## Mô hình chi phí & ước tính GateB đầy đủ
- T2.2 walk-forward cắt tại mọi ngày (1.113 mốc): 1.113 × ~0,07 s (cut muộn nhất ~14.056 hàng) ≈ **80 s (~1,5 phút)**.
- T2.3 xáo trộn tương lai: 47 ngày cắt × ~4 kiểu (toàn NaN / toàn 0 / ×10 / hoán vị) × rebuild ≈ **200 lần build ≈ vài chục giây–3 phút**.
- T2.4 fixture cạnh tổng hợp: 14 tình huống / 67 hàng (xem dưới) — dãy ngắn, **<1 phút**.
- T2.5 tham số tiền xử lý chỉ học trên train: kiểm bất biến tham số (imputer/scaler/encoder), **không huấn luyện lớn**, **<1 phút**.
- **Tổng GateB ước tính: ~5–10 phút** (chưa tính metric A–D/CI — thuộc GateC).

## Đề xuất GateB đầy đủ (chờ duyệt)
- Chạy **FULL walk-forward 1.113 ngày** (T2.2): chi phí đo được ~0,05 s/cut ≪ ngưỡng 6 s của protocol → **không cần tập thay thế 17 mốc**. Giữ tập thay thế làm dự phòng nếu môi trường chậm hơn.
- T2.3: 47 ngày cắt × 4 kiểu perturb (theo protocol), so feature ngày ≤ t không đổi.
- **"fixture 14" làm rõ**: theo RA-DEC-03 "14 fixture/67 hàng" = **14 tình huống fixture, 67 hàng tổng cộng** (không phải 14 hàng). Pilot chỉ chạy 3 dãy con làm smoke; coverage đầy đủ 14/67 dành cho GateB chính, không thu nhỏ.
- T2.5: chỉ kiểm bất biến tham số, không train lại.
- Không sửa code Dev; output vào thư mục scratch; chỉ commit bằng chứng tối thiểu + SHA.

## SHA / bằng chứng
- Code: `a9757af398ddac2f8536e8019e4eb6b5900b4f75`. Venv: reuse `/tmp/da_venv_dev` (3.11.2).
- Script: `pilot_gateB.py`; raw output: `pilot_out.log` (cùng thư mục này).
