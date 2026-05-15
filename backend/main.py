"""FastAPI entrypoint for the Product QR backend.

Run:  uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.batches import router as batches_router
from app.api.generate import router as generate_router
from app.api.products import router as products_router
from app.api.quantities import router as quantities_router
from app.api.redirect import router as redirect_router
from app.api.settings import router as settings_router
from app.api.whatsapp_presets import router as whatsapp_router
from app.config import settings
from app.database import Base, engine
from app.utils.logger import configure_logging, get_logger

configure_logging()
log = get_logger("main")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Best-effort: create tables if Postgres is reachable and schema.sql hasn't
    # been applied. In production we recommend running sql/schema.sql explicitly.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:  # pragma: no cover
        log.warning("Could not auto-create tables: %s", exc)
    os.makedirs(settings.EXCEL_EXPORT_DIR, exist_ok=True)
    log.info("Product QR backend started. Excel dir: %s", settings.EXCEL_EXPORT_DIR)
    yield


app = FastAPI(
    title="Product QR API",
    version="1.0.0",
    description="Enterprise QR product code generation + Zoho CRM integration.",
    lifespan=lifespan,
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins_list,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


# Order matters: register protected routers BEFORE the catch-all redirect.
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(quantities_router)
app.include_router(whatsapp_router)
app.include_router(settings_router)
app.include_router(generate_router)
app.include_router(batches_router)

# Public short-link redirect — must be last because it matches /{short_token}.
app.include_router(redirect_router)
