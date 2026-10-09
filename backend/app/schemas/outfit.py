from pydantic import BaseModel

from app.schemas.clothing import ClothingItem
from app.schemas.weather import WeatherConditions


class OutfitSuggestions(BaseModel):
    tops: list[ClothingItem]
    bottoms: list[ClothingItem]
    weather: WeatherConditions
