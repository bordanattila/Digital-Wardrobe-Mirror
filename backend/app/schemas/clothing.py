from pydantic import BaseModel, Field


class ClothingItem(BaseModel):
    id: int
    name: str
    color: str
    size: str
    category: str
    subcategory: str
    image_path: str


class NewClothingItem(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(..., min_length=1, max_length=20)
    size: str = Field(..., min_length=1, max_length=10)
    category: str = Field(..., min_length=1, max_length=20)
    subcategory: str = Field(..., min_length=1, max_length=50)
    image_path: str
