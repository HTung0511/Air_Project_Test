"""DA — chạy lại một notebook trong BẢN SAO (scratch), không ghi đè artifact baseline.

Dùng:  python run_notebook.py <work_root> <notebook.ipynb> [timeout_s]
  work_root = bản sao của Air-Project-main (ví dụ /home/user/scratch/repro/Air-Project-main)
Kết quả: <work_root>/notebooks/_executed/<notebook>  + in JSON tóm tắt (runtime, lỗi, cell lỗi).
"""
import json, sys, time, traceback
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

work, name = Path(sys.argv[1]), sys.argv[2]
timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
src = work / "notebooks" / name
nb = nbformat.read(src, as_version=4)
out_dir = work / "notebooks" / "_executed"; out_dir.mkdir(exist_ok=True)
client = NotebookClient(nb, timeout=timeout, kernel_name="python3", resources={"metadata": {"path": str(work / "notebooks")}},
                        allow_errors=False)
t0 = time.time(); status, err = "ok", None
try:
    client.execute()
except CellExecutionError as e:
    status, err = "error", str(e)[-3000:]
except Exception as e:                                   # noqa: BLE001
    status, err = "error", traceback.format_exc()[-3000:]
nbformat.write(nb, out_dir / name)
n_code = sum(c.cell_type == "code" for c in nb.cells)
n_run = sum(c.cell_type == "code" and c.get("execution_count") is not None for c in nb.cells)
print(json.dumps({"notebook": name, "status": status, "runtime_s": round(time.time() - t0, 1), "code_cells": n_code,
                  "cells_executed": n_run, "error_tail": err}, ensure_ascii=False, indent=1))
sys.exit(0 if status == "ok" else 1)
