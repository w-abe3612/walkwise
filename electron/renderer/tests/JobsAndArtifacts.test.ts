/**
 * STEP3 test scaffold for TASK-UI-004: Job進捗・cancel/retry・成果物画面.
 * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
 * Release scope: MVP.
 * The file intentionally imports no production module before STEP4.
 * Vitest test.fails is the strict-xfail equivalent: an unexpected pass fails.
 */

import { describe, test } from "vitest";

describe("TASK-UI-004 Job進捗・cancel/retry・成果物画面", () => {
  test.fails("TC-UI-004-02: retry条件 [unit/P0]", async () => {
    /**
     * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
     * Given: failed/cancelled/other
     * When: render
     * Then: 前2つだけretry可能
     * STEP7: import only approved symbols and replace this explicit error
     * with concrete arrange/act/assert logic while preserving the case ID.
     */
    throw new Error("STEP3 scaffold not implemented: TC-UI-004-02");
  });

  test.fails("TC-UI-004-04: job:get/subscribe/cancel/start retry [unit/P1]", async () => {
    /**
     * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
     * Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
     * When: `job:get/subscribe/cancel/retry handlers`を通じて「job:get/subscribe/cancel/start retry」を実行する
     * Then: 再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。
     * STEP7: import only approved symbols and replace this explicit error
     * with concrete arrange/act/assert logic while preserving the case ID.
     */
    throw new Error("STEP3 scaffold not implemented: TC-UI-004-04");
  });

  test.fails("TC-UI-004-06: stale注記 [unit/P1]", async () => {
    /**
     * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
     * Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
     * When: `job:get/subscribe/cancel/retry handlers`を通じて「stale注記」を実行する
     * Then: 「stale注記」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
     * STEP7: import only approved symbols and replace this explicit error
     * with concrete arrange/act/assert logic while preserving the case ID.
     */
    throw new Error("STEP3 scaffold not implemented: TC-UI-004-06");
  });

  test.fails("TC-UI-004-08: 必須入力欠落 [unit/P0]", async () => {
    /**
     * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
     * Given: 主ID、必須path、必須設定のいずれかが欠落した入力
     * When: `job:get/subscribe/cancel/retry handlers`を実行する
     * Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
     * STEP7: import only approved symbols and replace this explicit error
     * with concrete arrange/act/assert logic while preserving the case ID.
     */
    throw new Error("STEP3 scaffold not implemented: TC-UI-004-08");
  });

});
