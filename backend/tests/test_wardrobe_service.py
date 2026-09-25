# tests/test_wardrobe_service.py

import pytest

from app.services import wardrobe_service
from app.services.background_service import MAX_IMAGE_SIZE
from tests.conftest import make_png_bytes


def test_list_clothing_items_empty(db):
    assert wardrobe_service.list_clothing_items(db) == []


def test_list_clothing_items_maps_rows(db):
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    items = wardrobe_service.list_clothing_items(db)
    assert len(items) == 1
    assert items[0].name == "Tee"
    assert items[0].color == "blue"
    assert items[0].image_path == "/img/tee.png"


def test_create_clothing_item_success(db, image_dirs):
    png = make_png_bytes(color=(0, 0, 0), accent=(200, 50, 50))

    item = wardrobe_service.create_clothing_item(
        db=db,
        name="Test Shirt",
        color="red",
        size="M",
        category="top",
        subcategory="t-shirt",
        filename="shirt.png",
        image_bytes=png,
    )

    assert item.id == 1
    assert item.name == "Test Shirt"
    assert "processed" in item.image_path
    assert image_dirs["processed"].exists()
    # Original upload should still exist after success
    originals = list(image_dirs["original"].iterdir())
    assert len(originals) == 1


def test_create_rejects_unsupported_extension(db, image_dirs):
    with pytest.raises(ValueError, match="Unsupported file type"):
        wardrobe_service.create_clothing_item(
            db=db,
            name="Bad",
            color="red",
            size="M",
            category="top",
            subcategory="t-shirt",
            filename="notes.txt",
            image_bytes=b"hello",
        )
    assert list(image_dirs["original"].iterdir()) == []


def test_create_rejects_oversized_file(db, image_dirs):
    huge = b"x" * (MAX_IMAGE_SIZE + 1)
    with pytest.raises(ValueError, match="File too large"):
        wardrobe_service.create_clothing_item(
            db=db,
            name="Huge",
            color="red",
            size="M",
            category="top",
            subcategory="t-shirt",
            filename="huge.png",
            image_bytes=huge,
        )
    assert list(image_dirs["original"].iterdir()) == []


def test_create_cleans_up_original_when_process_fails(db, image_dirs):
    with pytest.raises(ValueError, match="not a valid image"):
        wardrobe_service.create_clothing_item(
            db=db,
            name="Corrupt",
            color="red",
            size="M",
            category="top",
            subcategory="t-shirt",
            filename="bad.png",
            image_bytes=b"not-a-real-png",
        )
    # Orphan original should be removed
    assert list(image_dirs["original"].iterdir()) == []
