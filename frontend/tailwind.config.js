/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#E3F2FD',
          100: '#BBDEFB',
          200: '#90CAF9',
          300: '#64B5F6',
          400: '#42A5F5',
          500: '#2196F3',
          600: '#1E88E5',
          700: '#1565C0',
          800: '#0D47A1',
          900: '#0A2E6E',
        },
        success: {
          50:  '#E8F5E9',
          100: '#C8E6C9',
          500: '#4CAF50',
          600: '#43A047',
          700: '#388E3C',
        },
        accent: {
          50:  '#F3E5F5',
          100: '#E1BEE7',
          500: '#9C27B0',
          600: '#8E24AA',
          700: '#6A1B9A',
        },
      },
    },
  },
  plugins: [],
}
