# Walkwise STEP4 ソースコード空実装

この一式は、`audio_book_creation_dump_2026-07-19_171441.txt`を基に作成した
STEP4のproduction側空実装です。

## 適用方法

このZIPの内容をWalkwiseリポジトリのrootへ重ねてください。

既存のGemini・VOICEVOX実装は保持し、STEP2で追加された公開契約を同じmoduleへ
追記しています。その他の新規public APIは型・signature・契約・関連テストケースを
ファイル内に保持し、本体では`NotImplementedError`またはTypeScriptの明示的errorを
送出します。

## 重要

- STEP4では本実装を行っていません。
- 外部API・VOICEVOX・OCR・ffmpeg等へ接続しません。
- COEIROINKはblockedのままで、endpointやspeaker IDを推測していません。
- 音声検査閾値はprovisionalのままです。
- `tests/`のSTEP3空実装は上書きしません。
- 最新ダンプには、STEP3で生成予定だったElectron/Vitest側16テストファイルが
  含まれていません。人間承認gateの前にSTEP3成果物から戻してください。

## 検証済み

- Python構文確認
- Python production module 124件のimport
- pytest 454件のcollection
- pytest通常実行: 431 xfailed / 23 skipped
- TypeScript `tsc --noEmit`
- STEP2で計画されたsource path 134件の存在確認
