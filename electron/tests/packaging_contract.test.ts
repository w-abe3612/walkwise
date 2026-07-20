/**
 * Test suite for TASK-RELEASE-001: Windows package・runtime同梱・license/privacy/backup.
 * Contract: docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md
 * Cases in this file: TC-RELEASE-001-01, 04, 07, 10.
 */

import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, test } from "vitest";

import { resolveRuntimeDependencies } from "../main/runtime";

const REPO_ROOT = join(__dirname, "..", "..");
const ELECTRON_BUILDER_YML_PATH = join(REPO_ROOT, "electron-builder.yml");
const RELEASE_MANIFEST_PATH = join(REPO_ROOT, "resources", "release-manifest.json");

function readReleaseManifest(): {
  code_signing: { signed: boolean; risk: string; mitigation: string };
  user_data: { stored_in_install_directory: boolean; deleted_on_uninstall: boolean };
  third_party_licenses: readonly { name: string; license: string; bundled: boolean }[];
} {
  return JSON.parse(readFileSync(RELEASE_MANIFEST_PATH, "utf-8"));
}

describe("TASK-RELEASE-001 Windows package・runtime同梱・license/privacy/backup", () => {
  test("TC-RELEASE-001-01: uninstall data保持 [e2e/P0]", () => {
    const builderConfig = readFileSync(ELECTRON_BUILDER_YML_PATH, "utf-8");
    expect(builderConfig).toMatch(/deleteAppDataOnUninstall:\s*false/);

    const manifest = readReleaseManifest();
    expect(manifest.user_data.deleted_on_uninstall).toBe(false);
    expect(manifest.user_data.stored_in_install_directory).toBe(false);

    // uninstallシナリオを、install先ディレクトリとは分離した利用者データ領域でsimulateする。
    const scratchRoot = mkdtempSync(join(tmpdir(), "walkwise-uninstall-"));
    const installDir = join(scratchRoot, "install");
    const userDataDir = join(scratchRoot, "userdata");
    mkdirSync(installDir, { recursive: true });
    mkdirSync(join(userDataDir, "projects", "sample-book"), { recursive: true });
    writeFileSync(join(installDir, "Walkwise.exe"), "fake-executable");
    writeFileSync(join(userDataDir, "app.db"), "fake-sqlite-bytes");
    writeFileSync(join(userDataDir, "projects", "sample-book", "book.json"), "{}");

    // uninstall: install先ディレクトリだけを削除する(5.8節)。
    rmSync(installDir, { recursive: true, force: true });

    expect(existsSync(installDir)).toBe(false);
    expect(existsSync(join(userDataDir, "app.db"))).toBe(true);
    expect(existsSync(join(userDataDir, "projects", "sample-book", "book.json"))).toBe(true);

    rmSync(scratchRoot, { recursive: true, force: true });
  });

  test("TC-RELEASE-001-04: Windows target [unit/P1]", () => {
    const builderConfig = readFileSync(ELECTRON_BUILDER_YML_PATH, "utf-8");
    expect(builderConfig).toMatch(/target:\s*nsis/);
    expect(builderConfig).toMatch(/arch:\s*\n\s*-\s*x64/);
    expect(builderConfig).not.toMatch(/dmg|AppImage|deb|rpm|pkg:/);

    const manifest = readReleaseManifest();
    expect(manifest).toHaveProperty("code_signing");
  });

  test("TC-RELEASE-001-07: code signing未実施表示 [unit/P1]", () => {
    const builderConfig = readFileSync(ELECTRON_BUILDER_YML_PATH, "utf-8");
    expect(builderConfig).toMatch(/forceCodeSigning:\s*false/);

    const manifest = readReleaseManifest();
    expect(manifest.code_signing.signed).toBe(false);
    expect(manifest.code_signing.risk.length).toBeGreaterThan(0);
    expect(manifest.code_signing.mitigation.length).toBeGreaterThan(0);
  });

  test("TC-RELEASE-001-10: 入力・既存成果物の不変性 [unit/P0]", async () => {
    const beforeBuilderConfig = readFileSync(ELECTRON_BUILDER_YML_PATH, "utf-8");
    const beforeManifest = readFileSync(RELEASE_MANIFEST_PATH, "utf-8");

    const probeVersion = async (command: string) => {
      if (command === "missing-tool") {
        return { stdout: "", stderr: "command not found", exitCode: 127 };
      }
      return { stdout: `${command} version 1.0.0`, stderr: "", exitCode: 0 };
    };

    const first = await resolveRuntimeDependencies({
      dependencies: [
        { id: "python", command: "python" },
        { id: "ffmpeg", command: "missing-tool" },
      ],
      probeVersion,
    });
    const second = await resolveRuntimeDependencies({
      dependencies: [
        { id: "python", command: "python" },
        { id: "ffmpeg", command: "missing-tool" },
      ],
      probeVersion,
    });

    expect(first).toEqual(second);
    expect(first[0].available).toBe(true);
    expect(first[1].available).toBe(false);

    expect(readFileSync(ELECTRON_BUILDER_YML_PATH, "utf-8")).toBe(beforeBuilderConfig);
    expect(readFileSync(RELEASE_MANIFEST_PATH, "utf-8")).toBe(beforeManifest);
  });
});
