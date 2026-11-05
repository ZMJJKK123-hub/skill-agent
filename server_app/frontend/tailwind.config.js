/** @type {import('tailwindcss').Config} */
export default {
  content: ['./site/**/*.{html,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0b0e14',
          900: '#11141c',
          800: '#1a1f2b',
          700: '#242b3a',
          600: '#2f384a',
        },
        forge: {
          300: '#b6edd0',
          400: '#a1e5bf',
          500: '#87d9ab',
          600: '#4bb982',
        },
      },
    },
  },
  plugins: [],
}
