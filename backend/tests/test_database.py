# tests/test_database.py
from app.database import Database


def test_add_clothing_item(tmp_path):
    db = Database(tmp_path / "test.db")
    db.create_table()
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    assert db.get_clothing_item_by_id(1) == (
        1,
        "Tee",
        "blue",
        "M",
        "tops",
        "tshirt",
        "/img/tee.png",
    )
    db.close()


def test_get_all_clothing_items(tmp_path):
    db = Database(tmp_path / "test.db")
    db.create_table()
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    assert db.get_all_clothing_items() == [
        (1, "Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    ]
    db.close()


def test_get_clothing_item_by_id(tmp_path):
    db = Database(tmp_path / "test.db")
    db.create_table()
    db.add_clothing_item("Tee", "blue", "M", "tops", "tshirt", "/img/tee.png")
    assert db.get_clothing_item_by_id(1) == (
        1,
        "Tee",
        "blue",
        "M",
        "tops",
        "tshirt",
        "/img/tee.png",
    )
    db.close()


def test_missing_item(tmp_path):
    db = Database(tmp_path / "test.db")
    db.create_table()
    assert db.get_clothing_item_by_id(1) is None
    db.close()


def test_close(tmp_path):
    db = Database(tmp_path / "test.db")
    db.close()
    assert db.conn.close() is None
