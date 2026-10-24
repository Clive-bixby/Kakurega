from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


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
