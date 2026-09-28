/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#2ab5a0",
          ink: "#5eead4",
          dark: "#0f172a",
          card: "#0b1422",
        },
      },
    },
  },
  plugins: [],
};
