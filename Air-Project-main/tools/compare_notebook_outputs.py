"""So phần OUTPUT dạng chữ của hai bản notebook đã chạy (cùng notebook, hai lần chạy), theo từng ô.

Dùng để trả lời: "đổi đầu vào / đổi môi trường / đổi mã thì con số nào trong notebook đổi?" mà không phải dò bằng mắt.
Ô được ghép theo `id`. Mỗi ô: lấy output dạng chữ (stream, text/plain, lỗi), so từng dòng. Hình ảnh chỉ được đếm (không so điểm ảnh).

  python tools/compare_notebook_outputs.py A.ipynb B.ipynb [--out diff.md] [--dump-dir DIR] [--ignore REGEX ...]

  --out       ghi báo cáo Markdown (mặc định: in ra màn hình)
  --dump-dir  ghi thêm output dạng chữ của từng bản thành file .txt (để tự diff bằng công cụ khác)
  --ignore    bỏ qua các dòng khớp biểu thức chính quy này (ví dụ dòng in đường dẫn tuyệt đối), lặp lại được
Mã thoát luôn là 0: đây là công cụ đo, không phải phép kiểm đạt/không đạt. Số dòng khác nhau được in ở dòng cuối.
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

NUM = re.compile(r"(?<![\w.])[-+−]?\d+(?:[.,]\d+)*(?:e[-+]?\d+)?(?![\w])")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def cell_text(cell):
    """(các dòng chữ của output, số hình)"""
    lines, n_img = [], 0
    for o in cell.get("outputs", []):
        t = o.get("output_type")
        if t == "stream":
            lines += "".join(o.get("text", "")).splitlines()
        elif t in ("display_data", "execute_result"):
            data = o.get("data", {})
            if "image/png" in data:
                n_img += 1
                continue                                        # text/plain của hình chỉ là "<Figure size ...>"
            if "text/plain" in data:
                lines += "".join(data["text/plain"]).splitlines()
        elif t == "error":
            lines += [f"LỖI {o.get('ename')}: {o.get('evalue')}"]
    return [ANSI.sub("", l).rstrip() for l in lines], n_img


def load(path):
    nb = json.loads(Path(path).read_text(encoding="utf-8"))
    out = {}
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            out[c.get("id") or f"#{i}"] = (i, c)
    return nb, out


def numbers(line):
    return [float(x.replace("−", "-").replace(",", ".")) if x.count(",") + x.count(".") <= 1 else x for x in NUM.findall(line)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--out"); ap.add_argument("--dump-dir")
    ap.add_argument("--ignore", action="append", default=[])
    a = ap.parse_args()
    ignore = [re.compile(x) for x in a.ignore]
    keep = lambda lines: [l for l in lines if not any(r.search(l) for r in ignore)]

    (nba, ca), (nbb, cb) = load(a.a), load(a.b)
    rep = [f"# So output dạng chữ của hai bản notebook đã chạy", "", f"- A: `{a.a}`", f"- B: `{a.b}`", ""]
    only_a, only_b = [k for k in ca if k not in cb], [k for k in cb if k not in ca]
    if only_a or only_b:
        rep += [f"- Ô mã chỉ có ở A: {only_a or 'không'}; chỉ có ở B: {only_b or 'không'}", ""]
    n_cells = n_cells_diff = n_lines_diff = n_num_diff = 0
    max_num = 0.0
    rows = []
    for k, (ia, cell_a) in ca.items():
        if k not in cb:
            continue
        ib, cell_b = cb[k]
        (la, img_a), (lb, img_b) = cell_text(cell_a), cell_text(cell_b)
        la, lb = keep(la), keep(lb)
        n_cells += 1
        if a.dump_dir:
            d = Path(a.dump_dir); d.mkdir(parents=True, exist_ok=True)
            (d / f"A_cell{ia:02d}_{k}.txt").write_text("\n".join(la) + "\n", encoding="utf-8")
            (d / f"B_cell{ib:02d}_{k}.txt").write_text("\n".join(lb) + "\n", encoding="utf-8")
        if la == lb and img_a == img_b:
            rows.append((ia, ib, k, 0, 0, 0.0, img_a, img_b))
            continue
        n_cells_diff += 1
        sm = difflib.SequenceMatcher(a=la, b=lb, autojunk=False)
        changed, cell_num, cell_max, body = 0, 0, 0.0, []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            changed += max(i2 - i1, j2 - j1)
            for x, y in zip(la[i1:i2], lb[j1:j2]):                 # dòng tương ứng: đếm số khác nhau và độ lệch lớn nhất
                nx, ny = numbers(x), numbers(y)
                if len(nx) == len(ny):
                    for p, q in zip(nx, ny):
                        if p != q:
                            cell_num += 1
                            if isinstance(p, float) and isinstance(q, float):
                                cell_max = max(cell_max, abs(p - q))
            body += [f"- A: `{l}`" for l in la[i1:i2]] + [f"+ B: `{l}`" for l in lb[j1:j2]] + [""]
        n_lines_diff += changed; n_num_diff += cell_num; max_num = max(max_num, cell_max)
        rows.append((ia, ib, k, changed, cell_num, cell_max, img_a, img_b))
        rep += [f"## Ô {ia} (A) / {ib} (B), id `{k}`: {changed} dòng khác, {cell_num} số khác, lệch số lớn nhất {cell_max:g}", ""] + body
    head = ["| Ô (A) | Ô (B) | id | dòng khác | số khác | lệch số lớn nhất | hình A | hình B |", "|---|---|---|---|---|---|---|---|"]
    head += [f"| {r[0]} | {r[1]} | `{r[2]}` | {r[3]} | {r[4]} | {r[5]:g} | {r[6]} | {r[7]} |" for r in rows]
    total = (f"Tổng: {n_cells} ô mã chung, {n_cells_diff} ô có output dạng chữ khác, {n_lines_diff} dòng khác, "
             f"{n_num_diff} số khác (trên các dòng ghép được), lệch số lớn nhất {max_num:g}.")
    rep = rep[:5] + [total, ""] + head + [""] + rep[5:]
    text = "\n".join(rep) + "\n"
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    print(total)


if __name__ == "__main__":
    main()
