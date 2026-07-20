<script setup lang="ts">
/**
 * electron/renderer/screens/ProjectWorkspace.vue — 公開契約: workspace UI.
 *
 * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
 * Spec: docs/screens/02-project-workspace-and-source-import.md
 *
 * router/store(TASK-UI-005)へ依存せず、実際のIPC呼び出しはpropsとして
 * 注入する(呼び出し側が`window.walkwise`と結線する)。
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
}>();

/** 02-project-workspace-and-source-import.md 7節の状態表示文言。 */
const STATUS_LABELS: Record<SourceItem["status"], string> = {
  registered: "登録済み・処理待ち",
  processing: "抽出・OCR処理中",
  ready: "準備完了",
  review_required: "要確認(低信頼・高リスク要素あり)",
  failed: "抽出に失敗しました",
};

/** 13節: MVP対象外(EPUB/Kindle/動画/録音)は選択肢に表示しない。 */
const ALLOWED_MEDIA_TYPES = ["text", "pdf", "image"] as const;

const requestChangesReason = reactive<Record<string, string>>({});
const requestChangesError = reactive<Record<string, string>>({});
const selectedMediaType = ref<(typeof ALLOWED_MEDIA_TYPES)[number]>("text");

async function submitRequestChanges(gate: string): Promise<void> {
  const reason = (requestChangesReason[gate] ?? "").trim();
  if (!reason) {
    requestChangesError[gate] = "差し戻し理由を入力してください。";
    return;
  }
  requestChangesError[gate] = "";
  await props.requestChanges(gate, reason);
}

async function registerFile(file: File | null | undefined): Promise<void> {
  if (!file) {
    return;
  }
  await props.registerSource({ filePath: file.name, mediaType: selectedMediaType.value });
}

function handleFileInputChange(event: Event): void {
  const target = event.target as HTMLInputElement;
  void registerFile(target.files?.[0]);
}

function handleDrop(event: DragEvent): void {
  void registerFile(event.dataTransfer?.files?.[0]);
}

defineExpose({ submitRequestChanges, registerFile, STATUS_LABELS, ALLOWED_MEDIA_TYPES });
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
    <select v-model="selectedMediaType" data-testid="media-type-select">
      <option v-for="mediaType in ALLOWED_MEDIA_TYPES" :key="mediaType" :value="mediaType">{{ mediaType }}</option>
    </select>
    <div data-testid="drop-zone" @drop.prevent="handleDrop" @dragover.prevent>
      ファイルをここへドロップ、または選択
      <input type="file" data-testid="file-input" @change="handleFileInputChange" />
    </div>

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
