# 開発ログ

## プロジェクト概要
YouTube検索結果を定期的にスクレイピングし、動画情報（タイトル、再生数、URL）をGoogle Sheetsに自動保存するツール

### 技術スタック
- Python 3.10
- Playwright (ブラウザ自動化)
- Browserless (ヘッドレスブラウザサービス)
- GitHub Actions (定期実行)
- Google Sheets API (データ保存)

## 開発ステップ

### MVP1: 基本スクレイピング機能
**完了日**: 2025-05-24
- ✅ YouTubeスクレイピングクラスの実装
- ✅ 動画タイトル、URL、再生数の取得
- ✅ ローカルファイルへの保存（JSON/CSV）

### MVP2: Browserless統合
**完了日**: 2025-05-24
- ✅ Browserlessクライアントの実装
- ✅ リトライメカニズム
- ✅ エラーハンドリング

### MVP3: 再生数パース機能
**完了日**: 2025-05-24
- ✅ 動的コンテンツのロード対応
- ✅ スクロールによる追加データ取得
- ✅ 再生数フォーマット変換（1.2M → 1200000）

### MVP4: Google Sheets連携
**完了日**: 2025-05-24
- ✅ Google Sheets APIの統合
- ✅ 認証処理（サービスアカウント対応）
- ✅ 重複チェック機能
- ✅ データの追記機能

### MVP5: GitHub Actions自動化
**完了日**: 2025-05-24
- ✅ GitHub Actions設定ファイル作成
- ✅ 定期実行（6時間ごと）
- ✅ 手動実行対応
- ✅ アーティファクト保存

## 主要コンポーネント

### 1. Scraper
- `ScraperInterface`: 抽象基底クラス
- `YoutubeScraper`: YouTube特化の実装
- `BrowserlessClient`: Browserless接続管理

### 2. Storage
- `StorageInterface`: 抽象基底クラス
- `LocalFileStorage`: ローカルファイル保存
- `GoogleSheetsStorage`: Google Sheets保存

### 3. Utils
- `config.py`: 設定管理
- `logger.py`: ログ管理（通常ログ + Markdownログ）

## 使用方法

### 環境設定
```bash
# 依存関係のインストール
pip install -r requirements.txt
playwright install chromium

# 環境変数の設定
cp .env.example .env
# .envファイルを編集
```

### ローカル実行
```bash
# 基本実行
python main.py

# カスタムクエリで実行
python main.py --query "Python tutorial" --max-results 30

# Browserless使用
python main.py --use-browserless

# ローカル保存のみ
python main.py --no-sheets
```

### GitHub Actions
- リポジトリのSettings > Secrets and variablesで以下を設定：
  - `BROWSERLESS_URL`: BrowserlessのWebSocket URL
  - `GOOGLE_SHEETS_CREDS`: Google認証情報（JSON）
  - `SHEET_ID`: Google SheetsのID

## トラブルシューティング

### よくある問題

1. **Playwrightのインストールエラー**
   ```bash
   playwright install-deps
   ```

2. **Google Sheets認証エラー**
   - サービスアカウントの権限を確認
   - Sheets APIが有効になっているか確認

3. **スクレイピング失敗**
   - YouTubeのHTML構造変更の可能性
   - セレクタの更新が必要

## 今後の改善案

1. **機能拡張**
   - チャンネル名、投稿日時の取得精度向上
   - 複数検索キーワード対応
   - 通知機能（Slack、Discord等）

2. **パフォーマンス**
   - 並列処理の実装
   - キャッシュ機能
   - データベース対応

3. **監視・分析**
   - エラー率の監視
   - スクレイピング成功率の追跡
   - データ分析ダッシュボード

---

最終更新: 2025-05-24