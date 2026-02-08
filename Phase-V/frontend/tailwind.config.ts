import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Dark Red Outline Theme Colors
        background: {
          dark: '#0B0A0A',
          darker: '#050505',
          card: '#111010',
          hover: '#1A1919',
        },
        primary: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          DEFAULT: '#8B1E1E', // Dark red
        },
        accent: {
          red: '#B11226', // Brighter red
        },
        'dark-red': '#8B1E1E',
        'bright-red': '#B11226',
        'off-white': '#E5E7EB',
        gray: {
          850: '#1f1f1f',
          900: '#111010',
          950: '#0f0f0f',
        },
      },
      screens: {
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
      boxShadow: {
        'glow-red': '0 0 20px rgba(139, 30, 30, 0.3)',
        'glow-bright-red': '0 0 20px rgba(177, 18, 38, 0.5)',
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },
    },
  },
  plugins: [],
}

export default config
