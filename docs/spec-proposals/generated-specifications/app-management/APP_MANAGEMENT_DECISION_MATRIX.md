---
status: provisional
version: "0.1"
created_at: "2026-07-19"
task_id: SPEC-APP-019
---

# app-management 意思決定マトリクス

翌朝、短時間で判断するための一覧。詳細は各草案本文を参照。

## 技術スタック (`02-architecture-and-runtime.md`)

| 案 | 概要 | 推奨 | 判断条件 |
|---|---|---|---|
| A. FastAPI + Vue3/Vite SPA | 既存Python資産と親和性が高い | **暫定採用** | Node.jsツールチェーン導入可否の人間確認が必要 |
| B. Python + SSR/HTMX | 追加ツールチェーン不要 | 対抗案として保持 | フロントのリッチさより配布の単純さを優先するなら採用 |
| C. Tauri + Web frontend | ネイティブアプリ体験 | 将来候補 | Rust導入コストが見合う配布要求が生じた場合 |

## 永続化方式 (`05-persistence-strategy.md`)

| 案 | 概要 | 推奨 | 判断条件 |
|---|---|---|---|
| 1. ファイル正本+SQLite索引 | 既存方針に最も忠実 | 不採用 (新概念の置き場が曖昧) | - |
| 2. SQLiteメタデータ正本+ファイル原本 | Job/BuildRequestに自然な置き場 | **暫定採用** | PoC-2 (ファイルからのDB再構築)成功が条件 |
| 3. PostgreSQL等サーバー型 | 将来の拡張性最大 | 不採用 (単一利用者前提と衝突) | 複数利用者要求が明確化したら再検討 |

## Job実行方式 (`02-architecture-and-runtime.md`)

| 方式 | 推奨 | 判断条件 |
|---|---|---|
| 同一プロセススレッド/async | 不採用 | APIクラッシュでJob消失リスク |
| サブプロセス起動 | **暫定採用** | 既存CLIとの親和性を優先 |
| 専用ワーカー | 次期候補 | 並列実行要求が明確化したら移行 |

## MVP範囲サマリ (`01-product-scope-and-mvp.md`)

| 機能 | 区分 |
|---|---|
| Project新規作成・素材import・出力/声選択・4段階承認・Job監視・成果物確認 | MVP |
| 複製/archive、差分再生成UI、原稿詳細編集、コスト表示 | 次期 |
| 複数利用者、クラウド同期、EPUB出力、COEIROINK | 将来 or 下位仕様待ち |

## 追加機能提案 Top5 (`15-additional-feature-proposals.md`)

1. 承認待ち一覧
2. AI利用コスト・使用量表示
3. バックアップ・復元のUI化
4. Project archive/複製
5. Engine/API疎通診断・定期ヘルスチェック

## 未確定の主要事項

| 事項 | 該当書 | 解消方法 |
|---|---|---|
| 技術スタック最終決定 | `02` | PoC-1実施後、人間承認 |
| 永続化方式最終決定 | `05`,`06` | PoC-2実施後、人間承認 |
| EPUB出力仕様 | `10` | 新規仕様策定 (別タスク) が必要 |
| COEIROINK対応時期 | `11` | クライアント実装状況に依存 |
| セキュリティ (認証なし方針の継続期間) | `13` | 人間判断 |
| タスク34番の依存関係自己参照 | `13` | 人間確認・タスク定義修正 |

## 翌朝レビュー順序

1. `00-current-state-and-terminology.md` (前提の用語・現状認識)
2. `01-product-scope-and-mvp.md` (MVP範囲)
3. `02-architecture-and-runtime.md` + `05-persistence-strategy.md` (技術選定、PoC計画)
4. `06`〜`14` (詳細設計)
5. `15-additional-feature-proposals.md` (追加機能)
6. `16-integrated-application-proposal.md` (統合)
7. `17-specification-promotion-plan.md` (昇格計画)
