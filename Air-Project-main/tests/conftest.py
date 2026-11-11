"""Cấu hình chung cho bộ kiểm thử vòng 2 (F02: thời tiết/NB04, F01: đường dự báo từ raw, NEW-002).

Chạy từ thư mục `Air-Project-main`:   python -m pytest
Không test nào ghi vào `data/` hay `reports/` của dự án; mọi file tạm nằm trong `tmp_path` của pytest.
"""
import os
import socket
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
os.environ.setdefault("MPLBACKEND", "Agg")
for _k in [k for k in os.environ if k.startswith("AIR_") and not k.startswith("AIR_TEST_")]:
    del os.environ[_k]                                           # test không thừa hưởng cấu hình AIR_* của người chạy

import numpy as np                                               # noqa: E402
import pandas as pd                                              # noqa: E402
import pytest                                                    # noqa: E402

import data_paths                                                # noqa: E402
import weather_utils as wu                                       # noqa: E402

BASELINE_FILES = [data_paths.RAW_FILE, data_paths.BASELINE_CLEAN, data_paths.BASELINE_WEATHER_DAILY, data_paths.BASELINE_MERGED] \
    + sorted(data_paths.WEATHER_CACHE_DIR.glob("*.csv.gz"))


@pytest.fixture(scope="session", autouse=True)
def baseline_untouched():
    """Sau cả phiên test, mọi file raw/cache/baseline của dự án phải còn nguyên từng byte."""
    before = {p: data_paths.sha256_file(p) for p in BASELINE_FILES}
    yield
    after = {p: data_paths.sha256_file(p) for p in BASELINE_FILES}
    changed = [str(p) for p in before if before[p] != after[p]]
    assert not changed, f"test đã làm đổi file baseline/raw: {changed}"


@pytest.fixture
def no_network(monkeypatch):
    """Vô hiệu hoá mạng trong tiến trình test và đếm mọi lần thử. Trả về list các lần thử (mong đợi rỗng)."""
    attempts = []

    def deny(kind):
        def _f(*a, **k):
            attempts.append((kind, repr(a[:2])))
            raise OSError(f"MẠNG BỊ VÔ HIỆU HOÁ TRONG TEST ({kind})")
        return _f
    monkeypatch.setattr(socket.socket, "connect", deny("socket.connect"))
    monkeypatch.setattr(socket, "getaddrinfo", deny("getaddrinfo"))
    monkeypatch.setattr(wu.requests, "get", deny("requests.get"))
    return attempts


@pytest.fixture(autouse=True)
def fast_retry(monkeypatch):
    """Không ngủ giữa các lần thử lại trong test."""
    monkeypatch.setattr(wu, "RETRY_SLEEP", 0)
    monkeypatch.setattr(wu.time, "sleep", lambda s: None)


# ----------------------------------------------------------------------------- dữ liệu giờ giả lập (khoảng ngắn, chạy nhanh)
T0, T1 = "2019-01-01", "2019-01-04"                              # 4 ngày = 96 giờ


def synth_hourly(start=T0, end=T1, seed=0):
    grid = pd.date_range(start, pd.Timestamp(end) + pd.Timedelta(hours=23), freq="h")
    rng = np.random.default_rng(seed)
    n = len(grid)
    return pd.DataFrame({
        "time": grid.strftime("%Y-%m-%dT%H:%M"),
        "temperature_2m": np.round(20 + 5 * rng.standard_normal(n), 1),
        "relative_humidity_2m": rng.integers(20, 100, n),
        "surface_pressure": np.round(980 + rng.standard_normal(n), 1),
        "wind_speed_10m": np.round(np.abs(rng.standard_normal(n)) * 2, 2),
        "wind_direction_10m": rng.integers(1, 361, n),
        "precipitation": np.round(np.abs(rng.standard_normal(n)) * (rng.random(n) < 0.1), 1),
        "boundary_layer_height": rng.integers(2, 400, n) * 5.0,
        "grid_lat": 28.5, "grid_lon": 77.25, "grid_elev": 217.0,
    })


def write_cache(df, city, cache_dir):
    path = wu.cache_path(city, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, compression="gzip")
    return path


def api_payload(df, variables, **override):
    """Một phản hồi GIẢ theo đúng hình dạng JSON của Open-Meteo (dùng cho mock; không phải dữ liệu API thật)."""
    p = {"latitude": 28.5, "longitude": 77.25, "elevation": 217.0, "timezone": wu.TIMEZONE, "timezone_abbreviation": "GMT+5:30",
         "utc_offset_seconds": wu.UTC_OFFSET_SECONDS, "generationtime_ms": 1.0,
         "hourly_units": {"time": "iso8601", **{v: wu.HOURLY_UNITS[v] for v in variables}},
         "hourly": {"time": df["time"].tolist(), **{v: [None if pd.isna(x) else float(x) for x in df[v]] for v in variables}}}
    p.update(override)
    return p


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload, self.status_code, self.text = payload, status, str(payload)[:200]

    def json(self):
        return self._payload


@pytest.fixture
def mock_api(monkeypatch):
    """Thay `requests.get` bằng một API GIẢ và ghi lại mọi lời gọi. `mock_api.payload_for` có thể bị test ghi đè để trả dữ liệu sai."""
    class Mock:
        calls = []
        error = None

        @staticmethod
        def payload_for(params):
            variables = params["hourly"].split(",")
            return api_payload(synth_hourly(params["start_date"], params["end_date"], seed=7), variables)

    def fake_get(url, params=None, timeout=None):
        Mock.calls.append({"url": url, "params": dict(params)})
        if Mock.error is not None:
            raise Mock.error
        return FakeResponse(Mock.payload_for(params))
    Mock.calls, Mock.error = [], None
    monkeypatch.setattr(wu.requests, "get", fake_get)
    return Mock


@pytest.fixture(scope="session")
def hourly_real():
    """8 cache gốc đã commit, đọc ở chế độ offline (không chạm mạng)."""
    return wu.fetch_all(mode="offline")


@pytest.fixture(scope="session")
def daily_real(hourly_real):
    return wu.build_daily(hourly_real)


@pytest.fixture(scope="session")
def baseline_daily():
    return pd.read_csv(data_paths.BASELINE_WEATHER_DAILY, parse_dates=["Date"])


@pytest.fixture(scope="session")
def raw8():
    import forecast_utils as F
    return F.load_raw()


@pytest.fixture(scope="session")
def features_full(raw8, baseline_daily):
    import forecast_utils as F
    return F.make_forecast_features(raw8, baseline_daily)


@pytest.fixture(scope="session")
def ds_new(raw8, baseline_daily):
    import forecast_utils as F
    return F.build_forecast_dataset(raw8, baseline_daily, verbose=False)


@pytest.fixture(scope="session")
def ds_old():
    import model_utils as M
    return M.build_dataset(verbose=False)


def evidence_dir():
    """Nếu đặt biến môi trường AIR_TEST_EVIDENCE_DIR thì một số test ghi thêm bảng bằng chứng (CSV) ra thư mục đó."""
    d = os.environ.get("AIR_TEST_EVIDENCE_DIR")
    if not d:
        return None
    p = Path(d)
    p.mkdir(parents=True, exist_ok=True)
    return p
