/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0A0A0A",
        surface: "#0E1013",
        "surface-low": "#0E1013",
        "surface-mid": "#15171C",
        "surface-high": "#1B1D22",
        "on-surface": "#EDEDED",
        "on-surface-muted": "#8E929B",
        "on-surface-dim": "#545761",
        outline: "#22242A",
        "outline-active": "#EDEDED",
        primary: "#FF4400",
        trustworthy: "#4ADE80",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Geist'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      borderRadius: {
        none: "0px",
      },
    },
  },
  plugins: [],
};
