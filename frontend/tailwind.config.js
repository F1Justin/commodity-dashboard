/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 深色主题色板
        dark: {
          bg: '#0f1419',
          card: '#1a1f2e',
          border: '#2a3441',
          hover: '#242d3a',
        },
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        accent: {
          gold: '#f59e0b',
          copper: '#ea580c',
          silver: '#94a3b8',
        },
      },
    },
  },
  plugins: [],
};
