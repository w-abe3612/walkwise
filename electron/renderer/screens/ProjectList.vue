<script setup lang="ts">
/**
 * electron/renderer/screens/ProjectList.vue — 公開契約: Project list/create UI.
 *
 * Contract: docs/test-cases/TASK-UI-001-project-list-and-create-screen.md
 * Spec: docs/screens/01-project-list-and-create.md
 */
import { computed, onMounted, reactive, ref } from "vue";
import { createProject, listProjects, type CreateProjectFormInput, type ProjectSummaryDto } from "../api/projects";

type LoadState = "loading" | "success" | "error" | "empty";

const SOURCE_STRATEGY_OPTIONS = ["upload_files", "manual_notes", "external_links"] as const;

const projects = ref<ProjectSummaryDto[]>([]);
const loadState = ref<LoadState>("loading");
const loadErrorMessage = ref("");

const form = reactive({
  title: "",
  domain: "",
  purpose: "",
  usagePurpose: "personal_learning",
  targetAudienceDescription: "",
  sourceStrategySet: {} as Record<string, boolean>,
});

const createError = ref("");
const creating = ref(false);

const selectedSourceStrategies = computed(() =>
  SOURCE_STRATEGY_OPTIONS.filter((option) => form.sourceStrategySet[option]),
);

const isFormValid = computed(() => {
  return (
    form.title.trim().length > 0 &&
    form.domain.trim().length > 0 &&
    form.purpose.trim().length > 0 &&
    form.usagePurpose.trim().length > 0 &&
    form.targetAudienceDescription.trim().length > 0 &&
    selectedSourceStrategies.value.length > 0
  );
});

async function loadProjects(): Promise<void> {
  loadState.value = "loading";
  try {
    const result = await listProjects();
    projects.value = [...result.projects];
    loadState.value = result.projects.length === 0 ? "empty" : "success";
  } catch (err) {
    loadErrorMessage.value = err instanceof Error ? err.message : String(err);
    loadState.value = "error";
  }
}

async function submitCreate(): Promise<void> {
  if (!isFormValid.value || creating.value) {
    return;
  }
  creating.value = true;
  createError.value = "";
  try {
    const input: CreateProjectFormInput = {
      title: form.title,
      domain: form.domain,
      purpose: form.purpose,
      usagePurpose: form.usagePurpose,
      targetAudienceDescription: form.targetAudienceDescription,
      sourceStrategy: selectedSourceStrategies.value,
    };
    await createProject(input);
    form.title = "";
    form.domain = "";
    form.purpose = "";
    form.targetAudienceDescription = "";
    form.sourceStrategySet = {};
    await loadProjects();
  } catch (err) {
    createError.value = err instanceof Error ? err.message : String(err);
  } finally {
    creating.value = false;
  }
}

function handleFormKeydown(event: KeyboardEvent): void {
  if (event.key === "Enter" && isFormValid.value && !creating.value) {
    event.preventDefault();
    void submitCreate();
  }
}

function toggleSourceStrategy(option: string): void {
  form.sourceStrategySet = { ...form.sourceStrategySet, [option]: !form.sourceStrategySet[option] };
}

onMounted(() => {
  void loadProjects();
});

/** TASK-REVIEW-001: Project選択後にworkspace画面へ遷移するための橋渡し(呼び出し側がAppの
 * navigationへ結線する)。 */
const emit = defineEmits<{ (event: "open-project", projectId: string): void }>();

defineExpose({ loadProjects, submitCreate, isFormValid });
</script>

<template>
  <section aria-label="Project一覧">
    <h1>Project</h1>

    <div v-if="loadState === 'loading'" data-testid="skeleton" role="status">読み込み中…</div>

    <div v-else-if="loadState === 'error'" data-testid="error-summary" role="alert">
      <p>{{ loadErrorMessage }}</p>
      <button type="button" data-testid="retry-button" @click="loadProjects">再試行</button>
    </div>

    <div v-else-if="loadState === 'empty'" data-testid="empty-state">
      <p>最初のプロジェクトを作成しましょう。</p>
    </div>

    <ul v-else data-testid="project-list">
      <li v-for="project in projects" :key="project.projectId" data-testid="project-item">
        <span>{{ project.title }}</span>
        <span>{{ project.planningStage }}</span>
        <span>{{ project.updatedAt }}</span>
        <button type="button" data-testid="open-project-button" @click="emit('open-project', project.projectId)">
          開く
        </button>
      </li>
    </ul>

    <form data-testid="create-form" @keydown="handleFormKeydown" @submit.prevent="submitCreate">
      <label>
        タイトル
        <input v-model="form.title" data-testid="field-title" type="text" tabindex="1" />
      </label>
      <label>
        ドメイン
        <input v-model="form.domain" data-testid="field-domain" type="text" tabindex="2" />
      </label>
      <label>
        目的
        <textarea v-model="form.purpose" data-testid="field-purpose" tabindex="3"></textarea>
      </label>
      <label>
        利用目的
        <input v-model="form.usagePurpose" data-testid="field-usage-purpose" type="text" tabindex="4" />
      </label>
      <label>
        想定読者
        <input v-model="form.targetAudienceDescription" data-testid="field-target-audience" type="text" tabindex="5" />
      </label>
      <fieldset data-testid="field-source-strategy">
        <label v-for="option in SOURCE_STRATEGY_OPTIONS" :key="option">
          <input
            type="checkbox"
            :checked="!!form.sourceStrategySet[option]"
            tabindex="6"
            @change="toggleSourceStrategy(option)"
          />
          {{ option }}
        </label>
      </fieldset>
      <p v-if="createError" role="alert" data-testid="create-error">{{ createError }}</p>
      <button type="submit" data-testid="submit-button" tabindex="7" :disabled="!isFormValid || creating">作成</button>
    </form>
  </section>
</template>
