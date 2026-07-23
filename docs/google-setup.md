# Google Drive・レビュー台帳の設定

## 保存先

Google DriveフォルダID: `1t5D_rUbm4kDWoE-5inPG7eZ646gWPiZZ`

サービスアカウントのメールアドレスへ、このフォルダとレビュー用Google Sheetを編集共有してください。

## GitHub設定

| 種別 | 名前 | 内容 |
|---|---|---|
| Secret | `GOOGLE_SERVICE_ACCOUNT_JSON` | サービスアカウントJSON全文 |
| Variable | `GOOGLE_DRIVE_FOLDER_ID` | 上記の保存先フォルダID |
| Variable | `REVIEW_SPREADSHEET_ID` | 作成後のレビュー台帳のID |

初期コミットでは、Google認証情報が未投入でも安全に収集ロジックとArtifact出力を検証できるようにしています。

## GitHub Actionsからの保存先

設定後、毎日04:30 JSTの実行で以下のように保存されます。

```text
<root folder>/
  2026-07-25/
    us-media/
      manifest.json
      cards/
        <card_id>.md
```

`GOOGLE_SERVICE_ACCOUNT_JSON` のサービスアカウントに、ルートフォルダの編集者権限が必要です。JSON本文をリポジトリやログへ貼り付けないでください。
