/**
 * electron/renderer/main.ts — 公開契約: renderer bootstrap.
 *
 * Contract: docs/test-cases/TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md
 * Spec: docs/specifications/20-electron-desktop-architecture.md(5.5節)
 *
 * 各画面(screens/router/store)の実装はTASK-UI-001〜005やTASK-DESKTOP-003の対象範囲であり、
 * 本タスクはNode APIへ直接アクセスせずVueアプリを起動する最小限のbootstrapのみを扱う。
 */

import { createApp, defineComponent, h, type App } from "vue";

export interface VueAppLike {
  mount(selector: string): unknown;
}

export interface MainOptions {
  readonly mountSelector: string;
  readonly rootComponent?: unknown;
  readonly appFactory?: (root: unknown) => VueAppLike;
}

const PlaceholderRoot = defineComponent({
  name: "WalkwiseRendererRoot",
  render() {
    return h("div", { id: "walkwise-root" });
  },
});

function defaultAppFactory(root: unknown): VueAppLike {
  return createApp(root as Parameters<typeof createApp>[0]) as unknown as App & VueAppLike;
}

/** Node APIへ直接アクセスせずVue rendererを起動する。 */
export function main(options: MainOptions): unknown {
  if (!options) {
    throw new Error("options is required");
  }
  if (!options.mountSelector) {
    throw new Error("mountSelector is required");
  }

  const root = options.rootComponent ?? PlaceholderRoot;
  const factory = options.appFactory ?? defaultAppFactory;
  const app = factory(root);
  return app.mount(options.mountSelector);
}
