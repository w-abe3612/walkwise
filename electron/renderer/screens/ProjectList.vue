<script setup lang="ts">
/**
 * STEP4 Vue scaffold for electron/renderer/screens/ProjectList.vue.
 * The approved UI contract and related test cases are recorded below.
 */
const step4PublicContracts = [
  {
    "taskId": "TASK-UI-001",
    "symbol": "Project list/create UI",
    "contract": "empty/loading/success/error/disabledとkeyboard操作を実装する。"
  }
] as const;
const step4TestCases = [
  {
    "id": "TC-UI-001-01",
    "priority": "P0",
    "layer": "unit",
    "title": "empty/loading/error",
    "given": "各service状態",
    "when": "画面表示",
    "then": "仕様の文言・再試行・skeletonを表示",
    "testFile": "`electron/tests/project_ipc.test.ts`"
  },
  {
    "id": "TC-UI-001-02",
    "priority": "P0",
    "layer": "unit",
    "title": "作成disabled",
    "given": "必須項目不足",
    "when": "form操作",
    "then": "確定button disabled",
    "testFile": "`electron/renderer/tests/ProjectList.test.ts`"
  },
  {
    "id": "TC-UI-001-03",
    "priority": "P0",
    "layer": "unit",
    "title": "keyboard",
    "given": "formへTab/Enter",
    "when": "操作",
    "then": "順序移動し有効時だけ作成",
    "testFile": "`electron/tests/project_ipc.test.ts`"
  },
  {
    "id": "TC-UI-001-04",
    "priority": "P1",
    "layer": "unit",
    "title": "一覧",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`registerProjectIpcHandlers(context)`を通じて「一覧」を実行する",
    "then": "必要項目を欠かさず安定順で返し、空一覧も正常結果として扱う。",
    "testFile": "`electron/renderer/tests/ProjectList.test.ts`"
  },
  {
    "id": "TC-UI-001-05",
    "priority": "P1",
    "layer": "unit",
    "title": "新規作成form",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`registerProjectIpcHandlers(context)`を通じて「新規作成form」を実行する",
    "then": "「新規作成form」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/tests/project_ipc.test.ts`"
  },
  {
    "id": "TC-UI-001-06",
    "priority": "P1",
    "layer": "unit",
    "title": "必須validation",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`registerProjectIpcHandlers(context)`を通じて「必須validation」を実行する",
    "then": "正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。",
    "testFile": "`electron/renderer/tests/ProjectList.test.ts`"
  },
  {
    "id": "TC-UI-001-07",
    "priority": "P1",
    "layer": "unit",
    "title": "Enter/Tab",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`registerProjectIpcHandlers(context)`を通じて「Enter/Tab」を実行する",
    "then": "「Enter/Tab」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/tests/project_ipc.test.ts`"
  },
  {
    "id": "TC-UI-001-08",
    "priority": "P0",
    "layer": "unit",
    "title": "必須入力欠落",
    "given": "主ID、必須path、必須設定のいずれかが欠落した入力",
    "when": "`registerProjectIpcHandlers(context)`を実行する",
    "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。",
    "testFile": "`electron/renderer/tests/ProjectList.test.ts`"
  },
  {
    "id": "TC-UI-001-09",
    "priority": "P1",
    "layer": "unit",
    "title": "再実行時の決定性",
    "given": "同じ入力、同じ設定、同じ依存応答",
    "when": "`registerProjectIpcHandlers(context)`を2回実行する",
    "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。",
    "testFile": "`electron/tests/project_ipc.test.ts`"
  }
] as const;

function step4Unimplemented(): never {
  throw new Error("STEP4 source scaffold is not implemented: electron/renderer/screens/ProjectList.vue");
}

void step4PublicContracts;
void step4TestCases;
void step4Unimplemented;
</script>

<template>
  <section data-step4-scaffold="ProjectList" aria-busy="true">
    <h1>ProjectList</h1>
    <p>STEP4 source scaffold. Claude Code will implement this approved screen contract.</p>
  </section>
</template>
