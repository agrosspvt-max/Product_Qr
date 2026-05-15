from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.settings import ShortDomainSettings, ZohoSettings
from app.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


# ----------------------------- Zoho --------------------------------------


@router.get("/zoho", response_model=ZohoSettings)
def get_zoho(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> ZohoSettings:
    v = settings_service.get_many(
        db,
        [
            "zoho_client_id",
            "zoho_client_secret",
            "zoho_refresh_token",
            "zoho_organization_id",
            "zoho_api_domain",
            "zoho_module_name",
        ],
    )
    return ZohoSettings(
        client_id=v.get("zoho_client_id", ""),
        client_secret=v.get("zoho_client_secret", ""),
        refresh_token=v.get("zoho_refresh_token", ""),
        organization_id=v.get("zoho_organization_id", ""),
        api_domain=v.get("zoho_api_domain") or "https://www.zohoapis.com",
        module_name=v.get("zoho_module_name") or "Product_QR",
    )


@router.put("/zoho", response_model=ZohoSettings)
def save_zoho(
    payload: ZohoSettings,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> ZohoSettings:
    settings_service.set_many(db, {
        "zoho_client_id": payload.client_id,
        "zoho_client_secret": payload.client_secret,
        "zoho_refresh_token": payload.refresh_token,
        "zoho_organization_id": payload.organization_id,
        "zoho_api_domain": payload.api_domain.rstrip("/"),
        "zoho_module_name": payload.module_name,
    })
    db.commit()
    return payload


# ----------------------------- Short Domain ------------------------------


@router.get("/short-domain", response_model=ShortDomainSettings)
def get_short_domain(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> ShortDomainSettings:
    return ShortDomainSettings(
        short_domain=settings_service.get_value(db, "short_domain", "https://qr.company.com")
    )


@router.put("/short-domain", response_model=ShortDomainSettings)
def save_short_domain(
    payload: ShortDomainSettings,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_user),
) -> ShortDomainSettings:
    settings_service.set_value(db, "short_domain", payload.short_domain.rstrip("/"))
    db.commit()
    return payload
