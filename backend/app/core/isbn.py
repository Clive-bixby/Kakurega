import re

_DIGITS = re.compile(r"[^0-9Xx]")


def _clean(value: str) -> str:
    return _DIGITS.sub("", value).upper()


def normalize_isbn(value: str | None) -> str | None:
    """Return digits-only ISBN (10 or 13 chars) or None when it cannot be one."""
    if value is None:
        return None
    cleaned = _clean(value)
    return cleaned if len(cleaned) in (10, 13) else None


def is_valid_isbn10(value: str) -> bool:
    cleaned = _clean(value)
    if len(cleaned) != 10:
        return False
    if "X" in cleaned[:-1]:
        return False
    total = sum(
        (10 - index) * (10 if char == "X" else int(char))
        for index, char in enumerate(cleaned)
    )
    return total % 11 == 0


def is_valid_isbn13(value: str) -> bool:
    cleaned = _clean(value)
    if len(cleaned) != 13:
        return False
    if any(char not in "0123456789" for char in cleaned):
        return False
    total = sum(
        int(char) * (1 if index % 2 == 0 else 3)
        for index, char in enumerate(cleaned)
    )
    return total % 10 == 0


def isbn10_to_isbn13(value: str) -> str:
    cleaned = _clean(value)
    core = "978" + cleaned[:9]
    total = sum(
        int(char) * (1 if index % 2 == 0 else 3)
        for index, char in enumerate(core)
    )
    check = (10 - total % 10) % 10
    return core + str(check)


def isbn13_to_isbn10(value: str) -> str | None:
    cleaned = _clean(value)
    if not cleaned.startswith("978"):
        return None
    core = cleaned[3:12]
    total = sum((10 - index) * int(char) for index, char in enumerate(core))
    check = (11 - total % 11) % 11
    return core + ("X" if check == 10 else str(check))


def canonicalize_isbns(
    isbn10: str | None, isbn13: str | None
) -> tuple[str | None, str | None]:
    """Normalise an ISBN pair, deriving the missing form. Raises ValueError."""
    canon10 = None
    canon13 = None

    if isbn10:
        cleaned = _clean(isbn10)
        if len(cleaned) != 10 or not is_valid_isbn10(cleaned):
            raise ValueError("Invalid ISBN-10")
        canon10 = cleaned

    if isbn13:
        cleaned = _clean(isbn13)
        if len(cleaned) != 13 or not is_valid_isbn13(cleaned):
            raise ValueError("Invalid ISBN-13")
        canon13 = cleaned

    if canon10 and canon13 and isbn10_to_isbn13(canon10) != canon13:
        raise ValueError("ISBN-10 and ISBN-13 do not match")

    if canon10 and not canon13:
        canon13 = isbn10_to_isbn13(canon10)
    elif canon13 and not canon10:
        canon10 = isbn13_to_isbn10(canon13)

    return canon10, canon13


def isbn_search_terms(query: str) -> tuple[str | None, str | None]:
    """For a valid ISBN query, return both forms to match; otherwise (None, None)."""
    cleaned = _clean(query)
    if len(cleaned) == 13 and is_valid_isbn13(cleaned):
        return isbn13_to_isbn10(cleaned), cleaned
    if len(cleaned) == 10 and is_valid_isbn10(cleaned):
        return cleaned, isbn10_to_isbn13(cleaned)
    return None, None
