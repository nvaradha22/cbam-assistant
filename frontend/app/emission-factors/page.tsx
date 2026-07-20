"use client"
import { useState, useEffect } from "react"
import type { EmissionFactor, APIResponse } from "@/lib/types"

export default function EmissionFactorsPage() {
  const [factors, setFactors] = useState<EmissionFactor[]>([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState("")
  const [q, setQ] = useState("")

  const load = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (category) params.set("category", category)
      if (q) params.set("q", q)
      const res: APIResponse<EmissionFactor[]> = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/emission-factors?${params}`
      ).then((r) => r.json())
      setFactors(res.data || [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const downloadCSV = () => {
    const header = "category,name,country_code,factor_value,unit,source"
    const rows = factors.map((f) => `${f.category},${f.name},${f.country_code || ""},${f.factor_value},${f.unit},${f.source || ""}`)
    const blob = new Blob([[header, ...rows].join("\n")], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a"); a.href = url; a.download = "emission_factors.csv"; a.click()
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Emission Factor Library</h1>
          <p style={{ color: "#8888AA", fontSize: 13, marginTop: 4 }}>IEA 2023 + IPCC AR6 + EU MRR factors</p>
        </div>
        <button className="btn-secondary" onClick={downloadCSV}>Download CSV</button>
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ width: 180 }}>
          <option value="">All Categories</option>
          <option value="electricity">Electricity</option>
          <option value="fuel">Fuel</option>
          <option value="material">Material</option>
        </select>
        <input type="text" placeholder="Search by name..." value={q} onChange={(e) => setQ(e.target.value)} style={{ width: 260 }} />
        <button className="btn-primary" onClick={load}>Filter</button>
      </div>

      <div className="panel" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ padding: 24, color: "#8888AA" }}>Loading...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Name</th>
                <th>Country</th>
                <th>Factor Value</th>
                <th>Unit</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {factors.map((f) => (
                <tr key={f.id}>
                  <td><span className={`badge-${f.category === "electricity" ? "info" : f.category === "fuel" ? "warning" : "success"}`}>{f.category}</span></td>
                  <td>{f.name}</td>
                  <td style={{ fontFamily: "monospace", color: "#0066CC" }}>{f.country_code || "—"}</td>
                  <td style={{ fontFamily: "monospace", fontWeight: 600 }}>{f.factor_value}</td>
                  <td style={{ color: "#8888AA", fontSize: 12 }}>{f.unit}</td>
                  <td style={{ color: "#8888AA", fontSize: 12 }}>{f.source || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <div style={{ padding: "10px 16px", color: "#8888AA", fontSize: 12 }}>
          {factors.length} factor{factors.length !== 1 ? "s" : ""}
        </div>
      </div>
    </div>
  )
}
