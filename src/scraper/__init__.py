"""スクレイピング関連モジュール"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ScraperInterface(ABC):
    """スクレイパーの抽象基底クラス"""
    
    @abstractmethod
    async def scrape(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        スクレイピングを実行
        
        Args:
            query: 検索クエリ
            max_results: 最大取得件数
        
        Returns:
            List[Dict[str, Any]]: スクレイピング結果のリスト
        """
        pass
    
    @abstractmethod
    async def close(self):
        """リソースのクリーンアップ"""
        pass