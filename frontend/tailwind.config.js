/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'western-deep': '#4A148C',
        'western-purple': '#7B1FA2',
      },
    },
  },
  plugins: [],
} 