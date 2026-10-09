import logging

import requests
from fastapi import APIRouter, Depends, HTTPException

from app.database import Database
from app.schemas.outfit import OutfitSuggestions
from app.services import outfit_service
from app.utils.dependencies import get_db
from app.utils.rate_limiter import rate_limit

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/suggest", response_model=OutfitSuggestions)
async def suggest_outfit(
    db: Database = Depends(get_db), _rate_limit: None = Depends(rate_limit)
):
    try:
        logger.info("Generating outfit suggestions")
        return outfit_service.generate_outfit_suggestions(db)
    except ValueError as exc:
        logger.warning("Outfit suggestions failed (config/data): %s", exc)
        detail = str(exc)
        status = 503 if "not configured" in detail.lower() else 502
        raise HTTPException(
            status_code=status, detail="Outfit suggestions service unavailable"
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.warning("Outfit suggestions failed (network error): %s", exc)
        raise HTTPException(
            status_code=502, detail="Outfit suggestions service unavailable"
        ) from exc
