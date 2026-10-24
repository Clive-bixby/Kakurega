def _tag(client, name):
    response = client.post("/api/v1/tags", json={"name": name})
    assert response.status_code == 200, response.text
    return response.json()


def _book(client, title, **payload):
    response = client.post("/api/v1/books", json={"title": title, **payload})
    assert response.status_code == 201, response.text
    return response.json()


def _titles(client, **params):
    response = client.get("/api/v1/books", params={"sort": "title", **params})
    assert response.status_code == 200, response.text
    return [item["title"] for item in response.json()["items"]]


def test_tag_list_includes_book_counts(client):
    fantasy = _tag(client, "Fantasy")
    space = _tag(client, "Space")
    _tag(client, "Unused")
    _book(client, "One", tag_ids=[fantasy["id"]])
    _book(client, "Two", tag_ids=[fantasy["id"], space["id"]])

    tags = client.get("/api/v1/tags").json()
    assert [(tag["name"], tag["book_count"]) for tag in tags] == [
        ("Fantasy", 2),
        ("Space", 1),
        ("Unused", 0),
    ]

    filtered = client.get("/api/v1/tags?q=fanta").json()
    assert filtered == [{"id": fantasy["id"], "name": "Fantasy", "book_count": 2}]


def test_tag_names_are_case_insensitive(client):
    first = _tag(client, "  Fantasy  ")
    assert first["name"] == "Fantasy"
    assert first["book_count"] == 0

    repeated = _tag(client, "fantasy")
    assert repeated["id"] == first["id"]
    assert repeated["name"] == "Fantasy"

    assert client.post("/api/v1/tags", json={"name": "  "}).status_code == 422


def test_rename_tag_keeps_books_and_counts(client):
    tag = _tag(client, "Fantasy")
    book = _book(client, "One", tag_ids=[tag["id"]])

    renamed = client.patch(
        f"/api/v1/tags/{tag['id']}", json={"name": "  Epic Fantasy  "}
    )
    assert renamed.status_code == 200, renamed.text
    assert renamed.json() == {
        "id": tag["id"],
        "name": "Epic Fantasy",
        "book_count": 1,
    }
    assert client.get(f"/api/v1/books/{book['id']}").json()["tags"] == [
        {"id": tag["id"], "name": "Epic Fantasy"}
    ]


def test_rename_tag_rejects_duplicates_and_unknown(client):
    _tag(client, "Fantasy")
    second = _tag(client, "Space")

    clash = client.patch(
        f"/api/v1/tags/{second['id']}", json={"name": "fantasy"}
    )
    assert clash.status_code == 409

    blank = client.patch(f"/api/v1/tags/{second['id']}", json={"name": "  "})
    assert blank.status_code == 422

    assert (
        client.patch("/api/v1/tags/999", json={"name": "Missing"}).status_code
        == 404
    )


def test_delete_tag_removes_it_from_books(client):
    tag = _tag(client, "Fantasy")
    other = _tag(client, "Space")
    book = _book(client, "One", tag_ids=[tag["id"], other["id"]])

    assert client.delete(f"/api/v1/tags/{tag['id']}").status_code == 204
    assert client.delete(f"/api/v1/tags/{tag['id']}").status_code == 404

    assert [item["name"] for item in client.get("/api/v1/tags").json()] == [
        "Space"
    ]
    assert client.get(f"/api/v1/books/{book['id']}").json()["tags"] == [
        {"id": other["id"], "name": "Space"}
    ]


def test_book_list_filters_by_tag(client):
    fantasy = _tag(client, "Fantasy")
    space = _tag(client, "Space")
    genre = client.post("/api/v1/genres", json={"name": "Novel"}).json()

    _book(
        client,
        "Old Fantasy",
        tag_ids=[fantasy["id"]],
        genre_ids=[genre["id"]],
        published_year=1999,
    )
    _book(
        client,
        "New Fantasy",
        tag_ids=[fantasy["id"]],
        genre_ids=[genre["id"]],
        published_year=2020,
    )
    _book(client, "Space Opera", tag_ids=[space["id"]], published_year=2020)

    assert _titles(client, tag="Fantasy") == ["New Fantasy", "Old Fantasy"]
    assert _titles(client, tag="fantasy") == ["New Fantasy", "Old Fantasy"]
    assert _titles(client, tag="Space") == ["Space Opera"]
    assert _titles(client, tag="Fantasy", year_from=2000) == ["New Fantasy"]
    assert _titles(client, tag="Fantasy", genre_id=genre["id"]) == [
        "New Fantasy",
        "Old Fantasy",
    ]
    assert _titles(client, tag="Ghosts") == []


def test_notes_round_trip(client):
    book = _book(client, "Annotated", notes="  Household favourite  ")
    assert book["notes"] == "Household favourite"

    updated = client.put(
        f"/api/v1/books/{book['id']}", json={"notes": "Lent to Maya"}
    ).json()
    assert updated["notes"] == "Lent to Maya"
    assert client.get(f"/api/v1/books/{book['id']}").json()["notes"] == (
        "Lent to Maya"
    )
