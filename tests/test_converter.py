from pathlib import Path

from PIL import Image

from converter import convert_tree, discover_image_files, summarize_image_counts_by_folder


def test_discover_and_convert_images(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    source_dir.mkdir()

    image_path = source_dir / "sample.png"
    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(image_path)

    discovered = discover_image_files(source_dir)
    assert len(discovered) == 1

    result = convert_tree(source_dir)

    assert result["converted_count"] == 1
    output_path = source_dir / "Converted.webp" / "sample.webp"
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_convert_tree_reports_progress(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    source_dir.mkdir()

    for name, color in (("one.png", (255, 0, 0)), ("two.jpg", (0, 255, 0))):
        image_path = source_dir / name
        Image.new("RGB", (64, 64), color=color).save(image_path)

    events = []

    def on_progress(processed: int, total: int, current_path: str) -> None:
        events.append((processed, total, current_path))

    result = convert_tree(source_dir, on_progress=on_progress)

    assert result["converted_count"] == 2
    assert len(events) >= 2
    assert events[0][0] == 1
    assert events[-1][0] == 2


def test_summarize_image_counts_by_folder(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    (source_dir / "first").mkdir(parents=True)
    (source_dir / "second").mkdir(parents=True)

    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(source_dir / "first" / "one.jpg")
    Image.new("RGB", (64, 64), color=(0, 255, 0)).save(source_dir / "first" / "two.png")
    Image.new("RGB", (64, 64), color=(0, 0, 255)).save(source_dir / "second" / "three.jpeg")

    summary = summarize_image_counts_by_folder(source_dir)

    assert summary == [
        {"folder": str(source_dir / "first"), "count": 2},
        {"folder": str(source_dir / "second"), "count": 1},
    ]


def test_summarize_image_counts_by_folder_returns_folder_rows_for_table(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    (source_dir / "nested").mkdir(parents=True)
    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(source_dir / "nested" / "one.jpg")

    summary = summarize_image_counts_by_folder(source_dir)

    assert summary[0]["folder"] == str(source_dir / "nested")
    assert summary[0]["count"] == 1
