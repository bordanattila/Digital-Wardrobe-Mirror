# tests/test_outfit_service.py

from unittest.mock import patch

import pytest
import requests

from app.schemas.clothing import ClothingItem
from app.schemas.outfit import OutfitSuggestions
from app.schemas.weather import WeatherConditions
from app.services import outfit_service


def _item(
    item_id: int,
    name: str,
    category: str,
    subcategory: str,
) -> ClothingItem:
    return ClothingItem(
        id=item_id,
        name=name,
        color="blue",
        size="M",
        category=category,
        subcategory=subcategory,
        image_path=f"{name.lower().replace(' ', '_')}.png",
    )


def _weather(temp_f: int) -> WeatherConditions:
    return WeatherConditions(
        temperature_celsius=round((temp_f - 32) * 5 / 9),
        temperature_fahrenheit=temp_f,
        icon="01d",
        conditions="clear sky",
        city="Testville",
    )


SAMPLE_WARDROBE = [
    _item(1, "Summer Tee", "top", "t_shirt"),
    _item(2, "Long Sleeve", "top", "long_sleeve"),
    _item(3, "Cozy Hoodie", "mid_layer", "hoodie"),
    _item(4, "Denim Shorts", "bottom", "shorts"),
    _item(5, "Blue Jeans", "bottom", "jeans"),
    _item(6, "Party Skirt", "bottom", "skirt"),
    _item(7, "White Sneakers", "shoes", "sneakers"),
    _item(8, "Winter Coat", "outer_layer", "coat"),
]


def test_warm_weather_builds_outfits(db):
    with (
        patch(
            "app.services.outfit_service.get_current_weather",
            return_value=_weather(75),
        ),
        patch(
            "app.services.outfit_service.list_clothing_items",
            return_value=SAMPLE_WARDROBE,
        ),
    ):
        result = outfit_service.generate_outfit_suggestions(db)

    assert isinstance(result, OutfitSuggestions)
    assert result.weather.temperature_fahrenheit == 75
    assert len(result.outfits) >= 1
    look = result.outfits[0]
    assert look.top[0].name == "Summer Tee"
    assert look.bottom[0].name in {"Denim Shorts", "Party Skirt"}
    assert look.shoes[0].name == "White Sneakers"
    assert look.mid_layer == []
    assert look.outer_layer == []
    assert "Warm" in look.reason


def test_mild_weather_can_include_mid_layer(db):
    with (
        patch(
            "app.services.outfit_service.get_current_weather",
            return_value=_weather(60),
        ),
        patch(
            "app.services.outfit_service.list_clothing_items",
            return_value=SAMPLE_WARDROBE,
        ),
    ):
        result = outfit_service.generate_outfit_suggestions(db)

    assert result.weather.temperature_fahrenheit == 60
    assert len(result.outfits) >= 1
    look = result.outfits[0]
    assert look.top[0].name == "Long Sleeve"
    assert look.bottom[0].name == "Blue Jeans"
    assert look.mid_layer[0].name == "Cozy Hoodie"
    assert look.outer_layer == []


def test_comfortable_band_at_70(db):
    with (
        patch(
            "app.services.outfit_service.get_current_weather",
            return_value=_weather(70),
        ),
        patch(
            "app.services.outfit_service.list_clothing_items",
            return_value=SAMPLE_WARDROBE,
        ),
    ):
        result = outfit_service.generate_outfit_suggestions(db)

    assert len(result.outfits) >= 1
    look = result.outfits[0]
    assert look.top[0].name == "Summer Tee"
    assert look.shoes[0].name == "White Sneakers"


def test_empty_wardrobe_returns_empty_outfits(db):
    with (
        patch(
            "app.services.outfit_service.get_current_weather",
            return_value=_weather(72),
        ),
        patch(
            "app.services.outfit_service.list_clothing_items",
            return_value=[],
        ),
    ):
        result = outfit_service.generate_outfit_suggestions(db)

    assert result.outfits == []


def test_missing_shoes_returns_empty_outfits(db):
    wardrobe = [item for item in SAMPLE_WARDROBE if item.category != "shoes"]
    with (
        patch(
            "app.services.outfit_service.get_current_weather",
            return_value=_weather(75),
        ),
        patch(
            "app.services.outfit_service.list_clothing_items",
            return_value=wardrobe,
        ),
    ):
        result = outfit_service.generate_outfit_suggestions(db)

    assert result.outfits == []


def test_weather_value_error_is_rewrapped(db):
    with patch(
        "app.services.outfit_service.get_current_weather",
        side_effect=ValueError("WEATHER_API_KEY is not configured"),
    ):
        with pytest.raises(ValueError, match="Error getting current weather"):
            outfit_service.generate_outfit_suggestions(db)


def test_weather_network_error_propagates(db):
    with patch(
        "app.services.outfit_service.get_current_weather",
        side_effect=requests.exceptions.Timeout("timed out"),
    ):
        with pytest.raises(requests.exceptions.RequestException):
            outfit_service.generate_outfit_suggestions(db)
