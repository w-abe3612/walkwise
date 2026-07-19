---
status: approved
version: "2.0"
approved_at: "2026-07-18"
last_updated: "2026-07-19"
---

# 承認済み仕様書

## 1. 目的

このディレクトリには、実装時の正本として扱う承認済み仕様書を格納する。

`docs/spec-proposals/`の文書は、検討中または検証中であり、本ディレクトリの
承認済み仕様より優先してはならない。DBテーブル仕様は`docs/db/`、画面仕様は
`docs/screens/`を正本とする(本ディレクトリには置かない)。

## 2. 上位仕様

- [オーディオブック作成全体パイプライン](audiobook-creation-pipeline.md)
- [アプリケーション製品範囲とMVP](19-application-scope-and-mvp.md)

## 3. 基本方針

- [仕様書作成ガイドライン](00-specification-guidelines.md)
- [共通ID・バージョン・命名規則](01-common-identifiers-and-versioning.md)
- [各プロセスの入力・出力](02-process-input-output.md)
- [企画書YAMLスキーマ](03-project-plan-schema.md)
- [ローカルデータ永続化方針](17-local-data-persistence-policy.md)
- [AIモデルルーティング・資料構築・コスト制御](18-ai-model-routing-and-cost-control.md)

## 4. コンテンツ作成

- [章単位の原稿生成仕様](04-chapter-generation-schema.md)
- [原稿セグメント共通スキーマ](05-script-segment-schema.md)
- [技術的主張と出典管理](06-claims-and-sources.md)
- [承認状態と差し戻し](07-approval-workflow.md)
- [キャラクタープロファイル](08-character-profile-schema.md)

## 5. 資料入力

- [カメラ写真・スキャナ画像の資料入力](image-material-ingestion.md)

Kindle画面キャプチャは本体の対象外であり、専用ツール案として
`docs/spec-proposals/kindle-capture-separate-tool.md`で未承認提案として管理する。

## 6. 音声生成

- [音声プロファイル](09-voice-profile-schema.md)
- [TTSクライアント共通インターフェース](10-tts-client-common-interface.md)
- [VOICEVOXクライアント](11-voicevox-client.md)
- [音声検査フレームワーク](13-audio-validation.md)
- [MP3結合と出力](14-audio-packaging.md)

## 7. Electronアプリケーション

- [アプリケーション製品範囲とMVP](19-application-scope-and-mvp.md)
- [Electronデスクトップアプリケーション構成](20-electron-desktop-architecture.md)
- [Electron-Python worker連携契約](21-electron-python-worker-interface.md)
- [Jobライフサイクルと復旧](22-job-lifecycle-and-recovery.md)
- [配布・プラットフォーム方針](23-distribution-and-platform-policy.md)
- DBテーブル仕様: [`docs/db/`](../db/README.md)
- 画面仕様: [`docs/screens/`](../screens/README.md)

## 8. 移行と開発

- [現行コードからの移行・互換性](15-migration-and-compatibility.md)
- [AI支援による仕様駆動・テスト先行開発](16-ai-assisted-development-workflow.md)

## 9. 未承認

次は承認済み仕様ではない。未承認仕様とタスクは`../spec-proposals/`を参照する。

- COEIROINKクライアント
- 話者別の最終プロファイル値
- 音声検査の最終閾値
- 資料入力パイプラインの下位仕様(PDF直接抽出、OCR、EPUB抽出、前処理等)
- M4Bと全文版
- ASR照合
- Kindle画面キャプチャ(専用ツール案)
- 動画・授業録音の資料入力

## 10. サンプル

サンプル1章は現在タスク1で検証中である。

検証完了前は、次を作業正本とする。

```text
docs/spec-proposals/examples/sample-book/
```

検証完了後だけ、次へ昇格する。

```text
docs/specifications/examples/sample-book/
```
