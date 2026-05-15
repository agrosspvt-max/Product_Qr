# Product QR — Enterprise QR Code Generation & Zoho CRM Integration

Internal company dashboard for generating unique 17-character product QR codes, exporting Excel batches, hosting short-link redirects to WhatsApp, and syncing every generated record into a Zoho CRM custom module.

---

## Tech Stack

**Backend**
- Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic-style schema bootstrap
- PostgreSQL 14+
- Pandas + OpenPyXL for Excel export
- Requests for Zoho CRM REST API
- python-jose + passlib for JWT auth

**Frontend**
- React 18 + Vite
- TailwindCSS
- React Router v6
- React Query (TanStack)
- React Hook Form
- Axios

---

## Project Layout

```
Product_QR/
├── README.md
├── .env.example
├── .gitignore
├── sql/
│   └── schema.sql                # Raw PostgreSQL DDL
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── main.py                   # FastAPI entrypoint
│   └── app/
│       ├── config.py             # Settings (pydantic-settings)
│       ├── database.py           # SQLAlchemy engine/session
│       ├── security.py           # JWT + password hashing
│       ├── models/               # SQLAlchemy ORM models
│       ├── schemas/              # Pydantic schemas
│       ├── api/                  # FastAPI routers
│       ├── services/             # Business logic (code gen, excel, batch)
│       ├── integrations/         # Zoho CRM client
│       └── utils/                # Logger
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    ├── .env.example
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css
        ├── api/                  # Axios + service helpers
        ├── services/             # API service modules
        ├── hooks/
        ├── components/           # Reusable UI
        ├── layouts/
        └── pages/                # Screens
```

---

## Product Code Format

Every generated code is **exactly 17 characters**, uppercase alphanumeric:

```
[INITIALS:2][QTY:4][YYMM:4][SUFFIX:5]
   VJ        1000   2606    AB12C    →  VJ10002606AB12C
```

Uniqueness is enforced by a Postgres `UNIQUE` constraint plus retry-on-collision logic.

---

## Short-Link Flow

QR-printable URLs stay under 30 chars:

```
https://qr.company.com/A1B2C
```

When scanned, the backend resolves the token and 302-redirects to:

```
https://wa.me/<NUMBER>?text=<PRODUCT_CODE>
```

The customer's WhatsApp opens with the product code pre-filled. Gallabox / Zoho CRM workflows then verify the code.

---

## Setup — Backend

### 1. Postgres

```bash
createdb product_qr
psql product_qr -f sql/schema.sql
```

### 2. Environment

```bash
cd backend
cp .env.example .env
# Fill in DATABASE_URL, JWT_SECRET, Zoho creds, SHORT_DOMAIN
```

### 3. Install + Run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: <http://localhost:8000/docs>

### 4. Default admin

The schema seeds an admin user:

```
email:    admin@company.com
password: admin123     # CHANGE IMMEDIATELY in production
```

---

## Setup — Frontend

```bash
cd frontend
cp .env.example .env       # Set VITE_API_URL=http://localhost:8000
npm install
npm run dev
```

Open <http://localhost:5173>.

---

## Zoho CRM Setup

1. In Zoho CRM, create a **Custom Module** named `Product_QR` with these fields (single-line text unless noted):
   - `Name` (single line — will hold the product code)
   - `Product_Name`
   - `Product_Initials`
   - `Quantity_Label`
   - `Quantity_Code`
   - `Manufacturing_Month`
   - `Manufacturing_Year`
   - `Manufacturing_Display`
   - `WhatsApp_Number`
   - `WhatsApp_Redirect_URL` (URL field)
   - `Short_Token`
   - `Short_Link` (URL field)
   - `Batch_ID`
   - `Status` (pick list: UNUSED / USED)
   - `Code_Created_At` (date-time)

2. Generate a **Self Client** in Zoho API Console, exchange the code for a **Refresh Token** with scope:
   `ZohoCRM.modules.ALL,ZohoCRM.settings.ALL`

3. Save the credentials in **Settings → Zoho** in the dashboard:
   - Client ID, Client Secret, Refresh Token
   - API Domain (e.g. `https://www.zohoapis.com` or `https://www.zohoapis.in`)
   - Module Name (`Product_QR`)

---

## Key API Endpoints

| Method | Path                              | Description                                  |
| ------ | --------------------------------- | -------------------------------------------- |
| POST   | `/auth/login`                     | JWT login                                    |
| GET    | `/products`                       | List products                                |
| POST   | `/products`                       | Create product                               |
| PUT    | `/products/{id}`                  | Update product                               |
| DELETE | `/products/{id}`                  | Delete (soft) product                        |
| GET    | `/quantities`                     | List quantities                              |
| POST   | `/quantities`                     | Create quantity                              |
| PUT    | `/quantities/{id}`                | Update quantity                              |
| DELETE | `/quantities/{id}`                | Delete (soft) quantity                       |
| GET    | `/whatsapp-presets`               | List presets                                 |
| POST   | `/whatsapp-presets`               | Create preset                                |
| PUT    | `/whatsapp-presets/{id}`          | Update preset                                |
| GET    | `/settings/zoho`                  | Get Zoho settings                            |
| PUT    | `/settings/zoho`                  | Save Zoho settings                           |
| GET    | `/settings/short-domain`          | Get short domain                             |
| PUT    | `/settings/short-domain`          | Save short domain                            |
| POST   | `/generate-codes`                 | Generate batch + push to Zoho                |
| GET    | `/batches`                        | List batches                                 |
| GET    | `/batch/{id}`                     | Batch detail + codes                         |
| GET    | `/download-excel/{batch_id}`      | Download batch Excel                         |
| POST   | `/batch/{id}/retry-zoho`          | Retry failed Zoho syncs                      |
| GET    | `/{short_token}`                  | Public — 302 redirect to WhatsApp            |

---

## Sample request — generate codes

```http
POST /generate-codes
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "product_id": 1,
  "quantity_id": 1,
  "manufacturing_month": 6,
  "manufacturing_year": 2026,
  "whatsapp_preset_id": 1,
  "count": 500
}
```

Response:

```json
{
  "batch_id": 7,
  "batch_name": "BATCH_20260514_001",
  "total_requested": 500,
  "total_generated": 500,
  "zoho_synced": 498,
  "zoho_failed": 2,
  "excel_url": "/download-excel/7",
  "sample_codes": ["VJ10002606AB12C", "VJ100026069X7QM", "..."]
}
```

---

## Security Notes

- JWT auth on every protected endpoint. Public short-link redirect is the only unauthenticated route.
- Bcrypt password hashing.
- All inputs validated via Pydantic.
- Zoho secrets stored in DB `settings` table (encrypt-at-rest by enabling Postgres-level encryption in production).
- Bulk inserts wrapped in transactions; Zoho push uses retry + 100-record batching.

---

## License

Internal use only.
