from fastapi import APIRouter, HTTPException
from typing import Annotated, Union
from pydantic import Field
from app.schemas.calculator import (
    SteelBOFInput, SteelEAFInput, AluminiumInput, CementInput, FertilizerInput,
    CalculationResult, DefaultFactorsResponse,
)
from app.schemas.common import APIResponse
from app.services import cbam_calculator as calc

router = APIRouter(prefix="/api/calculator", tags=["calculator"])

CalcInput = Annotated[
    Union[SteelBOFInput, SteelEAFInput, AluminiumInput, CementInput, FertilizerInput],
    Field(discriminator="sector"),
]


@router.post("/calculate", response_model=APIResponse[CalculationResult])
async def calculate(payload: CalcInput) -> APIResponse[CalculationResult]:  # type: ignore[valid-type]
    sector = payload.sector
    try:
        if sector == "steel_bof":
            r = calc.calculate_steel_bof(
                payload.hot_metal_quantity, payload.scrap_quantity,
                payload.coal_consumption, payload.electricity_mwh,
                payload.electricity_ef, payload.production_quantity,
            )
        elif sector == "steel_eaf":
            r = calc.calculate_steel_eaf(
                payload.scrap_quantity, payload.electricity_mwh,
                payload.electricity_ef, payload.electrode_consumption,
                payload.production_quantity,
            )
        elif sector == "aluminium":
            r = calc.calculate_aluminium(
                payload.alumina_quantity, payload.electricity_mwh,
                payload.electricity_ef, payload.anode_consumption,
                payload.production_quantity,
            )
        elif sector == "cement":
            r = calc.calculate_cement(
                payload.clinker_quantity, payload.fuel_type,
                payload.fuel_consumption, payload.production_quantity,
            )
        elif sector == "fertilizer":
            r = calc.calculate_fertilizer(
                payload.natural_gas_consumption, payload.electricity_mwh,
                payload.electricity_ef, payload.production_quantity,
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown sector: {sector}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return APIResponse.ok(CalculationResult(
        sector=r.sector,
        direct_emissions=r.direct_emissions,
        indirect_emissions=r.indirect_emissions,
        embedded_emissions=r.embedded_emissions,
        emission_intensity=r.emission_intensity,
        calculation_method=r.calculation_method,
        calculation_log=r.calculation_log,
    ))


@router.get("/defaults/{sector}", response_model=APIResponse[DefaultFactorsResponse])
async def get_defaults(sector: str) -> APIResponse[DefaultFactorsResponse]:
    if sector not in calc.SECTOR_DEFAULTS:
        raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found")
    return APIResponse.ok(DefaultFactorsResponse(sector=sector, defaults=calc.SECTOR_DEFAULTS[sector]))
