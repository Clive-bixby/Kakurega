"""create books table

Revision ID: 0001_create_books
Revises:
Create Date: 2026-10-23
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_create_books"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("subtitle", sa.String(length=500)),
        sa.Column("isbn10", sa.String(length=10)),
        sa.Column("isbn13", sa.String(length=13)),
        sa.Column("description", sa.Text()),
        sa.Column("pages", sa.Integer()),
        sa.Column("language", sa.String(length=20)),
        sa.Column("published_year", sa.Integer()),
        sa.Column("cover_url", sa.String(length=1000)),
        sa.Column("google_books_id", sa.String(length=100)),
        sa.Column("openlibrary_id", sa.String(length=100)),
    )


def downgrade():
    op.drop_table("books")
