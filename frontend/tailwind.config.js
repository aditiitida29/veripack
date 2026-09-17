/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        doca: {
          50: '#f0f6fc',
          100: '#e1ecf7',
          200: '#c3daf0',
          300: '#94bfe4',
          400: '#5e9ed4',
          500: '#3880c1',
          600: '#2766a5',
          700: '#1f5186',
          800: '#1c4570',
          900: '#0f2942',
          950: '#0a1a2c',
        },
        india: {
          saffron: '#FF9933',
          navy: '#000080',
          green: '#138808'
        }
      }
    },
  },
  plugins: [],
}
