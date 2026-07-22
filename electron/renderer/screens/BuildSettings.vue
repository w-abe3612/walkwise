<script setup lang="ts">
/**
 * electron/renderer/screens/BuildSettings.vue — 公開契約: build settings UI.
 *
 * Contract: docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md
 * Spec: docs/screens/03-build-settings.md
 *
 * TASK-VOICE-PROFILE-UI-001: 旧来のVOICEVOX speaker/style直接選択UI(`voice:list-engines`
 * ベース)は削除した。本画面はこのProjectのapproved VoiceProfileを1件選択するだけになり、
 * 新規作成・編集・承認・archiveはProject Workspace側でのみ行う(本画面には新規作成
 * ボタンを置かない)。draft/archivedのVoiceProfileは選択肢に一切出さない。
 *
 * router/store(TASK-UI-005)へ依存せず、実際のIPC呼び出しはpropsとして注入する。
 */
import { computed, reactive, ref, watch } from "vue";
import type { OutputFormat, VoiceProfileOptionView } from "./BuildSettings.types";
import { mapVoiceProfileErrorMessage } from "../voiceProfileErrors";

const props = defineProps<{
  voiceProfiles: readonly VoiceProfileOptionView[];
  createBuildRequest: (input: { outputFormats: OutputFormat[]; voiceProfileId?: string }) => Promise<unknown>;
  startJob: (buildRequestId: string) => Promise<unknown>;
}>();

const selectedFormats = reactive<Record<OutputFormat, boolean>>({ mp3: false, text: false });
const selectedVoiceProfileId = ref("");
const submitError = ref("");
const showApprovalLink = ref(false);
const voiceProfileClearedNotice = ref(false);

const mp3Selected = computed(() => selectedFormats.mp3);

/** 12.2節: 選択肢は常にこのProjectのapproved VoiceProfileだけ(draft/archivedは出さない)。 */
const approvedVoiceProfiles = computed(() => props.voiceProfiles.filter((profile) => profile.status === "approved"));

/** 13.2節: text-only時はVoiceProfile欄を非表示にせず、disabledのグレー表示にする。 */
const voiceProfileSelectDisabled = computed(() => !mp3Selected.value);

const isSubmitEnabled = computed(() => {
  const anyFormatSelected = selectedFormats.mp3 || selectedFormats.text;
  if (!anyFormatSelected) {
    return false;
  }
  if (selectedFormats.mp3 && !selectedVoiceProfileId.value) {
    return false;
  }
  return true;
});

/** 15節: 選択中のProfileが(archive等で)approved一覧から消えたら選択を解除し、Buildを禁止する。 */
watch(approvedVoiceProfiles, (profiles) => {
  if (!selectedVoiceProfileId.value) {
    return;
  }
  const stillValid = profiles.some((profile) => profile.voiceProfileId === selectedVoiceProfileId.value);
  if (!stillValid) {
    selectedVoiceProfileId.value = "";
    voiceProfileClearedNotice.value = true;
  }
});

function toggleFormat(format: OutputFormat): void {
  selectedFormats[format] = !selectedFormats[format];
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
      // TASK-VOICE-PROFILE-UI-001: voiceProfileIdには必ずvoice_profiles.voice_profile_idを送る
      // (旧実装の不整合: 生のspeaker_idをそのまま送っていた問題の是正)。
      voiceProfileId: selectedFormats.mp3 ? selectedVoiceProfileId.value : undefined,
    })) as { buildRequestId: string };
    await props.startJob(buildRequest.buildRequestId);
  } catch (err) {
    submitError.value = mapVoiceProfileErrorMessage(err);
    const rawMessage = err instanceof Error ? err.message : String(err);
    if (rawMessage.includes("approval_gate_not_satisfied")) {
      showApprovalLink.value = true;
    }
  }
}

defineExpose({ isSubmitEnabled, voiceProfileSelectDisabled, submitBuild, approvedVoiceProfiles });
</script>

<template>
  <section aria-label="出力・声設定">
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

    <label for="voice-profile-select">音声設定</label>
    <select
      id="voice-profile-select"
      v-model="selectedVoiceProfileId"
      data-testid="voice-profile-select"
      :disabled="voiceProfileSelectDisabled"
    >
      <option value="" disabled>音声設定を選択</option>
      <option v-for="profile in approvedVoiceProfiles" :key="profile.voiceProfileId" :value="profile.voiceProfileId">
        {{ profile.name }}
      </option>
    </select>
    <p v-if="voiceProfileSelectDisabled" data-testid="voice-profile-select-disabled-note">
      音声を出力しないため使用しません
    </p>
    <p v-else-if="approvedVoiceProfiles.length === 0" data-testid="voice-profile-none-available">
      利用可能な音声設定がありません。Project画面で音声設定を追加し、「利用可能にする」を実行してください。
    </p>
    <p v-if="voiceProfileClearedNotice" role="alert" data-testid="voice-profile-cleared-notice">
      選択していた音声設定は現在利用できません。別の音声設定を選択してください。
    </p>

    <p v-if="submitError" role="alert" data-testid="submit-error">{{ submitError }}</p>
    <a v-if="showApprovalLink" href="#" data-testid="approval-link">承認画面へ</a>

    <button type="button" data-testid="submit-button" :disabled="!isSubmitEnabled" @click="submitBuild">制作開始</button>
  </section>
</template>
