from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.member import Member

READING_STATUSES = ("want_to_read", "reading", "finished", "abandoned")


class ReadingEntry(Base):
    __tablename__ = "reading_entries"
    __table_args__ = (
        UniqueConstraint(
            "book_id", "member_id", name="uq_reading_entries_book_member"
        ),
        CheckConstraint(
            "status IN ('want_to_read', 'reading', 'finished', 'abandoned')",
            name="ck_reading_entries_status",
        ),
        Index("ix_reading_entries_member_id", "member_id"),
        Index("ix_reading_entries_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    current_page: Mapped[int | None] = mapped_column(Integer)
    started_on: Mapped[date | None] = mapped_column(Date)
    finished_on: Mapped[date | None] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    book: Mapped[Book] = relationship(back_populates="reading_entries")
    member: Mapped[Member] = relationship(back_populates="reading_entries")

    @property
    def member_name(self) -> str | None:
        return self.member.name if self.member is not None else None

    @property
    def book_title(self) -> str | None:
        return self.book.title if self.book is not None else None

    @property
    def book_pages(self) -> int | None:
        return self.book.pages if self.book is not None else None
