"""DEV-01 / F02 - luồng thời tiết đọc cache trước, offline rõ ràng, online chỉ tải phần thiếu (kiểm bằng API GIẢ).

Các test "online" ở đây dùng `mock_api`: chúng kiểm logic của mã, KHÔNG phải kiểm API Open-Meteo thật.
Test duy nhất gọi API thật là `test_real_api_smoke` (đánh dấu `network`); nó tự bỏ qua khi môi trường chặn mạng.
"""
import gzip
import json

import numpy as np
import pandas as pd
import pytest
import requests

import data_paths
import weather_utils as wu
from conftest import T0, T1, synth_hourly, write_cache, api_payload

CITIES2 = ["Delhi", "Jaipur"]
KW = dict(start=T0, end=T1)


def _dirs(tmp_path):
    cache, dl = tmp_path / "cache", tmp_path / "downloads"
    cache.mkdir(); dl.mkdir()
    return cache, dl


def _snapshot(d):
    return {p.name: data_paths.sha256_file(p) for p in sorted(d.iterdir())}


# ----------------------------------------------------------------------------- cache gốc thật + mạng bị vô hiệu hoá
def test_full_cache_offline_makes_no_network_call(no_network, hourly_real):
    """8 cache gốc hợp lệ => đọc lại hết, không một lần thử mạng nào (kể cả tra DNS), và có lớp biên khí quyển."""
    before = wu.N_API_CALLS
    hourly = wu.fetch_all(mode="offline")
    assert list(hourly) == wu.CITIES
    assert all(len(h) == 48384 for h in hourly.values())
    assert all("boundary_layer_height" in h.columns and h["boundary_layer_height"].notna().all() for h in hourly.values())
    assert all(h.attrs["from_cache"] and h.attrs["source"] == "cache gốc" for h in hourly.values())
    assert wu.N_API_CALLS == before and no_network == []


def test_default_mode_is_offline(monkeypatch):
    monkeypatch.delenv(data_paths.ENV_MODE, raising=False)
    assert wu.network_mode() == "offline"
    monkeypatch.setenv(data_paths.ENV_MODE, "online")
    assert wu.network_mode() == "online"
    with pytest.raises(ValueError):
        wu.network_mode("tu-dong")


def test_cache_status_is_read_only_and_offline(no_network):
    st = wu.cache_status()
    assert st["hop_le"].all() and st["co_BLH"].all() and (st["nguon"] == "cache gốc").all()
    assert (st["so_dong"] == 48384).all() and (st[["gio_trung", "gio_thieu", "o_trong"]] == 0).all().all()
    assert no_network == []


def test_offline_blocks_smoke_test_and_probe(no_network):
    """Offline thì hai hàm thử API cũ cũng không được chạm mạng; và probe không được trả False giả."""
    before = wu.N_API_CALLS
    with pytest.raises(wu.WeatherOfflineError):
        wu.smoke_test()
    with pytest.raises(wu.WeatherOfflineError):
        wu.probe_variable("boundary_layer_height")
    assert wu.N_API_CALLS == before and no_network == []


# ----------------------------------------------------------------------------- cache thiếu / hỏng ở chế độ offline
def test_missing_one_cache_offline_fails_clearly(tmp_path, no_network):
    cache, dl = _dirs(tmp_path)
    write_cache(synth_hourly(), "Delhi", cache)                               # Jaipur không có file
    with pytest.raises(wu.WeatherCacheError) as e:
        wu.fetch_all(cities=CITIES2, mode="offline", cache_dir=cache, download_dir=dl, **KW)
    msg = str(e.value)
    assert "Jaipur" in msg and "openmeteo_jaipur_hourly.csv.gz" in msg and "không có file" in msg
    assert "Delhi," not in msg                                                # thành phố hợp lệ không bị nêu là lỗi
    assert "boundary_layer_height" in msg and data_paths.ENV_MODE in msg      # nêu biến bắt buộc và cách bật online
    assert no_network == [] and list(dl.iterdir()) == []                      # không gọi mạng, không tạo file nào


def test_offline_failure_lists_every_bad_city(tmp_path, no_network):
    cache, dl = _dirs(tmp_path)
    write_cache(synth_hourly().drop(columns="boundary_layer_height"), "Delhi", cache)
    with pytest.raises(wu.WeatherCacheError) as e:
        wu.fetch_all(cities=CITIES2, mode="offline", cache_dir=cache, download_dir=dl, **KW)
    assert "Delhi" in str(e.value) and "Jaipur" in str(e.value)


@pytest.mark.parametrize("case, expect", [
    ("no_blh", "thiếu cột: boundary_layer_height"),
    ("dup_hour", "1 giờ bị trùng"),
    ("missing_hours", "thiếu 3 giờ"),
    ("nan_value", "biến `surface_pressure` có 2 ô trống"),
    ("short_range", "thiếu 24 giờ"),
    ("bad_time", "cột time không đọc được"),
    ("off_grid", "không nằm trên lưới giờ"),
    ("unsorted", "cột time không tăng dần"),
    ("text_value", "biến `temperature_2m` không phải kiểu số"),
    ("no_grid", "thiếu cột: grid_lat"),
])
def test_invalid_cache_is_rejected_with_reason(tmp_path, no_network, case, expect):
    cache, dl = _dirs(tmp_path)
    h = synth_hourly()
    if case == "no_blh":
        h = h.drop(columns="boundary_layer_height")
    elif case == "dup_hour":
        h = pd.concat([h, h.iloc[[10]]]).sort_values("time", kind="stable").reset_index(drop=True)
    elif case == "missing_hours":
        h = h.drop(index=[20, 21, 50]).reset_index(drop=True)
    elif case == "nan_value":
        h.loc[[5, 6], "surface_pressure"] = np.nan
    elif case == "short_range":
        h = h.iloc[:-24]
    elif case == "bad_time":
        h.loc[3, "time"] = "hong"
    elif case == "off_grid":
        h.loc[3, "time"] = "2019-01-01T03:30"
    elif case == "unsorted":
        h = h.iloc[::-1].reset_index(drop=True)
    elif case == "text_value":
        h["temperature_2m"] = h["temperature_2m"].astype(object)
        h.loc[3, "temperature_2m"] = "abc"
    elif case == "no_grid":
        h = h.drop(columns="grid_lat")
    path = write_cache(h, "Delhi", cache)
    sha = data_paths.sha256_file(path)
    rep = wu.validate_cache("Delhi", path, **KW)
    assert not rep["ok"] and any(expect in p for p in rep["problems"]), rep["problems"]
    with pytest.raises(wu.WeatherCacheError) as e:
        wu.fetch_city("Delhi", mode="offline", cache_dir=cache, download_dir=dl, **KW)
    assert "Delhi" in str(e.value) and path.name in str(e.value) and expect in str(e.value)
    assert data_paths.sha256_file(path) == sha and no_network == [] and list(dl.iterdir()) == []


def test_corrupt_gzip_is_reported_not_raised(tmp_path, no_network):
    cache, dl = _dirs(tmp_path)
    path = write_cache(synth_hourly(), "Delhi", cache)
    path.write_bytes(path.read_bytes()[:200])                                 # file bị cắt cụt
    rep = wu.validate_cache("Delhi", path, **KW)
    assert not rep["ok"] and "không đọc được file" in rep["problems"][0]
    with pytest.raises(wu.WeatherCacheError):
        wu.fetch_city("Delhi", mode="offline", cache_dir=cache, download_dir=dl, **KW)


def test_valid_cache_wider_than_range_is_sliced_exactly(tmp_path, no_network):
    cache, dl = _dirs(tmp_path)
    write_cache(synth_hourly("2018-12-30", "2019-01-06"), "Delhi", cache)
    h = wu.fetch_city("Delhi", mode="offline", cache_dir=cache, download_dir=dl, **KW)
    assert len(h) == 96 and h["time"].iloc[0] == "2019-01-01T00:00" and h["time"].iloc[-1] == "2019-01-04T23:00"
    assert wu.check_hourly(h, wu.REQUIRED_HOURLY, T0, T1)["so_dong"] == 96


def test_validate_hourly_counts_match_legacy_check(hourly_real):
    """Bộ kiểm mới và `check_hourly` cũ (notebook vẫn assert) cho cùng số liệu trên cache thật."""
    h = hourly_real["Delhi"]
    _, st, problems = wu.validate_hourly(h)
    old = wu.check_hourly(h, wu.REQUIRED_HOURLY)
    assert problems == [] and (st["so_dong"], st["mong_doi"], st["gio_trung"], st["o_trong"]) == (old["so_dong"], old["mong_doi"], old["gio_trung"], old["o_trong"])
    assert (st["dau"], st["cuoi"]) == (old["dau"], old["cuoi"]) == ("2014-12-25 00:00", "2020-07-01 23:00")


# ----------------------------------------------------------------------------- online qua API GIẢ (mock)
def test_online_mock_downloads_only_the_missing_city(tmp_path, mock_api):
    cache, dl = _dirs(tmp_path)
    write_cache(synth_hourly(), "Delhi", cache)
    before = _snapshot(cache)
    hourly = wu.fetch_all(cities=CITIES2, mode="online", cache_dir=cache, download_dir=dl, pause=0, **KW)
    assert len(mock_api.calls) == 1                                           # chỉ một lời gọi, cho đúng thành phố thiếu
    p = mock_api.calls[0]["params"]
    assert (p["latitude"], p["longitude"]) == wu.CITY_COORDS["Jaipur"] and p["timezone"] == "Asia/Kolkata"
    assert p["wind_speed_unit"] == "ms" and p["models"] == "era5" and p["hourly"].split(",") == wu.REQUIRED_HOURLY
    assert (p["start_date"], p["end_date"]) == (T0, T1)
    assert hourly["Delhi"].attrs["source"] == "cache gốc" and hourly["Jaipur"].attrs["source"] == "API (vừa tải)"
    assert _snapshot(cache) == before                                         # thư mục cache gốc không đổi, không thêm file
    saved = wu.download_path("Jaipur", dl)
    assert saved.is_file() and len(pd.read_csv(saved)) == 96
    meta = json.loads((dl / (saved.name + ".provenance.json")).read_text(encoding="utf-8"))
    assert meta["city"] == "Jaipur" and meta["sha256"] == data_paths.sha256_file(saved)
    assert meta["response"]["timezone"] == "Asia/Kolkata" and meta["response"]["hourly_units"]["wind_speed_10m"] == "m/s"
    assert meta["params"]["models"] == "era5"
    # lần chạy sau: đọc lại bản tải mới, không gọi API nữa, kể cả khi offline
    again = wu.fetch_all(cities=CITIES2, mode="offline", cache_dir=cache, download_dir=dl, **KW)
    assert len(mock_api.calls) == 1 and again["Jaipur"].attrs["source"] == "bản tải mới"
    pd.testing.assert_frame_equal(again["Jaipur"], hourly["Jaipur"])


def test_online_mock_never_overwrites_an_invalid_original(tmp_path, mock_api):
    cache, dl = _dirs(tmp_path)
    bad = write_cache(synth_hourly().drop(columns="boundary_layer_height"), "Delhi", cache)
    sha_bad = data_paths.sha256_file(bad)
    h = wu.fetch_city("Delhi", mode="online", cache_dir=cache, download_dir=dl, **KW)
    assert "boundary_layer_height" in h.columns and len(mock_api.calls) == 1
    assert data_paths.sha256_file(bad) == sha_bad and [p.name for p in cache.iterdir()] == [bad.name]
    assert wu.download_path("Delhi", dl).is_file()


def test_online_mock_refuses_to_overwrite_an_invalid_earlier_download(tmp_path, mock_api):
    cache, dl = _dirs(tmp_path)
    stale = wu.download_path("Delhi", dl)
    synth_hourly().iloc[:-5].to_csv(stale, index=False, compression="gzip")
    sha = data_paths.sha256_file(stale)
    with pytest.raises(wu.WeatherCacheError) as e:
        wu.fetch_city("Delhi", mode="online", cache_dir=cache, download_dir=dl, **KW)
    assert "sẽ không bị ghi đè" in str(e.value) and stale.name in str(e.value)
    assert data_paths.sha256_file(stale) == sha and mock_api.calls == []


def test_online_network_error_names_city_file_and_variables(tmp_path, mock_api):
    cache, dl = _dirs(tmp_path)
    mock_api.error = requests.ConnectionError("SSL_ERROR_SYSCALL (giả lập)")
    with pytest.raises(wu.WeatherDownloadError) as e:
        wu.fetch_city("Jaipur", mode="online", cache_dir=cache, download_dir=dl, **KW)
    msg = str(e.value)
    assert "Jaipur" in msg and "openmeteo_jaipur_hourly.csv.gz" in msg
    assert all(v in msg for v in wu.REQUIRED_HOURLY) and "ConnectionError" in msg and f"{T0} -> {T1}" in msg
    assert len(mock_api.calls) == 5 and list(dl.iterdir()) == []              # thử lại đủ 5 lần rồi mới bỏ; không tạo file


@pytest.mark.parametrize("case, expect", [
    ("wrong_unit", "Biến `wind_speed_10m`: API trả đơn vị 'km/h', mong đợi 'm/s'"),
    ("wrong_tz", "API trả múi giờ 'GMT'"),
    ("blh_all_null", "API trả toàn giá trị rỗng cho biến `boundary_layer_height`"),
    ("blh_absent", "API không trả biến `boundary_layer_height`"),
    ("no_units", "không xác nhận được đơn vị"),
    ("hole", "không qua kiểm tra nên không lưu"),
])
def test_online_mock_bad_response_is_rejected_and_not_saved(tmp_path, mock_api, case, expect):
    cache, dl = _dirs(tmp_path)

    def payload(params):
        variables = params["hourly"].split(",")
        df = synth_hourly(params["start_date"], params["end_date"])
        if case == "blh_all_null":
            df["boundary_layer_height"] = np.nan
        if case == "hole":
            df = df.drop(index=[30, 31]).reset_index(drop=True)
        p = api_payload(df, variables)
        if case == "wrong_unit":
            p["hourly_units"]["wind_speed_10m"] = "km/h"
        if case == "wrong_tz":
            p["timezone"], p["utc_offset_seconds"] = "GMT", 0
        if case == "blh_absent":
            del p["hourly"]["boundary_layer_height"]
        if case == "no_units":
            del p["hourly_units"]
        return p
    mock_api.payload_for = payload
    with pytest.raises(wu.WeatherDownloadError) as e:
        wu.fetch_city("Delhi", mode="online", cache_dir=cache, download_dir=dl, **KW)
    assert expect in str(e.value) and "Delhi" in str(e.value)
    assert list(dl.iterdir()) == [] and list(cache.iterdir()) == []


def test_probe_variable_does_not_turn_a_network_error_into_false(mock_api):
    """Lỗi cũ: probe trả False khi mạng lỗi, làm notebook lặng lẽ bỏ lớp biên. Giờ lỗi mạng phải nổi lên."""
    mock_api.error = requests.ConnectionError("giả lập")
    with pytest.raises(wu.WeatherDownloadError):
        wu.probe_variable("boundary_layer_height", mode="online")
    mock_api.error = None
    assert wu.probe_variable("boundary_layer_height", mode="online") is True


def test_smoke_test_online_mock_does_not_write(tmp_path, mock_api, monkeypatch):
    monkeypatch.setenv(data_paths.ENV_DOWNLOAD_DIR, str(tmp_path / "dl"))
    h = wu.smoke_test(mode="online")
    assert len(h) == 168 and not (tmp_path / "dl").exists()


@pytest.mark.network
def test_real_api_smoke():
    """Gọi API Open-Meteo THẬT (7 ngày của Delhi, không lưu). Bị chặn mạng thì SKIP: khi đó API thật CHƯA được kiểm."""
    try:
        h = wu.smoke_test(mode="online")
    except wu.WeatherDownloadError as e:
        pytest.skip(f"API thật không gọi được từ môi trường này, chưa kiểm được: {str(e)[-160:]}")
    assert len(h) == 168 and set(wu.HOURLY_CORE) <= set(h.columns)


# ----------------------------------------------------------------------------- nơi ghi output và nơi bước sau đọc
def test_save_outputs_refuses_the_baseline_tree(tmp_path, daily_real, monkeypatch):
    monkeypatch.delenv(data_paths.ENV_ALLOW_BASELINE, raising=False)
    merged = daily_real.head(5)
    sha = {p: data_paths.sha256_file(p) for p in (wu.BASELINE_DAILY, wu.BASELINE_MERGED)}
    with pytest.raises(PermissionError):
        wu.save_outputs(merged, daily_real, out_dir=wu.BASELINE_DAILY.parent)
    assert {p: data_paths.sha256_file(p) for p in sha} == sha
    p_merged, p_daily = wu.save_outputs(merged, daily_real, out_dir=tmp_path / "out")
    assert p_daily.is_file() and p_merged.is_file()
    man = json.loads((tmp_path / "out" / "nb04_manifest.json").read_text(encoding="utf-8"))
    assert {o["sha256"] for o in man["outputs"]} == {data_paths.sha256_file(p_daily), data_paths.sha256_file(p_merged)}
    assert man["mode"] == "offline" and man["python"].startswith("3.")


def test_default_output_dir_is_not_the_baseline(monkeypatch):
    monkeypatch.delenv(data_paths.ENV_NB04_OUT, raising=False)
    p_merged, p_daily = wu.output_paths()
    assert not data_paths.in_baseline_tree(p_daily) and not data_paths.in_baseline_tree(p_merged)
    assert p_daily != wu.BASELINE_DAILY and p_daily.name == wu.BASELINE_DAILY.name


def test_weather_daily_path_never_falls_back_silently(tmp_path, monkeypatch):
    monkeypatch.delenv(data_paths.ENV_WEATHER_DAILY, raising=False)
    assert data_paths.weather_daily_path() == data_paths.BASELINE_WEATHER_DAILY
    monkeypatch.setenv(data_paths.ENV_WEATHER_DAILY, str(tmp_path / "khong_co.csv"))
    with pytest.raises(FileNotFoundError):
        data_paths.weather_daily_path()
    f = tmp_path / "moi.csv"
    f.write_text("City,Date\n", encoding="utf-8")
    monkeypatch.setenv(data_paths.ENV_WEATHER_DAILY, str(f))
    assert data_paths.weather_daily_path() == f.resolve()


def test_record_input_reports_path_hash_and_kind(tmp_path, monkeypatch, capsys):
    log = tmp_path / "prov.jsonl"
    monkeypatch.setenv(data_paths.ENV_PROV_LOG, str(log))
    monkeypatch.setenv(data_paths.ENV_RUN_LABEL, "thu")
    data_paths._seen.clear()
    rec = data_paths.record_input("thời tiết theo ngày", data_paths.BASELINE_WEATHER_DAILY)
    out = capsys.readouterr().out
    assert rec["kind"] == "baseline đã commit" and rec["sha256"][:16] in out and "weather_daily_8cities.csv" in out
    f = tmp_path / "moi.csv"
    f.write_text("x\n", encoding="utf-8")
    assert data_paths.record_input("thời tiết theo ngày", f)["kind"].startswith("KHÔNG phải baseline")
    lines = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()]
    assert [x["run"] for x in lines] == ["thu", "thu"] and lines[0]["sha256"] == rec["sha256"]


def test_downloaded_file_is_plain_gzip_csv(tmp_path, mock_api):
    cache, dl = _dirs(tmp_path)
    wu.fetch_city("Delhi", mode="online", cache_dir=cache, download_dir=dl, **KW)
    with gzip.open(wu.download_path("Delhi", dl), "rt", encoding="utf-8") as f:
        assert f.readline().strip().split(",") == ["time"] + wu.REQUIRED_HOURLY + wu.PROVENANCE_COLS
