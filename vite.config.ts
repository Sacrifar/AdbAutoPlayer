import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import devtoolsJson from "vite-plugin-devtools-json";

export default defineConfig({
  plugins: [tailwindcss(), sveltekit(), devtoolsJson()],
  optimizeDeps: {
    exclude: ["@skeletonlabs/skeleton-svelte", "@skeletonlabs/skeleton"],
  },

  // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
  //
  // 1. prevent vite from obscuring rust errors
  clearScreen: false,
  // 2. tauri expects a fixed port, fail if that port is not available
  server: {
    host: "127.0.0.1",
    port: 1420,
    strictPort: true,
    watch: {
      // 3. tell vite to ignore watching `src-tauri`
      ignored: [
        "**/src-tauri/**",
        "**/.venv/**",
        "**/data/**",
        "**/debug/**",
        "**/ocr_debug.txt",
        "**/full_hero_report.txt",
        "**/hero_audit_report.txt",
      ],
    },
  },
});
