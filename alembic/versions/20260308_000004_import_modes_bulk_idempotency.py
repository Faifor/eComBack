"""add import ledger and sku status

Revision ID: 20260308_000004
Revises: 20260305_000003
Create Date: 2026-03-08 00:00:04
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260308_000004"
down_revision = "20260305_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("commerce_variants", sa.Column("status", sa.String(length=32), nullable=False, server_default="active"))
    op.create_table(
        "commerce_import_ledger",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_key", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("sku", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_key", "version", "content_hash", name="uq_import_ledger_key_version_hash"),
    )


def downgrade() -> None:
    op.drop_table("commerce_import_ledger")
    op.drop_column("commerce_variants", "status")