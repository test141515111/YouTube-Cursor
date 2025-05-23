"""ログ管理モジュール"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import config


class Logger:
    """カスタムロガークラス"""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        """
        ロガーの初期化
        
        Args:
            name: ロガー名
            log_file: ログファイルパス（指定しない場合は設定から取得）
        """
        self.name = name
        self.log_file = log_file or config.log_file
        self._setup_logger()
    
    def _setup_logger(self):
        """ロガーのセットアップ"""
        # ログディレクトリの作成
        if self.log_file:
            log_dir = Path(self.log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # ロガーの作成
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, config.log_level.upper()))
        
        # 既存のハンドラーをクリア
        self.logger.handlers.clear()
        
        # フォーマッターの設定
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # ファイルハンドラー
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """デバッグレベルのログ出力"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """情報レベルのログ出力"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告レベルのログ出力"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """エラーレベルのログ出力"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """クリティカルレベルのログ出力"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """例外情報付きのエラーログ出力"""
        self.logger.exception(message, *args, **kwargs)


def get_logger(name: str, log_file: Optional[str] = None) -> Logger:
    """
    ロガーを取得
    
    Args:
        name: ロガー名
        log_file: ログファイルパス
    
    Returns:
        Logger: カスタムロガーインスタンス
    """
    return Logger(name, log_file)


class MarkdownLogger:
    """Markdown形式のログを出力するロガー"""
    
    def __init__(self, file_path: str = "DEVELOPMENT.md"):
        """
        初期化
        
        Args:
            file_path: Markdownファイルパス
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """ファイルが存在しない場合は作成"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write("# 開発ログ\n\n")
    
    def log(self, title: str, content: str, level: str = "INFO"):
        """
        Markdown形式でログを追記
        
        Args:
            title: ログタイトル
            content: ログ内容
            level: ログレベル
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"""
## [{level}] {title}
**時刻**: {timestamp}

{content}

---

"""
        
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def log_error(self, title: str, error: Exception, context: str = ""):
        """
        エラー情報をMarkdown形式でログ出力
        
        Args:
            title: エラータイトル
            error: 例外オブジェクト
            context: エラーコンテキスト
        """
        error_details = f"""
### エラー詳細
- **タイプ**: `{type(error).__name__}`
- **メッセージ**: {str(error)}
- **コンテキスト**: {context}

### スタックトレース
```python
{self._get_traceback(error)}
```
"""
        self.log(title, error_details, "ERROR")
    
    def _get_traceback(self, error: Exception) -> str:
        """トレースバック情報を取得"""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    
    def log_success(self, title: str, details: str):
        """成功ログを出力"""
        self.log(title, details, "SUCCESS")
    
    def log_info(self, title: str, details: str):
        """情報ログを出力"""
        self.log(title, details, "INFO")


# グローバルMarkdownロガー
md_logger = MarkdownLogger()