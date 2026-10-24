from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ReadingStatus = Literal["want_to_read", "reading", "finished", "abandoned"]


class _MemberName(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name", mode="before")
    @classmethod
    def _strip_name(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("name cannot be blank")
        return value


class MemberCreate(_MemberName):
    pass


class MemberUpdate(_MemberName):
    pass


class MemberRead(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReadingEntryUpsert(BaseModel):
    status: ReadingStatus
    current_page: int | None = Field(default=None, ge=0, le=100_000)
    started_on: date | None = None
    finished_on: date | None = None
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("note", mode="before")
    @classmethod
    def _strip_note(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ReadingEntryRead(BaseModel):
    id: int
    book_id: int
    member_id: int
    member_name: str
    book_title: str
    book_pages: int | None
    status: ReadingStatus
    current_page: int | None
    started_on: date | None
    finished_on: date | None
    note: str | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
