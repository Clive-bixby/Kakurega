def test_insights(client):
    client.post("/api/v1/books", json={"title": "One", "published_year": 2020})
    client.post("/api/v1/books", json={"title": "Two", "published_year": 2020})
    client.post("/api/v1/books", json={"title": "Three", "published_year": 2021})

    response = client.get("/api/v1/insights")
    assert response.status_code == 200
    data = response.json()
    assert data["total_books"] == 3
    assert data["total_members"] == 0
    assert data["by_published_year"]["2020"] == 2
    assert data["by_published_year"]["2021"] == 1
    assert data["by_genre"] == []
    assert data["by_author"] == []
    assert data["by_language"] == {}
    assert data["currently_reading"] == []
    assert [item["title"] for item in data["recently_added"]] == [
        "Three",
        "Two",
        "One",
    ]


def test_insights_lists_currently_reading(client):
    author = client.post("/api/v1/authors", json={"name": "Amy Author"}).json()
    book = client.post(
        "/api/v1/books",
        json={
            "title": "One",
            "pages": 300,
            "cover_url": "/storage/images/one.jpg",
            "author_ids": [author["id"]],
        },
    ).json()
    member = client.post("/api/v1/members", json={"name": "Amy"}).json()
    client.put(
        f"/api/v1/books/{book['id']}/reading/{member['id']}",
        json={"status": "reading", "current_page": 75},
    )

    data = client.get("/api/v1/insights").json()
    assert data["total_members"] == 1
    assert data["currently_reading"] == [
        {
            "book_id": book["id"],
            "book_title": "One",
            "cover_url": "/storage/images/one.jpg",
            "author_name": "Amy Author",
            "member_id": member["id"],
            "member_name": "Amy",
            "current_page": 75,
            "pages": 300,
        }
    ]
    assert data["recently_added"][0]["author_name"] == "Amy Author"


def _named(client, kind, name):
    response = client.post(f"/api/v1/{kind}", json={"name": name})
    assert response.status_code == 200, response.text
    return response.json()


def test_insights_breakdowns(client):
    fantasy = _named(client, "genres", "Fantasy")
    novel = _named(client, "genres", "Novel")
    art = _named(client, "genres", "Art")
    le_guin = _named(client, "authors", "Ursula Le Guin")
    butler = _named(client, "authors", "Octavia Butler")

    books = [
        {
            "title": "One",
            "language": "English",
            "genre_ids": [fantasy["id"], novel["id"]],
            "author_ids": [le_guin["id"]],
        },
        {
            "title": "Two",
            "language": "English",
            "genre_ids": [fantasy["id"]],
            "author_ids": [le_guin["id"]],
        },
        {
            "title": "Three",
            "language": "French",
            "genre_ids": [novel["id"], art["id"]],
            "author_ids": [butler["id"]],
        },
    ]
    for payload in books:
        response = client.post("/api/v1/books", json=payload)
        assert response.status_code == 201, response.text

    data = client.get("/api/v1/insights").json()
    assert data["by_language"] == {"English": 2, "French": 1}
    assert [(item["name"], item["count"]) for item in data["by_genre"]] == [
        ("Fantasy", 2),
        ("Novel", 2),
        ("Art", 1),
    ]
    assert [(item["name"], item["count"]) for item in data["by_author"]] == [
        ("Ursula Le Guin", 2),
        ("Octavia Butler", 1),
    ]


def test_insights_recently_added_and_top_ten(client):
    created = []
    for index in range(12):
        response = client.post(
            "/api/v1/books",
            json={"title": f"Book {index:02d}", "language": "English"},
        )
        assert response.status_code == 201, response.text
        created.append(response.json())

    for index in range(12):
        author = _named(client, "authors", f"Author {index:02d}")
        genre = _named(client, "genres", f"Genre {index:02d}")
        response = client.put(
            f"/api/v1/books/{created[index]['id']}",
            json={"author_ids": [author["id"]], "genre_ids": [genre["id"]]},
        )
        assert response.status_code == 200, response.text

    data = client.get("/api/v1/insights").json()
    assert len(data["by_author"]) == 10
    assert len(data["by_genre"]) == 10
    assert [item["name"] for item in data["by_author"]] == [
        f"Author {index:02d}" for index in range(10)
    ]

    assert [item["title"] for item in data["recently_added"]] == [
        f"Book {index:02d}" for index in range(11, 6, -1)
    ]
    assert data["recently_added"][0]["book_id"] == created[-1]["id"]
    assert data["recently_added"][0]["created_at"]
