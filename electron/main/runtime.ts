/** electron/main/runtime.ts — 公開契約: resolveRuntimeDependencies(options).
 *
 * Contract: docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md
 * Spec: docs/specifications/23-distribution-and-platform-policy.md(5.3節)
 */

export type RuntimeDependencyId = "python" | "ffmpeg" | "ffprobe" | "tesseract";

export interface RuntimeDependencyCheck {
  readonly id: RuntimeDependencyId;
  readonly command: string;
  readonly versionArgs?: readonly string[];
}

export interface RuntimeDependencyResult {
  readonly id: RuntimeDependencyId;
  readonly available: boolean;
  readonly version: string | null;
  readonly detail: string | null;
}

export interface ProbeVersionOutcome {
  readonly stdout: string;
  readonly stderr: string;
  readonly exitCode: number;
}

export interface ResolveRuntimeDependenciesOptions {
  readonly dependencies: readonly RuntimeDependencyCheck[];
  readonly probeVersion: (command: string, args: readonly string[]) => Promise<ProbeVersionOutcome>;
}

/** Python/ffmpeg/ffprobe/Tesseract等の存在とversionを確認する(23節 5.3節)。副作用なし。 */
export async function resolveRuntimeDependencies(
  options: ResolveRuntimeDependenciesOptions
): Promise<readonly RuntimeDependencyResult[]> {
  if (!options) {
    throw new Error("options is required");
  }
  if (!options.dependencies || options.dependencies.length === 0) {
    throw new Error("dependencies is required");
  }
  if (!options.probeVersion) {
    throw new Error("probeVersion is required");
  }

  const results: RuntimeDependencyResult[] = [];
  for (const dependency of options.dependencies) {
    if (!dependency.id || !dependency.command) {
      throw new Error("each dependency requires id and command");
    }
    const args = dependency.versionArgs ?? ["--version"];
    try {
      const outcome = await options.probeVersion(dependency.command, args);
      if (outcome.exitCode !== 0) {
        results.push({
          id: dependency.id,
          available: false,
          version: null,
          detail: outcome.stderr.trim() || `exit code ${outcome.exitCode}`,
        });
        continue;
      }
      const versionText = (outcome.stdout || outcome.stderr || "").trim();
      results.push({ id: dependency.id, available: true, version: versionText || null, detail: null });
    } catch (error) {
      results.push({
        id: dependency.id,
        available: false,
        version: null,
        detail: error instanceof Error ? error.message : String(error),
      });
    }
  }
  return results;
}
