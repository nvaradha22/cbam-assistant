from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.shipment import Shipment, EmissionCalculation
from app.schemas.validation import ValidationResult
from app.schemas.common import APIResponse
from app.services.validator import validate_shipment

router = APIRouter(prefix="/api/validate", tags=["validation"])


@router.post("/shipment/{shipment_id}", response_model=APIResponse[ValidationResult])
async def validate_single(shipment_id: str, db: AsyncSession = Depends(get_db)) -> APIResponse[ValidationResult]:
    stmt = select(Shipment).where(Shipment.id == shipment_id)
    result = await db.execute(stmt)
    shipment = result.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    calc_stmt = select(EmissionCalculation).where(EmissionCalculation.shipment_id == shipment_id)
    calc_result = await db.execute(calc_stmt)
    calc = calc_result.scalar_one_or_none()

    data = {
        "shipment_id": shipment_id,
        "cn_code": shipment.product.cn_code if shipment.product else "",
        "cbam_applicable": True,
        "quantity": float(shipment.quantity),
        "embedded_emissions": float(calc.embedded_emissions) if calc and calc.embedded_emissions else 0,
        "emission_intensity": float(calc.emission_intensity) if calc and calc.emission_intensity else 0,
        "electricity_ef": float(calc.electricity_emission_factor) if calc and calc.electricity_emission_factor else None,
        "supplier_country": shipment.supplier.country_code if shipment.supplier else "",
        "reporting_period": shipment.reporting_period,
        "shipment_date": shipment.shipment_date,
        "installation_id": shipment.supplier.installation_id if shipment.supplier else None,
        "calculation_method": calc.calculation_method if calc else "default",
        "declaration_uploaded": shipment.supplier.cbam_data_available if shipment.supplier else False,
        "sector": "",
    }

    validation = validate_shipment(data)
    return APIResponse.ok(validation)


@router.post("/report/{period}", response_model=APIResponse[ValidationResult])
async def validate_period(period: str, db: AsyncSession = Depends(get_db)) -> APIResponse[ValidationResult]:
    stmt = select(Shipment).where(Shipment.reporting_period == period)
    result = await db.execute(stmt)
    shipments = result.scalars().all()

    if not shipments:
        raise HTTPException(status_code=404, detail=f"No shipments found for period {period}")

    all_issues = []
    total_score = 100

    for shipment in shipments:
        calc_stmt = select(EmissionCalculation).where(EmissionCalculation.shipment_id == shipment.id)
        calc_result = await db.execute(calc_stmt)
        calc = calc_result.scalar_one_or_none()

        data = {
            "shipment_id": shipment.id,
            "cn_code": shipment.product.cn_code if shipment.product else "",
            "cbam_applicable": True,
            "quantity": float(shipment.quantity),
            "embedded_emissions": float(calc.embedded_emissions) if calc and calc.embedded_emissions else 0,
            "emission_intensity": float(calc.emission_intensity) if calc and calc.emission_intensity else 0,
            "electricity_ef": float(calc.electricity_emission_factor) if calc and calc.electricity_emission_factor else None,
            "supplier_country": shipment.supplier.country_code if shipment.supplier else "",
            "reporting_period": shipment.reporting_period,
            "shipment_date": shipment.shipment_date,
            "installation_id": shipment.supplier.installation_id if shipment.supplier else None,
            "calculation_method": calc.calculation_method if calc else "default",
            "declaration_uploaded": shipment.supplier.cbam_data_available if shipment.supplier else False,
            "sector": "",
        }

        v = validate_shipment(data)
        all_issues.extend(v.issues)
        total_score = min(total_score, v.score)

    from app.schemas.validation import ValidationResult
    return APIResponse.ok(ValidationResult(score=total_score, issues=all_issues, period=period))
