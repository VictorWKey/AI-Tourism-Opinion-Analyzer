/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{js,ts,jsx,tsx,html}', './index.html'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '8px',
        lg: '12px',
      },
      typography: {
        DEFAULT: {
          css: {
            '--tw-prose-body': '#475569',
            '--tw-prose-headings': '#0f172a',
            lineHeight: '1.75',
            h2: {
              marginTop: '2em',
              marginBottom: '1em',
              fontSize: '1.25em',
              letterSpacing: '-0.01em',
            },
            h3: {
              marginTop: '1.6em',
              marginBottom: '0.75em',
              fontSize: '1.1em',
            },
            p: {
              marginTop: '0.85em',
              marginBottom: '0.85em',
            },
            'ul > li': {
              paddingLeft: '0.25em',
            },
            'ol > li': {
              paddingLeft: '0.25em',
            },
            hr: {
              marginTop: '2.5em',
              marginBottom: '2.5em',
            },
          },
        },
        invert: {
          css: {
            '--tw-prose-body': '#cbd5e1',
            '--tw-prose-headings': '#f1f5f9',
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
