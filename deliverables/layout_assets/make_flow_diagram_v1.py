# Sơ đồ quy trình — vẽ lại NGUYÊN VĂN chuỗi bước đã xác nhận trong bản thảo (§1.5 + chỉ dẫn dàn trang).
# Không chứa số liệu mới; chỉ là sơ đồ dàn trang.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

steps = [
    "Dữ liệu gốc",
    "Kiểm tra và\nlàm sạch",
    "Bảng hồi cứu\ncó cờ",
    "EDA và tích hợp\nthời tiết",
    "Phân tích\nliên hệ",
    "Thực nghiệm\ndự báo",
    "Ứng dụng\nphát lại",
]
note = ("Ghi chú: nhánh dự báo cần kiểm soát riêng thông tin theo thời điểm; "
        "không mặc định bảng hồi cứu là dữ liệu causal.")

n = len(steps)
bw, bh, gap = 2.05, 1.05, 0.42
W = n * bw + (n - 1) * gap + 0.9
H = 2.55
fig, ax = plt.subplots(figsize=(W, H), dpi=300)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

y0 = 1.32
for i, s in enumerate(steps):
    x = 0.45 + i * (bw + gap)
    is_last = (i == n - 1)
    is_fore = (i == n - 2)
    fc = "#f4e3d0" if is_last else ("#e8eef5" if is_fore else "#ffffff")
    ec = "#8a4b12" if is_last else ("#33506e" if is_fore else "#4a4a4a")
    box = FancyBboxPatch((x, y0), bw, bh, boxstyle="round,pad=0.06,rounding_size=0.12",
                         linewidth=1.4, edgecolor=ec, facecolor=fc)
    ax.add_patch(box)
    ax.text(x + bw / 2, y0 + bh / 2, s, ha="center", va="center", fontsize=9.2,
            fontweight="bold" if i in (0, n - 1) else "normal", color="#1a1a1a")
    if i < n - 1:
        ax.add_patch(FancyArrowPatch((x + bw + 0.03, y0 + bh / 2), (x + bw + gap - 0.03, y0 + bh / 2),
                                     arrowstyle="-|>", mutation_scale=13,
                                     linewidth=1.3, color="#4a4a4a"))
ax.text(0.45, 0.45, note, ha="left", va="center", fontsize=8.6, style="italic", color="#333333")
ax.text(0.45, 2.40, "Quy trình sáu nhóm công việc của đề tài (sơ đồ dàn trang, vẽ lại từ §1.5)",
        ha="left", va="center", fontsize=8.2, color="#666666")
plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
plt.savefig("so_do_quy_trinh.png", dpi=300, facecolor="white")
print("saved")
