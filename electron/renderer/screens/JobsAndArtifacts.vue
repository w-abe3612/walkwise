<script setup lang="ts">
/**
 * STEP4 Vue scaffold for electron/renderer/screens/JobsAndArtifacts.vue.
 * The approved UI contract and related test cases are recorded below.
 */
const step4PublicContracts = [
  {
    "taskId": "TASK-UI-004",
    "symbol": "jobs/artifacts UI",
    "contract": "進捗、stale注記、cancel確認、retry、最新成果物を表示する。"
  }
] as const;
const step4TestCases = [
  {
    "id": "TC-UI-004-01",
    "priority": "P0",
    "layer": "unit",
    "title": "cancel確認",
    "given": "running Job",
    "when": "cancel click",
    "then": "確認後だけIPCを呼ぶ",
    "testFile": "`electron/tests/job_artifact_ipc.test.ts`"
  },
  {
    "id": "TC-UI-004-02",
    "priority": "P0",
    "layer": "unit",
    "title": "retry条件",
    "given": "failed/cancelled/other",
    "when": "render",
    "then": "前2つだけretry可能",
    "testFile": "`electron/renderer/tests/JobsAndArtifacts.test.ts`"
  },
  {
    "id": "TC-UI-004-03",
    "priority": "P0",
    "layer": "unit",
    "title": "最新Artifact",
    "given": "複数version",
    "when": "render",
    "then": "最新を既定表示し旧versionを破壊しない",
    "testFile": "`electron/tests/job_artifact_ipc.test.ts`"
  },
  {
    "id": "TC-UI-004-04",
    "priority": "P1",
    "layer": "unit",
    "title": "job:get/subscribe/cancel/start retry",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`job:get/subscribe/cancel/retry handlers`を通じて「job:get/subscribe/cancel/start retry」を実行する",
    "then": "再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。",
    "testFile": "`electron/renderer/tests/JobsAndArtifacts.test.ts`"
  },
  {
    "id": "TC-UI-004-05",
    "priority": "P1",
    "layer": "unit",
    "title": "状態別button",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`job:get/subscribe/cancel/retry handlers`を通じて「状態別button」を実行する",
    "then": "承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。",
    "testFile": "`electron/tests/job_artifact_ipc.test.ts`"
  },
  {
    "id": "TC-UI-004-06",
    "priority": "P1",
    "layer": "unit",
    "title": "stale注記",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`job:get/subscribe/cancel/retry handlers`を通じて「stale注記」を実行する",
    "then": "「stale注記」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/renderer/tests/JobsAndArtifacts.test.ts`"
  },
  {
    "id": "TC-UI-004-07",
    "priority": "P1",
    "layer": "unit",
    "title": "技術detail折畳み",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`job:get/subscribe/cancel/retry handlers`を通じて「技術detail折畳み」を実行する",
    "then": "「技術detail折畳み」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/tests/job_artifact_ipc.test.ts`"
  },
  {
    "id": "TC-UI-004-08",
    "priority": "P0",
    "layer": "unit",
    "title": "必須入力欠落",
    "given": "主ID、必須path、必須設定のいずれかが欠落した入力",
    "when": "`job:get/subscribe/cancel/retry handlers`を実行する",
    "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。",
    "testFile": "`electron/renderer/tests/JobsAndArtifacts.test.ts`"
  },
  {
    "id": "TC-UI-004-09",
    "priority": "P1",
    "layer": "unit",
    "title": "再実行時の決定性",
    "given": "同じ入力、同じ設定、同じ依存応答",
    "when": "`job:get/subscribe/cancel/retry handlers`を2回実行する",
    "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。",
    "testFile": "`electron/tests/job_artifact_ipc.test.ts`"
  }
] as const;

function step4Unimplemented(): never {
  throw new Error("STEP4 source scaffold is not implemented: electron/renderer/screens/JobsAndArtifacts.vue");
}

void step4PublicContracts;
void step4TestCases;
void step4Unimplemented;
</script>

<template>
  <section data-step4-scaffold="JobsAndArtifacts" aria-busy="true">
    <h1>JobsAndArtifacts</h1>
    <p>STEP4 source scaffold. Claude Code will implement this approved screen contract.</p>
  </section>
</template>
