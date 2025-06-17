/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        courseraBlue: '#004E92', // Coursera's blue color
        courseraBlueDark: '#003C7F', // A slightly darker shade for contrast
        customblue: '#0071BC',
        custom: '0 0 10px rgba(0, 0, 0, 0.1)',
        wawablue:'#daf0ff',
      },

    },
  },
  plugins: [],
}

