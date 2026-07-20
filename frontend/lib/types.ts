export interface HSCode {
  id: string
  cn_code: string
  description: string
  sector: string
  cbam_applicable: boolean
  reporting_notes: string | null
  created_at: string
}

export interface EmissionFactor {
  id: string
  category: string
  name: string
  country_code: string | null
  factor_value: number
  unit: string
  source: string | null
  valid_from: string | null
  valid_to: string | null
}

export interface Supplier {
  id: string
  name: string
  country_code: string
  factory_name: string | null
  contact_email: string | null
  installation_id: string | null
  cbam_data_available: boolean
  notes: string | null
  created_at: string
  updated_at: string
}

export interface CalculationResult {
  sector: string
  direct_emissions: number
  indirect_emissions: number
  embedded_emissions: number
  emission_intensity: number
  calculation_method: string
  calculation_log: Record<string, unknown>
}

export interface ValidationIssue {
  rule_id: string
  severity: "ERROR" | "WARNING" | "INFO"
  message: string
  field: string | null
}

export interface ValidationResult {
  score: number
  issues: ValidationIssue[]
  shipment_id: string | null
  period: string | null
}

export interface Report {
  id: string
  reporting_period: string
  status: string
  xml_path: string | null
  pdf_path: string | null
  validation_score: number | null
  validation_issues: unknown | null
  submitted_at: string | null
  created_at: string
  updated_at: string
}

export interface APIResponse<T> {
  data: T | null
  error: { code: string; message: string } | null
}
