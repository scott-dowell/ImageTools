from pathlib import Path

from PIL import Image

from converter import convert_tree, discover_image_files


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
