/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ledger: {
          ink: '#101B2D',      // deep navy - primary text/bg
          paper: '#F6F3EC',    // warm paper background
          rule: '#D8D2C2',     // hairline rule color
          slate: '#3C5068',    // secondary navy-blue
          gold: '#B9862F',     // approved / accent
          rust: '#9C4634',     // rejected / warning
          moss: '#4B6A52'      // approved seal
        },
      },
      fontFamily: {
        display: ['"Fraunces"', 'serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
