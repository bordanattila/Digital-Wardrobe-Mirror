import os
import time

import requests
from dotenv import load_dotenv

from app.schemas.weather import WeatherConditions

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
TOKEN = os.getenv("IP_INFO_TOKEN")


WEATHER_CACHE = {"data": None, "expires_at": 0}
TOTAL_CACHE_TIME = 30 * 60  # 30 minutes


def get_location():
    """
    Attempts to retrieve the user's geographical location using their IP address.

    Returns:
        tuple: (latitude: float, longitude: float, city: str)
        or raises an exception on failure.
    """
    try:
        response = requests.get(f"https://ipinfo.io/json?token={TOKEN}", timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        loc = data.get("loc")
        city = data.get("city")

        if not loc:
            print("Failed to get location: 'loc' field missing from response")
            raise ValueError(
                "Failed to get location: 'loc' field missing from response"
            )

        try:
            lat, lon = map(float, loc.split(","))
            return lat, lon, city
        except (ValueError, AttributeError) as e:
            print(f"Failed to parse location data '{loc}': {e}")
            raise ValueError(f"Failed to parse location data '{loc}'") from e
    except requests.exceptions.RequestException as e:
        print(f"Failed to get location (network error): {e}")
        raise
    except (KeyError, TypeError) as e:
        print(f"Failed to get location (data error): {e}")
        raise ValueError("Failed to get location (data error)") from e


def get_weather(lat, lon, city) -> WeatherConditions:
    """
    Retrieves current temperature and weather icon from OpenWeatherMap API.

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        WeatherConditions: WeatherConditions object
        or raises an exception on failure
    """
    if lat is None or lon is None:
        print("Failed to get weather: Invalid coordinates")
        raise ValueError("Failed to get weather: Invalid coordinates")

    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        # Validate response structure
        if "main" not in data or "temp" not in data["main"]:
            print("Failed to get weather: Invalid response structure missing temp)")
            raise ValueError("Invalid response structure missing temp")

        if (
            "weather" not in data
            or not data["weather"]
            or "icon" not in data["weather"][0]
        ):
            print("Failed to get weather: Invalid response structure missing icon")
            raise ValueError("Invalid response structure missing icon")

        celsius = round(data["main"]["temp"])
        fahrenheit = round((celsius * (9 / 5)) + 32)
        icon = data["weather"][0]["icon"]
        conditions = data["weather"][0]["description"]
        weather_data = WeatherConditions(
            temperature_celsius=celsius,
            temperature_fahrenheit=fahrenheit,
            icon=icon,
            conditions=conditions,
            city=city,
        )
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Failed to get weather (network error): {e}")
        raise
    except (KeyError, TypeError, IndexError) as e:
        print(f"Failed to get weather (data error): {e}")
        raise ValueError("Failed to get weather (data error)") from e


def get_current_weather():
    now = time.time()

    # Check if the weather data is already in the cache
    if WEATHER_CACHE["data"] is not None and now < WEATHER_CACHE["expires_at"]:
        return WEATHER_CACHE["data"]

    # Get the user's location
    lat, lon, city = get_location()
    if lat is None or lon is None:
        raise ValueError("Failed to get location: Invalid coordinates")

    # Get the weather data
    weather = get_weather(lat, lon, city)
    WEATHER_CACHE["data"] = weather
    WEATHER_CACHE["expires_at"] = now + TOTAL_CACHE_TIME
    return weather
