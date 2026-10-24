import logging
from types import SimpleNamespace

import httpx
import pytest

from app.services.metadata import (
    GOOGLE_BOOKS_URL,
    OPEN_LIBRARY_SEARCH_URL,
    OPEN_LIBRARY_URL,
    reset_lookup_state,
)


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class FakeClient:
    def __init__(self, responses, calls):
        self.responses = responses
        self.calls = calls

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, url, params=None):
        self.calls.append({"url": url, "params": dict(params or {})})
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        return response


def install(monkeypatch, responses, calls=None):
    calls = calls if calls is not None else []
    monkeypatch.setattr(
        "app.services.metadata.httpx.Client",
        lambda timeout=5.0: FakeClient(responses, calls),
    )
    return calls


@pytest.fixture(autouse=True)
def clear_lookup_state():
    reset_lookup_state()
    yield
    reset_lookup_state()


def open_library_payload(**overrides):
    payload = {
        "title": "Fantastic Mr Fox",
        "authors": [{"name": "Roald Dahl"}],
        "publishers": [{"name": "Puffin"}],
        "publish_date": "1993",
        "isbn_10": ["0140328726"],
        "isbn_13": ["9780140328721"],
        "cover": {"large": "https://example.com/cover.jpg"},
        "number_of_pages": 96,
    }
    payload.update(overrides)
    return {"ISBN:9780140328721": payload}


def google_payload(isbn: str = "9780140328721", title: str = "Dune"):
    return {
        "items": [
            {
                "volumeInfo": {
                    "title": title,
                    "authors": ["Frank Herbert"],
                    "publisher": "Chilton",
                    "publishedDate": "1965",
                    "industryIdentifiers": [
                        {"type": "ISBN_13", "identifier": isbn}
                    ],
                    "description": "A novel",
                    "imageLinks": {"thumbnail": "https://example.com/dune.jpg"},
                    "pageCount": 412,
                }
            }
        ]
    }


def test_open_library_success_does_not_call_google(client, monkeypatch):
    calls = install(
        monkeypatch, {OPEN_LIBRARY_URL: FakeResponse(open_library_payload())}
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9780140328721"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fantastic Mr Fox"
    assert data["authors"] == ["Roald Dahl"]
    assert data["pages"] == 96
    assert data["source"] == "open_library"
    assert [call["url"] for call in calls] == [OPEN_LIBRARY_URL]


def test_open_library_404_falls_back_to_google(client, monkeypatch):
    calls = install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: FakeResponse({}, status_code=404),
            GOOGLE_BOOKS_URL: FakeResponse(google_payload(isbn="9789388304771")),
        },
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9789388304771"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Dune"
    assert data["source"] == "google_books"
    assert [call["url"] for call in calls] == [OPEN_LIBRARY_URL, GOOGLE_BOOKS_URL]


def test_google_volume_for_a_different_isbn_is_rejected(client, monkeypatch):
    install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: FakeResponse({}),
            GOOGLE_BOOKS_URL: FakeResponse(google_payload(isbn="9780441013593")),
        },
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9789388304771"})

    assert response.status_code == 404


def test_open_library_failure_then_google_quota(client, monkeypatch):
    calls = install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: httpx.ConnectError("open library down"),
            GOOGLE_BOOKS_URL: FakeResponse(
                {
                    "error": {
                        "code": 429,
                        "message": "Quota exceeded for quota metric 'Queries'",
                        "status": "RESOURCE_EXHAUSTED",
                        "errors": [{"reason": "rateLimitExceeded"}],
                    }
                },
                status_code=429,
            ),
        },
    )

    first = client.post("/api/v1/lookup", json={"isbn": "9789388304771"})
    second = client.post("/api/v1/lookup", json={"isbn": "9789388304771"})

    assert first.status_code == 503
    assert "quota" in first.json()["detail"].lower()
    assert "manually" in first.json()["detail"].lower()
    assert second.status_code == 503
    google_calls = [call for call in calls if call["url"] == GOOGLE_BOOKS_URL]
    # A quota-exceeded response is never retried within the back-off window.
    assert len(google_calls) == 1


def test_both_providers_fail_gracefully(client, monkeypatch):
    install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: httpx.ConnectError("no network"),
            GOOGLE_BOOKS_URL: httpx.TimeoutException("too slow"),
        },
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9780140328721"})

    assert response.status_code == 502
    assert "manually" in response.json()["detail"].lower()


def test_both_providers_return_no_metadata(client, monkeypatch):
    install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: FakeResponse({}),
            GOOGLE_BOOKS_URL: FakeResponse({"items": []}),
        },
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9789388304771"})

    assert response.status_code == 404


def test_hyphenated_isbn13_is_normalized(client, monkeypatch):
    calls = install(
        monkeypatch, {OPEN_LIBRARY_URL: FakeResponse(open_library_payload())}
    )

    response = client.post(
        "/api/v1/lookup", json={"isbn": "978-0-14-032872-1"}
    )

    assert response.status_code == 200
    assert calls[0]["params"]["bibkeys"] == "ISBN:9780140328721"


def test_isbn10_is_normalized_and_both_forms_returned(client, monkeypatch):
    calls = install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: FakeResponse(
                {"ISBN:9780140328721": {"title": "Fantastic Mr Fox"}}
            )
        },
    )

    response = client.post("/api/v1/lookup", json={"isbn": "0 14 032872 6"})

    assert response.status_code == 200
    assert calls[0]["params"]["bibkeys"] == "ISBN:9780140328721"
    data = response.json()
    assert data["isbn10"] == "0140328726"
    assert data["isbn13"] == "9780140328721"


def test_invalid_checksum_is_rejected_without_provider_calls(client, monkeypatch):
    calls = install(
        monkeypatch, {OPEN_LIBRARY_URL: FakeResponse(open_library_payload())}
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9780140328722"})

    assert response.status_code == 422
    assert "Invalid ISBN-13" in response.json()["detail"]
    assert calls == []


def test_partial_metadata_is_returned(client, monkeypatch):
    install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: FakeResponse(
                {"ISBN:9780140328721": {"title": "Bare Edition"}}
            )
        },
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9780140328721"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Bare Edition"
    assert data["authors"] == []
    assert data["publisher"] is None
    assert data["pages"] is None
    assert data["isbn10"] == "0140328726"
    assert data["isbn13"] == "9780140328721"


def test_unusable_open_library_payload_falls_back(client, monkeypatch):
    install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: FakeResponse(
                {"ISBN:9780140328721": {"authors": [{"name": "Anonymous"}]}}
            ),
            GOOGLE_BOOKS_URL: FakeResponse(google_payload()),
        },
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9780140328721"})

    assert response.status_code == 200
    assert response.json()["source"] == "google_books"


def test_malformed_open_library_json_falls_back(client, monkeypatch):
    install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: FakeResponse(ValueError("not json")),
            GOOGLE_BOOKS_URL: FakeResponse(google_payload()),
        },
    )

    response = client.post("/api/v1/lookup", json={"isbn": "9780140328721"})

    assert response.status_code == 200
    assert response.json()["source"] == "google_books"


def test_successful_isbn_lookup_is_cached(client, monkeypatch):
    calls = install(
        monkeypatch, {OPEN_LIBRARY_URL: FakeResponse(open_library_payload())}
    )

    first = client.post("/api/v1/lookup", json={"isbn": "9780140328721"})
    second = client.post("/api/v1/lookup", json={"isbn": "978-0-14-032872-1"})

    assert first.status_code == second.status_code == 200
    assert len(calls) == 1


def test_google_api_key_is_sent_but_never_logged(
    client, monkeypatch, caplog
):
    calls = install(
        monkeypatch,
        {
            OPEN_LIBRARY_URL: FakeResponse({}),
            GOOGLE_BOOKS_URL: FakeResponse(
                {
                    "error": {
                        "code": 429,
                        "message": "Quota exceeded for quota metric 'Queries'",
                        "status": "RESOURCE_EXHAUSTED",
                        "errors": [{"reason": "rateLimitExceeded"}],
                    }
                },
                status_code=429,
            ),
        },
    )
    monkeypatch.setattr(
        "app.services.metadata.get_settings",
        lambda: SimpleNamespace(google_books_api_key="secret-test-key"),
    )
    caplog.set_level(logging.DEBUG)

    response = client.post("/api/v1/lookup", json={"isbn": "9780140328721"})

    assert response.status_code == 503
    google_call = next(call for call in calls if call["url"] == GOOGLE_BOOKS_URL)
    assert google_call["params"]["key"] == "secret-test-key"
    assert "secret-test-key" not in caplog.text
    assert "secret-test-key" not in response.text


def test_title_lookup_falls_back_to_google(client, monkeypatch):
    calls = install(
        monkeypatch,
        {
            OPEN_LIBRARY_SEARCH_URL: FakeResponse({"docs": []}),
            GOOGLE_BOOKS_URL: FakeResponse(google_payload()),
        },
    )

    response = client.post("/api/v1/lookup", json={"title": "Dune"})

    assert response.status_code == 200
    assert response.json()["source"] == "google_books"
    assert [call["url"] for call in calls] == [
        OPEN_LIBRARY_SEARCH_URL,
        GOOGLE_BOOKS_URL,
    ]
