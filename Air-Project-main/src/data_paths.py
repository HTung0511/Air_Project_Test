"""Một nơi duy nhất quyết định notebook ĐỌC file nào và GHI output mới ra đâu (vòng 2: F02, RA-DEC-02 mục 5).

Mặc định, không cần đặt gì:
  * NB03/NB05/NB06 đọc các file baseline đã commit trong `data/` (nhánh EDA giữ nguyên).
  * NB04 ghi output MỚI ra `outputs/nb04/` (thư mục scratch, không commit). NB04 KHÔNG ghi đè baseline trong `data/processed/`.
  * NB06 ghi bảng tóm tắt lần chạy (cohort, chỉ số, dự đoán theo khoá) ra `outputs/nb06/`.
  * Cache thời tiết gốc `data/raw/weather/` chỉ được đọc. Bản tải mới (nếu bật online) nằm ở `outputs/weather_downloads/`.

Muốn NB05/NB06 đọc output mới của NB04 thì phải nói rõ, bằng một trong hai cách:
  * đặt biến môi trường `AIR_WEATHER_DAILY=<đường dẫn weather_daily_8cities.csv mới>` trước khi mở notebook, hoặc
  * chạy `python tools/run_chain.py --work <thư mục ngoài dự án> --weather nb04` (chạy NB04 -> NB05 -> NB06 trong một bản sao
    và tự nối đường dẫn; ghi lại file nào đã thật sự được đọc ở mỗi bước).
Nếu `AIR_WEATHER_DAILY` trỏ tới file không tồn tại thì dừng với lỗi; không bao giờ lặng lẽ quay về baseline.

Mỗi file đầu vào được đọc đều đi qua `record_input`: in đường dẫn + sha256, và nếu có `AIR_PROVENANCE_LOG` thì ghi thêm một
dòng JSON. Nhờ vậy người kiểm biết chắc mỗi bước đã đọc file nào, thay vì suy đoán.

Biến môi trường (tất cả đều tuỳ chọn):
  AIR_WEATHER_DAILY             file thời tiết theo ngày mà NB05/NB06 đọc
  AIR_NB04_OUT_DIR              thư mục NB04 ghi output mới
  AIR_NB06_OUT_DIR              thư mục NB06 ghi bảng tóm tắt lần chạy (mặc định `outputs/nb06/`)
  AIR_ALLOW_BASELINE_OVERWRITE  đặt "1" mới cho phép NB04 ghi vào `data/processed/` (chỉ dùng trong BẢN SAO)
  AIR_WEATHER_MODE              "offline" (mặc định) hoặc "online"
  AIR_WEATHER_CACHE_DIR         thư mục cache thời tiết gốc (chỉ đọc)
  AIR_WEATHER_DOWNLOAD_DIR      thư mục lưu bản tải mới
  AIR_PROVENANCE_LOG            file JSON-lines ghi các file đã đọc/ghi
  AIR_RUN_LABEL                 nhãn của lần chạy, ghi vào log (ví dụ tên notebook)
"""
import hashlib
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = ROOT / "data" / "raw" / "city_day.csv"
WEATHER_CACHE_DIR = ROOT / "data" / "raw" / "weather"
BASELINE_DIR = ROOT / "data" / "processed"
BASELINE_CLEAN = BASELINE_DIR / "air_quality_8cities.csv"
BASELINE_WEATHER_DAILY = BASELINE_DIR / "weather_daily_8cities.csv"
BASELINE_MERGED = BASELINE_DIR / "air_quality_8cities_weather.csv"
DEFAULT_NB04_OUT = ROOT / "outputs" / "nb04"
DEFAULT_DOWNLOAD_DIR = ROOT / "outputs" / "weather_downloads"
DEFAULT_NB06_OUT = ROOT / "outputs" / "nb06"
DAILY_NAME, MERGED_NAME = "weather_daily_8cities.csv", "air_quality_8cities_weather.csv"

ENV_WEATHER_DAILY = "AIR_WEATHER_DAILY"
ENV_NB04_OUT = "AIR_NB04_OUT_DIR"
ENV_NB06_OUT = "AIR_NB06_OUT_DIR"
ENV_ALLOW_BASELINE = "AIR_ALLOW_BASELINE_OVERWRITE"
ENV_MODE = "AIR_WEATHER_MODE"
ENV_CACHE_DIR = "AIR_WEATHER_CACHE_DIR"
ENV_DOWNLOAD_DIR = "AIR_WEATHER_DOWNLOAD_DIR"
ENV_PROV_LOG = "AIR_PROVENANCE_LOG"
ENV_RUN_LABEL = "AIR_RUN_LABEL"

# sha256 của các file raw / cache / baseline ĐÃ COMMIT mà vòng sửa 2 làm việc trên đó (khoá: đường dẫn tương đối so với thư mục
# dự án). Dùng để nói ĐÚNG về một file được đọc: nằm ở vị trí baseline chưa đủ, nội dung phải trùng bản đã commit. Ví dụ NB01
# chạy lại trong một bản sao sẽ ghi đè bảng sạch của bản sao đó (lệch cỡ 1e-13 do số học); khi ấy file ở vị trí baseline không
# còn là bản đã commit và phải được ghi nhận như vậy. `tests/test_snapshot_checks.py` kiểm bảng này khớp với file trong repo.
COMMITTED_SHA256 = {
    "data/raw/city_day.csv": "0d84b21c3e4878bbad8df362f2ab05f61ad959538dddf5918e714077ed3c1847",
    "data/processed/air_quality_8cities.csv": "38653221fda73fedb9c1f6cac13953cec8f00b81c6628ab44b0bdcef03e7c0c7",
    "data/processed/weather_daily_8cities.csv": "45f3579a222c55c0156eb7571565bb7a818b89c64ad9b89eff97da02ef224c77",
    "data/processed/air_quality_8cities_weather.csv": "2729117038eabafe3cac1ca7eec39dd99377cc7dbfbea4ca2ffc604d6bf68bc2",
    "data/raw/weather/openmeteo_amritsar_hourly.csv.gz": "43317b4763944086619f7f999217645734ab860f79010b7a55b4822d9b3c5c7e",
    "data/raw/weather/openmeteo_bengaluru_hourly.csv.gz": "a3832c8ebea5674bb5c960aa36a634b161f1ed70a7c557c46ff541158f65aa3b",
    "data/raw/weather/openmeteo_chennai_hourly.csv.gz": "6e64ca1594d5367bc4fa48bf97399d5d1ffa39c8a61165e245c04d0f3ff50fa1",
    "data/raw/weather/openmeteo_delhi_hourly.csv.gz": "4aad409d28169a027f8bc419299f6f86884f9575c31812bb1dcb3a93a6a6c90e",
    "data/raw/weather/openmeteo_gurugram_hourly.csv.gz": "444cba0e015ca4beac75215f6db018d03c4942a73bd0dbdff98cdaaf9247c427",
    "data/raw/weather/openmeteo_hyderabad_hourly.csv.gz": "482b19cee699c6ee57c60f560e62157d0a027a5b94239409415b78a20d4620e4",
    "data/raw/weather/openmeteo_jaipur_hourly.csv.gz": "dd32d11f53138e9e4abace695ca78d2dac25f3273423f8019ede4618c16f548e",
    "data/raw/weather/openmeteo_lucknow_hourly.csv.gz": "c9f452a4449bc8a9225c760a96fd3897abbc124edd755dade1b0a8aff2af931f",
}
KIND_RAW, KIND_BASELINE = "raw đã commit", "baseline đã commit"
KIND_CHANGED = "Ở VỊ TRÍ baseline/raw nhưng NỘI DUNG KHÁC bản đã commit"
KIND_OTHER = "KHÔNG phải baseline (output mới hoặc đường dẫn tự đặt)"

_seen = set()          # (kind, role, path, sha256) đã in trong tiến trình này, để không in lặp


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _env_path(name):
    v = os.environ.get(name, "").strip()
    return Path(v).expanduser().resolve() if v else None


def show(path):
    """Đường dẫn để in: tương đối so với thư mục dự án nếu nằm trong đó, ngược lại là đường dẫn tuyệt đối."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def in_baseline_tree(path):
    """True nếu `path` nằm trong `data/` của dự án (raw, cache gốc, CSV baseline): vùng không được ghi đè."""
    p = Path(path).resolve()
    return p == (ROOT / "data") or (ROOT / "data") in p.parents


# ----------------------------------------------------------------------------- nơi đọc
def weather_daily_path():
    """File thời tiết theo ngày mà NB05/NB06 đọc: `AIR_WEATHER_DAILY` nếu có đặt, nếu không là baseline đã commit."""
    p = _env_path(ENV_WEATHER_DAILY)
    if p is None:
        return BASELINE_WEATHER_DAILY
    if not p.is_file():
        raise FileNotFoundError(f"{ENV_WEATHER_DAILY} trỏ tới file không tồn tại: {p}. Dừng ở đây, không tự quay về baseline "
                                f"({show(BASELINE_WEATHER_DAILY)}). Chạy NB04 trước hoặc bỏ biến môi trường này.")
    return p


def weather_cache_dir():
    return _env_path(ENV_CACHE_DIR) or WEATHER_CACHE_DIR


def weather_download_dir():
    return _env_path(ENV_DOWNLOAD_DIR) or DEFAULT_DOWNLOAD_DIR


# ----------------------------------------------------------------------------- nơi ghi
def nb04_out_dir():
    return _env_path(ENV_NB04_OUT) or DEFAULT_NB04_OUT


def nb06_out_dir():
    return _env_path(ENV_NB06_OUT) or DEFAULT_NB06_OUT


def baseline_overwrite_allowed():
    return os.environ.get(ENV_ALLOW_BASELINE, "").strip() == "1"


def check_writable(path):
    """Chặn việc ghi vào `data/` của dự án, trừ khi người chạy bật rõ `AIR_ALLOW_BASELINE_OVERWRITE=1` (dành cho bản sao)."""
    if in_baseline_tree(path) and not baseline_overwrite_allowed():
        raise PermissionError(f"Từ chối ghi vào {show(path)}: đây là vùng baseline/raw của dự án. Output mới ghi ở "
                              f"{show(nb04_out_dir())} (đổi bằng {ENV_NB04_OUT}). Chỉ khi chạy trong BẢN SAO và thật sự muốn "
                              f"thay file baseline của bản sao đó mới đặt {ENV_ALLOW_BASELINE}=1.")
    return Path(path)


# ----------------------------------------------------------------------------- ghi nhận file đã đọc / đã ghi
def _kind_of(path, sha=None):
    """Loại của một file được đọc/ghi, xét cả VỊ TRÍ lẫn NỘI DUNG (sha256). Chỉ gọi là "đã commit" khi nội dung trùng bản đã commit."""
    p = Path(path).resolve()
    try:
        rel = p.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return KIND_OTHER
    if rel in COMMITTED_SHA256:
        sha = sha or sha256_file(p)
        if sha != COMMITTED_SHA256[rel]:
            return KIND_CHANGED
        return KIND_RAW if rel.startswith("data/raw/") else KIND_BASELINE
    if in_baseline_tree(p):
        return "trong data/ của dự án nhưng không thuộc danh sách file đã commit được theo dõi"
    return KIND_OTHER


def _log(rec):
    log = _env_path(ENV_PROV_LOG)
    if log is None:
        return
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _record(direction, role, path, quiet):
    p = Path(path).resolve()
    rec = {"run": os.environ.get(ENV_RUN_LABEL, ""), "direction": direction, "role": role, "path": str(p),
           "sha256": sha256_file(p), "bytes": p.stat().st_size, "kind": None,
           "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["kind"] = _kind_of(p, rec["sha256"])
    key = (direction, role, rec["path"], rec["sha256"])
    if key not in _seen:
        _seen.add(key)
        _log(rec)
        if not quiet:
            print(f"[{'đọc' if direction == 'input' else 'ghi'}] {role}: {show(p)} | sha256 {rec['sha256'][:16]} | {rec['kind']}")
    return rec


def record_input(role, path, quiet=False):
    """Ghi nhận một file đầu vào vừa được đọc. Trả về dict (path, sha256, kind...)."""
    rec = _record("input", role, path, quiet)
    if role == "thời tiết theo ngày" and not quiet:
        _stale_notice(rec)
    return rec


def record_output(role, path, quiet=False):
    return _record("output", role, path, quiet)


def _plain(o):
    """Đổi kiểu numpy/pandas về kiểu JSON chuẩn (NaN/inf thành null, khoá dict thành chuỗi)."""
    if isinstance(o, dict):
        return {str(k): _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [_plain(v) for v in o]
    if hasattr(o, "isoformat"):
        return o.isoformat()
    if hasattr(o, "item") and getattr(o, "ndim", 1) == 0:
        o = o.item()
    elif hasattr(o, "tolist"):
        return _plain(o.tolist())
    if isinstance(o, float):
        return o if o == o and abs(o) != float("inf") else None
    if o is None or isinstance(o, (bool, int, str)):
        return o
    return str(o)


def save_json(obj, path, role, quiet=False):
    """Ghi một dict ra JSON ở nơi được phép ghi (không phải `data/` của dự án) và ghi nhận file output."""
    path = check_writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_plain(obj), f, ensure_ascii=False, indent=1, allow_nan=False)
    return record_output(role, path, quiet=quiet)


def save_table(df, path, role, quiet=False, **to_csv_kwargs):
    """Ghi một bảng ra CSV (UTF-8) ở nơi được phép ghi và ghi nhận file output."""
    path = check_writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, encoding="utf-8", **to_csv_kwargs)
    return record_output(role, path, quiet=quiet)


def _stale_notice(rec):
    """Nếu đang đọc baseline trong khi có output NB04 mới khác nội dung, nói rõ ra (không đổi file được đọc)."""
    new = nb04_out_dir() / DAILY_NAME
    if rec["kind"] not in (KIND_BASELINE, KIND_CHANGED) or not new.is_file():
        return
    sha_new = sha256_file(new)
    if sha_new != rec["sha256"]:
        print(f"  LƯU Ý: có output NB04 mới ở {show(new)} (sha256 {sha_new[:16]}) nhưng bước này đang đọc {show(rec['path'])} "
              f"({rec['kind']}). Muốn đọc output mới: đặt {ENV_WEATHER_DAILY}={new}")


# ----------------------------------------------------------------------------- con số thực nghiệm gắn với một snapshot đầu vào
class SnapshotChecks:
    """Kiểm các CON SỐ THỰC NGHIỆM mà phần viết của một notebook nhắc tới (RA-DEC-02 mục 5).

    Một con số như "MAE 19,5" chỉ đúng với một snapshot đầu vào cụ thể (sha256 của raw, của bảng thời tiết) và một protocol.
    * Đầu vào đúng snapshot: con số PHẢI khớp, lệch là AssertionError (phần viết đã lỗi thời hoặc mã đã đổi hành vi).
    * Đầu vào khác snapshot (ví dụ bảng thời tiết vừa tạo lại, lệch 0,01 ở vài ô): con số được phép khác; lớp này ghi lại từng
      chỗ lệch và in ra, không dừng notebook và cũng không giả vờ là khớp.
    * Mỗi con số khai báo nó phụ thuộc đầu vào nào (`needs`; mặc định: mọi đầu vào). Chỉ các đầu vào ĐÓ quyết định con số có bắt
      buộc khớp hay không: bảng thời tiết đổi thì các con số chỉ tính từ raw vẫn phải khớp.
    Bất biến về cấu trúc (thứ tự thời gian, không rò rỉ, số mẫu đếm lại từ raw...) KHÔNG đi qua lớp này: chúng dùng `assert` thường
    và phải đúng với mọi đầu vào.

    `defer=False` (mặc định): chỗ lệch ở chế độ bắt buộc khớp báo AssertionError ngay.
    `defer=True`: gom mọi chỗ lệch lại, để notebook kịp lưu bảng "đo được / giá trị snapshot" ra file rồi mới báo lỗi; khi đó
    BẮT BUỘC gọi `finish()` ở cuối, nơi AssertionError được phát ra nếu có chỗ lệch bắt buộc khớp.
    Mọi con số đã đối chiếu nằm trong `records` (và `table()`), kể cả các con số khớp.
    """

    def __init__(self, expected, actual, protocol="", defer=False):
        self.expected, self.actual, self.protocol, self.defer = dict(expected), dict(actual), protocol, defer
        self.matches = {k: self.actual.get(k) == v for k, v in self.expected.items()}
        self.records, self.deviations, self.failures, self.finished = [], [], [], False

    @property
    def on_snapshot(self):
        return all(self.matches.values())

    @property
    def n_checked(self):
        return len(self.records)

    @property
    def n_strict(self):
        return sum(r["bắt buộc khớp"] for r in self.records)

    def describe(self):
        for k, v in self.expected.items():
            print(f"  {k}: sha256 {str(self.actual.get(k))[:16]} | snapshot {v[:16]} | {'TRÙNG' if self.matches[k] else 'KHÁC snapshot'}")
        print("  => " + ("mọi đầu vào đúng snapshot: mọi con số thực nghiệm phải khớp." if self.on_snapshot else
                         "có đầu vào KHÁC snapshot: con số nào phụ thuộc đầu vào đó chỉ được đối chiếu và ghi lại chỗ lệch; "
                         "con số chỉ phụ thuộc các đầu vào còn trùng snapshot vẫn phải khớp."))

    def _strict(self, needs):
        needs = list(needs or self.expected)
        unknown = [k for k in needs if k not in self.expected]
        if unknown:
            raise KeyError(f"`needs` nhắc tới đầu vào không có trong snapshot: {unknown}")
        return all(self.matches[k] for k in needs)

    def _note(self, what, ok, strict, measured=None, snapshot=None, tol=None, msg=None, hold=None):
        """Ghi một con số đã đối chiếu. `msg`: câu báo khi lệch (mặc định = mô tả). `hold`: danh sách gom lỗi để báo một lần."""
        self.records.append({"con số": what, "đo được": measured, "giá trị snapshot": snapshot, "dung sai": tol,
                             "khớp": bool(ok), "bắt buộc khớp": bool(strict)})
        if ok:
            return True
        msg = msg or what
        if not strict:
            self.deviations.append(msg)
            print(f"LỆCH so với giá trị của snapshot (đầu vào mà con số này phụ thuộc khác snapshot, không dừng): {msg}")
        elif self.defer:
            self.failures.append(msg)
            print(f"LỆCH khỏi giá trị gắn với snapshot (đầu vào ĐÚNG snapshot: sẽ báo lỗi ở finish()): {msg}")
        elif hold is not None:
            hold.append(msg)
        else:
            raise AssertionError(f"Con số thực nghiệm lệch khỏi giá trị gắn với snapshot ({self.protocol}): {msg}")
        return False

    def expect(self, cond, what, needs=None):
        """Một điều kiện đúng/sai. `needs`: tên các đầu vào mà con số này phụ thuộc (mặc định: tất cả). Chỉ khi các đầu vào đó
        đúng snapshot mới bắt buộc khớp."""
        return self._note(what, bool(cond), self._strict(needs), measured=bool(cond), snapshot=True)

    def expect_values(self, items, needs=None):
        """Đối chiếu một loạt con số. `items`: các bộ (mô tả, giá trị đo được, giá trị của snapshot, dung sai); dung sai None nghĩa
        là phải bằng đúng. Kiểm HẾT rồi mới báo, để thấy mọi chỗ lệch trong một lần chạy. Trả về True nếu mọi con số khớp."""
        strict = self._strict(needs)
        bad, all_ok = [], True
        for what, got, want, tol in items:
            ok = bool(got == want) if tol is None else bool(got == got and abs(float(got) - float(want)) <= tol)
            got_s = f"{float(got):.4f}" if isinstance(got, float) else str(got)
            msg = f"{what}: đo được {got_s}, giá trị của snapshot {want}" + (f" (dung sai {tol})" if tol is not None else "")
            all_ok &= self._note(what, ok, strict, measured=got, snapshot=want, tol=tol, msg=msg, hold=bad)
        if bad:
            raise AssertionError(f"{len(bad)} con số thực nghiệm lệch khỏi giá trị gắn với snapshot ({self.protocol}):\n  " + "\n  ".join(bad))
        return all_ok

    def table(self):
        """Mọi con số đã đối chiếu, mỗi dòng một con số: đo được, giá trị snapshot, dung sai, có khớp không, có bắt buộc khớp không."""
        import pandas as pd
        return pd.DataFrame(self.records, columns=["con số", "đo được", "giá trị snapshot", "dung sai", "khớp", "bắt buộc khớp"])

    def summary(self):
        s = (f"{self.n_checked} con số thực nghiệm đã đối chiếu, {self.n_strict} ở chế độ bắt buộc khớp; "
             f"{len(self.failures)} chỗ lệch ở chế độ bắt buộc khớp, {len(self.deviations)} chỗ lệch được ghi lại (đầu vào khác snapshot).")
        print(s)
        for d in self.failures + self.deviations:
            print("  -", d)
        return s

    def finish(self):
        """Gọi ở cuối notebook. In tóm tắt; nếu có chỗ lệch ở chế độ bắt buộc khớp thì báo AssertionError (kể cả khi `defer=True`)."""
        self.finished = True
        s = self.summary()
        if self.failures:
            raise AssertionError(f"{len(self.failures)} con số thực nghiệm lệch khỏi giá trị gắn với snapshot ({self.protocol}):\n  "
                                 + "\n  ".join(self.failures))
        return s
