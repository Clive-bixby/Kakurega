from app.models.author import Author
from app.models.genre import Genre
from app.models.publisher import Publisher


def test_create_book(client):
    response = client.post("/api/v1/books", json={"title": "Test Book"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["id"] > 0


def test_list_and_get_book(client):
    created = client.post("/api/v1/books", json={"title": "Listed"}).json()
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    assert len(response.json()) == 1
    response = client.get(f"/api/v1/books/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Listed"


def test_update_book(client):
    created = client.post("/api/v1/books", json={"title": "Old"}).json()
    response = client.put(f"/api/v1/books/{created['id']}", json={"title": "New"})
    assert response.status_code == 200
    assert response.json()["title"] == "New"


def test_delete_book(client):
    created = client.post("/api/v1/books", json={"title": "Delete"}).json()
    response = client.delete(f"/api/v1/books/{created['id']}")
    assert response.status_code == 204
    response = client.get(f"/api/v1/books/{created['id']}")
    assert response.status_code == 404


def test_book_not_found(client):
    assert client.get("/api/v1/books/999").status_code == 404
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
    db.close()
