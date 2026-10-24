"""add author publisher genre relationships

Revision ID: 0002_relationships
Revises: 0001_create_books
Create Date: 2026-10-23
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_relationships"
down_revision = "0001_create_books"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("bio", sa.Text()),
    )
    op.create_table(
        "publishers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=100)),
    )
    op.create_table(
        "genres",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )
    op.add_column("books", sa.Column("publisher_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_books_publisher_id", "books", "publishers", ["publisher_id"], ["id"])
    op.create_table(
        "book_authors",
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id"), primary_key=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("authors.id"), primary_key=True),
    )
    op.create_table(
        "book_genres",
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id"), primary_key=True),
        sa.Column("genre_id", sa.Integer(), sa.ForeignKey("genres.id"), primary_key=True),
    )


def downgrade():
    op.drop_table("book_genres")
    op.drop_table("book_authors")
    op.drop_constraint("fk_books_publisher_id", "books", type_="foreignkey")
    op.drop_column("books", "publisher_id")
    op.drop_table("genres")
    op.drop_table("publishers")
    op.drop_table("authors")
