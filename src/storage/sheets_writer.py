"""Google Sheets書き込みモジュール"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..utils.logger import get_logger, md_logger
from ..utils.config import config
from . import StorageInterface


logger = get_logger(__name__)


class GoogleSheetsStorage(StorageInterface):
    """Google Sheetsストレージ"""
    
    def __init__(self, sheet_id: Optional[str] = None, sheet_name: str = "Sheet1"):
        """
        初期化
        
        Args:
            sheet_id: Google SheetsのID
            sheet_name: シート名
        """
        self.sheet_id = sheet_id or config.sheet_id
        self.sheet_name = sheet_name
        self.service = None
        self._init_service()
    
    def _init_service(self):
        """Google Sheets APIサービスの初期化"""
        try:
            # 認証情報の取得
            credentials = self._get_credentials()
            
            if credentials:
                # APIサービスの構築
                self.service = build('sheets', 'v4', credentials=credentials)
                logger.info("Google Sheets APIサービスを初期化しました")
            else:
                logger.warning("Google Sheets認証情報が見つかりません")
                
        except Exception as e:
            logger.error(f"Google Sheets APIの初期化に失敗: {e}")
            md_logger.log_error("Google Sheets API初期化エラー", e)
    
    def _get_credentials(self):
        """認証情報を取得"""
        try:
            # 環境変数から認証情報を取得（GitHub Actions用）
            if config.google_sheets_creds:
                creds_dict = json.loads(config.google_sheets_creds)
                return service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            
            # ファイルから認証情報を取得（ローカル開発用）
            elif config.google_sheets_creds_path and os.path.exists(config.google_sheets_creds_path):
                return service_account.Credentials.from_service_account_file(
                    config.google_sheets_creds_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"認証情報の取得に失敗: {e}")
            return None
    
    async def save(self, data: List[Dict[str, Any]]) -> bool:
        """
        データをGoogle Sheetsに保存
        
        Args:
            data: 保存するデータのリスト
        
        Returns:
            bool: 保存が成功した場合True
        """
        if not self.service or not self.sheet_id:
            logger.error("Google Sheets APIが初期化されていないか、Sheet IDが設定されていません")
            return False
        
        try:
            # 既存のデータを確認
            existing_data = await self._get_sheet_data()
            
            # ヘッダーの確認と作成
            if not existing_data:
                await self._create_headers()
            
            # データを追加用に整形
            rows = []
            for item in data:
                row = [
                    item.get('title', ''),
                    item.get('url', ''),
                    item.get('views_text', ''),
                    str(item.get('views_count', 0)),
                    item.get('channel_name', ''),
                    item.get('upload_time', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
                rows.append(row)
            
            # データを追加
            if rows:
                body = {
                    'values': rows
                }
                
                result = self.service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_id,
                    range=f'{self.sheet_name}!A:G',
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                
                updated_rows = result.get('updates', {}).get('updatedRows', 0)
                logger.info(f"Google Sheetsに{updated_rows}行を追加しました")
                
                md_logger.log_success(
                    "Google Sheets保存成功",
                    f"シートID: {self.sheet_id}\n追加行数: {updated_rows}"
                )
                
                return True
            
            return True
            
        except HttpError as e:
            logger.error(f"Google Sheets APIエラー: {e}")
            md_logger.log_error("Google Sheets APIエラー", e, f"シートID: {self.sheet_id}")
            return False
        except Exception as e:
            logger.error(f"データの保存に失敗: {e}")
            md_logger.log_error("Google Sheets保存エラー", e)
            return False
    
    async def _create_headers(self):
        """ヘッダー行を作成"""
        headers = [
            ['タイトル', 'URL', '再生数', '再生数（数値）', 'チャンネル名', '投稿日時', '取得日時']
        ]
        
        body = {
            'values': headers
        }
        
        self.service.spreadsheets().values().update(
            spreadsheetId=self.sheet_id,
            range=f'{self.sheet_name}!A1:G1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        logger.info("ヘッダー行を作成しました")
    
    async def _get_sheet_data(self) -> List[List[str]]:
        """シートの既存データを取得"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f'{self.sheet_name}!A:G'
            ).execute()
            
            return result.get('values', [])
            
        except Exception:
            return []
    
    async def load(self) -> List[Dict[str, Any]]:
        """
        Google Sheetsからデータを読み込み
        
        Returns:
            List[Dict[str, Any]]: 読み込んだデータのリスト
        """
        if not self.service or not self.sheet_id:
            logger.error("Google Sheets APIが初期化されていないか、Sheet IDが設定されていません")
            return []
        
        try:
            # データを取得
            values = await self._get_sheet_data()
            
            if not values or len(values) < 2:
                return []
            
            # ヘッダーを取得
            headers = values[0]
            
            # データを辞書形式に変換
            data = []
            for row in values[1:]:
                item = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        if header == '再生数（数値）':
                            try:
                                item['views_count'] = int(row[i])
                            except ValueError:
                                item['views_count'] = 0
                        else:
                            # ヘッダー名を英語に変換
                            key_map = {
                                'タイトル': 'title',
                                'URL': 'url',
                                '再生数': 'views_text',
                                'チャンネル名': 'channel_name',
                                '投稿日時': 'upload_time',
                                '取得日時': 'saved_at'
                            }
                            key = key_map.get(header, header)
                            item[key] = row[i]
                
                if item:
                    data.append(item)
            
            logger.info(f"Google Sheetsから{len(data)}件のデータを読み込みました")
            return data
            
        except Exception as e:
            logger.error(f"データの読み込みに失敗: {e}")
            return []
    
    async def clear(self) -> bool:
        """
        シートをクリア（ヘッダーは残す）
        
        Returns:
            bool: クリアが成功した場合True
        """
        if not self.service or not self.sheet_id:
            logger.error("Google Sheets APIが初期化されていないか、Sheet IDが設定されていません")
            return False
        
        try:
            # ヘッダー以外をクリア
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.sheet_id,
                range=f'{self.sheet_name}!A2:G',
                body={}
            ).execute()
            
            logger.info("Google Sheetsのデータをクリアしました（ヘッダーは保持）")
            return True
            
        except Exception as e:
            logger.error(f"データのクリアに失敗: {e}")
            return False
    
    async def check_duplicates(self, urls: List[str]) -> List[str]:
        """
        重複するURLをチェック
        
        Args:
            urls: チェックするURLのリスト
        
        Returns:
            List[str]: 既に存在するURLのリスト
        """
        try:
            existing_data = await self.load()
            existing_urls = {item.get('url') for item in existing_data if item.get('url')}
            
            duplicates = [url for url in urls if url in existing_urls]
            
            if duplicates:
                logger.info(f"{len(duplicates)}件の重複URLを検出しました")
            
            return duplicates
            
        except Exception as e:
            logger.error(f"重複チェックに失敗: {e}")
            return []
    
    def get_sheet_url(self) -> str:
        """Google SheetsのURLを取得"""
        if self.sheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"
        return ""