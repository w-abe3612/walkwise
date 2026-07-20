/**
 * electron/main/worker_manager.ts — 公開契約: WorkerManager.start/stop/request.
 *
 * Contract: docs/test-cases/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md
 * Spec: docs/specifications/21-electron-python-worker-interface.md(5.2〜5.5節)
 */

export interface WritableStreamLike {
  write(chunk: string): void;
}

export interface ReadableStreamLike {
  on(event: "data", listener: (chunk: Buffer | string) => void): void;
}

export interface ChildProcessLike {
  readonly stdin: WritableStreamLike;
  readonly stdout: ReadableStreamLike;
  readonly stderr: ReadableStreamLike;
  on(event: "exit", listener: (code: number | null) => void): void;
  on(event: "error", listener: (err: Error) => void): void;
  kill(signal?: string): void;
}

export type SpawnFn = (command: string, args: readonly string[]) => ChildProcessLike;

export interface WorkerEventLike {
  readonly event: string;
  readonly job_id?: string;
  readonly [key: string]: unknown;
}

const TERMINAL_EVENTS = new Set(["completed", "error", "cancelled"]);

export interface WorkerManagerOptions {
  readonly command: string;
  readonly args?: readonly string[];
  /** 実subprocess起動は本タスクの通常テストで使わないため、呼び出し側が必ず注入する。 */
  readonly spawn: SpawnFn;
  readonly requestTimeoutMs?: number;
  readonly onStderr?: (chunk: string) => void;
  readonly generateJobId?: () => string;
}

export interface WorkerRequestResult {
  readonly jobId: string;
  readonly events: readonly WorkerEventLike[];
  readonly terminalEvent: WorkerEventLike;
}

interface PendingRequest {
  readonly jobId: string;
  readonly events: WorkerEventLike[];
  readonly resolve: (result: WorkerRequestResult) => void;
  readonly reject: (error: Error) => void;
  timeoutHandle?: ReturnType<typeof setTimeout>;
}

let jobIdCounter = 0;
function defaultGenerateJobId(): string {
  jobIdCounter += 1;
  return `worker-req-${jobIdCounter}`;
}

/** Python worker subprocessとJSON Lines(21-electron-python-worker-interface.md)を管理する。 */
export class WorkerManager {
  private readonly command: string;
  private readonly args: readonly string[];
  private readonly spawnFn: SpawnFn;
  private readonly requestTimeoutMs: number;
  private readonly onStderr: (chunk: string) => void;
  private readonly generateJobId: () => string;

  private child: ChildProcessLike | null = null;
  private stopped = true;
  private stdoutBuffer = "";
  private readonly pending = new Map<string, PendingRequest>();

  constructor(options: WorkerManagerOptions) {
    if (!options) {
      throw new Error("options is required");
    }
    if (!options.command) {
      throw new Error("command is required");
    }
    if (!options.spawn) {
      throw new Error("spawn is required");
    }

    this.command = options.command;
    this.args = options.args ?? [];
    this.spawnFn = options.spawn;
    this.requestTimeoutMs = options.requestTimeoutMs ?? 30000;
    this.onStderr = options.onStderr ?? (() => {});
    this.generateJobId = options.generateJobId ?? defaultGenerateJobId;
  }

  start(): void {
    if (!this.stopped) {
      return; // 既に起動済みであれば冪等に何もしない
    }

    const child = this.spawnFn(this.command, this.args);
    this.child = child;
    this.stopped = false;
    this.stdoutBuffer = "";

    child.stdout.on("data", (chunk) => this.handleStdoutChunk(chunk));
    child.stderr.on("data", (chunk) => this.onStderr(chunk.toString()));
    child.on("exit", (code) => this.handleExit(code));
    child.on("error", (err) => this.handleFatalError(err));
  }

  /** 起動済みprocessを冪等に停止する。 */
  stop(): void {
    if (this.stopped || !this.child) {
      this.stopped = true;
      return;
    }
    const child = this.child;
    this.stopped = true;
    this.child = null;
    this.rejectAllPending(new Error("worker_manager_stopped"));
    child.kill();
  }

  /** commandをdispatchし、terminal eventまでのeventを集めて返す。 */
  request(command: string, parameters: Record<string, unknown> = {}): Promise<WorkerRequestResult> {
    if (!command) {
      return Promise.reject(new Error("command is required"));
    }
    if (this.stopped || !this.child) {
      return Promise.reject(new Error("worker_not_running"));
    }

    const jobId = this.generateJobId();
    const line = JSON.stringify({ job_id: jobId, job_type: command, parameters });

    return new Promise<WorkerRequestResult>((resolve, reject) => {
      const pendingEntry: PendingRequest = { jobId, events: [], resolve, reject };
      pendingEntry.timeoutHandle = setTimeout(() => {
        this.pending.delete(jobId);
        reject(new Error(`worker_request_timeout: ${command}`));
      }, this.requestTimeoutMs);
      this.pending.set(jobId, pendingEntry);

      try {
        this.child!.stdin.write(`${line}\n`);
      } catch (err) {
        this.pending.delete(jobId);
        clearTimeout(pendingEntry.timeoutHandle);
        reject(err instanceof Error ? err : new Error(String(err)));
      }
    });
  }

  private handleStdoutChunk(chunk: Buffer | string): void {
    this.stdoutBuffer += chunk.toString();
    const lines = this.stdoutBuffer.split("\n");
    this.stdoutBuffer = lines.pop() ?? "";

    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line) continue;

      let parsed: WorkerEventLike | null = null;
      try {
        parsed = JSON.parse(line) as WorkerEventLike;
      } catch {
        // 不正JSONは技術ログ扱いとし、workerプロセス全体は継続する(protocol stdoutと分離)。
        this.onStderr(`malformed worker stdout line: ${line}`);
        continue;
      }

      this.handleEvent(parsed);
    }
  }

  private handleEvent(event: WorkerEventLike): void {
    const jobId = event.job_id;
    if (!jobId) return;
    const entry = this.pending.get(jobId);
    if (!entry) return;

    entry.events.push(event);
    if (TERMINAL_EVENTS.has(event.event)) {
      this.pending.delete(jobId);
      clearTimeout(entry.timeoutHandle);
      if (event.event === "error") {
        entry.reject(new Error(`worker_request_failed: ${String(event.message ?? event.code ?? "unknown")}`));
      } else {
        entry.resolve({ jobId, events: entry.events, terminalEvent: event });
      }
    }
  }

  private handleExit(_code: number | null): void {
    this.stopped = true;
    this.child = null;
    this.rejectAllPending(new Error("worker_exited_unexpectedly"));
  }

  private handleFatalError(err: Error): void {
    this.stopped = true;
    this.child = null;
    this.rejectAllPending(err);
  }

  private rejectAllPending(error: Error): void {
    for (const entry of this.pending.values()) {
      clearTimeout(entry.timeoutHandle);
      entry.reject(error);
    }
    this.pending.clear();
  }
}

export interface ResolvePythonExecutableOptions {
  readonly env: Readonly<Record<string, string | undefined>>;
  readonly platform: NodeJS.Platform;
}

/** 環境変数`WALKWISE_PYTHON_EXECUTABLE`を優先し、なければplatform既定candidateを返す。 */
export function resolvePythonExecutable(options: ResolvePythonExecutableOptions): string {
  if (!options) {
    throw new Error("options is required");
  }
  const fromEnv = options.env.WALKWISE_PYTHON_EXECUTABLE;
  if (fromEnv && fromEnv.trim()) {
    return fromEnv.trim();
  }
  return options.platform === "win32" ? "python" : "python3";
}
