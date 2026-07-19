# STEP3 テスト空実装

このディレクトリ群は、`docs/test-cases/`の54契約・530ケースを正本として生成した
STEP3成果物です。

- Python test files: 93
- TypeScript/Vitest test files: 16
- Test cases: 530
- External connectivity gates: 9

## 空実装ルール

- Pythonは`pytest.mark.xfail(strict=True)`と`pytest.fail`を併用する。
- TypeScriptは`test.fails`と明示的`throw new Error`を使用する。
- `pass`、無条件成功assertion、実装済みを装うmock結果は置かない。
- production moduleはSTEP4前のためimportしない。
- case ID、Given/When/Then、layer、priorityを各テスト自身へ記録する。
- 通常実行では外部API・ローカルruntimeへ接続しない。

## 外部接続

`integration_smoke`が軽量疎通確認、`integration_live`が実機能確認です。
liveケースは契約上のconnectivity fixtureまたはgate名を必ず記録しています。
STEP3のgateは常にskipし、外部I/Oを行いません。
