import type { Metadata } from "next"
import "./globals.css"
import Sidebar from "@/components/layout/Sidebar"

export const metadata: Metadata = {
  title: "CBAM Assistant",
  description: "Open-source EU CBAM compliance tool for GCC exporters",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: "#0A0A0F", color: "#E8E8F0" }}>
        <Sidebar />
        <main style={{ marginLeft: 220, minHeight: "100vh", padding: "24px 32px" }}>
          {children}
        </main>
      </body>
    </html>
  )
}
