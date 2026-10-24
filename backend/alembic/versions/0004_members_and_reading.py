"""add household members and reading entries

Revision ID: 0004_members_and_reading
Revises: 0003_identity_and_listing
Create Date: 2026-10-24
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_members_and_reading"
down_revision = "0003_identity_and_listing"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "uq_members_name_lower", "members", [sa.text("lower(name)")], unique=True
    )

    op.create_table(
        "reading_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "book_id",
            sa.Integer(),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "member_id",
            sa.Integer(),
            sa.ForeignKey("members.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("current_page", sa.Integer()),
        sa.Column("started_on", sa.Date()),
        sa.Column("finished_on", sa.Date()),
        sa.Column("note", sa.Text()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "book_id", "member_id", name="uq_reading_entries_book_member"
        ),
        sa.CheckConstraint(
            "status IN ('want_to_read', 'reading', 'finished', 'abandoned')",
            name="ck_reading_entries_status",
        ),
    )
    op.create_index(
        "ix_reading_entries_member_id", "reading_entries", ["member_id"]
    )
    op.create_index("ix_reading_entries_status", "reading_entries", ["status"])


def downgrade():
    op.drop_index("ix_reading_entries_status", table_name="reading_entries")
    op.drop_index("ix_reading_entries_member_id", table_name="reading_entries")
    op.drop_table("reading_entries")
    op.drop_index("uq_members_name_lower", table_name="members")
    op.drop_table("members")
