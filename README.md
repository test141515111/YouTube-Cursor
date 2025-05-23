# YouTube Search Results Scraper

YouTube検索結果を定期的にスクレイピングし、動画情報（タイトル、再生数、URL）をGoogle Sheetsに自動保存するツールです。

## 技術スタック

- **言語**: Python 3.10
- **ブラウザ自動化**: Playwright (async_api)
- **ヘッドレスブラウザ**: Browserless
- **スケジューラー**: GitHub Actions (cron)
- **データ保存**: Google Sheets API

## セットアップ

### 1. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、必要な値を設定してください。

```bash
cp .env.example .env
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Google Sheets APIの設定

1. Google Cloud ConsoleでプロジェクトとGoogle Sheets APIを有効化
2. サービスアカウントを作成し、認証情報をダウンロード
3. 認証情報をGitHub Secretsに設定

## 使用方法

### ローカル実行

```bash
python main.py --query "ChatGPT" --max-results 30
```

### GitHub Actions

GitHub Actionsは6時間ごとに自動実行されます。手動実行も可能です。

## ライセンス

MIT License