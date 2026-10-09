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
    _item(1, "Summer Tee", "top", "t-shirt"),
    _item(2, "Cozy Hoodie", "top", "hoodie"),
    _item(3, "Denim Shorts", "bottom", "shorts"),
    _item(4, "Blue Jeans", "bottom", "jeans"),
    _item(5, "Party Skirt", "bottom", "Skirt"),  # mixed case
    _item(6, "Dress Shoes", "shoes", "oxford"),
]


def test_warm_weather_filters_tops_and_bottoms(db):
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
    assert {item.name for item in result.tops} == {"Summer Tee"}
    assert {item.name for item in result.bottoms} == {"Denim Shorts", "Party Skirt"}


def test_cool_weather_filters_tops_and_bottoms(db):
    with (
        patch(
            "app.services.outfit_service.get_current_weather",
            return_value=_weather(55),
        ),
        patch(
            "app.services.outfit_service.list_clothing_items",
            return_value=SAMPLE_WARDROBE,
        ),
    ):
        result = outfit_service.generate_outfit_suggestions(db)

    assert result.weather.temperature_fahrenheit == 55
    assert {item.name for item in result.tops} == {"Cozy Hoodie"}
    assert {item.name for item in result.bottoms} == {"Blue Jeans"}


def test_exactly_70_uses_warm_allowlists(db):
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

    assert {item.name for item in result.tops} == {"Summer Tee"}
    assert {item.name for item in result.bottoms} == {"Denim Shorts", "Party Skirt"}


def test_empty_wardrobe_returns_empty_lists(db):
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

    assert result.tops == []
    assert result.bottoms == []


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
