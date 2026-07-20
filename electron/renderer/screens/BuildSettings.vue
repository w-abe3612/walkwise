<script setup lang="ts">
/**
 * electron/renderer/screens/BuildSettings.vue — 公開契約: build settings UI.
 *
 * Contract: docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md
 * Spec: docs/screens/03-build-settings.md
 *
 * router/store(TASK-UI-005)へ依存せず、実際のIPC呼び出しはpropsとして注入する。
 */
import { computed, reactive, ref } from "vue";
import type { EngineHealthView, OutputFormat, SpeakerOptionView } from "./BuildSettings.types";

const props = defineProps<{
  engineHealth: EngineHealthView | null; // null = 接続確認中(loading)
  speakers: readonly SpeakerOptionView[];
  preview: (speakerId: string, text: string) => Promise<unknown>;
  createBuildRequest: (input: { outputFormats: OutputFormat[]; voiceProfileId?: string }) => Promise<unknown>;
  startJob: (buildRequestId: string) => Promise<unknown>;
}>();

const selectedFormats = reactive<Record<OutputFormat, boolean>>({ mp3: false, text: false });
const selectedSpeakerId = ref("");
const speedScale = ref(1.0);
const submitError = ref("");
const showApprovalLink = ref(false);

const mp3Selected = computed(() => selectedFormats.mp3);
// 03-build-settings.md 7節: VOICEVOX未接続の間はMP3出力を選択できない。
const voiceControlsDisabled = computed(() => !mp3Selected.value || !props.engineHealth?.available);

const isSubmitEnabled = computed(() => {
  const anyFormatSelected = selectedFormats.mp3 || selectedFormats.text;
  if (!anyFormatSelected) {
    return false;
  }
  if (selectedFormats.mp3 && !selectedSpeakerId.value) {
    return false;
  }
  return true;
});

function toggleFormat(format: OutputFormat): void {
  selectedFormats[format] = !selectedFormats[format];
  if (format === "mp3" && !selectedFormats.mp3) {
    selectedSpeakerId.value = "";
  }
}

async function submitPreview(): Promise<void> {
  if (voiceControlsDisabled.value || !selectedSpeakerId.value) {
    return;
  }
  await props.preview(selectedSpeakerId.value, "プレビュー用サンプルテキスト");
}

async function submitBuild(): Promise<void> {
  if (!isSubmitEnabled.value) {
    return;
  }
  submitError.value = "";
  showApprovalLink.value = false;
  const outputFormats = (Object.keys(selectedFormats) as OutputFormat[]).filter((f) => selectedFormats[f]);
  try {
    const buildRequest = (await props.createBuildRequest({
      outputFormats,
      voiceProfileId: selectedFormats.mp3 ? selectedSpeakerId.value : undefined,
    })) as { buildRequestId: string };
    await props.startJob(buildRequest.buildRequestId);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    submitError.value = message;
    if (message.includes("approval_gate_not_satisfied")) {
      showApprovalLink.value = true;
    }
  }
}

defineExpose({ isSubmitEnabled, voiceControlsDisabled, submitBuild, submitPreview });
</script>

<template>
  <section aria-label="出力・声設定">
    <div v-if="engineHealth === null" data-testid="engine-loading" role="status">VOICEVOX接続確認中…</div>
    <div v-else-if="!engineHealth.available" data-testid="engine-error" role="alert">
      <p>VOICEVOX Engineに接続できません。</p>
      <button type="button" data-testid="engine-retry">再確認</button>
    </div>
    <div v-else data-testid="engine-success">
      <p>VOICEVOX Engine接続済み</p>
    </div>

    <fieldset data-testid="output-format-fieldset">
      <label>
        <input type="checkbox" data-testid="format-mp3" :checked="selectedFormats.mp3" @change="toggleFormat('mp3')" />
        MP3
      </label>
      <label>
        <input type="checkbox" data-testid="format-text" :checked="selectedFormats.text" @change="toggleFormat('text')" />
        テキスト
      </label>
    </fieldset>

    <select v-model="selectedSpeakerId" data-testid="speaker-select" :disabled="voiceControlsDisabled">
      <option value="" disabled>speakerを選択</option>
      <option v-for="speaker in speakers" :key="speaker.speakerId" :value="speaker.speakerId">
        {{ speaker.displayName }}
      </option>
    </select>

    <input
      v-model.number="speedScale"
      type="range"
      min="0.5"
      max="2.0"
      step="0.1"
      data-testid="speed-slider"
      :disabled="voiceControlsDisabled"
    />

    <button type="button" data-testid="preview-button" :disabled="voiceControlsDisabled || !selectedSpeakerId" @click="submitPreview">
      試聴
    </button>

    <p v-if="submitError" role="alert" data-testid="submit-error">{{ submitError }}</p>
    <a v-if="showApprovalLink" href="#" data-testid="approval-link">承認画面へ</a>

    <button type="button" data-testid="submit-button" :disabled="!isSubmitEnabled" @click="submitBuild">制作開始</button>
  </section>
</template>
