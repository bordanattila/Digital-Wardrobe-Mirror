# tests/test_weather_service.py

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.schemas.weather import WeatherConditions
from app.services import weather_service


@pytest.fixture(autouse=True)
def clear_weather_cache():
    """Isolate tests from the module-level weather cache."""
    weather_service.WEATHER_CACHE["data"] = None
    weather_service.WEATHER_CACHE["expires_at"] = 0
    yield
    weather_service.WEATHER_CACHE["data"] = None
    weather_service.WEATHER_CACHE["expires_at"] = 0


def _mock_response(json_data, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            f"{status_code} error"
        )
    return response


def test_get_location_success():
    with patch("app.services.weather_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(
            {"loc": "40.71,-74.00", "city": "New York"}
        )
        lat, lon, city = weather_service.get_location()

    assert lat == pytest.approx(40.71)
    assert lon == pytest.approx(-74.00)
    assert city == "New York"
    mock_get.assert_called_once()


def test_get_location_missing_loc():
    with patch("app.services.weather_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response({"city": "New York"})
        with pytest.raises(ValueError, match="loc"):
            weather_service.get_location()


def test_get_location_invalid_loc():
    with patch("app.services.weather_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response({"loc": "not-a-coord", "city": "X"})
        with pytest.raises(ValueError, match="parse location"):
            weather_service.get_location()


def test_get_location_network_error():
    with patch("app.services.weather_service.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("timed out")
        with pytest.raises(requests.exceptions.RequestException):
            weather_service.get_location()


def test_get_weather_maps_to_dto():
    openweather = {
        "main": {"temp": 21.6},
        "weather": [{"icon": "01d", "description": "clear sky"}],
    }
    with patch("app.services.weather_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(openweather)
        result = weather_service.get_weather(40.71, -74.0, "New York")

    assert isinstance(result, WeatherConditions)
    assert result.temperature_celsius == 22
    assert result.temperature_fahrenheit == 72
    assert result.icon == "01d"
    assert result.conditions == "clear sky"
    assert result.city == "New York"


def test_get_weather_rejects_missing_coords():
    with pytest.raises(ValueError, match="Invalid coordinates"):
        weather_service.get_weather(None, -74.0, "New York")


def test_get_weather_rejects_missing_temp():
    with patch("app.services.weather_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(
            {"weather": [{"icon": "01d", "description": "clear sky"}]}
        )
        with pytest.raises(ValueError, match="temp"):
            weather_service.get_weather(40.71, -74.0, "New York")


def test_get_weather_rejects_missing_icon():
    with patch("app.services.weather_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(
            {"main": {"temp": 20}, "weather": [{"description": "clouds"}]}
        )
        with pytest.raises(ValueError, match="icon"):
            weather_service.get_weather(40.71, -74.0, "New York")


def test_get_current_weather_uses_cache():
    sample = WeatherConditions(
        temperature_celsius=20,
        temperature_fahrenheit=68,
        icon="01d",
        conditions="clear sky",
        city="New York",
    )

    with (
        patch(
            "app.services.weather_service.get_location",
            return_value=(40.71, -74.0, "New York"),
        ) as mock_loc,
        patch(
            "app.services.weather_service.get_weather",
            return_value=sample,
        ) as mock_weather,
    ):
        first = weather_service.get_current_weather()
        second = weather_service.get_current_weather()

    assert first == sample
    assert second == sample
    mock_loc.assert_called_once()
    mock_weather.assert_called_once()


def test_get_current_weather_refetches_after_expiry():
    sample = WeatherConditions(
        temperature_celsius=20,
        temperature_fahrenheit=68,
        icon="01d",
        conditions="clear sky",
        city="New York",
    )

    with (
        patch(
            "app.services.weather_service.get_location",
            return_value=(40.71, -74.0, "New York"),
        ) as mock_loc,
        patch(
            "app.services.weather_service.get_weather",
            return_value=sample,
        ) as mock_weather,
        patch(
            "app.services.weather_service.time.time",
            side_effect=[1000, 1000 + 1801],
        ),
    ):
        weather_service.get_current_weather()
        weather_service.get_current_weather()

    assert mock_loc.call_count == 2
    assert mock_weather.call_count == 2
