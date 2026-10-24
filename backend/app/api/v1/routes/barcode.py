from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.barcode import BarcodeResponse
from app.services.barcode import decode_barcode

router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("", response_model=BarcodeResponse)
async def detect_barcode(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    try:
        isbn = decode_barcode(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if isbn is None:
        raise HTTPException(status_code=404, detail="No ISBN barcode found")
    return BarcodeResponse(isbn=isbn)
