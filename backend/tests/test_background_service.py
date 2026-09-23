# tests/test_background_service.py


from PIL import Image

from app.services.background_service import (
    is_path_inside_directory,
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
