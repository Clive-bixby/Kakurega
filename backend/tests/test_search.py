def test_search_books(client):
    client.post("/api/v1/books", json={"title": "Alpha Book"})
    client.post("/api/v1/books", json={"title": "Beta Book"})

    response = client.get("/api/v1/search?q=alpha")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Alpha Book"

    response = client.get("/api/v1/search?q=gamma")
    assert response.status_code == 200
    assert response.json() == []
