"""
Google Sheets API 客戶端
"""
import os
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Google Sheets API 客戶端"""
    
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        """
        初始化 Google Sheets 客戶端
        
        Args:
            credentials_file: Service Account JSON 憑證檔案路徑
            spreadsheet_id: Google Sheets 文件 ID
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """認證 Google Sheets API"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets API 認證成功")
        except Exception as e:
            logger.error(f"Google Sheets API 認證失敗: {e}")
            raise
    
    def read_sheet(self, sheet_name: str, range_name: str = None) -> List[List[str]]:
        """
        讀取 Google Sheets 數據
        
        Args:
            sheet_name: 工作表名稱
            range_name: 範圍 (例如: "A1:Z100")
            
        Returns:
            二維陣列，包含工作表數據
        """
        try:
            if range_name:
                range_str = f"{sheet_name}!{range_name}"
            else:
                range_str = sheet_name
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_str
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"成功讀取 {sheet_name} 工作表，共 {len(values)} 行")
            return values
            
        except HttpError as e:
            logger.error(f"讀取 Google Sheets 失敗: {e}")
            raise
    
    def write_sheet(self, sheet_name: str, values: List[List[str]], 
                   range_name: str = None) -> Dict[str, Any]:
        """
        寫入 Google Sheets 數據
        
        Args:
            sheet_name: 工作表名稱
            values: 要寫入的數據 (二維陣列)
            range_name: 範圍 (例如: "A1:Z100")
            
        Returns:
            API 回應結果
        """
        try:
            if range_name:
                range_str = f"{sheet_name}!{range_name}"
            else:
                range_str = sheet_name
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_str,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"成功寫入 {sheet_name} 工作表，更新了 {result.get('updatedCells', 0)} 個儲存格")
            return result
            
        except HttpError as e:
            logger.error(f"寫入 Google Sheets 失敗: {e}")
            raise
    
    def update_cell(self, sheet_name: str, cell_range: str, value: str) -> Dict[str, Any]:
        """
        更新單個儲存格
        
        Args:
            sheet_name: 工作表名稱
            cell_range: 儲存格範圍 (例如: "A1", "B2")
            value: 要更新的值
            
        Returns:
            API 回應結果
        """
        try:
            range_str = f"{sheet_name}!{cell_range}"
            
            body = {
                'values': [[value]]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_str,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"成功更新儲存格 {sheet_name}!{cell_range} = {value}")
            return result
            
        except HttpError as e:
            logger.error(f"更新儲存格失敗: {e}")
            raise
    
    def append_sheet(self, sheet_name: str, values: List[List[str]]) -> Dict[str, Any]:
        """
        追加數據到 Google Sheets
        
        Args:
            sheet_name: 工作表名稱
            values: 要追加的數據 (二維陣列)
            
        Returns:
            API 回應結果
        """
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"成功追加數據到 {sheet_name} 工作表")
            return result
            
        except HttpError as e:
            logger.error(f"追加 Google Sheets 數據失敗: {e}")
            raise
    
    def get_sheet_info(self) -> Dict[str, Any]:
        """
        獲取工作表資訊
        
        Returns:
            工作表資訊
        """
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            return result
            
        except HttpError as e:
            logger.error(f"獲取工作表資訊失敗: {e}")
            raise


def test_connection():
    """測試 Google Sheets 連接"""
    try:
        # 從環境變量獲取配置
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
        
        # 創建客戶端
        client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 測試讀取
        print("測試讀取同學會帳號管理表...")
        kol_data = client.read_sheet('同學會帳號管理', 'A1:Z10')
        print(f"成功讀取 {len(kol_data)} 行數據")
        
        # 測試讀取貼文記錄表
        print("測試讀取貼文記錄表...")
        post_data = client.read_sheet('貼文記錄表', 'A1:Z10')
        print(f"成功讀取 {len(post_data)} 行數據")
        
        print("Google Sheets API 連接測試成功！")
        return True
        
    except Exception as e:
        print(f"Google Sheets API 連接測試失敗: {e}")
        return False


if __name__ == "__main__":
    test_connection()
