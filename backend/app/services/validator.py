"""
CBAM Validation Engine
12 rule-based checks. Returns score (0-100) and issues list.
"""
from typing import Any
from app.schemas.validation import ValidationIssue, ValidationResult
from app.services.cbam_calculator import SECTOR_INTENSITY_RANGES, ELECTRICITY_EF

VALID_CBAM_SECTORS = {"steel_bof", "steel_eaf", "aluminium", "cement", "fertilizer", "electricity", "hydrogen"}

# EU member state codes — CBAM only applies to non-EU imports
EU_COUNTRY_CODES = {
    "AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA",
    "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD",
    "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE",
}

VALID_PERIOD_PATTERN = r"^\d{4}-Q[1-4]$"


def _add_issue(
    issues: list[ValidationIssue],
    rule_id: str,
    severity: str,
    message: str,
    field: str | None = None,
) -> None:
    issues.append(ValidationIssue(rule_id=rule_id, severity=severity, message=message, field=field))


def validate_shipment(shipment_data: dict[str, Any]) -> ValidationResult:
    """
    Validate a single shipment dict. Returns score + issues.
    shipment_data keys: cn_code, quantity, embedded_emissions, emission_intensity,
    electricity_ef, supplier_country, reporting_period, shipment_date,
    installation_id, calculation_method, declaration_uploaded, sector
    """
    import re

    issues: list[ValidationIssue] = []

    # V001 — CN code is CBAM-covered
    cn_code = shipment_data.get("cn_code", "")
    cbam_applicable = shipment_data.get("cbam_applicable", True)
    if not cbam_applicable:
        _add_issue(issues, "V001", "ERROR", f"CN code {cn_code} is not a CBAM-covered code.", "cn_code")

    # V002 — Quantity > 0
    quantity = shipment_data.get("quantity", 0)
    if not quantity or float(quantity) <= 0:
        _add_issue(issues, "V002", "ERROR", "Quantity must be greater than 0.", "quantity")

    # V003 — Embedded emissions > 0
    embedded = shipment_data.get("embedded_emissions", 0)
    if not embedded or float(embedded) <= 0:
        _add_issue(issues, "V003", "ERROR", "Embedded emissions must be greater than 0.", "embedded_emissions")

    # V004 — Emission intensity within sector range
    sector = shipment_data.get("sector", "")
    intensity = shipment_data.get("emission_intensity", 0)
    if sector in SECTOR_INTENSITY_RANGES and intensity:
        lo, hi = SECTOR_INTENSITY_RANGES[sector]
        if not (lo <= float(intensity) <= hi):
            _add_issue(
                issues, "V004", "WARNING",
                f"Emission intensity {intensity} tCO2e/t is outside expected range ({lo}–{hi}) for {sector}.",
                "emission_intensity",
            )

    # V005 — Electricity EF matches supplier country
    supplier_country = shipment_data.get("supplier_country", "")
    electricity_ef = shipment_data.get("electricity_ef")
    if supplier_country and electricity_ef and supplier_country in ELECTRICITY_EF:
        expected = ELECTRICITY_EF[supplier_country]
        if abs(float(electricity_ef) - expected) > 0.05:
            _add_issue(
                issues, "V005", "WARNING",
                f"Electricity emission factor {electricity_ef} differs from country default {expected} for {supplier_country}.",
                "electricity_ef",
            )

    # V006 — Supplier country is non-EU
    if supplier_country in EU_COUNTRY_CODES:
        _add_issue(
            issues, "V006", "ERROR",
            f"Supplier country {supplier_country} is an EU member state. CBAM only applies to non-EU imports.",
            "supplier_country",
        )

    # V007 — Reporting period format
    period = shipment_data.get("reporting_period", "")
    if not re.match(VALID_PERIOD_PATTERN, str(period)):
        _add_issue(issues, "V007", "ERROR", f"Reporting period '{period}' is invalid. Expected format: YYYY-Q1.", "reporting_period")

    # V008 — Shipment date within reporting period
    shipment_date = shipment_data.get("shipment_date", "")
    if period and shipment_date and re.match(VALID_PERIOD_PATTERN, str(period)):
        try:
            from datetime import date
            year, q = str(period).split("-Q")
            q_month_ranges = {"1": (1, 3), "2": (4, 6), "3": (7, 9), "4": (10, 12)}
            q_start, q_end = q_month_ranges[q]
            if isinstance(shipment_date, str):
                d = date.fromisoformat(shipment_date)
            else:
                d = shipment_date
            if not (int(year) == d.year and q_start <= d.month <= q_end):
                _add_issue(
                    issues, "V008", "ERROR",
                    f"Shipment date {d} does not fall within reporting period {period}.",
                    "shipment_date",
                )
        except Exception:
            _add_issue(issues, "V008", "ERROR", "Could not parse shipment date.", "shipment_date")

    # V009 — Missing supplier installation ID
    installation_id = shipment_data.get("installation_id")
    if not installation_id:
        _add_issue(issues, "V009", "WARNING", "Supplier installation ID is missing. Required for actual data reporting.", "installation_id")

    # V010 — Default values used
    if shipment_data.get("calculation_method") == "default":
        _add_issue(issues, "V010", "INFO", "Default emission factors used. Actual supplier data preferred for accuracy.", "calculation_method")

    # V011 — Outlier check: intensity > 3x sector average
    if sector in SECTOR_INTENSITY_RANGES and intensity:
        lo, hi = SECTOR_INTENSITY_RANGES[sector]
        avg = (lo + hi) / 2
        if float(intensity) > avg * 3:
            _add_issue(
                issues, "V011", "WARNING",
                f"Emission intensity {intensity} is more than 3× the sector average ({avg:.2f}). Verify inputs.",
                "emission_intensity",
            )

    # V012 — No supplier declaration uploaded
    if not shipment_data.get("declaration_uploaded"):
        _add_issue(issues, "V012", "WARNING", "No supplier declaration document uploaded.", "declaration_uploaded")

    # Scoring
    score = 100
    for issue in issues:
        if issue.severity == "ERROR":
            score -= 20
        elif issue.severity == "WARNING":
            score -= 5
        elif issue.severity == "INFO":
            score -= 1
    score = max(0, score)

    return ValidationResult(
        score=score,
        issues=issues,
        shipment_id=shipment_data.get("shipment_id"),
        period=period,
    )
