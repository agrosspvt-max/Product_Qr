# API Reference — Product QR

Base URL: `http://localhost:8000` (set via `VITE_API_URL` on the frontend).
All endpoints except `GET /{short_token}` (public redirect) and `POST /auth/login` require:

```
Authorization: Bearer <jwt>
```

OpenAPI / Swagger UI is auto-published at `/docs` and `/redoc`.

---

## Auth

### `POST /auth/login`
```http
Content-Type: application/json

{
  "email": "admin@company.com",
  "password": "admin123"
}
```
Response `200`:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 43200,
  "user": {
    "id": 1,
    "email": "admin@company.com",
    "full_name": "Default Admin",
    "is_superuser": true
  }
}
```

### `GET /auth/me`
Returns the authenticated `UserOut`.

---

## Products

### `GET /products?only_active=false`
Returns `ProductOut[]`.

### `POST /products`
```json
{ "name": "Vajeer", "initials": "VJ", "is_active": true }
```

### `PUT /products/{id}`
Partial update — any field optional.
```json
{ "name": "Vajeer Premium" }
```

### `DELETE /products/{id}?hard=false`
Default is **soft delete** (sets `is_active=false`). Pass `?hard=true` to fully
remove; will 409 if any QR codes still reference the product.

---

## Quantities

Same shape — `label`, `internal_code` (must be exactly 4 alphanumeric chars,
uppercase enforced), `is_active`.

---

## WhatsApp Presets

```json
{
  "preset_name": "Sales Team",
  "whatsapp_number": "919999999999",
  "is_default": true,
  "is_active": true
}
```

`whatsapp_number` must be digits only (no `+`, no spaces). Setting
`is_default: true` automatically clears the flag on other presets.

---

## Settings

### `GET /settings/zoho` → `PUT /settings/zoho`
```json
{
  "client_id": "1000.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "client_secret": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
  "refresh_token": "1000.zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.aaaa",
  "organization_id": "60012345678",
  "api_domain": "https://www.zohoapis.com",
  "module_name": "Product_QR"
}
```

### `GET /settings/short-domain` → `PUT /settings/short-domain`
```json
{ "short_domain": "https://qr.company.com" }
```

---

## Generate

### `POST /generate-codes`
```json
{
  "product_id": 1,
  "quantity_id": 1,
  "manufacturing_month": 6,
  "manufacturing_year": 2026,
  "whatsapp_preset_id": 1,
  "count": 500
}
```
Response `200`:
```json
{
  "batch_id": 7,
  "batch_name": "BATCH_20260514_001",
  "total_requested": 500,
  "total_generated": 500,
  "zoho_synced": 498,
  "zoho_failed": 2,
  "excel_url": "/download-excel/7",
  "sample_codes": [
    "VJ10002606AB12C",
    "VJ100026069X7QM",
    "VJ1000260671ZQA",
    "VJ1000260603PLM",
    "VJ100026069MMTT"
  ]
}
```

---

## Batches

| Method | Path                          | Description                          |
| ------ | ----------------------------- | ------------------------------------ |
| GET    | `/batches`                    | List `BatchSummary[]`                |
| GET    | `/batch/{id}`                 | `BatchDetail` with all `codes[]`     |
| GET    | `/download-excel/{batch_id}`  | Streams the `.xlsx` file             |
| POST   | `/batch/{id}/retry-zoho`      | Re-push FAILED rows                  |

`BatchDetail.codes[]` items:
```json
{
  "id": 9001,
  "code": "VJ10002606AB12C",
  "short_token": "AB12C",
  "short_link": "https://qr.company.com/AB12C",
  "whatsapp_link": "https://wa.me/919999999999?text=VJ10002606AB12C",
  "zoho_sync_status": "SYNCED",
  "zoho_record_id": "550000000123456",
  "status": "UNUSED",
  "created_at": "2026-05-14T09:21:11.224Z"
}
```

---

## Public Redirect

### `GET /{short_token}` — **unauthenticated**

Resolves the short token, builds `https://wa.me/<number>?text=<code>`, and
returns `302 Found`. Token must match `[A-Z0-9]{5,7}`; everything else returns
`404`.

```
GET /AB12C  →  302 Location: https://wa.me/919999999999?text=VJ10002606AB12C
```

---

## Error format

All non-2xx responses follow FastAPI conventions:
```json
{ "detail": "Initials 'VJ' already exist" }
```

Validation errors (`422`) return the standard `loc`/`msg`/`type` list.
