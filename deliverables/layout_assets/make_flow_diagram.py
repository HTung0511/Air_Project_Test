# Sơ đồ quy trình v2 — VẼ LẠI KHỔ HẸP ĐỂ CHỮ ĐỌC ĐƯỢC ở khổ ảnh 450pt trên trang A4.
# v1 (khổ 17,77 inch) khiến chữ 9pt chỉ còn ~3,2pt khi in ở 450pt. v2 dùng khổ 8,0 inch
# (dpi 400) nên chữ 9pt trong hộp ≈ 7,0pt và chữ 8pt (tiêu đề/ghi chú) ≈ 6,3pt khi hiển thị 450pt.
# Nội dung KHÔNG đổi so với v1: cùng 7 khối, cùng màu, cùng ghi chú; chỉ đổi khổ và ngắt dòng.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

labels = [
    ["Dữ liệu gốc"],
    ["Kiểm tra và", "làm sạch"],
    ["Bảng hồi cứu", "có cờ"],
    ["EDA và tích", "hợp thời tiết"],
    ["Phân tích", "liên hệ"],
    ["Thực nghiệm", "dự báo"],
    ["Ứng dụng", "phát lại"],
]
note = ("Ghi chú: nhánh dự báo cần kiểm soát riêng thông tin theo thời điểm; "
        "không mặc định bảng hồi cứu là dữ liệu causal.")
title = "Quy trình sáu nhóm công việc của đề tài (sơ đồ dàn trang, vẽ lại từ §1.5)"

n = len(labels)
W = 8.0
gap = 0.14
bw = (W - 0.30 - (n - 1) * gap) / n
H = 1.54
y_box, bh = 0.62, 0.72
fig, ax = plt.subplots(figsize=(W, H), dpi=400)
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

for i, lines in enumerate(labels):
    x = 0.15 + i * (bw + gap)
    is_last = (i == n - 1); is_fore = (i == n - 2); is_input = (i == 0)
    fc = "#f4e3d0" if is_last else ("#e8eef5" if is_fore else ("#f2f2f2" if is_input else "#ffffff"))
    ec = "#8a4b12" if is_last else ("#33506e" if is_fore else ("#8a8a8a" if is_input else "#4a4a4a"))
    ls = "--" if is_input else "-"
    ax.add_patch(FancyBboxPatch((x, y_box), bw, bh, boxstyle="round,pad=0.035,rounding_size=0.07",
                                linewidth=1.1, linestyle=ls, edgecolor=ec, facecolor=fc))
    ax.text(x + bw / 2, y_box + bh / 2, "\n".join(lines), ha="center", va="center",
            fontsize=9, fontweight="bold" if i in (0, n - 1) else "normal",
            color="#1a1a1a", linespacing=1.25)
    if i < n - 1:
        ax.add_patch(FancyArrowPatch((x + bw + 0.015, y_box + bh / 2), (x + bw + gap - 0.015, y_box + bh / 2),
                                     arrowstyle="-|>", mutation_scale=8, linewidth=1.0, color="#4a4a4a"))
ax.text(0.15, 0.20, note, ha="left", va="center", fontsize=8, style="italic", color="#333333")
ax.text(0.15, 1.44, title, ha="left", va="center", fontsize=8, color="#666666")
plt.subplots_adjust(left=0.004, right=0.996, top=0.996, bottom=0.004)
plt.savefig("so_do_quy_trinh.png", dpi=400, facecolor="white")
print("saved so_do_quy_trinh.png")
