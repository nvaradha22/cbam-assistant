from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.models.hs_code import HSCode
from app.schemas.hs_code import HSCodeResponse, HSCodeSearchResult
from app.schemas.common import APIResponse

router = APIRouter(prefix="/api/hs-codes", tags=["hs-codes"])


@router.get("/search", response_model=APIResponse[HSCodeSearchResult])
async def search_hs_codes(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[HSCodeSearchResult]:
    stmt = select(HSCode).where(
        or_(
            HSCode.cn_code.ilike(f"%{q}%"),
            HSCode.description.ilike(f"%{q}%"),
        )
    ).limit(50)
    result = await db.execute(stmt)
    codes = result.scalars().all()
    return APIResponse.ok(HSCodeSearchResult(results=[HSCodeResponse.model_validate(c) for c in codes], total=len(codes)))


@router.get("/{cn_code}", response_model=APIResponse[HSCodeResponse])
async def get_hs_code(cn_code: str, db: AsyncSession = Depends(get_db)) -> APIResponse[HSCodeResponse]:
    stmt = select(HSCode).where(HSCode.cn_code == cn_code)
    result = await db.execute(stmt)
    code = result.scalar_one_or_none()
    if not code:
        raise HTTPException(status_code=404, detail="CN code not found")
    return APIResponse.ok(HSCodeResponse.model_validate(code))
