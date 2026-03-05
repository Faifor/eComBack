"""encrypt personal data and add profile audit logs

Revision ID: 20260305_000003
Revises: 20260305_000002
Create Date: 2026-03-05 00:00:03.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260305_000003"
down_revision: Union[str, None] = "20260305_000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_enc", sa.String(length=1024), nullable=True))
    op.add_column("users", sa.Column("email_hash", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("full_name_enc", sa.String(length=1024), nullable=True))
    op.add_column("users", sa.Column("phone_enc", sa.String(length=1024), nullable=True))

    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("UPDATE users SET email_enc = email, full_name_enc = full_name, email_hash = encode(digest(lower(email), 'sha256'), 'hex')")

    op.alter_column("users", "email_enc", nullable=False)
    op.alter_column("users", "email_hash", nullable=False)
    op.alter_column("users", "full_name_enc", nullable=False)

    op.create_index(op.f("ix_users_email_hash"), "users", ["email_hash"], unique=True)

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_column("users", "email")
    op.drop_column("users", "full_name")

    op.create_table(
        "profile_change_logs",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("diff", sa.JSON(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_profile_change_logs_id"), "profile_change_logs", ["id"], unique=False)
    op.create_index(op.f("ix_profile_change_logs_user_id"), "profile_change_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_profile_change_logs_user_id"), table_name="profile_change_logs")
    op.drop_index(op.f("ix_profile_change_logs_id"), table_name="profile_change_logs")
    op.drop_table("profile_change_logs")

    op.add_column("users", sa.Column("full_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.execute("UPDATE users SET email = email_enc, full_name = full_name_enc")
    op.alter_column("users", "email", nullable=False)
    op.alter_column("users", "full_name", nullable=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.drop_index(op.f("ix_users_email_hash"), table_name="users")
    op.drop_column("users", "phone_enc")
    op.drop_column("users", "full_name_enc")
    op.drop_column("users", "email_hash")
    op.drop_column("users", "email_enc")