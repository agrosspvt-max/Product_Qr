# Setup — Product QR

End-to-end setup on a fresh machine.

---

## 1. Prerequisites

| Tool       | Version          |
| ---------- | ---------------- |
| Python     | 3.11+            |
| Node       | 18+              |
| PostgreSQL | 14+              |

---

## 2. PostgreSQL

```bash
createdb product_qr
psql product_qr -f sql/schema.sql
```

This script is **idempotent** — re-running it is safe. It also seeds:

- Default admin: `admin@company.com` / `admin123`
- Sample products: `Vajeer / VJ`, `Vegmax / VG`
- Sample quantities: `1L / 1000`, `500ml / 0500`, `250ml / 0250`
- Sample presets: `Sales Team / 919999999999` (default), `Support Team / 918888888888`

> **Schema migrations:** the schema is the single source of truth. The backend
> also runs `Base.metadata.create_all()` on startup as a safety net for fresh
> envs. For production migrations, swap in Alembic — point its `env.py` at
> `app.database.Base.metadata`.

---

## 3. Backend

```bash
cd backend
cp .env.example .env       # edit DATABASE_URL, JWT_SECRET, SHORT_DOMAIN
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Test:

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

Open <http://localhost:8000/docs> for Swagger UI.

---

## 4. Frontend

```bash
cd frontend
cp .env.example .env       # VITE_API_URL=http://localhost:8000
npm install
npm run dev
```

Open <http://localhost:5173>. Sign in with the default admin and change the
password from the database (or via a custom user-management endpoint you can
add later).

---

## 5. Zoho CRM

1. **Create the custom module** `Product_QR` (Setup → Modules and Fields) with
   the fields listed in [README.md](../README.md#zoho-crm-setup).
2. Generate a Self-Client in <https://api-console.zoho.com>:
   - **Scope:** `ZohoCRM.modules.ALL,ZohoCRM.settings.ALL`
   - **Time duration:** 10 minutes (long enough to exchange the code)
3. Exchange the auth code for a **refresh token**:
   ```bash
   curl -X POST "https://accounts.zoho.com/oauth/v2/token" \
     -d "grant_type=authorization_code" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "redirect_uri=YOUR_REDIRECT_URI" \
     -d "code=YOUR_AUTH_CODE"
   ```
   Save the `refresh_token` from the response.
4. In the dashboard, go to **Settings → Zoho** and paste:
   - Client ID, Client Secret, Refresh Token
   - API Domain — `https://www.zohoapis.com` (or `.in`, `.eu`, etc., to match
     your Zoho region)
   - Module Name — `Product_QR`

The backend caches the access token in memory; on `401` it auto-refreshes.

---

## 6. First batch

1. Settings → Short Domain → set `https://qr.company.com` (or your real host).
2. Settings → Zoho → fill credentials.
3. Generate Codes → pick Product, Quantity, Month, Year, Preset, count (try 10).
4. Click **Generate Codes**.
5. On the result card: **Download Excel** and **View Batch** to inspect rows.
6. Anything with `zoho_sync_status = FAILED`? Hit **Retry Failed** on the batch
   detail page.

---

## 7. Production checklist

- [ ] Change the default admin password (`UPDATE admin_users …`).
- [ ] Set a strong `JWT_SECRET` (32+ random chars).
- [ ] Terminate TLS in front of FastAPI (nginx, Caddy, ALB, etc.).
- [ ] Make the short domain (`qr.company.com`) point at the backend host.
- [ ] Restrict `CORS_ORIGINS` to the real frontend origin.
- [ ] Back up Postgres — `qr_codes` rows are the source of truth for codes
      already printed on packaging.
- [ ] Rotate the Zoho refresh token periodically and update Settings → Zoho.

---

## 8. Troubleshooting

**"Could not generate a unique 17-char code"** — the 36⁵ = ~60M random suffix
space is nearly exhausted for that prefix. Add a new product/quantity combo or
extend the suffix length in `app/services/code_generator.py`.

**"Zoho not configured"** — fill Settings → Zoho. The DB row still saves with
`zoho_sync_status = FAILED`; use **Retry Failed** once credentials are in.

**Token 5–7 chars exhausted** — `app/services/short_token.py` already escalates
length on collision; you can raise `MAX_LENGTH` if needed.
