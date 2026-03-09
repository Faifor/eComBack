"""add product images and reviews

Revision ID: 20260309_000006
Revises: 20260308_000005
Create Date: 2026-03-09 00:00:06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260309_000006"
down_revision = "20260308_000005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("commerce_product_images"):
        op.create_table(
            "commerce_product_images",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("image_url", sa.String(length=1024), nullable=False),
            sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["product_id"], ["commerce_products.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("commerce_product_reviews"):
        op.create_table(
            "commerce_product_reviews",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("rating", sa.Integer(), nullable=False),
            sa.Column("review", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["product_id"], ["commerce_products.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    for table_name in ["commerce_product_reviews", "commerce_product_images"]:
        if inspector.has_table(table_name):
            op.drop_table(table_name)
