"""Wardrobe use-case / orchestration layer.

WHY THIS FILE EXISTS

The FastAPI *router* should only speak HTTP:
  - parse the request (form fields, uploaded file)
  - call a service function
  - turn results into a response, or ValueError into HTTPException

This *service* owns the business workflow:
  - list / get / create / update / delete clothing items
  - save uploads, run background removal, clean up files on delete

It calls lower-level helpers:
  - Database           -> SQL insert / select / update / delete
  - background_service -> path constants + process_image()

RULE: do not import FastAPI or raise HTTPException here.
      Raise ValueError for bad input or missing IDs.
      The router maps those to HTTP 400 (validation) or 404 (not found).
"""

import uuid
from pathlib import Path

from app.database import Database
from app.schemas.clothing import ClothingItem
from app.services.background_service import (
    ALLOWED_EXTENSIONS,
    MAX_IMAGE_SIZE,
    ORIGINAL_IMAGES_DIR,
    process_image,
)


def _row_to_clothing_item(row) -> ClothingItem:
    """Convert one sqlite3.Row into our API schema.

    The DB columns are named item_name, item_color, ...
    The Pydantic model uses name, color, ...
    This helper keeps that rename in one place.
    """
    return ClothingItem(
        id=row["id"],
        name=row["item_name"],
        color=row["item_color"],
        size=row["item_size"],
        category=row["item_category"],
        subcategory=row["item_subcategory"],
        image_path=row["item_image_path"],
    )


def list_clothing_items(db: Database) -> list[ClothingItem]:
    """Fetch every clothing item and return them as ClothingItem schemas."""
    rows = db.get_all_clothing_items()
    return [_row_to_clothing_item(row) for row in rows]


def get_one_clothing_item_by_id(db: Database, item_id: int) -> ClothingItem:
    """Fetch one clothing item by ID and return it as a ClothingItem schema.

    Raises:
        ValueError: if no row exists for item_id (router maps to HTTP 404).
    """
    row = db.get_clothing_item_by_id(item_id)
    if row is None:
        raise ValueError(f"Clothing item with ID {item_id} not found")
    return _row_to_clothing_item(row)


def update_item_by_id(
    db: Database,
    item_id: int,
    item_name: str,
    item_color: str,
    item_size: str,
    item_category: str,
    item_subcategory: str,
) -> ClothingItem:
    """Update metadata for one item; image_path is left unchanged.

    Raises:
        ValueError: if no row exists for item_id (router maps to HTTP 404).
    """
    row = db.get_clothing_item_by_id(item_id)
    if row is None:
        raise ValueError(f"Clothing item with ID {item_id} not found")
    db.update_clothing_item_by_id(
        item_id, item_name, item_color, item_size, item_category, item_subcategory
    )
    return get_one_clothing_item_by_id(db, item_id)


def create_item(
    db: Database,
    name: str,
    color: str,
    size: str,
    category: str,
    subcategory: str,
    filename: str | None,
    image_bytes: bytes,
) -> ClothingItem:
    """Create one clothing item from plain Python values.

    Parameters are deliberately NOT FastAPI types:
      - filename: str | None   (from image.filename)
      - image_bytes: bytes     (from await image.read())

    Raises:
        ValueError: unsupported extension, file too large, or process_image failure.
        The router catches these and turns them into HTTP 400.
    """
    # 1. Validate file type from the original filename
    # Path("shirt.PNG").suffix.lower() -> ".png"
    # Empty / missing filename -> "" which is not in ALLOWED_EXTENSIONS.
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type")

    # 2. Reject oversized uploads before we write anything
    # Protects disk and memory (especially on a Raspberry Pi).
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError("File too large")

    # 3. Save the raw upload under a unique name
    # uuid4() avoids collisions if two users upload "shirt.jpg".
    # We keep the real extension so process_image / PIL know the format.
    saved_path = ORIGINAL_IMAGES_DIR / f"{uuid.uuid4()}{suffix}"
    saved_path.write_bytes(image_bytes)

    # 4. Background removal (delegates to background_service)
    # process_image already raises ValueError on bad paths / corrupt images.
    # We let that bubble up unchanged so the router can map it to HTTP 400.
    try:
        background_removed_path = process_image(saved_path)

        # 5. Persist metadata + processed image path
        db.add_clothing_item(
            name,
            color,
            size,
            category,
            subcategory,
            str(background_removed_path),
        )
        # lastrowid is the auto-increment id SQLite assigned on that INSERT.
        item_id = db.cursor.lastrowid

        # 6. Return the same shape the API documents
        return ClothingItem(
            id=item_id,
            name=name,
            color=color,
            size=size,
            category=category,
            subcategory=subcategory,
            image_path=str(background_removed_path),
        )
    except Exception:
        # Service raised ValueError("File too large") etc. -> HTTP 400 for clients.
        saved_path.unlink(missing_ok=True)
        raise


def remove_clothing_item_by_id(db: Database, item_id: int) -> None:
    """Delete one clothing item and its image files on disk.

    Uses item_image_path (processed file). If the name is bg_removed_<file>,
    also removes the matching upload under ORIGINAL_IMAGES_DIR.

    Raises:
        ValueError: if no row exists for item_id (router maps to HTTP 404).
    """
    row = db.get_clothing_item_by_id(item_id)
    if row is None:
        raise ValueError(f"Clothing item with ID {item_id} not found")
    db.delete_clothing_item_by_id(item_id)

    # Delete processed image; derive original name from bg_removed_ prefix
    processed_path = Path(row["item_image_path"])
    name = processed_path.name
    if name.startswith("bg_removed_"):
        original_name = name.removeprefix("bg_removed_")
        original_path = ORIGINAL_IMAGES_DIR / original_name
        original_path.unlink(missing_ok=True)
    processed_path.unlink(missing_ok=True)
