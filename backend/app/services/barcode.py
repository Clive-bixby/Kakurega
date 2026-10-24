import io
import re

from PIL import Image
import zxingcpp


def _normalize_isbn(value: str) -> str | None:
    cleaned = value.strip().replace("-", "").replace(" ", "")
    if re.fullmatch(r"\d{9}[\dX]", cleaned) or re.fullmatch(r"\d{13}", cleaned):
        return cleaned
    return None


def decode_barcode(image_bytes: bytes) -> str | None:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        results = zxingcpp.read_barcodes(image)
    except Exception as exc:
        raise ValueError("Invalid image") from exc

    for result in results:
        isbn = _normalize_isbn(getattr(result, "text", ""))
        if isbn:
            return isbn
    return None
