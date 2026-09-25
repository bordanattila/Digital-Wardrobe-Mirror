"""Shared pytest fixtures for the backend test suite."""

import io

import pytest
from PIL import Image

from app.database import Database


@pytest.fixture
def db(tmp_path):
    """Fresh SQLite database with ClothingItems table created."""
    database = Database(tmp_path / "test.db")
    database.create_table()
    yield database
    database.close()


@pytest.fixture
def image_dirs(tmp_path, monkeypatch):
    """Point background/wardrobe image dirs at an isolated temp tree."""
    original = tmp_path / "original"
    processed = tmp_path / "processed"
    original.mkdir()
    processed.mkdir()

    monkeypatch.setattr("app.services.background_service.ORIGINAL_IMAGES_DIR", original)
    monkeypatch.setattr(
        "app.services.background_service.BACKGROUND_REMOVED_IMAGES_DIR", processed
    )
    monkeypatch.setattr("app.services.wardrobe_service.ORIGINAL_IMAGES_DIR", original)

    return {"original": original, "processed": processed}


def make_png_bytes(color=(0, 0, 0), size=(8, 8), accent=None) -> bytes:
    """Build a small in-memory PNG for upload / process tests."""
    img = Image.new("RGB", size, color)
    if accent is not None:
        img.putpixel((size[0] // 2, size[1] // 2), accent)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
