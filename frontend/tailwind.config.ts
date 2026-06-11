import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Material You (Material Design 3) light tonal palette.
        surface: {
          DEFAULT: "#FFFBFE",
          container: "#F3EDF7",
          "container-low": "#E7E0EC",
        },
        "on-surface": "#1C1B1F",
        "on-surface-variant": "#49454F",
        primary: {
          DEFAULT: "#6750A4",
          container: "#EADDFF",
        },
        "on-primary": "#FFFFFF",
        "on-primary-container": "#21005D",
        secondary: {
          DEFAULT: "#625B71",
          container: "#E8DEF8",
        },
        "on-secondary-container": "#1D192B",
        tertiary: {
          DEFAULT: "#7D5260",
          container: "#FFD8E4",
        },
        "on-tertiary-container": "#31111D",
        outline: "#79747E",
        "outline-variant": "#CAC4D0",
        error: {
          DEFAULT: "#B3261E",
          container: "#F9DEDC",
        },
        "on-error-container": "#410E0B",
      },
      fontFamily: {
        sans: ["var(--font-roboto)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-lg": ["3.5rem", { lineHeight: "1.12", fontWeight: "500" }],
        "display-md": ["2.8rem", { lineHeight: "1.15", fontWeight: "500" }],
        "headline-md": ["2rem", { lineHeight: "1.25", fontWeight: "500" }],
        "headline-sm": ["1.75rem", { lineHeight: "1.28", fontWeight: "500" }],
        "title-lg": ["1.5rem", { lineHeight: "1.3", fontWeight: "500" }],
        "title-md": ["1.125rem", { lineHeight: "1.4", fontWeight: "500" }],
        "body-lg": ["1.25rem", { lineHeight: "1.6", fontWeight: "400" }],
        "body-md": ["1rem", { lineHeight: "1.6", fontWeight: "400" }],
        "body-sm": ["0.875rem", { lineHeight: "1.55", fontWeight: "400" }],
        "label-lg": [
          "0.9375rem",
          { lineHeight: "1.4", letterSpacing: "0.01em", fontWeight: "500" },
        ],
        "label-md": [
          "0.875rem",
          { lineHeight: "1.4", letterSpacing: "0.02em", fontWeight: "500" },
        ],
      },
      borderRadius: {
        "md-xs": "8px",
        "md-sm": "12px",
        "md-md": "16px",
        "md-lg": "24px",
        "md-xl": "32px",
        "md-2xl": "48px",
      },
      boxShadow: {
        "md-1": "0 1px 2px rgba(28,27,31,0.10), 0 1px 3px rgba(28,27,31,0.06)",
        "md-2": "0 1px 2px rgba(28,27,31,0.10), 0 2px 6px rgba(28,27,31,0.10)",
        "md-3": "0 4px 8px rgba(28,27,31,0.10), 0 8px 24px rgba(28,27,31,0.12)",
        "md-4": "0 8px 16px rgba(28,27,31,0.12), 0 16px 40px rgba(28,27,31,0.16)",
      },
      transitionTimingFunction: {
        emphasized: "cubic-bezier(0.2, 0, 0, 1)",
        "emphasized-decel": "cubic-bezier(0.05, 0.7, 0.1, 1)",
      },
      maxWidth: {
        content: "75rem",
      },
      keyframes: {
        "fade-in-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "blob-float": {
          "0%, 100%": { transform: "translate(0px, 0px) scale(1)" },
          "33%": { transform: "translate(20px, -28px) scale(1.06)" },
          "66%": { transform: "translate(-18px, 16px) scale(0.96)" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "0.6" },
        },
        "result-pop": {
          from: { opacity: "0", transform: "scale(0.96)" },
          to: { opacity: "1", transform: "scale(1)" },
        },
        "badge-pop": {
          "0%": { transform: "scale(0.94)" },
          "55%": { transform: "scale(1.04)" },
          "100%": { transform: "scale(1)" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.6s cubic-bezier(0.05,0.7,0.1,1) both",
        "blob-float": "blob-float 16s ease-in-out infinite",
        "pulse-soft": "pulse-soft 6s ease-in-out infinite",
        "result-pop": "result-pop 0.28s cubic-bezier(0.05,0.7,0.1,1) both",
        "badge-pop": "badge-pop 0.32s cubic-bezier(0.2,0,0,1) both",
      },
    },
  },
  plugins: [],
};

export default config;
