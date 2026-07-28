import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172026",
        slate: "#46545f",
        paper: "#f7f5ef",
        ember: "#bc4f2a",
        moss: "#4d6f5c"
      }
    }
  },
  plugins: []
};

export default config;
