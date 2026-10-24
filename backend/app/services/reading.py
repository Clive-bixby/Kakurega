from datetime import date

from sqlalchemy.orm import Session

from app.core.errors import DuplicateMemberError, InvalidReadingError
from app.models.book import Book
from app.models.member import Member
from app.models.reading import ReadingEntry
from app.repositories.book import BookRepository
from app.repositories.reading import ReadingRepository
from app.schemas.reading import MemberCreate, MemberUpdate, ReadingEntryUpsert


class ReadingService:
    def __init__(self, db: Session):
        self.repo = ReadingRepository(db)
        self.books = BookRepository(db)

    # Members ---------------------------------------------------------------

    def list_members(self) -> list[Member]:
        return self.repo.list_members()

    def create_member(self, data: MemberCreate) -> Member:
        if self.repo.find_member_by_name(data.name) is not None:
            raise DuplicateMemberError()
        return self.repo.create_member(data.name)

    def update_member(self, member_id: int, data: MemberUpdate) -> Member | None:
        member = self.repo.get_member(member_id)
        if member is None:
            return None
        if self.repo.find_member_by_name(data.name, exclude_id=member.id) is not None:
            raise DuplicateMemberError()
        return self.repo.rename_member(member, data.name)

    def delete_member(self, member_id: int) -> bool:
        member = self.repo.get_member(member_id)
        if member is None:
            return False
        self.repo.delete_member(member)
        return True

    # Entries ---------------------------------------------------------------

    def list_book_entries(self, book_id: int) -> list[ReadingEntry] | None:
        if self.books.get(book_id) is None:
            return None
        return self.repo.entries_for_book(book_id)

    def list_entries(
        self, member_id: int | None = None, status: str | None = None
    ) -> list[ReadingEntry]:
        return self.repo.list_entries(member_id, status)

    def upsert_entry(
        self, book_id: int, member_id: int, data: ReadingEntryUpsert
    ) -> ReadingEntry | None:
        book = self.books.get(book_id)
        if book is None or self.repo.get_member(member_id) is None:
            return None

        values = data.model_dump(exclude_unset=True)
        status = values.pop("status")

        entry = self.repo.get_entry(book_id, member_id)
        if entry is None:
            entry = ReadingEntry(book_id=book_id, member_id=member_id)

        entry.status = status
        for field, value in values.items():
            setattr(entry, field, value)

        if status == "reading":
            if "finished_on" not in values:
                entry.finished_on = None
            if entry.started_on is None:
                entry.started_on = date.today()
        if status == "finished":
            if entry.finished_on is None:
                entry.finished_on = date.today()
            if "current_page" not in values and book.pages is not None:
                entry.current_page = book.pages

        self._validate(entry, book)
        return self.repo.save_entry(entry)

    def delete_entry(self, book_id: int, member_id: int) -> bool:
        entry = self.repo.get_entry(book_id, member_id)
        if entry is None:
            return False
        self.repo.delete_entry(entry)
        return True

    @staticmethod
    def _validate(entry: ReadingEntry, book: Book) -> None:
        if (
            entry.current_page is not None
            and book.pages is not None
            and entry.current_page > book.pages
        ):
            raise InvalidReadingError(
                f"current_page cannot exceed the book's {book.pages} pages"
            )
        if (
            entry.started_on is not None
            and entry.finished_on is not None
            and entry.finished_on < entry.started_on
        ):
            raise InvalidReadingError("finished_on cannot be before started_on")
