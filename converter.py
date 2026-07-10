from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, List

from PIL import Image, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff"}
ProgressCallback = Callable[[int, int, str], None]


def _normalize_folder_path(path: str | os.PathLike[str]) -> str:
    return str(Path(path)).replace("\\", "/")


def discover_image_files(root: str | os.PathLike[str]) -> List[Path]:
    root_path = Path(root)
    if not root_path.exists():
        return []

    discovered: List[Path] = []
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            discovered.append(path)

    return sorted(discovered)


def summarize_image_counts_by_folder(root: str | os.PathLike[str]) -> List[Dict[str, Any]]:
    root_path = Path(root)
    if not root_path.exists():
        return []

    folders: Dict[Path, int] = {}
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            folders[path.parent] = folders.get(path.parent, 0) + 1

    summaries = [{"folder": str(folder), "count": count} for folder, count in sorted(folders.items(), key=lambda item: str(item[0]))]
    return summaries


def summarize_folder_status(root: str | os.PathLike[str]) -> List[Dict[str, Any]]:
    root_path = Path(root)
    summaries = summarize_image_counts_by_folder(root_path)
    folder_sizes: Dict[Path, int] = {}
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            folder_sizes[path.parent] = folder_sizes.get(path.parent, 0) + path.stat().st_size

    return [{
        "folder": item["folder"],
        "count": item["count"],
        "status": "pending",
        "converted": 0,
        "skipped": 0,
        "saved_bytes": 0,
        "size_before_bytes": folder_sizes.get(Path(item["folder"]), 0),
        "size_after_bytes": 0,
        "savings_percent": 0,
        "progress": 0,
    } for item in summaries]


def build_folder_progress_summary(
    root: str | os.PathLike[str],
    processed_paths: List[Path],
    completed_paths: List[Path],
) -> List[Dict[str, Any]]:
    root_path = Path(root)
    summaries = summarize_folder_status(root_path)
    folder_map = {item["folder"]: item for item in summaries}

    for source_path in processed_paths:
        folder = str(source_path.parent)
        item = folder_map.get(folder)
        if item is None:
            continue
        item["progress"] = int(round((item.get("converted", 0) + item.get("skipped", 0)) / item["count"] * 100)) if item["count"] else 100

    for source_path in completed_paths:
        folder = str(source_path.parent)
        item = folder_map.get(folder)
        if item is None:
            continue
        output_path = source_path.parent / "Converted.webp" / f"{source_path.stem}.webp"
        if output_path.exists():
            item["converted"] += 1
            output_size = output_path.stat().st_size
            item["size_after_bytes"] += output_size
            item["saved_bytes"] += max(source_path.stat().st_size - output_size, 0)
        else:
            item["converted"] += 1
        item["progress"] = int(round((item.get("converted", 0) + item.get("skipped", 0)) / item["count"] * 100)) if item["count"] else 100
        if item.get("size_before_bytes", 0) > 0:
            item["savings_percent"] = int(round((item.get("saved_bytes", 0) / item["size_before_bytes"]) * 100)) if item["size_before_bytes"] else 0
            item["savings_percent"] = max(0, min(100, item["savings_percent"]))

    return list(folder_map.values())


def update_folder_statuses(statuses: List[Dict[str, Any]], folder: str, status: str) -> List[Dict[str, Any]]:
    normalized_folder = _normalize_folder_path(folder)
    updated = [dict(item) for item in statuses]
    for item in updated:
        if _normalize_folder_path(item.get("folder", "")) == normalized_folder:
            item["status"] = status
            break
    return updated


def convert_tree(
    root: str | os.PathLike[str],
    quality: int = 85,
    on_progress: ProgressCallback | None = None,
) -> Dict[str, Any]:
    root_path = Path(root)
    discovered_files = discover_image_files(root_path)
    results: Dict[str, Any] = {
        "root": str(root_path),
        "converted_count": 0,
        "skipped_count": 0,
        "files": [],
    }
    processed_paths: List[Path] = []
    completed_paths: List[Path] = []

    for index, source_path in enumerate(discovered_files, start=1):
        if source_path.name.lower().startswith("converted") or source_path.suffix.lower() == ".webp":
            continue

        output_path = source_path.with_suffix(".webp")

        try:
            with Image.open(source_path) as img:
                img.load()
                if img.mode in {"RGBA", "LA", "P"}:
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
                img.save(output_path, "WEBP", quality=quality)
        except (UnidentifiedImageError, OSError, ValueError):
            results["skipped_count"] += 1
            results["files"].append({"path": str(source_path), "status": "failed"})
        else:
            source_path.unlink(missing_ok=True)
            results["converted_count"] += 1
            results["files"].append({"path": str(source_path), "status": "converted", "output": str(output_path)})

        processed_paths.append(source_path)
        completed_paths.append(source_path)

        if on_progress is not None:
            on_progress(index, len(discovered_files), str(source_path))

    results["folder_progress"] = build_folder_progress_summary(root_path, processed_paths, completed_paths)
    return results
