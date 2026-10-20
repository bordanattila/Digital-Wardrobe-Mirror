from pydantic import BaseModel

from app.schemas.clothing import ClothingItem
from app.schemas.weather import WeatherConditions


class Outfit(BaseModel):
    top: list[ClothingItem]
    bottom: list[ClothingItem]
    shoes: list[ClothingItem]
    mid_layer: list[ClothingItem]
    outer_layer: list[ClothingItem]
    # hat: list[ClothingItem]
    # gloves: list[ClothingItem]
    # scarf: list[ClothingItem]
    # accessory: list[ClothingItem]
    # bag: list[ClothingItem]
    score: int
    reason: str


class OutfitSuggestions(BaseModel):
    outfits: list[Outfit]
    weather: WeatherConditions
