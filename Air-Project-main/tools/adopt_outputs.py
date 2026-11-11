"""Đưa OUTPUT của một bản notebook đã chạy (trong bản sao, do `tools/run_chain.py` tạo) vào notebook của repo.

Notebook không được chạy ngay trong repo (NB01 ghi đè bảng sạch, mọi notebook ghi đè hình trong `reports/figures/`), nên muốn
notebook trong repo có output thì: chạy trong bản sao, rồi dùng công cụ này để chép output về. Công cụ CHỈ chép output:

  * Dừng (mã thoát 2) nếu hai bản khác nhau ở bất kỳ ô nào về loại ô, id hoặc mã nguồn: output phải đúng là của mã đang có trong repo.
  * Chép `outputs` và `execution_count` của ô mã, và `language_info` (phiên bản Python đã chạy).
  * Bỏ dấu thời gian chạy từng ô (`metadata.execution`) để file không đổi mỗi lần chạy lại khi kết quả không đổi.
  * Không đổi mã nguồn của bất kỳ ô nào; ghi file theo đúng định dạng JSON của các notebook trong repo.

  python tools/adopt_outputs.py <bản đã chạy .ipynb> <notebook trong repo .ipynb> [--check]

  --check   chỉ kiểm hai bản có cùng mã nguồn và cùng output hay không, không ghi gì (mã thoát 0: trùng, 1: khác output, 2: khác mã)
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cleaned_outputs(cell):
    """(outputs, execution_count) của một ô mã, không kèm dấu thời gian."""
    return cell.get("outputs", []), cell.get("execution_count")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("executed"); ap.add_argument("target"); ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    src = json.loads(Path(a.executed).read_text(encoding="utf-8"))
    dst = json.loads(Path(a.target).read_text(encoding="utf-8"))
    if len(src["cells"]) != len(dst["cells"]):
        print(f"KHÁC MÃ: số ô khác nhau ({len(src['cells'])} và {len(dst['cells'])})"); return 2
    for i, (s, d) in enumerate(zip(src["cells"], dst["cells"])):
        if (s["cell_type"], s.get("id"), "".join(s["source"])) != (d["cell_type"], d.get("id"), "".join(d["source"])):
            print(f"KHÁC MÃ: ô {i} (id {d.get('id')}) khác loại, id hoặc mã nguồn; không chép output của mã khác vào repo"); return 2
    code = [(s, d) for s, d in zip(src["cells"], dst["cells"]) if d["cell_type"] == "code"]
    same = all(cleaned_outputs(s) == cleaned_outputs(d) for s, d in code)
    n_out = sum(len(s.get("outputs", [])) for s, _ in code)
    if a.check:
        print(f"{'TRÙNG' if same else 'KHÁC OUTPUT'}: {len(code)} ô mã, {n_out} output ở bản đã chạy")
        return 0 if same else 1
    before = sha(a.target)
    for s, d in code:
        d["outputs"], d["execution_count"] = cleaned_outputs(s)
        d.get("metadata", {}).pop("execution", None)
    if "language_info" in src.get("metadata", {}):
        dst.setdefault("metadata", {})["language_info"] = src["metadata"]["language_info"]
    Path(a.target).write_text(json.dumps(dst, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"đã chép output của {len(code)} ô mã ({n_out} output) từ {a.executed}\n  vào {a.target}\n"
          f"  sha256 trước {before[:16]} -> sau {sha(a.target)[:16]}; mã nguồn các ô không đổi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
