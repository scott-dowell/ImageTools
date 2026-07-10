from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any

from PIL import Image, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}


def discover_image_files(root: str | os.PathLike[str]) -> List[Path]:
    root_path = Path(root)
    if not root_path.exists():
        return []

    discovered: List[Path] = []
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            discovered.append(path)

    return sorted(discovered)


def convert_tree(root: str | os.PathLike[str], quality: int = 85) -> Dict[str, Any]:
    root_path = Path(root)
    results: Dict[str, Any] = {
        "root": str(root_path),
        "converted_count": 0,
        "skipped_count": 0,
        "files": [],
    }

    for source_path in discover_image_files(root_path):
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
            continue

        results["converted_count"] += 1
        results["files"].append({"path": str(source_path), "status": "converted", "output": str(output_path)})

    return results
