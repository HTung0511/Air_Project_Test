"""`data_paths.SnapshotChecks`: con số thực nghiệm của notebook gắn với một snapshot đầu vào (RA-DEC-02 mục 5).

Điều phải đúng: (1) đầu vào đúng snapshot mà con số lệch thì LUÔN thành lỗi, không có đường nào lặng lẽ cho qua;
(2) đầu vào khác snapshot thì chỗ lệch được ghi lại và in ra, không dừng, và không được tính là "khớp";
(3) mọi con số đã đối chiếu đều nằm trong bảng `table()`, kể cả con số khớp.
"""
import json

import numpy as np
import pandas as pd
import pytest

import data_paths as D

SNAP = {"raw": "aaa", "thời tiết": "bbb"}


def test_on_snapshot_a_deviation_raises_immediately():
    c = D.SnapshotChecks(SNAP, dict(SNAP), "P")
    assert c.on_snapshot and c.expect(True, "đúng") is True
    with pytest.raises(AssertionError, match="số mẫu = 5"):
        c.expect(False, "số mẫu = 5")
    assert (c.n_checked, c.n_strict) == (2, 2) and not c.deviations


def test_off_snapshot_a_deviation_is_recorded_and_printed_not_raised(capsys):
    c = D.SnapshotChecks(SNAP, {"raw": "aaa", "thời tiết": "KHÁC"}, "P")
    assert not c.on_snapshot and c.matches == {"raw": True, "thời tiết": False}
    assert c.expect(False, "MAE = 19,5") is False                       # trả False: không được tính là khớp
    assert c.deviations == ["MAE = 19,5"] and "LỆCH" in capsys.readouterr().out
    assert c.n_strict == 0 and not c.table()["khớp"].iloc[0]
    assert "1 chỗ lệch được ghi lại" in c.finish()                      # finish không báo lỗi: không có chỗ lệch bắt buộc khớp


def test_needs_limits_strictness_to_the_inputs_a_number_depends_on():
    c = D.SnapshotChecks(SNAP, {"raw": "aaa", "thời tiết": "KHÁC"}, "P")
    with pytest.raises(AssertionError):                                 # số mẫu chỉ phụ thuộc raw, raw đúng snapshot -> bắt buộc khớp
        c.expect(False, "số mẫu", needs=["raw"])
    assert c.expect(False, "MAE", needs=["raw", "thời tiết"]) is False   # phụ thuộc cả thời tiết -> chỉ ghi lại
    with pytest.raises(KeyError):                                       # gõ nhầm tên đầu vào không được lặng lẽ thành "không bắt buộc"
        c.expect(False, "x", needs=["rawww"])


def test_expect_values_checks_everything_then_reports_all_deviations():
    c = D.SnapshotChecks(SNAP, dict(SNAP), "P")
    items = [("a", 1.04, 1.0, 0.05), ("b", 1.06, 1.0, 0.05), ("c", 3, 3, None), ("d", 3, 4, None), ("e", float("nan"), 1.0, 0.1),
             ("f", np.float64(2.0), 2.0, None), ("g", np.int64(7), 7, None)]
    with pytest.raises(AssertionError) as e:
        c.expect_values(items)
    msg = str(e.value)
    assert msg.startswith("3 con số") and all(k in msg for k in ("b: đo được 1.0600", "d: đo được 3", "e: đo được nan"))
    assert "a:" not in msg and "c:" not in msg                          # con số khớp không bị báo
    t = c.table()
    assert list(t["con số"]) == list("abcdefg") and list(t["khớp"]) == [True, False, True, False, False, True, True]
    assert c.n_checked == 7 and c.n_strict == 7


def test_expect_values_off_snapshot_records_each_deviation():
    c = D.SnapshotChecks(SNAP, {"raw": "x", "thời tiết": "bbb"}, "P")
    assert c.expect_values([("a", 1.0, 1.0, 0.0), ("b", 2.0, 1.0, 0.5)]) is False
    assert len(c.deviations) == 1 and c.deviations[0].startswith("b: đo được 2.0000")
    assert c.expect_values([("a", 1.0, 1.0, 0.0)]) is True and c.expect_values([]) is True


def test_deferred_mode_still_fails_at_finish_and_keeps_the_full_table(capsys):
    """`defer=True` chỉ HOÃN lỗi để kịp lưu bảng số; `finish()` vẫn báo AssertionError với đủ danh sách."""
    c = D.SnapshotChecks(SNAP, dict(SNAP), "P", defer=True)
    assert c.expect(False, "điều kiện sai") is False
    assert c.expect_values([("a", 1.0, 1.0, 0.0), ("b", 9, 8, None)]) is False
    out = capsys.readouterr().out
    assert out.count("sẽ báo lỗi ở finish()") == 2 and not c.finished
    assert len(c.table()) == 3 and c.failures == ["điều kiện sai", "b: đo được 9, giá trị của snapshot 8"]
    with pytest.raises(AssertionError, match="2 con số thực nghiệm lệch"):
        c.finish()
    assert c.finished


def test_deferred_mode_passes_cleanly_when_everything_matches():
    c = D.SnapshotChecks(SNAP, dict(SNAP), "P", defer=True)
    assert c.expect(True, "x") and c.expect_values([("a", 1.0, 1.0, 0.0)])
    s = c.finish()
    assert s.startswith("2 con số thực nghiệm đã đối chiếu, 2 ở chế độ bắt buộc khớp; 0 chỗ lệch") and c.finished and not c.failures


def test_missing_actual_hash_is_off_snapshot_not_a_match():
    c = D.SnapshotChecks(SNAP, {"raw": "aaa"}, "P")                     # thiếu sha của một đầu vào: KHÔNG được coi là trùng
    assert c.matches == {"raw": True, "thời tiết": False} and not c.on_snapshot


def test_save_json_and_table_write_outside_the_baseline_tree_only(tmp_path, capsys):
    obj = {"a": np.float64(1.5), "b": np.arange(3), "c": pd.Timestamp("2020-01-02"), "d": np.int64(3), "e": np.bool_(True),
           "f": float("nan"), "g": {("x", 1): np.array([1.0, np.nan])}, "h": None, "i": float("inf")}
    rec = D.save_json(obj, tmp_path / "sub" / "x.json", "thử")
    back = json.loads((tmp_path / "sub" / "x.json").read_text(encoding="utf-8"))   # JSON chuẩn: NaN/inf thành null, khoá thành chuỗi
    assert back == {"a": 1.5, "b": [0, 1, 2], "c": "2020-01-02T00:00:00", "d": 3, "e": True, "f": None, "g": {"('x', 1)": [1.0, None]},
                    "h": None, "i": None}
    assert rec["sha256"] == D.sha256_file(tmp_path / "sub" / "x.json") and "[ghi] thử" in capsys.readouterr().out
    D.save_table(pd.DataFrame({"k": [1, 2]}), tmp_path / "t.csv", "bảng", index=False)
    assert (tmp_path / "t.csv").read_text(encoding="utf-8").splitlines() == ["k", "1", "2"]
    for target in (D.ROOT / "data" / "processed" / "x.json", D.ROOT / "data" / "raw" / "x.csv"):
        with pytest.raises(PermissionError):
            D.save_json({}, target, "thử")
        with pytest.raises(PermissionError):
            D.save_table(pd.DataFrame(), target, "thử")
        assert not target.exists()


def test_nb06_output_dir_default_and_override(tmp_path, monkeypatch):
    assert D.nb06_out_dir() == D.ROOT / "outputs" / "nb06"
    monkeypatch.setenv(D.ENV_NB06_OUT, str(tmp_path / "o"))
    assert D.nb06_out_dir() == tmp_path / "o"


# ----------------------------------------------------------------------------- "đã commit" xét theo NỘI DUNG, không chỉ theo vị trí
def test_committed_sha256_registry_matches_the_files_in_the_repo():
    """Bảng sha256 trong `data_paths` phải đúng là các file raw/cache/baseline đang có trong repo (và phủ đủ 8 file cache thời tiết)."""
    for rel, sha in D.COMMITTED_SHA256.items():
        assert (D.ROOT / rel).is_file(), rel
        assert D.sha256_file(D.ROOT / rel) == sha, f"{rel}: file trong repo khác sha256 đã ghi trong data_paths.COMMITTED_SHA256"
    caches = {p.relative_to(D.ROOT).as_posix() for p in D.WEATHER_CACHE_DIR.glob("*.csv.gz")}
    assert len(caches) == 8 and caches <= set(D.COMMITTED_SHA256)
    for p in (D.RAW_FILE, D.BASELINE_CLEAN, D.BASELINE_WEATHER_DAILY, D.BASELINE_MERGED):
        assert p.relative_to(D.ROOT).as_posix() in D.COMMITTED_SHA256


def test_kind_of_a_file_depends_on_content_not_only_on_location(tmp_path, monkeypatch):
    assert D._kind_of(D.RAW_FILE) == D.KIND_RAW and D._kind_of(D.BASELINE_CLEAN) == D.KIND_BASELINE
    assert D._kind_of(sorted(D.WEATHER_CACHE_DIR.glob("*.csv.gz"))[0]) == D.KIND_RAW
    f = tmp_path / "weather_daily_8cities.csv"
    f.write_text("x\n", encoding="utf-8")
    assert D._kind_of(f) == D.KIND_OTHER                                # cùng tên nhưng ở nơi khác: không phải baseline
    # cùng VỊ TRÍ baseline nhưng nội dung không còn là bản đã commit (giả lập bằng cách đổi sha256 mong đợi): phải nói rõ là đã khác
    rel = D.BASELINE_CLEAN.relative_to(D.ROOT).as_posix()
    monkeypatch.setitem(D.COMMITTED_SHA256, rel, "0" * 64)
    assert D._kind_of(D.BASELINE_CLEAN) == D.KIND_CHANGED
    D._seen.clear()
    rec = D.record_input("bảng chất lượng không khí đã làm sạch", D.BASELINE_CLEAN, quiet=True)
    assert rec["kind"] == D.KIND_CHANGED and rec["sha256"] == D.sha256_file(D.BASELINE_CLEAN)
