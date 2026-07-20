<script setup lang="ts">
/**
 * electron/renderer/screens/ProjectWorkspace.vue — 公開契約: workspace UI.
 *
 * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
 * Spec: docs/screens/02-project-workspace-and-source-import.md
 *
 * router/store(TASK-UI-005)へ依存せず、実際のIPC呼び出しはpropsとして
 * 注入する(呼び出し側が`window.walkwise`と結線する)。
 *
 * TASK-REVIEW-001 2.6節: 以前はブラウザの`<input type=file>`/drag&dropが返す
 * `File.name`(拡張子付きファイル名のみで実在するpathではない)をそのまま
 * `filePath`として送っており、main/Workerは対象fileを一度も実際に読めなかった。
 * 本componentはファイル選択そのものをmain process(`dialog.showOpenDialog()`)へ
 * 委譲し、renderer側では検証済みの絶対path以外を一切組み立てない。
 */
import { reactive, ref } from "vue";
import type { ApprovalItem, SourceItem } from "./ProjectWorkspace.types";

const props = defineProps<{
  sources: readonly SourceItem[];
  approvals: readonly ApprovalItem[];
  registerSource: (input: { filePath: string; mediaType: string }) => Promise<unknown>;
  retrySource: (sourceId: string) => Promise<unknown>;
  approve: (gate: string) => Promise<unknown>;
  requestChanges: (gate: string, reason: string) => Promise<unknown>;
  /** main processの`dialog:select-source-file`を呼び出し、検証済みの絶対pathと推定media typeを返す
   * (利用者がdialogを閉じた場合はnull)。 */
  selectSourceFile: () => Promise<{ filePath: string; mediaType: string } | null>;
}>();

/** 02-project-workspace-and-source-import.md 7節の状態表示文言。 */
const STATUS_LABELS: Record<SourceItem["status"], string> = {
  registered: "登録済み・処理待ち",
  processing: "抽出・OCR処理中",
  ready: "準備完了",
  review_required: "要確認(低信頼・高リスク要素あり)",
  failed: "抽出に失敗しました",
};

/** 13節: MVP対象外(EPUB/Kindle/動画/録音)は選択肢に表示しない(表示専用、選択はdialog側のfilterが決める)。 */
const ALLOWED_MEDIA_TYPES = ["text", "pdf", "image"] as const;

const requestChangesReason = reactive<Record<string, string>>({});
const requestChangesError = reactive<Record<string, string>>({});
const selectFileError = ref("");

async function submitRequestChanges(gate: string): Promise<void> {
  const reason = (requestChangesReason[gate] ?? "").trim();
  if (!reason) {
    requestChangesError[gate] = "差し戻し理由を入力してください。";
    return;
  }
  requestChangesError[gate] = "";
  await props.requestChanges(gate, reason);
}

/** dialog選択→main側検証済みの絶対path以外は一切registerSourceへ渡さない。 */
async function selectAndRegisterFile(): Promise<void> {
  selectFileError.value = "";
  try {
    const selection = await props.selectSourceFile();
    if (!selection) {
      return; // 利用者がdialogを閉じた
    }
    await props.registerSource({ filePath: selection.filePath, mediaType: selection.mediaType });
  } catch (err) {
    selectFileError.value = err instanceof Error ? err.message : String(err);
  }
}

defineExpose({ submitRequestChanges, selectAndRegisterFile, STATUS_LABELS, ALLOWED_MEDIA_TYPES });
</script>

<template>
  <section aria-label="Project workspace">
    <h2>Source一覧</h2>
    <ul data-testid="source-list">
      <li v-for="source in sources" :key="source.sourceId" data-testid="source-item">
        <span data-testid="source-status">{{ STATUS_LABELS[source.status] }}</span>
        <button
          v-if="source.status === 'review_required'"
          type="button"
          data-testid="review-link"
        >
          確認する
        </button>
        <button
          v-if="source.status === 'failed'"
          type="button"
          data-testid="retry-button"
          @click="retrySource(source.sourceId)"
        >
          再試行
        </button>
      </li>
    </ul>

    <h2>素材を登録</h2>
    <p>対応形式: {{ ALLOWED_MEDIA_TYPES.join(", ") }}</p>
    <button type="button" data-testid="select-file-button" @click="selectAndRegisterFile">
      ファイルを選択…
    </button>
    <p v-if="selectFileError" role="alert" data-testid="select-file-error">{{ selectFileError }}</p>

    <h2>承認</h2>
    <ul data-testid="approval-list">
      <li v-for="approval in approvals" :key="approval.gate" data-testid="approval-badge">
        <span>{{ approval.gate }}: {{ approval.status }}</span>
        <button type="button" data-testid="approve-button" @click="approve(approval.gate)">承認</button>
        <input
          :data-testid="`reason-input-${approval.gate}`"
          v-model="requestChangesReason[approval.gate]"
          type="text"
        />
        <p
          v-if="requestChangesError[approval.gate]"
          role="alert"
          :data-testid="`reason-error-${approval.gate}`"
        >
          {{ requestChangesError[approval.gate] }}
        </p>
        <button
          type="button"
          :data-testid="`request-changes-button-${approval.gate}`"
          @click="submitRequestChanges(approval.gate)"
        >
          差し戻し
        </button>
      </li>
    </ul>
  </section>
</template>
