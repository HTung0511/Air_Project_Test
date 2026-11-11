# Kết quả kiểm chứng vòng 2 của DA

Phiên bản 0.1 (khung, giai đoạn chuẩn bị) · 11/11/2026 · Người lập: AI-3 DA.

**Chưa có kết quả nghiệm thu nào.** DA chưa nhận commit của Dev, nên mọi mục `R2-V01…R2-V06` dưới đây ở trạng thái ❓. File này chỉ cố định anchor và ghi phần đối chứng trên mã cũ. F01 và F02 vẫn mở.

- Giao thức: [`da_verification_protocol.md`](da_verification_protocol.md) v1.0, commit `e0eef8cccce7a09cbdbcb7de3cbdde9b35b2ab61`.
- Mã Dev: chưa có SHA.
- Môi trường, lệnh, exit code của phần chuẩn bị: [`reproduction_log.md`](reproduction_log.md).

## Trạng thái theo mã việc

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| <a id="R2-V01"></a>R2-V01 · DA-01/F02 · NB04 chạy offline bằng cache, đúng nội dung (T1.1–T1.5) | ❓ chưa chạy trên mã Dev | — | Công cụ sẵn: `r2_run_nb.sh`, `r2_weather_check.py`. Đối chứng mã cũ: [R2-B03](#R2-B03). |
| <a id="R2-V02"></a>R2-V02 · DA-01/F02 · thử âm tính và API (T1.6, T1.7) | ❓ chưa chạy trên mã Dev | — | Công cụ sẵn: `r2_nb04_negative.py`. API thật trên máy DA: ⛔ blocked. Đối chứng mã cũ: [R2-B04](#R2-B04). |
| <a id="R2-V03"></a>R2-V03 · DA-01/F02 · NB05 và NB06 đọc đúng output của NB04 (T1.8) | ❓ chưa chạy trên mã Dev | — | Công cụ sẵn: bộ theo dõi I/O. Đối chứng mã cũ: [R2-B02](#R2-B02). |
| <a id="R2-V04"></a>R2-V04 · DA-02/F01 · đặc trưng không dùng tương lai (T2.1–T2.7) | ❓ chưa chạy trên mã Dev | — | Sẵn: bảng tham chiếu và 14 ca biên của DA ([R2-B06](#R2-B06)). Cắt raw và xáo trộn tương lai phụ thuộc điểm vào Dev công bố. |
| <a id="R2-V05"></a>R2-V05 · DA-03 · nhãn và tập mẫu | ❓ chưa chạy trên mã Dev | — | Sẵn: tập mẫu tham chiếu của DA ([R2-B05](#R2-B05)). Số của Dev không được dùng làm điều kiện đạt. |
| <a id="R2-V06"></a>R2-V06 · DA-04 · chạy lại 01→06 và metric, bốn thiết kế A–D | ❓ chưa chạy trên mã Dev | — | Sẵn: bộ tính metric `r2_protocol.py`, đã đối chiếu với v1.1 ([R2-B01](#R2-B01)). |
| <a id="R2-V07"></a>R2-V07 · DA-05 · bảng V16, V18, V19 cho BA | ✅ đã trích | [`ba_evidence_extract.md`](ba_evidence_extract.md) | Số vòng 1 trên dữ liệu baseline; không phải kết quả kiểm bản sửa. S05 không tính lại. |

## Đối chứng trên mã cũ (không phải nghiệm thu)

| Tiêu chí | Kết quả | Bằng chứng | Ghi chú |
|---|---|---|---|
| <a id="R2-B01"></a>R2-B01 · Bộ tính metric của DA tái lập số v1.1 | 327/327 giá trị khớp; lệch lớn nhất 4,88e-04 | [`R2_B05_baseline_vs_v11.csv`](evidence/R2_B05_baseline_vs_v11.csv) | Mẫu 5.741 / 1.947 / 975. |
| <a id="R2-B02"></a>R2-B02 · NB01–NB06 mã cũ chạy lại; file downstream đọc | NB01, 02, 03, 05, 06: exit 0. NB04 gốc: exit 1 (mạng). NB04 offline: exit 1 (15/16 ô, cú pháp 3.11). 8/8 file so sánh output trùng vòng 1 | [`R2_B02_chain_io_summary.csv`](evidence/R2_B02_chain_io_summary.csv); [`R2_B07_rerun_vs_v11_files.csv`](evidence/R2_B07_rerun_vs_v11_files.csv) | NB05 và NB06 chỉ đọc `air_quality_8cities.csv` và `weather_daily_8cities.csv`. |
| <a id="R2-B03"></a>R2-B03 · Thời tiết: cache, bảng ngày, bảng gộp | Dữ liệu đã commit: 70/70 tiêu chí. Bảng dựng lại so với file đã commit: 852 ô khác, lớn nhất 0,01, 0 vi phạm dung sai | [`R2_W01_baseline_commit_checks.csv`](evidence/R2_W01_baseline_commit_checks.csv); [`R2_W02_chay_lai_offline_daily_vs_committed.csv`](evidence/R2_W02_chay_lai_offline_daily_vs_committed.csv) | Ba cột lệch: `temp_mean` 335, `pressure_mean` 348, `wind_speed_mean` 169. |
| <a id="R2-B04"></a>R2-B04 · Thử âm tính trên NB04 cũ | 8/8 ca cache hỏng dừng với exit 1 và không ghi output. 3 ca dừng bằng `ConnectionError` thay vì nêu lỗi cache | [`R2_B06_nb04_negative_baseline_offline.csv`](evidence/R2_B06_nb04_negative_baseline_offline.csv) | Ca đối chứng của mã cũ cũng exit 1 vì lỗi cú pháp. |
| <a id="R2-B05"></a>R2-B05 · Tập mẫu tham chiếu của DA từ raw | 8.668 mẫu (5.746 / 1.947 / 975); so với tập cũ: thêm 5 khóa ở train, bớt 0 | [`R2_C04_raw_aqi_and_cohort_checks.csv`](evidence/R2_C04_raw_aqi_and_cohort_checks.csv); [`R2_C03_cohort_key_diff.csv`](evidence/R2_C03_cohort_key_diff.csv) | Dựng không qua `src/`. |
| <a id="R2-B06"></a>R2-B06 · Tham chiếu "as-of t" và ca biên của DA | Tham chiếu so với đặc trưng mã cũ: 63 ô khác ở 57 hàng, tất cả ở train. Ca biên: 14 ca, 67/67 kỳ vọng viết tay khớp tham chiếu | [`R2_C06_ref_vs_baseline_feature_diff_summary.csv`](evidence/R2_C06_ref_vs_baseline_feature_diff_summary.csv); [`R2_F01_fixture_expected.csv`](evidence/R2_F01_fixture_expected.csv) | Theo cách DA đọc RA-DEC-02; cần RA xác nhận. |
| <a id="R2-B07"></a>R2-B07 · Walk-forward mã cũ (hiện trạng F01) | 57/8.912 hàng khác khi dựng theo thời gian thực; 64 ô; tất cả ở train; trùng kết quả vòng 1 | [`R2_B07_rerun_vs_v11_files.csv`](evidence/R2_B07_rerun_vs_v11_files.csv); [`../evidence/V07_walkforward_feature_diff.csv`](../evidence/V07_walkforward_feature_diff.csv) | 1.114 mốc cắt (14/06/2017–01/07/2020); hai tiến trình, 919 s và 923 s. |

## Vấn đề mới

Chưa có mục `NEW-R2-…` nào. NEW-001…004 của vòng 1 giữ nguyên trạng thái.
