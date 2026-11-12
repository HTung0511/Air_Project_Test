"""Kiểm công cụ chép output của notebook đã chạy vào notebook của repo (`tools/adopt_outputs.py`). Không cần kernel.

Điều phải đúng: công cụ CHỈ chép output; không bao giờ chép output của một bản có mã nguồn khác vào notebook của repo.
"""
import json
import subprocess
import sys
from pathlib import Path

import data_paths

TOOL = data_paths.ROOT / "tools" / "adopt_outputs.py"


def notebook(sources, outputs=None, timing=False, version=None):
    cells = []
    for i, (kind, src) in enumerate(sources):
        c = {"cell_type": kind, "id": f"c{i}", "metadata": {}, "source": src.splitlines(keepends=True)}
        if kind == "code":
            c["outputs"] = (outputs or {}).get(i, [])
            c["execution_count"] = i + 1 if outputs is not None else None
            if timing:
                c["metadata"]["execution"] = {"iopub.execute_input": "2026-01-01T00:00:00Z"}
        cells.append(c)
    meta = {"kernelspec": {"name": "python3"}, "language_info": {"name": "python", **({"version": version} if version else {})}}
    return {"cells": cells, "metadata": meta, "nbformat": 4, "nbformat_minor": 5}


def write(path, nb):
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


def call(*args):
    r = subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout


SRC = [("markdown", "# Tiêu đề"), ("code", "x = 1\nprint(x)"), ("code", "x + 1")]
OUT = {1: [{"output_type": "stream", "name": "stdout", "text": ["1\n"]}],
       2: [{"output_type": "execute_result", "execution_count": 3, "metadata": {}, "data": {"text/plain": ["2"]}}]}


def test_adopt_copies_outputs_only_and_drops_run_timestamps(tmp_path):
    executed = write(tmp_path / "executed.ipynb", notebook(SRC, OUT, timing=True, version="3.11.2"))
    target = write(tmp_path / "target.ipynb", notebook(SRC, timing=True))               # notebook của repo: chưa có output, còn dấu thời gian cũ
    assert call(executed, target, "--check")[0] == 1                                    # cùng mã, khác output
    assert call(executed, target)[0] == 0
    got = json.loads(target.read_text(encoding="utf-8"))
    assert [("".join(c["source"]), c["cell_type"], c["id"]) for c in got["cells"]] == [(s, k, f"c{i}") for i, (k, s) in enumerate(SRC)]
    assert got["cells"][1]["outputs"] == OUT[1] and got["cells"][2]["outputs"] == OUT[2]
    assert [c.get("execution_count") for c in got["cells"][1:]] == [2, 3]
    assert all("execution" not in c["metadata"] for c in got["cells"])                  # dấu thời gian chạy không đi vào repo
    assert got["metadata"]["language_info"]["version"] == "3.11.2"                      # ghi phiên bản Python đã tạo ra output
    assert call(executed, target, "--check")[0] == 0 and target.read_text(encoding="utf-8").endswith("}\n")


def test_stream_chunking_is_not_a_difference_but_text_and_order_are(tmp_path):
    """Kernel có thể cắt một chuỗi print thành nhiều đoạn stream tuỳ lúc xả bộ đệm. Hai bản chỉ khác cách cắt là TRÙNG; khác một ký
    tự, khác tên luồng, hay khác thứ tự giữa chữ và hình thì vẫn là KHÁC."""
    one = {1: [{"output_type": "stream", "name": "stdout", "text": ["a\n", "b\n", "c\n"]}]}
    two = {1: [{"output_type": "stream", "name": "stdout", "text": ["a\n"]}, {"output_type": "stream", "name": "stdout", "text": "b\nc\n"}]}
    target = write(tmp_path / "target.ipynb", notebook(SRC, one))
    assert call(write(tmp_path / "two.ipynb", notebook(SRC, two)), target, "--check")[0] == 0
    typo = {1: [{"output_type": "stream", "name": "stdout", "text": ["a\n"]}, {"output_type": "stream", "name": "stdout", "text": "b\nC\n"}]}
    assert call(write(tmp_path / "typo.ipynb", notebook(SRC, typo)), target, "--check")[0] == 1
    err = {1: [{"output_type": "stream", "name": "stdout", "text": ["a\n"]}, {"output_type": "stream", "name": "stderr", "text": "b\nc\n"}]}
    assert call(write(tmp_path / "err.ipynb", notebook(SRC, err)), target, "--check")[0] == 1          # stdout và stderr không gộp vào nhau
    img = {"output_type": "display_data", "metadata": {}, "data": {"text/plain": ["<Figure>"]}}
    s = lambda t: {"output_type": "stream", "name": "stdout", "text": [t]}
    a = write(tmp_path / "a.ipynb", notebook(SRC, {1: [s("x\n"), img, s("y\n")]}))
    b = write(tmp_path / "b.ipynb", notebook(SRC, {1: [s("x\n"), s("y\n"), img]}))
    assert call(a, b, "--check")[0] == 1                                                              # đoạn chữ cách nhau bởi hình không được gộp
    assert call(write(tmp_path / "two2.ipynb", notebook(SRC, two)), write(tmp_path / "empty.ipynb", notebook(SRC))) [0] == 0
    got = json.loads((tmp_path / "empty.ipynb").read_text(encoding="utf-8"))["cells"][1]["outputs"]
    assert got == one[1]                                                                              # khi chép, các đoạn được gộp thành dạng chuẩn


def test_adopt_refuses_outputs_of_different_source_code(tmp_path):
    other = [("markdown", "# Tiêu đề"), ("code", "x = 2\nprint(x)"), ("code", "x + 1")]  # một ô mã khác một ký tự
    executed = write(tmp_path / "executed.ipynb", notebook(other, OUT))
    target = write(tmp_path / "target.ipynb", notebook(SRC))
    before = target.read_bytes()
    for extra in ([], ["--check"]):
        code, out = call(executed, target, *extra)
        assert code == 2 and "KHÁC MÃ" in out
    assert target.read_bytes() == before                                                # không ghi gì
    fewer = write(tmp_path / "fewer.ipynb", notebook(SRC[:2], {1: OUT[1]}))
    assert call(fewer, target)[0] == 2 and target.read_bytes() == before                # khác số ô cũng dừng


def test_committed_notebooks_have_no_run_timestamps_and_no_error_outputs():
    """Notebook trong repo: không còn dấu thời gian chạy từng ô, không có output lỗi; NB04 và NB06 mang output (do Dev chạy ở vòng 2)."""
    for p in sorted((data_paths.ROOT / "notebooks").glob("0[46]_*.ipynb")):
        nb = json.loads(p.read_text(encoding="utf-8"))
        code = [c for c in nb["cells"] if c["cell_type"] == "code"]
        assert all("execution" not in c.get("metadata", {}) for c in code), p.name
        assert not any(o.get("output_type") == "error" for c in code for o in c.get("outputs", [])), p.name
        with_out = [c for c in code if c.get("outputs")]
        if with_out:                                                                    # có output thì phải là output của một lần chạy trọn, theo thứ tự
            assert [c["execution_count"] for c in code] == list(range(1, len(code) + 1)), p.name
