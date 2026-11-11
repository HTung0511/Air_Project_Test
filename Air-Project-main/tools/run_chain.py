"""Chạy một chuỗi notebook trong một BẢN SAO của dự án, có nối đường dẫn giữa các bước, và ghi lại mọi thứ cần để kiểm.

Vì sao cần: từ vòng 2, NB04 ghi output mới ra `outputs/nb04/` chứ không ghi đè `data/processed/`. Muốn NB05/NB06 đọc output mới
đó thì phải nói rõ. Script này làm việc ấy trong một bản sao, để repo gốc không bị đụng tới, và ghi lại file nào đã thật sự
được đọc ở mỗi bước (đường dẫn + sha256).

Dùng (từ thư mục dự án `Air-Project-main/`):
  python tools/run_chain.py --work <thư mục làm việc> [--name TÊN] [--notebooks 04,05,06] [--weather baseline|nb04]
                            [--allow-network] [--timeout GIÂY] [--force]

  --work        thư mục làm việc NẰM NGOÀI dự án. Kết quả nằm ở `<work>/<name>/`.
  --name        tên lần chạy (mặc định = giá trị của --weather)
  --notebooks   các notebook chạy lần lượt, viết bằng số đầu tên file (mặc định 04,05,06)
  --weather     baseline: NB05/NB06 đọc bảng thời tiết baseline đã commit (mặc định của dự án)
                nb04:     NB05/NB06 đọc `weather_daily_8cities.csv` do NB04 vừa tạo trong bản sao (phải có 04 trong --notebooks)
  --allow-network  không chặn mạng trong kernel (mặc định: CHẶN, và ghi lại mọi lần thử kết nối)

Kết quả trong `<work>/<name>/`:
  proj/                 bản sao của dự án, nơi các notebook chạy (hình và output mới nằm trong đây)
  executed/             các notebook đã chạy, có output
  provenance.jsonl      mỗi dòng: một file đã đọc hoặc đã ghi (bước nào, đường dẫn, sha256)
  environment.txt       phiên bản Python, hệ điều hành, `pip freeze`
  chain_summary.json    lệnh, mã thoát, thời gian, trạng thái từng bước; sha256 của mã nguồn đã chạy; baseline có bị đổi không
Mã thoát: 0 nếu mọi bước chạy trọn và không file baseline nào trong bản sao bị đổi ngoài dự kiến; ngược lại 1.
"""
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(HERE))
import run_notebook  # noqa: E402

SKIP_DIRS = {"outputs", "_executed", "__pycache__", ".ipynb_checkpoints", ".pytest_cache", ".git"}
# file mà bước 01-03 (nhánh làm sạch/EDA) được phép ghi lại trong BẢN SAO; mọi file khác trong data/ phải giữ nguyên
WRITABLE_BY = {"01": ["data/processed/air_quality_8cities.csv"], "02": [], "03": [], "04": [], "05": [], "06": []}


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def tree_hashes(root, sub):
    base = Path(root) / sub
    return {str(p.relative_to(root)).replace(os.sep, "/"): sha256_file(p) for p in sorted(base.rglob("*"))
            if p.is_file() and not (set(p.relative_to(root).parts) & SKIP_DIRS)}


def git_info(path):
    def g(*args):
        r = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
        return r.stdout.rstrip("\n") if r.returncode == 0 else None
    return {"commit": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty_files": (g("status", "--porcelain", "--", ".") or "").splitlines()}        # rỗng = cây làm việc sạch ở commit trên


def find_notebook(prefix):
    hits = sorted((PROJECT / "notebooks").glob(f"{prefix}_*.ipynb"))
    if len(hits) != 1:
        raise SystemExit(f"không xác định được notebook cho '{prefix}': {[h.name for h in hits]}")
    return hits[0].name


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--name")
    ap.add_argument("--notebooks", default="04,05,06")
    ap.add_argument("--weather", choices=["baseline", "nb04"], default="baseline")
    ap.add_argument("--allow-network", action="store_true")
    ap.add_argument("--timeout", type=int, default=3000)
    ap.add_argument("--force", action="store_true", help="xoá `<work>/<name>` nếu đã có")
    a = ap.parse_args()

    steps = [s.strip() for s in a.notebooks.split(",") if s.strip()]
    if a.weather == "nb04" and "04" not in steps:
        raise SystemExit("--weather nb04 cần có 04 trong --notebooks (NB04 phải chạy trước để tạo file thời tiết mới)")
    work = Path(a.work).resolve()
    if work == PROJECT or PROJECT in work.parents:
        raise SystemExit(f"--work phải nằm NGOÀI thư mục dự án ({PROJECT}); đang là {work}")
    run_dir = work / (a.name or a.weather)
    if run_dir.exists():
        if not a.force:
            raise SystemExit(f"{run_dir} đã tồn tại; dùng --force để chạy lại từ đầu")
        shutil.rmtree(run_dir)
    proj = run_dir / "proj"
    run_dir.mkdir(parents=True)
    shutil.copytree(PROJECT, proj, ignore=lambda d, names: [n for n in names if n in SKIP_DIRS])

    env_txt = [f"python {platform.python_version()} ({sys.executable})", f"platform {platform.platform()}", "", "pip freeze:"]
    env_txt.append(subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout)
    (run_dir / "environment.txt").write_text("\n".join(env_txt), encoding="utf-8")

    data_before = tree_hashes(proj, "data")
    repo_data_before = tree_hashes(PROJECT, "data")
    source = {**tree_hashes(proj, "src"), **tree_hashes(proj, "tools"), **tree_hashes(proj, "tests/netguard"),
              **{f"notebooks/{p.name}": sha256_file(p) for p in sorted((proj / "notebooks").glob("*.ipynb"))}}
    prov = run_dir / "provenance.jsonl"
    new_daily = proj / "outputs" / "nb04" / "weather_daily_8cities.csv"

    results, failed = [], False
    for s in steps:
        name = find_notebook(s)
        env = {"AIR_PROVENANCE_LOG": str(prov), "AIR_RUN_LABEL": Path(name).stem}
        if a.weather == "nb04" and s in ("05", "06"):
            if not new_daily.is_file():
                results.append({"notebook": name, "status": "skipped", "error_tail": f"không có {new_daily}: NB04 chưa tạo được output"})
                failed = True
                continue
            env["AIR_WEATHER_DAILY"] = str(new_daily)
        cmd = (f"python tools/run_notebook.py {proj} {name} --out {run_dir / 'executed'} --timeout {a.timeout}"
               + ("" if a.allow_network else " --block-network") + "".join(f" --env {k}={v}" for k, v in env.items()))
        print(f"[{time.strftime('%H:%M:%S')}] chạy {name} ...", flush=True)
        res = run_notebook.run(proj, name, run_dir / "executed", a.timeout, not a.allow_network, env)
        res.update({"command": cmd, "exit_code": 0 if res["status"] == "ok" else 1, "env": env,
                    "executed_sha256": sha256_file(res["executed_copy"])})
        print(f"    -> {res['status']}, {res['cells_executed']}/{res['code_cells']} ô mã, {res['runtime_s']} s, "
              f"{res['network_attempts']} lần thử mạng", flush=True)
        results.append(res)
        if res["status"] != "ok":
            failed = True
            print(res["error_tail"], flush=True)
            break                                                # bước sau phụ thuộc bước trước: dừng, không chạy tiếp trên output dở

    data_after = tree_hashes(proj, "data")
    allowed = {f for s in steps for f in WRITABLE_BY.get(s, [])}
    changed = sorted(k for k in set(data_before) | set(data_after) if data_before.get(k) != data_after.get(k))
    unexpected = [k for k in changed if k not in allowed]
    repo_changed = sorted(k for k, v in tree_hashes(PROJECT, "data").items() if repo_data_before.get(k) != v)

    records = [json.loads(l) for l in prov.read_text(encoding="utf-8").splitlines()] if prov.exists() else []
    for r in records:                                           # đường dẫn tương đối so với bản sao cho dễ đọc
        try:
            r["path"] = str(Path(r["path"]).relative_to(proj))
        except ValueError:
            pass
    outputs = {str(p.relative_to(proj)).replace(os.sep, "/"): sha256_file(p) for p in sorted((proj / "outputs").rglob("*")) if p.is_file()} \
        if (proj / "outputs").exists() else {}
    summary = {"name": run_dir.name, "weather": a.weather, "notebooks": steps, "network_blocked": not a.allow_network,
               "started_from": {"project": str(PROJECT), **git_info(PROJECT)},
               "python": platform.python_version(), "platform": platform.platform(),
               "steps": results, "inputs_and_outputs_recorded": records,
               "new_outputs": outputs, "source_sha256": source,
               "data_files_changed_in_copy": changed, "unexpected_changes_in_copy": unexpected,
               "data_files_changed_in_repo": repo_changed,
               "ok": not failed and not unexpected and not repo_changed}
    (run_dir / "chain_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nTóm tắt: {run_dir / 'chain_summary.json'}")
    print(f"  các bước: " + ", ".join(f"{r['notebook']}={r['status']}" for r in results))
    print(f"  file trong data/ của bản sao bị đổi: {changed or 'không'}" + (f" (NGOÀI DỰ KIẾN: {unexpected})" if unexpected else ""))
    print(f"  file trong data/ của repo gốc bị đổi: {repo_changed or 'không'}")
    for r in records:
        if r["direction"] == "input" and r["role"] == "thời tiết theo ngày":
            print(f"  [{r['run']}] đọc thời tiết theo ngày: {r['path']} | sha256 {r['sha256'][:16]} | {r['kind']}")
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
