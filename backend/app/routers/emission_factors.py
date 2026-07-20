from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.models.emission_factor import EmissionFactor
from app.schemas.common import APIResponse

router = APIRouter(prefix="/api/emission-factors", tags=["emission-factors"])


@router.get("/")
async def list_emission_factors(
    category: str | None = Query(None),
    country: str | None = Query(None),
    q: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[list]:
    stmt = select(EmissionFactor)
    filters = []
    if category:
        filters.append(EmissionFactor.category == category)
    if country:
        filters.append(EmissionFactor.country_code == country)
    if q:
        filters.append(EmissionFactor.name.ilike(f"%{q}%"))
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(EmissionFactor.category, EmissionFactor.name).limit(200)
    result = await db.execute(stmt)
    factors = result.scalars().all()
    return APIResponse.ok([
        {
            "id": f.id, "category": f.category, "name": f.name,
            "country_code": f.country_code, "factor_value": float(f.factor_value),
            "unit": f.unit, "source": f.source,
            "valid_from": f.valid_from.isoformat() if f.valid_from else None,
            "valid_to": f.valid_to.isoformat() if f.valid_to else None,
        }
        for f in factors
    ])
