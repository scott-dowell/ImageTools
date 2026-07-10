from pathlib import Path

from scripts.prepare_test_images import prepare_copy


def test_prepare_copy_creates_a_fresh_fixture_directory(tmp_path: Path) -> None:
    fixture_root = prepare_copy()

    assert fixture_root.exists()
    assert fixture_root.is_dir()
    assert (fixture_root / "Test Images 1").exists()
    assert (fixture_root / "Test Images 2").exists()
    assert (fixture_root / "Test Images 3").exists()
    assert (fixture_root / "Test Images 4").exists()
    assert len(list((fixture_root / "Test Images 1").glob("*.jpg"))) == 10
    assert len(list((fixture_root / "Test Images 2").glob("*.jpg"))) == 20
    assert len(list((fixture_root / "Test Images 3").glob("*.jpg"))) == 5
    assert len(list((fixture_root / "Test Images 4").glob("*.jpg"))) == 30
