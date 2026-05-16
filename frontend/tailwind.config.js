/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'financial-green': '#10B981',
        'financial-red': '#EF4444',
        'dark-bg': '#0B0E11',
        'dark-card': '#1E2329',
      },
      backgroundImage: {
        'radial-gradient': 'radial-gradient(circle at top right, #1e1b4b, #0B0E11)',
      },
      animation: {
        'scroll-text': 'scroll-text 30s linear infinite',
      },
      keyframes: {
        'scroll-text': {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(-100%)' },
        }
      }
    },
  },
  plugins: [],
}
