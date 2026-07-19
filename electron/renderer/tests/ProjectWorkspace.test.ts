/**
 * STEP3 test scaffold for TASK-UI-002: Project workspace・Source登録/レビュー・承認UI.
 * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
 * Release scope: MVP.
 * The file intentionally imports no production module before STEP4.
 * Vitest test.fails is the strict-xfail equivalent: an unexpected pass fails.
 */

import { describe, test } from "vitest";

describe("TASK-UI-002 Project workspace・Source登録/レビュー・承認UI", () => {
  test.fails("TC-UI-002-02: 差し戻し [unit/P0]", async () => {
    /**
     * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
     * Given: 理由空/あり
     * When: request changes
     * Then: 空は拒否、ありはIPC1回
     * STEP7: import only approved symbols and replace this explicit error
     * with concrete arrange/act/assert logic while preserving the case ID.
     */
    throw new Error("STEP3 scaffold not implemented: TC-UI-002-02");
  });

  test.fails("TC-UI-002-04: file dialog/drop [integration_mock/P1]", async () => {
    /**
     * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
     * Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
     * When: `source:register handlers`を通じて「file dialog/drop」を実行する
     * Then: 「file dialog/drop」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
     * STEP7: import only approved symbols and replace this explicit error
     * with concrete arrange/act/assert logic while preserving the case ID.
     */
    throw new Error("STEP3 scaffold not implemented: TC-UI-002-04");
  });

  test.fails("TC-UI-002-06: 再処理/修正/問題なし [unit/P1]", async () => {
    /**
     * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
     * Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
     * When: `source:register handlers`を通じて「再処理/修正/問題なし」を実行する
     * Then: 「再処理/修正/問題なし」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
     * STEP7: import only approved symbols and replace this explicit error
     * with concrete arrange/act/assert logic while preserving the case ID.
     */
    throw new Error("STEP3 scaffold not implemented: TC-UI-002-06");
  });

  test.fails("TC-UI-002-08: 必須入力欠落 [unit/P0]", async () => {
    /**
     * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
     * Given: 主ID、必須path、必須設定のいずれかが欠落した入力
     * When: `source:register handlers`を実行する
     * Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
     * STEP7: import only approved symbols and replace this explicit error
     * with concrete arrange/act/assert logic while preserving the case ID.
     */
    throw new Error("STEP3 scaffold not implemented: TC-UI-002-08");
  });

});
