"""add product description column

Revision ID: 20260309_000007
Revises: 20260309_000006
Create Date: 2026-03-09 00:00:07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260309_000007"
down_revision = "20260309_000006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("commerce_products")}
    if "description" not in columns:
        op.add_column("commerce_products", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("commerce_products")}
    if "description" in columns:
        op.drop_column("commerce_products", "description")
