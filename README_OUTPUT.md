# スクレイピング結果の出力場所

## 📁 ローカル実行時の出力

### 1. データファイル
スクレイピング結果は以下のファイルに保存されます：

- **JSON形式**: `data/youtube_results.json`
- **CSV形式**: `data/youtube_results.csv`

### 2. ログファイル
実行ログは以下に保存されます：

- **通常ログ**: `logs/scraper.log`
- **開発ログ**: `DEVELOPMENT.md`（Markdown形式）

### 実行例
```bash
python main.py --query "ChatGPT" --max-results 30
```

実行後、`data/`ディレクトリに以下のファイルが作成されます：
```
data/
├── youtube_results.json
└── youtube_results.csv
```

## ☁️ Google Sheetsへの出力

環境変数が設定されている場合、自動的にGoogle Sheetsに保存されます：

1. **必要な環境変数**：
   - `GOOGLE_SHEETS_CREDS`: サービスアカウントの認証情報（JSON文字列）
   - `SHEET_ID`: Google SheetsのID

2. **シートの形式**：
   | タイトル | URL | 再生数 | 再生数（数値） | チャンネル名 | 投稿日時 | 取得日時 |
   |---------|-----|--------|---------------|-------------|---------|---------|
   | 動画タイトル | https://... | 1.2M回 | 1200000 | チャンネル名 | 1日前 | 2025-05-24 02:30:00 |

## 🤖 GitHub Actions実行時の出力

### アーティファクト
GitHub Actionsで実行すると、結果は**アーティファクト**として保存されます：

1. **データアーティファクト** (`scraper-data`)：
   - `data/youtube_results.json`
   - `data/youtube_results.csv`
   - 保存期間：90日間

2. **ログアーティファクト** (`scraper-logs`)：
   - `logs/`ディレクトリの全ファイル
   - `DEVELOPMENT.md`
   - 保存期間：30日間

### アーティファクトのダウンロード方法

1. GitHubリポジトリの**Actions**タブを開く
2. 実行済みのワークフローをクリック
3. ページ下部の**Artifacts**セクションから必要なファイルをダウンロード

![GitHub Actions Artifacts](https://docs.github.com/assets/images/help/repository/artifact-drop-down-updated.png)

## 📊 データ形式

### JSON形式の例
```json
[
  {
    "title": "ChatGPTの使い方完全ガイド",
    "url": "https://www.youtube.com/watch?v=example1",
    "views_text": "1.2M回",
    "views_count": 1200000,
    "channel_name": "Tech Channel",
    "upload_time": "1日前",
    "scrape_timestamp": 1716495000.123,
    "saved_at": "2025-05-24T02:30:00"
  }
]
```

### CSV形式の例
```csv
title,url,views_text,views_count,channel_name,upload_time,saved_at
ChatGPTの使い方完全ガイド,https://www.youtube.com/watch?v=example1,1.2M回,1200000,Tech Channel,1日前,2025-05-24 02:30:00
```

## 🔧 出力先のカスタマイズ

### ローカルファイルの保存先を変更
`main.py`の以下の部分を編集：

```python
# JSONファイルの保存先
json_storage = LocalFileStorage("data/youtube_results.json", "json")

# CSVファイルの保存先
csv_storage = LocalFileStorage("data/youtube_results.csv", "csv")
```

### Google Sheetsを無効化
```bash
python main.py --no-sheets
```

### ローカル保存を無効化
```bash
python main.py --no-local