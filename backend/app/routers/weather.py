import logging

import requests
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.weather import WeatherConditions
from app.services.weather_service import get_current_weather
from app.utils.rate_limiter import rate_limit

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/", response_model=WeatherConditions)
async def get_weather_route(_rate_limit: None = Depends(rate_limit)):
    """
    Get the current weather data for the user's location.
    """
    try:
        return get_current_weather()

    except ValueError as exc:
        logger.warning("Weather request failed (config/data): %s", exc)
        detail = str(exc)
        status = 503 if "not configured" in detail.lower() else 502
        raise HTTPException(
            status_code=status, detail="Weather service unavailable"
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.warning("Weather request failed (network error): %s", exc)
        raise HTTPException(
            status_code=502, detail="Weather service unavailable"
        ) from exc
