from pathlib import Path

from scripts.prepare_test_images import DEST_ROOT, SOURCE_ROOT, prepare_copy


def test_prepare_copy_creates_a_fresh_fixture_directory(prepared_fixture_root: Path) -> None:
    fixture_root = prepared_fixture_root

    assert fixture_root.exists()
    assert fixture_root.is_dir()
    assert fixture_root == DEST_ROOT
    assert SOURCE_ROOT.exists()
    assert (fixture_root / "Test Images 1").exists()
    assert (fixture_root / "Test Images 2").exists()
    assert (fixture_root / "Test Images 3").exists()
    assert (fixture_root / "Test Images 4").exists()

    for relative_path in [
        Path("Test Images 1"),
        Path("Test Images 2"),
        Path("Test Images 3"),
        Path("Test Images 4"),
    ]:
        source_files = sorted((SOURCE_ROOT / relative_path).glob("*"))
        copied_files = sorted((fixture_root / relative_path).glob("*"))
        assert len(copied_files) == len(source_files)
        assert [path.name for path in copied_files] == [path.name for path in source_files]


def test_prepare_copy_rebuilds_fixture_after_previous_conversion(prepared_fixture_root: Path) -> None:
    fixture_root = prepared_fixture_root
    marker_path = fixture_root / "Test Images 1" / "converted.webp"
    marker_path.write_bytes(b"stale")

    rebuilt_root = prepare_copy()

    assert rebuilt_root == fixture_root
    assert marker_path.exists() is False
    assert any(path.name.startswith("AmourAngels") for path in (fixture_root / "Test Images 1").iterdir())
