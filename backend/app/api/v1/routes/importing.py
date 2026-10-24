from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.uploads import FileTooLargeError, read_limited
from app.schemas.importing import ImportResult
from app.services.importer import ImportService

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/csv", response_model=ImportResult)
async def import_csv(
    file: UploadFile = File(...),
    update_existing: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        contents = await read_limited(file, MAX_FILE_SIZE)
    except FileTooLargeError as exc:
        raise HTTPException(status_code=413, detail="File too large") from exc

    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        return ImportService(db).import_csv(contents, update_existing)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
