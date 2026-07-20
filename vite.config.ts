import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

/**
 * vite.config.ts — Rendererの実build設定。
 *
 * TASK-REVIEW-001監査2.3節: 以前`npm run build`は`tsc --noEmit`(型検査のみ)であり、
 * Renderer(Vue)の実HTML/JS/CSSを一切生成していなかった。`electron/renderer/index.html`を
 * 入力に、`dist/renderer/`へ実際にbundleする。`base: "./"`はpackage後、Electronが
 * `file://`経由でindex.htmlを開いても相対pathで解決できるようにするため。
 */
export default defineConfig({
  root: "electron/renderer",
  base: "./",
  plugins: [vue()],
  build: {
    outDir: "../../dist/renderer",
    emptyOutDir: true,
  },
});
