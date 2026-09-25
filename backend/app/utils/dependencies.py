"""Dependency functions for the app."""

from collections.abc import Generator

from app.database import Database

DB_PATH = "digital_wardrobe_mirror.db"


def get_db() -> Generator[Database, None, None]:
    db = Database(DB_PATH)
    try:
        yield db
    finally:
        db.close()
