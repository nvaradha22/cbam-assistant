from pydantic import BaseModel
from typing import Literal


class ValidationIssue(BaseModel):
    rule_id: str
    severity: Literal["ERROR", "WARNING", "INFO"]
    message: str
    field: str | None = None


class ValidationResult(BaseModel):
    score: int
    issues: list[ValidationIssue]
    shipment_id: str | None = None
    period: str | None = None
