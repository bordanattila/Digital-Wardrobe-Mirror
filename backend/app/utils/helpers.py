from pathlib import Path

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
