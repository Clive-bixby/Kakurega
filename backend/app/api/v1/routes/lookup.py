from fastapi import APIRouter, HTTPException

from app.schemas.lookup import LookupRequest, MetadataResponse
from app.services.metadata import MetadataLookupError, lookup_metadata

router = APIRouter()


@router.post("", response_model=MetadataResponse)
def lookup(data: LookupRequest):
    try:
        result = lookup_metadata(data.isbn, data.title, data.author)
    except MetadataLookupError as exc:
        raise HTTPException(status_code=502, detail="Metadata lookup failed") from exc
    if result is None:
        raise HTTPException(status_code=404, detail="No metadata found")
    return result
