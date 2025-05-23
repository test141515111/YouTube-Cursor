"""データ保存関連モジュール"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class StorageInterface(ABC):
    """ストレージの抽象基底クラス"""
    
    @abstractmethod
    async def save(self, data: List[Dict[str, Any]]) -> bool:
        """
        データを保存
        
        Args:
            data: 保存するデータのリスト
        
        Returns:
            bool: 保存が成功した場合True
        """
        pass
    
    @abstractmethod
    async def load(self) -> List[Dict[str, Any]]:
        """
        データを読み込み
        
        Returns:
            List[Dict[str, Any]]: 読み込んだデータのリスト
        """
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """
        データをクリア
        
        Returns:
            bool: クリアが成功した場合True
        """
        pass