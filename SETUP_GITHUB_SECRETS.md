# GitHub Actions設定手順

## 1. Google Sheets IDの設定

提供されたスプレッドシートURL:
```
https://docs.google.com/spreadsheets/d/12dmTloPFhuB-Fx1R3O9qcYOjQAS4gTBmSh-GjWar3Fk/edit?gid=1403876847#gid=1403876847
```

Sheet ID: `12dmTloPFhuB-Fx1R3O9qcYOjQAS4gTBmSh-GjWar3Fk`

## 2. Google Cloud Console設定

### ステップ1: プロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（例: youtube-scraper-project）

### ステップ2: Google Sheets APIを有効化
1. 「APIとサービス」→「ライブラリ」
2. 「Google Sheets API」を検索
3. 「有効にする」をクリック

### ステップ3: サービスアカウント作成
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. サービスアカウント名を入力（例: youtube-scraper-bot）
4. 「作成して続行」

### ステップ4: 認証情報のダウンロード
1. 作成したサービスアカウントをクリック
2. 「キー」タブ
3. 「鍵を追加」→「新しい鍵を作成」
4. 「JSON」を選択して「作成」
5. JSONファイルがダウンロードされます

### ステップ5: Google Sheetsに権限付与
1. ダウンロードしたJSONファイルを開く
2. `"client_email"` の値をコピー（例: youtube-scraper-bot@project.iam.gserviceaccount.com）
3. 対象のGoogle Sheetsを開く
4. 「共有」ボタンをクリック
5. コピーしたメールアドレスを追加（編集権限）

## 3. GitHub Secretsの設定

### リポジトリでの設定
1. GitHubリポジトリ: https://github.com/test141515111/YouTube-Cursor
2. Settings → Secrets and variables → Actions
3. 「New repository secret」をクリック

### 設定するSecrets

#### 1. GOOGLE_SHEETS_CREDS
- Name: `GOOGLE_SHEETS_CREDS`
- Value: ダウンロードしたJSONファイルの内容を**そのまま**貼り付け

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}
```

#### 2. SHEET_ID
- Name: `SHEET_ID`
- Value: `12dmTloPFhuB-Fx1R3O9qcYOjQAS4gTBmSh-GjWar3Fk`

#### 3. BROWSERLESS_URL（オプション）
- Name: `BROWSERLESS_URL`
- Value: `ws://your-browserless-instance.com`
- ※ローカルで実行する場合は不要

## 4. GitHub Actions実行

### 手動実行
1. Actionsタブを開く
2. 「YouTube Scraper」ワークフローを選択
3. 「Run workflow」をクリック
4. 必要に応じてパラメータを設定：
   - 検索クエリ: ChatGPT（デフォルト）
   - 最大取得件数: 50（デフォルト）
   - Browserless使用: true（デフォルト）

### 実行確認
1. ワークフローの実行状況を確認
2. 成功後、Google Sheetsを確認
3. Artifactsからローカルファイルもダウンロード可能

## 5. トラブルシューティング

### よくあるエラー

#### 1. 認証エラー
```
Error: The caller does not have permission
```
→ サービスアカウントのメールアドレスがGoogle Sheetsに追加されているか確認

#### 2. API未有効化
```
Error: Google Sheets API has not been used in project
```
→ Google Cloud ConsoleでSheets APIが有効になっているか確認

#### 3. シートが見つからない
```
Error: Requested entity was not found
```
→ SHEET_IDが正しいか確認

## 6. 定期実行の確認

GitHub Actionsは6時間ごとに自動実行されます：
- cron: `0 */6 * * *`
- 時刻: 0:00, 6:00, 12:00, 18:00 (UTC)

## デプロイ完了チェックリスト

- [ ] Google Cloud Projectを作成
- [ ] Google Sheets APIを有効化
- [ ] サービスアカウントを作成
- [ ] 認証情報JSONをダウンロード
- [ ] Google Sheetsに編集権限を付与
- [ ] GitHub Secretsを設定（GOOGLE_SHEETS_CREDS、SHEET_ID）
- [ ] GitHub Actionsを手動実行して動作確認
- [ ] Google Sheetsにデータが書き込まれることを確認