"""DA vòng 2 — T1.6: thử âm tính cho NB04 khi cache hỏng và mạng tắt. Mỗi ca chạy trên một BẢN SAO riêng; không sửa notebook.

Dùng: python r2_nb04_negative.py <python> <root Air-Project-main (nguồn, chỉ đọc)> <tên notebook trong notebooks/> <thư mục làm việc> <out.csv> [nhãn]
Mỗi ca ghi: exit code, số ô đã chạy, tên lỗi và dòng lỗi cuối, số lần thử mạng, file trong data/processed bị đổi hoặc được tạo,
và 8 file cache có bị ghi đè không. Điều kiện đạt (da_verification_protocol.md, T1.6): exit khác 0; thông báo nêu đúng vấn đề;
không có output "hoàn chỉnh" nào được ghi hay ghi đè. Ca 00 (cache nguyên vẹn) là ca đối chứng: phải exit 0.
Cột `dat_tu_dong` chỉ xét hai điều kiện đo được bằng máy (exit code, output không đổi); việc thông báo lỗi có "nêu đúng vấn đề" do DA đọc.
"""
import gzip, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
import pandas as pd

py, src, nb, work, out_csv = sys.argv[1], Path(sys.argv[2]).resolve(), sys.argv[3], Path(sys.argv[4]), sys.argv[5]
tag = sys.argv[6] if len(sys.argv) > 6 else ""
HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
cache = lambda root, city: root / "data" / "raw" / "weather" / f"openmeteo_{city}_hourly.csv.gz"

def rewrite(p, fn):
    df = pd.read_csv(p); df = fn(df)
    with gzip.open(p, "wt", newline="") as f:
        df.to_csv(f, index=False)

def c_missing_one(r): cache(r, "delhi").unlink()
def c_missing_all(r): [p.unlink() for p in (r / "data/raw/weather").glob("openmeteo_*_hourly.csv.gz")]
def c_truncated_tail(r): rewrite(cache(r, "lucknow"), lambda d: d.iloc[:-24])
def c_no_blh(r): rewrite(cache(r, "jaipur"), lambda d: d.drop(columns="boundary_layer_height"))
def c_renamed_col(r): rewrite(cache(r, "chennai"), lambda d: d.rename(columns={"temperature_2m": "temp"}))
def c_dup_hours(r): rewrite(cache(r, "amritsar"), lambda d: pd.concat([d, d.iloc[-24:]], ignore_index=True))
def c_corrupt_gzip(r):
    p = cache(r, "hyderabad"); b = p.read_bytes(); p.write_bytes(b[: len(b) // 2])
def c_ends_early(r): rewrite(cache(r, "bengaluru"), lambda d: d[d["time"] <= "2019-12-31T23:00"])

CASES = [("00_doi_chung_cache_nguyen_ven", None, "đối chứng: phải chạy hết, exit 0"),
         ("01_thieu_1_cache", c_missing_one, "xóa cache Delhi"), ("02_thieu_ca_8_cache", c_missing_all, "xóa cả 8 cache"),
         ("03_cache_cut_24_gio_cuoi", c_truncated_tail, "Lucknow: bỏ 24 dòng giờ cuối"), ("04_thieu_cot_BLH", c_no_blh, "Jaipur: bỏ cột boundary_layer_height"),
         ("05_doi_ten_cot_bat_buoc", c_renamed_col, "Chennai: temperature_2m -> temp"), ("06_trung_gio", c_dup_hours, "Amritsar: lặp lại 24 dòng giờ cuối"),
         ("07_gzip_hong", c_corrupt_gzip, "Hyderabad: cắt file còn một nửa số byte"), ("08_cache_ket_thuc_som", c_ends_early, "Bengaluru: chỉ đến 31/12/2019")]
rows = []
for name, fn, desc in CASES:
    root = work / name / "Air-Project-main"
    if root.parent.exists(): shutil.rmtree(root.parent)
    shutil.copytree(src, root, ignore=shutil.ignore_patterns("_executed", "__pycache__", ".ipynb_checkpoints", "ra"))
    if fn: fn(root)
    proc = {p.name: sha(p) for p in sorted((root / "data/processed").glob("*"))}
    cach = {p.name: sha(p) for p in sorted((root / "data/raw/weather").glob("*"))}
    logd = work / "logs"
    r = subprocess.run([str(HERE / "r2_run_nb.sh"), py, str(root), nb, str(logd), name, "block", "600"], capture_output=True, text=True)
    j = json.loads((logd / f"{name}.json").read_text())
    err = re.sub(r"\x1b\[[0-9;]*m", "", j.get("error_tail") or "")
    last = [l for l in err.strip().splitlines() if l.strip()]
    ename = re.findall(r"^([A-Za-z_.]*(?:Error|Exception|Exit|Interrupt))\b", "\n".join(last), flags=re.M)
    net = sum(1 for l in open(logd / f"{name}.jsonl", encoding="utf-8") if '"ev": "net"' in l) if (logd / f"{name}.jsonl").exists() else 0
    proc2 = {p.name: sha(p) for p in sorted((root / "data/processed").glob("*"))}
    cach2 = {p.name: sha(p) for p in sorted((root / "data/raw/weather").glob("*"))}
    changed = sorted(k for k in proc2 if k in proc and proc2[k] != proc[k]); created = sorted(set(proc2) - set(proc))
    cache_changed = sorted(k for k in set(cach) | set(cach2) if cach.get(k) != cach2.get(k))
    ok = (r.returncode == 0 and j["cells_executed"] == j["code_cells"]) if fn is None else (r.returncode != 0 and not changed and not created and not cache_changed)
    rows.append({"bo": tag, "ca": name, "thao_tac": desc, "notebook": nb, "exit_code": r.returncode, "o_da_chay": f'{j["cells_executed"]}/{j["code_cells"]}',
                 "ten_loi": ename[-1] if ename else "", "dong_loi_cuoi": (last[-1] if last else "")[:300], "so_lan_thu_mang (đã chặn)": net,
                 "processed_bi_doi": ";".join(changed), "processed_duoc_tao": ";".join(created), "cache_bi_ghi": ";".join(cache_changed), "dat_tu_dong": bool(ok)})
    print(f'{name}: exit={r.returncode} ô={j["cells_executed"]}/{j["code_cells"]} lỗi={rows[-1]["ten_loi"]} mạng={net} đổi={changed} tạo={created} cache_ghi={cache_changed} -> {"ĐẠT" if ok else "KHÔNG ĐẠT"}', flush=True)
    shutil.rmtree(root.parent)
pd.DataFrame(rows).to_csv(out_csv, index=False)
