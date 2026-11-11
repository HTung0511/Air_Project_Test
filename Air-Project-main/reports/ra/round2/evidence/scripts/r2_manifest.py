"""DA vòng 2 — manifest SHA-256 của mã và dữ liệu trong một bản sao dự án (để ghim baseline / so trước-sau).
Dùng: python r2_manifest.py <root Air-Project-main> <out.csv> [nhãn]
"""
import hashlib, sys
from pathlib import Path
import pandas as pd

root, out = Path(sys.argv[1]).resolve(), sys.argv[2]
label = sys.argv[3] if len(sys.argv) > 3 else ""
pats = ["data/raw/*.csv", "data/raw/weather/*", "data/processed/*", "src/*.py", "notebooks/*.ipynb", "Requirements.txt", "Metadata.json", "reports/figures/*.png"]
rows = []
for pat in pats:
    for p in sorted(root.glob(pat)):
        if p.is_file():
            rows.append({"nhan": label, "file": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
pd.DataFrame(rows).to_csv(out, index=False)
print(len(rows), "file ->", out)
