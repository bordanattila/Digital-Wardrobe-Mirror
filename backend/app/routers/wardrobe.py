"""HTTP adapters for wardrobe clothing items.

It only:
  1. Declares routes and request shapes (Form / File / Depends)
  2. Reads the upload into bytes (async I/O that belongs at the edge)
  3. Calls wardrobe_service
  4. Maps ValueError -> HTTPException(400)

All validation, file saving, image processing, and DB writes live in
app.services.wardrobe_service.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.database import Database
from app.schemas.clothing import ClothingItem
from app.services import wardrobe_service
from app.utils.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=list[ClothingItem])
async def get_clothing_items(
    db: Database = Depends(get_db),
):
    """GET /wardrobe/ — list every clothing item."""
    # The service owns fetching + mapping rows -> ClothingItem.
    return wardrobe_service.list_clothing_items(db)


@router.post("/", response_model=ClothingItem)
async def create_clothing_item(
    name: str = Form(...),
    color: str = Form(...),
    size: str = Form(...),
    category: str = Form(...),
    subcategory: str = Form(...),
    image: UploadFile = File(...),
    db: Database = Depends(get_db),
):
    """POST /wardrobe/ — create an item from multipart form + image file.

    UploadFile is a FastAPI/Starlette type, so we read it HERE and pass
    plain bytes + filename into the service. That keeps the service free
    of web-framework types (easier to test later).
    """
    # Read the whole file into memory once. The service never sees UploadFile.
    image_bytes = await image.read()

    try:
        return wardrobe_service.create_clothing_item(
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
        raise HTTPException(status_code=400, detail=str(exc)) from exc
