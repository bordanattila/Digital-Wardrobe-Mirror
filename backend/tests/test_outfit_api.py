# tests/test_outfit_api.py

from unittest.mock import patch

import pytest
import requests
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.clothing import ClothingItem
from app.schemas.outfit import OutfitSuggestions
from app.schemas.weather import WeatherConditions
from app.utils import rate_limiter


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_rate_limiter():
    rate_limiter._hits.clear()
    yield
    rate_limiter._hits.clear()


def _sample_suggestion() -> OutfitSuggestions:
    return OutfitSuggestions(
        weather=WeatherConditions(
            temperature_celsius=22,
            temperature_fahrenheit=72,
            icon="01d",
            conditions="clear sky",
            city="New York",
        ),
        tops=[
            ClothingItem(
                id=1,
                name="Summer Tee",
                color="white",
                size="M",
                category="top",
                subcategory="t-shirt",
                image_path="tee.png",
            )
        ],
        bottoms=[
            ClothingItem(
                id=2,
                name="Denim Shorts",
                color="blue",
                size="M",
                category="bottom",
                subcategory="shorts",
                image_path="shorts.png",
            )
        ],
    )


def test_suggest_outfit_success(client):
    sample = _sample_suggestion()
    with patch(
        "app.routers.outfits.outfit_service.generate_outfit_suggestions",
        return_value=sample,
    ):
        response = client.get("/api/outfits/suggest")

    assert response.status_code == 200
    body = response.json()
    assert body["weather"]["temperature_fahrenheit"] == 72
    assert body["tops"][0]["name"] == "Summer Tee"
    assert body["bottoms"][0]["name"] == "Denim Shorts"


def test_suggest_outfit_value_error_returns_502(client):
    with patch(
        "app.routers.outfits.outfit_service.generate_outfit_suggestions",
        side_effect=ValueError("Error getting current weather"),
    ):
        response = client.get("/api/outfits/suggest")

    assert response.status_code == 502
    assert response.json()["detail"] == "Outfit suggestions service unavailable"


def test_suggest_outfit_network_error_returns_502(client):
    with patch(
        "app.routers.outfits.outfit_service.generate_outfit_suggestions",
        side_effect=requests.exceptions.Timeout("timed out"),
    ):
        response = client.get("/api/outfits/suggest")

    assert response.status_code == 502
    assert response.json()["detail"] == "Outfit suggestions service unavailable"


def test_suggest_outfit_rate_limited(client):
    sample = _sample_suggestion()
    with patch(
        "app.routers.outfits.outfit_service.generate_outfit_suggestions",
        return_value=sample,
    ) as mock_suggest:
        for _ in range(rate_limiter.MAX_HITS):
            assert client.get("/api/outfits/suggest").status_code == 200

        limited = client.get("/api/outfits/suggest")
        assert limited.status_code == 429
        assert limited.json()["detail"] == "Too many requests"
        assert mock_suggest.call_count == rate_limiter.MAX_HITS
