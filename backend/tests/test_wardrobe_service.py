# tests/test_wardrobe_service.py

from pathlib import Path

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


def test_get_one_clothing_item_by_id(db):
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    item = wardrobe_service.get_one_clothing_item_by_id(db, 1)
    assert item.id == 1
    assert item.name == "Tee"


def test_get_one_clothing_item_missing(db):
    with pytest.raises(ValueError, match="not found"):
        wardrobe_service.get_one_clothing_item_by_id(db, 99)


def test_create_item_success(db, image_dirs):
    png = make_png_bytes(color=(0, 0, 0), accent=(200, 50, 50))

    item = wardrobe_service.create_item(
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
    originals = list(image_dirs["original"].iterdir())
    assert len(originals) == 1


def test_create_rejects_unsupported_extension(db, image_dirs):
    with pytest.raises(ValueError, match="Unsupported file type"):
        wardrobe_service.create_item(
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
        wardrobe_service.create_item(
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
        wardrobe_service.create_item(
            db=db,
            name="Corrupt",
            color="red",
            size="M",
            category="top",
            subcategory="t-shirt",
            filename="bad.png",
            image_bytes=b"not-a-real-png",
        )
    assert list(image_dirs["original"].iterdir()) == []


def test_update_item_by_id(db):
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    updated = wardrobe_service.update_item_by_id(
        db, 1, "Polo", "green", "L", "tops", "polo"
    )
    assert updated.name == "Polo"
    assert updated.color == "green"
    assert updated.size == "L"
    assert updated.subcategory == "polo"
    # Image path is metadata-only update — unchanged
    assert updated.image_path == "/img/tee.png"


def test_update_item_missing(db):
    with pytest.raises(ValueError, match="not found"):
        wardrobe_service.update_item_by_id(db, 99, "Polo", "green", "L", "tops", "polo")


def test_remove_clothing_item_by_id_deletes_files(db, image_dirs):
    png = make_png_bytes(color=(0, 0, 0), accent=(200, 50, 50))
    item = wardrobe_service.create_item(
        db=db,
        name="Temp",
        color="red",
        size="M",
        category="top",
        subcategory="t-shirt",
        filename="shirt.png",
        image_bytes=png,
    )
    original = list(image_dirs["original"].iterdir())[0]
    processed = Path(item.image_path)
    assert original.exists()
    assert processed.exists()

    wardrobe_service.remove_clothing_item_by_id(db, item.id)

    assert db.get_clothing_item_by_id(item.id) is None
    assert not original.exists()
    assert not processed.exists()


def test_remove_clothing_item_missing(db):
    with pytest.raises(ValueError, match="not found"):
        wardrobe_service.remove_clothing_item_by_id(db, 99)
