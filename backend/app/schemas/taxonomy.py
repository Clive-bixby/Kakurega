from pydantic import BaseModel, ConfigDict, Field, field_validator


class _NamedCreate(BaseModel):
    name: str = Field(min_length=1)

    @field_validator("name", mode="before")
    @classmethod
    def _strip_name(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("name cannot be blank")
        return value


class AuthorCreate(_NamedCreate):
    name: str = Field(min_length=1, max_length=255)


class GenreCreate(_NamedCreate):
    name: str = Field(min_length=1, max_length=100)


class TagCreate(_NamedCreate):
    name: str = Field(min_length=1, max_length=100)


class PublisherCreate(_NamedCreate):
    name: str = Field(min_length=1, max_length=255)
    country: str | None = Field(default=None, max_length=100)

    @field_validator("country", mode="before")
    @classmethod
    def _strip_country(cls, value):
        return value.strip() if isinstance(value, str) else value


class NamedEntityRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TagRead(NamedEntityRead):
    book_count: int = 0


class PublisherRead(NamedEntityRead):
    country: str | None
