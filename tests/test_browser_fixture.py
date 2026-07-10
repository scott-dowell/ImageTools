from pathlib import Path

from scripts.prepare_test_images import prepare_copy


def test_prepare_copy_creates_a_fresh_fixture_directory(tmp_path: Path) -> None:
    fixture_root = prepare_copy()

    assert fixture_root.exists()
    assert fixture_root.is_dir()
    assert (fixture_root / "AmourAngels - Red Angel - Ethereal Beauty").exists()
    assert len(list((fixture_root / "AmourAngels - Red Angel - Ethereal Beauty").glob("*.jpg"))) == 10
