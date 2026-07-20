export default function Dashboard() {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: "#E8E8F0", margin: 0 }}>Dashboard</h1>
        <p style={{ color: "#8888AA", fontSize: 13, marginTop: 4 }}>
          EU CBAM compliance overview
        </p>
      </div>

      {/* KPI row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
        {[
          { label: "Total Shipments (Q)", value: "—", sub: "This quarter" },
          { label: "Embedded Emissions", value: "—", sub: "tCO₂e" },
          { label: "Est. CBAM Cost", value: "—", sub: "@ €75.36/tCO₂e" },
          { label: "Pending Validations", value: "—", sub: "Score < 80" },
        ].map((k) => (
          <div key={k.label} className="panel" style={{ padding: 16 }}>
            <div style={{ color: "#8888AA", fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              {k.label}
            </div>
            <div style={{ color: "#E8E8F0", fontSize: 26, fontWeight: 700, margin: "8px 0 4px" }}>
              {k.value}
            </div>
            <div style={{ color: "#8888AA", fontSize: 12 }}>{k.sub}</div>
          </div>
        ))}
      </div>

      {/* Quick links */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 24 }}>
        {[
          { href: "/hs-checker", label: "HS Code Checker", desc: "Check CBAM applicability for a CN code" },
          { href: "/calculator", label: "New Calculation", desc: "Calculate embedded emissions for a shipment" },
          { href: "/reports", label: "Generate Report", desc: "Create XML + PDF report for a period" },
        ].map((q) => (
          <a
            key={q.href}
            href={q.href}
            style={{
              background: "#111118",
              border: "1px solid #1E1E2E",
              padding: "14px 16px",
              display: "block",
              textDecoration: "none",
              transition: "border-color 0.15s",
            }}
            onMouseOver={(e) => (e.currentTarget.style.borderColor = "#0066CC")}
            onMouseOut={(e) => (e.currentTarget.style.borderColor = "#1E1E2E")}
          >
            <div style={{ color: "#0066CC", fontSize: 13, fontWeight: 600, marginBottom: 4 }}>
              {q.label} →
            </div>
            <div style={{ color: "#8888AA", fontSize: 12 }}>{q.desc}</div>
          </a>
        ))}
      </div>

      {/* Reports summary */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div className="panel">
          <div style={{ color: "#8888AA", fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 12 }}>
            Reports
          </div>
          <div style={{ display: "flex", gap: 24 }}>
            {["Draft", "Validated", "Submitted"].map((s) => (
              <div key={s}>
                <div style={{ color: "#E8E8F0", fontSize: 22, fontWeight: 700 }}>0</div>
                <div style={{ color: "#8888AA", fontSize: 12 }}>{s}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel">
          <div style={{ color: "#8888AA", fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 12 }}>
            Getting Started
          </div>
          <ol style={{ color: "#8888AA", fontSize: 13, paddingLeft: 18, margin: 0, lineHeight: 2 }}>
            <li>Check your HS codes in <a href="/hs-checker" style={{ color: "#0066CC" }}>HS Code Checker</a></li>
            <li>Add suppliers in <a href="/suppliers" style={{ color: "#0066CC" }}>Suppliers</a></li>
            <li>Calculate emissions in <a href="/calculator" style={{ color: "#0066CC" }}>Emission Calculator</a></li>
            <li>Generate report in <a href="/reports" style={{ color: "#0066CC" }}>Reports</a></li>
          </ol>
        </div>
      </div>
    </div>
  )
}
