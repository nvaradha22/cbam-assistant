"use client"
import { useState } from "react"
import type { HSCode, APIResponse } from "@/lib/types"

export default function HSCheckerPage() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<HSCode[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res: APIResponse<{ results: HSCode[]; total: number }> = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/hs-codes/search?q=${encodeURIComponent(query)}`
      ).then((r) => r.json())
      if (res.error) throw new Error(res.error.message)
      setResults(res.data?.results || [])
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>HS Code Checker</h1>
        <p style={{ color: "#8888AA", fontSize: 13, marginTop: 4 }}>
          Check CBAM applicability for CN codes — Annex I of EU Regulation 2023/956
        </p>
      </div>

      {/* Search */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24, maxWidth: 600 }}>
        <input
          type="text"
          placeholder="Search by CN code or product name (e.g. 7208, hot rolled steel)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
          style={{ flex: 1 }}
        />
        <button className="btn-primary" onClick={search} disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {error && (
        <div style={{ color: "#FF4444", fontSize: 13, marginBottom: 16 }}>{error}</div>
      )}

      {results.length > 0 && (
        <div className="panel" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>CN Code</th>
                <th>Description</th>
                <th>Sector</th>
                <th>CBAM Applicable</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {results.map((code) => (
                <tr key={code.id}>
                  <td style={{ fontFamily: "monospace", color: "#0066CC", fontWeight: 600 }}>
                    {code.cn_code}
                  </td>
                  <td style={{ maxWidth: 360 }}>{code.description}</td>
                  <td style={{ textTransform: "capitalize" }}>{code.sector}</td>
                  <td>
                    {code.cbam_applicable ? (
                      <span className="badge-success">YES</span>
                    ) : (
                      <span className="badge-error">NO</span>
                    )}
                  </td>
                  <td style={{ color: "#8888AA", fontSize: 12 }}>{code.reporting_notes || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ padding: "10px 16px", color: "#8888AA", fontSize: 12 }}>
            {results.length} result{results.length !== 1 ? "s" : ""}
          </div>
        </div>
      )}

      {results.length === 0 && query && !loading && !error && (
        <div style={{ color: "#8888AA", fontSize: 13 }}>No results found for "{query}".</div>
      )}
    </div>
  )
}
