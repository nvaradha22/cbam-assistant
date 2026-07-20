from pydantic import BaseModel
from datetime import datetime


class HSCodeResponse(BaseModel):
    id: str
    cn_code: str
    description: str
    sector: str
    cbam_applicable: bool
    reporting_notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class HSCodeSearchResult(BaseModel):
    results: list[HSCodeResponse]
    total: int
