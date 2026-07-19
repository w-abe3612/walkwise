---
status: active
version: "2.0"
last_updated: "2026-07-19"
---

# 仕様策定タスク一覧

## 1. 実行規則

- 原則として番号順に進める。
- `depends_on`が未完了のタスクには着手しない。
- 承認済み仕様は`spec_refs`で参照する。
- 完成した仕様は`docs/specifications/`へ移す。
- 仕様承認後にのみ`docs/tasks/`へ実装タスクを作成する。
- 本一覧には**未実行タスクだけ**を掲載する。完了履歴はGit履歴を正本とし、
  本ファイルへは残さない。

## 2. 承認済みの横断仕様

- [オーディオブック作成全体パイプライン](../../specifications/audiobook-creation-pipeline.md)
- [AIモデルルーティング・資料構築・コスト制御](../../specifications/18-ai-model-routing-and-cost-control.md)
- [アプリケーション製品範囲とMVP](../../specifications/19-application-scope-and-mvp.md)

## 3. タスク状態

| 状態 | 意味 |
|---|---|
| `draft` | 未着手または検討中 |
| `review` | 仕様案の確認中 |
| `blocked` | 依存事項や外部条件により停止 |
| `done` | 仕様が承認され、正本へ反映済み(完了後は本一覧から削除する) |

## 4. 一覧(未実行タスクのみ)

| 順序 | テーマ | 状態 | 依存 | 出力仕様 |
|---:|---|---|---|---|
| 1 | [サンプル1章による仕様間整合性確認](1_sample-book-end-to-end-validation.md) | draft | 承認済み上位仕様 | `docs/specifications/examples/sample-book/` |
| 2 | [ファイル保存運用の詳細](2_file-persistence-operations.md) | draft | 1 | `docs/specifications/file-persistence-operations.md` |
| 3 | [話者別音声プロファイル初期値](3_voice-profile-default-values.md) | draft | 1 | `docs/specifications/voice-profile-default-values.md` |

## 5. 未承認提案として継続検討中のテーマ

次のテーマは仕様策定タスクとしては完了(削除)しているが、内容は
`docs/spec-proposals/`直下の提案書として引き続き検討中である。

- [音声検査の最終閾値](../audio-validation-thresholds.md)
- [COEIROINKクライアント](../coeiroink-client.md)
- [資料入力パイプラインの責務と境界](../material-input-pipeline.md)
- [資料保存構成と共通資料スキーマ](../source-storage-and-common-schema.md)
- [著作権・ライセンス・利用目的の管理](../rights-and-license-management.md)
- [PDF直接テキスト抽出](../pdf-direct-text-extraction.md)
- [OCRとスキャンPDF](../ocr-and-scanned-pdf.md)
- [EPUBテキスト抽出](../epub-text-extraction.md)
- [書籍データ前処理](../source-preprocessing.md)
- [M4Bと全文版出力](../m4b-and-complete-book-output.md)
- [ASRによる原稿と音声の照合](../asr-script-audio-verification.md)
- [Kindle画面キャプチャ(専用ツール案)](../kindle-capture-separate-tool.md)
- [動画・YouTube等の資料入力](../video-source-ingestion.md)
- [授業録音・音声ファイルの資料入力](../audio-recording-source-ingestion.md)

カメラ写真・スキャナ画像は承認済み仕様へ昇格済みである。

```text
docs/specifications/image-material-ingestion.md
```
