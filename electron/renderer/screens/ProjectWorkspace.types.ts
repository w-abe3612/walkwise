/**
 * electron/renderer/screens/ProjectWorkspace.types.ts — ProjectWorkspace.vueの型定義。
 *
 * `.vue`ファイルは`electron/env.d.ts`の汎用`declare module "*.vue"`shim経由でしか
 * plain `tsc`から型付けされず、named exportが認識されない(vue-tscでは可能だが
 * 本プロジェクトのtypecheck scriptはplain tscを使う)。そのため`<script setup>`側の
 * named export型をこの独立したplain `.ts`ファイルへ切り出し、componentとtestの
 * 両方がここから型をimportする。
 */

export interface SourceItem {
  readonly sourceId: string;
  readonly mediaType: string;
  readonly status: "registered" | "processing" | "ready" | "review_required" | "failed";
}

export interface ApprovalItem {
  readonly gate: string;
  readonly status: string;
}
