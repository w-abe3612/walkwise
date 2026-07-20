/**
 * electron/renderer/stores/app.ts — 公開契約: global UI state.
 *
 * Contract: docs/test-cases/TASK-UI-005-renderer-state-routing-errors-and-accessibility.md
 * Spec: docs/screens/README.md, 各画面のempty/loading/success/error状態(7節)
 */

/** 利用者向け要約messageと技術detailを分離して保持する(7節: 日本語利用者message/technical detail分離)。 */
export interface UserFacingError {
  readonly message: string;
  readonly technicalDetail?: string;
}

export interface AppState {
  readonly loading: boolean;
  readonly currentProjectId: string | null;
  readonly error: UserFacingError | null;
}

export class AppStateValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

function freshState(): AppState {
  return { loading: false, currentProjectId: null, error: null };
}

/** loading/error/current projectを一元管理する。 */
export class AppStore {
  private state: AppState = freshState();

  getState(): AppState {
    return this.state;
  }

  setLoading(loading: boolean): void {
    this.state = { ...this.state, loading };
  }

  setCurrentProject(projectId: string | null): void {
    this.state = { ...this.state, currentProjectId: projectId };
  }

  /** errorは利用者向けmessage必須。技術detailは任意で折りたたみ表示用に分離保持する。 */
  setError(error: unknown, technicalDetail?: string): void {
    const message = error instanceof Error ? error.message : String(error ?? "");
    if (!message.trim()) {
      throw new AppStateValidationError("validation_error", "error message is required");
    }
    this.state = { ...this.state, error: { message, technicalDetail } };
  }

  clearError(): void {
    this.state = { ...this.state, error: null };
  }
}
