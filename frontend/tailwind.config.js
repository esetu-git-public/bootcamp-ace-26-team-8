/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: "class",
    content: [
      "./app/**/*.{ts,tsx}",
      "./components/**/*.{ts,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          surface: {
            DEFAULT: "var(--color-surface)",
            muted: "var(--color-surface-muted)",
            inset: "var(--color-surface-inset)",
          },
          ink: {
            DEFAULT: "var(--color-ink)",
            muted: "var(--color-ink-muted)",
            faint: "var(--color-ink-faint)",
          },
          border: {
            DEFAULT: "var(--color-border)",
          },
          brand: {
            DEFAULT: "var(--color-brand)",
            hover: "var(--color-brand-hover)",
            subtle: "var(--color-brand-subtle)",
          },
          success: {
            DEFAULT: "var(--color-success)",
            subtle: "var(--color-success-subtle)",
          },
          warning: {
            DEFAULT: "var(--color-warning)",
            subtle: "var(--color-warning-subtle)",
          },
          danger: {
            DEFAULT: "var(--color-danger)",
            subtle: "var(--color-danger-subtle)",
          },
          navy: {
            DEFAULT: "var(--color-navy)",
            light: "var(--color-navy-light)",
          },
        },
        fontFamily: {
          display: ["var(--font-display)", "sans-serif"],
          sans: ["var(--font-sans)", "sans-serif"],
          mono: ["var(--font-mono)", "monospace"],
        },
        borderRadius: {
          sm: "6px",
          DEFAULT: "10px",
          lg: "14px",
          xl: "20px",
        },
        boxShadow: {
          card: "0 1px 2px rgba(16, 24, 40, 0.04), 0 1px 3px rgba(16, 24, 40, 0.06)",
          raised: "0 4px 12px rgba(16, 24, 40, 0.08)",
          overlay: "0 20px 40px rgba(16, 24, 40, 0.18)",
        },
        keyframes: {
          "fade-in": {
            "0%": { opacity: "0", transform: "translateY(4px)" },
            "100%": { opacity: "1", transform: "translateY(0)" },
          },
          "slide-in": {
            "0%": { opacity: "0", transform: "translateX(-8px)" },
            "100%": { opacity: "1", transform: "translateX(0)" },
          },
        },
        animation: {
          "fade-in": "fade-in 0.25s ease-out",
          "slide-in": "slide-in 0.2s ease-out",
        },
      },
    },
    plugins: [require("tailwindcss-animate")],
  };