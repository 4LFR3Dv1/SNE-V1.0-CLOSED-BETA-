/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'terminal-green': '#00ff00',
        'terminal-dark': '#000000',
        'terminal-gray': '#1a1a1a',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Courier New', 'monospace'],
      },
      fontVariantNumeric: {
        'tabular': 'tabular-nums',
      }
    },
  },
  plugins: [],
}

