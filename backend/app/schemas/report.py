from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReportGenerateRequest(BaseModel):
    period: str  # 2026-Q1
    declarant_name: str
    eori: str
    declarant_country: str = "AE"


class ReportResponse(BaseModel):
    id: str
    reporting_period: str
    status: str
    xml_path: Optional[str]
    pdf_path: Optional[str]
    validation_score: Optional[int]
    validation_issues: Optional[dict]
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportDownloadResponse(BaseModel):
    report_id: str
    xml_url: Optional[str]
    pdf_url: Optional[str]
