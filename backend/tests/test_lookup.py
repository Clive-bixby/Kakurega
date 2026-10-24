import httpx

from app.services.metadata import MetadataLookupError


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeClient:
    def __init__(self, responses):
        self.responses = responses

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, url, params=None):
        response = self.responses.get(url)
        if isinstance(response, Exception):
            raise response
        return response


def test_lookup_open_library(client, monkeypatch):
    payload = {
        "ISBN:9780140328721": {
            "title": "Fantastic Mr Fox",
            "authors": [{"name": "Roald Dahl"}],
            "publishers": [{"name": "Puffin"}],
            "publish_date": "1993",
            "isbn_10": ["0140328726"],
            "isbn_13": ["9780140328721"],
            "cover": {"large": "https://example.com/cover.jpg"},
        }
    }
    monkeypatch.setattr(
        "app.services.metadata.httpx.Client",
        lambda timeout=5.0: FakeClient({"https://openlibrary.org/api/books": FakeResponse(payload)}),
    )
    response = client.post("/api/v1/lookup", json={"isbn": "9780140328721"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fantastic Mr Fox"
    assert data["authors"] == ["Roald Dahl"]
    assert data["source"] == "open_library"


def test_lookup_google_books_fallback(client, monkeypatch):
    open_response = FakeResponse({})
    google_response = FakeResponse(
        {
            "items": [
                {
                    "volumeInfo": {
                        "title": "Dune",
                        "authors": ["Frank Herbert"],
                        "publisher": "Chilton",
                        "publishedDate": "1965",
                        "industryIdentifiers": [
                            {"type": "ISBN_13", "identifier": "9780441013593"}
                        ],
                        "description": "A novel",
                        "imageLinks": {"thumbnail": "https://example.com/dune.jpg"},
                    }
                }
            ]
        }
    )
    def factory(timeout=5.0):
        return FakeClient(
                {
                    "https://openlibrary.org/api/books": open_response,
                    "https://openlibrary.org/search.json": open_response,
                    "https://www.googleapis.com/books/v1/volumes": google_response,
                }
        )
    monkeypatch.setattr("app.services.metadata.httpx.Client", factory)
    response = client.post("/api/v1/lookup", json={"title": "Dune"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Dune"
    assert data["source"] == "google_books"


def test_lookup_not_found(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.metadata.httpx.Client",
        lambda timeout=5.0: FakeClient(
            {
                "https://openlibrary.org/api/books": FakeResponse({}),
                "https://openlibrary.org/search.json": FakeResponse({"docs": []}),
                "https://www.googleapis.com/books/v1/volumes": FakeResponse({"items": []}),
            }
        ),
    )
    response = client.post("/api/v1/lookup", json={"title": "Unknown"})
    assert response.status_code == 404


def test_lookup_upstream_failure(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.metadata.httpx.Client",
        lambda timeout=5.0: FakeClient(
            {
                "https://openlibrary.org/api/books": httpx.ConnectError("boom"),
                "https://www.googleapis.com/books/v1/volumes": httpx.ConnectError("boom"),
            }
        ),
    )
    response = client.post("/api/v1/lookup", json={"isbn": "123"})
    assert response.status_code == 502
