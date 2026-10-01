# tests/test_weather_api.py

from unittest.mock import patch

import pytest
import requests
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.weather import WeatherConditions
from app.services import weather_service


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_weather_cache():
    weather_service.WEATHER_CACHE["data"] = None
    weather_service.WEATHER_CACHE["expires_at"] = 0
    yield
    weather_service.WEATHER_CACHE["data"] = None
    weather_service.WEATHER_CACHE["expires_at"] = 0


def test_get_weather_success(client):
    sample = WeatherConditions(
        temperature_celsius=22,
        temperature_fahrenheit=72,
        icon="01d",
        conditions="clear sky",
        city="New York",
    )
    with patch(
        "app.routers.weather.get_current_weather",
        return_value=sample,
    ):
        response = client.get("/api/weather/")

    assert response.status_code == 200
    body = response.json()
    assert body["temperature_celsius"] == 22
    assert body["temperature_fahrenheit"] == 72
    assert body["icon"] == "01d"
    assert body["conditions"] == "clear sky"
    assert body["city"] == "New York"


def test_get_weather_value_error_returns_502(client):
    with patch(
        "app.routers.weather.get_current_weather",
        side_effect=ValueError("Failed to get location"),
    ):
        response = client.get("/api/weather/")

    assert response.status_code == 502
    assert "Failed to get location" in response.json()["detail"]


def test_get_weather_request_exception_returns_500(client):
    with patch(
        "app.routers.weather.get_current_weather",
        side_effect=requests.exceptions.Timeout("timed out"),
    ):
        response = client.get("/api/weather/")

    assert response.status_code == 500
