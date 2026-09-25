# tests/test_background_service.py

import pytest
from PIL import Image

from app.services.background_service import (
    is_path_inside_directory,
    process_image,
    remove_background,
)


def test_is_path_inside_directory(tmp_path):
    allowed_dir = tmp_path / "original"
    allowed_dir.mkdir()
    safe = allowed_dir / "shirt.png"
    safe.write_bytes(b"x")
    assert is_path_inside_directory(safe, allowed_dir) is True
    assert is_path_inside_directory(tmp_path / "other.png", allowed_dir) is False


def test_remove_background_turns_black_to_white():
    img = Image.new("RGB", (2, 2), (0, 0, 0))
    img.putpixel((1, 1), (10, 20, 30))
    out = remove_background(img)
    assert out.getpixel((0, 0)) == (255, 255, 255)
    assert out.getpixel((1, 1)) == (10, 20, 30)


def test_process_image_writes_processed_file(image_dirs):
    source = image_dirs["original"] / "shirt.png"
    Image.new("RGB", (4, 4), (0, 0, 0)).save(source)

    out_path = process_image(source)

    assert out_path.is_file()
    assert out_path.parent == image_dirs["processed"].resolve()
    assert out_path.name.startswith("bg_removed_")
    with Image.open(out_path) as result:
        assert result.getpixel((0, 0)) == (255, 255, 255)


def test_process_image_rejects_path_outside_original(image_dirs, tmp_path):
    outside = tmp_path / "escape.png"
    Image.new("RGB", (2, 2), (0, 0, 0)).save(outside)

    with pytest.raises(ValueError, match="not inside the original"):
        process_image(outside)


def test_process_image_rejects_non_image(image_dirs):
    fake = image_dirs["original"] / "not-an-image.png"
    fake.write_bytes(b"this is not a png")

    with pytest.raises(ValueError, match="not a valid image"):
        process_image(fake)


def test_process_image_sanitizes_unsafe_stem(image_dirs):
    source = image_dirs["original"] / "weird name!!.png"
    Image.new("RGB", (2, 2), (0, 0, 0)).save(source)

    out_path = process_image(source)

    assert " " not in out_path.name
    assert "!" not in out_path.name
    assert out_path.name.startswith("bg_removed_")
