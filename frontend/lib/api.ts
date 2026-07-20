const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  // HS Codes
  searchHSCodes: (q: string) => request(`/api/hs-codes/search?q=${encodeURIComponent(q)}`),
  getHSCode: (cn_code: string) => request(`/api/hs-codes/${cn_code}`),

  // Calculator
  calculate: (payload: unknown) =>
    request("/api/calculator/calculate", { method: "POST", body: JSON.stringify(payload) }),
  getDefaults: (sector: string) => request(`/api/calculator/defaults/${sector}`),

  // Emission Factors
  listEmissionFactors: (params?: { category?: string; country?: string; q?: string }) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString()
    return request(`/api/emission-factors${qs ? `?${qs}` : ""}`)
  },

  // Suppliers
  createSupplier: (payload: unknown) =>
    request("/api/suppliers/", { method: "POST", body: JSON.stringify(payload) }),
  listSuppliers: () => request("/api/suppliers/"),
  getSupplier: (id: string) => request(`/api/suppliers/${id}`),
  updateSupplier: (id: string, payload: unknown) =>
    request(`/api/suppliers/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  downloadTemplate: () => `${BASE_URL}/api/suppliers/template/download`,

  // Reports
  generateReport: (payload: unknown) =>
    request("/api/reports/generate", { method: "POST", body: JSON.stringify(payload) }),
  listReports: () => request("/api/reports/"),
  getReport: (id: string) => request(`/api/reports/${id}`),
  downloadXML: (id: string) => `${BASE_URL}/api/reports/${id}/download/xml`,
  downloadPDF: (id: string) => `${BASE_URL}/api/reports/${id}/download/pdf`,
}
