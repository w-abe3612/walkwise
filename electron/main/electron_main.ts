/**
 * electron/main/electron_main.ts — 実Electronプロセスの唯一の起動entrypoint。
 *
 * `package.json`の`main`は、tscでcompileされた`dist/main/electron_main.js`を指す
 * (electron-builder.ymlの`files`にも`dist/**`が含まれる)。このfile自体は
 * `app_entry.ts`の`main()`を呼び出すだけで、ロジックは一切持たない
 * (副作用のないapp_entry.tsをtest importできるようにするための分離)。
 */
import { main } from "./app_entry";

void main();
