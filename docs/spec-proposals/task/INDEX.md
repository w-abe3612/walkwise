---
status: active
version: "3.0"
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

現在、未実行の仕様策定タスクはない。旧タスク1〜3
(サンプル1章検証・ファイル保存運用・話者別音声プロファイル初期値)は
`TASK-REVIEW-001`時点で完了・削除済み(決定内容は`docs/specifications/`の
`17-local-data-persistence-policy.md`・`09-voice-profile-schema.md`等へ
吸収済み、`docs/specifications/examples/sample-book/`は実データとして存在)。
完了履歴はGit履歴を正本とする(本節冒頭の実行規則どおり)。

## 5. 未承認提案として継続検討中のテーマ

次のテーマは仕様策定タスクとしては完了(削除)しているが、内容は
`docs/spec-proposals/`直下の提案書として引き続き検討中である。

- [音声検査の最終閾値](../audio-validation-thresholds.md) — `status: provisional`
- [COEIROINKクライアント](../coeiroink-client.md) — `status: blocked`

次のテーマは、資料入力パイプラインの下位仕様として`docs/specifications/`へ
昇格済みであり、本ディレクトリには重複して残していない。

- 資料入力パイプラインの責務と境界 → `docs/specifications/material-input-pipeline.md`
- 資料保存構成と共通資料スキーマ → `docs/specifications/source-storage-and-common-schema.md`
- 著作権・ライセンス・利用目的の管理 → `docs/specifications/rights-and-license-management.md`
- PDF直接テキスト抽出 → `docs/specifications/pdf-direct-text-extraction.md`
- OCRとスキャンPDF → `docs/specifications/ocr-and-scanned-pdf.md`
- EPUBテキスト抽出 → `docs/specifications/epub-text-extraction.md`
- 書籍データ前処理 → `docs/specifications/source-preprocessing.md`
- M4B出力 → `docs/specifications/m4b-output.md`
- ASRによる原稿と音声の照合 → `docs/specifications/asr-script-audio-verification.md`

カメラ写真・スキャナ画像は承認済み仕様へ昇格済みである。

```text
docs/specifications/image-material-ingestion.md
```

Kindle画面キャプチャ・Kindle専用ツール、動画・授業録音の資料入力は、
製品の恒久的対象外であり、仕様策定タスク・未承認提案のいずれとしても存在しない
(`docs/specifications/19-application-scope-and-mvp.md` 5.5節)。

## 6. 実装準備タスク切り出し

承認済み仕様を実装契約へ変換するSTEP1の一覧は、次を正本とする。

- [実装準備タスク一覧](IMPLEMENTATION_INDEX.md)

(実装準備マスタープランは、記載していた全54タスクの実装完了に伴い
`TASK-REVIEW-001`で削除した。内容はGit履歴を参照。)

この一覧のtaskはClaude Codeへ直接実行させない。
MVP対象taskすべてについて、契約・テストケース、テスト空実装、ソース空実装、
コマンド文書、`docs/tasks/`契約書、構文・import・pytest収集確認を完了し、
人間が承認してから本実装へ進む。
