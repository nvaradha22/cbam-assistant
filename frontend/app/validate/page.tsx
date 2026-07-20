"use client"
import { useState } from "react"
import type { ValidationResult, APIResponse } from "@/lib/types"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function ValidatePage() {
  const [period, setPeriod] = useState("2026-Q1")
  const [result, setResult] = useState<ValidationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validate = async () => {
    setLoading(true)
    setError(null)
    try {
      const res: APIResponse<ValidationResult> = await fetch(`${API}/api/validate/report/${period}`, { method: "POST" }).then(r => r.json())
      if (res.error) throw new Error(res.error.message)
      setResult(res.data)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Validation failed")
    } finally {
      setLoading(false)
    }
  }

  const scoreColor = result ? (result.score >= 80 ? "#00C851" : result.score >= 60 ? "#FFB300" : "#FF4444") : "#8888AA"

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Validation Engine</h1>
        <p style={{ color: "#8888AA", fontSize: 13, marginTop: 4 }}>12 rule-based checks — scored 0–100</p>
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 24, maxWidth: 400 }}>
        <input type="text" value={period} onChange={(e) => setPeriod(e.target.value)} placeholder="2026-Q1" style={{ flex: 1 }} />
        <button className="btn-primary" onClick={validate} disabled={loading}>{loading ? "Validating..." : "Validate Period"}</button>
      </div>

      {error && <div style={{ color: "#FF4444", fontSize: 13, marginBottom: 16 }}>{error}</div>}

      {result && (
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 24, marginBottom: 20 }}>
            <div className="panel" style={{ padding: "16px 24px", display: "inline-flex", alignItems: "center", gap: 16 }}>
              <div>
                <div style={{ color: "#8888AA", fontSize: 11, fontWeight: 600, textTransform: "uppercase" }}>Validation Score</div>
                <div style={{ fontSize: 40, fontWeight: 700, color: scoreColor }}>{result.score}<span style={{ fontSize: 20, color: "#8888AA" }}>/100</span></div>
              </div>
              <div style={{ width: 1, height: 40, background: "#1E1E2E" }} />
              <div>
                <div style={{ color: "#FF4444", fontSize: 20, fontWeight: 700 }}>{result.issues.filter(i => i.severity === "ERROR").length}</div>
                <div style={{ color: "#8888AA", fontSize: 12 }}>Errors</div>
              </div>
              <div>
                <div style={{ color: "#FFB300", fontSize: 20, fontWeight: 700 }}>{result.issues.filter(i => i.severity === "WARNING").length}</div>
                <div style={{ color: "#8888AA", fontSize: 12 }}>Warnings</div>
              </div>
              <div>
                <div style={{ color: "#8888AA", fontSize: 20, fontWeight: 700 }}>{result.issues.filter(i => i.severity === "INFO").length}</div>
                <div style={{ color: "#8888AA", fontSize: 12 }}>Info</div>
              </div>
            </div>
          </div>

          {result.issues.length === 0 ? (
            <div className="panel" style={{ color: "#00C851" }}>All checks passed. Report is ready for submission.</div>
          ) : (
            <div className="panel" style={{ padding: 0 }}>
              <table>
                <thead>
                  <tr><th>Rule</th><th>Severity</th><th>Message</th><th>Field</th></tr>
                </thead>
                <tbody>
                  {result.issues.map((issue, i) => (
                    <tr key={i}>
                      <td style={{ fontFamily: "monospace", color: "#0066CC", fontWeight: 600 }}>{issue.rule_id}</td>
                      <td>
                        <span className={`badge-${issue.severity === "ERROR" ? "error" : issue.severity === "WARNING" ? "warning" : "info"}`}>
                          {issue.severity}
                        </span>
                      </td>
                      <td>{issue.message}</td>
                      <td style={{ fontFamily: "monospace", fontSize: 12, color: "#8888AA" }}>{issue.field || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
