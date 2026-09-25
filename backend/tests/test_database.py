# tests/test_database.py
from app.database import Database


def _as_dict(row):
    return dict(row)


def test_add_clothing_item(db):
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    row = db.get_clothing_item_by_id(1)
    assert _as_dict(row) == {
        "id": 1,
        "item_name": "Tee",
        "item_color": "blue",
        "item_size": "M",
        "item_category": "tops",
        "item_subcategory": "tshirt",
        "item_image_path": "/img/tee.png",
    }


def test_get_all_clothing_items(db):
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    rows = db.get_all_clothing_items()
    assert len(rows) == 1
    assert _as_dict(rows[0])["item_name"] == "Tee"


def test_get_clothing_item_by_id(db):
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    row = db.get_clothing_item_by_id(1)
    assert row["item_color"] == "blue"
    assert row["item_image_path"] == "/img/tee.png"


def test_missing_item(db):
    assert db.get_clothing_item_by_id(1) is None


def test_close(tmp_path):
    database = Database(tmp_path / "test.db")
    database.close()
    # Connection should be closed; further use raises ProgrammingError
    import sqlite3

    try:
        database.cursor.execute("SELECT 1")
        raised = False
    except sqlite3.ProgrammingError:
        raised = True
    assert raised
