# Chuyển bổ sung sang Git chính của nhóm

## Gói tối thiểu nên chuyển

Chỉ tải2 file từ `Air-Project-main/docs/` của repo Test:
1. `GOI_BO_SUNG_BAO_CAO.md`: nội dung gợi ý và quy tắc trích số.
2. `HUONG_DAN_CHUYEN_SANG_GIT_NHOM.md`: checklist thao tác này (không bắt buộc đưa vào bài nộp).

Không copy cả repo, không thay toàn bộ README/Data_dictionary/Metadata của nhóm bằng bản Test. Chưa có URL/phiên bản Git nhóm nên chưa thể bảo đảm đường dẫn hoặc nội dung hiện tại giống nhau.

## Cách đơn giản trên GitHub web

1. Mở Git chính của nhóm, kiểm đúng repository và nhánh; nhờ nhóm cho phép tạo PR tài liệu.
2. Tạo nhánh bổ sung tài liệu theo quy trình của nhóm. Đây là thao tác ở Git nhóm của người dùng, không yêu cầu agent đổi nhánh phiên Arena.
3. Chọn **Add file → Upload files**, đặt `GOI_BO_SUNG_BAO_CAO.md` vào thư mục `docs/` nếu nhóm có thư mục đó (có thể đổi đường dẫn theo cấu trúc nhóm). Nếu tải2 file thì đặt cả2 cùng thư mục. Commit lên nhánh bổ sung, không ghi đè main trực tiếp.
4. Mở file báo cáo thực tế, lấy từng đoạn phù hợp từ gói để chỉnh phương pháp/thảo luận/hạn chế. Đối chiếu mọi số với notebook/bảng nguồn cùng phiên bản. File gợi ý không tự thay thế báo cáo chính.
5. Mở PR với mô tả: “Bổ sung diễn giải và hạn chế; không thay dữ liệu, mô hình hoặc kết quả tính toán”. Nhóm xem diff rồi quyết định merge.

Nếu chỉ nộp PDF/Word, đưa các đoạn đã thống nhất vào Word rồi xuất lại PDF; không cần đưa toàn bộ tài liệu nội bộ vào bài nộp.

## File hiện có của nhóm: sửa khi thực sự cần

| File/nội dung | Đề xuất |
|---|---|
| Báo cáo chính | Bổ sung lý do8TP, quy ước14 ngày, phân biệt tỷ số mùa/FDR, hạn chế dự báo theo gói |
| README | Chỉ chỉnh mô tả phạm vi/kết quả nếu đang khẳng định quá mạnh; không ghi chức năng code chưa nhận |
| Data_dictionary.md / Metadata.json | Chỉ chỉnh mô tả dữ liệu đã được xác nhận; giữ JSON hợp lệ và không thêm trường dự đoán chưa triển khai |
| Notebook | Chưa thay code/output trong đợt tài liệu này; nếu sửa markdown kết luận thì bảo đảm khớp số đang hiển thị |

## Những thứ KHÔNG chuyển trong đợt này

- `reports/ra/` và các quyết định/handoff/checkpoint AI, evidence CSV/JSON/log hàng loạt.
- `src/`, `tests/`, `tools/`, Requirements/lock, notebook sửa của Dev, hình model mới.
- `data/`, cache, output sinh, venv và mọi nội dung `/tmp`.

Các thứ trên không vô giá trị, nhưng là gói kỹ thuật riêng. Chỉ tiếp nhận nếu nhóm chủ động duyệt một PR code có kiểm thử, không trộn với PR diễn giải báo cáo.

## Checklist trước merge ở Git nhóm

- [ ] Đúng Git nhóm và không làm mất thay đổi của thành viên khác.
- [ ] Chỉ các file tài liệu đã thống nhất xuất hiện trong diff.
- [ ] Số liệu khớp notebook/bảng nguồn của phiên bản nộp.
- [ ] Không nhầm số trước sửa và số ứng viên Dev.
- [ ] Không tuyên bố leakage đã giải quyết hoặc offline đã triển khai khi chưa đúng.
- [ ] Thành viên phụ trách xem và đồng ý trước merge.

PR2 của repo Test là hồ sơ RA và gói hướng dẫn; việc merge PR2 KHÔNG có nghĩa PR4 Dev đã được merge/nghiệm thu, cũng KHÔNG cập nhật tự động Git nhóm.
