from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.author import Author
from app.models.genre import Genre
from app.models.publisher import Publisher
from app.models.tag import Tag


class CatalogRepository:
    """Case-insensitive create-or-get for named catalog entities."""

    def __init__(self, db: Session):
        self.db = db
        self._cache: dict[tuple[type, str], object] = {}

    def _get_or_create(self, model, name: str):
        key = (model, name.casefold())
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        entity = (
            self.db.query(model)
            .filter(func.lower(model.name) == name.lower())
            .first()
        )
        if entity is None:
            entity = model(name=name)
            self.db.add(entity)
            self.db.flush()

        self._cache[key] = entity
        return entity

    def author(self, name: str) -> Author:
        return self._get_or_create(Author, name.strip())

    def publisher(self, name: str) -> Publisher:
        return self._get_or_create(Publisher, name.strip())

    def genre(self, name: str) -> Genre:
        return self._get_or_create(Genre, name.strip())

    def tag(self, name: str) -> Tag:
        return self._get_or_create(Tag, name.strip())
