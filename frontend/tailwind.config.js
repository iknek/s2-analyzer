/** @type {import('tailwindcss').Config} */
export default {
  content: [ './src/**/*.{js,jsx,ts,tsx}', './index.html',
],
  theme: {
    extend: {
      colors:{
        "tno-blue": "#1A0DAB",
        "stephanie-color": "#FFFFFF",
        "components-gray": "#414245",
        "base-gray": "#2C2D31"
      }
    },
  }
}

