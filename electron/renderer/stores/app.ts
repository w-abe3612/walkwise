/** STEP4 typed source scaffold for electron/renderer/stores/app.ts.
 * Public bodies intentionally throw until Claude Code implements the task.
 */

export type Step4ContractEntry = Readonly<{ taskId: string; symbol: string; contract: string }>;
export type Step4TestCase = Readonly<{ id: string; priority: string; layer: string; title: string; given: string; when: string; then: string; testFile: string }>;

export const STEP4_PUBLIC_CONTRACTS: readonly Step4ContractEntry[] = [
  { taskId: "TASK-UI-005", symbol: "global UI state", contract: "loading/error/current project\u3092\u4e00\u5143\u7ba1\u7406\u3059\u308b\u3002" },
];

export const STEP4_TEST_CASES: readonly Step4TestCase[] = [
  {"id": "TC-UI-005-01", "priority": "P0", "layer": "unit", "title": "5画面navigation", "given": "Project文脈あり/なし", "when": "遷移", "then": "無効routeを安全な既定画面へ戻す", "testFile": "`electron/renderer/tests/navigation.test.ts`"},
  {"id": "TC-UI-005-02", "priority": "P0", "layer": "unit", "title": "focus/error summary", "given": "validation error", "when": "render", "then": "error summaryへfocus移動しariaで関連付け", "testFile": "`electron/renderer/tests/accessibility.test.ts`"},
  {"id": "TC-UI-005-03", "priority": "P0", "layer": "unit", "title": "keyboard only", "given": "mouseなし", "when": "主要操作", "then": "全操作に到達可能", "testFile": "`electron/renderer/tests/navigation.test.ts`"},
  {"id": "TC-UI-005-04", "priority": "P1", "layer": "unit", "title": "Project context", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`navigation state`を通じて「Project context」を実行する", "then": "「Project context」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/renderer/tests/accessibility.test.ts`"},
  {"id": "TC-UI-005-05", "priority": "P1", "layer": "integration_mock", "title": "typed API wrapper", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`navigation state`を通じて「typed API wrapper」を実行する", "then": "「typed API wrapper」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/renderer/tests/navigation.test.ts`"},
  {"id": "TC-UI-005-06", "priority": "P1", "layer": "unit", "title": "loading skeleton", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`navigation state`を通じて「loading skeleton」を実行する", "then": "「loading skeleton」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/renderer/tests/accessibility.test.ts`"},
  {"id": "TC-UI-005-07", "priority": "P1", "layer": "unit", "title": "日本語利用者message/technical detail分離", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`navigation state`を通じて「日本語利用者message/technical detail分離」を実行する", "then": "「日本語利用者message/technical detail分離」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/renderer/tests/navigation.test.ts`"},
  {"id": "TC-UI-005-08", "priority": "P0", "layer": "unit", "title": "必須入力欠落", "given": "主ID、必須path、必須設定のいずれかが欠落した入力", "when": "`navigation state`を実行する", "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。", "testFile": "`electron/renderer/tests/accessibility.test.ts`"},
  {"id": "TC-UI-005-09", "priority": "P1", "layer": "unit", "title": "再実行時の決定性", "given": "同じ入力、同じ設定、同じ依存応答", "when": "`navigation state`を2回実行する", "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。", "testFile": "`electron/renderer/tests/navigation.test.ts`"},
];

function step4Unimplemented(symbol: string): never {
  throw new Error(`STEP4 source scaffold is not implemented: ${symbol} (electron/renderer/stores/app.ts)`);
}

export function app(..._args: readonly unknown[]): unknown {
  return step4Unimplemented("app");
}
