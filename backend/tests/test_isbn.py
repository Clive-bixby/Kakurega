import pytest

from app.core.isbn import (
    canonicalize_isbns,
    is_valid_isbn10,
    is_valid_isbn13,
    isbn10_to_isbn13,
    isbn13_to_isbn10,
    isbn_search_terms,
    normalize_isbn,
)


def test_normalize_strips_hyphens_and_spaces():
    assert normalize_isbn("0-14-032872-6") == "0140328726"
    assert normalize_isbn("978 0140 328721") == "9780140328721"


def test_normalize_rejects_wrong_length():
    assert normalize_isbn("12345") is None
    assert normalize_isbn("") is None


def test_isbn10_checksum():
    assert is_valid_isbn10("0-14-032872-6")
    assert is_valid_isbn10("0140328726")
    assert not is_valid_isbn10("0140328727")


def test_isbn10_allows_trailing_x():
    assert is_valid_isbn10("080442957X")


def test_isbn13_checksum():
    assert is_valid_isbn13("9780140328721")
    assert not is_valid_isbn13("9780140328722")
    assert not is_valid_isbn13("9770140328721")


def test_convert_between_forms():
    assert isbn10_to_isbn13("0140328726") == "9780140328721"
    assert isbn13_to_isbn10("9780140328721") == "0140328726"


def test_979_has_no_isbn10():
    assert isbn13_to_isbn10("9791234567896") is None


def test_canonicalize_derives_missing_form():
    assert canonicalize_isbns("0140328726", None) == ("0140328726", "9780140328721")
    assert canonicalize_isbns(None, "9780140328721") == ("0140328726", "9780140328721")
    assert canonicalize_isbns(None, None) == (None, None)


def test_canonicalize_rejects_invalid_and_mismatched():
    with pytest.raises(ValueError):
        canonicalize_isbns("0140328727", None)
    with pytest.raises(ValueError):
        canonicalize_isbns("0140328726", "9780140328722")
    with pytest.raises(ValueError):
        canonicalize_isbns("0140328726", "9780306406157")


def test_search_terms_for_both_forms():
    assert isbn_search_terms("0-14-032872-6") == ("0140328726", "9780140328721")
    assert isbn_search_terms("9780140328721") == ("0140328726", "9780140328721")
    assert isbn_search_terms("dune") == (None, None)
