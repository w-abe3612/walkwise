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
import type {
  ApprovalItem,
  SourceItem,
  VoiceEngineHealthView,
  VoiceProfileFormInput,
  VoiceProfileItem,
  VoiceProfileStatus,
  VoiceSpeakerOptionView,
} from "./screens/ProjectWorkspace.types";
import type { OutputFormat, VoiceProfileOptionView } from "./screens/BuildSettings.types";
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
  readonly voiceProfile: {
    create(input: unknown): Promise<unknown>;
    list(projectId: string): Promise<unknown>;
    get(voiceProfileId: string): Promise<unknown>;
    update(input: unknown): Promise<unknown>;
    archive(voiceProfileId: string): Promise<unknown>;
  };
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

const workspace = reactive<{
  sources: SourceItem[];
  approvals: ApprovalItem[];
  voiceProfiles: VoiceProfileItem[];
  voiceEngineHealth: VoiceEngineHealthView | null;
  voiceSpeakers: VoiceSpeakerOptionView[];
}>({ sources: [], approvals: [], voiceProfiles: [], voiceEngineHealth: null, voiceSpeakers: [] });
const build = reactive<{ voiceProfiles: VoiceProfileOptionView[] }>({ voiceProfiles: [] });
const jobsAndArtifacts = reactive<{ jobs: JobItem[]; artifacts: ArtifactItem[] }>({ jobs: [], artifacts: [] });

function unwrapList<T>(result: unknown, key: string): T[] {
  if (Array.isArray(result)) return result as T[];
  const record = result as Record<string, unknown> | null | undefined;
  return (record?.[key] as T[] | undefined) ?? [];
}

/** Project WorkspaceのVoiceProfile一覧だけを再取得する(create/update/approve/archive後の反映用)。 */
async function loadVoiceProfiles(projectId: string): Promise<void> {
  const result = await walkwiseApi().voiceProfile.list(projectId);
  workspace.voiceProfiles = unwrapList<VoiceProfileItem>(result, "voiceProfiles");
}

async function loadWorkspace(projectId: string): Promise<void> {
  await withLoading(async () => {
    const [sourceResult, approvalResult, voiceProfileResult, engineResult] = await Promise.all([
      walkwiseApi().source.list(projectId),
      walkwiseApi().approval.list(projectId),
      walkwiseApi().voiceProfile.list(projectId),
      walkwiseApi().voice.listEngines(),
    ]);
    workspace.sources = unwrapList<SourceItem>(sourceResult, "sources");
    workspace.approvals = unwrapList<ApprovalItem>(approvalResult, "approvals");
    workspace.voiceProfiles = unwrapList<VoiceProfileItem>(voiceProfileResult, "voiceProfiles");
    const engines = engineResult as { health: VoiceEngineHealthView; speakers: VoiceSpeakerOptionView[] };
    workspace.voiceEngineHealth = engines.health;
    workspace.voiceSpeakers = engines.speakers;
  });
}

/** Build Settingsでは、このProjectのVoiceProfile一覧(approved絞り込みはBuildSettings.vue側で行う)だけを読み込む。 */
async function loadBuildSettings(projectId: string): Promise<void> {
  await withLoading(async () => {
    const result = await walkwiseApi().voiceProfile.list(projectId);
    build.voiceProfiles = unwrapList<VoiceProfileOptionView>(result, "voiceProfiles");
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
    else if (screen === "build-settings") void loadBuildSettings(projectId);
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

// --- ProjectWorkspace VoiceProfile wiring ---
// create/updateはmodal側で局所的にerrorを表示できるよう、あえてwithLoading()で
// 包まない(失敗してもmodalの入力内容を保持したまま呼び出し元がcatchできるようにする)。
async function createVoiceProfile(input: VoiceProfileFormInput): Promise<void> {
  if (!navigation.projectId) throw new Error("Project文脈がありません");
  await walkwiseApi().voiceProfile.create({ projectId: navigation.projectId, ...input });
  await loadVoiceProfiles(navigation.projectId);
}

async function updateVoiceProfile(
  voiceProfileId: string,
  input: Partial<VoiceProfileFormInput> & { status?: VoiceProfileStatus },
): Promise<void> {
  if (!navigation.projectId) throw new Error("Project文脈がありません");
  await walkwiseApi().voiceProfile.update({ voiceProfileId, ...input });
  await loadVoiceProfiles(navigation.projectId);
}

async function approveVoiceProfile(voiceProfileId: string): Promise<void> {
  await withLoading(async () => {
    await walkwiseApi().voiceProfile.update({ voiceProfileId, status: "approved" });
    if (navigation.projectId) await loadVoiceProfiles(navigation.projectId);
  });
}

async function archiveVoiceProfile(voiceProfileId: string): Promise<void> {
  await withLoading(async () => {
    await walkwiseApi().voiceProfile.archive(voiceProfileId);
    if (navigation.projectId) await loadVoiceProfiles(navigation.projectId);
  });
}

// --- BuildSettings wiring ---
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
      :voice-profiles="workspace.voiceProfiles"
      :voice-engine-health="workspace.voiceEngineHealth"
      :voice-speakers="workspace.voiceSpeakers"
      :create-voice-profile="createVoiceProfile"
      :update-voice-profile="updateVoiceProfile"
      :approve-voice-profile="approveVoiceProfile"
      :archive-voice-profile="archiveVoiceProfile"
    />

    <BuildSettings
      v-else-if="currentScreen === 'build-settings'"
      :voice-profiles="build.voiceProfiles"
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
