# API documentation (without AI module)

Base URL: `/api/v1`

## Why there are similar endpoints (`/admin/*` and `/catalog/*`)

There are **two API styles** in this project:

1. **Domain API** (`/catalog`, `/pricing`, `/orders`, ...)
   - closer to internal domain models (`title`, `base_price`, `variant_id`, etc.).
   - useful for backend/backend integrations.

2. **Backoffice API** (`/admin/*`)
   - adapted for admin panel UX (`name`, `external_key`, bulk operations, imports, reports).
   - includes operational features absent in domain API.

So `POST /admin/categories` and `POST /catalog/categories` are not ideal duplication; they are two contracts over similar business entities.

---

## Recommended usage (to avoid duplication in frontend docs)

### For **admin panel frontend**: use `/admin/*` as canonical.

### For **storefront/user frontend**: use:
- `/auth/*`
- read-only catalog endpoints from `/catalog/*`
- `/cart/*`
- `/orders/*`

### For **integrations/technical clients**:
- use domain endpoints (`/catalog/*`, `/pricing/*`) only when you intentionally need low-level contract.

---

## Access matrix

- `USER` and `ADMIN`: `/catalog` (read), `/cart`, `/orders` (read + checkout)
- `ADMIN` only:
  - all `/admin/*`
  - write endpoints in `/catalog/*`
  - all `/pricing/*`
  - order status management endpoints in `/orders/*`

---

## 1) User/storefront API

### Auth

- `POST /auth/register` — register user + issue tokens.
- `POST /auth/login` — login + issue tokens.
- `POST /auth/refresh` — refresh token pair.
- `GET /auth/me` — current user profile.
- `PATCH /auth/profile` — update profile fields.

### Catalog (storefront)

- `GET /catalog/categories` — categories list.
- `GET /catalog/products` — products list with images and rating summary.
- `POST /catalog/products/{product_id}/reviews` — add review.
- `GET /catalog/products/{product_id}/reviews` — list reviews.

### Cart

- `POST /cart/` — create cart (`user_id`).
- `GET /cart/{cart_id}` — get cart.
- `PUT /cart/{cart_id}/items/{variant_id}` — upsert cart item (`qty`, optional `promo_code`).

### Orders

- `POST /orders/checkout` — create order from cart (`payment_method`: `yookassa` or `cod`).
- `GET /orders/` — list orders.
- `GET /orders/{order_id}` — order details.

### Payments webhook (service-to-service)

- `POST /payments/yookassa/webhook` — async payment status callback from YooKassa.

---

## 2) Admin panel API (canonical for admin frontend)

### Catalog management

- `POST /admin/categories`
- `GET /admin/categories`
- `POST /admin/products`
- `GET /admin/products`
- `POST /admin/products/{product_id}/images`
- `POST /admin/skus`
- `GET /admin/skus`
- `POST /admin/inventory`
- `GET /admin/skus/{sku_id}/inventory-card`

### Pricing and bulk operations

- `POST /admin/pricing-rules`
- `GET /admin/pricing-rules`
- `POST /admin/bulk/sku-prices`
- `POST /admin/bulk/sku-stocks`
- `POST /admin/bulk/sku-statuses`

### Imports

- `POST /admin/imports/products` (`dry_run`, `upsert`, `rollback_on_error`, idempotency fields)

### Analytics/reports

- `GET /admin/reports/business-rules`
- `GET /admin/reports/revenue`
- `GET /admin/reports/top-products`
- `GET /admin/reports/conversion`
- `GET /admin/reports/average-check`
- `GET /admin/reports/retention-ltv`

### Order operations (admin rights required, route is in orders module)

- `POST /orders/{order_id}/status`
- `POST /orders/{order_id}/cod/confirm`

---

## 3) Domain API kept for compatibility/integrations

These endpoints can overlap conceptually with admin API and should be treated as
**low-level/technical** for integrations, not as canonical admin-panel contract.

### Catalog write endpoints (ADMIN)

- `POST /catalog/categories`
- `POST /catalog/products`
- `POST /catalog/variants`
- `PUT /catalog/inventory`
- `POST /catalog/attributes`

### Pricing endpoints (ADMIN)

- `POST /pricing/rules`
- `GET /pricing/rules`
- `POST /pricing/calculate`

---

## Notes for implementation

1. In admin frontend docs, do **not** document both `/admin/*` and matching `/catalog/*` operations together in one use-case.
2. For each admin screen, reference only `/admin/*` endpoints.
3. Keep `/catalog/*` write endpoints in a separate "integration/compatibility" section.
