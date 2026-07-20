"use client"
import { useState, useEffect } from "react"
import type { Report, APIResponse } from "@/lib/types"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ period: "2026-Q1", declarant_name: "", eori: "", declarant_country: "AE" })
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    const res: APIResponse<Report[]> = await fetch(`${API}/api/reports/`).then(r => r.json())
    setReports(res.data || [])
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const generate = async () => {
    setGenerating(true)
    setError(null)
    try {
      const res: APIResponse<Report> = await fetch(`${API}/api/reports/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ period: form.period, declarant_name: form.declarant_name, eori: form.eori, declarant_country: form.declarant_country }),
      }).then(r => r.json())
      if (res.error) throw new Error(res.error.message)
      setShowForm(false)
      load()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed")
    } finally {
      setGenerating(false)
    }
  }

  const statusColor = (s: string) => s === "submitted" ? "#00C851" : s === "validated" ? "#FFB300" : "#8888AA"

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Reports</h1>
          <p style={{ color: "#8888AA", fontSize: 13, marginTop: 4 }}>XML (CBAM Transitional Registry) + PDF</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ Generate Report"}
        </button>
      </div>

      {showForm && (
        <div className="panel" style={{ marginBottom: 24, maxWidth: 500 }}>
          <div style={{ color: "#8888AA", fontSize: 12, fontWeight: 600, textTransform: "uppercase", marginBottom: 16 }}>Generate CBAM Report</div>
          {[
            { k: "period", label: "Reporting Period", placeholder: "2026-Q1" },
            { k: "declarant_name", label: "Declarant Name" },
            { k: "eori", label: "EORI Number" },
            { k: "declarant_country", label: "Country Code", placeholder: "AE" },
          ].map(({ k, label, placeholder }) => (
            <div key={k} style={{ marginBottom: 12 }}>
              <label style={{ display: "block", color: "#8888AA", fontSize: 12, marginBottom: 4 }}>{label}</label>
              <input type="text" placeholder={placeholder} value={(form as Record<string, string>)[k]} onChange={(e) => setForm(f => ({ ...f, [k]: e.target.value }))} />
            </div>
          ))}
          {error && <div style={{ color: "#FF4444", fontSize: 13, marginBottom: 12 }}>{error}</div>}
          <button className="btn-primary" onClick={generate} disabled={generating}>{generating ? "Generating..." : "Generate XML + PDF"}</button>
        </div>
      )}

      <div className="panel" style={{ padding: 0 }}>
        {loading ? <div style={{ padding: 24, color: "#8888AA" }}>Loading...</div> : (
          <table>
            <thead>
              <tr><th>Period</th><th>Status</th><th>Validation Score</th><th>Created</th><th>Downloads</th></tr>
            </thead>
            <tbody>
              {reports.length === 0 ? (
                <tr><td colSpan={5} style={{ color: "#8888AA", textAlign: "center", padding: 24 }}>No reports yet. Generate one above.</td></tr>
              ) : reports.map((r) => (
                <tr key={r.id}>
                  <td style={{ fontFamily: "monospace", fontWeight: 600, color: "#0066CC" }}>{r.reporting_period}</td>
                  <td>
                    <span style={{ color: statusColor(r.status), fontWeight: 600, fontSize: 12, textTransform: "uppercase" }}>
                      {r.status}
                    </span>
                  </td>
                  <td>
                    {r.validation_score !== null ? (
                      <span style={{ color: (r.validation_score || 0) >= 80 ? "#00C851" : "#FFB300", fontWeight: 600 }}>
                        {r.validation_score}/100
                      </span>
                    ) : "—"}
                  </td>
                  <td style={{ color: "#8888AA", fontSize: 12 }}>{new Date(r.created_at).toLocaleDateString()}</td>
                  <td>
                    <div style={{ display: "flex", gap: 8 }}>
                      {r.xml_path && (
                        <a href={`${API}/api/reports/${r.id}/download/xml`} className="btn-secondary" style={{ textDecoration: "none", padding: "4px 10px", fontSize: 12 }}>
                          XML
                        </a>
                      )}
                      {r.pdf_path && (
                        <a href={`${API}/api/reports/${r.id}/download/pdf`} className="btn-secondary" style={{ textDecoration: "none", padding: "4px 10px", fontSize: 12 }}>
                          PDF
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
