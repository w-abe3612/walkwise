/**
 * electron/renderer/router.ts — 公開契約: navigation state.
 *
 * Contract: docs/test-cases/TASK-UI-005-renderer-state-routing-errors-and-accessibility.md
 * Spec: docs/screens/README.md(6節), 01〜05の各画面route定義
 */

export type ScreenId = "projects-list" | "project-workspace" | "build-settings" | "jobs" | "artifacts";

/** docs/screens/README.md 6節・01〜05の承認済み5画面(この順序で固定)。 */
export const NAVIGATION_SCREENS: readonly ScreenId[] = [
  "projects-list",
  "project-workspace",
  "build-settings",
  "jobs",
  "artifacts",
];

const VALID_SCREENS = new Set<string>(NAVIGATION_SCREENS);

/** projects-list以外は`:project_id`を伴うrouteのため、Project文脈が必須。 */
const SCREENS_REQUIRING_PROJECT = new Set<ScreenId>(["project-workspace", "build-settings", "jobs", "artifacts"]);

const DEFAULT_SCREEN: ScreenId = "projects-list";

export interface NavigationState {
  readonly screen: ScreenId;
  readonly projectId: string | null;
}

export interface NavigateOptions {
  readonly screen: string;
  readonly projectId?: string | null;
}

export class NavigationValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

/** 5画面とProject文脈を決定的に遷移する。無効routeやProject文脈欠落は既定画面へ戻す。 */
export function resolveNavigation(options: NavigateOptions): NavigationState {
  if (!options) {
    throw new NavigationValidationError("validation_error", "options is required");
  }
  if (typeof options.screen !== "string" || !options.screen) {
    throw new NavigationValidationError("validation_error", "screen is required");
  }

  if (!VALID_SCREENS.has(options.screen)) {
    return { screen: DEFAULT_SCREEN, projectId: null };
  }
  const screen = options.screen as ScreenId;
  const projectId = options.projectId ?? null;

  if (SCREENS_REQUIRING_PROJECT.has(screen) && !projectId) {
    // Project文脈がない状態でProject-scoped画面へは遷移できないため、安全な既定画面へ戻す。
    return { screen: DEFAULT_SCREEN, projectId: null };
  }

  return { screen, projectId };
}
