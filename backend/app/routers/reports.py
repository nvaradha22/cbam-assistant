import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.report import Report
from app.models.shipment import Shipment, EmissionCalculation
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.schemas.common import APIResponse
from app.services.report_generator import generate_xml, generate_pdf
import uuid

router = APIRouter(prefix="/api/reports", tags=["reports"])


async def _collect_goods_lines(period: str, db: AsyncSession) -> list[dict]:
    stmt = select(Shipment).where(Shipment.reporting_period == period)
    result = await db.execute(stmt)
    shipments = result.scalars().all()

    lines = []
    for s in shipments:
        calc_stmt = select(EmissionCalculation).where(EmissionCalculation.shipment_id == s.id)
        calc_result = await db.execute(calc_stmt)
        calc = calc_result.scalar_one_or_none()

        lines.append({
            "cn_code": s.product.cn_code if s.product else "",
            "country_of_origin": s.product.country_of_origin if s.product else "",
            "quantity": float(s.quantity),
            "unit": s.unit,
            "embedded_emissions": float(calc.embedded_emissions) if calc and calc.embedded_emissions else 0,
            "emission_intensity": float(calc.emission_intensity) if calc and calc.emission_intensity else 0,
            "production_route": s.product.production_route if s.product else "",
            "installation_id": s.supplier.installation_id if s.supplier else "",
            "calculation_method": calc.calculation_method if calc else "default",
            "supplier_name": s.supplier.name if s.supplier else "",
        })
    return lines


@router.post("/generate", response_model=APIResponse[ReportResponse])
async def generate_report(payload: ReportGenerateRequest, db: AsyncSession = Depends(get_db)) -> APIResponse[ReportResponse]:
    goods_lines = await _collect_goods_lines(payload.period, db)
    if not goods_lines:
        raise HTTPException(status_code=404, detail=f"No shipments found for period {payload.period}")

    xml_path = generate_xml(payload.period, payload.declarant_name, payload.eori, payload.declarant_country, goods_lines)
    pdf_path = generate_pdf(payload.period, payload.declarant_name, payload.eori, payload.declarant_country, goods_lines)

    report = Report(
        id=str(uuid.uuid4()),
        reporting_period=payload.period,
        status="draft",
        xml_path=xml_path,
        pdf_path=pdf_path,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return APIResponse.ok(ReportResponse.model_validate(report))


@router.get("/", response_model=APIResponse[list[ReportResponse]])
async def list_reports(db: AsyncSession = Depends(get_db)) -> APIResponse[list[ReportResponse]]:
    result = await db.execute(select(Report).order_by(Report.created_at.desc()))
    reports = result.scalars().all()
    return APIResponse.ok([ReportResponse.model_validate(r) for r in reports])


@router.get("/{report_id}", response_model=APIResponse[ReportResponse])
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)) -> APIResponse[ReportResponse]:
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return APIResponse.ok(ReportResponse.model_validate(report))


@router.get("/{report_id}/download/xml")
async def download_xml(report_id: str, db: AsyncSession = Depends(get_db)) -> FileResponse:
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report or not report.xml_path or not os.path.exists(report.xml_path):
        raise HTTPException(status_code=404, detail="XML report not found")
    return FileResponse(report.xml_path, media_type="application/xml", filename=os.path.basename(report.xml_path))


@router.get("/{report_id}/download/pdf")
async def download_pdf(report_id: str, db: AsyncSession = Depends(get_db)) -> FileResponse:
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report or not report.pdf_path or not os.path.exists(report.pdf_path):
        raise HTTPException(status_code=404, detail="PDF report not found")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=os.path.basename(report.pdf_path))
