import uuid
from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.storage import IMAGES_DIR
from app.core.uploads import FileTooLargeError, read_limited
from app.schemas.upload import UploadImageResponse

router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024
EXTENSION_BY_FORMAT = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


@router.post("/image", response_model=UploadImageResponse)
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    try:
        contents = await read_limited(file, MAX_FILE_SIZE)
    except FileTooLargeError as exc:
        raise HTTPException(status_code=413, detail="File too large") from exc

    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        with Image.open(BytesIO(contents)) as image:
            image_format = image.format
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Invalid image file")

    extension = EXTENSION_BY_FORMAT.get(image_format or "")
    if extension is None:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    image_id = str(uuid.uuid4())
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    destination = IMAGES_DIR / f"{image_id}{extension}"
    destination.write_bytes(contents)

    return UploadImageResponse(image_id=image_id, path=f"/storage/images/{destination.name}")
