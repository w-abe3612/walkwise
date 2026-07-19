<script setup lang="ts">
/**
 * STEP4 Vue scaffold for electron/renderer/components/AppShell.vue.
 * The approved UI contract and related test cases are recorded below.
 */
const step4PublicContracts = [
  {
    "taskId": "TASK-UI-005",
    "symbol": "共通shell",
    "contract": "focus、keyboard、aria、error summaryを提供する。"
  }
] as const;
const step4TestCases = [
  {
    "id": "TC-UI-005-01",
    "priority": "P0",
    "layer": "unit",
    "title": "5画面navigation",
    "given": "Project文脈あり/なし",
    "when": "遷移",
    "then": "無効routeを安全な既定画面へ戻す",
    "testFile": "`electron/renderer/tests/navigation.test.ts`"
  },
  {
    "id": "TC-UI-005-02",
    "priority": "P0",
    "layer": "unit",
    "title": "focus/error summary",
    "given": "validation error",
    "when": "render",
    "then": "error summaryへfocus移動しariaで関連付け",
    "testFile": "`electron/renderer/tests/accessibility.test.ts`"
  },
  {
    "id": "TC-UI-005-03",
    "priority": "P0",
    "layer": "unit",
    "title": "keyboard only",
    "given": "mouseなし",
    "when": "主要操作",
    "then": "全操作に到達可能",
    "testFile": "`electron/renderer/tests/navigation.test.ts`"
  },
  {
    "id": "TC-UI-005-04",
    "priority": "P1",
    "layer": "unit",
    "title": "Project context",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`navigation state`を通じて「Project context」を実行する",
    "then": "「Project context」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/renderer/tests/accessibility.test.ts`"
  },
  {
    "id": "TC-UI-005-05",
    "priority": "P1",
    "layer": "integration_mock",
    "title": "typed API wrapper",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`navigation state`を通じて「typed API wrapper」を実行する",
    "then": "「typed API wrapper」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/renderer/tests/navigation.test.ts`"
  },
  {
    "id": "TC-UI-005-06",
    "priority": "P1",
    "layer": "unit",
    "title": "loading skeleton",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`navigation state`を通じて「loading skeleton」を実行する",
    "then": "「loading skeleton」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/renderer/tests/accessibility.test.ts`"
  },
  {
    "id": "TC-UI-005-07",
    "priority": "P1",
    "layer": "unit",
    "title": "日本語利用者message/technical detail分離",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`navigation state`を通じて「日本語利用者message/technical detail分離」を実行する",
    "then": "「日本語利用者message/technical detail分離」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/renderer/tests/navigation.test.ts`"
  },
  {
    "id": "TC-UI-005-08",
    "priority": "P0",
    "layer": "unit",
    "title": "必須入力欠落",
    "given": "主ID、必須path、必須設定のいずれかが欠落した入力",
    "when": "`navigation state`を実行する",
    "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。",
    "testFile": "`electron/renderer/tests/accessibility.test.ts`"
  },
  {
    "id": "TC-UI-005-09",
    "priority": "P1",
    "layer": "unit",
    "title": "再実行時の決定性",
    "given": "同じ入力、同じ設定、同じ依存応答",
    "when": "`navigation state`を2回実行する",
    "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。",
    "testFile": "`electron/renderer/tests/navigation.test.ts`"
  }
] as const;

function step4Unimplemented(): never {
  throw new Error("STEP4 source scaffold is not implemented: electron/renderer/components/AppShell.vue");
}

void step4PublicContracts;
void step4TestCases;
void step4Unimplemented;
</script>

<template>
  <section data-step4-scaffold="AppShell" aria-busy="true">
    <h1>AppShell</h1>
    <p>STEP4 source scaffold. Claude Code will implement this approved screen contract.</p>
  </section>
</template>
