import io

import pytest
from PIL import Image


@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.upload.IMAGES_DIR", tmp_path)
    return tmp_path


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "white").save(buffer, format="PNG")
    return buffer.getvalue()


def test_upload_valid_image(client, temp_storage):
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.png", io.BytesIO(_png_bytes()), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["image_id"]
    assert data["path"] == f"/storage/images/{data['image_id']}.png"
    assert (temp_storage / f"{data['image_id']}.png").exists()


def test_upload_ignores_client_extension(client):
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("evil.html", io.BytesIO(_png_bytes()), "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["path"].endswith(".png")


def test_upload_rejects_non_image_bytes(client):
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("fake.png", io.BytesIO(b"<script>alert(1)</script>"), "image/png")},
    )
    assert response.status_code == 400


def test_upload_invalid_mime(client):
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


def test_upload_empty_file(client):
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
    )
    assert response.status_code == 400


def test_upload_oversized_file(client):
    response = client.post(
        "/api/v1/upload/image",
        files={"file": ("big.png", io.BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "image/png")},
    )
    assert response.status_code == 413
