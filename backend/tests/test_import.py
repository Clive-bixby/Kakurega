import io

from app.models.book import Book


def post_csv(client, text: str, update_existing: bool = False):
    url = "/api/v1/import/csv"
    if update_existing:
        url += "?update_existing=true"
    return client.post(
        url,
        files={"file": ("books.csv", io.BytesIO(text.encode("utf-8")), "text/csv")},
    )


def isbn13_for(number: int) -> str:
    core = f"978{number:09d}"
    total = sum(
        int(char) * (1 if index % 2 == 0 else 3)
        for index, char in enumerate(core)
    )
    return core + str((10 - total % 10) % 10)


def test_import_creates_books_and_relationships(client):
    text = (
        "Title,Author,ISBN,ISBN13,Number of Pages,Publisher,Year Published,"
        "Bookshelves,Genres,My Review\n"
        'Dune,Frank Herbert,="0441013597",9780441013593,528,Ace,1965,'
        '"read, sci-fi","Science Fiction, Classic",Loved it\n'
    )

    response = post_csv(client, text)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["created"] == 1
    assert data["updated"] == 0
    assert data["skipped_duplicates"] == 0
    assert data["failed"] == []
    assert data["warnings"] == []
    assert data["ignored_columns"] == []

    db = client.app.state.session_factory()
    book = db.query(Book).one()
    assert book.title == "Dune"
    assert book.isbn10 == "0441013597"
    assert book.isbn13 == "9780441013593"
    assert book.pages == 528
    assert book.published_year == 1965
    assert book.notes == "Loved it"
    assert [author.name for author in book.authors] == ["Frank Herbert"]
    assert book.publisher.name == "Ace"
    assert sorted(genre.name for genre in book.genres) == [
        "Classic",
        "Science Fiction",
    ]
    assert [tag.name for tag in book.tags] == ["sci-fi"]
    db.close()


def test_reimport_creates_nothing(client):
    text = "title,isbn13\nDune,9780441013593\n"

    assert post_csv(client, text).json()["created"] == 1
    second = post_csv(client, text).json()

    assert second["created"] == 0
    assert second["skipped_duplicates"] == 1
    assert client.get("/api/v1/books").json()["total"] == 1


def test_update_existing_fills_blanks_without_overwriting(client):
    assert post_csv(client, "title,isbn13\nDune,9780441013593\n").json()["created"] == 1

    richer = (
        "title,isbn13,pages,my review,tags\n"
        "Different,9780441013593,528,Mine,sci-fi\n"
    )
    result = post_csv(client, richer, update_existing=True).json()

    assert result["created"] == 0
    assert result["updated"] == 1
    assert result["skipped_duplicates"] == 0

    db = client.app.state.session_factory()
    book = db.query(Book).one()
    assert book.title == "Dune"
    assert book.pages == 528
    assert book.notes == "Mine"
    assert [tag.name for tag in book.tags] == ["sci-fi"]

    overwrite = "title,isbn13,my review\nOther,9780441013593,Changed\n"
    assert post_csv(client, overwrite, update_existing=True).json()["updated"] == 1
    db.refresh(book)
    assert book.title == "Dune"
    assert book.notes == "Mine"
    db.close()


def test_invalid_isbn_is_a_warning_not_a_failure(client):
    result = post_csv(client, "title,isbn13\nBook,9780140328722\n").json()

    assert result["created"] == 1
    assert result["failed"] == []
    assert result["warnings"] == [
        {"row": 2, "reason": "Invalid ISBN; imported without ISBN"}
    ]

    db = client.app.state.session_factory()
    book = db.query(Book).one()
    assert book.isbn10 is None
    assert book.isbn13 is None
    db.close()


def test_one_bad_row_does_not_abort_the_file(client):
    text = "title,isbn13\n,9780140328721\nGood Book,9780306406157\n"

    result = post_csv(client, text).json()

    assert result["created"] == 1
    assert result["failed"] == [{"row": 2, "reason": "Missing title"}]
    assert client.get("/api/v1/books").json()["total"] == 1


def test_ignored_columns_are_reported(client):
    text = (
        "title,my rating,exclusive shelf,date read\n"
        "Book,5,read,2020/01/02\n"
    )

    result = post_csv(client, text).json()

    assert result["created"] == 1
    assert result["ignored_columns"] == ["my rating", "exclusive shelf", "date read"]


def test_missing_title_column_is_a_bad_request(client):
    response = post_csv(client, "author,isbn\nSomeone,9780140328721\n")

    assert response.status_code == 400
    assert "Title" in response.json()["detail"]


def test_empty_file_is_a_bad_request(client):
    response = client.post(
        "/api/v1/import/csv",
        files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
    )
    assert response.status_code == 400


def test_oversized_file_is_rejected(client):
    payload = b"title\n" + b"x" * (10 * 1024 * 1024)
    response = client.post(
        "/api/v1/import/csv",
        files={"file": ("big.csv", io.BytesIO(payload), "text/csv")},
    )
    assert response.status_code == 413


def test_500_row_goodreads_fixture(client):
    rows = [("Title,ISBN13")]
    for index in range(490):
        rows.append(f"Book {index},{isbn13_for(index)}")
    for index in range(5):
        rows.append(f"Book {index},{isbn13_for(index)}")
    for index in range(3):
        rows.append(f"Broken {index},9780140328722")
    rows.append(f",{isbn13_for(500)}")
    rows.append(f",{isbn13_for(501)}")
    text = "\n".join(rows) + "\n"

    first = post_csv(client, text).json()

    assert first["created"] == 493
    assert first["skipped_duplicates"] == 5
    assert len(first["failed"]) == 2
    assert first["warnings"] == [
        {"row": 497, "reason": "Invalid ISBN; imported without ISBN"},
        {"row": 498, "reason": "Invalid ISBN; imported without ISBN"},
        {"row": 499, "reason": "Invalid ISBN; imported without ISBN"},
    ]

    page = client.get("/api/v1/books?limit=50").json()
    assert page["total"] == 493
    assert len(page["items"]) == 50

    second = post_csv(client, text).json()

    assert second["created"] == 0
    assert second["skipped_duplicates"] == 498
    assert len(second["failed"]) == 2
    assert client.get("/api/v1/books").json()["total"] == 493
