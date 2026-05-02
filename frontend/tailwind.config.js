/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./pages/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        congestion: { 혼잡: "#ef4444", 보통: "#f59e0b", 여유: "#22c55e" },
      },
    },
  },
  plugins: [],
}
