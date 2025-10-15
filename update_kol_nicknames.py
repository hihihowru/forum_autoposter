#!/usr/bin/env python3
"""
更新 KOL 暱稱腳本
從 Google Sheets 讀取 KOL 記錄表，並使用 CMoney API 更新暱稱
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.google.sheets_client import GoogleSheetsClient
from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials, UpdateNicknameResult
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KOLNicknameUpdater:
    """KOL 暱稱更新器"""
    
    def __init__(self):
        """初始化更新器"""
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        self.cmoney_client = CMoneyClient()
        
    async def get_kol_data(self) -> List[Dict[str, Any]]:
        """從 Google Sheets 獲取 KOL 數據"""
        try:
            logger.info("📊 讀取 Google Sheets KOL 記錄表...")
            
            # 讀取同學會帳號管理表
            data = self.sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            
            if not data or len(data) < 2:
                logger.warning("❌ 沒有找到 KOL 配置數據")
                return []
            
            headers = data[0]
            rows = data[1:]
            
            # 建立欄位索引映射
            field_map = {}
            for i, header in enumerate(headers):
                if '序號' in header:
                    field_map['serial'] = i
                elif '暱稱' in header:
                    field_map['nickname'] = i
                elif 'Email' in header or '帳號' in header:
                    field_map['email'] = i
                elif '密碼' in header:
                    field_map['password'] = i
                elif 'MemberId' in header:
                    field_map['member_id'] = i
                elif '狀態' in header and i < 20:
                    field_map['status'] = i
            
            logger.info(f"📋 欄位映射: {field_map}")
            
            # 解析 KOL 資料
            kol_profiles = []
            for row_idx, row in enumerate(rows):
                if len(row) < max(field_map.values()) + 1:
                    continue
                
                # 檢查狀態是否為 active
                status = row[field_map.get('status', 0)] if field_map.get('status') is not None else ""
                if status.lower() != 'active':
                    continue
                
                kol_data = {
                    'row_index': row_idx + 2,  # Google Sheets 行號 (從1開始，加上標題行)
                    'serial': row[field_map['serial']] if field_map.get('serial') is not None else "",
                    'nickname': row[field_map['nickname']] if field_map.get('nickname') is not None else "",
                    'email': row[field_map['email']] if field_map.get('email') is not None else "",
                    'password': row[field_map['password']] if field_map.get('password') is not None else "",
                    'member_id': row[field_map['member_id']] if field_map.get('member_id') is not None else "",
                    'status': status
                }
                
                # 只處理有完整資料的 KOL
                if kol_data['email'] and kol_data['password'] and kol_data['nickname']:
                    kol_profiles.append(kol_data)
            
            logger.info(f"✅ 找到 {len(kol_profiles)} 個活躍的 KOL")
            return kol_profiles
            
        except Exception as e:
            logger.error(f"❌ 讀取 KOL 數據失敗: {e}")
            return []
    
    async def update_nickname_for_kol(self, kol_data: Dict[str, Any]) -> Dict[str, Any]:
        """為單個 KOL 更新暱稱"""
        try:
            logger.info(f"🔄 開始更新 KOL {kol_data['serial']} ({kol_data['nickname']}) 的暱稱...")
            
            # 1. 登入獲取 Bearer Token
            credentials = LoginCredentials(
                email=kol_data['email'],
                password=kol_data['password']
            )
            
            logger.info(f"🔐 登入 KOL {kol_data['serial']}...")
            access_token = await self.cmoney_client.login(credentials)
            
            if not access_token or not access_token.token:
                error_msg = f"登入失敗: {kol_data['serial']}"
                logger.error(f"❌ {error_msg}")
                return {
                    'serial': kol_data['serial'],
                    'nickname': kol_data['nickname'],
                    'success': False,
                    'error': error_msg,
                    'raw_response': None
                }
            
            logger.info(f"✅ 登入成功: {kol_data['serial']}")
            
            # 2. 更新暱稱
            logger.info(f"📝 更新暱稱為: {kol_data['nickname']}")
            result = await self.cmoney_client.update_nickname(access_token.token, kol_data['nickname'])
            
            if result.success:
                logger.info(f"✅ 暱稱更新成功: {kol_data['serial']} -> {result.new_nickname}")
                return {
                    'serial': kol_data['serial'],
                    'nickname': result.new_nickname,
                    'success': True,
                    'error': None,
                    'raw_response': result.raw_response
                }
            else:
                error_msg = f"暱稱更新失敗: {result.error_message}"
                logger.error(f"❌ {error_msg}")
                return {
                    'serial': kol_data['serial'],
                    'nickname': kol_data['nickname'],
                    'success': False,
                    'error': error_msg,
                    'raw_response': result.raw_response
                }
                
        except Exception as e:
            error_msg = f"更新過程發生錯誤: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                'serial': kol_data['serial'],
                'nickname': kol_data['nickname'],
                'success': False,
                'error': error_msg,
                'raw_response': None
            }
    
    async def update_all_nicknames(self) -> Dict[str, Any]:
        """更新所有 KOL 的暱稱"""
        try:
            logger.info("🚀 開始批量更新 KOL 暱稱...")
            print("=" * 80)
            
            # 1. 獲取 KOL 數據
            kol_profiles = await self.get_kol_data()
            
            if not kol_profiles:
                logger.warning("❌ 沒有找到可更新的 KOL")
                return {
                    'total': 0,
                    'success': 0,
                    'failed': 0,
                    'results': []
                }
            
            # 2. 批量更新暱稱
            results = []
            success_count = 0
            failed_count = 0
            
            for kol_data in kol_profiles:
                print(f"\n📋 處理 KOL {kol_data['serial']}: {kol_data['nickname']}")
                print("-" * 60)
                
                result = await self.update_nickname_for_kol(kol_data)
                results.append(result)
                
                if result['success']:
                    success_count += 1
                    print(f"✅ 成功: {result['serial']} -> {result['nickname']}")
                else:
                    failed_count += 1
                    print(f"❌ 失敗: {result['serial']} - {result['error']}")
                    if result['raw_response']:
                        print(f"📄 原始回應: {result['raw_response']}")
                
                # 添加延遲避免 API 限制
                await asyncio.sleep(2)
            
            # 3. 生成摘要報告
            print("\n" + "=" * 80)
            print("📊 更新摘要報告")
            print("=" * 80)
            print(f"總計 KOL 數量: {len(kol_profiles)}")
            print(f"✅ 成功更新: {success_count}")
            print(f"❌ 更新失敗: {failed_count}")
            print(f"📈 成功率: {(success_count/len(kol_profiles)*100):.1f}%")
            
            # 顯示失敗的詳細信息
            if failed_count > 0:
                print(f"\n❌ 失敗詳情:")
                for result in results:
                    if not result['success']:
                        print(f"  - {result['serial']}: {result['error']}")
            
            return {
                'total': len(kol_profiles),
                'success': success_count,
                'failed': failed_count,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"❌ 批量更新失敗: {e}")
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'results': [],
                'error': str(e)
            }
        finally:
            # 關閉客戶端
            self.cmoney_client.close()

async def main():
    """主函數"""
    try:
        print("🎯 KOL 暱稱更新工具")
        print("=" * 80)
        print("📋 功能說明:")
        print("  1. 從 Google Sheets 讀取 KOL 記錄表")
        print("  2. 自動登入每個 KOL 帳號獲取 Bearer Token")
        print("  3. 使用 CMoney API 更新暱稱為 Google Sheets 中的稱呼")
        print("  4. 生成詳細的更新報告")
        print("=" * 80)
        
        # 創建更新器
        updater = KOLNicknameUpdater()
        
        # 執行更新
        result = await updater.update_all_nicknames()
        
        # 最終結果
        if result['total'] > 0:
            print(f"\n🎉 更新完成！")
            print(f"📊 總計: {result['total']} 個 KOL")
            print(f"✅ 成功: {result['success']} 個")
            print(f"❌ 失敗: {result['failed']} 個")
        else:
            print(f"\n⚠️ 沒有找到可更新的 KOL")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 程式執行失敗: {e}")
        return None

if __name__ == "__main__":
    # 執行主程式
    result = asyncio.run(main())
    
    if result:
        print(f"\n📋 最終結果: {result}")
    else:
        print(f"\n❌ 程式執行失敗")
