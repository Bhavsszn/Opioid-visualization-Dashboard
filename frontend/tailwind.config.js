/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html','./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        night: '#0c0f16',
        cyber: { pink:'#ff00e6', teal:'#00fff0', lime:'#c8ff00', purple:'#8a2be2' }
      },
      boxShadow: {
        neon: '0 0 10px rgba(255,0,230,0.6), 0 0 20px rgba(0,255,240,0.4)',
        neonSoft: '0 0 8px rgba(138,43,226,0.45)'
      },
      dropShadow: { glow: '0 0 0.75rem #00fff0' },
      fontFamily: {
        display: ['Orbitron','ui-sans-serif','system-ui'],
        mono: ['JetBrains Mono','ui-monospace','SFMono-Regular']
      }
    }
  },
  plugins: []
}
