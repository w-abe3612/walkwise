/** STEP4 typed source scaffold for electron/main/database.ts.
 * Public bodies intentionally throw until Claude Code implements the task.
 */

export type Step4ContractEntry = Readonly<{ taskId: string; symbol: string; contract: string }>;
export type Step4TestCase = Readonly<{ id: string; priority: string; layer: string; title: string; given: string; when: string; then: string; testFile: string }>;

export const STEP4_PUBLIC_CONTRACTS: readonly Step4ContractEntry[] = [
  { taskId: "TASK-DESKTOP-002", symbol: "openApplicationDatabase(path)", contract: "renderer\u3078\u63a5\u7d9a\u3092\u6e21\u3055\u305amain\u5185\u306b\u4fdd\u6301\u3059\u308b\u3002" },
];

export const STEP4_TEST_CASES: readonly Step4TestCase[] = [
  {"id": "TC-DESKTOP-002-01", "priority": "P0", "layer": "integration_mock", "title": "bootstrap順", "given": "初回起動", "when": "bootstrap", "then": "data root→backup/migration→DB→worker healthの順", "testFile": "`electron/tests/bootstrap.test.ts`"},
  {"id": "TC-DESKTOP-002-02", "priority": "P0", "layer": "integration_mock", "title": "migration失敗", "given": "DB migration error", "when": "bootstrap", "then": "windowへ安全なerrorを返しworkerを開始しない", "testFile": "`electron/tests/worker_manager.test.ts`"},
  {"id": "TC-DESKTOP-002-03", "priority": "P0", "layer": "integration_mock", "title": "worker疎通失敗", "given": "ping失敗", "when": "bootstrap", "then": "再試行/診断可能な起動errorにする", "testFile": "`electron/tests/bootstrap.test.ts`"},
  {"id": "TC-DESKTOP-002-04", "priority": "P1", "layer": "unit", "title": "appData配下root", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`bootstrapApplication(): Promise<AppContext>`を通じて「appData配下root」を実行する", "then": "「appData配下root」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/worker_manager.test.ts`"},
  {"id": "TC-DESKTOP-002-05", "priority": "P1", "layer": "unit", "title": "stale recovery", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`bootstrapApplication(): Promise<AppContext>`を通じて「stale recovery」を実行する", "then": "「stale recovery」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/bootstrap.test.ts`"},
  {"id": "TC-DESKTOP-002-06", "priority": "P1", "layer": "unit", "title": "Python executable解決", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`bootstrapApplication(): Promise<AppContext>`を通じて「Python executable解決」を実行する", "then": "「Python executable解決」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/worker_manager.test.ts`"},
  {"id": "TC-DESKTOP-002-07", "priority": "P1", "layer": "unit", "title": "shutdown cleanup", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`bootstrapApplication(): Promise<AppContext>`を通じて「shutdown cleanup」を実行する", "then": "「shutdown cleanup」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/bootstrap.test.ts`"},
  {"id": "TC-DESKTOP-002-08", "priority": "P0", "layer": "unit", "title": "必須入力欠落", "given": "主ID、必須path、必須設定のいずれかが欠落した入力", "when": "`bootstrapApplication(): Promise<AppContext>`を実行する", "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。", "testFile": "`electron/tests/worker_manager.test.ts`"},
  {"id": "TC-DESKTOP-002-09", "priority": "P1", "layer": "unit", "title": "再実行時の決定性", "given": "同じ入力、同じ設定、同じ依存応答", "when": "`bootstrapApplication(): Promise<AppContext>`を2回実行する", "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。", "testFile": "`electron/tests/bootstrap.test.ts`"},
  {"id": "TC-DESKTOP-002-10", "priority": "P0", "layer": "unit", "title": "入力・既存成果物の不変性", "given": "hash取得済みの入力と既存正常成果物", "when": "正常処理または意図的な失敗を発生させる", "then": "入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。", "testFile": "`electron/tests/worker_manager.test.ts`"},
  {"id": "TC-DESKTOP-002-11", "priority": "P0", "layer": "integration_smoke", "title": "Python worker subprocessの疎通確認", "given": "実接続テストが明示的に有効化され、必要な設定が存在する", "when": "workerを起動してhealth/ping requestだけを送り、JSON Linesの正常応答と終了を確認する。", "then": "ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。", "testFile": "`electron/tests/bootstrap.test.ts`"},
  {"id": "TC-DESKTOP-002-12", "priority": "P1", "layer": "integration_live", "title": "Python worker subprocessの実機能テスト", "given": "`worker_connectivity_gate`が成功済み", "when": "疎通成功後、固定の副作用のないcommandをdispatchしてprogress/result順を確認する。", "then": "最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。", "testFile": "`electron/tests/worker_manager.test.ts`"},
];

function step4Unimplemented(symbol: string): never {
  throw new Error(`STEP4 source scaffold is not implemented: ${symbol} (electron/main/database.ts)`);
}

export async function openApplicationDatabase(..._args: readonly unknown[]): Promise<unknown> {
  return step4Unimplemented("openApplicationDatabase");
}
