# eComBack

FastAPI backend для e-commerce: auth, catalog, cart, checkout, платежи (YooKassa webhook), admin/API.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000`.

## Локальный запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Миграции Alembic

Применить:

```bash
alembic upgrade head
```

Откат на 1 шаг:

```bash
alembic downgrade -1
```

Создать новую миграцию:

```bash
alembic revision --autogenerate -m "message"
```


## API documentation

Structured API docs (without AI module, with duplicate-handling strategy): `docs/api.md`.

## Примеры curl

### Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","full_name":"User","password":"password123"}'
```

### Логин

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Создать корзину и оформить COD checkout

```bash
curl -X POST http://localhost:8000/api/v1/cart/ -H 'Content-Type: application/json' -d '{"user_id":1}'
curl -X POST http://localhost:8000/api/v1/orders/checkout -H 'Content-Type: application/json' -d '{"cart_id":1,"payment_method":"cod"}'
```

### YooKassa webhook (mock)

```bash
BODY='{"object":{"id":"payment_1","status":"succeeded"}}'
SIGN=$(python - <<'PY'
import hmac,hashlib
body=b'{"object":{"id":"payment_1","status":"succeeded"}}'
print(hmac.new(b'top-secret', body, hashlib.sha256).hexdigest())
PY
)
curl -X POST http://localhost:8000/api/v1/payments/yookassa/webhook \
  -H "Content-Type: application/json" \
  -H "X-Yookassa-Signature: ${SIGN}" \
  -d "$BODY"
```

## Error format

Глобально используется `application/problem+json` с полями:
`type`, `title`, `status`, `detail`, `instance`, `request_id`.

## Логи и request-id

Добавлен middleware, который:
- принимает `X-Request-ID` из запроса (или генерирует UUID),
- возвращает его в response header,
- пишет структурный JSON-лог для каждого запроса.