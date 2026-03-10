"""add variant_id to commerce_attributes

Revision ID: 20260310_000008
Revises: 20260309_000007
Create Date: 2026-03-10 00:00:08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "20260310_000008"
down_revision: Union[str, Sequence[str], None] = "20260309_000007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("commerce_attributes")}
    if "variant_id" not in columns:
        op.add_column("commerce_attributes", sa.Column("variant_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_commerce_attributes_variant_id",
            "commerce_attributes",
            "commerce_variants",
            ["variant_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("commerce_attributes")}
    if "variant_id" in columns:
        op.drop_constraint("fk_commerce_attributes_variant_id", "commerce_attributes", type_="foreignkey")
        op.drop_column("commerce_attributes", "variant_id")
