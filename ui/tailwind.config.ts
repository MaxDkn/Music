import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class', // 👈 active le mode sombre via classe
  content: [
    './src/**/*.{ts,tsx}', // adapte selon ta structure
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
export default config;
