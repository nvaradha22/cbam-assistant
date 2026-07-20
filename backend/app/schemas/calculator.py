from pydantic import BaseModel
from typing import Optional, Literal


class SteelBOFInput(BaseModel):
    sector: Literal["steel_bof"]
    hot_metal_quantity: float  # tonnes
    scrap_quantity: float  # tonnes
    coal_consumption: float  # GJ
    electricity_mwh: float
    electricity_ef: float  # tCO2e/MWh
    production_quantity: float  # tonnes output


class SteelEAFInput(BaseModel):
    sector: Literal["steel_eaf"]
    scrap_quantity: float  # tonnes
    electricity_mwh: float
    electricity_ef: float
    electrode_consumption: float  # kg
    production_quantity: float


class AluminiumInput(BaseModel):
    sector: Literal["aluminium"]
    alumina_quantity: float  # tonnes
    electricity_mwh: float
    electricity_ef: float
    anode_consumption: float  # tonnes
    production_quantity: float


class CementInput(BaseModel):
    sector: Literal["cement"]
    clinker_quantity: float  # tonnes
    fuel_type: str
    fuel_consumption: float  # GJ
    fuel_ef: float  # tCO2e/GJ
    production_quantity: float


class FertilizerInput(BaseModel):
    sector: Literal["fertilizer"]
    natural_gas_consumption: float  # GJ
    electricity_mwh: float
    electricity_ef: float
    production_quantity: float


class CalculationResult(BaseModel):
    sector: str
    direct_emissions: float
    indirect_emissions: float
    embedded_emissions: float
    emission_intensity: float  # tCO2e/tonne
    calculation_method: str
    calculation_log: dict


class DefaultFactorsResponse(BaseModel):
    sector: str
    defaults: dict
