"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"

const NAV = [
  { href: "/", label: "Dashboard", icon: "⬛" },
  { href: "/hs-checker", label: "HS Code Checker", icon: "🔍" },
  { href: "/calculator", label: "Emission Calculator", icon: "⚡" },
  { href: "/emission-factors", label: "Emission Factors", icon: "📊" },
  { href: "/suppliers", label: "Suppliers", icon: "🏭" },
  { href: "/validate", label: "Validation", icon: "✅" },
  { href: "/reports", label: "Reports", icon: "📄" },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside
      style={{
        width: 220,
        minHeight: "100vh",
        background: "#111118",
        borderRight: "1px solid #1E1E2E",
        display: "flex",
        flexDirection: "column",
        position: "fixed",
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 100,
      }}
    >
      {/* Logo */}
      <div style={{ padding: "20px 16px 16px", borderBottom: "1px solid #1E1E2E" }}>
        <div style={{ color: "#0066CC", fontWeight: 700, fontSize: 15, letterSpacing: "0.02em" }}>
          CBAM Assistant
        </div>
        <div style={{ color: "#8888AA", fontSize: 11, marginTop: 2 }}>
          EU Compliance Tool
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "8px 0" }}>
        {NAV.map((item) => {
          const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "9px 16px",
                fontSize: 13,
                color: active ? "#E8E8F0" : "#8888AA",
                background: active ? "rgba(0,102,204,0.12)" : "transparent",
                borderLeft: active ? "2px solid #0066CC" : "2px solid transparent",
                textDecoration: "none",
                fontWeight: active ? 600 : 400,
                transition: "all 0.1s",
              }}
            >
              <span style={{ fontSize: 14 }}>{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{ padding: "12px 16px", borderTop: "1px solid #1E1E2E", fontSize: 11, color: "#8888AA" }}>
        <div>MIT License</div>
        <a
          href="https://github.com/nvaradha22/cbam-assistant"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "#0066CC", textDecoration: "none" }}
        >
          github.com/nvaradha22/cbam-assistant
        </a>
      </div>
    </aside>
  )
}
