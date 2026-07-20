/**
 * electron/renderer/screens/JobsAndArtifacts.types.ts — JobsAndArtifacts.vueの型定義。
 *
 * `.vue`ファイルはplain tscからnamed exportを認識されないため
 * (詳細は`ProjectWorkspace.types.ts`と同じ理由)、型のみ独立ファイルへ切り出す。
 */

export type JobStatus = "queued" | "running" | "succeeded" | "failed" | "cancel_requested" | "cancelled";

export interface JobItem {
  readonly jobId: string;
  readonly jobType: string;
  readonly status: JobStatus;
  readonly progressCurrent?: number;
  readonly progressTotal?: number;
  readonly lastMessage?: string;
  readonly stale?: boolean;
  readonly technicalDetail?: string;
}

export interface ArtifactItem {
  readonly artifactId: string;
  readonly artifactType: string;
  readonly versionNumber: number;
  readonly createdAt: string;
}
