"""Chạy một notebook bằng nbclient trong một thư mục dự án (thường là BẢN SAO), ghi bản đã chạy ra nơi khác và in tóm tắt JSON.

Notebook gốc không bị sửa. Mã thoát 0 nếu chạy trọn, 1 nếu có ô lỗi.

Dùng:
  python tools/run_notebook.py <project_root> <notebook.ipynb> [--out DIR] [--timeout S] [--block-network] [--env K=V ...]

  project_root     thư mục chứa `notebooks/`, `src/`, `data/` (notebook chạy với thư mục làm việc là `<project_root>/notebooks`)
  --out            nơi ghi bản đã chạy (mặc định `<project_root>/notebooks/_executed`)
  --block-network  chặn mọi kết nối ra ngoài máy trong kernel và ghi lại mọi lần thử (xem `tests/netguard/sitecustomize.py`)
  --env K=V        biến môi trường thêm cho kernel (lặp lại được), ví dụ AIR_WEATHER_DAILY=/duong/dan/file.csv
"""
import argparse
import json
import os
import platform
import sys
import time
import traceback
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

HERE = Path(__file__).resolve().parent
NETGUARD = HERE.parent / "tests" / "netguard"


def run(project_root, name, out_dir=None, timeout=3000, block_network=False, env=None):
    root = Path(project_root).resolve()
    src = root / "notebooks" / name
    out_dir = Path(out_dir).resolve() if out_dir else root / "notebooks" / "_executed"
    out_dir.mkdir(parents=True, exist_ok=True)
    nb = nbformat.read(src, as_version=4)

    saved = dict(os.environ)
    net_log = out_dir / (Path(name).stem + ".net_attempts.log")
    try:
        os.environ.update(env or {})
        if block_network:
            if net_log.exists():
                net_log.unlink()
            os.environ["AIR_BLOCK_NETWORK"] = "1"
            os.environ["AIR_NET_ATTEMPT_LOG"] = str(net_log)
            os.environ["PYTHONPATH"] = os.pathsep.join([str(NETGUARD)] + [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p])
        client = NotebookClient(nb, timeout=timeout, kernel_name="python3", allow_errors=False,
                                resources={"metadata": {"path": str(root / "notebooks")}})
        t0 = time.time()
        status, err = "ok", None
        try:
            client.execute()
        except CellExecutionError as e:
            status, err = "error", str(e)[-3000:]
        except Exception:                                    # noqa: BLE001 - lỗi kernel/timeout cũng phải được báo, không nuốt
            status, err = "error", traceback.format_exc()[-3000:]
        runtime = round(time.time() - t0, 1)
    finally:
        os.environ.clear()
        os.environ.update(saved)

    nbformat.write(nb, out_dir / name)
    code = [c for c in nb.cells if c.cell_type == "code"]
    attempts = net_log.read_text(encoding="utf-8").splitlines() if net_log.exists() else []
    return {"notebook": name, "status": status, "runtime_s": runtime, "code_cells": len(code),
            "cells_executed": sum(c.get("execution_count") is not None for c in code),
            "executed_copy": str(out_dir / name), "network_blocked": block_network,
            "network_attempts": len(attempts), "network_attempts_detail": attempts[:10],
            "python": platform.python_version(), "error_tail": err}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_root")
    ap.add_argument("notebook")
    ap.add_argument("--out")
    ap.add_argument("--timeout", type=int, default=3000)
    ap.add_argument("--block-network", action="store_true")
    ap.add_argument("--env", action="append", default=[], metavar="K=V")
    a = ap.parse_args()
    env = dict(kv.split("=", 1) for kv in a.env)
    res = run(a.project_root, a.notebook, a.out, a.timeout, a.block_network, env)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    sys.exit(0 if res["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
