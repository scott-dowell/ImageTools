from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, List

from PIL import Image, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff"}
ProgressCallback = Callable[[int, int, str, Dict[str, Any] | None], str | None]


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
    processed_paths: List[Path] | None = None,
    completed_paths: List[Path] | None = None,
    conversion_results: List[Dict[str, Any]] | None = None,
    initial_folder_summaries: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    if conversion_results is None and processed_paths is not None and completed_paths is None and processed_paths and isinstance(processed_paths[0], dict):
        conversion_results = processed_paths
        processed_paths = []

    root_path = Path(root)
    summaries = [dict(item) for item in initial_folder_summaries] if initial_folder_summaries is not None else summarize_folder_status(root_path)
    folder_map = {item["folder"]: item for item in summaries}

    for item in summaries:
        item.setdefault("converted", 0)
        item.setdefault("skipped", 0)
        item.setdefault("saved_bytes", 0)
        item.setdefault("size_before_bytes", 0)
        item.setdefault("size_after_bytes", 0)
        item.setdefault("savings_percent", 0)
        item.setdefault("progress", 0)
        item.setdefault("size_before_bytes_for_percent", 0)

    if conversion_results:
        for result in conversion_results:
            source_path = Path(result.get("path", ""))
            if not source_path:
                continue
            folder = str(source_path.parent)
            item = folder_map.get(folder)
            if item is None:
                continue
            if result.get("status") == "converted":
                item["converted"] += 1
                if not item.get("size_before_bytes", 0):
                    item["size_before_bytes"] = int(result.get("size_before_bytes", 0) or 0)
                size_before_bytes = int(result.get("size_before_bytes", 0) or 0)
                item["size_before_bytes_for_percent"] = int(item.get("size_before_bytes_for_percent", 0) or 0) + size_before_bytes
                item["size_after_bytes"] += int(result.get("size_after_bytes", 0) or 0)
                item["saved_bytes"] += int(result.get("saved_bytes", 0) or 0)
            elif result.get("status") in {"failed", "skipped"}:
                item["skipped"] += 1
            item["progress"] = int(round((item.get("converted", 0) + item.get("skipped", 0)) / item["count"] * 100)) if item["count"] else 100
            percent_baseline = item.get("size_before_bytes_for_percent", 0) or item.get("size_before_bytes", 0)
            if percent_baseline > 0:
                item["savings_percent"] = int(round((item.get("saved_bytes", 0) / max(percent_baseline, 1)) * 100)) if percent_baseline else 0
                item["savings_percent"] = max(0, min(100, item["savings_percent"]))
    else:
        for source_path in completed_paths or []:
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
            percent_baseline = item.get("size_before_bytes_for_percent", 0) or item.get("size_before_bytes", 0)
            if percent_baseline > 0:
                item["savings_percent"] = int(round((item.get("saved_bytes", 0) / max(percent_baseline, 1)) * 100)) if percent_baseline else 0
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
    initial_folder_summaries = summarize_folder_status(root_path)
    results: Dict[str, Any] = {
        "root": str(root_path),
        "converted_count": 0,
        "skipped_count": 0,
        "files": [],
    }
    processed_paths: List[Path] = []
    completed_paths: List[Path] = []
    conversion_results: List[Dict[str, Any]] = []

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
            conversion_results.append({"path": str(source_path), "status": "failed"})
        else:
            size_before_bytes = source_path.stat().st_size
            source_path.unlink(missing_ok=True)
            output_size = output_path.stat().st_size
            saved_bytes = max(size_before_bytes - output_size, 0)
            results["converted_count"] += 1
            results["files"].append({
                "path": str(source_path),
                "status": "converted",
                "output": str(output_path),
                "size_before_bytes": size_before_bytes,
                "size_after_bytes": output_size,
                "saved_bytes": saved_bytes,
            })
            conversion_results.append({
                "path": str(source_path),
                "status": "converted",
                "size_before_bytes": size_before_bytes,
                "size_after_bytes": output_size,
                "saved_bytes": saved_bytes,
            })

        processed_paths.append(source_path)
        completed_paths.append(source_path)

        if on_progress is not None:
            sig = None
            try:
                sig = on_progress(index, len(discovered_files), str(source_path), conversion_results[-1])
            except TypeError:
                sig = on_progress(index, len(discovered_files), str(source_path))
            
            if sig == "stop":
                break

    results["folder_progress"] = build_folder_progress_summary(
        root_path,
        processed_paths,
        completed_paths,
        conversion_results=conversion_results,
        initial_folder_summaries=initial_folder_summaries,
    )
    return results
