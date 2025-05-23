"""ローカルファイルストレージモジュール"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from ..utils.logger import get_logger, md_logger
from . import StorageInterface


logger = get_logger(__name__)


class LocalFileStorage(StorageInterface):
    """ローカルファイルストレージ"""
    
    def __init__(self, file_path: str = "data/youtube_results.json", format: str = "json"):
        """
        初期化
        
        Args:
            file_path: ファイルパス
            format: ファイル形式（json, csv）
        """
        self.file_path = Path(file_path)
        self.format = format.lower()
        
        # ディレクトリの作成
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def save(self, data: List[Dict[str, Any]]) -> bool:
        """
        データをファイルに保存
        
        Args:
            data: 保存するデータのリスト
        
        Returns:
            bool: 保存が成功した場合True
        """
        try:
            # タイムスタンプを追加
            for item in data:
                if 'saved_at' not in item:
                    item['saved_at'] = datetime.now().isoformat()
            
            if self.format == 'json':
                return await self._save_json(data)
            elif self.format == 'csv':
                return await self._save_csv(data)
            else:
                raise ValueError(f"サポートされていない形式: {self.format}")
                
        except Exception as e:
            logger.error(f"データの保存に失敗: {e}")
            md_logger.log_error("ローカルストレージ保存エラー", e, f"ファイル: {self.file_path}")
            return False
    
    async def _save_json(self, data: List[Dict[str, Any]]) -> bool:
        """JSON形式で保存"""
        try:
            # 既存のデータを読み込み
            existing_data = await self.load()
            
            # 新しいデータを追加
            existing_data.extend(data)
            
            # ファイルに書き込み
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSONファイルに{len(data)}件のデータを保存しました: {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"JSON保存エラー: {e}")
            raise
    
    async def _save_csv(self, data: List[Dict[str, Any]]) -> bool:
        """CSV形式で保存"""
        try:
            if not data:
                return True
            
            # ファイルが存在するか確認
            file_exists = self.file_path.exists()
            
            # CSVファイルに追記
            with open(self.file_path, 'a', encoding='utf-8', newline='') as f:
                fieldnames = [
                    'title', 'url', 'views_text', 'views_count',
                    'channel_name', 'upload_time', 'saved_at'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # ヘッダーを書き込み（新規ファイルの場合）
                if not file_exists:
                    writer.writeheader()
                
                # データを書き込み
                for item in data:
                    # 必要なフィールドのみ抽出
                    row = {k: item.get(k, '') for k in fieldnames}
                    writer.writerow(row)
            
            logger.info(f"CSVファイルに{len(data)}件のデータを保存しました: {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"CSV保存エラー: {e}")
            raise
    
    async def load(self) -> List[Dict[str, Any]]:
        """
        ファイルからデータを読み込み
        
        Returns:
            List[Dict[str, Any]]: 読み込んだデータのリスト
        """
        try:
            if not self.file_path.exists():
                return []
            
            if self.format == 'json':
                return await self._load_json()
            elif self.format == 'csv':
                return await self._load_csv()
            else:
                raise ValueError(f"サポートされていない形式: {self.format}")
                
        except Exception as e:
            logger.error(f"データの読み込みに失敗: {e}")
            return []
    
    async def _load_json(self) -> List[Dict[str, Any]]:
        """JSON形式から読み込み"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("JSONファイルの解析に失敗しました")
            return []
    
    async def _load_csv(self) -> List[Dict[str, Any]]:
        """CSV形式から読み込み"""
        try:
            data = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # views_countを数値に変換
                    if 'views_count' in row and row['views_count']:
                        try:
                            row['views_count'] = int(row['views_count'])
                        except ValueError:
                            row['views_count'] = 0
                    data.append(row)
            return data
        except Exception as e:
            logger.error(f"CSV読み込みエラー: {e}")
            return []
    
    async def clear(self) -> bool:
        """
        ファイルをクリア
        
        Returns:
            bool: クリアが成功した場合True
        """
        try:
            if self.file_path.exists():
                if self.format == 'json':
                    # 空のJSONファイルを作成
                    with open(self.file_path, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                elif self.format == 'csv':
                    # ヘッダーのみのCSVファイルを作成
                    with open(self.file_path, 'w', encoding='utf-8', newline='') as f:
                        fieldnames = [
                            'title', 'url', 'views_text', 'views_count',
                            'channel_name', 'upload_time', 'saved_at'
                        ]
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                
                logger.info(f"ファイルをクリアしました: {self.file_path}")
                return True
                
            return True
            
        except Exception as e:
            logger.error(f"ファイルのクリアに失敗: {e}")
            return False
    
    def get_file_path(self) -> str:
        """ファイルパスを取得"""
        return str(self.file_path)
    
    async def backup(self, backup_dir: str = "data/backups") -> str:
        """
        ファイルをバックアップ
        
        Args:
            backup_dir: バックアップディレクトリ
        
        Returns:
            str: バックアップファイルのパス
        """
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # バックアップファイル名を生成
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_path / f"{self.file_path.stem}_{timestamp}{self.file_path.suffix}"
            
            # ファイルをコピー
            if self.file_path.exists():
                import shutil
                shutil.copy2(self.file_path, backup_file)
                logger.info(f"バックアップを作成しました: {backup_file}")
                return str(backup_file)
            
            return ""
            
        except Exception as e:
            logger.error(f"バックアップの作成に失敗: {e}")
            return ""