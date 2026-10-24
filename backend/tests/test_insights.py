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
