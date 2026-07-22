---
document_type: implementation_assumptions_log
status: in_progress
last_updated: "2026-07-22"
---

# 実装時の仮定記録(夜間自律実行)

本書は、`docs/tasks/`実行中に人間確認を待たず安全側の仮定を置いた箇所を記録する。
各タスクの完了報告にも同じ内容を要約するが、恒久的な参照先は本書とする。

## 記録方針

- 停止条件(データ破壊、契約矛盾、セキュリティ問題、Repository破壊、STEP4公開API変更、秘密漏洩)に
  該当しない曖昧さは、承認済み仕様・contract・STEP4公開signatureのうち最も具体的なものを優先し、
  最小の追加解釈で実装する。
- 仮定は後日person確認できるよう、タスクID・対象ファイル・仮定内容・根拠・置き換え条件を記録する。

## 仮定一覧

### TASK-CORE-001

- 対象: `script/core/config.py`
- 仮定: `AppConfig`の必須設定キーを`WALKWISE_DATA_ROOT`(1件)とした。上位仕様
  (`17-local-data-persistence-policy.md`等)は具体的な環境変数名を規定していないため。
- 根拠: 契約の「設定読込の優先順位」「必須入力欠落」ケースを満たすには最低1つの
  必須キーが必要であり、資料永続化のroot pathが最も基盤的な設定であるため。
- 置き換え条件: 後続タスク(`TASK-FILE-001`等)で正式な環境変数名・必須設定一覧が
  仕様として確定した場合、`_REQUIRED_KEYS`をそちらに合わせて更新する。

- 対象: `script/core/errors.py`
- 仮定: `AppError`に`to_public_dict() -> dict[str, str]`を追加した。公開契約表には
  明記されていないが、テストケース「公開dictへ変換する」を満たすために必要な
  最小限の公開methodである。
- 根拠: 契約6節はconstructor signatureのみを列挙する簡略形式であり、7節の
  テストケースが要求する変換操作には対応する公開methodが必要なため。
- 置き換え条件: 後続タスクが別名の変換methodを要求する場合は、そちらへ統一する。

- 対象: `script/core/errors.py`
- 仮定: `ErrorCode`を`str, Enum`とし、`VALIDATION_ERROR/NOT_FOUND/CONFLICT/
  PERMISSION_DENIED/EXTERNAL_UNAVAILABLE/INTERNAL_ERROR`の6値を用意した。
- 根拠: 契約は`ErrorCode`の具体的な値集合を規定していないため、他タスクの
  エラー分類(validation/not_found/conflict等)から一般的に必要と判断される
  最小集合を用意した。
- 置き換え条件: 後続タスクが追加のerror codeを必要とする場合、既存6値の意味を
  変えずに追加してよい。

### TASK-CORE-002

- 対象: `requirements.txt`
- 仮定: 契約の`load_yaml/dump_yaml`を安全に実装するため`pyyaml==6.0.2`を新規依存として
  追加した(このtaskのsource_files一覧には`requirements.txt`は含まれないが、YAML
  読み書きは標準ライブラリだけでは実装できないため必須の追加と判断)。
- 根拠: 契約6節が`load_yaml/dump_yaml`を明示的に公開契約として要求しており、
  自前でYAML parserを書くことは他タスクが依存する基盤としてリスクが高い。
- 置き換え条件: なし(標準的で広く使われるライブラリであり、置き換えの必要は
  現時点で想定しない)。

- 対象: `script/core/serialization.py`
- 仮定: `load_yaml/load_json/dump_yaml/dump_json`の引数を`(path: Path)`/
  `(path: Path, data: Any)`とした(STEP4空実装は引数0個のplaceholderだった)。
- 根拠: STEP4_README.mdが明記する通り、STEP4空実装のsignatureは
  「finalized during task implementation」であり、引数0個のload/dump関数は
  意味を成さないため、最小限で自明な引数を確定した。
- 置き換え条件: なし(finalizeされたsignatureとして扱う)。

- 対象: `script/core/serialization.py`
- 仮定: schema_versionの`未知minor`検出を戻り値ではなく`warnings.warn`
  (`UnknownSchemaMinorWarning`)で通知する設計にした。
- 根拠: 契約は新しい公開symbol(戻り値wrapper型等)を追加しないことを求めており、
  Python標準の`warnings`機構を使うことで戻り値の型を`Any`のまま維持できるため。
- 置き換え条件: 後続タスクが構造化されたwarning一覧を戻り値として要求する場合は
  この設計を見直す。

- 対象: `script/core/serialization.py`
- 仮定: 対応する`schema_version` majorを`1`固定とした。
- 根拠: `01-common-identifiers-and-versioning.md`の全サンプルが`schema_version: "1.0"`
  であり、現時点でmajor 2以降は未定義であるため。
- 置き換え条件: 上位仕様がmajor 2を正式に定義した場合、`_SUPPORTED_SCHEMA_MAJOR`を
  更新する。

### TASK-FILE-001

- 対象: `script/persistence/paths.py`
- 仮定: `ProjectPaths`に`project_root`/`sources_dir`/`chapters_dir`/`manifests_dir`
  (property)、`resolve_relative(relative)`、`to_relative_str(path)`を追加した。
  契約表は`for_root`のみを列挙するが、返り値の`ProjectPaths`が実際に
  「相対path制約」「絶対パスのDB保存禁止」を実行できる必要があるため。
- 根拠: 対象範囲(4節)に明記された「相対パス制約」「絶対パスのDB保存禁止」を
  満たすには、`for_root`が返すオブジェクト自身にpath解決・検証methodが
  なければ検証不能なため。
- 置き換え条件: 後続タスク(`TASK-DB-001`等)が別名・別形式のpath解決APIを
  要求する場合、そちらに統一する。

- 対象: `script/persistence/locking.py`
- 仮定: `ProjectLock.acquire`を`@classmethod @contextmanager`として実装し、
  排他制御はロックファイルの`O_CREAT|O_EXCL`によるatomic生成で行った。
  stale lock自動解除は実装していない(範囲外、`19-application-scope-and-mvp.md`
  等で別途規定されない限りMVP外と判断)。
- 根拠: `O_CREAT|O_EXCL`はPOSIX/Windows双方でatomicなfile-based mutexとして
  広く使われる標準的手法であり、外部依存を増やさずProject単位排他を実現できる。
- 置き換え条件: 後続タスクでプロセスクラッシュ時のstale lock復旧が必要になった場合、
  別途仕様化してから実装する。

### TASK-DOMAIN-001

- 対象: `script/domain/validation.py`, `script/domain/models.py`
- 仮定: `_assert_relative_path`という非公開helperを追加し、`Project.plan_file_path`,
  `Source.original_file_path`, `Artifact.file_path`の`__post_init__`で絶対path・
  `..`によるroot escapeを拒否する形にした。
- 根拠: 対象範囲(4節)の「相対path value object」を満たすには、domain modelの
  path系フィールド自体が絶対path/escapeを拒否する必要があるため。名前に
  `_`を付け非公開helperとして扱い、新しい公開symbolの追加を避けた。
- 置き換え条件: `TASK-FILE-001`の`ProjectPaths`が返すpathと重複する検証だが、
  domain層はfilesystem非依存であるべきという要件上、意図的に軽量な文字列検証
  として独立させている。将来統合する場合はこの関数を置き換える。

- 対象: `script/domain/models.py`
- 仮定: DBの`output_formats_json`(JSON文字列)は、domain層では
  `tuple[str, ...]`として表現した(`BuildRequest.output_formats`)。
- 根拠: 契約6節が「DBやUIに依存しないdataclass」を明記しており、JSON文字列化は
  永続化層(`TASK-DB-002`等)の責務であるため。
- 置き換え条件: なし。

### TASK-DB-001

- 対象: `script/persistence/migrations.py`
- 仮定: `MigrationRunner`のコンストラクタは無引数とし(`MigrationRunner()`)、
  `connection`/`migrations_dir`は各methodの引数として明示的に渡す設計にした。
  STEP4空実装は`__init__(self, *args, **kwargs)`という汎用placeholderで、
  契約の`apply_all(connection, migrations_dir, ...)`という記法も
  connectionをmethod引数として受け取る形と整合する。
- 根拠: 契約6節の記法(`MigrationRunner.apply_all(connection, migrations_dir, ...)`)が
  connectionをインスタンス状態ではなく引数として渡す設計を示しているため。
- 置き換え条件: なし。

- 対象: `script/persistence/sql/0001_initial.sql`
- 仮定: `output_formats_json`の内容検証(許可値mp3/text限定、重複禁止)は
  SQLiteのCHECK制約だけでは完全に表現できないため、DB層では
  `json_valid`と`mp3含有時のvoice_profile_id必須`のみを制約し、許可値・重複の
  完全検証はApplication Service層(`TASK-BUILD-001`)に委ねた。
- 根拠: `03-build-requests-table.md`が「SQLiteのCHECK制約だけでは...完全に検証
  できない場合があるため、Application Service層でも同じ規則を必ず検証する」と
  明記しているため、DB層は仕様どおり部分的な制約に留めた。
- 置き換え条件: なし(仕様どおりの設計)。

### TASK-DB-002

- 対象: `script/persistence/unit_of_work.py`
- 仮定: `SqliteUnitOfWork(connection)`は既存の`sqlite3.Connection`を受け取り、
  5つのRepositoryを属性(`projects`/`sources`/`build_requests`/`jobs`/`artifacts`)
  として束ねるcontext managerとした。DB接続の生成自体は`TASK-DB-001`の
  `connect_database`の責務のまま分離した。
- 根拠: 契約6節が`SqliteUnitOfWork`を「各Repositoryを共有接続へ束ねる」ものと
  説明しており、接続生成は既存の`connect_database`と責務が重複しないように
  分離するのが自然なため。
- 置き換え条件: なし。

- 対象: `script/persistence/repositories.py`
- 仮定: 各Repositoryの`find`系methodは、IDが空/Noneの場合`AppError`を送出する
  よう統一した(元のSTEP4 placeholderには存在しない挙動)。
- 根拠: 契約の「必須入力欠落」ケース(TC-DB-002-06)を満たすために、明示的な
  validationが必要だったため。
- 置き換え条件: なし。

### 横断バグ修正: script/core/serialization.py (元TASK-CORE-002)

- 対象: `script/core/serialization.py`
- 内容: `dump_yaml`/`dump_json`が親ディレクトリを作成せず、Project作成のような
  新規ネストpathへの初回書込みで`FileNotFoundError`になっていた。`TASK-PROJECT-001`の
  Red確認時に発覚したため、`path.parent.mkdir(parents=True, exist_ok=True)`を追加した。
  `TASK-CORE-002`のテスト(`tests/test_hashing.py::test_tc_core_002_05`等)は
  既存tmp_pathへの書込みのみだったため、この不具合を検出できていなかった。
- 影響範囲確認: `tests/test_hashing.py`, `tests/test_serialization.py`を再実行し
  regressionがないことを確認済み。

### TASK-PROJECT-001

- 対象: `script/services/projects.py`
- 仮定: `ProjectService.create`は、plan file書込み前に`ProjectRepository.find`で
  既存project_idの有無を確認し、既存の場合は副作用(file書込み)前に
  `AppError(ErrorCode.CONFLICT)`を返す設計にした。
- 根拠: 事前確認なしにfileへ書込んでからDB insertの重複PK違反で失敗する設計だと、
  同一project_idへの2回目のcreate試行が、既存project(1回目)の正常なplan fileを
  上書きしたうえで失敗時cleanupにより削除してしまい、「既存正常成果物を破壊しない」
  という共通規則に違反するため。事前チェックにより、この経路を構造的に防いだ。
- 置き換え条件: なし(要求される不変性のための必須設計)。

- 対象: `script/services/projects.py`
- 仮定: `CreateProject`の`usage_purpose`に既定値`"personal_learning"`を設定した。
- 根拠: `03-project-plan-schema.md`の最小スキーマ例が同じ既定値を使用しており、
  個人学習用途がMVPの主要ユースケースであるため。
- 置き換え条件: 画面(`TASK-UI-001`)が別の既定値・選択UIを要求する場合、そちらに従う。

### TASK-SOURCE-001

- 対象: `script/schemas/source_metadata.py`
- 仮定: `media_type`未指定時、拡張子から`text`(.txt/.md)/`pdf`(.pdf)/
  `image`(.jpg/.jpeg/.png/.tif/.tiff)を推定した。未対応拡張子は
  `AppError(VALIDATION_ERROR)`とした。
- 根拠: 契約の対象範囲「text/pdf/image media type判定」を満たすための
  最小限の判定ロジック。`19-application-scope-and-mvp.md`のMVP対応形式と一致する。
- 置き換え条件: 対応形式が追加された場合、拡張子mapを追加する。

- 対象: `script/services/sources.py`
- 仮定: `SourceStatus`の遷移表を
  `registered→{processing,failed}`, `processing→{ready,review_required,failed}`,
  `ready→{}`(終端), `review_required→{ready,failed}`, `failed→{registered}`とした。
- 根拠: 契約の対象範囲「registered/processing/ready/review_required/failed遷移」
  と`02-sources-table.md`の更新責務(PDF/imageはprocessing経由、textは即ready)
  から導出した最小限の状態機械。
- 置き換え条件: 後続タスク(`TASK-OCR-001`, `TASK-PDF-001`)が追加の遷移条件を
  要求する場合、この遷移表を拡張する(縮小はしない)。

- 対象: `script/services/sources.py`
- 仮定: `list_for_project`は`TASK-DB-002`の`SourceRepository.list_by_project`
  (source_id順)を使わず、`rowid`(挿入順)で独自に問い合わせる設計にした。
- 根拠: 契約が「登録順で返す」ことを明示的に要求しており、`source_id`は
  利用者が任意に選べる文字列のため登録順と一致するとは限らないため。
- 置き換え条件: なし。

- 対象: `script/persistence/repositories.py`
- 仮定: `script/persistence/repositories.py`が独自に持っていたSTEP4 placeholderの
  `AppError`クラスを削除し、`script.core.errors.AppError`(`TASK-CORE-001`実装済み)を
  import して使うよう統一した。
- 根拠: 複数タスクが同じ概念(`AppError`)を別々に定義するのは契約の
  「本書にない公開symbolを安易に追加しない」の精神に反し、`TASK-CORE-001`が
  すでに正式なcanonical実装を提供しているため。
- 置き換え条件: なし。

### TASK-RIGHTS-001

- 対象: `script/schemas/rights.py`
- 仮定: `RightsStatus`(8値)、`UsagePurpose`(4値)、`GateDecision`(3値: allowed/
  review_required/blocked)、`Evidence`、`ConfirmedBy`を新規enum/dataclassとして
  追加した。契約表は`RightsRecord/CreditEntry/DistributionDecision`のみを列挙するが、
  `rights-and-license-management.md` 5.1〜5.4節の状態・利用目的・証拠形式を
  型として表現する必要があるため。
- 根拠: 5.3節のゲート表(8状態×4用途)を安全に実装するには、文字列直書きではなく
  型付きenumが必須。5.4節のYAML例がそのままEvidence/ConfirmedBy構造と対応する。
- 置き換え条件: なし(仕様の直接反映)。

- 対象: `script/schemas/rights.py`
- 仮定: `RightsRecord.gate_decision()`という公開契約外のmethodを追加した。
- 根拠: `RightsService`の2つのevaluateメソッドが同じゲート表参照ロジックを
  重複させないための最小限の内部委譲。`gate_decision`はpublicだが、
  `RightsRecord`自身が持つ状態(`status`+`usage_purpose`)から導出される
  純粋関数であり、新しい外部依存やDB/file副作用を持たない。
- 置き換え条件: なし。

- 対象: `script/services/rights.py`
- 仮定: 5.3節ゲート表で「拒否」は`GateDecision.BLOCKED`、「許可」は`ALLOWED`、
  「review_required」は`REVIEW_REQUIRED`とし、`unverified`+`personal_learning`の
  「許可(生成過程のみ)」注記は`evaluate_local_generation`でのみ`ALLOWED`として扱い、
  `evaluate_distribution`側では`usage_purpose`が`public_distribution`等であれば
  そもそも`BLOCKED`になるため、local/distributionの区別は`usage_purpose`の値と
  呼び出すevaluateメソッドの組み合わせで自然に表現されるとした。
- 根拠: 仕様が「生成過程のみ」許可すると明記しており、`distribution`用の
  `usage_purpose`(`public_distribution`/`commercial_distribution`)を渡す限り
  ゲート表がそのままblockedを返すため、専用の特殊分岐を追加する必要がなかった。
- 置き換え条件: なし。

### TASK-JOB-001

- 対象: `script/domain/job_state.py`
- 仮定: `22-job-lifecycle-and-recovery.md` 5.2節の状態遷移図に`queued→
  cancel_requested`を追加した(図はrunning→cancel_requestedのみ明示)。
- 根拠: 開始前のqueued Jobを取消できないと、利用者が投入直後に取消す一般的な
  操作ができなくなるため。他の遷移は図のとおり変更していない。
- 置き換え条件: 上位仕様がqueued Jobの取消を明示的に禁止した場合、この拡張を削除する。

- 対象: `script/services/jobs.py`
- 仮定: `JobService`は`TASK-APPROVAL-001`(未実装)に直接依存せず、
  `approval_gate_check: Callable[[str], bool] | None`という注入可能なhookとして
  承認gate確認を表現した(既定は常に許可)。
- 根拠: `TASK-JOB-001`の依存タスクは`TASK-BUILD-001`/`TASK-DB-002`のみで
  `TASK-APPROVAL-001`を含まない。契約の対象範囲も「approval gate hook」であり
  「approval gate統合」ではないため、実際の承認判定ロジックは後続タスクが
  hookとして注入する設計とした。
- 置き換え条件: `TASK-APPROVAL-001`実装後、Electron main等の呼び出し側で
  実際の`ApprovalService.assert_gate`をhookとして渡す。

- 対象: `script/services/jobs.py`
- 仮定: `retry`の再試行上限を`_MAX_RETRIES = 3`(parent_job_idチェーンの深さ)とした。
- 根拠: 仕様は「上限回数」の具体的な数値を規定していないため、無限再試行を防ぐ
  安全側のデフォルト値として3を設定した。
- 置き換え条件: 上位仕様が具体的な上限値を規定した場合、その値に置き換える。

- 対象: `script/services/jobs.py`
- 仮定: `request_cancel`は`cancel_requested`への遷移のみを行い、`cancelled`への
  最終確定は行わない(別途`_transition(job_id, JobStatus.CANCELLED)`が必要)。
- 根拠: 対象範囲外の「Python subprocess制御」(プロセス終了確認)なしに
  `cancelled`を確定させると、実際にはまだ動作中のprocessを誤って終了扱いする
  リスクがあるため。
- 置き換え条件: `TASK-WORKER-002`(cancel・timeout実装)が確定ロジックを提供する。

### TASK-ARTIFACT-001

- 対象: `script/services/artifacts.py`
- 仮定: 「上書き禁止」を、呼び出し側が指定した`destination_relative`に既存ファイルが
  存在する場合は`AppError(CONFLICT)`で即座に拒否する設計にした(version番号は
  サービス側が自動採番するが、実際のfile path自体は呼び出し側が決める設計を維持)。
- 根拠: 契約が「新version/pathを要求する」としており、既存ファイルへの書込み
  そのものを防げれば十分なため、path命名規則をサービス内に固定化しなかった。
- 置き換え条件: 将来`TASK-AUDIO-003`等がpath命名規則(例: version番号を
  ファイル名へ自動埋め込む)を要求する場合、そちらに統一する。

- 対象: `script/services/artifacts.py`
- 仮定: `register`が「Job/Project整合」を、`Job.build_request_id`から
  `BuildRequest.project_id`を辿って比較する方法で検証した(Artifactの
  `project_id`は`05-artifacts-table.md`が「横断検索用の非正規化列」と明記して
  いるため、正本は`build_requests.project_id`側とした)。
- 根拠: 05節の記述どおり、`artifacts.project_id`は非正規化列であり、
  真の所属関係は`job_id → build_request_id → project_id`の経路で決まるため。
- 置き換え条件: なし(仕様どおり)。

- 対象: `script/services/artifacts.py`
- 仮定: 登録失敗時(DB insert失敗等)に、直前でコピー済みのartifact fileを
  削除するcleanup処理を追加していない。
- 根拠: 対象範囲外の「Artifact削除」に該当する操作を、失敗時ロールバックの
  ためであっても追加しない方針とした。既存の正常な成果物(他のversionの
  ファイル)には一切影響しない。
- 置き換え条件: 後続タスクが失敗時cleanupを明示的に要求する場合、
  「Artifact削除」の許可範囲を含めて再定義してから実装する。

### TASK-APPROVAL-001

- 対象: `script/services/approvals.py`
- 仮定: `ApprovalService`をSQLite DBではなく、`ProjectPaths`配下の
  `project/approvals.yaml`を正本とするfile-backed設計にした
  (sqlite3.Connectionを一切受け取らない)。
- 根拠: `docs/specifications/07-approval-workflow.md`5節が明示的に
  「ファイル: project/approvals.yaml」を承認記録の正本と定義しており、
  `docs/db/`配下の5テーブル一覧にも承認用テーブルは存在しないため。
  既存の`ProjectPaths.resolve_relative`/`dump_yaml`/`load_yaml`
  (`TASK-FILE-001`/`TASK-CORE-002`)をそのまま再利用できる。
- 置き換え条件: なし(仕様どおり)。

- 対象: `script/schemas/approvals.py`
- 仮定: 07節10節の変更種別→無効化対象gateマッピングを、9種類の
  文字列定数(`materials_list_changed`/`project_plan_changed`/
  `chapter_spec_changed`/`script_text_changed`/`tts_text_changed`/
  `voice_profile_changed`/`character_profile_changed`/
  `tts_engine_version_changed`/`mp3_tag_only_changed`)として
  `_INVALIDATION_TABLE`に固定した。
- 根拠: 仕様の表は日本語の変更内容の説明であり、呼び出し側(将来の
  `TASK-PIPELINE-001`等)が指定するための安定したキーが必要なため、
  意味を保ったまま英語snake_caseのenum的定数へ変換した。
  `mp3_tag_only_changed`は仕様どおり空タプル(無効化対象なし)とした。
- 置き換え条件: 後続タスクが変更検知のトリガーを実装する際、この
  定数名をそのまま使うか、必要なら`ApprovalGate`同様の`str, Enum`へ
  昇格させる。

- 対象: `script/services/approvals.py`
- 仮定: `invalidate_changed_targets`は、対象gateが`approved`以外
  (draft/review_pending/changes_requested/revised/rejected/invalidated)
  の場合は無条件でスキップし(既にapprovedでないものを無効化する
  意味がないため)、実際にinvalidatedへ遷移したgate名のみを
  戻り値のlistへ含める。
- 根拠: 仕様は「approved対象のhashを変更した場合の無効化」のみを
  規定しており、非approved状態への影響には言及していないため、
  安全側(状態を壊さない側)の最小解釈を採用した。
- 置き換え条件: なし(仕様どおり)。

### TASK-INGEST-001

- 対象: `script/source_processing/orchestrator.py`
- 仮定: `process(source)`の`source`引数の型として、公開契約表にない
  `IngestSource`(`source_id`/`media_type`/`path`/`context`)を新規追加した。
- 根拠: 公開契約は`MaterialInputOrchestrator.process(source) -> ProcessingResult`
  としか書かれておらず、`source`の具体的な形状は未定義である。他タスク
  (`TASK-BUILD-001`の`CreateBuildRequest`、`TASK-ARTIFACT-001`の
  `RegisterArtifact`等)と同様に、公開methodの引数を表す最小限の入力
  dataclassを1件追加する既存パターンを踏襲した。
- 置き換え条件: 後続タスク(`TASK-SOURCE-002`等)が`Source`ドメインモデル
  (`script/domain/models.py`)と直接連携する形へ拡張する場合、その形状に
  合わせて再検討する。

- 対象: `script/source_processing/orchestrator.py`
- 仮定: 「未知media」(TC-INGEST-001-02)を、`epub`/`video`/
  `audio_recording`/`kindle_capture`の恒久的対象外media typeと、単に
  未登録のmedia typeの両方について、同一の`AppError(VALIDATION_ERROR,
  "unsupported_media_type: ...")`で拒否する設計にした。
- 根拠: `19-application-scope-and-mvp.md`5.5節が動画・録音・Kindle操作を
  製品の恒久的対象外、`epub-text-extraction.md`をpost-MVPと明記しており、
  MVPの本タスクではこれらにadapterを登録する経路自体を用意しないため、
  「未登録」と「恒久的対象外」を呼び出し側から見て区別する必要がない。
- 置き換え条件: `TASK-EPUB-001`(post-MVP)が有効化される際、`epub`を
  `_PERMANENTLY_UNSUPPORTED_MEDIA_TYPES`から外し、通常のadapter未登録
  判定へ合流させる。

- 対象: `script/source_processing/text_ingestion.py`
- 仮定: `_normalize`を「改行をLFへ統一し、各行の行末空白を除去する」
  最小限の処理とし、`structured_text`はtext素材については
  `normalized_text`と同一内容にした。
- 根拠: 本タスクの対象範囲は「original/extracted/normalized/structured
  handoff」の枠組みを提供することであり、詳細な正規化・構造化ルールは
  対象外の`source-preprocessing.md`が定義する範囲のため、
  最小限の可逆的処理に留めた。
- 置き換え条件: `source-preprocessing.md`を実装対象とする後続タスクが、
  より詳細な正規化ルール(見出し検出、段落分割等)を`_normalize`または
  `structured_text`の生成へ追加する。

### TASK-IMAGE-001

- 対象: `script/source_processing/images/ingestion.py`
- 仮定: `ImageIngestionService.__init__`に公開契約にない`destination_dir`
  引数を追加した。
- 根拠: `image-material-ingestion.md`6節は`sources/originals/<source_id>/
  images/`への保存を要求しているが、本タスクの公開契約は`ingest(paths, *,
  explicit_order=None)`のみでProject/Source文脈を受け取らない。
  `TASK-ARTIFACT-001`等と同様、副作用の書込み先を明示するための最小限の
  constructor引数として追加した。
- 置き換え条件: 後続タスク(`TASK-SOURCE-002`等)が`ProjectPaths`経由の
  正式な保存先解決に統合する場合、その方式に合わせて置き換える。

- 対象: `script/source_processing/images/ingestion.py`
- 仮定: 「壊れた画像検出」を、全入力画像を検証してから初めて1件でも
  コピーを開始する two-phase設計(1件でも形式違反・壊れていれば、
  他の正常画像も含めて一切書き込まない)にした。
- 根拠: `image-material-ingestion.md`13節はファイルを開けない・0 byte等を
  「Error」category(Warningより重い、処理停止相当)に分類しており、
  「副作用を開始する前に安定したvalidation errorを返す」という本タスクの
  共通規則(TC-IMAGE-001-08と同型の要求)と整合させるため。
- 置き換え条件: 大量画像の部分成功を許容する運用要件が明確になった場合、
  per-image try/exceptで部分成功+per-pageのfailed flagを返す設計へ変更する。

- 対象: `script/source_processing/images/ingestion.py`
- 仮定: EXIF位置情報(GPS IFD、tag 34853)は「有無」のみを
  `exif_location_present`という文字列flagとして`quality_flags`/`warnings`
  へ記録し、実際の緯度経度等の値は一切読み取り後も保持・返却しない設計にした。
- 根拠: 12節が`exportable_metadata`に位置情報を既定で含めないことを要求して
  おり、「内部warningは保持しても公開成果物に位置情報を含めない」という
  TC-IMAGE-001-03の要求を満たす最も安全な実装は、そもそも座標値自体を
  読み取り結果として保持しないことだと判断した。
- 置き換え条件: なし(仕様どおり)。

- 対象: `script/source_processing/images/ingestion.py`
- 仮定: 原画像への「上書き」を、既存destinationファイルの内容hashと
  新規コピー元の内容hashが一致する場合は冪等成功(no-op相当)とし、
  内容が異なる場合のみ`AppError(CONFLICT)`で拒否する設計にした。
- 根拠: TC-IMAGE-001-09(再実行時の決定性)が同一入力での2回目の`ingest()`
  実行も成功することを要求している一方、13節は「originalを上書きしようと
  した」をErrorと規定しており、両者を両立させるには「内容が同じか」で
  上書き可否を判定する必要がある。
- 置き換え条件: なし(両仕様の両立に必要な解釈)。

### TASK-IMAGE-002

- 対象: `script/source_processing/images/preprocess.py`
- 仮定: `ImagePreprocessor.__init__`に公開契約にない`destination_dir`
  引数を追加し、`split_spread(page)`は`page.derivative_path`(既存の
  派生PNG)を入力とし、その親directoryへ`<stem>-left.png`/
  `<stem>-right.png`として左右を書き出す設計にした(`split_spread`
  自体には追加の出力先引数を持たせていない)。
- 根拠: `TASK-IMAGE-001`と同じ理由(`destination_dir`要否)に加え、
  `split_spread(page) -> tuple[...]`という公開契約は引数が`page`のみで
  あり、出力先を別引数で受け取れない。既存派生物のpathを起点にすることで
  契約signatureを変更せずに済ませた。
- 置き換え条件: 後続タスクが専用の出力先解決(`ProjectPaths`等)を要求する
  場合、その方式へ統合する。

- 対象: `script/source_processing/images/quality.py`
- 仮定: `assess_image_quality`は「blank_candidate」(グレースケールの
  標準偏差が閾値未満)と「low_resolution」(画素数が閾値未満)の2種類のみ
  具体的に検出し、契約説明文にある「blur/skew/contrast/vertical」候補は
  実装しなかった。
- 根拠: `image-material-ingestion.md`19節が「ぼけ・傾き・反射の具体的閾値」
  を実装後にprofileへ切り出す前提の未決定事項と明記しており、本タスクの
  必須テストケース(TC-IMAGE-002-02)もblank候補のみを対象としている。
  根拠のない閾値を先回りで実装すると、未検証のまま「対応済み」に
  見えてしまう方が悪いと判断した。
- 置き換え条件: 実測に基づく閾値がprofileとして確定した場合、
  blur/skew/contrast/vertical検出を追加する。

### TASK-PDF-001

- 対象: `requirements.txt`
- 仮定: `PyMuPDF==1.24.14`(未導入だったため新規追加)と`pypdf==6.10.2`
  (環境に既存installだったversionをそのまま`requirements.txt`へ固定)を
  追加した。
- 根拠: `pdf-direct-text-extraction.md`5.2節が両ライブラリを
  primary/secondary候補として明示し、本タスクの公開契約が
  「PyMuPDF primary adapter」「pypdf secondary adapter境界」を
  テストケースとして要求しているため、いずれか一方の欠如では契約を
  満たせない。最終的な採用ライブラリの確定はbenchmark実施後(仕様
  13節)であり、本タスクでは両方を選択可能なadapterとして実装した。
- 置き換え条件: benchmark実施後にどちらか一方へ一本化する仕様変更が
  承認された場合、`extractor`引数の既定値・選択肢を見直す。

- 対象: `script/source_processing/pdf/extract.py`
- 仮定: `should_fallback_to_ocr(report) -> bool`の引数名は仕様書のSTEP4
  stubでは`report`だが、実装上は単一の`PdfPage`を受け取る関数として
  実装した(`PdfExtractionReport`全体ではない)。
- 根拠: TC-PDF-001-03の期待が「該当pageだけOCR候補となる」という
  page単位の判定であり、`PdfExtractionReport`全体に対して単一の
  bool を返す設計では「どのpageが該当するか」を表現できない。
  STEP4 stubの引数名`report`はauto-generatedの汎用placeholderであり、
  正本である契約表の説明文(「空・極少文字等を根拠に」)がpage単位の
  判定を要求していると判断した。
- 置き換え条件: 後続タスクが`PdfExtractionReport`全体を受け取る
  上位APIを別途必要とする場合、`should_fallback_to_ocr`をラップする
  形で追加する(既存signatureは変更しない)。

- 対象: `script/source_processing/pdf/extract.py`
- 仮定: 複数段組みの読み順推定を「block bboxのy座標(丸め)→x座標」の
  単純ソートのみとし、列(column)検出などの高度なアルゴリズムは
  実装しなかった。
- 根拠: `pdf-direct-text-extraction.md`5.3節が「初期候補」として
  同様の単純な位置ベース推定を明示しており、13節でも「複数段組み
  読み順推定の具体的アルゴリズム」を未決定事項として明記しているため、
  仕様が要求する以上の複雑さを先回りで実装しなかった。
- 置き換え条件: 複数段組みのread order検証が必要な後続タスクが
  具体的なアルゴリズムを確定した場合、置き換える。

### TASK-OCR-001

- 対象: `tests/conftest.py`(`TASK-DEV-001`所有の共通fixture)
- 仮定: STEP3placeholderだった`tesseract_connectivity_gate`fixtureの本体を
  実装した(`TASK-OCR-001`の変更範囲外だが、他タスクが担当しない
  1対1専用fixtureのため)。`require_environment("TESSERACT_CMD")`で
  設定確認(未設定はskip)→`OcrClient.check_runtime()`で疎通確認
  (失敗は`pytest.fail`)という2段階にした。
- 根拠: `tests/conftest.py`のdocstringが「real connectivity
  implementations are created in STEP4/STEP7」と明記しており、
  本タスクが対応するTesseract専用のgateである。既存の公開境界
  (fixture名、設定未確認時はskipという契約)は変更していない。
- 置き換え条件: なし(仕様どおり)。

- 対象: `script/source_processing/ocr/client.py`
- 仮定: `OcrClient.recognize`はplain textではなくTSV出力モード
  (`tesseract <image> stdout -l <lang> tsv`)を使用し、word単位の
  confidence列を平均してpage全体のconfidence(0.0-1.0)を再構成した。
- 根拠: `ocr-and-scanned-pdf.md`5.5節のpage result例が
  `"confidence": {"overall": 0.87}`を要求しており、tesseractの
  既定stdout出力(plain text)にはconfidenceが含まれないため、
  TSV出力形式が必須だった。
- 置き換え条件: benchmark実施後、より詳細なconfidence集計方式
  (region単位のlow_confidence_regions等)が必要になった場合、
  TSVのbbox列(left/top/width/height)も利用して拡張する。

- 対象: `script/source_processing/ocr/pipeline.py`
- 仮定: 「table/code/math/figure候補page」を、`OcrPageRequest`に
  公開契約にない`high_risk_hint`(`formula`/`code`/`table`/`diagram`/
  `figure`のいずれか)という入力fieldとして表現し、この値が
  設定されたpageは信頼度に関わらず常に`review_required=True`にした。
- 根拠: 本タスクの対象範囲は「table/code/math/figure flagの付与」
  であり、実際に画像内容から高リスク領域を検出するアルゴリズム
  (5.4節)は対象外(「対象外: 高リスク要素の自動確定」)。上流
  (呼び出し側またはTASK-IMAGE-002等)が既に候補と判定した情報を
  受け取り、それをreview_required化する境界として設計した。
- 置き換え条件: 高リスク領域の自動検出を担当する後続タスクが
  確定した場合、そちらの出力を`high_risk_hint`として渡す。

- 対象: `script/source_processing/ocr/pipeline.py`
- 仮定: 「confidence全体が閾値未満 -> review_required」の閾値を
  `_LOW_CONFIDENCE_THRESHOLD = 0.6`とした(仕様は具体的な数値を
  規定していない)。
- 根拠: `ocr-and-scanned-pdf.md`14節が「信頼度閾値の実測による調整」を
  未決定事項と明記しており、5.5節のOCR page result例が
  `confidence.overall: 0.87`を正常値として示していることから、
  それより十分低い値を安全側の暫定閾値として採用した。
- 置き換え条件: benchmark実施後にprofile化された閾値へ置き換える。

### TASK-SOURCE-002

- 対象: `tests/test_source_chunking.py`, `tests/test_source_manifest.py`
- 仮定: STEP3 test stubの`test_file`割当では、TC-SOURCE-002-05
  (「繰返しheader/footer除去」)が`test_source_chunking.py`へ、
  TC-SOURCE-002-06(「footnote分離」)と一部TC-07相当の説明が
  `test_source_manifest.py`側へ割り当てられているが、実際にこれらの
  機能は`normalize_text`(normalize.py)が提供する。テストファイルの
  物理的な配置はSTEP3契約の割当をそのまま踏襲しつつ、対象関数は
  `normalize_text`をimportして検証した(caseの意味・title・Given/When/
  Thenは変更していない)。
- 根拠: 本タスクの契約書がテストケースの一覧を「本タスクでは次のcase
  IDをすべて本実装する」と明記しており、file割当自体はSTEP3で既に
  固定されている。事前のTASK-INGEST-001/TASK-IMAGE-001等でも同様の
  「テスト内容の実体と割当fileが厳密には一致しない」パターンが
  繰り返し見られ、都度、公開契約表の実体(この場合は`normalize_text`が
  提供する機能)を優先して実装・検証する方針を一貫して採用している。
- 置き換え条件: なし(既存の一貫した解釈方針を踏襲)。

- 対象: `script/source_processing/normalize.py`
- 仮定: 「繰返しheader/footer除去」を、同一内容の行が2回以上出現し、
  かつ80文字以下の短い行である場合にheader/footer候補とみなし、
  最初の出現だけを残して以降を除去する簡易heuristicとした。
- 根拠: `source-preprocessing.md`13節が「header/footerの既知パターン
  ルールの具体的な実装(正規表現辞書等)」を未決定事項と明記しており、
  ページ単位のheader/footerパターンを厳密に検出する仕組みは対象外の
  情報(ページ境界)を必要とする。プレーンテキスト入力から決定的に
  導出できる最小限のheuristicとして、反復検出+短い行という条件を
  採用した。
- 置き換え条件: header/footerの既知パターン辞書やページ境界情報が
  利用可能になった後続タスクが、より精密な検出ロジックへ置き換える。

### TASK-SOURCE-003

- 対象: `script/services/source_review.py`
- 仮定: review issueの状態を`open→resolved`/`open→corrected`/
  `open→reprocessing_requested`の3遷移のみ許可し、いずれも`open`以外
  からは一切遷移できない(終端状態)設計にした。`mark_resolved`/
  `apply_correction`/`require_reprocessing`のいずれも、対象issueが
  `open`でなければ`AppError(CONFLICT)`で拒否する。
- 根拠: TC-SOURCE-003-07の期待(「必要な承認が揃う場合だけ後工程へ進み、
  未承認・invalidated・changes_requestedでは安定errorで停止する」)が
  `TASK-APPROVAL-001`と同型の承認gate文言であり、同タスクで採用した
  「open以外からの操作を一律拒否する」設計方針をここでも踏襲した。
  1つのissueに対して複数の解決経路(修正・再処理・問題なし)が
  競合しないようにする意図もある。
- 置き換え条件: 1つのissueに対して複数回の修正(revision追記)を
  許可する要件が明確になった場合、`corrected`から`corrected`への
  自己遷移を許可するよう拡張する。

- 対象: `script/services/source_review.py`
- 仮定: `apply_correction`が書き込む新revisionのファイル名を
  `<destination_dir>/<source_id>/revision-NNNN.md`(4桁ゼロ埋め、
  原本を暗黙のrevision 1とみなし2から採番)という命名規則にした。
- 根拠: 公開契約に具体的な保存先・命名規則の指定がなく、
  `TASK-IMAGE-001`/`TASK-IMAGE-002`で採用した「`destination_dir`を
  constructor引数として受け取り、決定的なファイル名で追記専用に
  保存する」という既存パターンを踏襲した。
- 置き換え条件: `source-storage-and-common-schema.md`の
  `sources/structured/<source_id>/`配下への正式な保存先解決が
  後続タスクで確立された場合、その方式へ統合する。

### 横断バグ修正: script/source_processing/pdf/extract.py(元TASK-PDF-001、Docker回帰で発見)

- 対象: `script/source_processing/pdf/extract.py`, `requirements.txt`
- 問題: Phase3クローズ時のDocker全体回帰で
  `tests/test_pdf_direct_extraction.py::test_tc_pdf_001_01`が失敗した。
  host(Windows)では`cryptography`packageが他の依存の副次installとして
  既に存在していたため気づかなかったが、クリーンなDocker imageでは
  `pypdf.PdfReader()`がAES暗号化PDFのmetadataを読むだけで
  `pypdf.errors.DependencyError('cryptography>=3.1 is required for AES
  algorithm')`を送出し、`_extract_with_pypdf`の汎用except節が
  これを「cannot open pdf」という別の(誤った)error messageへ変換して
  いた。
- 修正: `requirements.txt`へ`cryptography==47.0.0`を追加(pypdfが
  暗号化PDFのmetadata検査に必要とする復号backend)。加えて
  `_extract_with_pypdf`に`pypdf.errors.DependencyError`専用のexcept節を
  追加し、backend欠如時も(復号を試みることなく)
  `unsupported_password_protected_pdf`として安定的に扱うよう防御的に
  修正した。
- 確認: Docker imageを再buildし、`docker compose run --rm test python -m
  pytest -ra -m "not integration_smoke and not integration_live and not
  performance and not resilience"`で193 passed, 7 skipped
  (`test_container_contract.py`のdocker CLI未検出skipのみ、コンテナ内で
  実行しているため想定どおり)を確認。host側の200 passedと合致する。
- 教訓: `requirements.txt`への依存追加後は、hostだけでなくクリーンな
  Docker imageでの回帰も必須で実施する(hostに偶然存在する transitive
  dependencyが問題を隠す場合があるため)。

### TASK-AI-001

- 対象: `script/ai_clients/gemini/client.py`
- 仮定: `GeminiClient`に公開契約にない`session_get`/`session_post`/
  `sleep`というDI hook引数を追加した(既定はそれぞれ`requests.get`/
  `requests.post`/`time.sleep`)。
- 根拠: 通常テストは外部接続してはならず、かつ429/5xx retryの
  実際のsleep(既定`GEMINI_RETRY_WAIT_SEC=5`秒、指数バックオフ)を
  実時間で待つとテストが極端に遅くなる。他タスク(`TASK-OCR-001`の
  `runner`、`TASK-JOB-001`の`approval_gate_check`等)で既に採用している
  DI hookパターンを踏襲し、subprocess/HTTP呼出しと待機処理を
  注入可能にした。
- 置き換え条件: なし(仕様どおり、外部接続なしのテスト実行に必須)。

- 対象: `script/ai_clients/gemini/client.py`
- 仮定: 既存のlegacy関数(`call_gemini`等)は一切変更せず、そのまま
  再利用可能な内部helper(`build_endpoint`/`extract_text_from_candidate`/
  `_is_retryable_status_code`/`_compute_retry_wait_sec`/
  `_summarize_response_error`)として`GeminiClient.generate`から呼び出す
  設計にした。`call_gemini`自体は`GeminiClient`から呼ばれず、独立した
  関数として保持されている。
- 根拠: 契約が「現行HTTP処理を共通結果・errorへ適合する」と明記しており、
  既存のendpoint構築・retry判定・error要約ロジックは正しく動作している
  ため重複実装を避けた。`call_gemini`自体を`GeminiClient.generate`の
  内部実装として呼び出さなかったのは、`call_gemini`が文字列を直接返し
  例外もRuntimeErrorで型付けされていないため、共通契約(`AIResult`/
  `AIClientError`)への変換にはより細かい制御が必要だったため。
  既存の`merged_text_fixer.py`/`mindmap_builder.py`は引き続き
  `call_gemini`を直接使用でき、影響を受けない。
- 置き換え条件: 後続タスクが`call_gemini`の呼び出し元をすべて
  `GeminiClient`経由へ移行する場合、`call_gemini`を`GeminiClient.generate`の
  薄いwrapperとして再定義することを検討する(本タスクの変更許可範囲外の
  ため今回は実施しない)。

### TASK-AI-002

- 対象: `script/ai/routing.py`
- 仮定: `AIRouter.resolve(task_class, policy)`の`task_class`引数を、
  具体的なtask_type(例: "chapter_draft")ではなく論理層名そのもの
  (`economy_structuring`/`standard_generation`/`high_assurance_review`)
  として扱う設計にした。
- 根拠: 公開契約の説明文が「論理層から物理provider/modelを解決」と
  明記しており、`docs/specifications/examples/ai-model-policy.yaml`の
  `tiers`直下のkeyも論理層名である。個別task_type→論理層の対応表
  (`ai-model-policy.yaml`の`tiers.*.task_types`)は本タスクの対象範囲
  (「対象外: 各生成業務prompt」)の外にあるcaller側の責務と判断した。
- 置き換え条件: 個別task_typeから論理層への解決を担当する後続タスクが
  確定した場合、その解決結果を`task_class`として`resolve()`へ渡す
  形を維持する(signatureは変更しない)。

- 対象: `script/ai/budget.py`
- 仮定: `reserve(estimate)`(呼出し前の推測値によるpre-check)と
  `record(usage)`(呼出し後の実測値記録)を明確に分離し、`reserve`は
  `spent_usd`/`records`を一切変更しない(判定のみ)設計にした。
- 根拠: 16節「usage情報が取得できない場合はnullとし、推測値を実測値
  として保存しない」および12節のcache re-use条件との整合を踏まえ、
  「予算判定のための見積り」と「実際に発生した費用の記録」を型
  (`UsageEstimate.is_measured`)とmethodの両方で区別する必要があった。
- 置き換え条件: なし(仕様どおり)。

### TASK-AI-003

- 対象: `script/pipelines/source_analysis.py`
- 仮定: 「同topicでのsource conflict」を、`SourceChunkInput`に公開契約に
  ない`conflicting: bool = False`という入力fieldとして表現し、
  この値がTrueのchunkを含むtopicは無条件でcoverage状態を`conflict`
  (`next_action="human_review_required"`)にする設計にした。
- 根拠: 本タスクの対象範囲は「conflictを黙って解決せずreviewへ送る」
  ことであり、実際に複数資料の主張内容を比較して矛盾を検出する
  アルゴリズム自体は対象外(「対象外: 最終curriculum」相当の判断ロジックは
  別タスクの責務)。上流(人間または別の分析工程)が既に矛盾候補と
  判定した情報を受け取り、それを黙って解決しないための境界として設計した
  (`TASK-OCR-001`の`high_risk_hint`と同型のパターン)。
- 置き換え条件: 資料間矛盾の自動検出を担当する後続タスクが確定した
  場合、その出力を`conflicting`として渡す。

- 対象: `script/pipelines/source_analysis.py`
- 仮定: `TopicIndex`の構築(chunkをtopic_idでグルーピングする処理)は
  AI呼出しを伴わない決定的な処理とし、AI(`AIClient.generate`)は
  `SourceSummary`(資料ごとの要約)生成にのみ使用する設計にした。
- 根拠: 契約の対象範囲「chunk選択」「economy structuring」は
  source summaryの生成コストを指しており、topic_idへの割当自体は
  各chunkが既に保持する`topic_ids`(上流のtopic抽出結果)を集約する
  だけで決定的に導出できる。ここでAI呼出しを追加すると「資料全文を
  繰り返し送信しない」という4.4節の原則にも反する余分な呼出しに
  なると判断した。
- 置き換え条件: topic_idの割当自体をAIで再判定する要件が明確になった
  場合、`_build_topic_index`にAI呼出しを追加する。

- 対象: `script/schemas/chapter_spec.py`(`TASK-CURRICULUM-001`)
- 仮定: `ChapterSpec.validate()`の公開契約は引数なし(`validate()`)だが、
  「未知topic/source参照」を検証するには「何が既知か」の情報が必要。
  この情報を`validate()`の引数として渡すのではなく、`known_topic_ids`/
  `known_source_ids`という2つのコンストラクタ引数(frozenset)として
  `ChapterSpec`自体に持たせる設計にした。
- 根拠: 公開契約の関数signature(`ChapterSpec.validate()`)を変更せずに
  参照整合検証を実現する必要があった。chapter-spec.yamlは1つの
  projectのcurriculum/topic mapに対して生成されるものであり、
  生成時点で「そのprojectの既知topic/source一覧」は決定済みである
  ため、コンストラクタ時点で確定させても仕様上の後方互換性は失われない。
- 置き換え条件: `ChapterSpec`をプロジェクト全体のcurriculum/topic map
  から独立して(既知集合を渡さずに)構築・検証する要件が生じた場合、
  `known_topic_ids`/`known_source_ids`をrepositoryから遅延解決する
  方式に切り替える。

- 対象: `script/pipelines/curriculum.py`(`TASK-CURRICULUM-001`)
- 仮定: `analysis`引数の型は`TASK-AI-003`の`SourceAnalysisBundle`
  (`script.pipelines.source_analysis`)をそのまま採用した。
  `project_plan`引数は`Mapping[str, object]`として最小限
  (非空であること)のみを検証し、`03-project-plan-schema.md`の
  個別フィールド(`planning_stage`等)への依存は導入していない。
- 根拠: 本タスクの扱う範囲は「topic map schema, curriculum order,
  learning outcomes, coverage反映, 章ID/order, source_ids,
  AI tier指定, review_pending成果物」であり、project_planの
  詳細なplanning_stage遷移ロジックはTASK-PROJECT-001側の責務。
  `project_plan`を空でないMappingとしてのみ受け取ることで、
  依存関係を最小限にしつつ将来の詳細スキーマ追加にも後方互換に
  対応できる。
- 置き換え条件: `project_plan`の特定フィールド(例:
  `planning_stage`が特定の値でなければcurriculum生成を拒否する等)
  を検証する要件が明確になった場合、`CurriculumPipeline.generate`に
  該当フィールドの検証を追加する。

- 対象: `script/schemas/script.py`(`TASK-SCRIPT-001`)
- 仮定: `05-script-segment-schema.md`12節の「claim ref欠落はerror」を
  `ScriptSegment`の構造的検証としては強制しなかった。
- 根拠: 本タスクの扱う範囲には「legacy TXT adapter境界」が明示的に
  含まれており、`segment_legacy_text`が生成するsegmentは定義上
  claim_refs/source_refsを持たない。claim ref必須ルールをdataclass
  レベルで強制すると、この明示的に対象内の機能自体が構築不能になる
  矛盾が生じる。「出典verified化」は対象外と明記されているため、
  claim/source refの有無・妥当性検証は後続タスク(`TASK-CLAIM-001`
  や承認workflow)の責務と判断した。
- 置き換え条件: `TASK-CLAIM-001`等でclaim ref必須ルールの適用範囲
  (segment_type別の要否等)が確定した場合、該当ルールを
  `ScriptSegment.__post_init__`または専用のvalidateへ追加する。

- 対象: `script/pipelines/draft_generation.py`(`TASK-SCRIPT-001`)
- 仮定: AI応答から「どのsource_idを引用したか」を判定するため、
  system_instructionで`SOURCE_REFS: <ids>`/`TEXT: <text>`という
  2行形式を明示的に指示し、応答をこの形式で決定的に解析する設計にした。
  未指定/解析不能な場合はchunk自身のsource_idを既定値として使う。
- 根拠: TC-SCRIPT-001-02(指定外資料)を検証するには、AI応答が
  どのsource_idに基づいているかをprogram的に判定できる必要がある。
  自由形式の生成テキストから事実の出典を機械的に特定することは
  本タスクの範囲外(自然言語のfact-checking相当)であるため、
  prompt/response間の軽量な構造化contract(TASK-AI-001の
  `AIRequest.system_instruction`経由)で表現した。
- 置き換え条件: 構造化出力(JSON mode等)を伴うAI応答契約が別タスクで
  確定した場合、`_parse_ai_segment_response`をその形式へ置き換える。

- 対象: `script/schemas/claims.py`/`script/pipelines/claims.py`(`TASK-CLAIM-001`)
- 仮定: `06-claims-and-sources.md`6節の`generated_analogy`/
  `generated_explanation`/`opinion`は「事実主張とは別の検査を行う」と
  あるが、その別検査(例え話の同一視・誤解チェック等、10節)自体は
  実装せず、これらのclaim_typeは`FACTUAL_CLAIM_TYPES`から除外して
  `source_evidence`なしでも人間承認だけでverified化できる設計にした。
- 根拠: 本タスクの扱う範囲には「例え話の検証」(10節相当)が
  明記されておらず、対象外の「原稿変換」寄りの検査に近い。
  一方で「人間承認なしverified禁止」は扱う範囲に明記されているため、
  claim_type種別に関わらず人間承認は一律で必須とした。
- 置き換え条件: 例え話の同一視・誤解チェックを担当する後続タスクが
  確定した場合、`generated_analogy`等のverify()判定にその検査結果を
  組み込む。

- 対象: `script/pipelines/claims.py`(`TASK-CLAIM-001`)
- 仮定: `ClaimPipeline.verify()`のconflict claim処理で、
  `TASK-AI-002`の`AIRouter`/`ModelPolicy`が渡されていれば
  `high_assurance_review` tierの解決を試みるが、解決の成否に関わらず
  最終的なstatusは常に`human_review_required`に固定した(高性能モデル
  解決に成功しても、その場でAIにconflictを自動解決させる処理は
  実装していない)。
- 根拠: 06-claims-and-sources.md 9節「システムは黙って一方を選ばない」
  という原則を最優先し、「高保証未設定時停止」(扱う範囲)は
  `AIRouter.resolve`が`AppError(EXTERNAL_UNAVAILABLE)`を送出しても
  `verify()`全体を失敗させず、該当claimを`human_review_required`に
  留める形で表現した。実際に高性能モデルで矛盾を解消させる判断ロジック
  は「法律判断」同様に人間判断の領域に近く、対象外と判断した。
- 置き換え条件: high_assurance tierによる自動的な矛盾解消(人間の
  最終承認を経た上での)フローが別タスクで確定した場合、
  `verify()`のconflict分岐にその結果を反映する。

- 対象: `script/schemas/profiles.py`(`TASK-PROFILE-001`)
- 仮定: `08-character-profile-schema.md`はcharacter profileの承認状態
  (status)を定義していない。「未承認profile選択拒否」(扱う範囲)を
  満たすため、`CharacterProfileStatus`(candidate/approved/rejected)を
  最小の3値で新設した。
- 根拠: `CharacterProfileRepository.select`が承認状態を検証する
  という公開契約("承認状態と用途を検証して選択する")を満たすには
  何らかのstatus概念が必須だが、承認済み仕様側に定義がない。
  voice profileの6状態モデル(09-voice-profile-schema.md 4節)を
  流用すると、character profileには不要な試聴関連の状態
  (on_hold/deprecated等)まで持ち込むことになるため、必要最小限の
  3値に留めた。
- 置き換え条件: character profile向けの承認状態がSTEP2契約として
  別途定義された場合、この3値enumをその定義へ置き換える。

- 対象: `script/schemas/profiles.py`(`TASK-PROFILE-001`)
- 仮定: `VoiceProfileStatus`は`09-voice-profile-schema.md`4節
  (承認済み仕様)の6状態(provisional/approved/
  approved_for_limited_use/on_hold/rejected/deprecated)を採用し、
  `docs/spec-proposals/task/3_voice-profile-default-values.md`
  (status: draft、未承認)8節のより詳細な試聴段階語彙
  (candidate/screening_passed/screening_rejected/detailed_review等)
  は採用しなかった。
- 根拠: spec-proposal task 3自身が「話者ごとの最終速度、音量、
  無音時間、採用スタイルは試聴後に確定する」と明記し、本タスクの
  対象外に「人間による最終試聴値の確定」を明記している。
  試聴段階を管理する詳細な状態機械は、この確定作業(未承認・
  対象外)の一部であり、本タスクが読み込む対象は承認済みspec
  (09番)が定義する最終的なvoice profile状態だけで十分と判断した。
- 置き換え条件: spec-proposal task 3が承認され
  `docs/specifications/voice-profile-default-values.md`として
  正式化された場合、試聴段階の状態遷移を別途表現する設計を検討する。

- 対象: `script/profiles/voices.py`(`TASK-PROFILE-001`)
- 仮定: `VoiceProfileRepository.list_available()`は
  `status=approved`のVOICEVOX profileだけを返し、
  `approved_for_limited_use`は含めなかった。
- 根拠: 09-voice-profile-schema.mdは
  「使用条件を満たすapproved_for_limited_use」も正式成果物に使用可能と
  するが、「使用条件を満たす」の判定(作品・用途ごとの許可)は
  本タスクの契約に含まれる情報だけでは決定できない
  (`select()`では明示的にvoice_profile_idを指定するため許可済み
  として扱うが、`list_available()`は無条件の一覧のため、
  条件付き許可のprofileを含めると「未承認profile選択拒否」の原則を
  弱める恐れがあると判断した)。
- 置き換え条件: 作品・用途ごとの`approved_for_limited_use`許可判定を
  担当する後続タスクが確定した場合、その許可情報を
  `list_available()`の引数として受け取り対象へ含める。

- 対象: `script/pipelines/narration.py`(`TASK-NARRATION-001`)
- 仮定: `apply_character()`は、character profileの承認状態検証と
  speaker(`character_id`)割り当てだけを行い、
  08-character-profile-schema.mdが定義する語尾変換アルゴリズム
  (`speech_style.sentence_endings`の機械的置換、`character_style
  .maximum_consecutive_styled_endings`による連続制限等)は実装せず、
  `text`を常に不変のまま返す設計にした。
- 根拠: `TASK-PROFILE-001`で実装した`CharacterProfile`
  (`script/schemas/profiles.py`)は、承認状態(`status`)と
  `style_enabled`/`default_strength`/`maximum_consecutive_styled
  _endings`のような集約設定は持つが、`speech_style.sentence_endings
  .preferred`のような語尾候補データ自体を保持していない。
  このデータなしに安全な語尾置換を実装すると「MUST NOT: 語尾だけを
  機械的に全置換する」「声のキャラクター名から口調を推測する」に
  抵触する恐れがあるため、本タスクの対象10 caseのいずれも実際の
  text書き換えアルゴリズムを検証しておらず(TC-04は解決/gating機構を
  検証)、textを不変に保つ選択がもっとも安全と判断した。
- 置き換え条件: `CharacterProfile`へ`speech_style`の具体的な語尾候補
  データが追加された場合、`apply_character()`にMUST/MUST NOTを
  満たす語尾変換ロジックを追加する。

- 対象: `script/pipelines/semantic_review.py`(`TASK-NARRATION-001`)
- 仮定: `SemanticReview.compare()`はAI呼出しを行わず、数値token集合・
  否定語マーカー・条件語マーカーの出現有無差を検出する決定的な
  heuristicとして実装した。
- 根拠: TC-NARRATION-001-02の対象は「数値・否定・条件を変更した変換」
  という明白な差異の検出であり、これは正規表現・キーワード照合で
  決定的に検出できる。自然言語の意味論的同値性を厳密に判定する
  fact-checking相当のAI検証は本タスクの対象外(既存のclaim検証
  (`TASK-CLAIM-001`)や、承認済み仕様が要求する範囲を超える)と
  判断した。
- 置き換え条件: より高度な意味差検出(言い換えによる意味変化等)が
  要件として明確になった場合、AI(high_assurance tier等)による
  比較をheuristicの後段に追加する。

- 対象: `script/pipelines/narration.py`(`TASK-NARRATION-001`)
- 仮定: `build_verified_script`のSTEP4スタブは`*args, **kwargs`の
  ままsignatureが確定していなかったため、
  `build_verified_script(*, transformed_script, source_script,
  claims, router, model_policy)`というkeyword-only引数のsignatureを
  新規に確定させた。
- 根拠: 公開契約は関数名と戻り値型(`-> ScriptDocument`)だけを固定し
  引数は`...`のまま未確定だった。fact check(`assert_script_claims
  _publishable`)・semantic review(`SemanticReview.compare`)・
  high assurance tier解決(`AIRouter.resolve`)という3つのgateを
  実行するには、変換後script、比較対象の元script、claim一覧、
  ルーティング設定の4種の入力が必須であり、keyword-only引数にする
  ことで呼び出し側の意図を明示させた。
- 置き換え条件: 後続タスク(`TASK-PIPELINE-001`等)がこの関数を
  呼び出す際に異なるsignatureを要求する場合、呼び出し側との
  整合を優先し、このtaskの完了報告に記録の上でsignatureを調整する。

- 対象: `script/pipelines/regeneration.py`(`TASK-PIPELINE-001`)
- 仮定: `RegenerationPlanner.plan()`が承認state(`CacheState
  .approvals`)を検証する際、`TargetCategory`と
  `07-approval-workflow.md`の4承認地点(materials_curriculum/
  planning/verified_script/preview_audio)の対応を独自に定義した
  (`_TARGET_TO_APPROVAL_POINT`)。承認済み仕様自体はこの対応表を
  明示的に定義していない。
- 根拠: 02-process-input-output.md 8.1節のAI工程表と07-approval
  -workflow.md 11節の実行ゲート説明から、topic/claim(資料由来)は
  materials_curriculum、project_plan/chapter_specはplanning、
  draft_script/narrationはverified_script、segment_audio/chapter_mp3
  /audio_manifestはpreview_audioに対応すると合理的に推論できる。
  MP3_PACKAGING(MP3タグのみ)は07-approval-workflow.md 10節
  「MP3タグだけ変更 | 原則として維持」に基づき、どの承認地点にも
  対応付けず常にgate対象外とした。
- 置き換え条件: 承認地点とTargetCategoryの対応が別途明文化された
  場合(例: STEP2契約の更新)、`_TARGET_TO_APPROVAL_POINT`をその
  定義へ置き換える。

- 対象: `script/pipelines/regeneration.py`(`TASK-PIPELINE-001`)
- 仮定: `RegenerationStep.scope`の解決順は
  segment_id指定 > chapter_id指定 > project全体、という優先順位で
  1つの文字列(`"segment:<id>"`等)にした。
- 根拠: 本タスクの対象外に「実際のAI/TTS実行」「全Project再構築」が
  明記されており、実際のfilesystem操作は行わない。scopeは後続の
  実行タスク(未確定)が識別子として解釈する軽量な文字列表現で
  十分と判断した。
- 置き換え条件: 実際に部分再生成を実行するタスクが、より構造化された
  scope表現(dataclass等)を要求する場合、この文字列表現を置き換える。

- 対象: `script/tts_clients/base.py`(`TASK-TTS-001`)
- 仮定: `TTSClient` Protocolの疎通確認methodを、承認済み仕様
  (10-tts-client-common-interface.md 3節)が示す`health_check`ではなく、
  STEP4ソース空実装が公開契約として固定した`check_connectivity`
  という名前で実装した。
- 根拠: タスク文書自身の「3. 正本」優先順位は承認済み仕様を最上位と
  するが、STEP4空実装の`STEP4_PUBLIC_CONTRACTS`には明示的に
  `'TTSClient Protocol: check_connectivity/list_speakers/synthesize'`
  と記載されており、これはSTEP2作成時点で意図的に決定された
  正式な公開契約row(単なる引用漏れではない)と判断した。また
  `TASK-AI-001`の`AIClient.check_connectivity`など、本セッションで
  実装した他の外部接続系Protocolはすべて`check_connectivity`という
  名前で統一されており、`health_check`はプロジェクト全体の命名規約と
  一致しない。両者が矛盾する場合、複数タスクにまたがる命名一貫性を
  優先し、STEP4契約の文言をそのまま採用した。
- 置き換え条件: 別タスクや人間承認によって`health_check`という名前が
  明示的に指定された場合、`check_connectivity`をrenameする。

- 対象: `script/tts_clients/base.py`(`TASK-TTS-001`)
- 仮定: `TTSClient` Protocolに`get_capabilities()`を追加した。
  STEP4空実装の`STEP4_PUBLIC_CONTRACTS`は
  `check_connectivity/list_speakers/synthesize`の3methodしか
  明記していない。
- 根拠: `EngineCapabilities`は`script/tts_clients/models.py`の公開
  契約行(`SynthesisRequest/SynthesisResult/SpeakerInfo/
  EngineCapabilities`)に明記された型であり、これを生成する手段が
  Protocol上に存在しないと型が孤立する。承認済み仕様
  (10-tts-client-common-interface.md 3節)の推奨interfaceにも
  `get_capabilities()`が明記されており、「扱う範囲」にも
  「capabilities」が独立した項目として挙げられている。STEP4契約の
  3method列挙は、この2つの上位正本と矛盾するため、優先順位に従い
  承認済み仕様を採用した。
- 置き換え条件: `get_capabilities()`が不要と明示された場合、または
  別の型付け方法が指定された場合に削除・変更する。

- 対象: `script/tts_clients/voicevox/client.py`(`TASK-VOICEVOX-001`)
- 仮定: STEP4ソース空実装は`list_speakers() -> list[SpeakerInfo]`を
  module-level関数(`self`引数なし)として宣言していたが、
  `VoicevoxHttpClient`のinstance method(`self.list_speakers()`)として
  実装した。
- 根拠: `TASK-TTS-001`が確定した`TTSClient` Protocol
  (`script/tts_clients/base.py`)は`list_speakers(self)`を
  instance methodとして要求しており、`VoicevoxHttpClient`が
  この共通契約を満たす(`TTSClientRegistry`経由でengineを
  差し替え可能にする)ことは本タスクの目的そのもの
  (「現行VOICEVOX clientを共通Protocolへ適合し」)である。
  module-level関数のままでは`TTSClient` Protocolを構造的に満たせず、
  `TTSClientRegistry.register("voicevox", ...)`にも登録できない。
  依存タスク(`TASK-TTS-001`)が確定した契約を優先し、STEP4スタブの
  この1点だけ実装時にmethod化した。
- 置き換え条件: 該当なし(`TTSClient` Protocol自体が変更されない限り
  維持する)。

- 対象: `script/tts_clients/voicevox/adapter.py`(`TASK-VOICEVOX-001`)
- 仮定: `VoicevoxAdapter.synthesize()`は合成したWAV bytesを
  実際にfilesystemへ書き込まない。`SynthesisResult.output_path`は
  `request.output_path`(未指定時は既定の`audio/cache/wav/segments/
  <request_id>.wav`という命名規則)をそのまま返すだけの、書込み予定
  pathの表明に留める。
- 根拠: 本タスクの対象外に「MP3 packaging」、`TASK-TTS-001`の対象外に
  「音声cache」が明記されており、`TASK-AUDIO-001`の扱う範囲には
  「segment単位音声生成」「WAV cache」「atomic保存」が明示されている。
  実ファイルへの書込みと、そのatomic rename・キャッシュ無効化条件は
  `TASK-AUDIO-001`が責務を持つ層と判断し、本タスクではWAVの
  bytes生成・検査(RIFF読込)・parameter適合までを実装した。
- 置き換え条件: `TASK-AUDIO-001`が`VoicevoxAdapter`(または共通
  `TTSClient`)に対して実際のatomic書込みを要求する契約を追加した
  場合、この関数にfilesystem書込みを追加する。

- 対象: `script/tts_clients/models.py`/`voicevox/adapter.py`
  (`TASK-AUDIO-001`、依存タスク`TASK-TTS-001`/`TASK-VOICEVOX-001`の
  ファイルを横断的に変更)
- 仮定: `SynthesisResult`(`TASK-TTS-001`)へ`audio_bytes: bytes |
  None = None`を追加し、`VoicevoxAdapter.synthesize()`
  (`TASK-VOICEVOX-001`)がこの新フィールドへ結合済みWAV bytesを
  設定するよう変更した。
- 根拠: 本タスク(`TASK-AUDIO-001`)の扱う範囲に明記された
  「atomic output」を実装するには、合成済み音声のbytesを
  `SegmentSynthesizer`が受け取る手段が必須。しかし`TASK-VOICEVOX
  -001`完了時点の`VoicevoxAdapter.synthesize()`は「音声cache」
  「MP3 packaging」を対象外としていたためbytesを返さない設計に
  していた(該当tasksの仮定記録を参照)。「完了済みタスクの
  無意味な再実装」を避けつつ、後続タスクが構造的に必要とする
  最小限のフィールド追加は許容範囲と判断した
  (`gemini_connectivity_gate`等、共有ファイルへの1対1追加と
  同種の判断)。追加は既定値`None`を持つ完全に後方互換な変更であり、
  追加後に`TASK-TTS-001`(10 case)・`TASK-VOICEVOX-001`
  (外部接続なしの10 case)を再実行し、全件pass・回帰なしを実測で
  確認した。
- 置き換え条件: 該当なし(共通`SynthesisResult`の構造自体が
  再設計されない限り維持する)。

- 対象: `script/audio/synthesis.py`(`TASK-AUDIO-001`)
- 仮定: 300文字超segmentの内部part分割は、`TASK-VOICEVOX-001`の
  `split_text_for_voicevox`(VOICEVOX固有・段落/文単位)を再利用せず、
  本タスク専用の`_split_into_parts`(文単位、句読点優先)を
  新規実装した。
- 根拠: `SegmentSynthesizer`は`profile.engine`を通じて任意の
  登録済みengine(将来のCOEIROINK等)を扱える設計であるべきで、
  VOICEVOX固有の分割関数に依存すると、他engineでの再生成時に
  意味不明な結合(VOICEVOXモジュールへの隠れた依存)が生じる。
  05-script-segment-schema.md 11節の「内部part分割」はTTS共通層の
  責務として記述されており、engine非依存な決定的分割ロジックを
  この層に置くことが設計として一貫すると判断した。
- 置き換え条件: engineごとに異なる分割ルール(最大文字数以外の
  制約)が必要になった場合、`profile`またはcapabilitiesから
  分割戦略を選択する仕組みを追加する。

- 対象: `script/audio/measurements.py`(`TASK-AUDIO-002`)
- 仮定: `AudioMeasurement.lufs`は常に`None`とし、実際のLUFS
  (統合ラウドネス、K-weighting)測定は実装しなかった。peak_dbfsと
  silence_ratioはPython標準`wave`+`struct`から生PCMを直接読んで
  決定的に計算した(ffmpeg実行なしで動作)。
- 根拠: LUFS計算にはITU-R BS.1770のK-weightingフィルタ実装が必要で
  あり、`docs/spec-proposals/audio-validation-thresholds.md`
  10節「音量・LUFS測定はffmpegのloudnormフィルタを候補とするが、
  本ドラフト作成時点ではインストール・実行していない。採用ツールは
  実測タスクで確定する」と明記されている。本タスクの対象外は
  「発音を自動fail」「最終閾値承認」「ASR」であり、LUFS実装自体は
  対象外と明記されていないが、閾値自体が`status: provisional`で
  「実測なしでは最終値にしない」とされている以上、正確なLUFS実装に
  投資するより、判定ロジック自体(warning/review累積規則、
  破損/0秒/形式不一致の常時fail)を正しく実装することを優先した。
  `loudness.target_lufs`関連の判定は、lufsが取得できた場合のみ
  条件分岐へ組み込める設計とし、現状は「測定不能」として扱う。
- 置き換え条件: ffmpeg loudnormベースまたは他ツールでのLUFS測定が
  実測タスクで確定した場合、`AudioMeasurementAdapter.measure()`へ
  loudness測定を追加し、`AudioValidator.validate()`のloudness
  警告判定を有効化する。

- 対象: `script/audio/thresholds.py`(`TASK-AUDIO-002`)
- 仮定: `AudioThresholdSet.__post_init__`(dataclass構築時の防御)と
  `AudioThresholds.validate_approval()`(正式な昇格経路)の両方に
  「evidence.measured=Falseまたはsample_count不足ならapproved拒否」
  という同じ検査を重複して実装した。
- 根拠: 「実測なしapproved禁止」は扱う範囲に明記された重要な安全
  規則であり、`dataclasses.replace()`等で直接`status="approved"`の
  インスタンスを作られても構造的に阻止できるよう、値オブジェクト
  自体の不変条件として`__post_init__`に持たせた。一方
  `validate_approval()`は呼び出し側にとっての正式な「昇格APIエントリ
  ポイント」として同じ判定を明示的なerror codeとともに提供する。
  二重実装だが、どちらか一方を消すと「直接構築での防御」または
  「明確なAPIエントリポイントでの防御」のいずれかが失われるため、
  意図的に残した。
- 置き換え条件: 該当なし(どちらかの経路を削除する場合は、
  もう一方が同等の安全性を提供できることを確認してから行う)。

- 対象: `script/pipelines/build.py`(`TASK-AUDIO-003`)
- 仮定: `ChapterPackager`/`BuildPipeline`自身はatomic disk writeを
  実装せず、`ArtifactService.register()`(`TASK-ARTIFACT-001`)へ
  完全に委譲した(`ChapterPackager.package()`は`mp3_bytes`のみ返し、
  disk pathを持たない)。versionは`ArtifactService.list_versions()`
  (公開API)から算出し、`artifact_id`/`destination_relative`へ
  埋め込む。
- 根拠: `ArtifactService.register()`は既にtempfile→`os.replace()`の
  atomic書込み・SHA-256 hash計算・version追跡を実測済みで提供して
  いる。当初`ChapterPackager`自身にoutput_path/version計算・atomic
  書込みを持たせる設計を検討したが、`ArtifactService`の
  append-only path一意性チェックと重複し、既にtestで保証済みの
  atomic書込みを別の場所で再実装することになるため、設計を変更した。
  これによりTC-01/TC-10(既存正常成果物は上書き・破損しない)と
  TC-09(再実行時、version以外は決定的)の両立を、`ArtifactService`
  側の既存contractにそのまま乗せて満たせる。
- 置き換え条件: `ArtifactService.register()`のcontractが変わる場合
  (例: version採番方式の変更)、`BuildPipeline._register_bytes()`の
  version算出ロジックも合わせて見直す。

- 対象: `script/audio/packaging.py`(`TASK-AUDIO-003`)
- 仮定: `ChapterPackager.__init__`は`mp3_encoder`を必須(既定値なし)の
  引数とし、実ffmpeg encoder(`make_ffmpeg_mp3_encoder()`)を
  自動配線しなかった。実ffmpeg encoderは関数として実装したが、本
  タスクの自動テストからは一切呼び出されない。
- 根拠: タスクの対象範囲に「このタスク単独の外部接続は不要である」
  と明記されており、`mp3_encoder`に既定で実ffmpeg実装を紐付けると、
  テストで明示的にfake encoderを注入しない限り誤って実プロセスを
  起動しうる。必須引数化することで、本番配線(将来のWorker/Job層)は
  明示的に実encoderを渡す責務を負い、テストは常にfakeを注入する
  ことが構造的に強制される。
- 置き換え条件: 実ffmpeg経路の統合smoke/live testが将来別タスクで
  追加された場合、そのタスクの`documentation_repair_ownership`配下で
  `make_ffmpeg_mp3_encoder()`を実際に呼ぶconnectivity gate付きtestを
  追加する。

- 対象: `script/audio/packaging.py`(`TASK-AUDIO-003`)
- 仮定: `ChapterPackager.package()`は、章内segment群の
  `voice_content_hash`が全て一致しない場合、警告に格下げせず常に
  `AppError(VALIDATION_ERROR)`とした。
- 根拠: 異なる`voice_content_hash`は異なるvoice profile revision
  由来のsegmentを意味し、これを黙って結合すると章内で声質が
  不整合のまま本番成果物になり得る(TC-07「形式ごとversion」の
  「改変検出」要件)。「実測なしでは緩めない」という本セッション
  全体の方針(`[[thresholds]]`のapproved二重防御等)と整合させ、
  最も安全側の挙動(結合拒否)をdefaultとした。
- 置き換え条件: 意図的な複数voice_content_hash混在(例:
  ナレーター交代の演出)が正式な仕様として承認された場合、
  `ChapterMetadata`等へ明示的な許可フラグを追加した上で緩和する。

- 対象: `script/worker/protocol.py`(`TASK-WORKER-001`)
- 仮定: `WorkerRequest`/`WorkerEvent`は、既存STEP4 scaffoldが持っていた
  `__init__(**data)` + `__getattr__`によるdict保持形状をそのまま維持し、
  frozen dataclass化や固定fieldへの変更は行わなかった。構築時の業務
  検証(`job_id`/`job_type`必須、`event`種別検証、artifact pathの
  絶対path拒否)は`__init__`本体に実装した。
- 根拠: 5節の公開契約は「`WorkerRequest/WorkerEvent/WorkerError`が
  JSON Linesのrequest/result/progress/artifact/errorを型付けする」と
  だけ定めており、内部表現をdataclass化することを要求していない。
  STEP4 scaffoldの`**data`形状は既に人間承認済みであり、これを変更
  すると「STEP4公開APIの破壊的変更」に該当しうるため、形状を維持した
  まま業務検証だけを追加する方針とした。
- 置き換え条件: 将来、event/requestのfield集合が確定し型安全性が
  必要になった場合、`**data`形状から個別fieldを持つdataclassへ移行を
  検討する(その場合は別途仕様変更として扱う)。

- 対象: `script/worker/cli.py`(`TASK-WORKER-001`)
- 仮定: `main(stdin, stdout, *, registry=None, stderr=None) -> int`は、
  stdinの各行を独立したrequestとして順次処理し、1requestのJSON不正や
  handler失敗が他のrequestの処理を止めない設計とした。
- 根拠: 契約表5節の`main(stdin, stdout) -> int`は仕様上「1行1request」
  の複数行ストリームを前提としており、TC-WORKER-001-01(2request投入)
  もこれを直接検証している。既定引数(`registry`/`stderr`)の追加は
  契約シグネチャ`main(stdin, stdout) -> int`に対する後方互換な拡張
  であり、テストからhandler registryとstderr出力先を注入可能にする。
  cancel/timeoutの制御(`WorkerRuntime`)は`TASK-WORKER-002`の対象範囲
  であり、本タスクの`main`はhandlerを同期的に直接呼び出すだけで
  timeout/cancel機構を持たない(3節「対象外: cancel signal」と一致)。
- 置き換え条件: `TASK-WORKER-002`実装時、`main`が`WorkerRuntime.run`を
  経由してcancel/timeoutを扱うよう拡張する可能性がある(その場合も
  `main(stdin, stdout) -> int`のシグネチャ自体は維持する)。

- 対象: `script/worker/handlers.py`(`TASK-WORKER-001`)
- 仮定: `HandlerRegistry.dispatch`は、handlerが生成する`progress`
  eventの`current`が直前の値より小さい場合、`error` eventへ変換する
  (完了扱いにしない)ことで「進捗を逆行させない」契約を能動的に強制
  した。
- 根拠: TC-WORKER-001-06のThen節が「current/totalとmessageを単調・
  順序どおりに通知し、完了後に進捗を逆行させない」と明示しており、
  これはhandler実装者の善意に委ねるのではなく、共通dispatch層で
  構造的に保証すべき安全規則と判断した(本セッション全体で維持して
  いる「実測なしでは緩めない」「軽い判定が重い判定を隠さない」等の
  設計方針と同種)。
- 置き換え条件: 意図的なprogress巻き戻し(例: 部分再生成時のカウンタ
  リセット)が正式な仕様として要求された場合、`current`のリセットを
  明示的に許可するeventフィールドを追加した上で緩和する。

- 対象: `script/worker/protocol.py`(`TASK-WORKER-002`)
- 仮定: `_VALID_EVENT_TYPES`へ`cancel_requested`/`cancelled`を追加した
  (既存6種別: started/progress/artifact/warning/error/completedへの
  純粋な追加)。
- 根拠: TC-WORKER-002-01のThen節が「cancel_requested→cancelled event
  で停止」と明示しており、この2種別はWORKER-002のcancel契約に必須。
  既存の`WorkerEvent`検証(`event`が既知種別であることの検証)を
  維持したまま、新種別を許可集合へ追加するだけの後方互換な変更であり、
  追加後に`TASK-WORKER-001`の対象10 case(`tests/test_worker_protocol.py`
  ・`tests/test_worker_dispatch.py`)を再実行し全件pass・回帰なしを
  実測で確認した。
- 置き換え条件: 該当なし(cancel関連eventの種別自体が再設計されない
  限り維持する)。

- 対象: `script/worker/runtime.py`(`TASK-WORKER-002`)
- 仮定: `WorkerRuntime`は`handler: Callable[[WorkerRequest,
  CancellationToken], Iterator[WorkerEvent]]`をconstructorで注入する
  設計とし、`grace_period_seconds`超過による強制終了・timeout検知を
  `clock: Callable[[], float]`の決定的注入で実現した(実時間の
  `sleep`は使わない)。
- 根拠: 契約表の公開symbolは`WorkerRuntime.run(request, token) ->
  Iterator[WorkerEvent]`のみを定めており、実処理(handler)をどう
  runtimeへ渡すかはSTEP4 scaffold(`__init__(self, *args, **kwargs)`)
  が未確定のまま残していた。`TASK-AUDIO-003`の`ChapterPackager
  (mp3_encoder=...)`と同様、STEP4 scaffoldの汎用`*args/**kwargs`から
  具体的なDI signatureへ具体化することは許容範囲と判断した。
  `clock`注入により、grace period超過・timeout超過を実時間の
  `sleep`なしに決定的にテストできる(本セッション全体で維持している
  「決定的な時刻注入」の方針、[[audio-thresholds]]等と同種)。
- 置き換え条件: 実際のOS process管理(Electron側のsubprocess
  kill/SIGTERM相当)と統合する`TASK-DESKTOP-002`実装時、`WorkerRuntime`
  がsubprocess由来のhandlerを受け取れることを確認し、必要なら
  handler signatureの拡張を検討する。

- 対象: `script/worker/runtime.py`(`TASK-WORKER-002`)
- 仮定: `recover_after_abnormal_exit(job)`は、`job.status ==
  JobStatus.RUNNING`である限り常に`new_status=JobStatus.FAILED`・
  `reason="stale_job_detected_on_startup"`・
  `discard_partial_artifacts=True`を返す、filesystem/DBへの副作用を
  一切持たない純粋な決定関数として実装した。実際の`failed`遷移の
  DB書込みや部分成果物の削除は、この関数の戻り値を見た呼び出し側
  (将来のElectron起動時stale job検出処理)の責務とした。
- 根拠: 22-job-lifecycle-and-recovery.md 5.6節は「対応するプロセスが
  存在しない場合、当該Jobをfailedへ遷移させ、理由
  (stale_job_detected_on_startup)を記録する」と一意に定めており、
  本タスクの対象範囲(3節)は「Job status mapping」の決定ロジックで
  あって実際のDB更新・IPC統合(Electron側)は別タスク
  (`TASK-DESKTOP-002`等)の責務と判断した。純粋関数にすることで、
  TC-WORKER-002-03(既存正常成果物保持)を副作用ゼロで自明に満たせる。
- 置き換え条件: 該当なし(実際のDB反映は別タスクが本関数の戻り値を
  消費する形で実装する)。

- 対象: `electron/preload/index.ts`(`TASK-DESKTOP-001`)
- 仮定: `ALLOWED_CHANNELS`は20-electron-desktop-architecture.md 5.6節に
  列挙された16件のIPCチャネル名をそのまま採用し、対応する型付きmethod
  (`project.*`, `source.*`, `approval.*`, `buildRequest.*`, `job.*`,
  `artifact.*`, `voice.*`)を`buildWalkwiseApi()`の戻り値へ実装した。
  各channelの背後にある実際のmain側handler(`electron/main/ipc/*.ts`)
  は他タスク(UI-*/WORKER-*)の対象範囲であり、本タスクでは一切変更
  していない。
- 根拠: 5.6節のIPCチャネル一覧は既に承認済み仕様として確定しており、
  「許可済みIPCだけを型付きで公開する」契約を満たすには、placeholder
  的な仮channel名ではなく、この確定済み一覧をそのまま使うのが最も
  意味がある。preloadが「どのchannelを許可するか」という境界だけを
  定義し、各channelの実際の処理(main側ハンドラ)は個別タスクが後から
  実装するという責務分割は、20-electron-desktop-architecture.md 5.2/
  5.3節の責務分離とも一致する。
- 置き換え条件: 5.6節のチャネル一覧が将来改訂された場合、
  `ALLOWED_CHANNELS`と対応するAPI methodを追随して更新する。

- 対象: `electron/preload/index.ts`(`TASK-DESKTOP-001`)
- 仮定: preloadモジュールの末尾に
  `if (typeof process !== "undefined" && process.versions?.electron)`
  guardを追加し、実Electron preload実行時のみ`installPreloadBridge
  (contextBridge, ipcRenderer)`を自動実行するようにした。
- 根拠: `contextBridge`/`ipcRenderer`をNode/vitest環境で無条件に
  importして実行すると、実Electron runtime外での構文・実行時挙動が
  不定であり、テストのたびに`vi.mock("electron", ...)`で全体を
  差し替える必要が生じる。`process.versions.electron`は実Electron
  process内でのみ存在するため、この guardによりテスト実行時は
  副作用なしにモジュールをimportでき、実行時は自動的に安全な
  contextBridge登録が行われる。
- 置き換え条件: 該当なし(Electronのprocess.versions.electron検出方法
  自体が非推奨になった場合のみ見直す)。

- 対象: `electron/renderer/main.ts`(`TASK-DESKTOP-001`)
- 仮定: `main(options)`は`TASK-UI-005`所有の`AppShell.vue`/`router.ts`/
  `stores/app.ts`(いずれも未実装のSTEP4 scaffold)を一切importせず、
  既定の`rootComponent`として本タスク内で完結する最小限のplaceholder
  Vue componentを使う設計にした。`rootComponent`/`appFactory`は
  どちらも注入可能とした。
- 根拠: 契約の対象外に「各画面」が明記されており、5節の公開契約も
  「Node APIへ直接アクセスせずVueを起動する」ことだけを求めている。
  未実装のAppShell等を直接importすると、それらのタスク(TASK-UI-005)
  が完了するまでrenderer/main.tsの静的import自体が壊れた状態を経由
  することになり、依存方向としても不適切(bootstrapが個別画面の実装
  詳細に依存すべきではない)と判断した。実際の画面をmountする配線は
  `TASK-UI-005`/`TASK-DESKTOP-003`が`rootComponent`/`appFactory`を
  注入する形で行う。
- 置き換え条件: `TASK-UI-005`完了後、実際の起動経路(Electron main起動
  時に呼ばれる箇所)で`rootComponent`に実際の`AppShell`を渡すよう配線
  する。

- 対象: `electron/main/database.ts`(`TASK-DESKTOP-002`)
- 仮定: `openApplicationDatabase(path, options)`の`options.connectionFactory`
  を必須(既定値なし)とし、実sqlite driver(`node:sqlite`/
  `better-sqlite3`等)の選定・依存追加は行わなかった。
- 根拠: 本タスクの対象範囲は「DB open/migrate」の orchestration であり、
  具体的なdriver選定は`package.json`への新規native依存追加を伴う
  別判断であるため、`TASK-AUDIO-003`の`mp3_encoder`必須注入と同様、
  実装詳細を呼び出し側へ委譲した。テストは常にfake
  `connectionFactory`を注入する。
- 置き換え条件: 実際のsqlite driverが選定された時点(将来のIPC実装
  タスクまたは別途の技術選定タスク)で、`electron/main/index.ts`等の
  実際の起動経路が具体的な`connectionFactory`を注入するよう配線する。

- 対象: `electron/main/worker_manager.ts`(`TASK-DESKTOP-002`)
- 仮定: `WorkerManager`の`spawn`を必須(既定値なし)とし、
  `node:child_process.spawn`を自動的に既定注入しなかった。
- 根拠: `TASK-DESKTOP-001`の`ChapterPackager.mp3_encoder`/
  `WorkerRuntime.handler`と同じ理由で、実subprocess起動を通常テストが
  誤って行わないよう構造的に強制した。実際の起動配線
  (`electron/main/index.ts`側)でのみ`node:child_process.spawn`を渡す。
- 置き換え条件: 該当なし。

- 対象: `electron/main/worker_manager.ts`(`TASK-DESKTOP-002`)
- 仮定: Python worker実行体を指す環境変数として新規に
  `WALKWISE_PYTHON_EXECUTABLE`を採用した(未設定時はplatform既定:
  win32は"python"、それ以外は"python3")。
- 根拠: 契約・既存文書のいずれにもこの環境変数名の先例がなく、
  他タスクの`VOICEVOX_URL`/`FFMPEG_PATH`/`GEMINI_API_KEY`等と同様の
  命名規則(`WALKWISE_`接頭辞ではなく機能名をそのまま使う既存例が
  混在するが、Python実行体という抽象度の高い設定はproject全体の
  設定であるためWALKWISE_接頭辞を付与)に倣い、新規に定義した。
- 置き換え条件: 該当なし(実配布形態確定時に、同名の環境変数または
  設定ファイル項目として維持する)。

- 対象: `script/worker/cli.py`(`TASK-WORKER-001`所有、本タスクで横断編集)
- 仮定: ファイル末尾に`if __name__ == "__main__": sys.exit(main(sys.stdin,
  sys.stdout))`を追加した。`main(stdin, stdout) -> int`自体の契約
  (署名・戻り値・挙動)は一切変更していない。
- 根拠: `TASK-DESKTOP-002`のintegration_smoke/liveテスト(TC-11/TC-12)
  は実Python subprocessを起動して疎通確認する契約であり、実行可能な
  entrypointが存在しないと疎通確認自体が原理的に不可能だった。
  `if __name__ == "__main__":`guardはpytest収集・import時には実行され
  ず、`TASK-WORKER-001`/`TASK-WORKER-002`の既存20 caseへの影響がない
  ことを再実行して確認した(全件pass、回帰なし)。
- 置き換え条件: 該当なし(将来、専用の起動scriptやpackaging済み
  実行体が用意された場合、このentrypointの代わりにそちらを使うよう
  `WorkerManager`の起動引数側で切り替える)。

- 対象: `package.json`/`vitest.config.ts`(`TASK-UI-001`)
- 仮定: `@vue/test-utils`/`jsdom`/`@vitejs/plugin-vue`をdevDependencies
  へ追加し、`vitest.config.ts`を新規作成した(`plugins: [vue()]`、
  既定environment "node"、DOM操作が必要なtestファイルは個別に
  `/** @vitest-environment jsdom */`docblockを付与)。`@vitejs/
  plugin-vue`は既存`vite@^7.0.0`と互換性のある最新版を採用した
  (`^5.0.0`はvite 7非対応でERESOLVEした)。
- 根拠: STEP4/STEP3のVue関連scaffoldは存在していたが、実際に`.vue`
  SFCをVitestでmount・DOM操作できるtoolingが皆無であり、これがない
  限り「静的文字列が存在するだけのテスト」しか書けず本セッションの
  明示的禁止事項に抵触する。UI-001〜005全体に影響する基盤的ギャップ
  だったため、最初のUIタスクであるTASK-UI-001で導入した。
- 置き換え条件: 該当なし(将来Vue test戦略が変わる場合のみ見直す)。

- 対象: `electron/renderer/screens/ProjectList.vue`(`TASK-UI-001`)
- 仮定: `ProjectList.vue`は`TASK-UI-005`所有のrouter/store/AppShellへ
  一切依存せず、`../api/projects`の`listProjects`/`createProject`だけを
  直接importする独立したcomponentとして実装した。「既存Projectを開く」
  (画面spec 5節)の実際のnavigationはこのタスクの対象外(対象外:
  「各画面」を跨ぐ遷移は`TASK-UI-005`のrouter統合時に配線する)とし、
  本タスクでは遷移相当のUIを実装しなかった。
- 根拠: `TASK-DESKTOP-001`の`electron/renderer/main.ts`と同じ理由
  ([[implementation_assumptions.md]]内の該当節参照)で、未実装の
  router/store/AppShellに依存すると、それらのタスク完了までこの
  componentの静的importが壊れた状態を経由することになる。
- 置き換え条件: `TASK-UI-005`完了後、実際のrouter統合時に「開く」
  操作からProjectWorkspace画面への遷移を配線する。

- 対象: `electron/renderer/screens/ProjectWorkspace.types.ts`(新規、`TASK-UI-002`)
- 仮定: `ProjectWorkspace.vue`の`<script setup>`が持つ型(`SourceItem`/
  `ApprovalItem`)を、componentから独立したplain `.ts`ファイルへ切り出し、
  component/testの両方がそこからimportする設計にした。
- 根拠: `electron/env.d.ts`の`declare module "*.vue"`は`default: unknown`
  しか宣言しておらず、plain `tsc`(本プロジェクトの`typecheck`script)は
  `.vue`ファイルからのnamed export型を認識できない(vue-tscなら可能だが
  未採用)。testファイルから`SourceItem`型をimportしようとして
  `TS2614`が発生したため、型だけを独立ファイルへ切り出して解決した
  (`TASK-UI-001`のProjectListでは型importが不要だったため表面化しな
  かった問題)。
- 置き換え条件: 将来`vue-tsc`を`typecheck`scriptへ採用する場合、この
  回避策は不要になる可能性があるが、既存の型ファイルをそのまま維持
  しても副作用はない。

- 対象: `electron/main/ipc/sources.ts`(`TASK-UI-002`)
- 仮定: 契約の「再処理/修正/問題なし」(TC-UI-002-06)を、20-electron-
  desktop-architecture.md 5.6節の承認済み固定IPCチャネル一覧に存在
  しない新規channelを追加するのではなく、既存の`source:register`を
  同じfilePathで再呼び出しする経路として解釈した。
- 根拠: 5節の公開契約は`source:register handlers`のみを定めており、
  5.6節の固定チャネル一覧にも「再処理」相当のchannelは存在しない。
  新規channelを追加すると承認済みアーキテクチャ仕様の拡張になり、
  人間承認なしに行うべきではないと判断した。一方、失敗したSourceの
  「再処理」は同じ入力での`source:register`再実行として自然に表現
  でき、既存の決定的再実行契約(TC-09)と一貫する。
- 置き換え条件: 将来、専用の`source:reprocess`等のchannelが承認済み
  仕様として追加された場合、そちらへ切り替える。

- 対象: `electron/main/ipc/builds.ts`(`TASK-UI-003`)
- 仮定: `job:start`ハンドラは`ApprovalGateCheckerLike.isSatisfied
  (buildRequestId)`という追加のDI依存を通じて承認ゲートを確認し、
  未充足の場合は`buildService.startJob()`を一切呼ばずに
  `approval_gate_not_satisfied`を送出する設計にした。実際の承認状態
  判定ロジック(どの承認地点が必要かの対応表等)はこのタスクの対象外
  とし、呼び出し側が注入する。
- 根拠: 22-job-lifecycle-and-recovery.md 5.5節は「承認ゲート未充足の
  場合、Job自体をqueuedにせず、IPC呼び出しの時点でエラーを返す
  (code: approval_gate_not_satisfied)」と明記しており、このタスクの
  契約(5節: 「approval gateを検証する」)とも一致する。実際の承認地点
  →Build Request対応判定は`TASK-PIPELINE-001`の
  `_TARGET_TO_APPROVAL_POINT`相当のPython側ロジックに依存するため、
  TypeScript側では抽象化したcheckerとして受け取るに留めた。
- 置き換え条件: 該当なし(実際の判定ロジックの配線は将来の統合時に
  `ApprovalGateCheckerLike`の実装を提供する形で行う)。

- 対象: `electron/renderer/screens/JobsAndArtifacts.vue`(`TASK-UI-004`)
- 仮定: cancel操作の確認モーダル(04-job-progress.md 10節)を、同じ
  cancelボタンへの2段階クリック(1回目で確認dialog表示、2回目
  =confirmボタンで実際にIPC呼出し)として実装した。
- 根拠: 契約は「確認後だけIPCを呼ぶ」ことだけを求めており、具体的な
  モーダル実装方式までは規定していない。ダイアログ表示状態を
  jobId単位で管理する`reactive`recordだけで実現でき、router/store
  なしで自己完結する。
- 置き換え条件: `TASK-UI-005`で共通modal componentが提供された場合、
  そちらへ差し替える。

- 対象: `electron/renderer/components/AppShell.vue`(`TASK-UI-005`)
- 仮定: error summaryへのfocus移動を、`watch(() => props.error, ...,
  { immediate: true })`+`await nextTick()`+`errorSummaryRef.value
  ?.focus()`という組み合わせで実装した(mount時に既にerrorが渡されて
  いる場合と、mount後にerrorが発生する場合の両方に対応するため
  `immediate: true`を付与)。
- 根拠: TC-UI-005-02は「validation error」を「render」した結果として
  focus移動を要求しており、propsとして最初からerrorを渡すテスト構成
  (mount時にerror済み)と、実際の利用では動作中にerrorが発生する
  ケースの両方をカバーする必要があった。`immediate: true`なしでは
  props初期値としてのerrorではwatcherが発火せず、mount時のfocus移動
  テストが成立しない。
- 置き換え条件: 該当なし。

- 対象: `electron/renderer/router.ts`(`TASK-UI-005`)
- 仮定: `NAVIGATION_SCREENS`(5画面の固定順序配列)を、`docs/screens/
  README.md` 6節のファイル命名規則(01〜05)の順序をそのまま採用して
  定義した。
- 根拠: 承認済み画面仕様(`docs/screens/README.md`)が唯一の正本であり、
  画面の並び順について他に指定がないため、既存の連番順をUIのnavigation
  順序としてそのまま採用するのが最も自然で、将来の画面仕様追加時にも
  一貫性を保てる。
- 置き換え条件: 該当なし(画面構成が変わる場合はdocs/screens/README.md
  改訂と合わせて更新する)。

- 対象: `script/integration/mvp_flow.py`(`TASK-DESKTOP-003`)
- 仮定: `run_mvp_flow(dependencies)`は、Project作成・Source登録・
  承認gate確認・worker実行・build実行の「順序」と「再試行上限」だけを
  制御する薄いorchestratorとし、各工程の実際の実装(実DB/file/IPC/
  worker呼出し)はすべて`MvpFlowDependencies`のcallableとして呼び出し
  側が注入する設計にした。既存の各サービス(ProjectService、
  SourceService、ApprovalService、BuildPipeline等)を直接importして
  内部でインスタンス化することはしなかった。
- 根拠: 実際のcurriculum/script/narration生成パイプライン(Phase3/4)
  全体を結線し直すと、本タスクの対象範囲(3節: 実IPC/DB/file/worker
  統合・正常導線・承認gate拒否・worker失敗/retry・再起動後永続化・
  複数artifact・原本不変・fixture VOICEVOX mock mode)を大きく超える
  範囲の再実装になり、「完了済みタスクの再実装」に該当しかねない。
  各工程をcallableとして注入する設計により、testは軽量なfakeで
  縦切りの「順序」「エラー伝播」「再試行」「決定性」を検証でき、
  実際のサービス結線(本物のProjectService等を注入すること)は
  将来の実際のElectron main起動シーケンス構築時に呼び出し側が担う。
- 置き換え条件: 該当なし(実際の本番結線は別途、Electron main起動
  entrypoint構築時に`MvpFlowDependencies`へ実サービスを注入する形で
  行う)。

- 対象: `electron/main/ipc/builds.ts`(`TASK-UI-003`所有)と
  `electron/main/ipc/jobs.ts`(`TASK-UI-004`所有)の間の技術的負債
  (`TASK-DESKTOP-003`のE2E統合中に発見)
- 仮定/既知の課題: `builds.ts`の`registerBuildIpcHandlers`と`jobs.ts`の
  `registerJobIpcHandlers`は、いずれも`"job:start"`というchannel名を
  それぞれ独自の意味(前者はbuildRequestIdを渡す新規Job起動、後者は
  `{parentJobId}`を渡す失敗Jobの再試行)で登録する。実Electronの
  `ipcMain.handle()`は同一channelへの二重登録でthrowするため、両方を
  同一の実ipcMain上で結線すると後から登録した方が前者を上書きし、
  実行時に矛盾したpayload解釈で失敗する。本タスクのE2E testでは、
  この2つのmoduleを意図的に別々のfake ipcMainインスタンスへ登録する
  ことでこの衝突を回避し、それぞれの単体契約(TASK-UI-003/UI-004時点
  で既にpass済み)を壊さずに済ませた。
- 根拠: 03-build-settings.mdと04-job-progress.mdの両画面仕様が、
  承認済み仕様としてどちらも独立に`job:start`をIPCチャネルとして
  列挙しており、どちらか一方を無断で改名・削除すると「承認済み仕様
  の意味変更」に該当する。また`TASK-UI-003`/`TASK-UI-004`は既に完了・
  文書化・pass済みのタスクであり、その場で無関係な大規模改修を
  加えることは「完了済みタスクの再実装」を避ける方針にも反する。
  この場でどちらの設計を正とするか推測で決めるのではなく、実際の
  main起動entrypointを組み立てる工程(将来のタスクまたは`TASK-
  RELEASE-001`のpackaging工程)で、`job:start`を単一のhandlerへ統合
  する(payload形状で新規/retryを判別する)という具体的な修正方針を
  ここに記録し、後続作業への申し送り事項とする。
- 置き換え条件: 実際のElectron main entrypoint構築時に、`builds.ts`の
  `job:start`ハンドラを正としてretry用payload(`{parentJobId}`)も
  受け付けるよう拡張し、`jobs.ts`側は`job:start`の登録を取り下げる
  (`job:get`/`job:subscribe-progress`/`job:cancel`のみ残す)。

### TASK-MIGRATION-001

- 対象: `script/migration/adapters.py`
- 仮定: `migrate_legacy_project`の新規生成物として、承認済み仕様が
  定義するproject-plan.yaml等のdomain schema(`TASK-PROJECT-001`等が
  所有)を模倣するのではなく、`migration-report.json`という本タスク
  専用の新形式JSON成果物(project_id/chapters/report)をdestinationへ
  出力する設計にした。
- 根拠: 本タスクの依存タスクは`TASK-CORE-002`/`TASK-SCRIPT-001`/
  `TASK-VOICEVOX-001`のみで`TASK-PROJECT-001`等のdomain/DB層を
  含まない。承認済みproject-plan.yaml等のschemaを本タスクが独自に
  推測して書き出すと、上位仕様の意味変更・未承認schemaの捏造に
  該当するリスクがある。`02-process-input-output.md`10節がJSON形式を
  「manifest、検査結果」の用途として認めており、変換結果の要約を
  JSON manifestとして出力するのは仕様の範囲内である。
- 置き換え条件: `TASK-PROJECT-001`等のdomain serviceと本adapterを
  実際に結線する後続タスクが確定した場合、`migration-report.json`の
  出力を、実際のproject作成呼び出し(`ProjectService.create`等)へ
  置き換えるか、その入力として利用する形に統合する。

- 対象: `script/migration/adapters.py`
- 仮定: 「approval.yaml/approvals.yaml」(TC-MIGRATION-001-06)を、
  `project/approval.yaml`(または`approval.yaml`)が存在し`status`が
  `approved`以外(`changes_requested`/`invalidated`/`pending`等)の
  場合、destinationへの副作用(書込)を一切開始する前に
  `AppError(PERMISSION_DENIED)`で停止する、という単純なgateとして
  実装した。実際の`approvals.yaml`(4gate構造)への変換自体は実体化
  せず、`report.conversions`へ「承認済みとして認識した」という記述の
  みを記録した。
- 根拠: 本タスクの依存タスクに`TASK-APPROVAL-001`が含まれておらず、
  同タスクが所有する`ApprovalBundle`/4gate構造(`materials_curriculum`/
  `planning`/`verified_script`/`preview_audio`)を本タスクが独自に
  模倣・再実装すると「本書にない公開symbolを安易に追加しない」
  「完了済みタスクの再実装」の両方に抵触しかねない。TC-06の
  Given/Then文言(「必要な承認が揃う場合だけ後工程へ進み、未承認・
  invalidated・changes_requestedでは安定errorで停止する」)は
  `TASK-APPROVAL-001`/`TASK-BUILD-001`等で繰り返し使われる定型文で
  あり、本タスクの文脈では「旧approval.yamlの状態を見て後続の変換を
  ゲートする」という最小解釈が対象範囲(5節「approval.yaml/
  approvals.yaml」)に最も忠実である。
- 置き換え条件: `TASK-APPROVAL-001`の`ApprovalService`と本adapterを
  実際に結線する後続タスクが確定した場合、旧approval.yamlの内容を
  実際の`ApprovalBundle`へ変換し`project/approvals.yaml`として
  書き出す処理へ置き換える。

- 対象: `script/migration/legacy_models.py`
- 仮定: `LegacyAudioInput`の`resolve()`が依存する`exists`引数は
  公開契約表にない追加引数だが、`__init__(self, **data)`のkeyword
  として渡す設計にした(コンストラクタ引数を増やす一方、公開symbol
  自体は`LegacyAudioInput`のまま変更していない)。
- 根拠: 契約8節が「filesystemはテストで注入または隔離可能にする」と
  明記しており、`TASK-OCR-001`の`runner`、`TASK-AI-001`の
  `session_get`等、既存タスクで一貫して採用してきたDI hookパターンを
  踏襲した。
- 置き換え条件: なし(外部接続なしのテスト実行に必須)。

### TASK-E2E-001

- 対象: `tests/integration/test_sample_book_e2e.py`
- 仮定: `run_sample_book_acceptance`を、実際のcurriculum/draft/claims
  生成パイプライン(Phase3/4本体)を再結線する「本物のE2E実行」では
  なく、決定的なfixture(sources/claims/segments/approvals/coverage/
  ai-routing-plan/model-policy)に対して(1)参照整合性、(2)承認gate、
  (3)`TASK-AI-002`のAI routing/cache/予算制御、(4)mock TTSによる
  章MP3/manifest生成、という「仕様間の配線」だけを検証する薄い
  acceptance関数として設計した。
- 根拠: 本タスクのSTEP2 depends_onは`TASK-DESKTOP-003`/
  `TASK-MIGRATION-001`のみで、Phase3/4の各AI生成pipeline
  (`SourceAnalysisPipeline`/`CurriculumPipeline`/
  `DraftGenerationPipeline`/`ClaimPipeline`等)を直接結線対象とは
  していない。またcontract 4節が「製品用教材の内容完成」を明示的に
  対象外としており、AIが実際に良い原稿を書けることではなく、
  4段階承認・AI tier routing・cache・予算制御・出典整合性・
  deliverables gateが仕様どおりに機能することの検証が本タスクの
  目的である。`TASK-DESKTOP-003`で確立した「callableベースの薄い
  orchestrator」設計方針をここでも踏襲し、各既存pipelineの
  再実装(「完了済みタスクの再実装」)を避けた。
- 置き換え条件: 該当なし。実際にAIで教材内容を生成するE2E検証が
  必要になった場合は、本関数のAI/TTS injection点(`ai_client`/
  `tts_synthesize`)へ実サービスを注入する形で拡張する
  (関数signatureは変更しない)。

- 対象: `tests/fixtures/sample_book/fixtures/*.yaml`
- 仮定: `docs/spec-proposals/task/1_sample-book-end-to-end-validation.md`
  11節が列挙する7種の異常fixture(`unsupported-claim`/`source-conflict`/
  `invalid-reference`/`high-assurance-unconfigured`/`budget-stop`/
  `cache-invalidation`/`unapproved-output-request`)を、基底fixtureへの
  差分overlay(`claims_add`/`claims_override`/`segments_override`/
  `approvals_override`/`policy_override`/`budget_state`の各key)として
  実装し、それぞれ次のerror codeへ対応させた: `unsupported-claim`→
  `VALIDATION_ERROR`(公開目次単独出典)、`source-conflict`→`CONFLICT`
  (未解決conflict claimのままverified_script承認)、
  `high-assurance-unconfigured`→`EXTERNAL_UNAVAILABLE`
  (`TASK-AI-002`の`AIRouter.resolve`が実装済みの黙った降格拒否を
  そのまま利用)、`invalid-reference`→`VALIDATION_ERROR`、
  `budget-stop`→`PERMISSION_DENIED`(`TASK-AI-002`の
  `BudgetGuard.assert_available`をそのまま利用)、
  `unapproved-output-request`→`PERMISSION_DENIED`。
  `cache-invalidation`はerrorを送出せず、`AICache`のcache miss件数の
  増加としてTC-04で検証する。
- 根拠: contract 3節・9節がこれら7種の異常fixtureをそのまま対象範囲・
  テストケースとして要求しており、仕様書の該当節(18節 予算制御、
  18節 モデルルーティング、06節 claims-and-sources)がそれぞれ
  対応する安定したerror codeの意味を既に定義しているため、それらを
  再利用した。
- 置き換え条件: なし(仕様どおりの対応表)。

- 対象: `tests/integration/test_sample_book_e2e.py`(TC-E2E-001-11/12)
- 仮定: `TASK-E2E-001`自身のTC-11/TC-12を独自実装せず、
  `TASK-VOICEVOX-001`が既に実装した`voicevox_connectivity_gate`
  fixtureと`VoicevoxHttpClient`/`VoicevoxAdapter`をそのまま再利用した
  (`tests/test_voicevox_adapter.py::test_tc_voicevox_001_12`と
  ほぼ同一の呼び出し列)。
- 根拠: contract 7節が「対象: 任意の実VOICEVOX」「本タスク独自の
  無秩序な実接続を追加しない」と明記しており、`TASK-VOICEVOX-001`が
  既に同じ疎通・実機能検証を実装済みであるため、重複実装を避けた。
- 置き換え条件: なし。

### TASK-RELEASE-001

- 対象: `resources/release-manifest.json`(新規)
- 仮定: 5節の公開契約表には「license manifest」専用のPython/TypeScript
  symbolが存在しない(`electron-builder.yml`/`resolveRuntimeDependencies`/
  `create_backup系`の3つのみ)。TC-03(license manifest)のlayerが
  `static`であることから、license manifestは呼び出し可能な関数ではなく
  `electron-builder.yml`の`extraResources`が実際に同梱する静的JSON
  artifactだと解釈し、新規に`resources/release-manifest.json`
  (platform/code_signing/auto_update/user_data/third_party_licensesの
  5節)を作成した。新しい公開関数symbolは一切追加していない。
- 根拠: 契約5.1節「本書にない公開symbolを安易に追加しない」を踏まえ、
  「static」layerという明示的な指定に最も忠実な実装は、生成コードでは
  なく検証可能な静的データファイルである。`23-distribution-and-
  platform-policy.md`5.4節「ライセンス一覧を含める」5.6節「code
  signing未実施のリスクを記録する」5.8節「uninstallでデータを自動
  削除しない」の3つをこの1つのartifactへ集約した。
- 置き換え条件: 実際のpackage生成タスクが確定した場合、この
  artifactの内容(特に`third_party_licenses`の一覧)を実際の
  `package.json`/`requirements.txt`から自動生成する処理へ置き換える。

- 対象: `tests/test_license_manifest.py`(TC-RELEASE-001-06)
- 仮定: 「ffmpeg/Tesseract存在確認」を、新しいPython production
  symbolを追加せず、`TASK-AUDIO-002`の`AudioMeasurementAdapter`と
  `TASK-OCR-001`の`OcrClient`(いずれも`runner`注入可能な
  `check_runtime()`を既に持つ)をそのまま再利用して検証した。
  `release-manifest.json`側の`bundled: false`宣言(まだ同梱方式が
  PoC未決定であることの表明)と、実行環境での実際のruntime存在確認
  (この既存adapter経由)は別の関心事として両立させた。
- 根拠: 本タスクのcontract 11節が変更許可するsource fileは
  `electron-builder.yml`/`electron/main/runtime.ts`/
  `script/maintenance/backup.py`の3つのみであり、新しいPython
  helperモジュールの追加は許可範囲外。`TASK-AUDIO-002`/`TASK-OCR-001`
  が既に同じ目的(ffmpeg/Tesseractのversion疎通確認)のadapterを
  実装済みであるため、重複実装を避けた(`TASK-E2E-001`のAIRouter/
  AICache/BudgetGuard再利用と同じ方針)。
- 置き換え条件: なし。

- 対象: `tests/test_backup_restore.py`(TC-RELEASE-001-05)
- 仮定: 「Python worker bundling strategy」というtitleを、
  `create_backup`が指定された`data_root`(利用者データ領域)だけを
  対象にし、アプリのinstall先ディレクトリやbundled runtime
  (`electron-builder.yml`の`extraResources`が同梱する`runtime/`)には
  一切触れないことを確認するtestとして実装した。
- 根拠: `17-local-data-persistence-policy.md`5.7節「利用者データは
  install先ディレクトリへ保存しない」という責務分離こそが、backup機能が
  「Python worker(および同梱runtime)のbundling戦略」と正しく直交して
  いることの証明であり、STEP3のtitleが指す関心事の最も具体的な
  解釈である(`TASK-SOURCE-002`等でこれまでも採用してきた、
  テストファイル物理配置とcase内容が厳密には一致しない場合に契約表の
  実体を優先する解釈方針を踏襲)。
- 置き換え条件: なし。

- 対象: `script/maintenance/backup.py`
- 仮定: `restore_backup`は、backup済みfileのうちhash検証に失敗した
  もの(`corrupted_files`)・欠落したもの(`missing_files`)を黙って
  復旧せず、検証に成功したfile(`valid_files`)だけをdestinationへ
  復旧し、破損・欠落分は戻り値へ明示的に列挙する設計にした
  (`restore_backup`は破損分についてAppErrorを送出しない)。
- 根拠: TC-RELEASE-001-02のThen「hash整合した状態へ復旧」は、
  復旧された内容がhash整合していることを要求しているのであり、
  破損分を無視して全体を失敗させることまでは求めていない。また
  5.1節「既存正常成果物を失敗時に削除・上書きしない」の精神に
  従い、破損file 1件のために復旧可能な他のfileまで復旧を諦める
  設計は安全側ではないと判断した。破損・欠落は隠さず明示的に
  報告するため、サイレントな部分成功にはしていない。
- 置き換え条件: なし。

### TASK-RELEASE-002

- 対象: `tests/performance/test_large_sources.py`,
  `tests/resilience/test_failure_recovery.py`
- 仮定: 公開契約表(5節)の"performance scenarios"/"resilience scenarios"は
  具体的なcallable symbol名ではなくprose説明であり、`TASK-E2E-001`の
  `run_sample_book_acceptance(...)`や`TASK-DESKTOP-003`の
  `run_mvp_flow(...)`のような単一の統合関数を新設する必要はないと
  判断した。各`test_tc_release_002_XX`関数自体が、既存の完了済み
  実装(`TASK-FILE-001`の`atomic_write_bytes`、`TASK-JOB-001`の
  `JobService`/`can_transition`、`TASK-WORKER-002`の`WorkerRuntime`/
  `recover_after_abnormal_exit`、`TASK-SOURCE-002`の`normalize_text`)を
  直接呼び出すscenario実装を兼ねる。新規production moduleは一切
  追加していない(11節の変更許可範囲どおり)。
- 根拠: 5.1節「本書にない公開symbolを安易に追加しない」と、directiveの
  「契約にない大規模な新production moduleを作らないでください。既存の
  実装を再利用してください」という明示的指示の両方に従った。
- 置き換え条件: なし。

- 対象: `tests/performance/test_large_sources.py`(TC-RELEASE-002-01,03,05,07,09)
- 仮定: Red確認は専用production moduleの`NotImplementedError`化ではなく、
  既存の再利用対象への一時的な破壊で行った: `atomic_write_bytes`
  (`script/persistence/files.py`)の例外処理を握り潰すよう変更し
  TC-01が正しくfailすることを確認、その後復元。TC-03/05/07/09は
  `normalize_text`(`TASK-SOURCE-002`、既に10 case・Red確認済み)を
  そのまま呼び出すだけであり、同じ関数への重複したRed確認は行わなかった
  (対象範囲外の再実装になるため)。性能値は`time.perf_counter`/
  `tracemalloc`による実測を記録するのみで、固定閾値によるpass/failは
  行っていない(directive 4.3節「根拠のない固定閾値でpassさせてはいけない」)。
- 根拠: 対象ケースに専用の未実装production moduleが存在しない場合の
  Red確認方法として、directiveが明示的に「failure injectorを一時的に
  未接続にする」等を許可している。
- 置き換え条件: なし。

- 対象: `tests/resilience/test_failure_recovery.py`(TC-RELEASE-002-02,04,06,08,10)
- 仮定: TC-02/04のRed確認は`JobService.recover_stale`
  (`script/services/jobs.py`)を一時的にno-op化(`continue`を挿入)して
  確認し、TC-06のRed確認は`can_transition`(`script/domain/job_state.py`)の
  `CANCEL_REQUESTED→CANCELLED`遷移を一時的に削除して確認した(いずれも
  確認後に復元)。TC-08/10は`JobService`/`JobRepository`の既存validation
  (`TASK-JOB-001`で既にRed確認済み)をそのまま検証しており、重複した
  破壊テストは行わなかった。TC-06では、cancel確定(`CANCEL_REQUESTED`
  →`CANCELLED`)の永続化に公開methodがないため、`JobRepository.update`
  (公開method)を直接使用した(`tests/test_stale_job_recovery.py`等
  既存テストにも`service._connection`/`repository._to_model`への
  直接アクセスの前例がある)。
- 根拠: 同上(directiveのRed確認方法の許可)。「cancel確定」は
  `TASK-JOB-001`の仮定として「実プロセス終了確認は対象外、確定は
  `TASK-WORKER-002`が担う」と記録済みだが、Electron main相当の
  確定ロジック自体はまだ実装されていないため、本タスクのtestでは
  `JobRepository.update`を直接呼ぶことでその後続処理を模擬した。
- 置き換え条件: 実際のElectron main entrypointが`WorkerRuntime`の
  `cancelled`eventを受けて`JobRepository`を更新する処理を実装した際、
  その公開APIへ置き換える。

- 対象: `electron/main/ipc/builds.ts`, `electron/main/ipc/jobs.ts`
- 仮定: `TASK-DESKTOP-003`で発見し申し送っていた`job:start`channel名の
  重複を、directive第6節の指示に従い本タスクで解消した。`builds.ts`の
  `job:start`handlerを正とし、bareな`buildRequestId`文字列(新規Job起動、
  既存挙動を無変更)と`{parentJobId}`オブジェクト(再試行、`jobs.ts`から
  移設)の両方を受け付けるよう拡張した。`BuildIpcContext`へ`jobService?:
  JobServiceLike`という**任意**項目を追加し(既存の`TASK-UI-003`テストが
  `jobService`なしで`registerBuildIpcHandlers`を呼び続けられるよう
  後方互換を保った)、未注入時は再試行payloadだけを
  `"jobService is required to retry a job"`という安定errorで拒否する。
  `jobs.ts`からは`job:start`の登録を削除し(`job:get`/
  `job:subscribe-progress`/`job:cancel`のみ残す)、`RETRYABLE_STATUSES`を
  `export`してbuilds.ts側から再利用させた(重複定義を避けた)。
- 根拠: 実Electronの`ipcMain.handle()`は同一channelの二重登録で
  throwするため、実main entrypointが両モジュールを結線する際に
  必ず顕在化する既知の問題だった。`jobService`を必須ではなく任意項目に
  したことで、「無断の公開signature変更」を避けつつ(既存必須引数は
  一切変更せず、新規の任意項目を追加しただけ)、実際の重複を解消できた。
- 影響確認: この変更に伴い、`electron/tests/job_artifact_ipc.test.ts`
  (`TASK-UI-004`所有、TC-UI-004-05)、`electron/renderer/tests/
  JobsAndArtifacts.test.ts`(`TASK-UI-004`所有、TC-UI-004-04)、
  `electron/tests/e2e/mvp-flow.test.ts`(`TASK-DESKTOP-003`所有、
  TC-DESKTOP-003-06)の3件が、`registerJobIpcHandlers`単独での
  `job:start`呼び出しを前提としていたため一時的に壊れた
  (`handlers.get("job:start")`が`undefined`になるため)。3件とも
  `registerJobIpcHandlers`と`registerBuildIpcHandlers`(`jobService`
  注入込み)を**同一のfake ipcMain**へ登録する形に更新し、再試行が
  単一handler経由で機能することを確認したうえで再回帰・pass確認した。
  これら3ファイルはいずれも「既存のtest caseの意味・assertion対象は
  変更せず、IPC登録方法(同一ipcMain共有)だけを実際のアーキテクチャに
  合わせて更新した」ものであり、契約・画面仕様・IPC channel一覧の
  意味変更ではない。
- 置き換え条件: なし(実main entrypoint構築時、この統合済みhandlerを
  そのまま利用する)。

### TASK-EPUB-001(post-MVP)

- 対象: `script/source_processing/epub/extract.py`
- 仮定: EPUB(zip container)の解析に`ebooklib`等の外部ライブラリを
  追加せず、Python標準ライブラリの`zipfile`+`xml.etree.ElementTree`
  だけで実装した。
- 根拠: EPUBはzip+XML(container.xml/OPF/XHTML)という単純な構造であり、
  本タスクの対象範囲(3節: EPUB2/3判定、DRM拒否、container/OPF/spine
  解決、XHTML本文、locator、annotation分離)を満たすために外部ライブラリの
  高度なAPIは必要ない。新規依存を避けることで、post-MVPタスクが
  MVPの依存関係グラフに影響を与えないようにした。
- 置き換え条件: 縦書き・EPUB3メディアオーバーレイ等の高度な機能(13節
  未決定事項)を扱う必要が生じた場合、専用ライブラリの追加を検討する。

- 対象: `script/source_processing/epub/extract.py`(ruby/footnote/image抽出)
- 仮定: `<ruby>base<rt>reading</rt></ruby>`形式(`<rb>`有無どちらも対応)の
  base文字列だけを本文へ含め、reading(ルビ読み)は`annotations.ruby`へ
  分離した。`epub:type="footnote"`を持つ要素(またはそのidを参照する
  `<a epub:type="noteref" href="#id">`)は本文へ一切含めず
  `annotations.footnotes`へ分離した。`<img>`は本文へ挿入せず
  `annotations.images`へ`src`/`alt`/`char_offset`を記録した。見出し
  (h1〜h6)は5.4節「保持する意味構造」に明記されているため本文へ含めた
  (`chapter_title`としても別途保持)。`char_offset`は、これらの本文
  除外要素より前に本文へ蓄積済みの文字数(見出し等を含む)を基準にした。
- 根拠: 仕様5.3節「脚注は本文中の参照位置を保持し、本文へ無条件で
  埋め込まない(読み上げ順序を暗黙に変えない)」「ルビはTTS用の読み
  表記へ変換可能な形で原文情報として保持する」を字句どおりに実装した。
  5.4節が見出しを「保持する意味構造」と明記しているため、本文からの
  除外対象にはしなかった。
- 置き換え条件: なし(仕様どおり)。

- 対象: `script/source_processing/epub/extract.py`(`EpubTextExtractor.extract`)
- 仮定: `extract()`はEPUBファイルを読み込むだけで、`sources/extracted/`
  等のfilesystemへの書込みは一切行わない、純粋な読込み専用関数とした。
  `source-storage-and-common-schema.md`のchunk manifest形式への実際の
  変換・永続化(7節「出力」に記載)は、本タスクの依存タスク
  (`TASK-INGEST-001`/`TASK-SOURCE-002`)の既存pipelineへ統合する際の
  後続作業とし、本タスクでは対象としなかった。
- 根拠: 本タスクのdepends_onは`TASK-INGEST-001`/`TASK-SOURCE-002`のみで
  あり、これらのpipelineへ実際にEPUB由来のchunkを書き込む統合作業までは
  要求していない。5.1節共通規則「入力正本を直接変更しない」を最も
  安全に満たす実装は、そもそも一切の書込みを行わないことである。
  また、この統合はEPUB入力がpost-MVPかつMVP画面には表示しないという
  対象外(4節)とも整合する。
- 置き換え条件: EPUB入力を実際の資料登録pipelineへ統合する後続作業が
  生じた場合、`EpubExtractionReport`をchunk manifest形式へ変換し
  `sources/extracted/`等へ書き込む処理を追加する(本関数のsignatureは
  変更しない)。

### TASK-M4B-001(post-MVP)

- 対象: `script/audio/m4b.py`(`M4BBuilder.build`)
- 仮定: 章の承認gate判定用の入力fieldとして、公開契約にない
  `script_approved: bool`/`preview_approved: bool`/
  `audio_validation_passed: bool`という3個の独立したbooleanを
  chapter辞書へ追加した(いずれか1つでもFalseならAppError
  (PERMISSION_DENIED)でM4B生成前に停止する)。
- 根拠: `m4b-output.md`5.2節「全章のverified script承認 ∧ 全章の
  試聴音声承認 ∧ 全章の音声検査がfailではない」という3条件のANDを
  検証可能にするには、呼び出し側がこの3条件をそれぞれ独立に伝える
  必要がある。本タスクの依存は`TASK-AUDIO-003`のみで、実際の
  `ApprovalService`/`JobService`等と直接結線する統合は対象外のため、
  `TASK-JOB-001`の`approval_gate_check`hookや`TASK-INGEST-001`の
  `IngestSource`と同じ「呼び出し側が用意する入力dataclass的field」
  パターンを踏襲した。
- 置き換え条件: 実際のapproval/audio validationサービスと結線する
  後続タスクが確定した場合、これら3fieldを実サービスの戻り値から
  導出する形にする(`build()`のsignature自体は変更しない)。

- 対象: `script/audio/m4b.py`, `script/schemas/m4b_manifest.py`
- 仮定: `M4BManifest.validation.validation_threshold_status`を、
  入力chapterの検査結果によらず常に`"provisional"`固定として記録する
  設計にした(「全章pass」でも`"approved"`へ昇格しない)。
- 根拠: `m4b-output.md`冒頭の状態注記が「本書が依存する
  audio-validation-thresholds.mdはstatus: provisionalである
  (実測未了)」「本書の合格条件はprovisional閾値に基づく暫定合格を
  意味する」と明記しており、依存仕様自体がprovisionalである以上、
  実装コード側の判断だけでこのステータスを`"approved"`へ格上げする
  ことはできない(仕様の`status`が`approved`へ改訂された時点で
  初めて変更されるべき値)。
- 置き換え条件: `docs/spec-proposals/audio-validation-thresholds.md`
  (または後継の承認済み仕様)の`status`が`approved`になった場合、
  この固定値を実測条件に基づく動的な判定へ置き換える。

- 対象: `script/audio/m4b.py`(`M4BBuilder.build`)
- 仮定: 全文MP3(3節・5.1節で対象外と明記)を生成する経路を一切
  実装しなかった。`build()`は常に章単位のchapter atomを持つM4Bだけを
  生成し、入力`chapters`が空の場合は「全文扱い」にフォールバックせず
  単に必須入力欠落として拒否する。
- 根拠: 11節「全文MP3を生成しようとする」がError(3節・5.1節の対象外
  方針違反)と明記されており、全文相当の出力を許容する分岐を一切
  作らないことが、この異常系を「発生させる経路自体を存在させない」
  という最も安全な実装だと判断した。
- 置き換え条件: なし(仕様が明示的に対象外とする機能のため)。

### TASK-ASR-001(post-MVP、post-MVP最終タスク)

- 対象: `script/asr/base.py`
- 仮定: 公開契約表(5節)には`ASRClient` Protocolしか列挙されていないが、
  `check_connectivity()`/`transcribe()`のシグネチャを具体化するため
  `ASRConnectivityResult`/`ASRSegment`/`ASRTranscript`という3つの
  最小限の補助dataclassを追加した。
- 根拠: `TASK-AI-001`が`AIClient` Protocolに対して`AIRequest`/
  `AIResult`/`AIUsage`を追加した precedentと同型であり、Protocolの
  method定義だけでは戻り値の形が確定せず呼び出し側で扱えない。
  5.1節「本書にない公開symbolを安易に追加しない」との整合は、
  これらがProtocol methodの型を成立させるために必須の最小限の
  companion typeであり、それ自体が独立した新機能ではないことで
  保っている。
- 置き換え条件: なし。

- 対象: `script/asr/verification.py`(CER/WER閾値)
- 仮定: `_REVIEW_REQUIRED_CER_THRESHOLD = 0.15`、
  `_REVIEW_REQUIRED_WER_THRESHOLD = 0.2`という暫定閾値を採用した。
- 根拠: `asr-script-audio-verification.md`15節が「CER/WERの具体的な
  閾値」を未決定事項として明記しており、9節のbenchmark計画も
  「未実施」である。仕様が確定するまでの実装上の安全側判断として、
  一般的な音声認識評価で「要確認」とされる水準よりやや厳しめの
  値を暫定採用した(閾値を超えた場合は`review_required`、下回っても
  誤差があれば`warning`に留め、`"pass"`は完全一致に近い場合のみ)。
- 置き換え条件: benchmark実施後、正式な閾値が承認済み仕様として
  確定した場合、この定数を置き換える。

- 対象: `script/asr/verification.py`(`ASRVerifier.verify`)
- 仮定: 「segment alignment不能」(TC-02)を、ASR転写結果のsegment数と
  `tts_segments`の件数が一致しない場合と定義し、その場合は全segmentの
  `tts_text`を1つの文字列へ結合、ASR側も1つの文字列へ結合して
  章単位で比較する設計にした。
- 根拠: 5.2節「segment単位のアラインメントが失敗した場合の代替」を
  満たす最も単純で決定的な判定方法であり、15節「アラインメント
  アルゴリズムの詳細」が未決定事項であるため、動的計画法によるより
  高度なsegmentマッチング(9節benchmark計画3)を先回りで実装しな
  かった。
- 置き換え条件: benchmark実施後、より高度なalignmentアルゴリズムが
  確定した場合、この判定方法を置き換える(`verify()`のsignatureは
  変更しない)。

- 対象: `script/asr/verification.py`(`ASRVerificationReport`)
- 仮定: `status`フィールドを`"pass"`/`"warning"`/`"review_required"`
  の3値だけを許可する型として実装し、`"fail"`という値を構造的に
  設定不可能にした(コンストラクタが`"fail"`を含むいかなる不正値も
  `AppError(VALIDATION_ERROR)`で拒否する)。
- 根拠: 5.5節「自動fail可否はしないとする」、12節「auto_fail_policy.
  allowedがfalseの間、ASR単独の結果でstatus: failを設定できない」を、
  実行時のif分岐だけでなく型定義そのもので保証することで、将来の
  コード変更で誤って`"fail"`を設定してしまうリグレッションを防いだ。
- 置き換え条件: 5.5節の`auto_fail_policy.allowed`が`true`へ改訂
  された場合(現時点で想定されていない)、許可する値集合を見直す。

## TASK-REVIEW-001: 実行時統合における設計判断

- 対象: `electron/main/worker_service_adapters.ts`、
  `script/worker/commands.py`
- 仮定: Electronの各`*ServiceLike`(Project/Source/Approval/Build/Job/
  Artifact/Voice)は、すべてPython Worker subprocess経由(WorkerManager.
  request())で実装し、Node側にSQLite driver(better-sqlite3等)を
  一切追加しない設計とした。
- 根拠: `docs/specifications/21-electron-python-worker-interface.md`
  5.2節の記述は「Electron mainがrequestを一時ファイル/stdinで
  Python CLIへ渡す」という形をJob実行の文脈で説明しているが、この
  protocol自体(JSON Lines request/response)を、Job実行以外の
  CRUD的操作(Project一覧取得等)にも一律で使うことを妨げる記述はない。
  対案(Node側に直接SQLite driverを追加し、`script/services/*`の
  業務ロジックをTypeScriptへ再実装する)は、(a)同じ業務ルールを
  2言語で二重実装することになり将来的な乖離リスクが高く、(b)
  better-sqlite3のようなnative moduleはElectron ABIとのversion
  一致が必要でpackaging時の脆弱性になりやすく、(c)本reviewの
  「既存の承認済みserviceを再利用する」という基本方針とも整合しない。
  そのためWorker常駐subprocess1本への集約を選んだ。
- 置き換え条件: 将来、Project一覧等の高頻度読み出しでWorker往復の
  遅延が問題になった場合、読み取り専用パスに限定してNode側キャッシュ層を
  追加することを検討する(書き込みパスの正本はPython側のまま変更しない)。

- 対象: `script/worker/handlers.py`(`HandlerRegistry.dispatch`)
- 仮定: handlerがPython generatorの`return`文で値を返した場合、
  その値を`completed`eventの`result`欄へ付与するよう拡張した。
  handlerが値を返さない(または`list`を返す、既存の全handler)場合は
  従来どおり`result`欄なしの`completed`eventのまま。
- 根拠: TASK-WORKER-001の既存契約(`docs/test-cases/
  TASK-WORKER-001-python-worker-request-and-event-protocol.md`)は
  `started`→`progress`→`artifact`→`completed`のevent列挙のみを定義し、
  `completed`eventの追加fieldを禁止していない。CRUD系job_type
  (`project.create`等)がElectron main側へ結果を返すには何らかの
  経路が必要で、`WorkerEvent`の型自体(`event`ごとの検証はartifactの
  pathのみ)を変更せずに実現できるこの方式を選んだ。既存test
  (`tests/test_worker_dispatch.py`)は非generator/値なしhandlerのみを
  使っており、後方互換であることを確認済み。
- 置き換え条件: 将来、`completed`eventのpayload形式自体を21節の
  正式改訂で定義する場合、この`result`fieldの名前・形式をそれに
  合わせて変更する。

- 対象: `electron/main/worker_service_adapters.ts`
  (`createJobServiceAdapter`の`subscribeProgress`)
- 仮定: 真のpush型progress配信の代わりに、`job:get`を500ms間隔で
  pollingしてProgressEventへ変換する暫定実装とした。
- 根拠: Python Worker側にはまだ実際のbuild pipeline実行ループ
  (章単位でAI原稿生成→TTS→M4Bを実行し、都度progress eventをemitする
  1つの長時間job)が接続されておらず、`job.start`はJobの
  queued/running状態遷移のみを行う。真のpush型progressを実装するには、
  Worker側の実行ループ自体を新設する必要があり、これは既存の
  各pipeline module(素材処理・原稿生成・TTS・音声パッケージング)を
  1つの`job.start`から呼び出す統合作業であって、本review(実行時
  統合の配線)の範囲外と判断した。
- 置き換え条件: 実際のbuild pipeline統合(別task)が完了し、Worker側が
  `progress`eventを実際にemitするようになった時点で、pollingを
  WorkerManagerの`progress`event中継(`event.sender.send`相当の
  push配信)へ置き換える。

- 対象: `electron/main/ipc/files.ts`、`ProjectWorkspace.vue`
- 仮定: file選択は`dialog.showOpenDialog()`(main process)経由のみを
  許可し、rendererは任意path文字列を一切組み立てられない設計とした。
  加えて`script/schemas/source_metadata.py`(`SourceMetadata.from_file`)
  側にもsymlink拒否を追加した(Electron層の検証を経由しない呼び出しに
  対する多重防御)。
- 根拠: ブラウザの`File`オブジェクトは`file.name`(拡張子付きファイル名)
  以外に実在するファイルシステムpathを一切持たない(セキュリティ上の
  設計、Web標準の仕様)。以前の実装はこの`file.name`を実pathであるかの
  ように送っており、main/Workerは対象fileを一度も実際に読めていなかった
  (機能しない、というだけでなく、将来同名の別fileを誤って参照する
  potentialなbugでもあった)。dialog経由に変更することで、main process
  が実際に選ばれた絶対pathを検証してから使う設計に変えた。
- 置き換え条件: 将来drag&dropを再度サポートする場合、Electronの
  `webUtils.getPathForFile()`(Electron 32+で実pathを取得できるAPI)を
  使い、同じ`validateSourceFilePath()`検証を経由させることを検討する。

- 対象: `tsconfig.main.json`、`scripts/finalize-dist.mjs`
- 仮定: `electron/main`・`electron/preload`はCommonJS(`module: CommonJS`、
  拡張子なし相対import)へcompileし、root `package.json`の
  `"type":"module"`とは独立させるため、`dist/main/package.json`・
  `dist/preload/package.json`へ`{"type":"commonjs"}`を書き込む
  (Node解決規則: 最も近いpackage.jsonの`type`が優先される)。
- 根拠: 既存の`electron/main`・`electron/preload`のTypeScriptは
  拡張子なしの相対import(`from "./jobs"`等)で書かれており、これは
  Node ESM(`NodeNext`解決)ではなくCommonJS/classic解決の書式である。
  全fileへ`.js`拡張子を追加してESM化する変更は、本review対象外の
  広範囲な書き換えになるため避けた。CommonJS化+dist側package.jsonの
  type上書きは、root自体をESMのまま保てる標準的な回避策である。
- 置き換え条件: 将来、main/preload配下のimportをすべて拡張子付きへ
  統一するタイミングで、`tsconfig.main.json`を`module: NodeNext`へ
  切り替え、`scripts/finalize-dist.mjs`のtype上書きを削除する。

- 対象: `script/ai_clients/gemini/mindmap_builder.py`、
  `merged_text_fixer.py`(削除)
- 仮定: 全body`NotImplementedError`のlegacy互換scaffoldであり、
  どのtask・test・pipelineからも参照されていないことを確認した上で、
  実装を追加せず削除・deprecateした。
- 根拠: これらの関数(`build_final_mindmap`/`load_sections`/
  `process_section`/`fix_text_file_with_gemini`)を実装する仕様・
  test caseが存在せず、実装すれば推測実装になる。`TASK-COEIR-001`のような
  「外部条件待ちのため永久blocked」とは異なり、これらは単に
  「参照元がない」ため、実装保留ではなく削除が適切と判断した。
- 置き換え条件: 将来これらの機能(mindmap構築、テキスト整形)が
  実際に必要になった場合、`script/ai_clients/gemini/client.py`の
  `GeminiClient`契約へ新規taskとして追加する。

## TASK-BUILD-EXEC-001: VoiceProfile→古いVoiceProfileスキーマへのadapter

- 対象: `script/pipelines/build_execution.py`(検討したが不採用、
  実装せず)
- 仮定: 既存の`script/audio/synthesis.py::SegmentSynthesizer`は
  `script/schemas/script.py::ScriptDocument`(`stage="verified"`必須、
  segmentごとに`SpeakerRef`必須)と`script/schemas/profiles.py::VoiceProfile`
  (YAML時代、`engine_identity.engine_version`/`audition_approved`が
  approved状態で必須)を要求するが、実際に永続化されているverified
  script.yaml(`tests/fixtures/sample_book/script.yaml`と同型)には
  speaker/segment_type/stage相当のfieldが存在せず、TASK-BUILD-EXEC-001の
  新しいDB正本VoiceProfileにも`engine_identity`/`audition_approved`に
  相当する概念がない。
- 判断: `SegmentSynthesizer`を経由せず、Build Execution Orchestratorから
  `TTSClient.synthesize()`を1segmentにつき1回直接呼び出す設計にした
  (300文字超segmentの内部分割は、`SegmentSynthesizer`の複数part WAVを
  1segment分の単一ファイルへ結合しない既存の設計上の穴を継承しないため、
  本orchestratorの対象外とした。300文字超のtext_for_ttsはengine側の
  `TEXT_TOO_LONG`としてそのまま失敗させ、サイレント分割・切り詰めは
  行わない)。`narration.mode: single_speaker_per_chapter`
  (`project-plan.yaml`の既存承認済みfield)により、章あたり単一speakerが
  前提であることは確認済みで、per-segment character割り当てを新たに
  発明する必要はなかった。
- 根拠: `SegmentSynthesizer`の300文字超分割・cacheは価値ある機能だが、
  それを流用するには`ScriptDocument`/`VoiceProfile`という別世代のschemaへ
  変換するadapterが必要になり、かつ`SegmentSynthesizer`自体の
  part-file命名の食い違い(`SegmentAudio.output_path`と実際に書き込まれる
  part fileのpathが一致しない、既存の潜在的な問題)を新しい統合経路へ
  持ち込むリスクがあった。TTS呼び出し自体は`TTSClientRegistry`/
  `TTSClient` protocolという既存の安定契約を直接使うため、新しい業務
  ロジックの推測は発生していない。
- 置き換え条件: 将来、300文字超segmentの複数part結合が必要になった場合、
  `SegmentSynthesizer`のpart file命名を修正したうえで、Build Execution
  Orchestratorから利用するように切り替える(既存のcaching機能も
  合わせて活用できる)。

## TASK-VOICE-PROFILE-UI-001: 試聴機能(voice:preview)をVoiceProfile modalへ引き継がなかった

- 対象: `electron/renderer/screens/BuildSettings.vue`(削除)、
  `electron/renderer/screens/ProjectWorkspace.vue`(新設したVoiceProfile
  modalへは配線せず)
- 仮定: 旧`BuildSettings.vue`の試聴ボタンは、生のspeaker_id + 任意の
  サンプルテキストを`voice:preview`へ渡す実装だった。旧speaker/style直接
  選択UIを削除した結果、この試聴機能の自然な呼び出し元がなくなった。
- 判断: `voice:preview` IPC自体(`electron/main/ipc/voice.ts`)は変更・削除
  せず、単に呼び出し元を配線しないままにした。VoiceProfile作成・編集modal
  へ試聴ボタンを追加することも検討したが、今回の承認済み実装対象(§4
  「実装範囲」)にも完了条件(§26)にも試聴機能への言及がなく、追加すると
  未承認のスコープ拡張になるため見送った。
- 根拠: `voice:preview`は既存のtested・動作するcapabilityであり、削除すると
  将来必要になった際の手戻りが大きい。呼び出し元を配線しないだけなら
  安全側(害がない)であり、「不要な複雑さを増やさない」という方針と
  「既存動作するコードを推測で消さない」という方針の両方に合致する。
- 置き換え条件: 将来、VoiceProfile作成・編集modalに試聴ボタンを追加する
  正式な要求が生じた場合、`voice:preview`をそのProfileの`speakerId`/
  `styleId`/parameters値で呼び出す形で配線する(新しいIPC設計は不要)。

## TASK-VOICE-PROFILE-UI-001: `wrapper.setProps()`の型付けがVue componentの実プロパティ型を認識しない

- 対象: `electron/renderer/tests/BuildSettings.test.ts`
- 仮定: `electron/env.d.ts`の`declare module "*.vue" { const component: unknown; }`
  shimにより、plain `tsc`は`.vue`コンポーネントの実際のprops型を認識できない
  (本プロジェクトの既存の制約、`ProjectWorkspace.types.ts`のコメント参照)。
  `mount(Component, { props: {...} })`呼び出し自体は緩い型で通るが、
  `wrapper.setProps({...})`は`VNodeProps`相当の基底属性しか認識せず、
  カスタムpropsを渡すと型エラーになる。
- 判断: `any`を使わず、`wrapper.setProps.bind(wrapper) as (props: Record<string,
  unknown>) => Promise<void>`という、`unknown`経由の局所的なcastで対応した。
  これはこのテストの1箇所だけであり(既存コードに`setProps`の使用前例がない)、
  型安全性を損なう範囲を最小限にしている。
- 根拠: 「境界でunknownを使いvalidationする」方針に沿った最小限の妥協であり、
  `any`によるコード全体の型安全性低下は避けた。
- 置き換え条件: 将来、`.vue`ファイルの型付けを`vue-tsc`等の専用type checkerへ
  移行するタイミングで、この局所castは不要になる。
