import pytest

from app.core.csv_import import parse_csv


def test_goodreads_row_is_parsed():
    data = (
        "Title,Author,ISBN,ISBN13,Number of Pages,Publisher,Year Published,"
        "Bookshelves,My Review,Date Read,My Rating,Exclusive Shelf,Book Id\n"
        'Dune,Frank Herbert,="0441013597",9780441013593,528,Ace,1965,'
        '"read, sci-fi",Loved it,2020/01/02,5,read,2347\n'
    ).encode()

    parsed = parse_csv(data)

    assert len(parsed.rows) == 1
    row = parsed.rows[0]
    assert row.row_number == 2
    assert row.title == "Dune"
    assert row.authors == ["Frank Herbert"]
    assert row.isbn10 == "0441013597"
    assert row.isbn13 == "9780441013593"
    assert row.pages == 528
    assert row.publisher == "Ace"
    assert row.published_year == 1965
    assert row.tags == ["sci-fi"]
    assert row.genres == []
    assert row.notes == "Loved it"
    assert row.warnings == []
    assert parsed.ignored_columns == [
        "Date Read",
        "My Rating",
        "Exclusive Shelf",
        "Book Id",
    ]


def test_headers_are_case_and_space_insensitive_with_bom():
    data = '\ufeffTITLE,Author(s),Published_Year,Page Count\nDune,Frank Herbert,1965,528\n'
    parsed = parse_csv(data.encode("utf-8"))

    row = parsed.rows[0]
    assert row.title == "Dune"
    assert row.authors == ["Frank Herbert"]
    assert row.published_year == 1965
    assert row.pages == 528


def test_tags_and_genres_split_and_dedupe():
    data = (
        "title,tags,genres\n"
        'Book,"read; sci-fi, fantasy","Fantasy, Epic; fantasy"\n'
    ).encode()

    row = parse_csv(data).rows[0]

    assert row.tags == ["sci-fi", "fantasy"]
    assert row.genres == ["Fantasy", "Epic"]


def test_default_goodreads_shelves_are_dropped():
    data = b"title,bookshelves\nBook,read\n"
    assert parse_csv(data).rows[0].tags == []


def test_authors_split_on_semicolon_not_comma():
    data = b'title,author\nBook,"Austen, Jane; Editor, Some"\n'
    assert parse_csv(data).rows[0].authors == ["Austen, Jane", "Editor, Some"]


def test_invalid_isbn_becomes_a_warning_without_an_isbn():
    data = b"title,isbn13\nBook,9780140328722\n"
    row = parse_csv(data).rows[0]

    assert row.isbn13 is None
    assert row.isbn10 is None
    assert row.warnings == ["Invalid ISBN; imported without ISBN"]


def test_mismatched_pair_uses_the_valid_half():
    data = b"title,isbn,isbn13\nBook,0140328726,9780306406157\n"
    row = parse_csv(data).rows[0]

    assert row.isbn10 == "0140328726"
    assert row.isbn13 == "9780140328721"
    assert row.warnings == ["ISBN pair invalid; used ISBN-10"]


def test_invalid_pages_and_year_become_warnings():
    data = b"title,pages,published_year\nBook,0,9999\n"
    row = parse_csv(data).rows[0]

    assert row.pages is None
    assert row.published_year is None
    assert row.warnings == ["Invalid pages; ignored", "Invalid published year; ignored"]


def test_non_numeric_pages_become_a_warning():
    data = b"title,pages\nBook,many\n"
    row = parse_csv(data).rows[0]

    assert row.pages is None
    assert row.warnings == ["Invalid pages; ignored"]


def test_missing_title_header_is_rejected():
    with pytest.raises(ValueError, match="Title"):
        parse_csv(b"author,isbn\nSomeone,9780140328721\n")


def test_empty_file_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        parse_csv(b"")


def test_blank_rows_are_skipped_but_row_numbers_stay():
    data = b"title\nFirst\n\nSecond\n"
    rows = parse_csv(data).rows

    assert [(row.row_number, row.title) for row in rows] == [
        (2, "First"),
        (4, "Second"),
    ]


def test_missing_title_is_kept_for_the_importer_to_fail():
    data = b"title,author\n,Someone\n"
    row = parse_csv(data).rows[0]

    assert row.title == ""
    assert row.authors == ["Someone"]


def test_long_title_is_truncated_with_a_warning():
    data = b"title\n" + (b"x" * 501) + b"\n"
    row = parse_csv(data).rows[0]

    assert len(row.title) == 500
    assert row.warnings == ["Title truncated to 500 characters"]
