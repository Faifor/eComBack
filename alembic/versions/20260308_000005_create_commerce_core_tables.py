"""create commerce core tables

Revision ID: 20260308_000005
Revises: 20260308_000004
Create Date: 2026-03-08 00:00:05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "20260308_000005"
down_revision = "20260308_000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("commerce_categories"):
        op.create_table(
            "commerce_categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("parent_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["parent_id"], ["commerce_categories.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("commerce_products"):
        op.create_table(
            "commerce_products",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=False),
            sa.Column("base_price", sa.Numeric(10, 2), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.ForeignKeyConstraint(["category_id"], ["commerce_categories.id"], ondelete="RESTRICT"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("commerce_variants"):
        op.create_table(
            "commerce_variants",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("sku", sa.String(length=128), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("base_price", sa.Numeric(10, 2), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
            sa.ForeignKeyConstraint(["product_id"], ["commerce_products.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("sku"),
        )

    if not inspector.has_table("commerce_inventory"):
        op.create_table(
            "commerce_inventory",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("variant_id", sa.Integer(), nullable=False),
            sa.Column("qty", sa.Integer(), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(["variant_id"], ["commerce_variants.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("variant_id"),
        )

    if not inspector.has_table("inventory_movements"):
        op.create_table(
            "inventory_movements",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("sku_id", sa.Integer(), nullable=False),
            sa.Column("movement_type", sa.String(length=32), nullable=False),
            sa.Column("qty", sa.Integer(), nullable=False),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("source_type", sa.String(length=64), nullable=True),
            sa.Column("source_id", sa.String(length=128), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["sku_id"], ["commerce_variants.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("commerce_attributes"):
        op.create_table(
            "commerce_attributes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column("value", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["product_id"], ["commerce_products.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("commerce_pricing_rules"):
        op.create_table(
            "commerce_pricing_rules",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
            sa.Column("rule_type", sa.String(length=16), nullable=False),
            sa.Column("value", sa.Numeric(10, 2), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=True),
            sa.Column("variant_id", sa.Integer(), nullable=True),
            sa.Column("min_qty", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("coupon_code", sa.String(length=100), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.ForeignKeyConstraint(["product_id"], ["commerce_products.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["variant_id"], ["commerce_variants.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("commerce_orders"):
        op.create_table(
            "commerce_orders",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=64), nullable=False),
            sa.Column("payment_method", sa.String(length=32), nullable=False),
            sa.Column("payment_id", sa.String(length=255), nullable=True),
            sa.Column("payment_status", sa.String(length=64), nullable=True),
            sa.Column("sales_channel", sa.String(length=64), nullable=True),
            sa.Column("promo_code", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("total_price", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("commerce_order_items"):
        op.create_table(
            "commerce_order_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("sku", sa.String(length=128), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("qty", sa.Integer(), nullable=False),
            sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
            sa.Column("line_total", sa.Numeric(10, 2), nullable=False),
            sa.Column("rule_trace", sa.JSON(), nullable=False),
            sa.ForeignKeyConstraint(["order_id"], ["commerce_orders.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("commerce_order_status_history"):
        op.create_table(
            "commerce_order_status_history",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("from_status", sa.String(length=64), nullable=True),
            sa.Column("to_status", sa.String(length=64), nullable=False),
            sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["order_id"], ["commerce_orders.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    for table_name in [
        "commerce_order_status_history",
        "commerce_order_items",
        "commerce_orders",
        "commerce_pricing_rules",
        "commerce_attributes",
        "inventory_movements",
        "commerce_inventory",
        "commerce_variants",
        "commerce_products",
        "commerce_categories",
    ]:
        if inspector.has_table(table_name):
            op.drop_table(table_name)