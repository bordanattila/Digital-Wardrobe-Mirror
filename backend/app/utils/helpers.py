from pathlib import Path

from app.database import Database
from app.services.background_service import (
    BACKGROUND_REMOVED_IMAGES_DIR,
    ORIGINAL_IMAGES_DIR,
    is_path_inside_directory,
)


def processed_path_from_stored(stored: str) -> Path:
    path = (BACKGROUND_REMOVED_IMAGES_DIR / Path(stored).name).resolve()
    if not is_path_inside_directory(path, BACKGROUND_REMOVED_IMAGES_DIR):
        raise ValueError("Invalid image path")
    return path


def processed_path_from_original(original: str) -> Path:
    path = (ORIGINAL_IMAGES_DIR / Path(original).name).resolve()
    if not is_path_inside_directory(path, ORIGINAL_IMAGES_DIR):
        raise ValueError("Invalid image path")
    return path


def get_item_image_path(db: Database, item_id: int) -> Path:
    row = db.get_clothing_item_by_id(item_id)
    if row is None:
        raise ValueError("Clothing item not found")
    path = processed_path_from_stored(row["item_image_path"])
    if not path.is_file():
        raise ValueError("Image file not found")
    return path
