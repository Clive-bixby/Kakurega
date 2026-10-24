from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import DuplicateTagError
from app.models.author import Author
from app.models.genre import Genre
from app.models.publisher import Publisher
from app.models.tag import Tag
from app.repositories.taxonomy import TaxonomyRepository
from app.schemas.taxonomy import (
    AuthorCreate,
    GenreCreate,
    NamedEntityRead,
    PublisherCreate,
    PublisherRead,
    TagCreate,
    TagRead,
)

router = APIRouter()


def _repo(db: Session) -> TaxonomyRepository:
    return TaxonomyRepository(db)


@router.get("/authors", response_model=list[NamedEntityRead])
def list_authors(
    q: str = "",
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return _repo(db).list(Author, q, limit)


@router.post("/authors", response_model=NamedEntityRead)
def create_author(data: AuthorCreate, db: Session = Depends(get_db)):
    return _repo(db).get_or_create(Author, data.name)


@router.get("/publishers", response_model=list[PublisherRead])
def list_publishers(
    q: str = "",
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return _repo(db).list(Publisher, q, limit)


@router.post("/publishers", response_model=PublisherRead)
def create_publisher(data: PublisherCreate, db: Session = Depends(get_db)):
    return _repo(db).get_or_create(Publisher, data.name, country=data.country)


@router.get("/genres", response_model=list[NamedEntityRead])
def list_genres(
    q: str = "",
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return _repo(db).list(Genre, q, limit)


@router.post("/genres", response_model=NamedEntityRead)
def create_genre(data: GenreCreate, db: Session = Depends(get_db)):
    return _repo(db).get_or_create(Genre, data.name)


@router.get("/tags", response_model=list[TagRead])
def list_tags(
    q: str = "",
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return _repo(db).list_tags_with_counts(q, limit)


@router.post("/tags", response_model=TagRead)
def create_tag(data: TagCreate, db: Session = Depends(get_db)):
    repo = _repo(db)
    tag = repo.get_or_create(Tag, data.name)
    return {
        "id": tag.id,
        "name": tag.name,
        "book_count": repo.tag_book_count(tag.id),
    }


@router.patch("/tags/{tag_id}", response_model=TagRead)
def rename_tag(tag_id: int, data: TagCreate, db: Session = Depends(get_db)):
    repo = _repo(db)
    try:
        tag = repo.rename_tag(tag_id, data.name)
    except DuplicateTagError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {
        "id": tag.id,
        "name": tag.name,
        "book_count": repo.tag_book_count(tag.id),
    }


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    if not _repo(db).delete_tag(tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    return None
