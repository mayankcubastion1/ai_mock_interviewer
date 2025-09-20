/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f5f9ff",
          100: "#e0ecff",
          500: "#3563eb",
          600: "#274ac7"
        }
      }
    }
  },
  plugins: []
};
