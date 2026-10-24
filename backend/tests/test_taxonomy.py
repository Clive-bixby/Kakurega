def test_author_create_is_idempotent_and_case_insensitive(client):
    first = client.post("/api/v1/authors", json={"name": "  Ursula K. Le Guin  "})
    second = client.post("/api/v1/authors", json={"name": "ursula k. le guin"})

    assert first.status_code == 200
    assert first.json()["name"] == "Ursula K. Le Guin"
    assert second.json()["id"] == first.json()["id"]
    assert len(client.get("/api/v1/authors").json()) == 1


def test_blank_names_are_rejected(client):
    for path in ("authors", "publishers", "genres", "tags"):
        assert client.post(f"/api/v1/{path}", json={"name": "   "}).status_code == 422
        assert client.post(f"/api/v1/{path}", json={"name": ""}).status_code == 422


def test_taxonomy_lists_filter_and_sort_case_insensitively(client):
    for name in ("Zed", "alpha", "Beta"):
        client.post("/api/v1/authors", json={"name": name})

    all_names = [item["name"] for item in client.get("/api/v1/authors").json()]
    filtered = client.get("/api/v1/authors?q=et").json()

    assert all_names == ["alpha", "Beta", "Zed"]
    assert [item["name"] for item in filtered] == ["Beta"]


def test_taxonomy_search_treats_wildcards_literally(client):
    client.post("/api/v1/genres", json={"name": "100% Real"})
    client.post("/api/v1/genres", json={"name": "Plain"})

    result = client.get("/api/v1/genres?q=%25").json()

    assert [item["name"] for item in result] == ["100% Real"]


def test_taxonomy_limit_bounds(client):
    assert client.get("/api/v1/authors?limit=0").status_code == 422
    assert client.get("/api/v1/authors?limit=501").status_code == 422


def test_publisher_country_round_trips(client):
    created = client.post(
        "/api/v1/publishers", json={"name": "Ace", "country": "US"}
    ).json()

    assert created["country"] == "US"
    listed = client.get("/api/v1/publishers?q=ace").json()
    assert listed == [created]


def test_genre_and_tag_creation(client):
    genre = client.post("/api/v1/genres", json={"name": "Fantasy"}).json()
    tag = client.post("/api/v1/tags", json={"name": "sci-fi"}).json()

    assert genre["id"] > 0
    assert tag["id"] > 0
    assert client.get("/api/v1/genres").json()[0]["name"] == "Fantasy"
    assert client.get("/api/v1/tags").json()[0]["name"] == "sci-fi"
