// scripts/finalize-dist.mjs — `npm run build`の最終step。
//
// TASK-REVIEW-001: package.jsonは"type":"module"だが、electron/main・electron/preloadは
// tsconfig.main.jsonでCommonJS(module/moduleResolution: Node、拡張子なし相対import)へ
// compileしている。Nodeは最も近いpackage.jsonの"type"でdist/main/*.js等の解釈を決めるため、
// dist/main/package.jsonとdist/preload/package.jsonへ{"type":"commonjs"}を書き込み、
// root package.jsonの"type":"module"に関わらずCommonJSとして実行されるようにする。
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");

for (const dir of ["dist/main", "dist/preload"]) {
  const fullDir = path.join(REPO_ROOT, dir);
  mkdirSync(fullDir, { recursive: true });
  writeFileSync(path.join(fullDir, "package.json"), `${JSON.stringify({ type: "commonjs" }, null, 2)}\n`);
}

console.log("[finalize-dist] wrote dist/main/package.json and dist/preload/package.json ({\"type\":\"commonjs\"})");
