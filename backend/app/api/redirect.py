"""Public short-link redirect to WhatsApp.

NOTE: this route is intentionally unauthenticated and mounted at the root.
It only matches uppercase 5-7 alphanumeric tokens so it never collides with
other API routes.
"""
from __future__ import annotations

import re
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.qr_code import QRCode

router = APIRouter(tags=["redirect"], include_in_schema=False)

_TOKEN_RE = re.compile(r"^[A-Z0-9]{5,7}$")


@router.get("/{short_token}")
def short_redirect(short_token: str, db: Session = Depends(get_db)) -> RedirectResponse:
    if not _TOKEN_RE.match(short_token or ""):
        raise HTTPException(404, "Not found")

    qr = (
        db.query(QRCode)
        .filter(QRCode.short_token == short_token)
        .first()
    )
    if not qr:
        raise HTTPException(404, "Not found")

    # Build the WhatsApp redirect freshly from preset + code (URL-encode the code).
    preset = qr.whatsapp_preset
    number = (preset.whatsapp_number if preset else "").strip()
    target = f"https://wa.me/{number}?text={quote(qr.code)}"
    return RedirectResponse(target, status_code=302)
