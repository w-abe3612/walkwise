<script setup lang="ts">
/**
 * electron/renderer/App.vue — 公開契約: Rendererのroot component.
 *
 * TASK-REVIEW-001監査2.4節: 各画面(ProjectList/ProjectWorkspace/BuildSettings/
 * JobsAndArtifacts)は完成していたが、それらをnavigation・共通state・実際の
 * `window.walkwise` API呼び出しへ結線するroot componentがどこにも存在しなかった
 * (`electron/renderer/main.ts`は空のplaceholder divをmountするだけだった)。
 * 本componentが、router.ts(resolveNavigation)・stores/app.ts(AppStore)・5画面・
 * preloadが公開する`window.walkwise`を実際に結線する唯一の場所となる。
 */
import { computed, onMounted, reactive, watch } from "vue";

import AppShell from "./components/AppShell.vue";
import { NAVIGATION_SCREENS, resolveNavigation, type ScreenId } from "./router";
import { AppStore } from "./stores/app";
import ProjectList from "./screens/ProjectList.vue";
import ProjectWorkspace from "./screens/ProjectWorkspace.vue";
import BuildSettings from "./screens/BuildSettings.vue";
import JobsAndArtifacts from "./screens/JobsAndArtifacts.vue";
import type { ApprovalItem, SourceItem } from "./screens/ProjectWorkspace.types";
import type { EngineHealthView, OutputFormat, SpeakerOptionView } from "./screens/BuildSettings.types";
import type { ArtifactItem, JobItem } from "./screens/JobsAndArtifacts.types";

interface WalkwiseApi {
  readonly project: { list(): Promise<unknown>; create(input: unknown): Promise<unknown>; get(id: string): Promise<unknown> };
  readonly source: {
    register(input: unknown): Promise<unknown>;
    list(projectId: string): Promise<unknown>;
    retry(sourceId: string): Promise<unknown>;
  };
  readonly approval: {
    list(projectId: string): Promise<unknown>;
    approve(input: unknown): Promise<unknown>;
    requestChanges(input: unknown): Promise<unknown>;
  };
  readonly buildRequest: { create(input: unknown): Promise<unknown> };
  readonly job: {
    start(input: unknown): Promise<unknown>;
    list(projectId: string): Promise<unknown>;
    get(jobId: string): Promise<unknown>;
    subscribeProgress(jobId: string, listener: (event: unknown) => void): () => void;
    cancel(jobId: string): Promise<unknown>;
  };
  readonly artifact: { list(projectId: string): Promise<unknown>; openFolder(artifactId: string): Promise<unknown> };
  readonly voice: { listEngines(): Promise<unknown>; preview(input: unknown): Promise<unknown> };
  readonly dialog: { selectSourceFile(): Promise<unknown> };
}

function walkwiseApi(): WalkwiseApi {
  const api = (globalThis as unknown as { walkwise?: WalkwiseApi }).walkwise;
  if (!api) {
    throw new Error("window.walkwise API is not available (preloadが正しく結線されていません)");
  }
  return api;
}

const store = new AppStore();
const state = reactive(store.getState());
function sync(): void {
  Object.assign(state, store.getState());
}

const navigation = reactive(resolveNavigation({ screen: "projects-list" }));

function navigate(screen: ScreenId, projectId?: string | null): void {
  const result = resolveNavigation({ screen, projectId: projectId ?? navigation.projectId });
  Object.assign(navigation, result);
  store.setCurrentProject(result.projectId);
  store.clearError();
  sync();
}

async function withLoading(fn: () => Promise<void>): Promise<void> {
  store.setLoading(true);
  sync();
  try {
    await fn();
    store.clearError();
  } catch (err) {
    store.setError(err, err instanceof Error ? err.stack : undefined);
  } finally {
    store.setLoading(false);
    sync();
  }
}

const workspace = reactive<{ sources: SourceItem[]; approvals: ApprovalItem[] }>({ sources: [], approvals: [] });
const build = reactive<{ engineHealth: EngineHealthView | null; speakers: SpeakerOptionView[] }>({
  engineHealth: null,
  speakers: [],
});
const jobsAndArtifacts = reactive<{ jobs: JobItem[]; artifacts: ArtifactItem[] }>({ jobs: [], artifacts: [] });

function unwrapList<T>(result: unknown, key: string): T[] {
  if (Array.isArray(result)) return result as T[];
  const record = result as Record<string, unknown> | null | undefined;
  return (record?.[key] as T[] | undefined) ?? [];
}

async function loadWorkspace(projectId: string): Promise<void> {
  await withLoading(async () => {
    const [sourceResult, approvalResult] = await Promise.all([
      walkwiseApi().source.list(projectId),
      walkwiseApi().approval.list(projectId),
    ]);
    workspace.sources = unwrapList<SourceItem>(sourceResult, "sources");
    workspace.approvals = unwrapList<ApprovalItem>(approvalResult, "approvals");
  });
}

async function loadBuildSettings(): Promise<void> {
  build.engineHealth = null;
  await withLoading(async () => {
    const result = (await walkwiseApi().voice.listEngines()) as {
      health: EngineHealthView;
      speakers: SpeakerOptionView[];
    };
    build.engineHealth = result.health;
    build.speakers = result.speakers;
  });
}

async function loadJobsAndArtifacts(projectId: string): Promise<void> {
  await withLoading(async () => {
    const [jobResult, artifactResult] = await Promise.all([
      walkwiseApi().job.list(projectId),
      walkwiseApi().artifact.list(projectId),
    ]);
    jobsAndArtifacts.jobs = unwrapList<JobItem>(jobResult, "jobs");
    jobsAndArtifacts.artifacts = unwrapList<ArtifactItem>(artifactResult, "artifacts");
  });
}

watch(
  () => [navigation.screen, navigation.projectId] as const,
  ([screen, projectId]) => {
    if (!projectId) return;
    if (screen === "project-workspace") void loadWorkspace(projectId);
    else if (screen === "build-settings") void loadBuildSettings();
    else if (screen === "jobs" || screen === "artifacts") void loadJobsAndArtifacts(projectId);
  },
  { immediate: true },
);

function handleOpenProject(projectId: string): void {
  navigate("project-workspace", projectId);
}

// --- ProjectWorkspace wiring ---
async function registerSource(input: { filePath: string; mediaType: string }): Promise<void> {
  if (!navigation.projectId) return;
  await withLoading(async () => {
    await walkwiseApi().source.register({ projectId: navigation.projectId, ...input });
    await loadWorkspace(navigation.projectId!);
  });
}

async function retrySource(sourceId: string): Promise<void> {
  await withLoading(async () => {
    await walkwiseApi().source.retry(sourceId);
    if (navigation.projectId) await loadWorkspace(navigation.projectId);
  });
}

async function approveGate(gate: string): Promise<void> {
  if (!navigation.projectId) return;
  await withLoading(async () => {
    await walkwiseApi().approval.approve({ projectId: navigation.projectId, gate, approvedBy: "current_user" });
    await loadWorkspace(navigation.projectId!);
  });
}

async function requestChangesForGate(gate: string, reason: string): Promise<void> {
  if (!navigation.projectId) return;
  await withLoading(async () => {
    await walkwiseApi().approval.requestChanges({ projectId: navigation.projectId, gate, reason });
    await loadWorkspace(navigation.projectId!);
  });
}

async function selectSourceFile(): Promise<{ filePath: string; mediaType: string } | null> {
  return (await walkwiseApi().dialog.selectSourceFile()) as { filePath: string; mediaType: string } | null;
}

// --- BuildSettings wiring ---
async function previewVoice(speakerId: string, text: string): Promise<void> {
  await withLoading(async () => {
    await walkwiseApi().voice.preview({ speakerId, text });
  });
}

async function createBuildRequest(input: { outputFormats: OutputFormat[]; voiceProfileId?: string }): Promise<unknown> {
  if (!navigation.projectId) throw new Error("Project文脈がありません");
  return walkwiseApi().buildRequest.create({ projectId: navigation.projectId, ...input });
}

async function startJob(buildRequestId: string): Promise<void> {
  await withLoading(async () => {
    await walkwiseApi().job.start(buildRequestId);
    if (navigation.projectId) navigate("jobs", navigation.projectId);
  });
}

// --- JobsAndArtifacts wiring ---
async function cancelJob(jobId: string): Promise<void> {
  await withLoading(async () => {
    await walkwiseApi().job.cancel(jobId);
    if (navigation.projectId) await loadJobsAndArtifacts(navigation.projectId);
  });
}

async function retryJob(jobId: string): Promise<void> {
  await withLoading(async () => {
    await walkwiseApi().job.start({ parentJobId: jobId });
    if (navigation.projectId) await loadJobsAndArtifacts(navigation.projectId);
  });
}

async function openFolder(artifactId: string): Promise<void> {
  await withLoading(async () => {
    await walkwiseApi().artifact.openFolder(artifactId);
  });
}

const currentScreen = computed(() => navigation.screen);

onMounted(() => {
  store.clearError();
  sync();
});

defineExpose({ navigate, handleOpenProject, NAVIGATION_SCREENS });
</script>

<template>
  <AppShell :current-screen="currentScreen" :loading="state.loading" :error="state.error" :navigate="navigate">
    <ProjectList v-if="currentScreen === 'projects-list'" @open-project="handleOpenProject" />

    <ProjectWorkspace
      v-else-if="currentScreen === 'project-workspace'"
      :sources="workspace.sources"
      :approvals="workspace.approvals"
      :register-source="registerSource"
      :retry-source="retrySource"
      :approve="approveGate"
      :request-changes="requestChangesForGate"
      :select-source-file="selectSourceFile"
    />

    <BuildSettings
      v-else-if="currentScreen === 'build-settings'"
      :engine-health="build.engineHealth"
      :speakers="build.speakers"
      :preview="previewVoice"
      :create-build-request="createBuildRequest"
      :start-job="startJob"
    />

    <JobsAndArtifacts
      v-else-if="currentScreen === 'jobs' || currentScreen === 'artifacts'"
      :jobs="jobsAndArtifacts.jobs"
      :artifacts="jobsAndArtifacts.artifacts"
      :cancel-job="cancelJob"
      :retry-job="retryJob"
      :open-folder="openFolder"
    />
  </AppShell>
</template>
