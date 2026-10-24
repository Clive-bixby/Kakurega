from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.errors import DuplicateMemberError
from app.models.member import Member
from app.models.reading import ReadingEntry


class ReadingRepository:
    def __init__(self, db: Session):
        self.db = db

    # Members ---------------------------------------------------------------

    def list_members(self) -> list[Member]:
        statement = select(Member).order_by(func.lower(Member.name), Member.id)
        return list(self.db.execute(statement).scalars().all())

    def get_member(self, member_id: int) -> Member | None:
        return self.db.get(Member, member_id)

    def find_member_by_name(
        self, name: str, exclude_id: int | None = None
    ) -> Member | None:
        statement = select(Member).where(func.lower(Member.name) == name.lower())
        if exclude_id is not None:
            statement = statement.where(Member.id != exclude_id)
        return self.db.execute(statement).scalars().first()

    def create_member(self, name: str) -> Member:
        member = Member(name=name)
        self.db.add(member)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateMemberError() from exc
        self.db.refresh(member)
        return member

    def rename_member(self, member: Member, name: str) -> Member:
        member.name = name
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateMemberError() from exc
        self.db.refresh(member)
        return member

    def delete_member(self, member: Member) -> None:
        self.db.delete(member)
        self.db.commit()

    # Entries ---------------------------------------------------------------

    def entries_for_book(self, book_id: int) -> list[ReadingEntry]:
        statement = (
            select(ReadingEntry)
            .where(ReadingEntry.book_id == book_id)
            .options(
                joinedload(ReadingEntry.member), joinedload(ReadingEntry.book)
            )
            .order_by(func.lower(Member.name), ReadingEntry.id)
            .join(ReadingEntry.member)
        )
        return list(self.db.execute(statement).scalars().unique().all())

    def get_entry(self, book_id: int, member_id: int) -> ReadingEntry | None:
        statement = (
            select(ReadingEntry)
            .where(
                ReadingEntry.book_id == book_id,
                ReadingEntry.member_id == member_id,
            )
            .options(
                joinedload(ReadingEntry.member), joinedload(ReadingEntry.book)
            )
        )
        return self.db.execute(statement).scalars().first()

    def list_entries(
        self, member_id: int | None = None, status: str | None = None
    ) -> list[ReadingEntry]:
        statement = select(ReadingEntry).options(
            joinedload(ReadingEntry.member), joinedload(ReadingEntry.book)
        )
        if member_id is not None:
            statement = statement.where(ReadingEntry.member_id == member_id)
        if status is not None:
            statement = statement.where(ReadingEntry.status == status)
        statement = statement.order_by(
            ReadingEntry.updated_at.desc(), ReadingEntry.id.desc()
        )
        return list(self.db.execute(statement).scalars().unique().all())

    def save_entry(self, entry: ReadingEntry) -> ReadingEntry:
        self.db.add(entry)
        self.db.commit()
        return self.get_entry(entry.book_id, entry.member_id)

    def delete_entry(self, entry: ReadingEntry) -> None:
        self.db.delete(entry)
        self.db.commit()
