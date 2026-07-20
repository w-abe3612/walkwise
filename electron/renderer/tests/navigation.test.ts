/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-005: navigation state, keyboard-only operability,
 * typed screen enumeration, message/technical-detail separation, re-execution determinism.
 * Contract: docs/test-cases/TASK-UI-005-renderer-state-routing-errors-and-accessibility.md
 * Release scope: MVP.
 */

import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import { NAVIGATION_SCREENS, resolveNavigation } from "../router";
import { AppStore } from "../stores/app";
import AppShell from "../components/AppShell.vue";

describe("TASK-UI-005 Renderer共通state・navigation・error・アクセシビリティ", () => {
  test("TC-UI-005-01: 5画面navigation [unit/P0]", () => {
    // 無効なscreen名は既定画面へ戻す
    expect(resolveNavigation({ screen: "unknown-screen" })).toEqual({ screen: "projects-list", projectId: null });

    // Project文脈がないままProject-scoped画面へ遷移しようとした場合も既定画面へ戻す
    expect(resolveNavigation({ screen: "build-settings" })).toEqual({ screen: "projects-list", projectId: null });
    expect(resolveNavigation({ screen: "build-settings", projectId: null })).toEqual({
      screen: "projects-list",
      projectId: null,
    });

    // projects-listはProject文脈不要
    expect(resolveNavigation({ screen: "projects-list" })).toEqual({ screen: "projects-list", projectId: null });
  });

  test("TC-UI-005-03: keyboard only [unit/P0]", async () => {
    const navigate = vi.fn();
    const wrapper = mount(AppShell, {
      props: { currentScreen: "projects-list", loading: false, error: null, navigate },
    });

    // 主要操作(navigation)はすべて<button>要素であり、mouse専用handlerに依存しない
    for (const screen of NAVIGATION_SCREENS) {
      const button = wrapper.get(`[data-testid="nav-${screen}"]`);
      expect(button.element.tagName.toLowerCase()).toBe("button");
      expect((button.element as HTMLButtonElement).tabIndex).not.toBe(-1);
    }

    await wrapper.get('[data-testid="nav-jobs"]').trigger("click");
    expect(navigate).toHaveBeenCalledWith("jobs");
  });

  test("TC-UI-005-05: typed API wrapper [integration_mock/P1]", () => {
    // 承認済み5画面(docs/screens/README.md 6節)と完全一致し、順序も固定である
    expect(NAVIGATION_SCREENS).toEqual(["projects-list", "project-workspace", "build-settings", "jobs", "artifacts"]);
  });

  test("TC-UI-005-07: 日本語利用者message/technical detail分離 [unit/P1]", () => {
    const store = new AppStore();
    store.setError(new Error("Projectを読み込めませんでした。"), "Traceback (most recent call last): ...");

    const state = store.getState();
    expect(state.error?.message).toBe("Projectを読み込めませんでした。");
    expect(state.error?.technicalDetail).toContain("Traceback");

    const wrapper = mount(AppShell, {
      props: { currentScreen: "projects-list", loading: false, error: state.error, navigate: vi.fn() },
    });

    expect(wrapper.get('[data-testid="error-message"]').text()).toBe("Projectを読み込めませんでした。");
    // 技術detailは折り畳み(<details>)内にのみ存在し、summaryの外へそのまま出さない
    const details = wrapper.get('[data-testid="error-technical-detail"]');
    expect(details.element.tagName.toLowerCase()).toBe("details");
    expect((details.element as HTMLDetailsElement).open).toBe(false);
  });

  test("TC-UI-005-09: 再実行時の決定性 [unit/P1]", () => {
    const first = resolveNavigation({ screen: "jobs", projectId: "proj-1" });
    const second = resolveNavigation({ screen: "jobs", projectId: "proj-1" });
    expect(first).toEqual(second);
  });
});
