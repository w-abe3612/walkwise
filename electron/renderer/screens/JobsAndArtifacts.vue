<script setup lang="ts">
/**
 * electron/renderer/screens/JobsAndArtifacts.vue — 公開契約: jobs/artifacts UI.
 *
 * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
 * Spec: docs/screens/04-job-progress.md, docs/screens/05-artifacts.md
 *
 * router/store(TASK-UI-005)へ依存せず、実際のIPC呼び出しはpropsとして注入する。
 */
import { computed, reactive } from "vue";
import type { ArtifactItem, JobItem, JobStatus } from "./JobsAndArtifacts.types";

const props = defineProps<{
  jobs: readonly JobItem[];
  artifacts: readonly ArtifactItem[];
  cancelJob: (jobId: string) => Promise<unknown>;
  retryJob: (jobId: string) => Promise<unknown>;
  openFolder: (artifactId: string) => Promise<unknown>;
}>();

const CANCELLABLE_STATUSES = new Set<JobStatus>(["queued", "running"]);
const RETRYABLE_STATUSES = new Set<JobStatus>(["failed", "cancelled"]);

const pendingCancelConfirmation = reactive<Record<string, boolean>>({});

function isCancellable(job: JobItem): boolean {
  return CANCELLABLE_STATUSES.has(job.status);
}

function isRetryable(job: JobItem): boolean {
  return RETRYABLE_STATUSES.has(job.status);
}

/** 04-job-progress.md 10節: cancelは確認モーダルを経てから実行する。 */
async function handleCancelClick(jobId: string): Promise<void> {
  if (!pendingCancelConfirmation[jobId]) {
    pendingCancelConfirmation[jobId] = true;
    return;
  }
  pendingCancelConfirmation[jobId] = false;
  await props.cancelJob(jobId);
}

function cancelDialogVisible(jobId: string): boolean {
  return !!pendingCancelConfirmation[jobId];
}

async function handleRetryClick(jobId: string): Promise<void> {
  await props.retryJob(jobId);
}

/** 05-artifacts.md 7節: 同一artifact_typeは最新versionのみを既定表示する(旧versionは保持したまま非表示)。 */
const latestArtifactsByType = computed(() => {
  const latest = new Map<string, ArtifactItem>();
  for (const artifact of props.artifacts) {
    const current = latest.get(artifact.artifactType);
    if (!current || artifact.versionNumber > current.versionNumber) {
      latest.set(artifact.artifactType, artifact);
    }
  }
  return [...latest.values()];
});

defineExpose({ isCancellable, isRetryable, handleCancelClick, handleRetryClick, latestArtifactsByType });
</script>

<template>
  <section aria-label="Job進捗・成果物">
    <h2>Job一覧</h2>
    <ul data-testid="job-list">
      <li v-for="job in jobs" :key="job.jobId" data-testid="job-item">
        <span data-testid="job-status">{{ job.status }}</span>
        <span v-if="job.progressTotal" data-testid="job-progress">{{ job.progressCurrent }}/{{ job.progressTotal }}</span>
        <p v-if="job.stale" data-testid="stale-note">前回異常終了しました</p>

        <details v-if="job.technicalDetail" data-testid="technical-detail">
          <summary>技術detail</summary>
          <pre>{{ job.technicalDetail }}</pre>
        </details>

        <button
          type="button"
          data-testid="cancel-button"
          :disabled="!isCancellable(job)"
          @click="handleCancelClick(job.jobId)"
        >
          cancel
        </button>
        <div v-if="cancelDialogVisible(job.jobId)" role="alertdialog" data-testid="cancel-confirm-dialog">
          <p>実行中の処理を中断します。よろしいですか?</p>
          <button type="button" data-testid="cancel-confirm-button" @click="handleCancelClick(job.jobId)">
            中断する
          </button>
        </div>

        <button
          type="button"
          data-testid="retry-button"
          :disabled="!isRetryable(job)"
          @click="handleRetryClick(job.jobId)"
        >
          再試行
        </button>
      </li>
    </ul>

    <h2>成果物</h2>
    <ul data-testid="artifact-list">
      <li v-for="artifact in latestArtifactsByType" :key="artifact.artifactId" data-testid="artifact-item">
        <span>{{ artifact.artifactType }} v{{ artifact.versionNumber }}</span>
        <button type="button" data-testid="open-folder-button" @click="openFolder(artifact.artifactId)">
          フォルダを開く
        </button>
      </li>
    </ul>
    <a href="#" data-testid="regenerate-link">再生成</a>
  </section>
</template>
