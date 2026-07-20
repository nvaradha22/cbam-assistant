from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class SupplierCreate(BaseModel):
    name: str
    country_code: str
    factory_name: Optional[str] = None
    contact_email: Optional[str] = None
    installation_id: Optional[str] = None
    cbam_data_available: bool = False
    notes: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    country_code: Optional[str] = None
    factory_name: Optional[str] = None
    contact_email: Optional[str] = None
    installation_id: Optional[str] = None
    cbam_data_available: Optional[bool] = None
    notes: Optional[str] = None


class SupplierResponse(BaseModel):
    id: str
    name: str
    country_code: str
    factory_name: Optional[str]
    contact_email: Optional[str]
    installation_id: Optional[str]
    cbam_data_available: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
