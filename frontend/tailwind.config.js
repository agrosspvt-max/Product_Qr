/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#eef4ff',
          100: '#dbe7ff',
          200: '#b6cdff',
          300: '#8aaeff',
          400: '#5d8cff',
          500: '#3a6cf6',
          600: '#2a52d6',
          700: '#2342ab',
          800: '#1f3a8e',
          900: '#1e3578',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
