"""YouTube検索結果スクレイピングモジュール"""

import asyncio
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeoutError

from ..utils.logger import get_logger, md_logger
from ..utils.config import config
from . import ScraperInterface


logger = get_logger(__name__)


class YoutubeScraper(ScraperInterface):
    """YouTube検索結果スクレイパー"""
    
    def __init__(self, use_browserless: bool = False):
        """
        初期化
        
        Args:
            use_browserless: Browserlessを使用するかどうか
        """
        self.use_browserless = use_browserless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    async def _init_browser(self):
        """ブラウザの初期化"""
        try:
            self.playwright = await async_playwright().start()
            
            if self.use_browserless:
                logger.info("Browserlessに接続中...")
                self.browser = await self.playwright.chromium.connect_over_cdp(
                    config.browserless_url
                )
            else:
                logger.info("ローカルブラウザを起動中...")
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
            
            # コンテキストの作成
            self.context = await self.browser.new_context(
                viewport={
                    'width': config.viewport_width,
                    'height': config.viewport_height
                },
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # ページの作成
            self.page = await self.context.new_page()
            self.page.set_default_timeout(config.browser_timeout)
            
            logger.info("ブラウザの初期化が完了しました")
            
        except Exception as e:
            logger.error(f"ブラウザの初期化に失敗しました: {e}")
            md_logger.log_error("ブラウザ初期化エラー", e, "ブラウザの起動中にエラーが発生")
            raise
    
    async def scrape(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        YouTube検索結果をスクレイピング
        
        Args:
            query: 検索クエリ
            max_results: 最大取得件数
        
        Returns:
            List[Dict[str, Any]]: 検索結果のリスト
        """
        if not self.browser:
            await self._init_browser()
        
        results = []
        
        try:
            # YouTube検索ページにアクセス
            search_url = f"https://www.youtube.com/results?search_query={query}"
            logger.info(f"検索URL: {search_url}")
            
            await self.page.goto(search_url, wait_until='networkidle')
            
            # 動的コンテンツのロードを待機
            await self.page.wait_for_selector('ytd-video-renderer', timeout=10000)
            
            # スクロールして追加のコンテンツをロード
            prev_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while len(results) < max_results and scroll_attempts < max_scroll_attempts:
                # 現在の動画要素を取得
                video_elements = await self.page.query_selector_all('ytd-video-renderer')
                
                # 各動画要素から情報を抽出
                for element in video_elements[prev_count:]:
                    if len(results) >= max_results:
                        break
                    
                    try:
                        video_data = await self._extract_video_data(element)
                        if video_data:
                            results.append(video_data)
                            logger.debug(f"取得: {video_data['title']}")
                    except Exception as e:
                        logger.warning(f"動画データの抽出に失敗: {e}")
                        continue
                
                # 取得数が変わらない場合はスクロール
                if len(results) == prev_count:
                    await self.page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
                    await asyncio.sleep(2)  # コンテンツのロードを待機
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                
                prev_count = len(results)
                logger.info(f"現在の取得件数: {len(results)}/{max_results}")
            
            logger.info(f"スクレイピング完了: {len(results)}件取得")
            md_logger.log_success(
                "スクレイピング成功",
                f"クエリ: {query}\n取得件数: {len(results)}件"
            )
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"スクレイピング中にエラーが発生: {e}")
            md_logger.log_error("スクレイピングエラー", e, f"クエリ: {query}")
            raise
    
    async def _extract_video_data(self, element) -> Optional[Dict[str, Any]]:
        """
        動画要素から情報を抽出
        
        Args:
            element: 動画要素
        
        Returns:
            Optional[Dict[str, Any]]: 動画情報
        """
        try:
            # タイトルの取得
            title_element = await element.query_selector('#video-title')
            title = await title_element.get_attribute('title') if title_element else None
            
            # URLの取得
            url = await title_element.get_attribute('href') if title_element else None
            if url:
                url = urljoin('https://www.youtube.com', url)
            
            # 再生数の取得
            views_text = None
            aria_label = await element.query_selector('#video-title')
            if aria_label:
                aria_text = await aria_label.get_attribute('aria-label')
                if aria_text:
                    # aria-labelから再生数を抽出
                    views_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:回|views)', aria_text)
                    if views_match:
                        views_text = views_match.group(1)
            
            # メタデータから再生数を取得（代替方法）
            if not views_text:
                metadata_elements = await element.query_selector_all('span.style-scope.ytd-video-meta-block')
                for meta in metadata_elements:
                    text = await meta.inner_text()
                    if '回視聴' in text or 'views' in text:
                        views_text = re.search(r'([\d,\.]+[KMB]?)', text)
                        if views_text:
                            views_text = views_text.group(1)
                            break
            
            # チャンネル名の取得
            channel_element = await element.query_selector('ytd-channel-name a')
            channel_name = await channel_element.inner_text() if channel_element else None
            
            # 投稿日時の取得
            time_element = await element.query_selector('#metadata-line span:nth-child(2)')
            upload_time = await time_element.inner_text() if time_element else None
            
            if not title or not url:
                return None
            
            return {
                'title': title,
                'url': url,
                'views_text': views_text or '不明',
                'views_count': self._parse_views_count(views_text),
                'channel_name': channel_name,
                'upload_time': upload_time,
                'scrape_timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.debug(f"動画データの抽出エラー: {e}")
            return None
    
    def _parse_views_count(self, views_text: Optional[str]) -> int:
        """
        再生数テキストを数値に変換
        
        Args:
            views_text: 再生数のテキスト（例: "1.2M", "1,234", "1.2万"）
        
        Returns:
            int: 再生数
        """
        if not views_text:
            return 0
        
        try:
            # カンマを削除
            views_text = views_text.replace(',', '').replace('，', '')
            
            # 単位の変換
            multipliers = {
                'K': 1000,
                'k': 1000,
                '千': 1000,
                'M': 1000000,
                'm': 1000000,
                '万': 10000,
                'B': 1000000000,
                'b': 1000000000,
                '億': 100000000
            }
            
            for unit, multiplier in multipliers.items():
                if unit in views_text:
                    number = float(re.search(r'([\d\.]+)', views_text).group(1))
                    return int(number * multiplier)
            
            # 単位がない場合
            number_match = re.search(r'([\d\.]+)', views_text)
            if number_match:
                return int(float(number_match.group(1)))
            
            return 0
            
        except Exception:
            return 0
    
    async def close(self):
        """ブラウザリソースのクリーンアップ"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("ブラウザを正常に終了しました")
            
        except Exception as e:
            logger.error(f"ブラウザの終了中にエラーが発生: {e}")