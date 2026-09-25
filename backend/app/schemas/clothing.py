from typing import Optional

from pydantic import BaseModel


class ClothingItem(BaseModel):
    id: int
    name: str
    color: str
    size: str
    category: str
    subcategory: str
    image_path: str


class ClothingItemUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    image_path: Optional[str] = None
