"""YouTube検索結果スクレイピングツール - メインエントリーポイント"""

import asyncio
import argparse
import sys
from typing import List, Dict, Any

from src.scraper.youtube_scraper import YoutubeScraper
from src.storage.local_storage import LocalFileStorage
from src.storage.sheets_writer import GoogleSheetsStorage
from src.utils.logger import get_logger, md_logger
from src.utils.config import config


logger = get_logger(__name__)


async def scrape_youtube(query: str, max_results: int, use_browserless: bool = False) -> List[Dict[str, Any]]:
    """
    YouTube検索結果をスクレイピング
    
    Args:
        query: 検索クエリ
        max_results: 最大取得件数
        use_browserless: Browserlessを使用するかどうか
    
    Returns:
        List[Dict[str, Any]]: スクレイピング結果
    """
    scraper = YoutubeScraper(use_browserless=use_browserless)
    
    try:
        logger.info(f"スクレイピングを開始します - クエリ: {query}, 最大取得件数: {max_results}")
        results = await scraper.scrape(query, max_results)
        logger.info(f"スクレイピング完了 - {len(results)}件取得")
        return results
        
    finally:
        await scraper.close()


async def save_results(results: List[Dict[str, Any]], use_sheets: bool = True, use_local: bool = True):
    """
    スクレイピング結果を保存
    
    Args:
        results: スクレイピング結果
        use_sheets: Google Sheetsに保存するか
        use_local: ローカルファイルに保存するか
    """
    if not results:
        logger.warning("保存するデータがありません")
        return
    
    success_count = 0
    
    # ローカルファイルに保存
    if use_local:
        try:
            # JSON形式で保存
            json_storage = LocalFileStorage("data/youtube_results.json", "json")
            if await json_storage.save(results):
                logger.info(f"JSONファイルへの保存が完了しました: {json_storage.get_file_path()}")
                success_count += 1
            
            # CSV形式でも保存
            csv_storage = LocalFileStorage("data/youtube_results.csv", "csv")
            if await csv_storage.save(results):
                logger.info(f"CSVファイルへの保存が完了しました: {csv_storage.get_file_path()}")
                success_count += 1
                
        except Exception as e:
            logger.error(f"ローカルファイルへの保存に失敗: {e}")
            md_logger.log_error("ローカルファイル保存エラー", e)
    
    # Google Sheetsに保存
    if use_sheets and config.sheet_id:
        try:
            sheets_storage = GoogleSheetsStorage()
            
            # 重複チェック
            urls = [r['url'] for r in results if r.get('url')]
            duplicates = await sheets_storage.check_duplicates(urls)
            
            if duplicates:
                logger.warning(f"{len(duplicates)}件の重複URLがあります")
                # 重複を除外
                results = [r for r in results if r.get('url') not in duplicates]
            
            if results and await sheets_storage.save(results):
                logger.info(f"Google Sheetsへの保存が完了しました: {sheets_storage.get_sheet_url()}")
                success_count += 1
                
        except Exception as e:
            logger.error(f"Google Sheetsへの保存に失敗: {e}")
            md_logger.log_error("Google Sheets保存エラー", e)
    
    # 結果サマリー
    md_logger.log_success(
        "データ保存完了",
        f"保存先数: {success_count}\n保存データ数: {len(results)}件"
    )


async def main():
    """メイン処理"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='YouTube検索結果スクレイピングツール')
    parser.add_argument('--query', '-q', 
                        default=config.default_search_query,
                        help='検索クエリ（デフォルト: ChatGPT）')
    parser.add_argument('--max-results', '-m', 
                        type=int, 
                        default=config.max_results,
                        help='最大取得件数（デフォルト: 50）')
    parser.add_argument('--use-browserless', '-b',
                        action='store_true',
                        help='Browserlessを使用する')
    parser.add_argument('--no-sheets',
                        action='store_true',
                        help='Google Sheetsへの保存をスキップ')
    parser.add_argument('--no-local',
                        action='store_true',
                        help='ローカルファイルへの保存をスキップ')
    
    args = parser.parse_args()
    
    # 開始ログ
    logger.info("="*50)
    logger.info("YouTube検索結果スクレイピングツール 開始")
    logger.info("="*50)
    
    md_logger.log_info(
        "スクレイピング開始",
        f"クエリ: {args.query}\n最大取得件数: {args.max_results}\nBrowserless使用: {args.use_browserless}"
    )
    
    try:
        # スクレイピング実行
        results = await scrape_youtube(
            query=args.query,
            max_results=args.max_results,
            use_browserless=args.use_browserless
        )
        
        if results:
            # 結果を保存
            await save_results(
                results,
                use_sheets=not args.no_sheets,
                use_local=not args.no_local
            )
            
            # サマリー出力
            logger.info("\n=== スクレイピング結果サマリー ===")
            logger.info(f"取得件数: {len(results)}")
            
            # 再生数ランキング（上位5件）
            sorted_results = sorted(results, key=lambda x: x.get('views_count', 0), reverse=True)
            logger.info("\n再生数TOP5:")
            for i, video in enumerate(sorted_results[:5], 1):
                logger.info(f"{i}. {video['title'][:50]}... - {video['views_text']}回")
            
        else:
            logger.warning("スクレイピング結果が空です")
            
    except KeyboardInterrupt:
        logger.info("\nユーザーによって中断されました")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        md_logger.log_error("メイン処理エラー", e)
        sys.exit(1)
        
    finally:
        logger.info("\n処理が完了しました")


if __name__ == "__main__":
    # イベントループの実行
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n処理を中断しました")