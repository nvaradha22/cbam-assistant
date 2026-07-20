"use client"
import { useState } from "react"
import type { CalculationResult, APIResponse } from "@/lib/types"

const SECTORS = [
  { value: "steel_bof", label: "Steel — Basic Oxygen Furnace (BOF)" },
  { value: "steel_eaf", label: "Steel — Electric Arc Furnace (EAF)" },
  { value: "aluminium", label: "Aluminium — Primary (Electrolysis)" },
  { value: "cement", label: "Cement (Clinker)" },
  { value: "fertilizer", label: "Fertilizer — Ammonia (SMR)" },
]

const EF_DEFAULTS: Record<string, number> = {
  ARE: 0.4057, SAU: 0.695, QAT: 0.465, KWT: 0.666, BHR: 0.643, OMN: 0.522, IND: 0.708, CHN: 0.581,
}

export default function CalculatorPage() {
  const [sector, setSector] = useState("steel_bof")
  const [fields, setFields] = useState<Record<string, string>>({})
  const [result, setResult] = useState<CalculationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const set = (k: string, v: string) => setFields((f) => ({ ...f, [k]: v }))
  const num = (k: string) => parseFloat(fields[k] || "0")

  const buildPayload = () => {
    const base = { sector, production_quantity: num("production_quantity") }
    if (sector === "steel_bof") return { ...base, hot_metal_quantity: num("hot_metal_quantity"), scrap_quantity: num("scrap_quantity"), coal_consumption: num("coal_consumption"), electricity_mwh: num("electricity_mwh"), electricity_ef: num("electricity_ef") }
    if (sector === "steel_eaf") return { ...base, scrap_quantity: num("scrap_quantity"), electricity_mwh: num("electricity_mwh"), electricity_ef: num("electricity_ef"), electrode_consumption: num("electrode_consumption") }
    if (sector === "aluminium") return { ...base, alumina_quantity: num("alumina_quantity"), electricity_mwh: num("electricity_mwh"), electricity_ef: num("electricity_ef"), anode_consumption: num("anode_consumption") }
    if (sector === "cement") return { ...base, clinker_quantity: num("clinker_quantity"), fuel_type: fields["fuel_type"] || "coal", fuel_consumption: num("fuel_consumption"), fuel_ef: num("fuel_ef") }
    if (sector === "fertilizer") return { ...base, natural_gas_consumption: num("natural_gas_consumption"), electricity_mwh: num("electricity_mwh"), electricity_ef: num("electricity_ef") }
    return base
  }

  const calculate = async () => {
    setLoading(true)
    setError(null)
    try {
      const res: APIResponse<CalculationResult> = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/calculator/calculate`,
        { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(buildPayload()) }
      ).then((r) => r.json())
      if (res.error) throw new Error(res.error.message)
      setResult(res.data)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Calculation failed")
    } finally {
      setLoading(false)
    }
  }

  const Field = ({ k, label, placeholder }: { k: string; label: string; placeholder?: string }) => (
    <div style={{ marginBottom: 12 }}>
      <label style={{ display: "block", color: "#8888AA", fontSize: 12, marginBottom: 4 }}>{label}</label>
      <input type="number" step="any" placeholder={placeholder} value={fields[k] || ""} onChange={(e) => set(k, e.target.value)} />
    </div>
  )

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Emission Calculator</h1>
        <p style={{ color: "#8888AA", fontSize: 13, marginTop: 4 }}>EU MRR methodology — all 5 CBAM sectors</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, maxWidth: 900 }}>
        {/* Form */}
        <div className="panel">
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", color: "#8888AA", fontSize: 12, marginBottom: 4 }}>Sector / Production Route</label>
            <select value={sector} onChange={(e) => { setSector(e.target.value); setFields({}); setResult(null) }}>
              {SECTORS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>

          <Field k="production_quantity" label="Production Quantity (tonnes output)" placeholder="e.g. 1000" />

          {(sector === "steel_bof") && <>
            <Field k="hot_metal_quantity" label="Hot Metal Quantity (tonnes)" />
            <Field k="scrap_quantity" label="Scrap Quantity (tonnes)" />
            <Field k="coal_consumption" label="Coal Consumption (GJ)" />
            <Field k="electricity_mwh" label="Electricity Consumption (MWh)" />
            <Field k="electricity_ef" label="Electricity Emission Factor (tCO₂e/MWh)" placeholder="e.g. 0.4057 for UAE" />
          </>}
          {(sector === "steel_eaf") && <>
            <Field k="scrap_quantity" label="Scrap Quantity (tonnes)" />
            <Field k="electricity_mwh" label="Electricity Consumption (MWh)" />
            <Field k="electricity_ef" label="Electricity Emission Factor (tCO₂e/MWh)" />
            <Field k="electrode_consumption" label="Electrode Consumption (kg)" />
          </>}
          {(sector === "aluminium") && <>
            <Field k="alumina_quantity" label="Alumina Quantity (tonnes)" />
            <Field k="electricity_mwh" label="Electricity Consumption (MWh)" />
            <Field k="electricity_ef" label="Electricity Emission Factor (tCO₂e/MWh)" />
            <Field k="anode_consumption" label="Anode Consumption (tonnes)" />
          </>}
          {(sector === "cement") && <>
            <Field k="clinker_quantity" label="Clinker Quantity (tonnes)" />
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: "block", color: "#8888AA", fontSize: 12, marginBottom: 4 }}>Fuel Type</label>
              <select value={fields["fuel_type"] || "coal"} onChange={(e) => set("fuel_type", e.target.value)}>
                {["coal", "natural_gas", "diesel", "heavy_fuel_oil", "lpg"].map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            <Field k="fuel_consumption" label="Fuel Consumption (GJ)" />
            <Field k="fuel_ef" label="Fuel Emission Factor (tCO₂e/GJ)" placeholder="e.g. 0.0946 for coal" />
          </>}
          {(sector === "fertilizer") && <>
            <Field k="natural_gas_consumption" label="Natural Gas Consumption (GJ)" />
            <Field k="electricity_mwh" label="Electricity Consumption (MWh)" />
            <Field k="electricity_ef" label="Electricity Emission Factor (tCO₂e/MWh)" />
          </>}

          {/* EF quick reference */}
          <div style={{ background: "#0A0A0F", border: "1px solid #1E1E2E", padding: 10, marginTop: 8, marginBottom: 16 }}>
            <div style={{ color: "#8888AA", fontSize: 11, marginBottom: 6, fontWeight: 600 }}>ELECTRICITY EF QUICK REF (tCO₂e/MWh)</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {Object.entries(EF_DEFAULTS).map(([c, v]) => (
                <span key={c} style={{ fontSize: 11, color: "#8888AA" }}>{c}: <strong style={{ color: "#E8E8F0" }}>{v}</strong></span>
              ))}
            </div>
          </div>

          {error && <div style={{ color: "#FF4444", fontSize: 13, marginBottom: 12 }}>{error}</div>}
          <button className="btn-primary" onClick={calculate} disabled={loading} style={{ width: "100%" }}>
            {loading ? "Calculating..." : "Calculate Embedded Emissions"}
          </button>
        </div>

        {/* Result */}
        <div>
          {result ? (
            <div className="panel">
              <div style={{ color: "#8888AA", fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 16 }}>
                Calculation Result
              </div>
              {[
                { label: "Direct Emissions", value: result.direct_emissions, unit: "tCO₂e" },
                { label: "Indirect Emissions", value: result.indirect_emissions, unit: "tCO₂e" },
                { label: "Embedded Emissions", value: result.embedded_emissions, unit: "tCO₂e", highlight: true },
                { label: "Emission Intensity", value: result.emission_intensity, unit: "tCO₂e/tonne", highlight: true },
              ].map((r) => (
                <div key={r.label} style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid #1E1E2E" }}>
                  <span style={{ color: "#8888AA", fontSize: 13 }}>{r.label}</span>
                  <span style={{ color: r.highlight ? "#0066CC" : "#E8E8F0", fontSize: 14, fontWeight: r.highlight ? 700 : 400 }}>
                    {r.value.toFixed(4)} <span style={{ color: "#8888AA", fontSize: 11 }}>{r.unit}</span>
                  </span>
                </div>
              ))}
              <div style={{ marginTop: 16 }}>
                <div style={{ color: "#8888AA", fontSize: 12, marginBottom: 8 }}>Calculation Log</div>
                <div style={{ background: "#0A0A0F", border: "1px solid #1E1E2E", padding: 10, fontSize: 11, fontFamily: "monospace", color: "#8888AA", maxHeight: 200, overflow: "auto" }}>
                  {Object.entries((result.calculation_log as Record<string, unknown>)?.steps || {}).map(([k, v]) => (
                    <div key={k} style={{ marginBottom: 4 }}><strong style={{ color: "#E8E8F0" }}>{k}:</strong> {String(v)}</div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="panel" style={{ color: "#8888AA", fontSize: 13 }}>
              Fill in the form and click Calculate to see results.
              <div style={{ marginTop: 16, fontSize: 12 }}>
                <strong style={{ color: "#E8E8F0" }}>Formula:</strong>
                <br />Embedded = Direct + (Electricity × Electricity EF)
                <br />Intensity = Embedded / Production Quantity
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
