from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CommerceCategory(Base):
    __tablename__ = "commerce_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("commerce_categories.id", ondelete="SET NULL"), nullable=True)


class CommerceProduct(Base):
    __tablename__ = "commerce_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("commerce_categories.id", ondelete="RESTRICT"), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)


class CommerceVariant(Base):
    __tablename__ = "commerce_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("commerce_products.id", ondelete="CASCADE"), nullable=False)
    sku: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    base_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


class CommerceInventory(Base):
    __tablename__ = "commerce_inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("commerce_variants.id", ondelete="CASCADE"), unique=True, nullable=False)
    qty: Mapped[int] = mapped_column(default=0, nullable=False)

class CommerceInventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku_id: Mapped[int] = mapped_column(ForeignKey("commerce_variants.id", ondelete="CASCADE"), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    qty: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class CommerceAttribute(Base):
    __tablename__ = "commerce_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("commerce_products.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("commerce_variants.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[str] = mapped_column(Text(), nullable=False)


class CommercePricingRule(Base):
    __tablename__ = "commerce_pricing_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[int] = mapped_column(default=100, nullable=False)
    rule_type: Mapped[str] = mapped_column(String(16), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("commerce_products.id", ondelete="CASCADE"), nullable=True)
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("commerce_variants.id", ondelete="CASCADE"), nullable=True)
    min_qty: Mapped[int] = mapped_column(default=1, nullable=False)
    coupon_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)

class CommerceImportLedger(Base):
    __tablename__ = "commerce_import_ledger"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_key: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    sku: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class CommerceOrder(Base):
    __tablename__ = "commerce_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(32), nullable=False)
    payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sales_channel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    promo_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))


class CommerceOrderItem(Base):
    __tablename__ = "commerce_order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("commerce_orders.id", ondelete="CASCADE"), nullable=False)
    sku: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    qty: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    rule_trace: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)


class CommerceOrderStatusHistory(Base):
    __tablename__ = "commerce_order_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("commerce_orders.id", ondelete="CASCADE"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_status: Mapped[str] = mapped_column(String(64), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class CommerceProductImage(Base):
    __tablename__ = "commerce_product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("commerce_products.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class CommerceProductReview(Base):
    __tablename__ = "commerce_product_reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("commerce_products.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    review: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
