from pathlib import Path

from PIL import Image

import app as app_module
from app import _update_folder_statuses_for_progress
from converter import (
    build_folder_progress_summary,
    convert_tree,
    discover_image_files,
    summarize_folder_status,
    summarize_image_counts_by_folder,
    update_folder_statuses,
)


def test_discover_and_convert_images(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    source_dir.mkdir()

    image_path = source_dir / "sample.png"
    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(image_path)

    discovered = discover_image_files(source_dir)
    assert len(discovered) == 1

    result = convert_tree(source_dir)

    assert result["converted_count"] == 1
    output_path = source_dir / "sample.webp"
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert not image_path.exists()


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


def test_summarize_folder_status_defaults_to_pending(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    (source_dir / "nested").mkdir(parents=True)
    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(source_dir / "nested" / "one.jpg")

    summary = summarize_folder_status(source_dir)

    assert summary[0]["folder"] == str(source_dir / "nested")
    assert summary[0]["status"] == "pending"


def test_summarize_folder_status_tracks_size_before_bytes(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    folder_dir = source_dir / "folder"
    folder_dir.mkdir(parents=True)

    source_path = folder_dir / "one.jpg"
    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(source_path)

    summary = summarize_folder_status(source_dir)

    assert summary[0]["folder"] == str(folder_dir)
    assert summary[0]["size_before_bytes"] == source_path.stat().st_size
    assert summary[0]["size_after_bytes"] == 0
    assert summary[0]["savings_percent"] == 0


def test_webp_files_are_skipped(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    source_dir.mkdir()

    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(source_dir / "sample.jpg")
    Image.new("RGB", (64, 64), color=(0, 255, 0)).save(source_dir / "existing.webp")

    discovered = discover_image_files(source_dir)
    assert [path.name for path in discovered] == ["sample.jpg"]

    result = convert_tree(source_dir)
    assert result["converted_count"] == 1
    assert (source_dir / "existing.webp").exists()
    assert (source_dir / "sample.webp").exists()


def test_update_folder_statuses_transitions_folder_states() -> None:
    statuses = [
        {"folder": "C:/one", "status": "pending"},
        {"folder": "C:/two", "status": "pending"},
    ]

    updated = update_folder_statuses(statuses, "C:/one", "converting")
    updated = update_folder_statuses(updated, "C:/one", "done")

    assert updated[0]["status"] == "done"
    assert updated[1]["status"] == "pending"


def test_update_folder_statuses_for_progress_marks_previous_folder_done() -> None:
    statuses = [
        {"folder": "/tmp/one", "count": 1, "status": "converting"},
        {"folder": "/tmp/two", "count": 1, "status": "pending"},
    ]

    updated, current_folder = _update_folder_statuses_for_progress(statuses, "/tmp/two/image.jpg", "/tmp/one")

    assert current_folder == app_module._normalize_folder_path("/tmp/two")
    assert updated[0]["status"] == "done"
    assert updated[1]["status"] == "converting"


def test_update_folder_statuses_for_progress_normalizes_dot_segments(tmp_path: Path) -> None:
    folder_dir = tmp_path / "images" / "folder"
    folder_dir.mkdir(parents=True)

    statuses = [{"folder": str(folder_dir), "status": "pending"}]
    current_path = folder_dir / "." / "image.jpg"

    updated, current_folder = _update_folder_statuses_for_progress(statuses, str(current_path), None)

    assert current_folder == app_module._normalize_folder_path(str(folder_dir))
    assert updated[0]["status"] == "converting"


def test_on_progress_accumulates_folder_totals_across_files(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    folder_dir = source_dir / "folder"
    folder_dir.mkdir(parents=True)

    first_path = folder_dir / "one.jpg"
    second_path = folder_dir / "two.jpg"
    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(first_path)
    Image.new("RGB", (64, 64), color=(0, 255, 0)).save(second_path)

    output_dir = folder_dir / "Converted.webp"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "one.webp").write_bytes(b"1234567890")
    (output_dir / "two.webp").write_bytes(b"12345678901234567890")

    app_module._run_state.update({
        "root": str(source_dir),
        "folders": [{"folder": str(folder_dir), "count": 2, "status": "pending", "converted": 0, "skipped": 0, "saved_bytes": 0, "progress": 0}],
        "processed_paths": [],
        "completed_paths": [],
        "current_file": "",
    })

    app_module._on_progress(1, 2, str(first_path))
    app_module._on_progress(2, 2, str(second_path))

    folder_state = next(item for item in app_module._run_state["folders"] if item["folder"] == str(folder_dir))
    assert folder_state["converted"] == 2
    assert folder_state["saved_bytes"] > 0
    assert folder_state["progress"] == 100


def test_build_folder_progress_summary_tracks_counts_and_saved_size(tmp_path: Path) -> None:
    source_dir = tmp_path / "images"
    folder_dir = source_dir / "folder"
    folder_dir.mkdir(parents=True)

    source_path = folder_dir / "one.jpg"
    Image.new("RGB", (64, 64), color=(255, 0, 0)).save(source_path)

    summary = build_folder_progress_summary(source_dir, [source_path], [source_path])

    assert summary[0]["folder"] == str(folder_dir)
    assert summary[0]["count"] == 1
    assert summary[0]["status"] == "pending"
    assert summary[0]["converted"] == 1
    assert summary[0]["skipped"] == 0
    assert summary[0]["saved_bytes"] == 0
    assert summary[0]["size_before_bytes"] == source_path.stat().st_size
    assert summary[0]["size_after_bytes"] == 0
    assert summary[0]["savings_percent"] == 0
    assert summary[0]["progress"] == 100
