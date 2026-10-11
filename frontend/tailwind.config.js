/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          950: '#0c1a13',
          900: '#13271e',
          800: '#1b382b', // Deep forest green
          700: '#264e3c',
          600: '#346b52',
          500: '#468e6d',
        },
        sage: {
          200: '#dce6df',
          300: '#bccfc2',
          400: '#8ea893', // Muted sage
          500: '#6f8d75',
          600: '#546f59',
        },
        cream: {
          50: '#fdfcf9',
          100: '#fbf8f1', // Warm cream background
          200: '#f4ede0',
          300: '#e8dcce',
          400: '#dac7b2',
        },
        amber: {
          400: '#f09652',
          500: '#d97736', // Restrained amber accent
          600: '#b85e25',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Lora', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
}

