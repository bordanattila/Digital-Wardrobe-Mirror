import requests
from fastapi import APIRouter, HTTPException

from app.schemas.weather import WeatherConditions
from app.services.weather_service import get_current_weather

router = APIRouter()


@router.get("/", response_model=WeatherConditions)
async def get_weather_route():
    """
    Get the current weather data for the user's location.
    """
    try:
        return get_current_weather()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
