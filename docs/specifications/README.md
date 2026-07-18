---
status: approved
version: "1.4"
approved_at: "2026-07-18"
last_updated: "2026-07-19"
---

# 承認済み仕様書

## 1. 目的

このディレクトリには、実装時の正本として扱う承認済み仕様書を格納する。

`docs/spec-proposals/`の文書は、検討中または検証中であり、
本ディレクトリの承認済み仕様より優先してはならない。

## 2. 上位仕様

- [オーディオブック作成全体パイプライン](audiobook-creation-pipeline.md)

## 3. 基本方針

- [仕様書作成ガイドライン](00-specification-guidelines.md)
- [共通ID・バージョン・命名規則](01-common-identifiers-and-versioning.md)
- [各プロセスの入力・出力](02-process-input-output.md)
- [企画書YAMLスキーマ](03-project-plan-schema.md)
- [ファイルベースのデータ永続化方針](17-file-based-data-persistence-policy.md)
- [AIモデルルーティング・資料構築・コスト制御](18-ai-model-routing-and-cost-control.md)

## 4. コンテンツ作成

- [章単位の原稿生成仕様](04-chapter-generation-schema.md)
- [原稿セグメント共通スキーマ](05-script-segment-schema.md)
- [技術的主張と出典管理](06-claims-and-sources.md)
- [承認状態と差し戻し](07-approval-workflow.md)
- [キャラクタープロファイル](08-character-profile-schema.md)

## 5. 資料入力

- [Kindle画面キャプチャ](kindle-capture.md)
- [カメラ写真・スキャナ画像の資料入力](image-material-ingestion.md)

## 6. 音声生成

- [音声プロファイル](09-voice-profile-schema.md)
- [TTSクライアント共通インターフェース](10-tts-client-common-interface.md)
- [VOICEVOXクライアント](11-voicevox-client.md)
- [音声検査フレームワーク](13-audio-validation.md)
- [MP3結合と出力](14-audio-packaging.md)

## 7. 移行と開発

- [現行コードからの移行・互換性](15-migration-and-compatibility.md)
- [AI支援による仕様駆動・テスト先行開発](16-ai-assisted-development-workflow.md)

## 8. 未承認

次は承認済み仕様ではない。

- COEIROINKクライアント
- 話者別の最終プロファイル値
- 音声検査の最終閾値
- 資料入力パイプライン
- M4Bと全文版
- ASR照合

未承認仕様とタスクは`../spec-proposals/`を参照する。

## 9. サンプル

サンプル1章は現在タスク1で検証中である。

検証完了前は、次を作業正本とする。

```text
docs/spec-proposals/examples/sample-book/
```

検証完了後だけ、次へ昇格する。

```text
docs/specifications/examples/sample-book/
```
