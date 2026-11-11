"""DA vòng 2 — gom log I/O (.jsonl của iotrace/sitecustomize.py) thành bảng: bước, file, đọc/ghi, sha256.
Với file được ghi, sha256 lấy tại lúc chạy script này (ngay sau khi bước đó kết thúc).
Dùng: python r2_iotrace_summary.py <trace.jsonl> <root bản sao> <tên bước> <out.csv>   (nối thêm vào out.csv nếu đã có)
"""
import hashlib, json, os, sys
import pandas as pd

log, root, step, out = sys.argv[1:5]
root = os.path.realpath(root)
rows, net = {}, []
for line in open(log, encoding="utf-8"):
    r = json.loads(line)
    if r["ev"] == "net":
        net.append(r); continue
    if "run_notebook.py" in r.get("argv", "") and os.environ.get("DA_IO_ALL") != "1":
        continue                                              # bỏ tiến trình nbclient (trình chạy); giữ kernel và tiến trình con
    rel = os.path.relpath(r["path"], root)
    if rel.startswith("notebooks/_executed") or rel.endswith(".jsonl") or os.path.basename(rel).startswith("<"):   # "<...>": tên giả của linecache
        continue
    d = rows.setdefault(rel, {"buoc": step, "file": rel, "doc": False, "ghi": False, "sha256_luc_doc": "", "sha256_sau_khi_ghi": ""})
    if r["kind"] == "read":
        if not d["doc"] and not d["ghi"]:
            d["sha256_luc_doc"] = r.get("sha256_at_open") or "(chưa tồn tại)"
        elif not d["doc"]:
            d["sha256_luc_doc"] = "(đọc lại file vừa ghi)"
        d["doc"] = True
    else:
        d["ghi"] = True
for d in rows.values():
    p = os.path.join(root, d["file"])
    if d["ghi"]:
        d["sha256_sau_khi_ghi"] = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else "(không còn file)"
df = pd.DataFrame(sorted(rows.values(), key=lambda d: d["file"]))
df["so_lan_thu_mang"] = len(net)
if len(df) == 0:
    df = pd.DataFrame([{"buoc": step, "file": "(không có sự kiện)", "doc": False, "ghi": False, "sha256_luc_doc": "", "sha256_sau_khi_ghi": "", "so_lan_thu_mang": len(net)}])
df.to_csv(out, mode="a", header=not os.path.exists(out), index=False, encoding="utf-8")
print(f"{step}: {int(df.doc.sum())} file đọc, {int(df.ghi.sum())} file ghi, {len(net)} lần thử mạng" + (f" -> {sorted(set(n['addr'] for n in net))[:3]}" if net else ""))
