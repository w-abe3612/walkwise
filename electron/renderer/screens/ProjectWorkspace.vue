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
import { computed, nextTick, reactive, ref } from "vue";
import type {
  ApprovalItem,
  SourceItem,
  VoiceEngineHealthView,
  VoiceProfileFormInput,
  VoiceProfileItem,
  VoiceProfileStatus,
  VoiceSpeakerOptionView,
} from "./ProjectWorkspace.types";
import { mapVoiceProfileErrorMessage } from "../voiceProfileErrors";

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
  voiceProfiles: readonly VoiceProfileItem[];
  voiceEngineHealth: VoiceEngineHealthView | null;
  voiceSpeakers: readonly VoiceSpeakerOptionView[];
  createVoiceProfile: (input: VoiceProfileFormInput) => Promise<void>;
  updateVoiceProfile: (
    voiceProfileId: string,
    input: Partial<VoiceProfileFormInput> & { status?: VoiceProfileStatus },
  ) => Promise<void>;
  approveVoiceProfile: (voiceProfileId: string) => Promise<void>;
  archiveVoiceProfile: (voiceProfileId: string) => Promise<void>;
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

// --- VoiceProfile management (TASK-VOICE-PROFILE-UI-001) ---
// 第6画面は追加せず、既存のProject Workspace内へ折り畳み式sectionとして統合する。

/** 利用者へstatus値をそのまま見せず、日本語文言へ変換する。 */
const VOICE_PROFILE_STATUS_LABELS: Record<VoiceProfileStatus, string> = {
  draft: "下書き",
  approved: "利用可能",
  archived: "アーカイブ済み",
};

const STATUS_ORDER: Record<VoiceProfileStatus, number> = { approved: 0, draft: 1, archived: 2 };

/** 推奨表示順: approved→draft→archived、同一status内はname順。 */
const sortedVoiceProfiles = computed(() =>
  [...props.voiceProfiles].sort((a, b) => {
    const statusDiff = STATUS_ORDER[a.status] - STATUS_ORDER[b.status];
    return statusDiff !== 0 ? statusDiff : a.name.localeCompare(b.name, "ja");
  }),
);

const approvedVoiceProfiles = computed(() => props.voiceProfiles.filter((p) => p.status === "approved"));
const draftVoiceProfiles = computed(() => props.voiceProfiles.filter((p) => p.status === "draft"));
const archivedVoiceProfiles = computed(() => props.voiceProfiles.filter((p) => p.status === "archived"));

const hasNoVoiceProfiles = computed(() => props.voiceProfiles.length === 0);
/** 11.2節: 全件がdraftの場合(承認済みが0件かつarchivedも0件)。 */
const hasOnlyDraftVoiceProfiles = computed(
  () => !hasNoVoiceProfiles.value && approvedVoiceProfiles.value.length === 0 && archivedVoiceProfiles.value.length === 0,
);
/** 11.3節: 全件がarchivedの場合。 */
const hasOnlyArchivedVoiceProfiles = computed(
  () => !hasNoVoiceProfiles.value && approvedVoiceProfiles.value.length === 0 && draftVoiceProfiles.value.length === 0,
);

/** 5.1節: 内部IDだけを利用者向け表示にせず、表示名が取得できる場合はそちらを優先する。 */
function speakerDisplayName(profile: VoiceProfileItem): string {
  const speaker = props.voiceSpeakers.find((candidate) => candidate.speakerId === profile.speakerId);
  return speaker ? speaker.displayName : profile.speakerId;
}

const pendingApprove = reactive<Record<string, boolean>>({});
const pendingArchive = reactive<Record<string, boolean>>({});
const pendingArchiveConfirmation = reactive<Record<string, boolean>>({});
const voiceProfileSectionError = ref("");

/** 8節: 二重送信を防止しつつdraft→approvedへ変更する。 */
async function handleApproveClick(voiceProfileId: string): Promise<void> {
  if (pendingApprove[voiceProfileId]) return;
  pendingApprove[voiceProfileId] = true;
  voiceProfileSectionError.value = "";
  try {
    await props.approveVoiceProfile(voiceProfileId);
  } catch (err) {
    voiceProfileSectionError.value = mapVoiceProfileErrorMessage(err);
  } finally {
    pendingApprove[voiceProfileId] = false;
  }
}

function isArchiveConfirmVisible(voiceProfileId: string): boolean {
  return !!pendingArchiveConfirmation[voiceProfileId];
}

/** 9節: archiveは削除ではなく、実行前に確認を表示する(JobsAndArtifacts.vueのcancel確認と同じ二段階方式)。 */
async function handleArchiveClick(voiceProfileId: string): Promise<void> {
  if (!pendingArchiveConfirmation[voiceProfileId]) {
    pendingArchiveConfirmation[voiceProfileId] = true;
    return;
  }
  if (pendingArchive[voiceProfileId]) return;
  pendingArchiveConfirmation[voiceProfileId] = false;
  pendingArchive[voiceProfileId] = true;
  voiceProfileSectionError.value = "";
  try {
    await props.archiveVoiceProfile(voiceProfileId);
  } catch (err) {
    voiceProfileSectionError.value = mapVoiceProfileErrorMessage(err);
  } finally {
    pendingArchive[voiceProfileId] = false;
  }
}

// --- 作成・編集modal ---
type VoiceProfileModalMode = "create" | "edit" | null;

function defaultVoiceProfileForm(): VoiceProfileFormInput {
  return {
    name: "",
    engine: "voicevox",
    speakerId: "",
    styleId: "",
    speedScale: 1.0,
    pitchScale: 0.0,
    intonationScale: 1.0,
    volumeScale: 1.0,
    sentencePauseMs: 250,
    paragraphPauseMs: 600,
    sectionPauseMs: 1000,
    chapterPauseMs: 1500,
    settingsJson: "{}",
  };
}

const voiceProfileModalMode = ref<VoiceProfileModalMode>(null);
const voiceProfileModalError = ref("");
const voiceProfileModalSaving = ref(false);
const editingVoiceProfileId = ref<string | null>(null);
const voiceProfileModalRef = ref<HTMLElement | null>(null);
const voiceProfileFirstFieldRef = ref<HTMLElement | null>(null);
const voiceProfileModalTitleId = "voice-profile-modal-title";
const voiceProfileForm = reactive<VoiceProfileFormInput>(defaultVoiceProfileForm());

const selectedSpeakerStyleIds = computed(() => {
  const speaker = props.voiceSpeakers.find((candidate) => candidate.speakerId === voiceProfileForm.speakerId);
  return speaker ? speaker.styleIds : [];
});

async function focusVoiceProfileModal(): Promise<void> {
  await nextTick();
  (voiceProfileFirstFieldRef.value ?? voiceProfileModalRef.value)?.focus();
}

/** 6節: Build Settingsには新規作成ボタンを置かず、この画面からだけ開ける。 */
async function openCreateVoiceProfileModal(): Promise<void> {
  Object.assign(voiceProfileForm, defaultVoiceProfileForm());
  editingVoiceProfileId.value = null;
  voiceProfileModalError.value = "";
  voiceProfileModalMode.value = "create";
  await focusVoiceProfileModal();
}

/** 7.2節: archivedは編集不可(呼び出し元のbuttonもdisabledにしているが、防御的に再確認する)。 */
async function openEditVoiceProfileModal(profile: VoiceProfileItem): Promise<void> {
  if (profile.status === "archived") return;
  Object.assign(voiceProfileForm, {
    name: profile.name,
    engine: profile.engine,
    speakerId: profile.speakerId,
    styleId: profile.styleId ?? "",
    speedScale: profile.speedScale,
    pitchScale: profile.pitchScale,
    intonationScale: profile.intonationScale,
    volumeScale: profile.volumeScale,
    sentencePauseMs: profile.sentencePauseMs,
    paragraphPauseMs: profile.paragraphPauseMs,
    sectionPauseMs: profile.sectionPauseMs,
    chapterPauseMs: profile.chapterPauseMs,
    settingsJson: profile.settingsJson,
  });
  editingVoiceProfileId.value = profile.voiceProfileId;
  voiceProfileModalError.value = "";
  voiceProfileModalMode.value = "edit";
  await focusVoiceProfileModal();
}

function closeVoiceProfileModal(): void {
  voiceProfileModalMode.value = null;
  editingVoiceProfileId.value = null;
  voiceProfileModalError.value = "";
}

function focusableElements(container: HTMLElement): HTMLElement[] {
  return Array.from(
    container.querySelectorAll<HTMLElement>(
      'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
    ),
  );
}

/** 18.1節: Escapeで閉じる、Tab/Shift+Tabでmodal内をfocus trapする。 */
function handleVoiceProfileModalKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape") {
    event.preventDefault();
    closeVoiceProfileModal();
    return;
  }
  if (event.key !== "Tab" || !voiceProfileModalRef.value) return;
  const focusable = focusableElements(voiceProfileModalRef.value);
  if (focusable.length === 0) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function validateSettingsJson(value: string): string | null {
  let parsed: unknown;
  try {
    parsed = JSON.parse(value);
  } catch {
    return "詳細設定のJSON形式が正しくありません。";
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    return "詳細設定はJSON objectで入力してください。";
  }
  return null;
}

/** 6.3節: 新規作成はdraft、承認済み方針(編集後もapprovedを維持)によりeditはstatusを送らない。 */
async function submitVoiceProfileModal(): Promise<void> {
  if (voiceProfileModalSaving.value) return;
  if (!voiceProfileForm.name.trim()) {
    voiceProfileModalError.value = "名前を入力してください。";
    return;
  }
  if (!voiceProfileForm.speakerId) {
    voiceProfileModalError.value = "speakerを選択してください。";
    return;
  }
  const settingsJsonError = validateSettingsJson(voiceProfileForm.settingsJson);
  if (settingsJsonError) {
    voiceProfileModalError.value = settingsJsonError;
    return;
  }

  voiceProfileModalSaving.value = true;
  voiceProfileModalError.value = "";
  const payload: VoiceProfileFormInput = { ...voiceProfileForm, styleId: voiceProfileForm.styleId || undefined };
  try {
    if (voiceProfileModalMode.value === "create") {
      await props.createVoiceProfile(payload);
    } else if (voiceProfileModalMode.value === "edit" && editingVoiceProfileId.value) {
      await props.updateVoiceProfile(editingVoiceProfileId.value, payload);
    }
    closeVoiceProfileModal();
  } catch (err) {
    voiceProfileModalError.value = mapVoiceProfileErrorMessage(err);
  } finally {
    voiceProfileModalSaving.value = false;
  }
}

defineExpose({
  submitRequestChanges,
  selectAndRegisterFile,
  STATUS_LABELS,
  ALLOWED_MEDIA_TYPES,
  VOICE_PROFILE_STATUS_LABELS,
  sortedVoiceProfiles,
  hasNoVoiceProfiles,
  hasOnlyDraftVoiceProfiles,
  hasOnlyArchivedVoiceProfiles,
  speakerDisplayName,
  handleApproveClick,
  handleArchiveClick,
  isArchiveConfirmVisible,
  openCreateVoiceProfileModal,
  openEditVoiceProfileModal,
  closeVoiceProfileModal,
  submitVoiceProfileModal,
  validateSettingsJson,
});
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

    <h2>音声設定</h2>
    <section aria-label="音声設定" data-testid="voice-profile-section">
      <p v-if="hasNoVoiceProfiles" data-testid="voice-profile-empty">
        音声設定がまだありません。<br />
        MP3を作成するには、音声設定を追加して利用可能にしてください。
      </p>
      <p v-else-if="hasOnlyDraftVoiceProfiles" data-testid="voice-profile-draft-only">
        利用可能な音声設定がありません。<br />
        下書きの音声設定を確認し、「利用可能にする」を実行してください。
      </p>
      <p v-else-if="hasOnlyArchivedVoiceProfiles" data-testid="voice-profile-archived-only">
        利用可能な音声設定がありません。<br />
        新しい音声設定を追加してください。
      </p>

      <p v-if="voiceProfileSectionError" role="alert" data-testid="voice-profile-section-error">
        {{ voiceProfileSectionError }}
      </p>

      <ul data-testid="voice-profile-list">
        <li v-for="profile in sortedVoiceProfiles" :key="profile.voiceProfileId" data-testid="voice-profile-item">
          <span data-testid="voice-profile-name">{{ profile.name }}</span>
          <span data-testid="voice-profile-engine">{{ profile.engine }}</span>
          <span data-testid="voice-profile-speaker">{{ speakerDisplayName(profile) }}</span>
          <span v-if="profile.styleId" data-testid="voice-profile-style">{{ profile.styleId }}</span>
          <span data-testid="voice-profile-status">{{ VOICE_PROFILE_STATUS_LABELS[profile.status] }}</span>
          <span v-if="profile.updatedAt" data-testid="voice-profile-updated-at">{{ profile.updatedAt }}</span>

          <button
            type="button"
            data-testid="voice-profile-edit-button"
            :disabled="profile.status === 'archived'"
            @click="openEditVoiceProfileModal(profile)"
          >
            編集
          </button>
          <button
            v-if="profile.status === 'draft'"
            type="button"
            data-testid="voice-profile-approve-button"
            :disabled="pendingApprove[profile.voiceProfileId]"
            @click="handleApproveClick(profile.voiceProfileId)"
          >
            利用可能にする
          </button>
          <button
            v-if="profile.status !== 'archived'"
            type="button"
            data-testid="voice-profile-archive-button"
            :disabled="pendingArchive[profile.voiceProfileId]"
            @click="handleArchiveClick(profile.voiceProfileId)"
          >
            アーカイブ
          </button>
          <div
            v-if="isArchiveConfirmVisible(profile.voiceProfileId)"
            role="alertdialog"
            data-testid="voice-profile-archive-confirm"
          >
            <p>この音声設定をアーカイブしますか?<br />アーカイブ後は新しい音声作成には使用できません。</p>
            <button
              type="button"
              data-testid="voice-profile-archive-confirm-button"
              @click="handleArchiveClick(profile.voiceProfileId)"
            >
              アーカイブする
            </button>
          </div>
        </li>
      </ul>

      <button type="button" data-testid="voice-profile-add-button" @click="openCreateVoiceProfileModal">
        音声設定を追加
      </button>

      <div
        v-if="voiceProfileModalMode"
        ref="voiceProfileModalRef"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="voiceProfileModalTitleId"
        tabindex="-1"
        data-testid="voice-profile-modal"
        @keydown="handleVoiceProfileModalKeydown"
      >
        <h3 :id="voiceProfileModalTitleId">
          {{ voiceProfileModalMode === "create" ? "音声設定を追加" : "音声設定を編集" }}
        </h3>
        <button type="button" data-testid="voice-profile-modal-close" @click="closeVoiceProfileModal">閉じる</button>

        <p v-if="voiceEngineHealth && !voiceEngineHealth.available" role="alert" data-testid="voice-profile-engine-error">
          VOICEVOX Engineに接続できないため、speaker候補を取得できません。
        </p>

        <label for="voice-profile-name-input">名前</label>
        <input
          id="voice-profile-name-input"
          ref="voiceProfileFirstFieldRef"
          v-model="voiceProfileForm.name"
          type="text"
          data-testid="voice-profile-name-input"
        />

        <label for="voice-profile-speaker-select">speaker</label>
        <select id="voice-profile-speaker-select" v-model="voiceProfileForm.speakerId" data-testid="voice-profile-speaker-select">
          <option value="" disabled>speakerを選択</option>
          <option v-for="speaker in voiceSpeakers" :key="speaker.speakerId" :value="speaker.speakerId">
            {{ speaker.displayName }}
          </option>
        </select>

        <label for="voice-profile-style-select">style</label>
        <select id="voice-profile-style-select" v-model="voiceProfileForm.styleId" data-testid="voice-profile-style-select">
          <option value="">(なし)</option>
          <option v-for="styleId in selectedSpeakerStyleIds" :key="styleId" :value="styleId">{{ styleId }}</option>
        </select>

        <label for="voice-profile-speed-input">速度</label>
        <input
          id="voice-profile-speed-input"
          v-model.number="voiceProfileForm.speedScale"
          type="range"
          min="0.5"
          max="2.0"
          step="0.05"
          data-testid="voice-profile-speed-input"
        />

        <label for="voice-profile-pitch-input">音高</label>
        <input
          id="voice-profile-pitch-input"
          v-model.number="voiceProfileForm.pitchScale"
          type="range"
          min="-0.15"
          max="0.15"
          step="0.01"
          data-testid="voice-profile-pitch-input"
        />

        <label for="voice-profile-intonation-input">抑揚</label>
        <input
          id="voice-profile-intonation-input"
          v-model.number="voiceProfileForm.intonationScale"
          type="range"
          min="0"
          max="2.0"
          step="0.05"
          data-testid="voice-profile-intonation-input"
        />

        <label for="voice-profile-volume-input">音量</label>
        <input
          id="voice-profile-volume-input"
          v-model.number="voiceProfileForm.volumeScale"
          type="range"
          min="0.1"
          max="2.0"
          step="0.05"
          data-testid="voice-profile-volume-input"
        />

        <label for="voice-profile-sentence-pause-input">文末の間(ms)</label>
        <input
          id="voice-profile-sentence-pause-input"
          v-model.number="voiceProfileForm.sentencePauseMs"
          type="number"
          min="0"
          data-testid="voice-profile-sentence-pause-input"
        />

        <label for="voice-profile-paragraph-pause-input">段落の間(ms)</label>
        <input
          id="voice-profile-paragraph-pause-input"
          v-model.number="voiceProfileForm.paragraphPauseMs"
          type="number"
          min="0"
          data-testid="voice-profile-paragraph-pause-input"
        />

        <label for="voice-profile-section-pause-input">節の間(ms)</label>
        <input
          id="voice-profile-section-pause-input"
          v-model.number="voiceProfileForm.sectionPauseMs"
          type="number"
          min="0"
          data-testid="voice-profile-section-pause-input"
        />

        <label for="voice-profile-chapter-pause-input">章の間(ms)</label>
        <input
          id="voice-profile-chapter-pause-input"
          v-model.number="voiceProfileForm.chapterPauseMs"
          type="number"
          min="0"
          data-testid="voice-profile-chapter-pause-input"
        />

        <label for="voice-profile-settings-json-input">詳細設定(JSON)</label>
        <textarea
          id="voice-profile-settings-json-input"
          v-model="voiceProfileForm.settingsJson"
          data-testid="voice-profile-settings-json-input"
        ></textarea>

        <p v-if="voiceProfileModalError" role="alert" data-testid="voice-profile-modal-error">
          {{ voiceProfileModalError }}
        </p>

        <button type="button" data-testid="voice-profile-modal-cancel" @click="closeVoiceProfileModal">Cancel</button>
        <button
          type="button"
          data-testid="voice-profile-modal-save"
          :disabled="voiceProfileModalSaving"
          @click="submitVoiceProfileModal"
        >
          保存
        </button>
      </div>
    </section>
  </section>
</template>
