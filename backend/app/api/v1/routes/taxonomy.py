from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
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


@router.get("/tags", response_model=list[NamedEntityRead])
def list_tags(
    q: str = "",
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return _repo(db).list(Tag, q, limit)


@router.post("/tags", response_model=NamedEntityRead)
def create_tag(data: TagCreate, db: Session = Depends(get_db)):
    return _repo(db).get_or_create(Tag, data.name)
