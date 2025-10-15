#!/usr/bin/env python3
"""
更新 KOL 209 暱稱腳本
將 KOL 209 的暱稱從 "爆爆哥" 改成 "報爆哥"
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.google.sheets_client import GoogleSheetsClient
from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def update_kol_209_nickname():
    """更新 KOL 209 的暱稱"""
    try:
        print("🎯 更新 KOL 209 暱稱")
        print("=" * 50)
        print("📋 目標: 將 KOL 209 的暱稱從 '爆爆哥' 改成 '報爆哥'")
        print("=" * 50)
        
        # 1. 初始化客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        cmoney_client = CMoneyClient()
        
        # 2. 讀取 Google Sheets 數據
        logger.info("📊 讀取 Google Sheets KOL 記錄表...")
        data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
        
        if not data or len(data) < 2:
            logger.error("❌ 沒有找到 KOL 配置數據")
            return False
        
        headers = data[0]
        rows = data[1:]
        
        # 3. 建立欄位索引映射
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
        
        # 4. 找到 KOL 209
        kol_209_data = None
        row_index = None
        
        for row_idx, row in enumerate(rows):
            if len(row) < max(field_map.values()) + 1:
                continue
            
            serial = row[field_map['serial']] if field_map.get('serial') is not None else ""
            
            if serial == "209":
                kol_209_data = {
                    'row_index': row_idx + 2,  # Google Sheets 行號
                    'serial': serial,
                    'nickname': row[field_map['nickname']] if field_map.get('nickname') is not None else "",
                    'email': row[field_map['email']] if field_map.get('email') is not None else "",
                    'password': row[field_map['password']] if field_map.get('password') is not None else "",
                    'member_id': row[field_map['member_id']] if field_map.get('member_id') is not None else "",
                    'status': row[field_map['status']] if field_map.get('status') is not None else ""
                }
                row_index = row_idx
                break
        
        if not kol_209_data:
            logger.error("❌ 沒有找到 KOL 209")
            return False
        
        print(f"📋 找到 KOL 209:")
        print(f"  - 序號: {kol_209_data['serial']}")
        print(f"  - 目前暱稱: {kol_209_data['nickname']}")
        print(f"  - Email: {kol_209_data['email']}")
        print(f"  - 狀態: {kol_209_data['status']}")
        
        # 5. 更新 Google Sheets 中的暱稱
        new_nickname = "報爆哥"
        logger.info(f"📝 更新 Google Sheets 中的暱稱為: {new_nickname}")
        
        # 更新行數據
        updated_row = rows[row_index].copy()
        updated_row[field_map['nickname']] = new_nickname
        
        # 寫入 Google Sheets
        range_name = f'A{kol_209_data["row_index"]}:Z{kol_209_data["row_index"]}'
        sheets_client.write_sheet('同學會帳號管理', [updated_row], range_name)
        
        logger.info(f"✅ Google Sheets 更新成功: {new_nickname}")
        
        # 6. 登入 CMoney 並更新暱稱
        logger.info(f"🔐 登入 KOL 209...")
        credentials = LoginCredentials(
            email=kol_209_data['email'],
            password=kol_209_data['password']
        )
        
        access_token = await cmoney_client.login(credentials)
        
        if not access_token or not access_token.token:
            logger.error(f"❌ 登入失敗: {kol_209_data['serial']}")
            return False
        
        logger.info(f"✅ 登入成功: {kol_209_data['serial']}")
        
        # 7. 更新暱稱
        logger.info(f"📝 更新 CMoney 暱稱為: {new_nickname}")
        result = await cmoney_client.update_nickname(access_token.token, new_nickname)
        
        if result.success:
            logger.info(f"✅ 暱稱更新成功: {kol_209_data['serial']} -> {result.new_nickname}")
            print(f"\n🎉 更新完成！")
            print(f"📊 KOL 209 暱稱已成功更新為: {result.new_nickname}")
            print(f"📄 API 回應: {result.raw_response}")
            return True
        else:
            logger.error(f"❌ 暱稱更新失敗: {result.error_message}")
            print(f"\n❌ 更新失敗: {result.error_message}")
            if result.raw_response:
                print(f"📄 原始回應: {result.raw_response}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 更新過程發生錯誤: {e}")
        print(f"\n❌ 更新失敗: {e}")
        return False
    finally:
        # 關閉客戶端
        if 'cmoney_client' in locals():
            cmoney_client.close()

async def main():
    """主函數"""
    try:
        success = await update_kol_209_nickname()
        
        if success:
            print(f"\n✅ 任務完成！KOL 209 暱稱已成功更新為 '報爆哥'")
        else:
            print(f"\n❌ 任務失敗！請檢查錯誤訊息")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 程式執行失敗: {e}")
        return False

if __name__ == "__main__":
    # 執行主程式
    result = asyncio.run(main())
    
    if result:
        print(f"\n🎉 成功！")
    else:
        print(f"\n❌ 失敗！")
