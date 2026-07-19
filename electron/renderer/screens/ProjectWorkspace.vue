<script setup lang="ts">
/**
 * STEP4 Vue scaffold for electron/renderer/screens/ProjectWorkspace.vue.
 * The approved UI contract and related test cases are recorded below.
 */
const step4PublicContracts = [
  {
    "taskId": "TASK-UI-002",
    "symbol": "workspace UI",
    "contract": "Source状態、review導線、4承認を表示・操作する。"
  }
] as const;
const step4TestCases = [
  {
    "id": "TC-UI-002-01",
    "priority": "P0",
    "layer": "unit",
    "title": "Source状態表示",
    "given": "5 statusのSource",
    "when": "render",
    "then": "仕様の日本語表示とreview/retry導線",
    "testFile": "`electron/tests/source_approval_ipc.test.ts`"
  },
  {
    "id": "TC-UI-002-02",
    "priority": "P0",
    "layer": "unit",
    "title": "差し戻し",
    "given": "理由空/あり",
    "when": "request changes",
    "then": "空は拒否、ありはIPC1回",
    "testFile": "`electron/renderer/tests/ProjectWorkspace.test.ts`"
  },
  {
    "id": "TC-UI-002-03",
    "priority": "P0",
    "layer": "unit",
    "title": "対象外非表示",
    "given": "EPUB/Kindle/video",
    "when": "render",
    "then": "選択肢にもdisabledにも表示しない",
    "testFile": "`electron/tests/source_approval_ipc.test.ts`"
  },
  {
    "id": "TC-UI-002-04",
    "priority": "P1",
    "layer": "integration_mock",
    "title": "file dialog/drop",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`source:register handlers`を通じて「file dialog/drop」を実行する",
    "then": "「file dialog/drop」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/renderer/tests/ProjectWorkspace.test.ts`"
  },
  {
    "id": "TC-UI-002-05",
    "priority": "P1",
    "layer": "unit",
    "title": "処理開始",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`source:register handlers`を通じて「処理開始」を実行する",
    "then": "「処理開始」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/tests/source_approval_ipc.test.ts`"
  },
  {
    "id": "TC-UI-002-06",
    "priority": "P1",
    "layer": "unit",
    "title": "再処理/修正/問題なし",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`source:register handlers`を通じて「再処理/修正/問題なし」を実行する",
    "then": "「再処理/修正/問題なし」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/renderer/tests/ProjectWorkspace.test.ts`"
  },
  {
    "id": "TC-UI-002-07",
    "priority": "P1",
    "layer": "unit",
    "title": "approval badges",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`source:register handlers`を通じて「approval badges」を実行する",
    "then": "必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。",
    "testFile": "`electron/tests/source_approval_ipc.test.ts`"
  },
  {
    "id": "TC-UI-002-08",
    "priority": "P0",
    "layer": "unit",
    "title": "必須入力欠落",
    "given": "主ID、必須path、必須設定のいずれかが欠落した入力",
    "when": "`source:register handlers`を実行する",
    "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。",
    "testFile": "`electron/renderer/tests/ProjectWorkspace.test.ts`"
  },
  {
    "id": "TC-UI-002-09",
    "priority": "P1",
    "layer": "unit",
    "title": "再実行時の決定性",
    "given": "同じ入力、同じ設定、同じ依存応答",
    "when": "`source:register handlers`を2回実行する",
    "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。",
    "testFile": "`electron/tests/source_approval_ipc.test.ts`"
  }
] as const;

function step4Unimplemented(): never {
  throw new Error("STEP4 source scaffold is not implemented: electron/renderer/screens/ProjectWorkspace.vue");
}

void step4PublicContracts;
void step4TestCases;
void step4Unimplemented;
</script>

<template>
  <section data-step4-scaffold="ProjectWorkspace" aria-busy="true">
    <h1>ProjectWorkspace</h1>
    <p>STEP4 source scaffold. Claude Code will implement this approved screen contract.</p>
  </section>
</template>
