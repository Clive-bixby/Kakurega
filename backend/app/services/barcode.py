import io
import re

import zxingcpp
from PIL import Image

from app.core.isbn import is_valid_isbn10, is_valid_isbn13

_BARCODE_CHARS = re.compile(r"[^0-9Xx]")


def isbn_from_barcode_text(value: str) -> str | None:
    """Return a valid book ISBN from a decoded barcode, else None."""
    cleaned = _BARCODE_CHARS.sub("", value or "").upper()
    if len(cleaned) == 10 and is_valid_isbn10(cleaned):
        return cleaned
    if (
        len(cleaned) == 13
        and cleaned.startswith(("978", "979"))
        and is_valid_isbn13(cleaned)
    ):
        return cleaned
    return None


def decode_barcode(image_bytes: bytes) -> str | None:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        results = zxingcpp.read_barcodes(image)
    except Exception as exc:
        raise ValueError("Invalid image") from exc

    for result in results:
        isbn = isbn_from_barcode_text(getattr(result, "text", ""))
        if isbn:
            return isbn
    return None
