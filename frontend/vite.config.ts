import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react(), {name:"connlab-development-entry",apply:"serve",transformIndexHtml(html){return html.replace('name="connlab-environment" content="release"', 'name="connlab-environment" content="development"');}}],
  test: {
    environment: "jsdom",
    globals: true,
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"]
  },
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: false }
    }
  }
});
