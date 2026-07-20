/**
 * electron/renderer/components/AppShell.types.ts — AppShell.vueの型定義。
 *
 * `.vue`ファイルはplain tscからnamed exportを認識されないため
 * (詳細は`ProjectWorkspace.types.ts`と同じ理由)、型のみ独立ファイルへ切り出す。
 */

import type { ScreenId } from "../router";
import type { UserFacingError } from "../stores/app";

export interface NavItem {
  readonly screen: ScreenId;
  readonly label: string;
}
