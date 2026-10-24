from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DuplicateTagError
from app.models.associations import book_tags
from app.models.tag import Tag


class TaxonomyRepository:
    """List and case-insensitive create-or-get for named catalog entities."""

    def __init__(self, db: Session):
        self.db = db

    def list(self, model, q: str, limit: int):
        statement = select(model)
        cleaned = q.strip()
        if cleaned:
            statement = statement.where(
                func.lower(model.name).contains(cleaned.lower(), autoescape=True)
            )
        return (
            self.db.execute(statement.order_by(func.lower(model.name)).limit(limit))
            .scalars()
            .all()
        )

    def get_or_create(self, model, name: str, **extra):
        """Return the entity with this name, creating it if needed.

        Commits immediately because the endpoints expose create-or-get as a
        standalone operation; callers do not wrap it in a larger transaction.
        """
        entity = (
            self.db.query(model).filter(func.lower(model.name) == name.lower()).first()
        )
        if entity is not None:
            return entity

        entity = model(name=name, **extra)
        self.db.add(entity)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return (
                self.db.query(model)
                .filter(func.lower(model.name) == name.lower())
                .one()
            )
        self.db.refresh(entity)
        return entity

    # Tags ------------------------------------------------------------------

    def list_tags_with_counts(self, q: str, limit: int) -> list[dict]:
        statement = (
            select(
                Tag.id,
                Tag.name,
                func.count(book_tags.c.book_id).label("book_count"),
            )
            .outerjoin(book_tags, book_tags.c.tag_id == Tag.id)
            .group_by(Tag.id, Tag.name)
        )
        cleaned = q.strip()
        if cleaned:
            statement = statement.where(
                func.lower(Tag.name).contains(cleaned.lower(), autoescape=True)
            )
        statement = statement.order_by(func.lower(Tag.name)).limit(limit)
        return [
            {"id": row.id, "name": row.name, "book_count": row.book_count}
            for row in self.db.execute(statement).all()
        ]

    def tag_book_count(self, tag_id: int) -> int:
        return self.db.execute(
            select(func.count(book_tags.c.book_id)).where(
                book_tags.c.tag_id == tag_id
            )
        ).scalar_one()

    def rename_tag(self, tag_id: int, name: str) -> Tag | None:
        tag = self.db.get(Tag, tag_id)
        if tag is None:
            return None
        duplicate = (
            self.db.query(Tag)
            .filter(func.lower(Tag.name) == name.lower(), Tag.id != tag_id)
            .first()
        )
        if duplicate is not None:
            raise DuplicateTagError()

        tag.name = name
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateTagError() from exc
        self.db.refresh(tag)
        return tag

    def delete_tag(self, tag_id: int) -> bool:
        tag = self.db.get(Tag, tag_id)
        if tag is None:
            return False
        self.db.execute(delete(book_tags).where(book_tags.c.tag_id == tag_id))
        self.db.delete(tag)
        self.db.commit()
        return True
