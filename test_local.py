"""ローカルテスト用スクリプト"""

import asyncio
import sys
from src.scraper.youtube_scraper import YoutubeScraper
from src.storage.local_storage import LocalFileStorage
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def test_scraping():
    """スクレイピングのテスト"""
    logger.info("ローカルテストを開始します...")
    
    # スクレイパーの作成（ローカルブラウザ使用）
    scraper = YoutubeScraper(use_browserless=False)
    
    try:
        # テスト用に少ない件数でスクレイピング
        results = await scraper.scrape("ChatGPT", max_results=5)
        
        if results:
            logger.info(f"\n{len(results)}件の動画を取得しました:")
            for i, video in enumerate(results, 1):
                logger.info(f"{i}. {video['title'][:50]}...")
                logger.info(f"   URL: {video['url']}")
                logger.info(f"   再生数: {video['views_text']}")
                logger.info("")
            
            # テスト用JSONファイルに保存
            storage = LocalFileStorage("data/test_results.json", "json")
            if await storage.save(results):
                logger.info(f"テスト結果を保存しました: {storage.get_file_path()}")
        else:
            logger.warning("動画が取得できませんでした")
            
    except Exception as e:
        logger.error(f"テスト中にエラーが発生: {e}")
        raise
    finally:
        await scraper.close()


if __name__ == "__main__":
    logger.info("=== YouTube Scraper ローカルテスト ===")
    logger.info("注意: このテストはPlaywrightがローカルにインストールされている必要があります")
    logger.info("playwright install chromium を実行してください\n")
    
    try:
        asyncio.run(test_scraping())
        logger.info("\nテストが正常に完了しました！")
    except KeyboardInterrupt:
        logger.info("\nテストを中断しました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nテストが失敗しました: {e}")
        sys.exit(1)