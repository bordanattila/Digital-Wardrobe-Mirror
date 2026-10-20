"""Outfit use-case / orchestration layer."""

import logging
from itertools import islice, product

import requests

from app.database import Database
from app.schemas.clothing import ClothingItem
from app.schemas.outfit import Outfit, OutfitSuggestions
from app.services.wardrobe_service import list_clothing_items
from app.services.weather_service import get_current_weather
from app.utils.temperature_bands import determine_temperature_band

logger = logging.getLogger(__name__)

MAX_OUTFITS = 5
REQUIRED_CATEGORIES = ("top", "bottom", "shoes")


def _items_for_slot(
    wardrobe: list[ClothingItem],
    category: str,
    allowed: frozenset[str],
) -> list[ClothingItem]:
    return [
        item
        for item in wardrobe
        if item.category == category and item.subcategory in allowed
    ]


def generate_outfit_suggestions(db: Database) -> OutfitSuggestions:
    """Generate outfit suggestions based on weather bands and the wardrobe."""

    try:
        current_weather = get_current_weather()
        logger.info(
            "Current weather: %s, %s",
            current_weather.temperature_fahrenheit,
            current_weather.city,
        )
    except ValueError as exc:
        logger.warning(
            "Error getting current weather (value error): %s", type(exc).__name__
        )
        raise ValueError("Error getting current weather") from exc
    except requests.exceptions.RequestException as exc:
        logger.warning(
            "Error getting current weather (network error): %s", type(exc).__name__
        )
        raise

    band = determine_temperature_band(current_weather.temperature_fahrenheit)
    full_wardrobe = list_clothing_items(db)

    pooled: dict[str, list[ClothingItem]] = {}
    for category, allowed_subs in band.allow.items():
        pooled[category] = _items_for_slot(full_wardrobe, category, allowed_subs)

    if any(not pooled.get(category) for category in REQUIRED_CATEGORIES):
        logger.info("Missing required categories for band %s", band.label)
        return OutfitSuggestions(outfits=[], weather=current_weather)

    # Combine only slots this band uses and that have candidates
    slot_order = [category for category in band.allow if pooled.get(category)]
    combos = product(*(pooled[category] for category in slot_order))

    outfits: list[Outfit] = []
    for combo in islice(combos, MAX_OUTFITS):
        by_slot = dict(zip(slot_order, combo, strict=True))
        outfits.append(
            Outfit(
                top=[by_slot["top"]],
                bottom=[by_slot["bottom"]],
                shoes=[by_slot["shoes"]],
                mid_layer=[by_slot["mid_layer"]] if "mid_layer" in by_slot else [],
                outer_layer=[by_slot["outer_layer"]]
                if "outer_layer" in by_slot
                else [],
                score=0,
                reason=band.label,
            )
        )

    logger.info("Generated %s outfits for band %s", len(outfits), band.label)
    return OutfitSuggestions(outfits=outfits, weather=current_weather)
