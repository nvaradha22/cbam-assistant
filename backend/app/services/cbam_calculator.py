"""
CBAM Emission Calculator
Implements EU MRR (Monitoring, Reporting, Regulation) methodology
for all 5 CBAM sectors.
"""
from dataclasses import dataclass


# Default electricity emission factors by country (tCO2e/MWh) — IEA 2023
ELECTRICITY_EF: dict[str, float] = {
    "ARE": 0.4057,  # UAE
    "SAU": 0.6950,  # Saudi Arabia
    "QAT": 0.4650,  # Qatar
    "KWT": 0.6660,  # Kuwait
    "BHR": 0.6430,  # Bahrain
    "OMN": 0.5220,  # Oman
    "IND": 0.7080,  # India
    "CHN": 0.5810,  # China
    "EU":  0.2330,  # EU average
}

# Fuel emission factors (tCO2e/GJ) — IPCC AR6
FUEL_EF: dict[str, float] = {
    "coal":          0.0946,
    "natural_gas":   0.0561,
    "diesel":        0.0741,
    "heavy_fuel_oil": 0.0779,
    "lpg":           0.0634,
}

# Sector default emission intensity ranges (tCO2e/tonne) for outlier detection
SECTOR_INTENSITY_RANGES: dict[str, tuple[float, float]] = {
    "steel_bof":   (1.5, 3.0),
    "steel_eaf":   (0.3, 1.2),
    "aluminium":   (6.0, 20.0),
    "cement":      (0.5, 1.0),
    "fertilizer":  (1.5, 4.0),
}


@dataclass
class CalcResult:
    sector: str
    direct_emissions: float
    indirect_emissions: float
    embedded_emissions: float
    emission_intensity: float
    calculation_method: str
    calculation_log: dict


def calculate_steel_bof(
    hot_metal_quantity: float,
    scrap_quantity: float,
    coal_consumption: float,
    electricity_mwh: float,
    electricity_ef: float,
    production_quantity: float,
    method: str = "default",
) -> CalcResult:
    """Basic Oxygen Furnace steel calculation."""
    process_ef = 1.8  # tCO2e per tonne hot metal (default)
    coal_ef = FUEL_EF["coal"]

    process_emissions = hot_metal_quantity * process_ef
    fuel_emissions = coal_consumption * coal_ef
    direct_emissions = process_emissions + fuel_emissions
    indirect_emissions = electricity_mwh * electricity_ef
    embedded_emissions = direct_emissions + indirect_emissions
    emission_intensity = embedded_emissions / production_quantity if production_quantity else 0

    log = {
        "sector": "steel_bof",
        "inputs": {
            "hot_metal_quantity_t": hot_metal_quantity,
            "scrap_quantity_t": scrap_quantity,
            "coal_consumption_gj": coal_consumption,
            "electricity_mwh": electricity_mwh,
            "electricity_ef_tco2e_mwh": electricity_ef,
            "production_quantity_t": production_quantity,
        },
        "factors": {
            "process_ef_tco2e_t_hot_metal": process_ef,
            "coal_ef_tco2e_gj": coal_ef,
        },
        "steps": {
            "process_emissions": f"{hot_metal_quantity} × {process_ef} = {process_emissions:.4f} tCO2e",
            "fuel_emissions": f"{coal_consumption} × {coal_ef} = {fuel_emissions:.4f} tCO2e",
            "direct_emissions": f"{process_emissions:.4f} + {fuel_emissions:.4f} = {direct_emissions:.4f} tCO2e",
            "indirect_emissions": f"{electricity_mwh} × {electricity_ef} = {indirect_emissions:.4f} tCO2e",
            "embedded_emissions": f"{direct_emissions:.4f} + {indirect_emissions:.4f} = {embedded_emissions:.4f} tCO2e",
            "emission_intensity": f"{embedded_emissions:.4f} / {production_quantity} = {emission_intensity:.4f} tCO2e/t",
        },
    }

    return CalcResult(
        sector="steel_bof",
        direct_emissions=round(direct_emissions, 6),
        indirect_emissions=round(indirect_emissions, 6),
        embedded_emissions=round(embedded_emissions, 6),
        emission_intensity=round(emission_intensity, 6),
        calculation_method=method,
        calculation_log=log,
    )


def calculate_steel_eaf(
    scrap_quantity: float,
    electricity_mwh: float,
    electricity_ef: float,
    electrode_consumption: float,  # kg
    production_quantity: float,
    method: str = "default",
) -> CalcResult:
    """Electric Arc Furnace steel calculation."""
    electrode_ef = 3.663  # tCO2e per tonne electrode
    electrode_tonnes = electrode_consumption / 1000

    direct_emissions = electrode_tonnes * electrode_ef  # no process emissions for EAF
    indirect_emissions = electricity_mwh * electricity_ef
    embedded_emissions = direct_emissions + indirect_emissions
    emission_intensity = embedded_emissions / production_quantity if production_quantity else 0

    log = {
        "sector": "steel_eaf",
        "inputs": {
            "scrap_quantity_t": scrap_quantity,
            "electricity_mwh": electricity_mwh,
            "electricity_ef_tco2e_mwh": electricity_ef,
            "electrode_consumption_kg": electrode_consumption,
            "production_quantity_t": production_quantity,
        },
        "factors": {
            "electrode_ef_tco2e_t": electrode_ef,
        },
        "steps": {
            "electrode_emissions": f"{electrode_tonnes:.4f}t × {electrode_ef} = {direct_emissions:.4f} tCO2e",
            "indirect_emissions": f"{electricity_mwh} × {electricity_ef} = {indirect_emissions:.4f} tCO2e",
            "embedded_emissions": f"{direct_emissions:.4f} + {indirect_emissions:.4f} = {embedded_emissions:.4f} tCO2e",
            "emission_intensity": f"{embedded_emissions:.4f} / {production_quantity} = {emission_intensity:.4f} tCO2e/t",
        },
    }

    return CalcResult(
        sector="steel_eaf",
        direct_emissions=round(direct_emissions, 6),
        indirect_emissions=round(indirect_emissions, 6),
        embedded_emissions=round(embedded_emissions, 6),
        emission_intensity=round(emission_intensity, 6),
        calculation_method=method,
        calculation_log=log,
    )


def calculate_aluminium(
    alumina_quantity: float,
    electricity_mwh: float,
    electricity_ef: float,
    anode_consumption: float,  # tonnes
    production_quantity: float,
    method: str = "default",
) -> CalcResult:
    """Primary aluminium (electrolysis) calculation."""
    pfc_ef = 1.6  # tCO2e per tonne aluminium (PFC default)
    anode_ef = 3.663  # tCO2e per tonne anode

    pfc_emissions = production_quantity * pfc_ef
    anode_emissions = anode_consumption * anode_ef
    direct_emissions = pfc_emissions + anode_emissions
    indirect_emissions = electricity_mwh * electricity_ef
    embedded_emissions = direct_emissions + indirect_emissions
    emission_intensity = embedded_emissions / production_quantity if production_quantity else 0

    log = {
        "sector": "aluminium",
        "inputs": {
            "alumina_quantity_t": alumina_quantity,
            "electricity_mwh": electricity_mwh,
            "electricity_ef_tco2e_mwh": electricity_ef,
            "anode_consumption_t": anode_consumption,
            "production_quantity_t": production_quantity,
        },
        "factors": {
            "pfc_ef_tco2e_t_al": pfc_ef,
            "anode_ef_tco2e_t": anode_ef,
        },
        "steps": {
            "pfc_emissions": f"{production_quantity} × {pfc_ef} = {pfc_emissions:.4f} tCO2e",
            "anode_emissions": f"{anode_consumption} × {anode_ef} = {anode_emissions:.4f} tCO2e",
            "direct_emissions": f"{pfc_emissions:.4f} + {anode_emissions:.4f} = {direct_emissions:.4f} tCO2e",
            "indirect_emissions": f"{electricity_mwh} × {electricity_ef} = {indirect_emissions:.4f} tCO2e",
            "embedded_emissions": f"{direct_emissions:.4f} + {indirect_emissions:.4f} = {embedded_emissions:.4f} tCO2e",
            "emission_intensity": f"{embedded_emissions:.4f} / {production_quantity} = {emission_intensity:.4f} tCO2e/t",
        },
    }

    return CalcResult(
        sector="aluminium",
        direct_emissions=round(direct_emissions, 6),
        indirect_emissions=round(indirect_emissions, 6),
        embedded_emissions=round(embedded_emissions, 6),
        emission_intensity=round(emission_intensity, 6),
        calculation_method=method,
        calculation_log=log,
    )


def calculate_cement(
    clinker_quantity: float,
    fuel_type: str,
    fuel_consumption: float,  # GJ
    production_quantity: float,
    method: str = "default",
) -> CalcResult:
    """Cement (clinker) calculation."""
    calcination_ef = 0.525  # tCO2e per tonne clinker
    fuel_ef = FUEL_EF.get(fuel_type, FUEL_EF["coal"])

    calcination_emissions = clinker_quantity * calcination_ef
    fuel_emissions = fuel_consumption * fuel_ef
    direct_emissions = calcination_emissions + fuel_emissions
    indirect_emissions = 0.0  # no electricity in basic cement calc
    embedded_emissions = direct_emissions
    emission_intensity = embedded_emissions / production_quantity if production_quantity else 0

    log = {
        "sector": "cement",
        "inputs": {
            "clinker_quantity_t": clinker_quantity,
            "fuel_type": fuel_type,
            "fuel_consumption_gj": fuel_consumption,
            "production_quantity_t": production_quantity,
        },
        "factors": {
            "calcination_ef_tco2e_t_clinker": calcination_ef,
            "fuel_ef_tco2e_gj": fuel_ef,
        },
        "steps": {
            "calcination_emissions": f"{clinker_quantity} × {calcination_ef} = {calcination_emissions:.4f} tCO2e",
            "fuel_emissions": f"{fuel_consumption} × {fuel_ef} = {fuel_emissions:.4f} tCO2e",
            "direct_emissions": f"{calcination_emissions:.4f} + {fuel_emissions:.4f} = {direct_emissions:.4f} tCO2e",
            "embedded_emissions": f"{direct_emissions:.4f} tCO2e (no indirect)",
            "emission_intensity": f"{embedded_emissions:.4f} / {production_quantity} = {emission_intensity:.4f} tCO2e/t",
        },
    }

    return CalcResult(
        sector="cement",
        direct_emissions=round(direct_emissions, 6),
        indirect_emissions=0.0,
        embedded_emissions=round(embedded_emissions, 6),
        emission_intensity=round(emission_intensity, 6),
        calculation_method=method,
        calculation_log=log,
    )


def calculate_fertilizer(
    natural_gas_consumption: float,  # GJ
    electricity_mwh: float,
    electricity_ef: float,
    production_quantity: float,
    method: str = "default",
) -> CalcResult:
    """Ammonia (fertilizer) calculation — steam methane reforming default."""
    smr_ef = 1.694  # tCO2e per tonne ammonia
    ng_ef = FUEL_EF["natural_gas"]

    smr_emissions = production_quantity * smr_ef
    ng_fuel_emissions = natural_gas_consumption * ng_ef
    direct_emissions = smr_emissions + ng_fuel_emissions
    indirect_emissions = electricity_mwh * electricity_ef
    embedded_emissions = direct_emissions + indirect_emissions
    emission_intensity = embedded_emissions / production_quantity if production_quantity else 0

    log = {
        "sector": "fertilizer",
        "inputs": {
            "natural_gas_consumption_gj": natural_gas_consumption,
            "electricity_mwh": electricity_mwh,
            "electricity_ef_tco2e_mwh": electricity_ef,
            "production_quantity_t": production_quantity,
        },
        "factors": {
            "smr_ef_tco2e_t_ammonia": smr_ef,
            "ng_ef_tco2e_gj": ng_ef,
        },
        "steps": {
            "smr_process_emissions": f"{production_quantity} × {smr_ef} = {smr_emissions:.4f} tCO2e",
            "ng_fuel_emissions": f"{natural_gas_consumption} × {ng_ef} = {ng_fuel_emissions:.4f} tCO2e",
            "direct_emissions": f"{smr_emissions:.4f} + {ng_fuel_emissions:.4f} = {direct_emissions:.4f} tCO2e",
            "indirect_emissions": f"{electricity_mwh} × {electricity_ef} = {indirect_emissions:.4f} tCO2e",
            "embedded_emissions": f"{direct_emissions:.4f} + {indirect_emissions:.4f} = {embedded_emissions:.4f} tCO2e",
            "emission_intensity": f"{embedded_emissions:.4f} / {production_quantity} = {emission_intensity:.4f} tCO2e/t",
        },
    }

    return CalcResult(
        sector="fertilizer",
        direct_emissions=round(direct_emissions, 6),
        indirect_emissions=round(indirect_emissions, 6),
        embedded_emissions=round(embedded_emissions, 6),
        emission_intensity=round(emission_intensity, 6),
        calculation_method=method,
        calculation_log=log,
    )


SECTOR_DEFAULTS: dict[str, dict] = {
    "steel_bof": {
        "process_ef_tco2e_t_hot_metal": 1.8,
        "coal_ef_tco2e_gj": FUEL_EF["coal"],
        "electricity_ef_by_country": ELECTRICITY_EF,
    },
    "steel_eaf": {
        "electrode_ef_tco2e_t": 3.663,
        "electricity_ef_by_country": ELECTRICITY_EF,
    },
    "aluminium": {
        "pfc_ef_tco2e_t_al": 1.6,
        "anode_ef_tco2e_t": 3.663,
        "electricity_ef_by_country": ELECTRICITY_EF,
    },
    "cement": {
        "calcination_ef_tco2e_t_clinker": 0.525,
        "fuel_ef_by_type": FUEL_EF,
    },
    "fertilizer": {
        "smr_ef_tco2e_t_ammonia": 1.694,
        "ng_ef_tco2e_gj": FUEL_EF["natural_gas"],
        "electricity_ef_by_country": ELECTRICITY_EF,
    },
}
