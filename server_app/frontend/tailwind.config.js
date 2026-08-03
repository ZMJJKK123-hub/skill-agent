/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 深色极客工坊：克制的高级感
        ink: {
          950: "#0a0a0a",
          900: "#121212",
          850: "#181818",
          800: "#1e1e1e",
          700: "#2a2a2a",
        },
        forge: {
          cyan: "#22d3ee",
          emerald: "#34d399",
          amber: "#f59e0b",
          purple: "#a78bfa",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Microsoft YaHei", "sans-serif"],
        mono: ["JetBrains Mono", "Cascadia Code", "Consolas", "monospace"],
      },
      backgroundImage: {
        "grid-faint": "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.03) 1px, transparent 0)",
        "hero-glow": "radial-gradient(800px 300px at 50% -10%, rgba(34,211,238,0.08), transparent 60%)",
      },
      keyframes: {
        breathe: {
          "0%, 100%": { opacity: "0.4", transform: "scale(1)" },
          "50%": { opacity: "1", transform: "scale(1.4)" },
        },
        shine: {
          "0%": { transform: "translateX(-120%)" },
          "60%, 100%": { transform: "translateX(220%)" },
        },
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        skeleton: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
      },
      animation: {
        breathe: "breathe 1.6s ease-in-out infinite",
        shine: "shine 2.8s ease infinite",
        pulseSoft: "pulse 2s ease-in-out infinite",
        fadeUp: "fadeUp 0.3s ease",
        skeleton: "skeleton 1.5s linear infinite",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(34,211,238,0.2), 0 0 24px rgba(34,211,238,0.08)",
        "inner-deep": "inset 0 2px 8px rgba(0,0,0,0.5)",
      },
    },
  },
  plugins: [],
};