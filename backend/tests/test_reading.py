from datetime import date

TODAY = date.today().isoformat()


def _create_book(client, title="Reading Book", pages=300):
    response = client.post("/api/v1/books", json={"title": title, "pages": pages})
    assert response.status_code == 201, response.text
    return response.json()


def _create_member(client, name):
    response = client.post("/api/v1/members", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


def _read(client, book_id, member_id, **payload):
    return client.put(
        f"/api/v1/books/{book_id}/reading/{member_id}", json=payload
    )


def test_member_crud_and_case_insensitive_names(client):
    amy = _create_member(client, "  Amy  ")
    assert amy["name"] == "Amy"

    duplicate = client.post("/api/v1/members", json={"name": "amy"})
    assert duplicate.status_code == 409

    _create_member(client, "zed")
    _create_member(client, "Bea")
    names = [m["name"] for m in client.get("/api/v1/members").json()]
    assert names == ["Amy", "Bea", "zed"]

    renamed = client.patch(f"/api/v1/members/{amy['id']}", json={"name": "Amelia"})
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Amelia"

    clash = client.patch(f"/api/v1/members/{amy['id']}", json={"name": "bea"})
    assert clash.status_code == 409

    assert client.delete(f"/api/v1/members/{amy['id']}").status_code == 204
    assert client.delete(f"/api/v1/members/{amy['id']}").status_code == 404
    assert [m["name"] for m in client.get("/api/v1/members").json()] == ["Bea", "zed"]


def test_blank_member_name_rejected(client):
    assert client.post("/api/v1/members", json={"name": ""}).status_code == 422
    assert client.post("/api/v1/members", json={"name": "   "}).status_code == 422


def test_two_members_track_different_progress(client):
    book = _create_book(client)
    amy = _create_member(client, "Amy")
    sam = _create_member(client, "Sam")

    first = _read(client, book["id"], amy["id"], status="reading", current_page=40)
    second = _read(client, book["id"], sam["id"], status="reading", current_page=120)

    assert first.status_code == 200, first.text
    assert first.json()["started_on"] == TODAY
    assert first.json()["current_page"] == 40
    assert first.json()["member_name"] == "Amy"
    assert second.json()["current_page"] == 120

    entries = client.get(f"/api/v1/books/{book['id']}/reading").json()
    assert [(e["member_name"], e["current_page"]) for e in entries] == [
        ("Amy", 40),
        ("Sam", 120),
    ]

    all_entries = client.get("/api/v1/reading").json()
    assert len(all_entries) == 2
    assert {entry["book_title"] for entry in all_entries} == {book["title"]}


def test_book_filters_by_member_and_status(client):
    first = _create_book(client, title="First")
    second = _create_book(client, title="Second")
    amy = _create_member(client, "Amy")
    sam = _create_member(client, "Sam")
    _read(client, first["id"], amy["id"], status="reading")
    _read(client, first["id"], sam["id"], status="finished")
    _read(client, second["id"], amy["id"], status="finished")

    def titles(**params):
        response = client.get("/api/v1/books", params={"sort": "title", **params})
        assert response.status_code == 200, response.text
        return [item["title"] for item in response.json()["items"]]

    assert titles(member_id=amy["id"]) == ["First", "Second"]
    assert titles(member_id=sam["id"]) == ["First"]
    assert titles(status="reading") == ["First"]
    assert titles(member_id=amy["id"], status="finished") == ["Second"]
    assert titles(member_id=sam["id"], status="reading") == []
    assert titles(status="reading") == ["First"]


def test_finishing_sets_date_and_last_page(client):
    book = _create_book(client, pages=200)
    member = _create_member(client, "Amy")

    response = _read(client, book["id"], member["id"], status="finished")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["finished_on"] == TODAY
    assert data["current_page"] == 200

    with_page = _read(
        client,
        book["id"],
        member["id"],
        status="reading",
        current_page=50,
    ).json()
    assert with_page["current_page"] == 50
    assert with_page["started_on"] == TODAY
    assert with_page["finished_on"] is None


def test_progress_is_capped_by_pages(client):
    book = _create_book(client, pages=100)
    member = _create_member(client, "Amy")

    too_far = _read(client, book["id"], member["id"], status="reading", current_page=101)
    assert too_far.status_code == 422
    assert "100" in too_far.json()["detail"]

    at_end = _read(client, book["id"], member["id"], status="reading", current_page=100)
    assert at_end.status_code == 200

    negative = _read(client, book["id"], member["id"], status="reading", current_page=-1)
    assert negative.status_code == 422


def test_progress_needs_a_known_page_count(client):
    book = _create_book(client, pages=None)
    member = _create_member(client, "Amy")

    response = _read(
        client, book["id"], member["id"], status="reading", current_page=250
    )
    assert response.status_code == 200


def test_finished_before_started_is_rejected(client):
    book = _create_book(client)
    member = _create_member(client, "Amy")

    response = _read(
        client,
        book["id"],
        member["id"],
        status="finished",
        started_on="2026-05-02",
        finished_on="2026-05-01",
    )
    assert response.status_code == 422


def test_repeated_put_updates_the_same_entry(client):
    book = _create_book(client)
    member = _create_member(client, "Amy")

    first = _read(client, book["id"], member["id"], status="reading", current_page=10)
    second = _read(
        client,
        book["id"],
        member["id"],
        status="reading",
        current_page=25,
        note="  good so far  ",
    )

    assert first.json()["id"] == second.json()["id"]
    assert second.json()["current_page"] == 25
    assert second.json()["note"] == "good so far"
    assert len(client.get("/api/v1/reading").json()) == 1

    assert (
        client.delete(
            f"/api/v1/books/{book['id']}/reading/{member['id']}"
        ).status_code
        == 204
    )
    assert client.get("/api/v1/reading").json() == []
    assert (
        client.delete(
            f"/api/v1/books/{book['id']}/reading/{member['id']}"
        ).status_code
        == 404
    )


def test_reading_rejects_unknown_book_or_member(client):
    book = _create_book(client)
    member = _create_member(client, "Amy")

    assert _read(client, 999, member["id"], status="reading").status_code == 404
    assert _read(client, book["id"], 999, status="reading").status_code == 404
    assert client.get("/api/v1/books/999/reading").status_code == 404
    assert client.put("/api/v1/books/999/reading/999", json={"status": "reading"}).status_code == 404


def test_invalid_status_is_rejected(client):
    book = _create_book(client)
    member = _create_member(client, "Amy")

    assert (
        _read(client, book["id"], member["id"], status="paused").status_code == 422
    )
    assert client.get("/api/v1/reading?status=paused").status_code == 422


def test_reading_list_filters(client):
    first = _create_book(client, title="First")
    second = _create_book(client, title="Second")
    amy = _create_member(client, "Amy")
    sam = _create_member(client, "Sam")
    _read(client, first["id"], amy["id"], status="reading")
    _read(client, second["id"], amy["id"], status="finished")
    _read(client, second["id"], sam["id"], status="reading")

    amy_entries = client.get(f"/api/v1/reading?member_id={amy['id']}").json()
    assert len(amy_entries) == 2

    reading = client.get("/api/v1/reading?status=reading").json()
    assert {entry["book_title"] for entry in reading} == {"First", "Second"}
    assert {
        (entry["book_title"], entry["member_name"])
        for entry in reading
    } == {("First", "Amy"), ("Second", "Sam")}


def test_deleting_member_removes_their_entries(client):
    book = _create_book(client)
    member = _create_member(client, "Amy")
    _read(client, book["id"], member["id"], status="reading")

    assert client.delete(f"/api/v1/members/{member['id']}").status_code == 204
    assert client.get("/api/v1/reading").json() == []
    assert client.get(f"/api/v1/books/{book['id']}/reading").json() == []


def test_deleting_book_removes_its_entries(client):
    book = _create_book(client)
    member = _create_member(client, "Amy")
    _read(client, book["id"], member["id"], status="reading")

    assert client.delete(f"/api/v1/books/{book['id']}").status_code == 204
    assert client.get("/api/v1/reading").json() == []
    assert [m["name"] for m in client.get("/api/v1/members").json()] == ["Amy"]
