/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#050505',
        surface: '#0A0A0C',
        primary: '#4F46E5', // Deep Indigo
        accent: '#00D6FF', // Electric Cyan
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', 'sans-serif'],
        merriweather: ['Merriweather', 'serif'],
      }
    },
  },
  plugins: [],
}

