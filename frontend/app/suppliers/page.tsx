"use client"
import { useState, useEffect } from "react"
import type { Supplier, APIResponse } from "@/lib/types"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: "", country_code: "", factory_name: "", contact_email: "", installation_id: "", notes: "" })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    const res: APIResponse<Supplier[]> = await fetch(`${API}/api/suppliers/`).then(r => r.json())
    setSuppliers(res.data || [])
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const save = async () => {
    setSaving(true)
    setError(null)
    try {
      const res: APIResponse<Supplier> = await fetch(`${API}/api/suppliers/`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form)
      }).then(r => r.json())
      if (res.error) throw new Error(res.error.message)
      setShowForm(false)
      setForm({ name: "", country_code: "", factory_name: "", contact_email: "", installation_id: "", notes: "" })
      load()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Suppliers</h1>
          <p style={{ color: "#8888AA", fontSize: 13, marginTop: 4 }}>Manage supplier data for CBAM reporting</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <a href={`${API}/api/suppliers/template/download`} className="btn-secondary" style={{ textDecoration: "none", padding: "8px 16px", fontSize: "0.875rem" }}>
            Download Template
          </a>
          <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "+ Add Supplier"}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="panel" style={{ marginBottom: 24, maxWidth: 600 }}>
          <div style={{ color: "#8888AA", fontSize: 12, fontWeight: 600, textTransform: "uppercase", marginBottom: 16 }}>New Supplier</div>
          {[
            { k: "name", label: "Supplier Name *" },
            { k: "country_code", label: "Country Code (ISO 3-letter) *", placeholder: "e.g. ARE" },
            { k: "factory_name", label: "Factory Name" },
            { k: "contact_email", label: "Contact Email" },
            { k: "installation_id", label: "EU Installation ID (if known)" },
            { k: "notes", label: "Notes" },
          ].map(({ k, label, placeholder }) => (
            <div key={k} style={{ marginBottom: 12 }}>
              <label style={{ display: "block", color: "#8888AA", fontSize: 12, marginBottom: 4 }}>{label}</label>
              <input
                type="text" placeholder={placeholder}
                value={(form as Record<string, string>)[k]}
                onChange={(e) => setForm(f => ({ ...f, [k]: e.target.value }))}
              />
            </div>
          ))}
          {error && <div style={{ color: "#FF4444", fontSize: 13, marginBottom: 12 }}>{error}</div>}
          <button className="btn-primary" onClick={save} disabled={saving}>{saving ? "Saving..." : "Save Supplier"}</button>
        </div>
      )}

      <div className="panel" style={{ padding: 0 }}>
        {loading ? <div style={{ padding: 24, color: "#8888AA" }}>Loading...</div> : (
          <table>
            <thead>
              <tr><th>Name</th><th>Country</th><th>Factory</th><th>Installation ID</th><th>CBAM Data</th><th>Contact</th></tr>
            </thead>
            <tbody>
              {suppliers.length === 0 ? (
                <tr><td colSpan={6} style={{ color: "#8888AA", textAlign: "center", padding: 24 }}>No suppliers yet. Add one above.</td></tr>
              ) : suppliers.map((s) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 600 }}>{s.name}</td>
                  <td style={{ fontFamily: "monospace", color: "#0066CC" }}>{s.country_code}</td>
                  <td style={{ color: "#8888AA" }}>{s.factory_name || "—"}</td>
                  <td style={{ fontFamily: "monospace", fontSize: 12 }}>{s.installation_id || "—"}</td>
                  <td>{s.cbam_data_available ? <span className="badge-success">YES</span> : <span className="badge-warning">NO</span>}</td>
                  <td style={{ color: "#8888AA", fontSize: 12 }}>{s.contact_email || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
