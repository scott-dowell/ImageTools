from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, List

from PIL import Image, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}
ProgressCallback = Callable[[int, int, str], None]


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
    summaries = summarize_image_counts_by_folder(root)
    return [{"folder": item["folder"], "count": item["count"], "status": "pending"} for item in summaries]


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

    for index, source_path in enumerate(discovered_files, start=1):
        if source_path.name.lower().startswith("converted"):
            continue

        output_dir = source_path.parent / "Converted.webp"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{source_path.stem}.webp"

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
            results["converted_count"] += 1
            results["files"].append({"path": str(source_path), "status": "converted", "output": str(output_path)})

        if on_progress is not None:
            on_progress(index, len(discovered_files), str(source_path))

    return results
