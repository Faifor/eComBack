# API documentation (without AI module)

Base URL: `/api/v1`

## Swagger structure (without duplication)

Swagger intentionally shows endpoints by **consumer role**:

- **User API**: `auth`, `catalog-user`, `cart`, `orders-user`, `payments`
- **Admin API**: `admin`, `orders-admin`
- **Technical/integration API**: `pricing`

To avoid duplicate contracts in Swagger, admin-only write operations in `/catalog/*`
(`POST /catalog/categories`, `POST /catalog/products`, `POST /catalog/variants`,
`PUT /catalog/inventory`, `POST /catalog/attributes`) are kept for compatibility,
but hidden from OpenAPI schema. Canonical admin contract is `/admin/*`.

---

## 1) User/storefront API

### Auth (`auth`)

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`
- `PATCH /auth/profile`

### Catalog (`catalog-user`)

- `GET /catalog/categories`
- `GET /catalog/products`
- `POST /catalog/products/{product_id}/reviews`
- `GET /catalog/products/{product_id}/reviews`

### Cart (`cart`)

- `POST /cart/`
- `GET /cart/{cart_id}`
- `PUT /cart/{cart_id}/items/{variant_id}`

### Orders (`orders-user`)

- `POST /orders/checkout`
- `GET /orders/`
- `GET /orders/{order_id}`

### Payments (`payments`)

- `POST /payments/yookassa/webhook`

---

## 2) Admin API (canonical)

### Admin panel (`admin`)

- `POST /admin/categories`
- `GET /admin/categories`
- `POST /admin/products`
- `GET /admin/products`
- `POST /admin/products/{product_id}/images`
- `POST /admin/skus`
- `GET /admin/skus`
- `POST /admin/inventory`
- `GET /admin/skus/{sku_id}/inventory-card`
- `POST /admin/pricing-rules`
- `GET /admin/pricing-rules`
- `POST /admin/bulk/sku-prices`
- `POST /admin/bulk/sku-stocks`
- `POST /admin/bulk/sku-statuses`
- `POST /admin/imports/products`
- `GET /admin/reports/business-rules`
- `GET /admin/reports/revenue`
- `GET /admin/reports/top-products`
- `GET /admin/reports/conversion`
- `GET /admin/reports/average-check`
- `GET /admin/reports/retention-ltv`

### Admin order operations (`orders-admin`)

- `POST /orders/{order_id}/status`
- `POST /orders/{order_id}/cod/confirm`

---

## 3) Integration/technical API

### Pricing (`pricing`)

- `POST /pricing/rules`
- `GET /pricing/rules`
- `POST /pricing/calculate`

Notes:
1. For admin frontend use only `/admin/*` and `orders-admin` endpoints.
2. For storefront use only user tags/endpoints.
3. Hidden `/catalog/*` write routes are compatibility endpoints and not canonical for UI.
