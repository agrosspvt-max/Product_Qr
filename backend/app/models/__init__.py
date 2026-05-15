"""Re-export ORM models so SQLAlchemy can discover them."""
from app.models.admin_user import AdminUser
from app.models.product import Product
from app.models.quantity import Quantity
from app.models.whatsapp_preset import WhatsappPreset
from app.models.batch import GenerationBatch
from app.models.qr_code import QRCode
from app.models.app_setting import AppSetting

__all__ = [
    "AdminUser",
    "Product",
    "Quantity",
    "WhatsappPreset",
    "GenerationBatch",
    "QRCode",
    "AppSetting",
]
