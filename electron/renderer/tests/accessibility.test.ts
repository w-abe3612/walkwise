/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-005: error-summary focus management, project context
 * preservation, loading skeleton, required-input-missing on the app store.
 * Contract: docs/test-cases/TASK-UI-005-renderer-state-routing-errors-and-accessibility.md
 * Release scope: MVP.
 */

import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import { resolveNavigation } from "../router";
import { AppStore, AppStateValidationError } from "../stores/app";
import AppShell from "../components/AppShell.vue";
import ProjectWorkspace from "../screens/ProjectWorkspace.vue";

function mountProjectWorkspaceForModal() {
  return mount(ProjectWorkspace, {
    attachTo: document.body,
    props: {
      sources: [],
      approvals: [],
      registerSource: vi.fn(),
      retrySource: vi.fn(),
      approve: vi.fn(),
      requestChanges: vi.fn(),
      selectSourceFile: vi.fn(),
      voiceProfiles: [],
      voiceEngineHealth: null,
      voiceSpeakers: [{ speakerId: "3", displayName: "四国めたん", styleIds: [] }],
      createVoiceProfile: vi.fn(),
      updateVoiceProfile: vi.fn(),
      approveVoiceProfile: vi.fn(),
      archiveVoiceProfile: vi.fn(),
    },
  });
}

describe("TASK-UI-005 Renderer共通state・navigation・error・アクセシビリティ", () => {
  test("TC-UI-005-02: focus/error summary [unit/P0]", async () => {
    const store = new AppStore();
    store.setError(new Error("入力内容を確認してください。"));

    const wrapper = mount(AppShell, {
      attachTo: document.body,
      props: { currentScreen: "projects-list", loading: false, error: store.getState().error, navigate: vi.fn() },
    });
    await flushPromises();

    const errorSummary = wrapper.get('[data-testid="error-summary"]');
    expect(errorSummary.attributes("role")).toBe("alert");
    // error summaryへfocusが移動している
    expect(document.activeElement).toBe(errorSummary.element);
    // ariaで技術detailと関連付けられている
    expect(errorSummary.attributes("aria-describedby")).toBeTruthy();

    wrapper.unmount();
  });

  test("TC-UI-005-04: Project context [unit/P1]", () => {
    // 有効なProject文脈付きでProject-scoped画面へ遷移する場合はそのまま維持される
    const result = resolveNavigation({ screen: "project-workspace", projectId: "proj-1" });
    expect(result).toEqual({ screen: "project-workspace", projectId: "proj-1" });
  });

  test("TC-UI-005-06: loading skeleton [unit/P1]", () => {
    const wrapper = mount(AppShell, {
      props: { currentScreen: "projects-list", loading: true, error: null, navigate: vi.fn() },
    });

    const skeleton = wrapper.get('[data-testid="global-skeleton"]');
    expect(skeleton.attributes("role")).toBe("status");
  });

  test("TC-UI-005-08: 必須入力欠落 [unit/P0]", () => {
    const store = new AppStore();

    expect(() => store.setError("")).toThrow(AppStateValidationError);
    expect(store.getState().error).toBeNull(); // 副作用(state変更)は発生していない

    expect(() => resolveNavigation(undefined as never)).toThrow();
    expect(() => resolveNavigation({ screen: "" })).toThrow();
  });

  test("TC-VOICE-PROFILE-UI-001-A11Y-01: VoiceProfile modalが開いた時、最初の入力欄へfocusが移動する", async () => {
    const wrapper = mountProjectWorkspaceForModal();
    await wrapper.get('[data-testid="voice-profile-add-button"]').trigger("click");
    await flushPromises();

    expect(document.activeElement).toBe(wrapper.get('[data-testid="voice-profile-name-input"]').element);
    wrapper.unmount();
  });

  test("TC-VOICE-PROFILE-UI-001-A11Y-02: labelとinputがforで関連付けられている", async () => {
    const wrapper = mountProjectWorkspaceForModal();
    await wrapper.get('[data-testid="voice-profile-add-button"]').trigger("click");

    const nameInput = wrapper.get('[data-testid="voice-profile-name-input"]');
    const nameInputId = nameInput.attributes("id")!;
    expect(wrapper.find(`label[for="${nameInputId}"]`).exists()).toBe(true);

    const speakerSelect = wrapper.get('[data-testid="voice-profile-speaker-select"]');
    const speakerSelectId = speakerSelect.attributes("id")!;
    expect(wrapper.find(`label[for="${speakerSelectId}"]`).exists()).toBe(true);

    wrapper.unmount();
  });

  test("TC-VOICE-PROFILE-UI-001-A11Y-03: Tabキーでmodal内をfocus trapし、外へは出ない", async () => {
    const wrapper = mountProjectWorkspaceForModal();
    await wrapper.get('[data-testid="voice-profile-add-button"]').trigger("click");
    await flushPromises();

    const modal = wrapper.get('[data-testid="voice-profile-modal"]');
    const saveButton = wrapper.get('[data-testid="voice-profile-modal-save"]').element as HTMLElement;
    saveButton.focus();
    expect(document.activeElement).toBe(saveButton);

    // 最後の要素でTabを押すと、modal外へ出ず先頭へ戻る(focus trap)。
    await modal.trigger("keydown", { key: "Tab" });
    expect(modal.element.contains(document.activeElement)).toBe(true);

    wrapper.unmount();
  });
});
