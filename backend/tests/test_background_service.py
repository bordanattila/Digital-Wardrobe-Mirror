# tests/test_background_service.py

from io import BytesIO

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


def test_remove_background_returns_rgba(monkeypatch):
    """rembg is mocked; remove_background must still return RGBA."""

    def fake_remove(data: bytes) -> bytes:
        with Image.open(BytesIO(data)) as im:
            rgba = im.convert("RGBA")
            # Simulate a cutout: transparent top-left pixel.
            rgba.putpixel((0, 0), (0, 0, 0, 0))
            buf = BytesIO()
            rgba.save(buf, format="PNG")
            return buf.getvalue()

    monkeypatch.setattr("app.services.background_service.remove", fake_remove)

    img = Image.new("RGB", (2, 2), (10, 20, 30))
    out = remove_background(img)
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((1, 1))[:3] == (10, 20, 30)


def test_process_image_writes_rgba_png(image_dirs, monkeypatch):
    def fake_remove(data: bytes) -> bytes:
        with Image.open(BytesIO(data)) as im:
            buf = BytesIO()
            im.convert("RGBA").save(buf, format="PNG")
            return buf.getvalue()

    monkeypatch.setattr("app.services.background_service.remove", fake_remove)

    # Portrait source (taller than wide) — no extra rotate needed.
    source = image_dirs["original"] / "shirt.png"
    Image.new("RGB", (4, 6), (0, 128, 255)).save(source)

    out_path = process_image(source)

    assert out_path.is_file()
    assert out_path.parent == image_dirs["processed"].resolve()
    assert out_path.name == "bg_removed_shirt.png"
    assert out_path.suffix == ".png"
    with Image.open(out_path) as result:
        assert result.mode == "RGBA"
        assert result.size == (4, 6)


def test_process_image_forces_landscape_to_portrait(image_dirs, monkeypatch):
    """Broken EXIF (Orientation=1)
    sideways phone shots stay landscape until we rotate."""
    seen_sizes: list[tuple[int, int]] = []

    def fake_remove(data: bytes) -> bytes:
        with Image.open(BytesIO(data)) as im:
            seen_sizes.append(im.size)
            buf = BytesIO()
            im.convert("RGBA").save(buf, format="PNG")
            return buf.getvalue()

    monkeypatch.setattr("app.services.background_service.remove", fake_remove)

    source = image_dirs["original"] / "sideways.jpeg"
    Image.new("RGB", (6, 4), (200, 50, 50)).save(source, format="JPEG")

    out_path = process_image(source)

    assert out_path.suffix == ".png"
    assert seen_sizes == [(4, 6)]  # rembg received portrait pixels
    with Image.open(out_path) as result:
        assert result.size == (4, 6)


def test_process_image_jpeg_input_still_saves_png(image_dirs, monkeypatch):
    def fake_remove(data: bytes) -> bytes:
        with Image.open(BytesIO(data)) as im:
            buf = BytesIO()
            im.convert("RGBA").save(buf, format="PNG")
            return buf.getvalue()

    monkeypatch.setattr("app.services.background_service.remove", fake_remove)

    source = image_dirs["original"] / "photo.jpeg"
    Image.new("RGB", (3, 5), (1, 2, 3)).save(source, format="JPEG")

    out_path = process_image(source)
    assert out_path.name == "bg_removed_photo.png"


def test_process_image_rejects_path_outside_original(image_dirs, tmp_path):
    outside = tmp_path / "escape.png"
    Image.new("RGB", (2, 2), (0, 0, 0)).save(outside)

    with pytest.raises(ValueError, match="not inside the original"):
        process_image(outside)


def test_process_image_rejects_non_image(image_dirs):
    fake = image_dirs["original"] / "not-an-image.png"
    fake.write_bytes(b"this is not a png")

    with pytest.raises(ValueError, match="Failed to open image"):
        process_image(fake)


def test_process_image_sanitizes_unsafe_stem(image_dirs, monkeypatch):
    def fake_remove(data: bytes) -> bytes:
        with Image.open(BytesIO(data)) as im:
            buf = BytesIO()
            im.convert("RGBA").save(buf, format="PNG")
            return buf.getvalue()

    monkeypatch.setattr("app.services.background_service.remove", fake_remove)

    source = image_dirs["original"] / "weird name!!.png"
    Image.new("RGB", (2, 3), (0, 0, 0)).save(source)

    out_path = process_image(source)

    assert " " not in out_path.name
    assert "!" not in out_path.name
    assert out_path.name.startswith("bg_removed_")
    assert out_path.suffix == ".png"
