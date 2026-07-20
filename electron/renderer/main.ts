/**
 * electron/renderer/main.ts — 公開契約: renderer bootstrap.
 *
 * Contract: docs/test-cases/TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md
 * Spec: docs/specifications/20-electron-desktop-architecture.md(5.5節)
 *
 * TASK-REVIEW-001監査2.4節: 既定rootComponentは、以前は空のplaceholder divを
 * mountするだけで、`window.walkwise`と結線されたどの画面も表示されなかった。
 * 既定を`App.vue`(router/store/5画面/window.walkwise APIを実際に結線するroot)へ
 * 変更する。Node APIへ直接アクセスしない、という本fileの契約自体は変わらない。
 */

import { createApp, type App } from "vue";

import AppRoot from "./App.vue";

export interface VueAppLike {
  mount(selector: string): unknown;
}

export interface MainOptions {
  readonly mountSelector: string;
  readonly rootComponent?: unknown;
  readonly appFactory?: (root: unknown) => VueAppLike;
}

function defaultAppFactory(root: unknown): VueAppLike {
  return createApp(root as Parameters<typeof createApp>[0]) as unknown as App & VueAppLike;
}

/** Node APIへ直接アクセスせずVue rendererを起動する(既定rootは`App.vue`)。 */
export function main(options: MainOptions): unknown {
  if (!options) {
    throw new Error("options is required");
  }
  if (!options.mountSelector) {
    throw new Error("mountSelector is required");
  }

  const root = options.rootComponent ?? AppRoot;
  const factory = options.appFactory ?? defaultAppFactory;
  const app = factory(root);
  return app.mount(options.mountSelector);
}

main({ mountSelector: "#app" });
