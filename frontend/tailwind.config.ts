import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0A0A0F",
        surface: "#111118",
        border: "#1E1E2E",
        primary: "#0066CC",
        "text-primary": "#E8E8F0",
        "text-secondary": "#8888AA",
        success: "#00C851",
        warning: "#FFB300",
        error: "#FF4444",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
}

export default config
