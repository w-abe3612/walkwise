/** STEP4 typed source scaffold for electron/renderer/main.ts.
 * Public bodies intentionally throw until Claude Code implements the task.
 */

export type Step4ContractEntry = Readonly<{ taskId: string; symbol: string; contract: string }>;
export type Step4TestCase = Readonly<{ id: string; priority: string; layer: string; title: string; given: string; when: string; then: string; testFile: string }>;

export const STEP4_PUBLIC_CONTRACTS: readonly Step4ContractEntry[] = [
  { taskId: "TASK-DESKTOP-001", symbol: "renderer bootstrap", contract: "Node API\u3078\u76f4\u63a5\u30a2\u30af\u30bb\u30b9\u305b\u305aVue\u3092\u8d77\u52d5\u3059\u308b\u3002" },
];

export const STEP4_TEST_CASES: readonly Step4TestCase[] = [
  {"id": "TC-DESKTOP-001-01", "priority": "P0", "layer": "static", "title": "webPreferences", "given": "main window作成", "when": "設定を検査", "then": "nodeIntegration=false, contextIsolation=true, sandbox方針を満たす", "testFile": "`electron/tests/main_security.test.ts`"},
  {"id": "TC-DESKTOP-001-02", "priority": "P0", "layer": "unit", "title": "preload allowlist", "given": "未許可channelを呼ぶ", "when": "API", "then": "rendererから送信できない", "testFile": "`electron/tests/preload_contract.test.ts`"},
  {"id": "TC-DESKTOP-001-03", "priority": "P0", "layer": "static", "title": "renderer isolation", "given": "renderer bundle", "when": "static scan", "then": "fs/child_process/sqliteを直接importしない", "testFile": "`electron/tests/main_security.test.ts`"},
  {"id": "TC-DESKTOP-001-04", "priority": "P1", "layer": "unit", "title": "package scripts", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`createMainWindow(): BrowserWindow`を通じて「package scripts」を実行する", "then": "「package scripts」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/preload_contract.test.ts`"},
  {"id": "TC-DESKTOP-001-05", "priority": "P1", "layer": "unit", "title": "contextBridge", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`createMainWindow(): BrowserWindow`を通じて「contextBridge」を実行する", "then": "「contextBridge」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/main_security.test.ts`"},
  {"id": "TC-DESKTOP-001-06", "priority": "P1", "layer": "integration_mock", "title": "typed IPC contract", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`createMainWindow(): BrowserWindow`を通じて「typed IPC contract」を実行する", "then": "「typed IPC contract」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/preload_contract.test.ts`"},
  {"id": "TC-DESKTOP-001-07", "priority": "P1", "layer": "integration_mock", "title": "任意IPC/FS/child_process非公開", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`createMainWindow(): BrowserWindow`を通じて「任意IPC/FS/child_process非公開」を実行する", "then": "「任意IPC/FS/child_process非公開」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/main_security.test.ts`"},
  {"id": "TC-DESKTOP-001-08", "priority": "P0", "layer": "unit", "title": "必須入力欠落", "given": "主ID、必須path、必須設定のいずれかが欠落した入力", "when": "`createMainWindow(): BrowserWindow`を実行する", "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。", "testFile": "`electron/tests/preload_contract.test.ts`"},
  {"id": "TC-DESKTOP-001-09", "priority": "P1", "layer": "unit", "title": "再実行時の決定性", "given": "同じ入力、同じ設定、同じ依存応答", "when": "`createMainWindow(): BrowserWindow`を2回実行する", "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。", "testFile": "`electron/tests/main_security.test.ts`"},
];

function step4Unimplemented(symbol: string): never {
  throw new Error(`STEP4 source scaffold is not implemented: ${symbol} (electron/renderer/main.ts)`);
}

export function main(..._args: readonly unknown[]): unknown {
  return step4Unimplemented("main");
}
