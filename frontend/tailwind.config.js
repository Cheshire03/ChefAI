/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        orange: '#FF5C00',
        orangePale: '#FFF0E8',
        ink: '#1C1917',
        cream: '#FDFCFA',
        green: '#22C55E',
        amber: '#F59E0B',
        red: '#EF4444',
      },
      fontFamily: {
        sora: ['Sora', 'sans-serif'],
        jakarta: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
