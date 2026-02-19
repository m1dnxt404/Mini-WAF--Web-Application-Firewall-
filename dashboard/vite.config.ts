import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      "/api": {
        target: "http://waf:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://waf:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
