# Research Desk

テーマ別に情報を収集し、根拠付きの「判断カード」へ整理してから、人が採用・保留・破棄を判断するための GitHub Actions 基盤です。

## 対象テーマ

1. 一次情報に限定した、生成AIによる業務効率化
2. デジタルマーケティング
3. 米国メディア（`config/feeds.yaml` のRSS・鮮度・除外ルール）
4. 日経225構成銘柄の決算・重要ニュース
5. 指定69通貨ペアに影響するニュース

このリポジトリは**情報を判断可能な状態にする**ためのものです。外部公開、売買、発注は自動化しません。

## 状態

`取り込み済み → 整理・準備中 → 次工程待ち → 検証中 → ユーザー待ち → 完了`

どの時点でも `保留` または `破棄` にでき、理由と次の確認日を残します。

## 初回設定

1. `config/*.yaml` をレビューします。日経225構成銘柄は `config/nikkei225.yaml` に、確認日つきで登録してください。
2. GitHub Actions の Variables に `GOOGLE_DRIVE_FOLDER_ID` を設定します。
   - 保存先フォルダ: `1rBwXMkBh5AZ1YXNdMrGxS0WIGcrkgkIj`
3. GitHub Actions の Secret `GOOGLE_SERVICE_ACCOUNT_JSON` に、Drive とレビュー用Sheetへ共有済みのサービスアカウントJSONを設定します。
4. レビュー台帳を作成後、Variables の `REVIEW_SPREADSHEET_ID` を設定します。

Secret またはレビューSheetが未設定の場合、実行結果は GitHub Actions Artifact として残ります。収集処理は停止しません。

## 自動実行

`Daily research desk - US media` は毎日 **04:30 JST** に実行されます。GitHub ActionsのcronはUTCのため、ワークフロー上では前日19:30 UTC (`30 19 * * *`) としています。

Drive設定済みなら、結果は `保存先/YYYY-MM-DD/us-media/` に保存されます。再実行時は同名ファイルを更新するため、同一日・同一テーマのファイルを増殖させません。GitHub Actionsの定刻実行には遅延があり得るため、分単位の監視には使いません。

現時点で自動収集を有効化しているテーマは米国メディアです。残る4テーマは、データソース・利用条件・人の確認点を設定後に同じ保存ループへ追加します。

## ローカル実行

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python -m research_desk collect --theme us-media --output-dir output
pytest
```

## 設計資料

- [運用設計](docs/operating-model.md)
- [Google連携の設定](docs/google-setup.md)
- [ソースと一次性の方針](docs/source-policy.md)
