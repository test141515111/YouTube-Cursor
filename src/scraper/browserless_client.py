"""Browserless接続管理モジュール"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser

from ..utils.logger import get_logger, md_logger
from ..utils.config import config


logger = get_logger(__name__)


class BrowserlessClient:
    """Browserlessクライアント"""
    
    def __init__(self, websocket_url: Optional[str] = None):
        """
        初期化
        
        Args:
            websocket_url: BrowserlessのWebSocket URL
        """
        self.websocket_url = websocket_url or config.browserless_url
        self.browser: Optional[Browser] = None
        self.playwright = None
        self._retry_count = 0
    
    async def connect(self) -> Browser:
        """
        Browserlessに接続
        
        Returns:
            Browser: 接続されたブラウザインスタンス
        """
        for attempt in range(config.max_retries):
            try:
                logger.info(f"Browserlessへの接続試行 {attempt + 1}/{config.max_retries}")
                
                if not self.playwright:
                    self.playwright = await async_playwright().start()
                
                self.browser = await self.playwright.chromium.connect_over_cdp(
                    self.websocket_url,
                    timeout=config.browser_timeout
                )
                
                logger.info("Browserlessへの接続に成功しました")
                md_logger.log_success(
                    "Browserless接続成功",
                    f"URL: {self.websocket_url}"
                )
                
                return self.browser
                
            except Exception as e:
                logger.error(f"Browserless接続エラー (試行 {attempt + 1}): {e}")
                
                if attempt < config.max_retries - 1:
                    delay = config.retry_delay * (2 ** attempt)  # 指数バックオフ
                    logger.info(f"{delay}秒後にリトライします...")
                    await asyncio.sleep(delay)
                else:
                    md_logger.log_error(
                        "Browserless接続失敗",
                        e,
                        f"最大リトライ回数({config.max_retries})に達しました"
                    )
                    raise
    
    async def disconnect(self):
        """接続を切断"""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("Browserlessから切断しました")
            
            if self.playwright:
                await self.playwright.stop()
                
        except Exception as e:
            logger.error(f"切断中にエラーが発生: {e}")
    
    async def health_check(self) -> bool:
        """
        Browserlessの健全性チェック
        
        Returns:
            bool: 正常に動作している場合True
        """
        try:
            if not self.browser:
                await self.connect()
            
            # テストページを開いて確認
            context = await self.browser.new_context()
            page = await context.new_page()
            
            await page.goto('about:blank')
            title = await page.title()
            
            await page.close()
            await context.close()
            
            logger.info("Browserlessの健全性チェック: OK")
            return True
            
        except Exception as e:
            logger.error(f"健全性チェックに失敗: {e}")
            return False
    
    async def __aenter__(self):
        """コンテキストマネージャーのエントリーポイント"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーの終了ポイント"""
        await self.disconnect()


async def create_browserless_browser() -> Browser:
    """
    Browserlessブラウザインスタンスを作成
    
    Returns:
        Browser: ブラウザインスタンス
    """
    client = BrowserlessClient()
    return await client.connect()