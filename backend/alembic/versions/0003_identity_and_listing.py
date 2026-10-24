"""add identity constraints, timestamps, notes and tags

Revision ID: 0003_identity_and_listing
Revises: 0002_relationships
Create Date: 2026-10-24
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_identity_and_listing"
down_revision = "0002_relationships"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("books") as batch:
        batch.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            )
        )
        batch.add_column(sa.Column("notes", sa.Text()))

    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_published_year", "books", ["published_year"])
    op.create_index("ix_books_publisher_id", "books", ["publisher_id"])
    op.create_index(
        "uq_books_isbn10",
        "books",
        ["isbn10"],
        unique=True,
        postgresql_where=sa.text("isbn10 IS NOT NULL"),
        sqlite_where=sa.text("isbn10 IS NOT NULL"),
    )
    op.create_index(
        "uq_books_isbn13",
        "books",
        ["isbn13"],
        unique=True,
        postgresql_where=sa.text("isbn13 IS NOT NULL"),
        sqlite_where=sa.text("isbn13 IS NOT NULL"),
    )

    op.create_index(
        "uq_authors_name_lower", "authors", [sa.text("lower(name)")], unique=True
    )
    op.create_index(
        "uq_publishers_name_lower", "publishers", [sa.text("lower(name)")], unique=True
    )
    op.create_index(
        "uq_genres_name_lower", "genres", [sa.text("lower(name)")], unique=True
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )
    op.create_index("uq_tags_name_lower", "tags", [sa.text("lower(name)")], unique=True)
    op.create_table(
        "book_tags",
        sa.Column(
            "book_id",
            sa.Integer(),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "tag_id",
            sa.Integer(),
            sa.ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade():
    op.drop_table("book_tags")
    op.drop_index("uq_tags_name_lower", table_name="tags")
    op.drop_table("tags")

    op.drop_index("uq_genres_name_lower", table_name="genres")
    op.drop_index("uq_publishers_name_lower", table_name="publishers")
    op.drop_index("uq_authors_name_lower", table_name="authors")

    op.drop_index("uq_books_isbn13", table_name="books")
    op.drop_index("uq_books_isbn10", table_name="books")
    op.drop_index("ix_books_publisher_id", table_name="books")
    op.drop_index("ix_books_published_year", table_name="books")
    op.drop_index("ix_books_title", table_name="books")

    with op.batch_alter_table("books") as batch:
        batch.drop_column("notes")
        batch.drop_column("created_at")
