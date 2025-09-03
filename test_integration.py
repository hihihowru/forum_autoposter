#!/usr/bin/env python3
"""
整合測試腳本
測試 Google Sheets + CMoney API 整合
"""
import sys
import asyncio
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.google.sheets_client import GoogleSheetsClient
from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials


async def test_integration():
    """測試完整整合流程"""
    print("開始整合測試...")
    print("=" * 60)
    
    try:
        # 1. 測試 Google Sheets 連接
        print("1. 測試 Google Sheets API...")
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 讀取 KOL 配置
        print("   讀取 KOL 配置...")
        kol_data = sheets_client.read_sheet('同學會帳號管理', 'A1:Z10')
        print(f"   ✅ 成功讀取 {len(kol_data)} 行 KOL 數據")
        
        # 讀取現有任務
        print("   讀取現有任務...")
        task_data = sheets_client.read_sheet('貼文記錄表', 'A1:Z10')
        print(f"   ✅ 成功讀取 {len(task_data)} 行任務數據")
        
        # 2. 分析 KOL 數據結構
        print("\n2. 分析 KOL 數據結構...")
        if len(kol_data) > 1:
            headers = kol_data[0]
            first_kol = kol_data[1] if len(kol_data) > 1 else []
            
            print(f"   欄位數量: {len(headers)}")
            print(f"   主要欄位: {headers[:10]}...")  # 只顯示前 10 個欄位
            
            # 查找關鍵欄位索引
            key_fields = {}
            for i, header in enumerate(headers):
                if '序號' in header:
                    key_fields['serial'] = i
                elif '暱稱' in header:
                    key_fields['nickname'] = i
                elif 'Email' in header or '帳號' in header:
                    key_fields['email'] = i
                elif '密碼' in header:
                    key_fields['password'] = i
            
            print(f"   關鍵欄位位置: {key_fields}")
            
            # 顯示第一個 KOL 的基本信息（隱藏敏感信息）
            if first_kol and key_fields:
                print("   第一個 KOL 信息:")
                if 'serial' in key_fields and len(first_kol) > key_fields['serial']:
                    print(f"     序號: {first_kol[key_fields['serial']]}")
                if 'nickname' in key_fields and len(first_kol) > key_fields['nickname']:
                    print(f"     暱稱: {first_kol[key_fields['nickname']]}")
                if 'email' in key_fields and len(first_kol) > key_fields['email']:
                    email = first_kol[key_fields['email']]
                    print(f"     帳號: {email[:5]}***@{email.split('@')[1] if '@' in email else '***'}")
        
        # 3. 分析任務數據結構
        print("\n3. 分析任務數據結構...")
        if len(task_data) > 1:
            task_headers = task_data[0]
            first_task = task_data[1] if len(task_data) > 1 else []
            
            print(f"   任務欄位數量: {len(task_headers)}")
            print(f"   任務欄位: {task_headers}")
            
            if first_task:
                print("   第一個任務信息:")
                for i, (header, value) in enumerate(zip(task_headers, first_task)):
                    if value and i < 5:  # 只顯示前 5 個有值的欄位
                        print(f"     {header}: {value}")
        
        # 4. 測試 CMoney API 結構（不進行實際登入）
        print("\n4. 測試 CMoney API 結構...")
        cmoney_client = CMoneyClient()
        print("   ✅ CMoney 客戶端初始化成功")
        print("   📝 注意: 實際登入和 API 調用需要有效的 KOL 憑證")
        
        # 5. 展示貼文ID格式
        print("\n5. 貼文ID 格式示例...")
        example_topic_id = "8d37cb0d-3901-4a04-a182-3dc4e09d570e"
        example_kol_serial = "200"
        example_post_id = f"{example_topic_id}::{example_kol_serial}"
        print(f"   話題ID: {example_topic_id}")
        print(f"   KOL序號: {example_kol_serial}")
        print(f"   貼文ID: {example_post_id}")
        print("   ✅ 使用 :: 分隔符避免與 UUID 中的 - 混淆")
        
        print("\n" + "=" * 60)
        print("🎉 整合測試完成！")
        print("✅ Google Sheets API 連接正常")
        print("✅ 數據結構分析完成")
        print("✅ CMoney API 客戶端準備就緒")
        print("✅ 貼文ID 格式設計完成")
        print("\n下一步: 實作話題派發服務")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_integration())
    if not success:
        sys.exit(1)
