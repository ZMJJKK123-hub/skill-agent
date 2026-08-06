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
        // === MC 经验条动画 ===
        xpShine: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(200%)" },
        },
        levelUpFlash: {
          "0%": { opacity: "0.8", transform: "scale(1)" },
          "100%": { opacity: "0", transform: "scale(1.05)" },
        },
        floatAway: {
          "0%": { opacity: "1", transform: "translateY(0)" },
          "100%": { opacity: "0", transform: "translateY(-16px)" },
        },
        // === MC 附魔动画 ===
        bookAppear: {
          "0%": { opacity: "0", transform: "scale(0.5) rotateY(90deg)" },
          "100%": { opacity: "1", transform: "scale(1) rotateY(0deg)" },
        },
        bookFlip: {
          "0%": { transform: "rotateY(0deg)" },
          "50%": { transform: "rotateY(90deg)" },
          "100%": { transform: "rotateY(0deg)" },
        },
        bookSpin: {
          "0%": { transform: "rotateY(0deg) scale(1)" },
          "50%": { transform: "rotateY(180deg) scale(1.05)" },
          "100%": { transform: "rotateY(360deg) scale(1)" },
        },
        enchantGlow: {
          "0%, 100%": { opacity: "0.6", filter: "brightness(1)" },
          "50%": { opacity: "1", filter: "brightness(1.5)" },
        },
        floatRune: {
          "0%": { transform: "translateY(20px) rotate(0deg)", opacity: "0" },
          "30%": { opacity: "0.8" },
          "70%": { opacity: "0.6" },
          "100%": { transform: "translateY(-40px) rotate(180deg)", opacity: "0" },
        },
        xpOrb: {
          "0%": { transform: "translateY(0) scale(0.5)", opacity: "0" },
          "30%": { opacity: "1", transform: "translateY(-10px) scale(1)" },
          "100%": { transform: "translateY(-40px) scale(0.3)", opacity: "0" },
        },
      },
      animation: {
        breathe: "breathe 1.6s ease-in-out infinite",
        shine: "shine 2.8s ease infinite",
        pulseSoft: "pulse 2s ease-in-out infinite",
        fadeUp: "fadeUp 0.3s ease",
        skeleton: "skeleton 1.5s linear infinite",
        // MC
        xpShine: "xpShine 2s ease-in-out infinite",
        levelUpFlash: "levelUpFlash 0.3s ease-out",
        floatAway: "floatAway 1.5s ease-out forwards",
        bookAppear: "bookAppear 0.6s ease-out",
        bookFlip: "bookFlip 0.8s ease-in-out",
        bookSpin: "bookSpin 1s ease-in-out",
        enchantGlow: "enchantGlow 0.5s ease-in-out infinite",
        floatRune: "floatRune 2s ease-in-out infinite",
        xpOrb: "xpOrb 1.5s ease-out infinite",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(34,211,238,0.2), 0 0 24px rgba(34,211,238,0.08)",
        "inner-deep": "inset 0 2px 8px rgba(0,0,0,0.5)",
      },
    },
  },
  plugins: [],
};