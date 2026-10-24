from fastapi import APIRouter, HTTPException

from app.schemas.lookup import LookupRequest, MetadataResponse
from app.services.metadata import (
    InvalidIsbnError,
    MetadataLookupError,
    lookup_metadata,
)

router = APIRouter()


@router.post("", response_model=MetadataResponse)
def lookup(data: LookupRequest):
    try:
        result = lookup_metadata(data.isbn, data.title, data.author)
    except InvalidIsbnError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MetadataLookupError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc) or "Metadata lookup failed",
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No metadata found for this book. Enter the details manually.",
        )
    return result
