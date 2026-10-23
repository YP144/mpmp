/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        pantone: {
          red: '#D01025',
          darkred: '#9E0A1B',
          lightred: '#FFF0F2',
          softred: '#FDE2E4',
          redborder: '#F8B4B9',
        },
      },
    },
  },
  plugins: [],
};