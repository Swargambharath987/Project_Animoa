import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Animoa brand colors (from v7)
        primary: {
          DEFAULT: '#4E9BB9',
          dark: '#3A7A94',
          light: '#6BB5D1',
        },
        secondary: {
          DEFAULT: '#31505E',
          light: '#4A6B7A',
        },
        accent: {
          success: '#4CAF50',
          warning: '#FFC107',
          error: '#F44336',
          info: '#4E9BB9',
        },
        // Mood colors
        mood: {
          'very-happy': '#28a745',
          'happy': '#8bc34a',
          'neutral': '#ffc107',
          'sad': '#fd7e14',
          'very-sad': '#dc3545',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

export default config
