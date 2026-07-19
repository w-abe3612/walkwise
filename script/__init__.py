"""script package boundary.

Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
Importing this package must have no side effects.
"""

from __future__ import annotations

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-DEV-001', 'package boundary', '`script`を副作用なくimport可能にする。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-DEV-001-01', 'priority': 'P0', 'layer': 'static', 'title': 'pytest収集', 'given': 'リポジトリ直下で依存が揃い、外部サービス環境変数は未設定', 'when': '`pytest --collect-only -q`を実行する', 'then': '全テストモジュールをnetwork接続なしで収集し、未知marker warningがない', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-02', 'priority': 'P0', 'layer': 'contract', 'title': '外部テスト既定無効', 'given': '通常pytest実行', 'when': 'integration_smoke/live marker付きテストを収集・実行する', 'then': '明示opt-inがなければ外部接続せずskip理由が表示される', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '秘密値非表示', 'given': 'API key環境変数が設定済み', 'when': 'skip/error/logを生成する', 'then': '秘密値本体が出力へ含まれない', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'script配下のPython package境界', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`pytest markers`を通じて「script配下のPython package境界」を実行する', 'then': '「script配下のPython package境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '共通fixture配置', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`pytest markers`を通じて「共通fixture配置」を実行する', 'then': '「共通fixture配置」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '外部サービスを通常テストから除外する既定値', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`pytest markers`を通じて「外部サービスを通常テストから除外する既定値」を実行する', 'then': '「外部サービスを通常テストから除外する既定値」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-07', 'priority': 'P1', 'layer': 'unit', 'title': '構文・import・collection確認の入口', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`pytest markers`を通じて「構文・import・collection確認の入口」を実行する', 'then': '「構文・import・collection確認の入口」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`pytest markers`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`pytest markers`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_test_environment_contract.py`'},
)
