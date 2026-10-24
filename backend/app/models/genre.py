from sqlalchemy import Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Genre(Base):
    __tablename__ = "genres"
    __table_args__ = (Index("uq_genres_name_lower", text("lower(name)"), unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
