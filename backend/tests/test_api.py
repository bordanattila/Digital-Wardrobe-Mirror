# tests/test_api.py

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database import Database
from app.main import app
from app.utils.dependencies import get_db
from tests.conftest import make_png_bytes


@pytest.fixture
def client(tmp_path, image_dirs):
    """TestClient with an isolated DB and image directories."""
    test_db_path = tmp_path / "api_test.db"

    def override_get_db():
        db = Database(test_db_path)
        db.create_table()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _create_item(client, name="Test Shirt"):
    png = make_png_bytes(color=(0, 0, 0), accent=(200, 50, 50))
    return client.post(
        "/api/wardrobe/",
        data={
            "name": name,
            "color": "red",
            "size": "M",
            "category": "top",
            "subcategory": "t-shirt",
        },
        files={"image": ("shirt.png", png, "image/png")},
    )


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Digital Wardrobe Mirror API"


def test_list_wardrobe_empty(client):
    response = client.get("/api/wardrobe/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_wardrobe_item(client, image_dirs):
    response = _create_item(client)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Test Shirt"
    assert body["color"] == "red"
    assert body["id"] == 1
    assert "processed" in body["image_path"]

    listed = client.get("/api/wardrobe/")
    assert listed.status_code == 200
    items = listed.json()
    assert len(items) == 1
    assert items[0]["name"] == "Test Shirt"


def test_get_wardrobe_item_by_id(client):
    created = _create_item(client).json()
    response = client.get(f"/api/wardrobe/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Shirt"


def test_get_wardrobe_item_not_found(client):
    response = client.get("/api/wardrobe/99")
    assert response.status_code == 404


def test_update_wardrobe_item(client):
    created = _create_item(client).json()
    response = client.put(
        f"/api/wardrobe/{created['id']}",
        data={
            "name": "Updated Shirt",
            "color": "blue",
            "size": "L",
            "category": "top",
            "subcategory": "polo",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Shirt"
    assert body["color"] == "blue"
    assert body["image_path"] == created["image_path"]


def test_update_wardrobe_item_not_found(client):
    response = client.put(
        "/api/wardrobe/99",
        data={
            "name": "X",
            "color": "red",
            "size": "M",
            "category": "top",
            "subcategory": "t-shirt",
        },
    )
    assert response.status_code == 404


def test_delete_wardrobe_item(client, image_dirs):
    created = _create_item(client).json()
    processed = created["image_path"]
    response = client.delete(f"/api/wardrobe/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""

    assert client.get(f"/api/wardrobe/{created['id']}").status_code == 404
    assert list(image_dirs["original"].iterdir()) == []
    assert not Path(processed).exists()


def test_delete_wardrobe_item_not_found(client):
    response = client.delete("/api/wardrobe/99")
    assert response.status_code == 404


def test_create_rejects_bad_extension(client):
    response = client.post(
        "/api/wardrobe/",
        data={
            "name": "Bad",
            "color": "red",
            "size": "M",
            "category": "top",
            "subcategory": "t-shirt",
        },
        files={"image": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_create_rejects_corrupt_image(client, image_dirs):
    response = client.post(
        "/api/wardrobe/",
        data={
            "name": "Corrupt",
            "color": "red",
            "size": "M",
            "category": "top",
            "subcategory": "t-shirt",
        },
        files={"image": ("bad.png", b"not-a-png", "image/png")},
    )
    assert response.status_code == 400
    assert list(image_dirs["original"].iterdir()) == []
