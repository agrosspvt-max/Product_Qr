from __future__ import annotations

from pydantic import BaseModel, Field


class ZohoSettings(BaseModel):
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    organization_id: str = ""
    api_domain: str = "https://www.zohoapis.com"
    module_name: str = "Product_QR"


class ShortDomainSettings(BaseModel):
    short_domain: str = Field(default="https://qr.company.com")
