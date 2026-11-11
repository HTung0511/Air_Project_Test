"""Kiểm thử tích hợp: chạy THẬT các notebook 04 -> 05 -> 06 trong một bản sao của dự án, mạng bị chặn ở mức socket.

Điều được kiểm (handoff DEV-01 mục 6-7, DEV-02 mục 7; RA-DEC-02 mục 5):
  * NB04 chạy trọn từ cache, không thử kết nối lần nào, ghi output MỚI ra `outputs/nb04/`, không đổi file nào trong `data/`.
  * NB04 với cache hỏng (8 kiểu hỏng) và mạng tắt: dừng với lỗi nêu thành phố, file, lý do; không ghi output nào.
  * NB05 và NB06 đọc đúng file thời tiết được chỉ định (đường dẫn + sha256 được ghi lại), không lặng lẽ quay về baseline.
  * NB06 thật sự dùng đường dự báo từ raw (không chỉ có hàm mới mà không gọi), và các con số thực nghiệm được đối chiếu thật:
    sửa một con số trong notebook thì notebook dừng với lỗi.
  * Chạy lại cho ra ĐÚNG output đã commit trong notebook: NB01, NB02, NB03, NB05 (nhánh hồi cứu/EDA, không sửa ở vòng 2) và
    NB04, NB06 (output do Dev chạy ở môi trường đã ghim). So output dạng chữ từng ô và số hình; không so điểm ảnh.
Các test này chậm (tổng khoảng 5 phút): `python -m pytest -m "not notebook"` để bỏ qua.
"""
import gzip
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

import data_paths
from conftest import evidence_dir

pytestmark = [pytest.mark.slow, pytest.mark.notebook]
ROOT = data_paths.ROOT
SKIP = shutil.ignore_patterns("outputs", "_executed", "__pycache__", ".ipynb_checkpoints", ".pytest_cache")
BASE_DAILY_SHA = data_paths.sha256_file(data_paths.BASELINE_WEATHER_DAILY)


def clean_env():
    """Môi trường cho tiến trình chạy notebook: như một người kiểm gọi lệnh từ shell. Bỏ mọi biến AIR_* và bỏ MPLBACKEND (conftest
    đặt MPLBACKEND=Agg cho unit test; nếu để lọt vào kernel thì notebook đã chạy không còn hình nhúng)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("AIR_") and k != "MPLBACKEND"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_chain(work, name, notebooks, weather):
    """Gọi đúng lệnh mà người kiểm sẽ gọi. Trả về (mã thoát, chain_summary.json, thư mục lần chạy)."""
    cmd = [sys.executable, str(ROOT / "tools" / "run_chain.py"), "--work", str(work), "--name", name,
           "--notebooks", notebooks, "--weather", weather, "--timeout", "1500"]
    r = subprocess.run(cmd, cwd=ROOT, env=clean_env(), capture_output=True, text=True)
    run_dir = Path(work) / name
    summary = json.loads((run_dir / "chain_summary.json").read_text(encoding="utf-8"))
    d = evidence_dir()
    if d is not None:
        (d / f"chain_{name}.log").write_text("$ " + " ".join(cmd) + f"\n[exit {r.returncode}]\n" + r.stdout + "\n--- stderr ---\n" + r.stderr, encoding="utf-8")
        (d / f"chain_{name}_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return r.returncode, summary, run_dir


def run_one(project, notebook, out, env=None):
    cmd = [sys.executable, str(ROOT / "tools" / "run_notebook.py"), str(project), notebook, "--out", str(out), "--timeout", "1500", "--block-network"]
    for k, v in (env or {}).items():
        cmd += ["--env", f"{k}={v}"]
    r = subprocess.run(cmd, cwd=ROOT, env=clean_env(), capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout[r.stdout.index("{"):])


def step(summary, prefix):
    return next(s for s in summary["steps"] if s["notebook"].startswith(prefix))


def records(summary, run, direction):
    return [r for r in summary["inputs_and_outputs_recorded"] if r["run"].startswith(run) and r["direction"] == direction]


@pytest.fixture(scope="module")
def chain_new_weather(tmp_path_factory):
    """04 -> 05 -> 06, NB05/NB06 đọc bảng thời tiết do NB04 vừa tạo trong bản sao."""
    return run_chain(tmp_path_factory.mktemp("chain"), "nb04", "04,05,06", "nb04")


@pytest.fixture(scope="module")
def nb06_baseline(tmp_path_factory):
    """Riêng NB06 với bảng thời tiết baseline (đúng snapshot mà các con số trong phần viết gắn vào)."""
    return run_chain(tmp_path_factory.mktemp("chain"), "baseline", "06", "baseline")


# ----------------------------------------------------------------------------- NB04 (F02)
def test_nb04_runs_to_the_end_offline_from_cache(chain_new_weather):
    code, summary, run_dir = chain_new_weather
    s = step(summary, "04")
    assert s["status"] == "ok" and s["cells_executed"] == s["code_cells"] == 16, s["error_tail"]
    assert summary["network_blocked"] and s["network_attempts"] == 0, s["network_attempts_detail"]   # cache đủ: không thử kết nối lần nào
    ins = records(summary, "04", "input")
    assert len(ins) == 8 and all(r["path"].startswith("data/raw/weather/") and r["kind"] == "raw đã commit" for r in ins)
    text = (run_dir / "executed" / "04_weather_merge.ipynb").read_text(encoding="utf-8")
    assert "blh_mean" in text and "SyntaxError" not in text                                           # BLH có mặt; ô 29 (f-string) chạy được trên Python này


def test_nb04_writes_new_outputs_and_leaves_data_untouched(chain_new_weather):
    code, summary, run_dir = chain_new_weather
    outs = {Path(r["path"]).name: r for r in records(summary, "04", "output")}
    assert set(outs) == {"weather_daily_8cities.csv", "air_quality_8cities_weather.csv", "nb04_vs_committed_cells.csv", "nb04_vs_committed_summary.csv"}
    assert all(r["path"].startswith("outputs/nb04/") and r["kind"].startswith("KHÔNG phải baseline") for r in outs.values())
    assert (run_dir / "proj" / "outputs" / "nb04" / "nb04_manifest.json").is_file()
    assert summary["data_files_changed_in_copy"] == [] and summary["data_files_changed_in_repo"] == []   # kể cả trong bản sao, data/ còn nguyên
    assert summary["files_changed_in_repo"] == []                                                     # repo gốc không bị đổi file nào khi chạy chuỗi
    new = pd.read_csv(run_dir / "proj" / "outputs" / "nb04" / "weather_daily_8cities.csv")
    base = pd.read_csv(data_paths.BASELINE_WEATHER_DAILY)
    assert list(new.columns) == list(base.columns) and len(new) == len(base) and new["blh_mean"].notna().all()
    assert outs["weather_daily_8cities.csv"]["sha256"] == data_paths.sha256_file(run_dir / "proj" / "outputs" / "nb04" / "weather_daily_8cities.csv")
    # Dung sai không thay cho việc liệt kê: mọi ô khác bản đã commit được lưu thành file, và danh sách đó khớp với phép so trực tiếp hai bảng.
    cells = pd.read_csv(run_dir / "proj" / "outputs" / "nb04" / "nb04_vs_committed_cells.csv")
    num = [c for c in base.columns if c not in ("City", "Date", "rain_day", "wind_dir_8")]
    n_diff = int(((new[num] - base[num]).abs() > 1e-9).to_numpy().sum()) + int((new[["rain_day", "wind_dir_8"]] != base[["rain_day", "wind_dir_8"]]).to_numpy().sum())
    assert (new[["City", "Date"]] == base[["City", "Date"]]).all().all() and len(cells) == n_diff
    assert cells["trong_dung_sai"].all() and set(cells["cot"]) <= {"temp_mean", "pressure_mean", "wind_speed_mean"}
    if len(cells):
        assert cells["abs_lech"].max() <= 0.01 + 1e-9
        frac = cells["tb_chua_lam_tron"] * 100 - (cells["tb_chua_lam_tron"] * 100).apply(__import__("math").floor)
        assert ((frac - 0.5).abs() <= 1e-6).all()                                                     # mọi ô lệch nằm đúng biên x,xx5 của trung bình chưa làm tròn


# ----------------------------------------------------------------------------- NB04 với cache hỏng, mạng tắt (handoff DEV-01 mục 4 và 6)
def _cache(proj, city):
    return proj / "data" / "raw" / "weather" / f"openmeteo_{city}_hourly.csv.gz"


def _rewrite(path, fn):
    df = fn(pd.read_csv(path))
    with gzip.open(path, "wt", newline="") as f:
        df.to_csv(f, index=False)


def _half(path):
    b = path.read_bytes()
    path.write_bytes(b[: len(b) // 2])


# (tên ca, cách làm hỏng cache trong BẢN SAO, các chuỗi phải có trong thông báo lỗi)
BROKEN_CACHE_CASES = [
    ("thiếu 1 cache", lambda p: _cache(p, "delhi").unlink(), ["Delhi", "openmeteo_delhi_hourly.csv.gz", "không có file"]),
    ("thiếu cả 8 cache", lambda p: [f.unlink() for f in (p / "data" / "raw" / "weather").glob("openmeteo_*_hourly.csv.gz")],
     ["Delhi", "Gurugram", "Lucknow", "Jaipur", "Bengaluru", "Amritsar", "Chennai", "Hyderabad", "không có file"]),
    ("cụt 24 giờ cuối", lambda p: _rewrite(_cache(p, "lucknow"), lambda d: d.iloc[:-24]), ["Lucknow", "thiếu 24 giờ", "2020-07-01"]),
    ("thiếu cột lớp biên", lambda p: _rewrite(_cache(p, "jaipur"), lambda d: d.drop(columns="boundary_layer_height")),
     ["Jaipur", "thiếu cột: boundary_layer_height"]),
    ("đổi tên một cột bắt buộc", lambda p: _rewrite(_cache(p, "chennai"), lambda d: d.rename(columns={"temperature_2m": "temp"})),
     ["Chennai", "thiếu cột: temperature_2m"]),
    ("trùng giờ", lambda p: _rewrite(_cache(p, "amritsar"), lambda d: pd.concat([d, d.iloc[-24:]], ignore_index=True)),
     ["Amritsar", "24 giờ bị trùng"]),
    ("gzip hỏng", lambda p: _half(_cache(p, "hyderabad")), ["Hyderabad", "không đọc được file"]),
    ("cache kết thúc sớm", lambda p: _rewrite(_cache(p, "bengaluru"), lambda d: d[d["time"] <= "2019-12-31T23:00"]),
     ["Bengaluru", "thiếu 4392 giờ", "2020-01-01"]),
]


@pytest.mark.parametrize("name, damage, expect", BROKEN_CACHE_CASES, ids=[c[0] for c in BROKEN_CACHE_CASES])
def test_nb04_with_a_broken_cache_stops_clearly_and_writes_nothing(tmp_path, name, damage, expect):
    """Chạy THẬT notebook 04 trên bản sao có cache hỏng, mạng tắt: notebook phải dừng với lỗi nêu đúng thành phố, file và lý do;
    không thử kết nối, không ghi output nào (kể cả output dở), không đụng tới `data/`."""
    proj = tmp_path / "proj"
    shutil.copytree(ROOT, proj, ignore=SKIP)
    damage(proj)
    before = {p.relative_to(proj).as_posix(): data_paths.sha256_file(p) for p in sorted((proj / "data").rglob("*")) if p.is_file()}
    code, res = run_one(proj, "04_weather_merge.ipynb", tmp_path / "exec")
    assert code == 1 and res["status"] == "error" and res["cells_executed"] < res["code_cells"]
    assert res["network_attempts"] == 0                                                              # offline: không thử tải thay
    for s in expect:
        assert s in res["error_tail"], f"thông báo lỗi thiếu '{s}': {res['error_tail'][-600:]}"
    assert "WeatherOfflineError" in res["error_tail"] or "WeatherCacheError" in res["error_tail"]
    assert not (proj / "outputs").exists()                                                            # không có output hoàn chỉnh giả, không có output dở
    after = {p.relative_to(proj).as_posix(): data_paths.sha256_file(p) for p in sorted((proj / "data").rglob("*")) if p.is_file()}
    assert after == before                                                                            # cache hỏng không bị "sửa", baseline không bị ghi


# ----------------------------------------------------------------------------- nối NB04 -> NB05/NB06 (RA-DEC-02 mục 5)
def test_downstream_notebooks_read_the_new_weather_not_the_baseline(chain_new_weather):
    code, summary, run_dir = chain_new_weather
    assert code == 0 and summary["ok"], [(s["notebook"], s["status"], s["error_tail"]) for s in summary["steps"]]
    new_sha = next(r["sha256"] for r in records(summary, "04", "output") if r["path"].endswith("weather_daily_8cities.csv"))
    for nb in ("05", "06"):
        s = step(summary, nb)
        assert s["status"] == "ok" and s["cells_executed"] == s["code_cells"] and s["network_attempts"] == 0
        wx = [r for r in records(summary, nb, "input") if r["role"] == "thời tiết theo ngày"]
        assert len(wx) == 1 and wx[0]["path"] == "outputs/nb04/weather_daily_8cities.csv" and wx[0]["sha256"] == new_sha, wx
        assert wx[0]["kind"].startswith("KHÔNG phải baseline")
    if new_sha == BASE_DAILY_SHA:
        pytest.skip("bảng thời tiết tạo lại trùng từng byte với baseline ở môi trường này: không phân biệt được hai file bằng sha256")


def test_weather_override_pointing_nowhere_stops_the_notebook(tmp_path):
    """AIR_WEATHER_DAILY trỏ tới file không tồn tại: NB06 phải dừng ngay ở ô Setup, không quay về đọc baseline."""
    proj = tmp_path / "proj"
    shutil.copytree(ROOT, proj, ignore=SKIP)                                                          # luôn chạy trong bản sao, không chạy trong repo
    code, res = run_one(proj, "06_predict_aqi.ipynb", tmp_path / "exec", {"AIR_WEATHER_DAILY": str(tmp_path / "khong_co.csv")})
    assert code == 1 and res["status"] == "error" and res["cells_executed"] <= 1
    assert "khong_co.csv" in res["error_tail"] and "FileNotFoundError" in res["error_tail"]
    assert not (proj / "outputs").exists()                                                            # không có output "hoàn chỉnh giả"
    # Notebook trong repo có output đã commit; bản đã chạy của lần chạy LỖI này không được còn output cũ nào của các ô chưa chạy tới.
    cells = [c for c in json.loads(Path(res["executed_copy"]).read_text(encoding="utf-8"))["cells"] if c["cell_type"] == "code"]
    assert [c.get("execution_count") for c in cells[1:]] == [None] * (len(cells) - 1) and not any(c["outputs"] for c in cells[1:])
    assert any(o.get("output_type") == "error" for o in cells[0]["outputs"])                          # ô Setup mang đúng lỗi của lần chạy này


# ----------------------------------------------------------------------------- NB06 (F01)
def test_nb06_really_runs_on_the_forecast_path_from_raw(nb06_baseline):
    code, summary, run_dir = nb06_baseline
    s = step(summary, "06")
    assert code == 0 and s["status"] == "ok" and s["cells_executed"] == s["code_cells"], s["error_tail"]
    ins = records(summary, "06", "input")
    assert ins[0]["path"] == "data/raw/city_day.csv" and ins[0]["kind"] == "raw đã commit"            # file đầu tiên được đọc là RAW
    assert not any(r["path"].endswith("air_quality_8cities_weather.csv") for r in ins)                 # bảng ghép hồi cứu không còn là đầu vào
    assert summary["files_changed_in_repo"] == []
    # trong reports/ NB06 chỉ ghi 5 hình model_0x của chính nó (ở môi trường đã ghim, hình tạo lại trùng từng byte nên danh sách rỗng)
    assert all(Path(k).parent.as_posix() == "reports/figures" and Path(k).name.startswith("model_0") for k in summary["report_files_rewritten_in_copy"])
    out = run_dir / "proj" / "outputs" / "nb06"
    run = json.loads((out / "nb06_run_summary.json").read_text(encoding="utf-8"))
    n = run["cohort"]["n"]
    preds = pd.read_csv(out / "nb06_predictions.csv", parse_dates=["Date", "Date_target"])
    assert len(preds) == n["test"] + n["lockdown"] and (preds["Date_target"] == preds["Date"] + pd.Timedelta(days=1)).all()
    raw = pd.read_csv(data_paths.RAW_FILE, usecols=["City", "Date", "AQI"], parse_dates=["Date"]).set_index(["City", "Date"])["AQI"]
    label = raw.reindex(pd.MultiIndex.from_arrays([preds["City"], preds["Date_target"]])).to_numpy()
    assert (preds["y"].to_numpy() == label).all()                                                     # nhãn trong file dự đoán = AQI raw của ngày t+1
    today = raw.reindex(pd.MultiIndex.from_arrays([preds["City"], preds["Date"]])).to_numpy()
    assert (preds["Ngày mai = hôm nay"].to_numpy() == today).all()                                    # baseline 'hôm nay' = AQI raw của ngày t
    assert run["rò rỉ từ raw"]["ô khác khi cắt raw ở t"] == 0 and run["rò rỉ từ raw"]["ô khác khi nhiễu dữ liệu sau t"] == 0
    assert run["rò rỉ từ raw"]["số ngày cắt"] >= 20
    mae_l3 = (preds.loc[preds["split"] == "test", "y"] - preds.loc[preds["split"] == "test", "Ridge L3"]).abs().mean()
    assert abs(mae_l3 - run["test"]["Ridge L3"]["MAE"]) < 1e-9                                        # chỉ số trong tóm tắt tính lại được từ file dự đoán
    # Mọi khoá mẫu và mọi ô bị che được lưu thành file (RA-DEC-02 mục 2 và 3): đối chiếu lại với raw bằng pandas thuần.
    keys = pd.read_csv(out / "nb06_cohort_keys.csv", parse_dates=["Date", "Date_target"])
    assert len(keys) == sum(n.values()) and not keys.duplicated(["City", "Date"]).any()
    assert (keys["Date_target"] == keys["Date"] + pd.Timedelta(days=1)).all()
    assert (keys["AQI"].to_numpy() == raw.reindex(pd.MultiIndex.from_arrays([keys["City"], keys["Date"]])).to_numpy()).all()
    assert (keys["y"].to_numpy() == raw.reindex(pd.MultiIndex.from_arrays([keys["City"], keys["Date_target"]])).to_numpy()).all()
    assert int((~keys["co_o_duong_hoi_cuu"]).sum()) == run["cohort"]["chỉ có ở đường dự báo"]
    masked = pd.read_csv(out / "nb06_masked_cells.csv", parse_dates=["Date"])
    assert len(masked) == run["che và điền chất ô nhiễm"]["số ô bị che"] and set(masked["cot_raw"]) <= set(run["che và điền chất ô nhiễm"]["cột áp quy tắc số 0 treo"])
    full = pd.read_csv(data_paths.RAW_FILE, usecols=["City", "Date", "CO"], parse_dates=["Date"]).set_index(["City", "Date"])["CO"]
    for back in (0, 1, 2):                                                                            # ô CO bị che: raw của ngày t, t-1, t-2 đều đúng bằng 0
        m = masked[masked["cot_raw"] == "CO"]
        assert (full.reindex(pd.MultiIndex.from_arrays([m["City"], m["Date"] - pd.Timedelta(days=back)])).to_numpy() == 0).all()
    d = evidence_dir()
    if d is not None:
        for f in sorted(out.iterdir()):
            shutil.copy(f, d / f.name)
        shutil.copy(run_dir / "executed" / "06_predict_aqi.ipynb", d / "06_predict_aqi.executed.ipynb")


def test_nb06_on_snapshot_every_narrative_number_is_checked_strictly(nb06_baseline):
    code, summary, run_dir = nb06_baseline
    out = run_dir / "proj" / "outputs" / "nb06"
    run = json.loads((out / "nb06_run_summary.json").read_text(encoding="utf-8"))
    sc = run["snapshot_checks"]
    assert all(v["trùng snapshot"] for v in run["inputs"].values()) and sc["đầu vào đúng snapshot"]
    assert sc["số con số đã đối chiếu"] == sc["số ở chế độ bắt buộc khớp"] >= 150                     # đúng snapshot: mọi con số đều bắt buộc khớp
    assert sc["lệch ở chế độ bắt buộc khớp"] == [] and sc["lệch được ghi lại (đầu vào khác snapshot)"] == []
    t = pd.read_csv(out / "nb06_snapshot_checks.csv")
    assert len(t) == sc["số con số đã đối chiếu"] and t["khớp"].all() and t["bắt buộc khớp"].all()
    last = json.loads((run_dir / "executed" / "06_predict_aqi.ipynb").read_text(encoding="utf-8"))["cells"]
    last_code = [c for c in last if c["cell_type"] == "code"][-1]
    assert "chk.finish()" in "".join(last_code["source"])                                             # lỗi hoãn lại PHẢI được phát ra ở ô mã cuối
    assert any("Mọi con số mà phần viết nhắc tới khớp" in "".join(o.get("text", "")) for o in last_code["outputs"])


def test_nb06_with_new_weather_reports_instead_of_pretending(chain_new_weather):
    """Bảng thời tiết khác snapshot: các con số phụ thuộc thời tiết không còn bắt buộc khớp, nhưng vẫn được đối chiếu và ghi lại;
    các con số chỉ phụ thuộc raw (số mẫu, ngày nặng, khoá thêm/bớt) vẫn bắt buộc khớp."""
    code, summary, run_dir = chain_new_weather
    run = json.loads((run_dir / "proj" / "outputs" / "nb06" / "nb06_run_summary.json").read_text(encoding="utf-8"))
    if run["inputs"]["thời tiết theo ngày"]["sha256"] == BASE_DAILY_SHA:
        pytest.skip("bảng thời tiết tạo lại trùng từng byte với baseline ở môi trường này")
    sc = run["snapshot_checks"]
    assert run["inputs"]["raw"]["trùng snapshot"] and not run["inputs"]["thời tiết theo ngày"]["trùng snapshot"] and not sc["đầu vào đúng snapshot"]
    assert 3 <= sc["số ở chế độ bắt buộc khớp"] < sc["số con số đã đối chiếu"] and sc["lệch ở chế độ bắt buộc khớp"] == []
    t = pd.read_csv(run_dir / "proj" / "outputs" / "nb06" / "nb06_snapshot_checks.csv")
    assert int((~t["khớp"]).sum()) == len(sc["lệch được ghi lại (đầu vào khác snapshot)"])            # chỗ lệch (nếu có) được liệt kê đủ, không bị nuốt
    assert run["cohort"]["n"] == {"train": 5746, "test": 1947, "lockdown": 975}                       # cohort không phụ thuộc bảng thời tiết


def test_nb06_stops_when_a_narrative_number_is_stale(tmp_path):
    """Phép đối chiếu KHÔNG phải assert luôn đúng: đổi một con số của snapshot trong notebook (19.53 -> 19.99) thì notebook dừng với
    AssertionError ở ô cuối, sau khi đã lưu bảng 'đo được / giá trị snapshot' để người kiểm thấy lệch ở đâu."""
    proj = tmp_path / "proj"
    shutil.copytree(ROOT, proj, ignore=SKIP)
    nb_path = proj / "notebooks" / "06_predict_aqi.ipynb"
    text = nb_path.read_text(encoding="utf-8")
    old = '(\\"Ridge L3\\", 19.53)'
    assert text.count(old) == 1, "không tìm thấy con số snapshot của Ridge L3 trong notebook"
    nb_path.write_text(text.replace(old, '(\\"Ridge L3\\", 19.99)'), encoding="utf-8")
    code, res = run_one(proj, "06_predict_aqi.ipynb", tmp_path / "exec")
    assert code == 1 and res["status"] == "error" and res["cells_executed"] == res["code_cells"]      # chạy tới ô cuối rồi mới dừng
    assert "AssertionError" in res["error_tail"] and "MAE test, Ridge L3" in res["error_tail"] and "19.99" in res["error_tail"]
    t = pd.read_csv(proj / "outputs" / "nb06" / "nb06_snapshot_checks.csv")
    bad = t[~t["khớp"]]
    assert list(bad["con số"]) == ["MAE test, Ridge L3"] and bad["bắt buộc khớp"].all()                # đúng một chỗ lệch, đúng chỗ đã sửa


# ----------------------------------------------------------------------------- output đã commit trong notebook = output khi chạy lại
# Dòng không thuộc KẾT QUẢ: đường dẫn của máy chạy, dòng ghi nhận file đọc/ghi (mới thêm ở vòng 2), phiên bản thư viện.
STDOUT_NOISE = ("Thư mục gốc:", "[đọc]", "[ghi]", "LƯU Ý:", "Môi trường:", "Python ")


def text_outputs(nb_path):
    """{id ô mã: (các dòng output dạng chữ, số hình)}. Lấy stdout và text/plain; bỏ stderr (cảnh báo của thư viện) và các dòng
    trong STDOUT_NOISE; chuẩn hoá dấu phân cách đường dẫn. Hình chỉ được đếm, không so điểm ảnh."""
    cells = {}
    for i, c in enumerate(json.loads(Path(nb_path).read_text(encoding="utf-8"))["cells"]):
        if c["cell_type"] != "code":
            continue
        lines, n_img = [], 0
        for o in c.get("outputs", []):
            if o.get("output_type") == "stream" and o.get("name") == "stdout":
                lines += "".join(o["text"]).splitlines()
            elif o.get("output_type") in ("display_data", "execute_result"):
                if "image/png" in o.get("data", {}):
                    n_img += 1
                else:
                    lines += "".join(o["data"].get("text/plain", "")).splitlines()
        cells[c.get("id", i)] = ([l.rstrip().replace("\\", "/") for l in lines if not l.lstrip().startswith(STDOUT_NOISE)], n_img)
    return cells


def assert_reproduces_committed_outputs(nb_name, executed):
    """Output dạng chữ (và số hình) của từng ô khi chạy lại phải TRÙNG output đã commit trong notebook của repo."""
    old, new = text_outputs(ROOT / "notebooks" / nb_name), text_outputs(executed)
    if not any(lines or n_img for lines, n_img in old.values()):
        pytest.skip(f"{nb_name} trong repo không có output đã commit để so")
    assert set(old) == set(new), f"{nb_name}: danh sách ô mã khác nhau"
    diff = [k for k in old if old[k] != new[k]]
    detail = ""
    if diff:
        (lo, _), (ln, _) = old[diff[0]], new[diff[0]]
        pairs = [(p, q) for p, q in zip(lo, ln) if p != q][:3]
        detail = f" Ô {diff[0]}: {len(lo)} dòng đã commit, {len(ln)} dòng chạy lại; vài dòng khác đầu tiên: {pairs}"
    assert not diff, (f"{nb_name}: output dạng chữ khi chạy lại khác bản đã commit ở {len(diff)} ô {diff}.{detail} "
                      f"(xem chi tiết: python tools/compare_notebook_outputs.py notebooks/{nb_name} {executed})")


def test_nb04_rerun_reproduces_the_outputs_committed_in_the_notebook(chain_new_weather):
    """NB04 đã commit kèm output của lần chạy offline từ cache: chạy lại (bản sao mới, chặn mạng) phải ra đúng các bảng và con số đó."""
    code, summary, run_dir = chain_new_weather
    assert step(summary, "04")["status"] == "ok"
    assert_reproduces_committed_outputs("04_weather_merge.ipynb", run_dir / "executed" / "04_weather_merge.ipynb")


def test_nb06_rerun_reproduces_the_outputs_committed_in_the_notebook(nb06_baseline):
    """NB06 đã commit kèm output của lần chạy trên đúng snapshot (raw + thời tiết baseline): chạy lại phải ra đúng output đó."""
    code, summary, run_dir = nb06_baseline
    assert step(summary, "06")["status"] == "ok"
    assert_reproduces_committed_outputs("06_predict_aqi.ipynb", run_dir / "executed" / "06_predict_aqi.ipynb")


# ----------------------------------------------------------------------------- nhánh hồi cứu / EDA không đổi (handoff DEV-02 mục 1)
@pytest.fixture(scope="module")
def chain_all_six(tmp_path_factory):
    """Cả sáu notebook 01 -> 06 nối tiếp trong MỘT bản sao, bảng thời tiết baseline. NB01 ghi lại bảng sạch của bản sao."""
    return run_chain(tmp_path_factory.mktemp("chain"), "all6", "01,02,03,04,05,06", "baseline")


def test_retrospective_notebooks_still_reproduce_the_committed_outputs(chain_all_six):
    """NB01, NB02, NB03 (làm sạch và EDA) và NB05 chạy lại trong bản sao phải in ra ĐÚNG các bảng và con số đã commit trong notebook
    gốc: `pipeline.py` (guard NEW-002) và `corr_utils.py` (đường dẫn thời tiết) đã sửa nhưng hành vi trên dữ liệu đầy đủ không đổi."""
    code, summary, run_dir = chain_all_six
    assert code == 0 and summary["ok"], [(s["notebook"], s["status"], s["error_tail"]) for s in summary["steps"]]
    assert summary["files_changed_in_repo"] == [] and summary["unexpected_changes_in_copy"] == []
    assert [s["notebook"][:2] for s in summary["steps"]] == ["01", "02", "03", "04", "05", "06"]
    # Trong reports/, thứ duy nhất được ghi lại với nội dung khác là HÌNH (khác do môi trường vẽ; không so điểm ảnh ở đây).
    # Các bảng và log mà nhánh hồi cứu ghi ra (bảng điểm nghi lỗi, log làm sạch...) phải trùng từng byte với bản đã commit.
    rewritten = summary["report_files_rewritten_in_copy"]
    assert all(k.startswith("reports/figures/") and k.endswith(".png") for k in rewritten), sorted(rewritten)
    for s in summary["steps"]:
        assert s["status"] == "ok" and s["cells_executed"] == s["code_cells"] and s["network_attempts"] == 0
        if s["notebook"][:2] in ("04", "06"):
            continue                # hai notebook sửa ở vòng 2 được so ở hai test phía trên, trên bản sao mà NB01 chưa ghi lại bảng sạch
        assert any(lines or n_img for lines, n_img in text_outputs(ROOT / "notebooks" / s["notebook"]).values())   # notebook gốc có output để so
        assert_reproduces_committed_outputs(s["notebook"], run_dir / "executed" / s["notebook"])
    # NB01 vừa ghi lại bảng sạch TRONG BẢN SAO: bước sau phải ghi nhận đúng file đó có còn là bản đã commit hay không (theo nội dung)
    clean = [r for r in records(summary, "05", "input") if r["path"] == "data/processed/air_quality_8cities.csv"]
    assert len(clean) == 1
    committed = data_paths.COMMITTED_SHA256["data/processed/air_quality_8cities.csv"]
    assert clean[0]["kind"] == (data_paths.KIND_BASELINE if clean[0]["sha256"] == committed else data_paths.KIND_CHANGED)
    assert set(summary["data_files_changed_in_copy"]) <= {"data/processed/air_quality_8cities.csv"}


def test_nb06_forecast_numbers_do_not_depend_on_the_retrospective_table(chain_all_six):
    """Sau khi NB01 ghi lại bảng sạch (lệch cỡ 1e-13 so với bản đã commit), NB06 vẫn chạy trọn và các con số của ĐƯỜNG DỰ BÁO vẫn ở
    chế độ bắt buộc khớp: chúng chỉ phụ thuộc raw và bảng thời tiết. Chỉ Phần G và phép so hai đường mới phụ thuộc bảng sạch."""
    code, summary, run_dir = chain_all_six
    out = run_dir / "proj" / "outputs" / "nb06"
    run = json.loads((out / "nb06_run_summary.json").read_text(encoding="utf-8"))
    t = pd.read_csv(out / "nb06_snapshot_checks.csv")
    assert run["inputs"]["raw"]["trùng snapshot"] and run["inputs"]["thời tiết theo ngày"]["trùng snapshot"]
    assert t["khớp"].all() and run["snapshot_checks"]["lệch ở chế độ bắt buộc khớp"] == []
    forecast = t[t["con số"].str.startswith(("MAE test", "ΔMAE test", "ngưỡng F2", "03-07/2020"))]
    assert len(forecast) >= 30 and forecast["bắt buộc khớp"].all()
    retro = t[t["con số"].str.startswith(("Phần G", "so đường", "số mẫu của đường hồi cứu"))]
    clean_same = run["inputs"]["bảng sạch hồi cứu (chỉ để đối chiếu)"]["trùng snapshot"]
    assert len(retro) >= 10 and (retro["bắt buộc khớp"] == clean_same).all()
