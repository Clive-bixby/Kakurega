import io

from app.services.barcode import isbn_from_barcode_text


def test_isbn_from_valid_isbn13():
    assert isbn_from_barcode_text("9780140328721") == "9780140328721"
    assert isbn_from_barcode_text("979-12-345-6789-6") == "9791234567896"


def test_isbn_from_valid_isbn10():
    assert isbn_from_barcode_text("0-14-032872-6") == "0140328726"


def test_grocery_ean_is_rejected():
    # Valid EAN-13 checksum, but not a book prefix
    assert isbn_from_barcode_text("4006381333931") is None


def test_bad_checksum_is_rejected():
    assert isbn_from_barcode_text("9780140328722") is None
    assert isbn_from_barcode_text("0140328727") is None


def test_non_numeric_text_is_rejected():
    assert isbn_from_barcode_text("hello world") is None
    assert isbn_from_barcode_text("") is None


def test_barcode_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.v1.routes.barcode.decode_barcode", lambda data: "9780140328721"
    )
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


def test_barcode_oversized_file(client):
    response = client.post(
        "/api/v1/barcode",
        files={
            "file": (
                "big.png",
                io.BytesIO(b"x" * (5 * 1024 * 1024 + 1)),
                "image/png",
            )
        },
    )
    assert response.status_code == 413
