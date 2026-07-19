<script setup lang="ts">
/**
 * STEP4 Vue scaffold for electron/renderer/screens/BuildSettings.vue.
 * The approved UI contract and related test cases are recorded below.
 */
const step4PublicContracts = [
  {
    "taskId": "TASK-UI-003",
    "symbol": "build settings UI",
    "contract": "複数形式、voice disabled、試聴、制作開始を扱う。"
  }
] as const;
const step4TestCases = [
  {
    "id": "TC-UI-003-01",
    "priority": "P0",
    "layer": "unit",
    "title": "text-only",
    "given": "textだけ選択",
    "when": "render/submit",
    "then": "voice controls disabledで制作開始可能",
    "testFile": "`electron/tests/build_voice_ipc.test.ts`"
  },
  {
    "id": "TC-UI-003-02",
    "priority": "P0",
    "layer": "unit",
    "title": "mp3条件",
    "given": "mp3選択・speaker未選択",
    "when": "render",
    "then": "制作開始disabled",
    "testFile": "`electron/renderer/tests/BuildSettings.test.ts`"
  },
  {
    "id": "TC-UI-003-03",
    "priority": "P0",
    "layer": "integration_mock",
    "title": "VOICEVOX疎通",
    "given": "engine未接続",
    "when": "画面表示",
    "then": "明確なerrorと再確認導線、Buildは開始しない",
    "testFile": "`electron/tests/build_voice_ipc.test.ts`"
  },
  {
    "id": "TC-UI-003-04",
    "priority": "P1",
    "layer": "unit",
    "title": "engine health/list",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`voice:list-engines/preview handlers`を通じて「engine health/list」を実行する",
    "then": "必要項目を欠かさず安定順で返し、空一覧も正常結果として扱う。",
    "testFile": "`electron/renderer/tests/BuildSettings.test.ts`"
  },
  {
    "id": "TC-UI-003-05",
    "priority": "P1",
    "layer": "unit",
    "title": "preview",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`voice:list-engines/preview handlers`を通じて「preview」を実行する",
    "then": "「preview」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/tests/build_voice_ipc.test.ts`"
  },
  {
    "id": "TC-UI-003-06",
    "priority": "P1",
    "layer": "unit",
    "title": "approval gate error導線",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`voice:list-engines/preview handlers`を通じて「approval gate error導線」を実行する",
    "then": "必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。",
    "testFile": "`electron/renderer/tests/BuildSettings.test.ts`"
  },
  {
    "id": "TC-UI-003-07",
    "priority": "P1",
    "layer": "unit",
    "title": "MVP外機能非表示",
    "given": "承認済み仕様に適合する最小入力と、必要な依存をmockした状態",
    "when": "`voice:list-engines/preview handlers`を通じて「MVP外機能非表示」を実行する",
    "then": "「MVP外機能非表示」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。",
    "testFile": "`electron/tests/build_voice_ipc.test.ts`"
  },
  {
    "id": "TC-UI-003-08",
    "priority": "P0",
    "layer": "unit",
    "title": "必須入力欠落",
    "given": "主ID、必須path、必須設定のいずれかが欠落した入力",
    "when": "`voice:list-engines/preview handlers`を実行する",
    "then": "副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。",
    "testFile": "`electron/renderer/tests/BuildSettings.test.ts`"
  },
  {
    "id": "TC-UI-003-09",
    "priority": "P1",
    "layer": "unit",
    "title": "再実行時の決定性",
    "given": "同じ入力、同じ設定、同じ依存応答",
    "when": "`voice:list-engines/preview handlers`を2回実行する",
    "then": "仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。",
    "testFile": "`electron/tests/build_voice_ipc.test.ts`"
  }
] as const;

function step4Unimplemented(): never {
  throw new Error("STEP4 source scaffold is not implemented: electron/renderer/screens/BuildSettings.vue");
}

void step4PublicContracts;
void step4TestCases;
void step4Unimplemented;
</script>

<template>
  <section data-step4-scaffold="BuildSettings" aria-busy="true">
    <h1>BuildSettings</h1>
    <p>STEP4 source scaffold. Claude Code will implement this approved screen contract.</p>
  </section>
</template>
