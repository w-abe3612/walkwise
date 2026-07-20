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
});
