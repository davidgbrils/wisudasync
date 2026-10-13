import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#F5F7F6",
          surface: "#FFFFFF",
          text: "#172321",
          secondary: "#66736F",
          accent: "#0F766E",
          "accent-hover": "#0C5F58",
          dark: "#0F4B46",
          border: "#DDE4E1",
          active: "#ECFAF8",
        },
      },
      fontFamily: {
        sans: ["var(--font-ibm-plex-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-ibm-plex-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
