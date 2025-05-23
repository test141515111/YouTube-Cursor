"""設定管理モジュール"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# .envファイルの読み込み
load_dotenv()


class Config(BaseModel):
    """アプリケーション設定"""
    
    # Browserless設定
    browserless_url: str = Field(
        default=os.getenv("BROWSERLESS_URL", "ws://localhost:3000"),
        description="Browserless WebSocket URL"
    )
    
    # Google Sheets設定
    google_sheets_creds_path: Optional[str] = Field(
        default=os.getenv("GOOGLE_SHEETS_CREDS_PATH"),
        description="Google Sheets認証情報ファイルパス"
    )
    google_sheets_creds: Optional[str] = Field(
        default=os.getenv("GOOGLE_SHEETS_CREDS"),
        description="Google Sheets認証情報（JSON文字列）"
    )
    sheet_id: Optional[str] = Field(
        default=os.getenv("SHEET_ID"),
        description="Google SheetsのID"
    )
    
    # 検索設定
    default_search_query: str = Field(
        default=os.getenv("DEFAULT_SEARCH_QUERY", "ChatGPT"),
        description="デフォルトの検索クエリ"
    )
    max_results: int = Field(
        default=int(os.getenv("MAX_RESULTS", "50")),
        description="最大取得件数"
    )
    
    # ログ設定
    log_level: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="ログレベル"
    )
    log_file: str = Field(
        default=os.getenv("LOG_FILE", "logs/scraper.log"),
        description="ログファイルパス"
    )
    
    # リトライ設定
    max_retries: int = Field(default=3, description="最大リトライ回数")
    retry_delay: float = Field(default=1.0, description="リトライ間隔（秒）")
    
    # ブラウザ設定
    browser_timeout: int = Field(default=30000, description="ブラウザタイムアウト（ミリ秒）")
    viewport_width: int = Field(default=1920, description="ビューポート幅")
    viewport_height: int = Field(default=1080, description="ビューポート高さ")
    
    class Config:
        """Pydantic設定"""
        env_file = ".env"
        env_file_encoding = "utf-8"


# グローバル設定インスタンス
config = Config()