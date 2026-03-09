/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary, #22c55e)',
        secondary: 'var(--color-secondary, #16a34a)',
      },
    },
  },
  plugins: [],
};
