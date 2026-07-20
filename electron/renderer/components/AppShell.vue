<script setup lang="ts">
/**
 * electron/renderer/components/AppShell.vue — 公開契約: 共通shell.
 *
 * Contract: docs/test-cases/TASK-UI-005-renderer-state-routing-errors-and-accessibility.md
 * Spec: docs/screens/README.md
 */
import { nextTick, ref, watch } from "vue";
import { NAVIGATION_SCREENS, type ScreenId } from "../router";
import type { UserFacingError } from "../stores/app";

const props = defineProps<{
  currentScreen: ScreenId;
  loading: boolean;
  error: UserFacingError | null;
  navigate: (screen: ScreenId) => void;
}>();

const SCREEN_LABELS: Record<ScreenId, string> = {
  "projects-list": "Project一覧",
  "project-workspace": "workspace",
  "build-settings": "出力・声設定",
  jobs: "Job進捗",
  artifacts: "成果物",
};

const errorSummaryRef = ref<HTMLElement | null>(null);

// TC-UI-005-02: validation errorが発生したらerror summaryへfocusを移動する。
watch(
  () => props.error,
  async (error) => {
    if (error) {
      await nextTick();
      errorSummaryRef.value?.focus();
    }
  },
  { immediate: true },
);

defineExpose({ SCREEN_LABELS });
</script>

<template>
  <div aria-label="Walkwise">
    <nav data-testid="main-nav" aria-label="主要navigation">
      <button
        v-for="screen in NAVIGATION_SCREENS"
        :key="screen"
        type="button"
        :data-testid="`nav-${screen}`"
        :aria-current="screen === currentScreen ? 'page' : undefined"
        @click="navigate(screen)"
      >
        {{ SCREEN_LABELS[screen] }}
      </button>
    </nav>

    <div v-if="loading" data-testid="global-skeleton" role="status" aria-live="polite">読み込み中…</div>

    <div
      v-if="error"
      ref="errorSummaryRef"
      data-testid="error-summary"
      role="alert"
      tabindex="-1"
      aria-describedby="error-technical-detail"
    >
      <p data-testid="error-message">{{ error.message }}</p>
      <details v-if="error.technicalDetail" id="error-technical-detail" data-testid="error-technical-detail">
        <summary>技術detail</summary>
        <pre>{{ error.technicalDetail }}</pre>
      </details>
    </div>

    <main data-testid="main-content">
      <slot />
    </main>
  </div>
</template>
