/** STEP4 typed source scaffold for electron/main/ipc/projects.ts.
 * Public bodies intentionally throw until Claude Code implements the task.
 */

export type Step4ContractEntry = Readonly<{ taskId: string; symbol: string; contract: string }>;
export type Step4TestCase = Readonly<{ id: string; priority: string; layer: string; title: string; given: string; when: string; then: string; testFile: string }>;

export const STEP4_PUBLIC_CONTRACTS: readonly Step4ContractEntry[] = [
  { taskId: "TASK-UI-001", symbol: "registerProjectIpcHandlers(context)", contract: "project:list/create\u3092schema\u691c\u8a3c\u3057\u3066service\u3078\u59d4\u8b72\u3059\u308b\u3002" },
];

export const STEP4_TEST_CASES: readonly Step4TestCase[] = [
  {"id": "TC-UI-001-01", "priority": "P0", "layer": "unit", "title": "empty/loading/error", "given": "各service状態", "when": "画面表示", "then": "仕様の文言・再試行・skeletonを表示", "testFile": "`electron/tests/project_ipc.test.ts`"},
  {"id": "TC-UI-001-02", "priority": "P0", "layer": "unit", "title": "作成disabled", "given": "必須項目不足", "when": "form操作", "then": "確定button disabled", "testFile": "`electron/renderer/tests/ProjectList.test.ts`"},
  {"id": "TC-UI-001-03", "priority": "P0", "layer": "unit", "title": "keyboard", "given": "formへTab/Enter", "when": "操作", "then": "順序移動し有効時だけ作成", "testFile": "`electron/tests/project_ipc.test.ts`"},
  {"id": "TC-UI-001-04", "priority": "P1", "layer": "unit", "title": "一覧", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`registerProjectIpcHandlers(context)`を通じて「一覧」を実行する", "then": "必要項目を欠かさず安定順で返し、空一覧も正常結果として扱う。", "testFile": "`electron/renderer/tests/ProjectList.test.ts`"},
  {"id": "TC-UI-001-05", "priority": "P1", "layer": "unit", "title": "新規作成form", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`registerProjectIpcHandlers(context)`を通じて「新規作成form」を実行する", "then": "「新規作成form」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/project_ipc.test.ts`"},
  {"id": "TC-UI-001-06", "priority": "P1", "layer": "unit", "title": "必須validation", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`registerProjectIpcHandlers(context)`を通じて「必須validation」を実行する", "then": "正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。", "testFile": "`electron/renderer/tests/ProjectList.test.ts`"},
  {"id": "TC-UI-001-07", "priority": "P1", "layer": "unit", "title": "Enter/Tab", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`registerProjectIpcHandlers(context)`を通じて「Enter/Tab」を実行する", "then": "「Enter/Tab」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/project_ipc.test.ts`"},
  {"id": "TC-UI-001-08", "priority": "P0", "layer": "unit", "title": "必須入力欠落", "given": "主ID、必須path、必須設定のいずれかが欠落した入力", "when": "`registerProjectIpcHandlers(context)`を実行する", "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。", "testFile": "`electron/renderer/tests/ProjectList.test.ts`"},
  {"id": "TC-UI-001-09", "priority": "P1", "layer": "unit", "title": "再実行時の決定性", "given": "同じ入力、同じ設定、同じ依存応答", "when": "`registerProjectIpcHandlers(context)`を2回実行する", "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。", "testFile": "`electron/tests/project_ipc.test.ts`"},
];

function step4Unimplemented(symbol: string): never {
  throw new Error(`STEP4 source scaffold is not implemented: ${symbol} (electron/main/ipc/projects.ts)`);
}

export function registerProjectIpcHandlers(..._args: readonly unknown[]): unknown {
  return step4Unimplemented("registerProjectIpcHandlers");
}
