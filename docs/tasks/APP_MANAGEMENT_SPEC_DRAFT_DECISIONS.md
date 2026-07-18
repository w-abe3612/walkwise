---
status: provisional
version: "1.0"
created_at: "2026-07-19"
---

# フロント・DB管理 草案作成時の初期判断

これは承認済み仕様ではない。
Claude Codeが比較を始めるための初期仮説である。

## 利用形態

- Windows中心のローカル単一利用者を初期対象候補とする。
- 一つのコマンドでbackend・DB準備・frontendを起動し、browserを開く。
- 外部公開serverを初期目的にしない。

## 永続化

- SQLiteを第一候補とする。
- DBはProject、Source metadata、Build Request、Job、Artifact index、Approval、設定を管理する候補。
- 原素材、画像、長文text、WAV、MP3、EPUBは原則fileに置く候補。
- DBとfileの二重正本を避ける。
- portable manifestまたはexportを残す。

## 技術構成候補

- Python backendと既存Python処理を中心にする。
- Vue 3＋Vite案、server-rendered案、Tauri/Electron案を比較する。
- APIとCLIは同じapplication serviceを呼ぶ将来構成を候補にする。

## MVP画面候補

- Dashboard / Project一覧
- Project新規作成
- Project詳細
- 素材import
- 出力設定
- 声・音声profile選択とpreview
- Job進捗・error・retry
- 成果物一覧
- 設定・TTS engine診断

## 必ず追加検討する機能

- 中断再開
- 差分再生成
- 承認待ち一覧
- 原稿・出典・音声preview
- output履歴
- Project複製・archive
- backup・restore
- 容量・engine・API key診断
- rights/privacy状態
- AI利用costとmodel routing表示

## 未確定

- frontend framework
- server-renderingかSPAか
- desktop包装の時期
- DBをmetadata正本にする範囲
- background worker方式
- EPUBをMVPに含めるか
- editing UIのMVP範囲
