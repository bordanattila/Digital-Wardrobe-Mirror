"""Outfit use-case / orchestration layer."""

import logging

import requests

from app.database import Database
from app.schemas.outfit import OutfitSuggestions
from app.services.wardrobe_service import list_clothing_items
from app.services.weather_service import get_current_weather

logger = logging.getLogger(__name__)


def generate_outfit_suggestions(db: Database) -> OutfitSuggestions:
    """
    Generate outfit suggestions based on the current weather and the full wardrobe.
    """

    try:
        current_weather = get_current_weather()

        logger.info(
            f"Current weather: {current_weather.temperature_fahrenheit}, "
            f"{current_weather.city}"
        )
    except ValueError as exc:
        logger.warning(
            "Error getting current weather (value error): %s", type(exc).__name__
        )
        raise ValueError("Error getting current weather")
    except requests.exceptions.RequestException as exc:
        logger.warning(
            "Error getting current weather (network error): %s", type(exc).__name__
        )
        raise

    # Get the full wardrobe from the database by calling list_clothing_items() function
    full_wardrobe = list_clothing_items(db)

    cool_weather_tops = {"jumper", "sweater", "hoodie", "long-sleeve", "longsleeve"}
    warm_weather_tops = {"t-shirt", "tank top", "shirt", "tank", "tee", "polo"}
    cool_weather_bottoms = {"jeans", "pants", "trousers", "leggings"}
    warm_weather_bottoms = {
        "shorts",
        "skirt",
    }

    suggestable_tops_list = []
    suggestable_bottoms_list = []

    # Generate an outfit based on the current weather and the full wardrobe
    if current_weather.temperature_fahrenheit >= 70:
        logger.info("Generating outfit for warm weather")
        tops_allowed, bottoms_allowed = warm_weather_tops, warm_weather_bottoms
    else:
        logger.info("Generating outfit for cool weather")
        tops_allowed, bottoms_allowed = cool_weather_tops, cool_weather_bottoms

    for outfit_item in full_wardrobe:
        if (
            outfit_item.category.lower().strip() in tops_allowed
            or outfit_item.subcategory.lower().strip() in tops_allowed
        ):
            suggestable_tops_list.append(outfit_item)
        if (
            outfit_item.category.lower().strip() in bottoms_allowed
            or outfit_item.subcategory.lower().strip() in bottoms_allowed
        ):
            suggestable_bottoms_list.append(outfit_item)

    logger.info(f"Suggestable tops list length: {len(suggestable_tops_list)}")
    logger.info(f"Suggestable bottoms list length: {len(suggestable_bottoms_list)}")

    return OutfitSuggestions(
        tops=suggestable_tops_list,
        bottoms=suggestable_bottoms_list,
        weather=current_weather,
    )
