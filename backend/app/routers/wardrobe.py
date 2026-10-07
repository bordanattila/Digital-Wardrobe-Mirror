"""HTTP adapters for wardrobe clothing items.

It only:
  1. Declares routes and request shapes (Form / File / Depends)
  2. Reads the upload into bytes (async I/O that belongs at the edge)
  3. Calls wardrobe_service
  4. Maps ValueError -> HTTPException
       - 400 for bad uploads / validation on POST
       - 404 for missing IDs on GET / PUT / DELETE

All validation, file saving, image processing, and DB writes live in
app.services.wardrobe_service.
"""

import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.database import Database
from app.schemas.clothing import ClothingItem, NewClothingItem
from app.services import wardrobe_service
from app.services.background_service import MAX_IMAGE_SIZE
from app.utils.dependencies import get_db
from app.utils.rate_limiter import rate_limit

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/", response_model=list[ClothingItem])
async def get_clothing_items(
    db: Database = Depends(get_db),
):
    """GET /wardrobe/ — list every clothing item."""
    # The service owns fetching + mapping rows -> ClothingItem.
    logger.info("Listing all clothing items")
    return wardrobe_service.list_clothing_items(db)


@router.get("/{item_id}", response_model=ClothingItem)
async def get_clothing_item_by_id(
    item_id: int,
    db: Database = Depends(get_db),
):
    """GET /wardrobe/{item_id} — get a clothing item by ID."""
    try:
        logger.info("Getting clothing item by ID: %s", item_id)
        return wardrobe_service.get_one_clothing_item_by_id(db, item_id)
    except ValueError as exc:
        logger.warning("Clothing item not found: %s", item_id)
        raise HTTPException(status_code=404, detail="Clothing item not found") from exc


@router.put("/{item_id}", response_model=ClothingItem)
async def update_clothing_item_by_id(
    item_id: int,
    name: str = Form(..., min_length=1, max_length=100),
    color: str = Form(..., min_length=1, max_length=20),
    size: str = Form(..., min_length=1, max_length=10),
    category: str = Form(..., min_length=1, max_length=20),
    subcategory: str = Form(..., min_length=1, max_length=50),
    db: Database = Depends(get_db),
):
    """PUT /wardrobe/{item_id} — update a clothing item by ID."""
    try:
        logger.info("Updating clothing item by ID: %s", item_id)
        return wardrobe_service.update_item_by_id(
            db, item_id, name, color, size, category, subcategory
        )
    except ValueError as exc:
        logger.warning("Clothing item not found: %s", item_id)
        raise HTTPException(status_code=404, detail="Clothing item not found") from exc


@router.post("/", response_model=NewClothingItem)
async def create_clothing_item(
    name: str = Form(..., min_length=1, max_length=100),
    color: str = Form(..., min_length=1, max_length=20),
    size: str = Form(..., min_length=1, max_length=10),
    category: str = Form(..., min_length=1, max_length=20),
    subcategory: str = Form(..., min_length=1, max_length=50),
    image: UploadFile = File(...),
    db: Database = Depends(get_db),
    _rate_limit: None = Depends(rate_limit),
):
    """POST /wardrobe/ — create an item from multipart form + image file.

    UploadFile is a FastAPI/Starlette type, so we read it HERE and pass
    plain bytes + filename into the service. That keeps the service free
    of web-framework types (easier to test later).
    """
    # Read the whole file into memory once. The service never sees UploadFile.
    chunk = await image.read(MAX_IMAGE_SIZE + 1)
    if len(chunk) > MAX_IMAGE_SIZE:
        logger.warning("File too large: %s", len(chunk))
        raise HTTPException(status_code=413, detail="File too large")
    image_bytes = chunk

    try:
        logger.info("Creating clothing item: %s", image.filename)
        return wardrobe_service.create_item(
            db=db,
            name=name,
            color=color,
            size=size,
            category=category,
            subcategory=subcategory,
            filename=image.filename,
            image_bytes=image_bytes,
        )
    except ValueError as exc:
        # Service raised ValueError("File too large") etc. -> HTTP 400 for clients.
        logger.warning("Failed to create clothing item: %s", type(exc).__name__)
        raise HTTPException(
            status_code=400, detail="Failed to create clothing item"
        ) from exc


@router.delete("/{item_id}", status_code=204)
async def delete_clothing_item_by_id(
    item_id: int,
    db: Database = Depends(get_db),
    _rate_limit: None = Depends(rate_limit),
):
    """DELETE /wardrobe/{item_id} — delete a clothing item by ID."""
    try:
        logger.info("Deleting clothing item by ID: %s", item_id)
        wardrobe_service.remove_clothing_item_by_id(db, item_id)
    except ValueError as exc:
        logger.warning("Clothing item not found: %s", item_id)
        raise HTTPException(status_code=404, detail="Clothing item not found") from exc
