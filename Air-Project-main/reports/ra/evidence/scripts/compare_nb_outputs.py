"""So sánh output ĐÃ LƯU trong notebook gốc (tác giả) với output DA chạy lại (nbclient), theo từng ô code.
Lấy text (stream + text/plain), bỏ mã màu ANSI, tách toàn bộ con số và so theo thứ tự.
Phân loại mỗi ô: 'khớp' (text giống hệt hoặc mọi số bằng nhau), 'lệch nhỏ' (cùng số lượng số, lệch tương đối ≤ rtol),
'lệch lớn' (lệch > rtol), 'khác cấu trúc' (số lượng số khác nhau -> xem thủ công), 'lỗi' (ô chạy lại bị lỗi/không chạy).
Dùng: python compare_nb_outputs.py <orig.ipynb> <executed.ipynb> <out.csv> [rtol=0.005]
"""
import sys, re, nbformat, pandas as pd, numpy as np
ANSI = re.compile(r"\x1b\[[0-9;]*m"); NUM = re.compile(r"(?<![A-Za-z_\d.])[-+]?\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?%?")

def text_of(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.output_type == "stream":
            if o.get("name") != "stderr": out.append(o.text)      # bỏ stderr (cảnh báo deprecation của thư viện)
        elif o.output_type in ("execute_result", "display_data"):
            d = o.get("data", {})
            if "text/plain" in d and not d["text/plain"].startswith("<Figure"): out.append(d["text/plain"])
            if "text/markdown" in d: out.append(d["text/markdown"])
        elif o.output_type == "error": out.append(f"ERROR {o.ename}: {o.evalue}")
    t = ANSI.sub("", "\n".join(out))
    return re.sub(r"[A-Za-z]:\\[^\s'\"]+|/[\w./-]*(?:scratch|home|Users)[\w./-]*", "<PATH>", t)

def nums(t):
    r = []
    for m in NUM.findall(t):
        s = m.rstrip("%")
        # số kiểu Việt "14.056" / "2,82": thử cả hai cách, ưu tiên float chuẩn
        try: r.append(float(s)); continue
        except ValueError: pass
        try: r.append(float(s.replace(".", "").replace(",", ".")))
        except ValueError: pass
    return r

def n_img(cell): return sum(1 for o in cell.get("outputs", []) if "image/png" in o.get("data", {}))

a = nbformat.read(sys.argv[1], 4); b = nbformat.read(sys.argv[2], 4); rtol = float(sys.argv[4]) if len(sys.argv) > 4 else 0.005
ca = [(i, c) for i, c in enumerate(a.cells) if c.cell_type == "code"]; cb = [(i, c) for i, c in enumerate(b.cells) if c.cell_type == "code"]
assert len(ca) == len(cb)
rows = []
for (i, x), (_, y) in zip(ca, cb):
    tx, ty = text_of(x), text_of(y); nx, ny = nums(tx), nums(ty)
    err = any(o.output_type == "error" for o in y.get("outputs", [])); ran = y.get("execution_count") is not None
    r = {"cell": i, "so_goc": len(nx), "so_chay_lai": len(ny), "hinh_goc": n_img(x), "hinh_chay_lai": n_img(y), "text_giong_het": tx == ty}
    if err or not ran: r.update(phan_loai="lỗi" if err else "không chạy", so_khac=None, max_abs=None, max_rel=None, vi_du="")
    elif tx == ty: r.update(phan_loai="khớp", so_khac=0, max_abs=0.0, max_rel=0.0, vi_du="")
    elif len(nx) != len(ny): r.update(phan_loai="khác cấu trúc", so_khac=None, max_abs=None, max_rel=None, vi_du="")
    else:
        A, B = np.array(nx), np.array(ny); d = np.abs(A - B); rel = d / np.maximum(np.abs(A), 1e-12); k = d > 0
        ex = "; ".join(f"{p:g}→{q:g}" for p, q in list(zip(A[k], B[k]))[:6])
        # sai khác tuyệt đối rất nhỏ so với độ phân giải in ra (≤ 0,02 đơn vị) cũng coi là lệch nhỏ
        small = (rel <= rtol) | (d <= 0.02)
        r.update(phan_loai="khớp" if not k.any() else ("lệch nhỏ" if small.all() else "lệch lớn"), so_khac=int(k.sum()),
                 max_abs=float(d.max()) if len(d) else 0.0, max_rel=float(rel[k].max()) if k.any() else 0.0, vi_du=ex)
    rows.append(r)
df = pd.DataFrame(rows); df.to_csv(sys.argv[3], index=False)
print(df.to_string()); print(df.phan_loai.value_counts().to_dict(), "| tổng số con số gốc:", int(df.so_goc.sum()))
