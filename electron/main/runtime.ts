/** STEP4 typed source scaffold for electron/main/runtime.ts.
 * Public bodies intentionally throw until Claude Code implements the task.
 */

export type Step4ContractEntry = Readonly<{ taskId: string; symbol: string; contract: string }>;
export type Step4TestCase = Readonly<{ id: string; priority: string; layer: string; title: string; given: string; when: string; then: string; testFile: string }>;

export const STEP4_PUBLIC_CONTRACTS: readonly Step4ContractEntry[] = [
  { taskId: "TASK-RELEASE-001", symbol: "resolveRuntimeDependencies()", contract: "Python/ffmpeg/Tesseract\u7b49\u306e\u5b58\u5728\u3068version\u3092\u78ba\u8a8d\u3059\u308b\u3002" },
];

export const STEP4_TEST_CASES: readonly Step4TestCase[] = [
  {"id": "TC-RELEASE-001-01", "priority": "P0", "layer": "e2e", "title": "uninstall data保持", "given": "利用者Projectがあるpackage", "when": "uninstall scenario", "then": "利用者dataを自動削除しない", "testFile": "`electron/tests/packaging_contract.test.ts`"},
  {"id": "TC-RELEASE-001-02", "priority": "P0", "layer": "integration_mock", "title": "backup restore", "given": "DB+filesをbackupし一部破損", "when": "restore", "then": "hash整合した状態へ復旧", "testFile": "`tests/test_backup_restore.py`"},
  {"id": "TC-RELEASE-001-03", "priority": "P0", "layer": "static", "title": "license manifest", "given": "package dependencies", "when": "生成", "then": "third-party licenseと同梱/非同梱を正しく列挙", "testFile": "`tests/test_license_manifest.py`"},
  {"id": "TC-RELEASE-001-04", "priority": "P1", "layer": "unit", "title": "Windows target", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`Windows packaging contract`を通じて「Windows target」を実行する", "then": "「Windows target」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/packaging_contract.test.ts`"},
  {"id": "TC-RELEASE-001-05", "priority": "P1", "layer": "unit", "title": "Python worker bundling strategy", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`Windows packaging contract`を通じて「Python worker bundling strategy」を実行する", "then": "「Python worker bundling strategy」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`tests/test_backup_restore.py`"},
  {"id": "TC-RELEASE-001-06", "priority": "P1", "layer": "unit", "title": "ffmpeg/Tesseract存在確認", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`Windows packaging contract`を通じて「ffmpeg/Tesseract存在確認」を実行する", "then": "「ffmpeg/Tesseract存在確認」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`tests/test_license_manifest.py`"},
  {"id": "TC-RELEASE-001-07", "priority": "P1", "layer": "unit", "title": "code signing未実施表示", "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態", "when": "`Windows packaging contract`を通じて「code signing未実施表示」を実行する", "then": "「code signing未実施表示」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。", "testFile": "`electron/tests/packaging_contract.test.ts`"},
  {"id": "TC-RELEASE-001-08", "priority": "P0", "layer": "unit", "title": "必須入力欠落", "given": "主ID、必須path、必須設定のいずれかが欠落した入力", "when": "`Windows packaging contract`を実行する", "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。", "testFile": "`tests/test_backup_restore.py`"},
  {"id": "TC-RELEASE-001-09", "priority": "P1", "layer": "unit", "title": "再実行時の決定性", "given": "同じ入力、同じ設定、同じ依存応答", "when": "`Windows packaging contract`を2回実行する", "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。", "testFile": "`tests/test_license_manifest.py`"},
  {"id": "TC-RELEASE-001-10", "priority": "P0", "layer": "unit", "title": "入力・既存成果物の不変性", "given": "hash取得済みの入力と既存正常成果物", "when": "正常処理または意図的な失敗を発生させる", "then": "入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。", "testFile": "`electron/tests/packaging_contract.test.ts`"},
  {"id": "TC-RELEASE-001-11", "priority": "P0", "layer": "integration_smoke", "title": "配布runtime群の疎通確認", "given": "実接続テストが明示的に有効化され、必要な設定が存在する", "when": "package内のPython、ffmpeg、ffprobe、Tesseractについてversion取得だけを順番に行う。", "then": "ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。", "testFile": "`tests/test_backup_restore.py`"},
  {"id": "TC-RELEASE-001-12", "priority": "P1", "layer": "integration_live", "title": "配布runtime群の実機能テスト", "given": "`release_runtime_connectivity_gate`が成功済み", "when": "全runtime疎通成功後、最小backup/restore・最小worker起動・最小media probeを実行する。", "then": "最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。", "testFile": "`tests/test_license_manifest.py`"},
];

function step4Unimplemented(symbol: string): never {
  throw new Error(`STEP4 source scaffold is not implemented: ${symbol} (electron/main/runtime.ts)`);
}

export async function resolveRuntimeDependencies(..._args: readonly unknown[]): Promise<unknown> {
  return step4Unimplemented("resolveRuntimeDependencies");
}
