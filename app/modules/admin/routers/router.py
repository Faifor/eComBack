from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from xml.etree import ElementTree

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.modules.admin.schemas.dto import (
    AdminUserCreate,
    AdminUserRead,
    AdminUserUpdate,
    AverageCheckReport,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ConversionReport,
    ImportReport,
    ImportRowError,
    InventoryCreate,
    InventoryRead,
    InventoryUpdate,
    OrderCreate,
    OrderRead,
    OrderUpdate,
    PricingRuleCreate,
    PricingRuleRead,
    PricingRuleUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    RetentionLtvReport,
    RevenueReport,
    SKUCreate,
    SKURead,
    SKUUpdate,
    TopProduct,
)
from app.modules.auth.dependencies import require_role
from app.modules.auth.models.entity import UserRole

router = APIRouter(prefix='/admin', tags=['admin'], dependencies=[Depends(require_role(UserRole.ADMIN))])

@dataclass
class _AdminStore:
    categories: dict[int, CategoryRead] = field(default_factory=dict)
    products: dict[int, ProductRead] = field(default_factory=dict)
    skus: dict[int, SKURead] = field(default_factory=dict)
    inventories: dict[int, InventoryRead] = field(default_factory=dict)
    pricing_rules: dict[int, PricingRuleRead] = field(default_factory=dict)
    orders: dict[int, OrderRead] = field(default_factory=dict)
    users: dict[int, AdminUserRead] = field(default_factory=dict)
    next_ids: dict[str, int] = field(
        default_factory=lambda: {
            'categories': 1,
            'products': 1,
            'skus': 1,
            'inventories': 1,
            'pricing_rules': 1,
            'orders': 1,
            'users': 1,
        }
    )

    def alloc(self, key: str) -> int:
        next_id = self.next_ids[key]
        self.next_ids[key] += 1
        return next_id


_store = _AdminStore()


# Categories CRUD
@router.get('/categories', response_model=list[CategoryRead])
def list_categories() -> list[CategoryRead]:
    return list(_store.categories.values())


@router.post('/categories', response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate) -> CategoryRead:
    item = CategoryRead(id=_store.alloc('categories'), name=payload.name, external_key=payload.external_key)
    _store.categories[item.id] = item
    return item


@router.get('/categories/{item_id}', response_model=CategoryRead)
def get_category(item_id: int) -> CategoryRead:
    item = _store.categories.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='category not found')
    return item


@router.put('/categories/{item_id}', response_model=CategoryRead)
def update_category(item_id: int, payload: CategoryUpdate) -> CategoryRead:
    item = _store.categories.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='category not found')
    updated = item.model_copy(
        update={
            'name': payload.name if payload.name is not None else item.name,
            'external_key': payload.external_key if payload.external_key is not None else item.external_key,
        }
    )
    _store.categories[item_id] = updated
    return updated


@router.delete('/categories/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(item_id: int) -> None:
    if _store.categories.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail='category not found')


# Products CRUD
@router.get('/products', response_model=list[ProductRead])
def list_products() -> list[ProductRead]:
    return list(_store.products.values())


@router.post('/products', response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate) -> ProductRead:
    if payload.category_id not in _store.categories:
        raise HTTPException(status_code=400, detail='category_id does not exist')
    item = ProductRead(
        id=_store.alloc('products'),
        name=payload.name,
        category_id=payload.category_id,
        external_key=payload.external_key,
    )
    _store.products[item.id] = item
    return item


@router.get('/products/{item_id}', response_model=ProductRead)
def get_product(item_id: int) -> ProductRead:
    item = _store.products.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='product not found')
    return item


@router.put('/products/{item_id}', response_model=ProductRead)
def update_product(item_id: int, payload: ProductUpdate) -> ProductRead:
    item = _store.products.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='product not found')

    category_id = payload.category_id if payload.category_id is not None else item.category_id
    if category_id not in _store.categories:
        raise HTTPException(status_code=400, detail='category_id does not exist')

    updated = item.model_copy(
        update={
            'name': payload.name if payload.name is not None else item.name,
            'category_id': category_id,
            'external_key': payload.external_key if payload.external_key is not None else item.external_key,
        }
    )
    _store.products[item_id] = updated
    return updated


@router.delete('/products/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(item_id: int) -> None:
    if _store.products.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail='product not found')


# SKU CRUD
@router.get('/skus', response_model=list[SKURead])
def list_skus() -> list[SKURead]:
    return list(_store.skus.values())


@router.post('/skus', response_model=SKURead, status_code=status.HTTP_201_CREATED)
def create_sku(payload: SKUCreate) -> SKURead:
    if payload.product_id not in _store.products:
        raise HTTPException(status_code=400, detail='product_id does not exist')
    item = SKURead(id=_store.alloc('skus'), product_id=payload.product_id, sku=payload.sku, attributes=payload.attributes)
    _store.skus[item.id] = item
    return item


@router.get('/skus/{item_id}', response_model=SKURead)
def get_sku(item_id: int) -> SKURead:
    item = _store.skus.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='sku not found')
    return item


@router.put('/skus/{item_id}', response_model=SKURead)
def update_sku(item_id: int, payload: SKUUpdate) -> SKURead:
    item = _store.skus.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='sku not found')

    product_id = payload.product_id if payload.product_id is not None else item.product_id
    if product_id not in _store.products:
        raise HTTPException(status_code=400, detail='product_id does not exist')

    updated = item.model_copy(
        update={
            'product_id': product_id,
            'sku': payload.sku if payload.sku is not None else item.sku,
            'attributes': payload.attributes if payload.attributes is not None else item.attributes,
        }
    )
    _store.skus[item_id] = updated
    return updated


@router.delete('/skus/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_sku(item_id: int) -> None:
    if _store.skus.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail='sku not found')


# Inventory CRUD
@router.get('/inventory', response_model=list[InventoryRead])
def list_inventory() -> list[InventoryRead]:
    return list(_store.inventories.values())


@router.post('/inventory', response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory(payload: InventoryCreate) -> InventoryRead:
    if payload.sku_id not in _store.skus:
        raise HTTPException(status_code=400, detail='sku_id does not exist')
    item = InventoryRead(id=_store.alloc('inventories'), sku_id=payload.sku_id, stock=payload.stock)
    _store.inventories[item.id] = item
    return item


@router.get('/inventory/{item_id}', response_model=InventoryRead)
def get_inventory(item_id: int) -> InventoryRead:
    item = _store.inventories.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='inventory not found')
    return item


@router.put('/inventory/{item_id}', response_model=InventoryRead)
def update_inventory(item_id: int, payload: InventoryUpdate) -> InventoryRead:
    item = _store.inventories.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='inventory not found')

    sku_id = payload.sku_id if payload.sku_id is not None else item.sku_id
    if sku_id not in _store.skus:
        raise HTTPException(status_code=400, detail='sku_id does not exist')

    updated = item.model_copy(update={'sku_id': sku_id, 'stock': payload.stock if payload.stock is not None else item.stock})
    _store.inventories[item_id] = updated
    return updated


@router.delete('/inventory/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory(item_id: int) -> None:
    if _store.inventories.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail='inventory not found')


# Pricing rules CRUD
@router.get('/pricing-rules', response_model=list[PricingRuleRead])
def list_pricing_rules() -> list[PricingRuleRead]:
    return list(_store.pricing_rules.values())


@router.post('/pricing-rules', response_model=PricingRuleRead, status_code=status.HTTP_201_CREATED)
def create_pricing_rule(payload: PricingRuleCreate) -> PricingRuleRead:
    item = PricingRuleRead(
        id=_store.alloc('pricing_rules'),
        name=payload.name,
        discount_percent=payload.discount_percent,
        is_active=payload.is_active,
    )
    _store.pricing_rules[item.id] = item
    return item


@router.get('/pricing-rules/{item_id}', response_model=PricingRuleRead)
def get_pricing_rule(item_id: int) -> PricingRuleRead:
    item = _store.pricing_rules.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='pricing rule not found')
    return item


@router.put('/pricing-rules/{item_id}', response_model=PricingRuleRead)
def update_pricing_rule(item_id: int, payload: PricingRuleUpdate) -> PricingRuleRead:
    item = _store.pricing_rules.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='pricing rule not found')
    updated = item.model_copy(
        update={
            'name': payload.name if payload.name is not None else item.name,
            'discount_percent': payload.discount_percent if payload.discount_percent is not None else item.discount_percent,
            'is_active': payload.is_active if payload.is_active is not None else item.is_active,
        }
    )
    _store.pricing_rules[item_id] = updated
    return updated


@router.delete('/pricing-rules/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_pricing_rule(item_id: int) -> None:
    if _store.pricing_rules.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail='pricing rule not found')


# Orders CRUD
@router.get('/orders', response_model=list[OrderRead])
def list_orders() -> list[OrderRead]:
    return list(_store.orders.values())


@router.post('/orders', response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate) -> OrderRead:
    if payload.sku_id not in _store.skus:
        raise HTTPException(status_code=400, detail='sku_id does not exist')
    item = OrderRead(
        id=_store.alloc('orders'),
        user_id=payload.user_id,
        sku_id=payload.sku_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        status=payload.status,
        created_at=datetime.now(UTC),
    )
    _store.orders[item.id] = item
    return item


@router.get('/orders/{item_id}', response_model=OrderRead)
def get_order(item_id: int) -> OrderRead:
    item = _store.orders.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='order not found')
    return item


@router.put('/orders/{item_id}', response_model=OrderRead)
def update_order(item_id: int, payload: OrderUpdate) -> OrderRead:
    item = _store.orders.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='order not found')

    sku_id = payload.sku_id if payload.sku_id is not None else item.sku_id
    if sku_id not in _store.skus:
        raise HTTPException(status_code=400, detail='sku_id does not exist')

    updated = item.model_copy(
        update={
            'user_id': payload.user_id if payload.user_id is not None else item.user_id,
            'sku_id': sku_id,
            'quantity': payload.quantity if payload.quantity is not None else item.quantity,
            'unit_price': payload.unit_price if payload.unit_price is not None else item.unit_price,
            'status': payload.status if payload.status is not None else item.status,
        }
    )
    _store.orders[item_id] = updated
    return updated


@router.delete('/orders/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_order(item_id: int) -> None:
    if _store.orders.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail='order not found')


# Users CRUD
@router.get('/users', response_model=list[AdminUserRead])
def list_users() -> list[AdminUserRead]:
    return list(_store.users.values())


@router.post('/users', response_model=AdminUserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: AdminUserCreate) -> AdminUserRead:
    item = AdminUserRead(id=_store.alloc('users'), email=payload.email, role=payload.role)
    _store.users[item.id] = item
    return item


@router.get('/users/{item_id}', response_model=AdminUserRead)
def get_user(item_id: int) -> AdminUserRead:
    item = _store.users.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='user not found')
    return item


@router.put('/users/{item_id}', response_model=AdminUserRead)
def update_user(item_id: int, payload: AdminUserUpdate) -> AdminUserRead:
    item = _store.users.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail='user not found')

    updated = item.model_copy(
        update={
            'email': payload.email if payload.email is not None else item.email,
            'role': payload.role if payload.role is not None else item.role,
        }
    )
    _store.users[item_id] = updated
    return updated


@router.delete('/users/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(item_id: int) -> None:
    if _store.users.pop(item_id, None) is None:
        raise HTTPException(status_code=404, detail='user not found')


def _read_xlsx(content: bytes) -> list[dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        shared_strings: list[str] = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            root = ElementTree.fromstring(archive.read('xl/sharedStrings.xml'))
            for text_node in root.findall('.//{*}t'):
                shared_strings.append(text_node.text or '')

        sheet_root = ElementTree.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        rows: list[list[str]] = []
        for row in sheet_root.findall('.//{*}row'):
            values: list[str] = []
            for cell in row.findall('{*}c'):
                cell_type = cell.attrib.get('t')
                value_node = cell.find('{*}v')
                raw_value = '' if value_node is None or value_node.text is None else value_node.text
                if cell_type == 's' and raw_value:
                    values.append(shared_strings[int(raw_value)])
                else:
                    values.append(raw_value)
            rows.append(values)

    if not rows:
        return []
    headers = rows[0]
    parsed: list[dict[str, str]] = []
    for row in rows[1:]:
        parsed.append({header: row[idx] if idx < len(row) else '' for idx, header in enumerate(headers)})
    return parsed


def _load_import_rows(filename: str, content: bytes) -> list[dict[str, str]]:
    if filename.endswith('.csv'):
        text = content.decode('utf-8-sig')
        return [dict(item) for item in csv.DictReader(io.StringIO(text))]
    if filename.endswith('.xlsx'):
        return _read_xlsx(content)
    raise HTTPException(status_code=400, detail='Only CSV/XLSX files are supported')


@router.post('/imports/products', response_model=ImportReport)
async def import_products(file: UploadFile = File(...), dry_run: bool = True) -> ImportReport:
    if not file.filename:
        raise HTTPException(status_code=400, detail='Filename is required')

    content = await file.read()
    rows = _load_import_rows(file.filename.lower(), content)
    required_columns = {'sku', 'external_key', 'product_name', 'category_name', 'price', 'stock'}
    if not rows:
        raise HTTPException(status_code=400, detail='Import file is empty')
    missing_columns = required_columns - set(rows[0].keys())
    if missing_columns:
        raise HTTPException(status_code=400, detail=f'Missing required columns: {sorted(missing_columns)}')

    report = ImportReport(created=0, updated=0, errors=[])

    for idx, row in enumerate(rows, start=2):
        try:
            sku_code = row['sku'].strip()
            external_key = row['external_key'].strip()
            product_name = row['product_name'].strip()
            category_name = row['category_name'].strip()
            price = float(row['price'])
            stock = int(float(row['stock']))
            attributes = json.loads(row['attributes']) if row.get('attributes') else {}
            if not sku_code or not external_key or not product_name or not category_name:
                raise ValueError('sku, external_key, product_name, category_name must be non-empty')
            if price <= 0:
                raise ValueError('price must be > 0')
            if stock < 0:
                raise ValueError('stock must be >= 0')
            if not isinstance(attributes, dict):
                raise ValueError('attributes must be a JSON object')

            if dry_run:
                product = next((item for item in _store.products.values() if item.external_key == external_key), None)
                sku = next((item for item in _store.skus.values() if item.sku == sku_code), None)
                if product or sku:
                    report.updated += 1
                else:
                    report.created += 1
                continue

            category = next((item for item in _store.categories.values() if item.name == category_name), None)
            if category is None:
                category = CategoryRead(id=_store.alloc('categories'), name=category_name, external_key=None)
                _store.categories[category.id] = category

            product = next((item for item in _store.products.values() if item.external_key == external_key), None)
            if product is None:
                product = ProductRead(
                    id=_store.alloc('products'),
                    name=product_name,
                    category_id=category.id,
                    external_key=external_key,
                )
                _store.products[product.id] = product
                report.created += 1
            else:
                _store.products[product.id] = product.model_copy(update={'name': product_name, 'category_id': category.id})
                report.updated += 1

            sku = next((item for item in _store.skus.values() if item.sku == sku_code), None)
            if sku is None:
                sku = SKURead(id=_store.alloc('skus'), product_id=product.id, sku=sku_code, attributes=attributes)
                _store.skus[sku.id] = sku
            else:
                _store.skus[sku.id] = sku.model_copy(update={'product_id': product.id, 'attributes': attributes})

            inventory = next((item for item in _store.inventories.values() if item.sku_id == sku.id), None)
            if inventory is None:
                inventory = InventoryRead(id=_store.alloc('inventories'), sku_id=sku.id, stock=stock)
                _store.inventories[inventory.id] = inventory
            else:
                _store.inventories[inventory.id] = inventory.model_copy(update={'stock': stock})

            price_rule_name = f'imported-price-{sku_code}'
            existing_rule = next((item for item in _store.pricing_rules.values() if item.name == price_rule_name), None)
            discount_percent = max(min(100 - (price / max(price, 1) * 100), 100), 0)
            if existing_rule is None:
                _store.pricing_rules[_store.alloc('pricing_rules')] = PricingRuleRead(
                    id=_store.next_ids['pricing_rules'] - 1,
                    name=price_rule_name,
                    discount_percent=discount_percent,
                    is_active=True,
                )
            else:
                _store.pricing_rules[existing_rule.id] = existing_rule.model_copy(update={'discount_percent': discount_percent})

        except Exception as exc:  # noqa: BLE001
            report.errors.append(ImportRowError(row=idx, message=str(exc)))

    return report


# Reports
@router.get('/reports/revenue', response_model=RevenueReport)
def revenue_report() -> RevenueReport:
    paid_orders = [order for order in _store.orders.values() if order.status in {'paid', 'completed'}]
    revenue = sum(order.quantity * order.unit_price for order in paid_orders)
    return RevenueReport(total_revenue=revenue, paid_orders=len(paid_orders))


@router.get('/reports/top-products', response_model=list[TopProduct])
def top_products_report(limit: int = 5) -> list[TopProduct]:
    by_product: dict[int, int] = defaultdict(int)
    for order in _store.orders.values():
        sku = _store.skus.get(order.sku_id)
        if sku is None:
            continue
        by_product[sku.product_id] += order.quantity

    ranked = sorted(by_product.items(), key=lambda item: item[1], reverse=True)[:limit]
    result: list[TopProduct] = []
    for product_id, units_sold in ranked:
        product = _store.products.get(product_id)
        if product is None:
            continue
        result.append(TopProduct(product_id=product_id, product_name=product.name, units_sold=units_sold))
    return result


@router.get('/reports/conversion', response_model=ConversionReport)
def conversion_report() -> ConversionReport:
    total_orders = len(_store.orders)
    total_users = len(_store.users)
    conversion_rate = (total_orders / total_users) if total_users else 0
    return ConversionReport(total_orders=total_orders, total_users=total_users, conversion_rate=conversion_rate)


@router.get('/reports/average-check', response_model=AverageCheckReport)
def average_check_report() -> AverageCheckReport:
    total_orders = len(_store.orders)
    if total_orders == 0:
        return AverageCheckReport(average_check=0)
    total_revenue = sum(order.quantity * order.unit_price for order in _store.orders.values())
    return AverageCheckReport(average_check=total_revenue / total_orders)


@router.get('/reports/retention-ltv', response_model=RetentionLtvReport)
def retention_ltv_report() -> RetentionLtvReport:
    order_count_by_user: dict[int, int] = defaultdict(int)
    spend_by_user: dict[int, float] = defaultdict(float)
    for order in _store.orders.values():
        order_count_by_user[order.user_id] += 1
        spend_by_user[order.user_id] += order.quantity * order.unit_price

    total_users = len(order_count_by_user)
    returning_users = sum(1 for count in order_count_by_user.values() if count > 1)
    retention_rate = (returning_users / total_users) if total_users else 0
    average_ltv = (sum(spend_by_user.values()) / total_users) if total_users else 0
    return RetentionLtvReport(returning_users=returning_users, retention_rate=retention_rate, average_ltv=average_ltv)