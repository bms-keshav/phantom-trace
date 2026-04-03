/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        panel: '#0e1217',
        panelSoft: '#151c24',
        neon: '#0ef3b8',
        danger: '#ff4a5e',
        amber: '#ffb454',
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        pulse: '0 0 0 1px rgba(14,243,184,0.25), 0 0 24px rgba(14,243,184,0.18)',
      },
    },
  },
  plugins: [],
}
