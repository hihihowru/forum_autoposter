#!/usr/bin/env python3
"""
刪除川川哥重複的盤中漲停文章
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加 src 目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

async def main():
    """主執行函數"""
    print("🗑️ 刪除川川哥重複的盤中漲停文章...")
    
    try:
        print("📋 步驟 1: 初始化CMoney客戶端...")
        cmoney_client = CMoneyClient()
        print("✅ CMoney 客戶端初始化成功")
        
        print("📋 步驟 2: 登入川川哥帳號...")
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password=os.getenv('CMONEY_PASSWORD')
        )
        
        token = await cmoney_client.login(credentials)
        print(f"✅ 川川哥登入成功: {token.token[:20]}...")
        
        print("📋 步驟 3: 準備要刪除的文章ID...")
        # 要刪除的文章ID列表（除了最新的173502031）
        articles_to_delete = [
            '173501947',  # 精成科盤中漲停...這根K棒要噴了嗎？
            '173501952',  # 越峰漲停背後...籌碼面爆炸了嗎...還是基...
            '173501956',  # 昇佳電子盤中漲停...這根K棒要噴了嗎...
            '173501962',  # 東友盤中漲停...籌碼面強勢爆發...這裡是...
        ]
        
        print(f"🗑️ 準備刪除 {len(articles_to_delete)} 篇重複文章...")
        
        print("📋 步驟 4: 開始刪除文章...")
        deleted_count = 0
        
        for article_id in articles_to_delete:
            try:
                print(f"🗑️ 刪除文章 {article_id}...")
                
                # 刪除文章
                delete_success = await cmoney_client.delete_article(token.token, article_id)
                
                if delete_success:
                    print(f"✅ 文章 {article_id} 刪除成功")
                    deleted_count += 1
                else:
                    print(f"❌ 文章 {article_id} 刪除失敗")
                
                # 等待一下再刪除下一篇
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ 刪除文章 {article_id} 時發生錯誤: {e}")
                continue
        
        print(f"\n✅ 刪除完成！")
        print(f"📈 成功刪除 {deleted_count} 篇重複文章")
        print(f"📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if deleted_count > 0:
            print(f"🎉 川川哥的頁面現在應該乾淨多了！")
            print(f"🔗 保留的最新文章: https://www.cmoney.tw/forum/article/173502031")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
