import io

from app.services.barcode import decode_barcode


def test_barcode_success(client, monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.barcode.decode_barcode", lambda data: "9780140328721")
    response = client.post(
        "/api/v1/barcode",
        files={"file": ("test.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )
    assert response.status_code == 200
    assert response.json() == {"isbn": "9780140328721"}


def test_barcode_not_found(client, monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.barcode.decode_barcode", lambda data: None)
    response = client.post(
        "/api/v1/barcode",
        files={"file": ("test.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )
    assert response.status_code == 404


def test_barcode_invalid_image(client, monkeypatch):
    def raise_error(data):
        raise ValueError("Invalid image")

    monkeypatch.setattr("app.api.v1.routes.barcode.decode_barcode", raise_error)
    response = client.post(
        "/api/v1/barcode",
        files={"file": ("test.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )
    assert response.status_code == 400


def test_barcode_invalid_mime(client):
    response = client.post(
        "/api/v1/barcode",
        files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


def test_barcode_empty_file(client):
    response = client.post(
        "/api/v1/barcode",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
    )
    assert response.status_code == 400
