---
spec_id: 07-approval-workflow
title: "承認状態と差し戻しルール"
status: approved
version: "1.1"
approved_at: "2026-07-18"
last_updated: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_231158.txt"
---


# 承認状態と差し戻しルール

## 1. 目的

資料・カリキュラム、作品企画、検証済み原稿、試聴音声の人間承認を管理し、
承認後の変更で古い承認が残らないようにする。

## 2. 承認地点

次の4地点をMUSTとする。

1. `materials_curriculum`
2. `planning`
3. `verified_script`
4. `preview_audio`

## 3. 状態

```text
draft
review_pending
approved
changes_requested
revised
rejected
invalidated
```

## 4. 基本遷移

```text
draft -> review_pending -> approved
review_pending -> changes_requested -> revised -> review_pending
review_pending -> rejected
approved -> invalidated
```

`invalidated`から直接`approved`へ戻してはならない。

## 5. ファイル

```text
project/approvals.yaml
```

## 6. 推奨スキーマ

```yaml
schema_version: "1.0"
project_id: database-foundations
content_revision: 1

approvals:
  materials_curriculum:
    approval_id: approval-materials-r0001
    status: approved
    target:
      type: bundle
      paths:
        - project/sources.yaml
        - curriculum/topic-map.yaml
        - curriculum/curriculum.yaml
      content_revision: 1
      content_hash: "..."
    approved_by: user
    approved_at: "2026-07-18T21:00:00+09:00"
    comment: null

  planning:
    approval_id: approval-planning-r0001
    status: approved
    target:
      type: file
      path: project/project-plan.yaml
      content_revision: 2
      content_hash: "..."
    approved_by: user
    approved_at: "2026-07-18T21:10:00+09:00"
    comment: null

  verified_script:
    status: review_pending

  preview_audio:
    status: draft
```

## 7. 承認対象

承認対象は単一ファイルまたはbundleとする。

bundle hashは、対象パス、各ファイルhash、順序をcanonical化して計算する。

## 8. 差し戻し

```yaml
change_requests:
  - request_id: cr-0001
    target:
      type: segment
      id: ch01-seg004
    category: factual_error
    severity: critical
    comment: 主キーと一意制約の違いを補足する
    status: open
```

## 9. 差し戻しカテゴリ

```text
source_missing
source_rights
curriculum_gap
factual_error
unsupported_claim
source_conflict
meaning_changed
missing_information
difficulty_mismatch
audio_clarity
pronunciation
character_style
technical_audio_error
other
```

## 10. 承認の無効化

| 変更 | 無効化する承認 |
|---|---|
| 資料一覧変更 | materials_curriculum、planning、verified_script、preview_audio |
| 資料役割変更 | materials_curriculum、planning、verified_script、preview_audio |
| 資料本文・版変更 | 該当materials_curriculum、planning、verified_script、preview_audio |
| topic map変更 | materials_curriculum、planning、verified_script、preview_audio |
| curriculum変更 | materials_curriculum、planning、verified_script、preview_audio |
| project plan変更 | planning、verified_script、preview_audio |
| chapter spec変更 | verified_script、preview_audio |
| 原稿text変更 | verified_script、preview_audio |
| tts_textのみ変更 | preview_audio |
| character profile変更 | verified_script、preview_audio |
| voice profile変更 | preview_audio |
| TTS engine version変更 | preview_audio |
| MP3タグだけ変更 | 原則として維持 |

承認対象hashと現在hashが一致しない場合、
承認状態を`invalidated`へ変更する。

## 11. 実行ゲート

- materials curriculum未承認: 作品企画の正式承認と章原稿の本生成を停止する。
- planning未承認: 初稿の本生成を停止する。
- verified script未承認: 本番TTSを停止する。
- preview audio未承認: deliverablesへのコピーを停止する。

## 12. 開発用強制実行

`--force`をMAYで用意できる。

MUST:

- 強制実行をログへ記録する。
- 出力を`unapproved/`へ分離する。
- manifestへ`approval_bypassed: true`を記録する。
- deliverablesへコピーしない。
- 承認済み成果物を上書きしない。

## 13. 試聴対象

- 導入
- 技術的定義
- AI生成例え話
- 数字
- 英字
- 専門用語
- SQLまたはコード
- 注意事項
- まとめ

中立原稿を許可する。

## 14. Error

- 必須承認キー欠落
- approval ID重複
- target path欠落
- target hash欠落
- 承認対象hash不一致
- 未承認成果物の正式出力
- invalidated承認を有効として使用
- 承認者または承認日時欠落

## 15. Warning

- 承認コメントなし
- bundle対象が多すぎる
- voice profileが暫定
- source locatorが粗い
- `--force`使用

## 16. 現行実装との関係

現行CLIには承認ゲートがない。

導入順:

1. approvals model
2. hash比較
3. 新オーケストレーターのゲート
4. `--force`分離出力
5. 既存低レベルコマンドの開発用明記

## 17. テスト観点

- 4件の承認キーを読み込める。
- materials変更で4承認が無効になる。
- planning変更で後続3承認が無効になる。
- 原稿1文字変更で原稿・試聴承認が無効になる。
- tts_text変更で試聴承認だけが無効になる。
- voice profile変更で試聴承認だけが無効になる。
- 未承認原稿から本番TTSできない。
- 未承認試聴からdeliverablesへ出力できない。
- bundle hash差分を検出できる。
- `--force`出力が正式成果物と混ざらない。

## 18. 完了条件

- 4段階の承認履歴を追跡できる。
- 変更済み成果物へ古い承認が適用されない。
- 正式成果物の各段階で承認状態を確認できる。
- 開発用強制出力がdeliverablesへ混入しない。
