def test_insights(client):
    client.post("/api/v1/books", json={"title": "One", "published_year": 2020})
    client.post("/api/v1/books", json={"title": "Two", "published_year": 2020})
    client.post("/api/v1/books", json={"title": "Three", "published_year": 2021})

    response = client.get("/api/v1/insights")
    assert response.status_code == 200
    data = response.json()
    assert data["total_books"] == 3
    assert data["by_published_year"]["2020"] == 2
    assert data["by_published_year"]["2021"] == 1
    assert data["currently_reading"] == []


def test_insights_lists_currently_reading(client):
    book = client.post(
        "/api/v1/books", json={"title": "One", "pages": 300}
    ).json()
    member = client.post("/api/v1/members", json={"name": "Amy"}).json()
    client.put(
        f"/api/v1/books/{book['id']}/reading/{member['id']}",
        json={"status": "reading", "current_page": 75},
    )

    data = client.get("/api/v1/insights").json()
    assert data["currently_reading"] == [
        {
            "book_id": book["id"],
            "book_title": "One",
            "member_id": member["id"],
            "member_name": "Amy",
            "current_page": 75,
            "pages": 300,
        }
    ]
