from sqlalchemy import event

from app.models.author import Author
from app.models.genre import Genre
from app.models.publisher import Publisher


def _create(client, **payload):
    response = client.post("/api/v1/books", json={"title": "Test Book", **payload})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_book(client):
    data = _create(client)
    assert data["title"] == "Test Book"
    assert data["id"] > 0
    assert data["created_at"]


def test_list_returns_page_envelope(client):
    _create(client)
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"items", "total", "limit", "offset"}
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Test Book"
    assert "description" not in data["items"][0]


def test_list_paginates(client):
    for index in range(5):
        _create(client, title=f"Book {index}")
    first = client.get("/api/v1/books?limit=2&offset=0").json()
    second = client.get("/api/v1/books?limit=2&offset=2").json()
    assert first["total"] == 5
    assert len(first["items"]) == 2
    assert len(second["items"]) == 2
    assert first["items"][0]["id"] != second["items"][0]["id"]


def test_list_sort_title_and_year(client):
    _create(client, title="Zebra", published_year=2000)
    _create(client, title="Apple", published_year=2020)
    titles = [b["title"] for b in client.get("/api/v1/books?sort=title").json()["items"]]
    years = [
        b["title"] for b in client.get("/api/v1/books?sort=year").json()["items"]
    ]
    assert titles == ["Apple", "Zebra"]
    assert years == ["Apple", "Zebra"]


def test_search_by_author_and_publisher(client):
    factory = client.app.state.session_factory
    db = factory()
    author = Author(name="Ursula Le Guin")
    publisher = Publisher(name="Ace Books")
    db.add_all([author, publisher])
    db.commit()
    _create(
        client,
        title="The Dispossessed",
        author_ids=[author.id],
        publisher_id=publisher.id,
    )
    _create(client, title="Unrelated")
    assert client.get("/api/v1/books?q=le%20guin").json()["total"] == 1
    assert client.get("/api/v1/books?q=ace").json()["total"] == 1
    db.close()


def test_search_treats_wildcards_literally(client):
    _create(client, title="100% Real")
    _create(client, title="Plain")
    result = client.get("/api/v1/books?q=%25").json()
    assert result["total"] == 1
    assert result["items"][0]["title"] == "100% Real"


def test_isbn_search_matches_either_form(client):
    created = _create(client, isbn10="0-14-032872-6")
    assert created["isbn13"] == "9780140328721"
    for query in ("9780140328721", "0-14-032872-6", "0140328726"):
        result = client.get("/api/v1/books", params={"q": query}).json()
        assert result["total"] == 1
        assert result["items"][0]["id"] == created["id"]


def test_duplicate_isbn_is_a_conflict(client):
    first = _create(client, title="First", isbn13="9780140328721")
    response = client.post(
        "/api/v1/books", json={"title": "Second", "isbn10": "0140328726"}
    )
    assert response.status_code == 409
    assert response.json()["detail"]["book_id"] == first["id"]
    assert client.get("/api/v1/books").json()["total"] == 1


def test_create_with_null_title_is_rejected(client):
    assert client.post("/api/v1/books", json={"title": None}).status_code == 422
    assert client.post("/api/v1/books", json={"title": "   "}).status_code == 422


def test_update_with_null_title_is_rejected(client):
    created = _create(client)
    response = client.put(f"/api/v1/books/{created['id']}", json={"title": None})
    assert response.status_code == 422


def test_pages_and_year_bounds(client):
    assert client.post(
        "/api/v1/books", json={"title": "Bad", "pages": 0}
    ).status_code == 422
    assert client.post(
        "/api/v1/books", json={"title": "Bad", "pages": 100_001}
    ).status_code == 422
    assert client.post(
        "/api/v1/books", json={"title": "Bad", "published_year": 999}
    ).status_code == 422
    assert client.post(
        "/api/v1/books", json={"title": "Bad", "published_year": 9999}
    ).status_code == 422


def test_invalid_isbn_is_rejected(client):
    response = client.post(
        "/api/v1/books", json={"title": "Bad ISBN", "isbn13": "9780140328722"}
    )
    assert response.status_code == 422


def test_list_query_count_is_constant(client):
    for index in range(10):
        _create(client, title=f"Book {index}")

    engine = client.app.state.engine
    statements: list[str] = []

    def before_cursor_execute(conn, cursor, statement, params, context, executemany):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        response = client.get("/api/v1/books?limit=20")
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)

    assert response.status_code == 200
    assert len(response.json()["items"]) == 10
    assert len(statements) <= 5, statements


def test_update_without_isbn_keeps_isbn(client):
    created = _create(client, isbn10="0140328726")
    updated = client.put(
        f"/api/v1/books/{created['id']}", json={"title": "Renamed"}
    ).json()
    assert updated["title"] == "Renamed"
    assert updated["isbn10"] == "0140328726"
    assert updated["isbn13"] == "9780140328721"


def test_update_book(client):
    created = _create(client)
    response = client.put(f"/api/v1/books/{created['id']}", json={"title": "New"})
    assert response.status_code == 200
    assert response.json()["title"] == "New"


def test_delete_book(client):
    created = _create(client, title="Delete")
    assert client.delete(f"/api/v1/books/{created['id']}").status_code == 204
    assert client.get(f"/api/v1/books/{created['id']}").status_code == 404


def test_book_not_found(client):
    assert client.get("/api/v1/books/999").status_code == 404
    assert client.get("/api/v1/books").json()["total"] == 0
    assert client.put("/api/v1/books/999", json={"title": "X"}).status_code == 404
    assert client.delete("/api/v1/books/999").status_code == 404


def test_invalid_relationship_ids(client):
    assert client.post("/api/v1/books", json={"title": "Bad", "publisher_id": 999}).status_code == 400
    assert client.post("/api/v1/books", json={"title": "Bad", "author_ids": [999]}).status_code == 400
    assert client.post("/api/v1/books", json={"title": "Bad", "genre_ids": [999]}).status_code == 400


def test_valid_relationship_ids(client):
    factory = client.app.state.session_factory
    db = factory()
    publisher = Publisher(name="Pub")
    author = Author(name="Author")
    genre = Genre(name="Genre")
    db.add_all([publisher, author, genre])
    db.commit()
    response = client.post(
        "/api/v1/books",
        json={
            "title": "Related",
            "publisher_id": publisher.id,
            "author_ids": [author.id],
            "genre_ids": [genre.id],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["publisher_id"] == publisher.id
    assert data["author_ids"] == [author.id]
    assert data["genre_ids"] == [genre.id]
    assert client.get(f"/api/v1/books?genre_id={genre.id}").json()["total"] == 1
    db.close()


def test_search_endpoint_is_gone(client):
    assert client.get("/api/v1/search?q=dune").status_code == 404
