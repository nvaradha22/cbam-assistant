from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.schemas.common import APIResponse
from app.services.excel_parser import generate_template, parse_excel
import uuid

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.post("/", response_model=APIResponse[SupplierResponse])
async def create_supplier(payload: SupplierCreate, db: AsyncSession = Depends(get_db)) -> APIResponse[SupplierResponse]:
    supplier = Supplier(id=str(uuid.uuid4()), **payload.model_dump())
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return APIResponse.ok(SupplierResponse.model_validate(supplier))


@router.get("/", response_model=APIResponse[list[SupplierResponse]])
async def list_suppliers(db: AsyncSession = Depends(get_db)) -> APIResponse[list[SupplierResponse]]:
    result = await db.execute(select(Supplier).order_by(Supplier.created_at.desc()))
    suppliers = result.scalars().all()
    return APIResponse.ok([SupplierResponse.model_validate(s) for s in suppliers])


@router.get("/{supplier_id}", response_model=APIResponse[SupplierResponse])
async def get_supplier(supplier_id: str, db: AsyncSession = Depends(get_db)) -> APIResponse[SupplierResponse]:
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return APIResponse.ok(SupplierResponse.model_validate(supplier))


@router.put("/{supplier_id}", response_model=APIResponse[SupplierResponse])
async def update_supplier(supplier_id: str, payload: SupplierUpdate, db: AsyncSession = Depends(get_db)) -> APIResponse[SupplierResponse]:
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(supplier, k, v)
    await db.commit()
    await db.refresh(supplier)
    return APIResponse.ok(SupplierResponse.model_validate(supplier))


@router.get("/template/download")
async def download_template() -> Response:
    template_bytes = generate_template()
    return Response(
        content=template_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=cbam_supplier_template.xlsx"},
    )


@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)) -> APIResponse[dict]:
    content = await file.read()
    result = parse_excel(content)
    return APIResponse.ok(result)
