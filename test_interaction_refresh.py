"""
測試互動數據刷新功能
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient

async def test_interaction_refresh():
    """測試互動數據刷新功能"""
    
    print("🧪 測試互動數據刷新功能")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 初始化客戶端
        cmoney_client = CMoneyClient()
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 1. 測試獲取所有Article ID
        print("\n📝 步驟1: 獲取所有Article ID")
        print("-" * 40)
        
        # 從貼文記錄表獲取所有Article ID
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Z')
        
        if not post_data or len(post_data) < 2:
            print("❌ 沒有找到貼文記錄數據")
            return
        
        headers = post_data[0]
        rows = post_data[1:]
        
        # 找到platform_post_id欄位索引
        platform_post_id_idx = None
        for i, header in enumerate(headers):
            if 'platform_post_id' in header.lower() or '貼文id' in header.lower():
                platform_post_id_idx = i
                break
        
        if platform_post_id_idx is None:
            print("❌ 找不到platform_post_id欄位")
            return
        
        # 提取所有Article ID
        article_ids = []
        for row in rows:
            if len(row) > platform_post_id_idx and row[platform_post_id_idx]:
                article_id = row[platform_post_id_idx].strip()
                if article_id and article_id not in article_ids:
                    article_ids.append(article_id)
        
        print(f"✅ 找到 {len(article_ids)} 個Article ID")
        print(f"前5個Article ID: {article_ids[:5]}")
        
        # 2. 測試登入
        print("\n📝 步驟2: 登入CMoney")
        print("-" * 40)
        
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password='N9t1kY3x'
        )
        
        login_result = await cmoney_client.login(credentials)
        if not login_result or login_result.is_expired:
            print("❌ 登入失敗")
            return
        
        print(f"✅ 登入成功，Token: {login_result.token[:20]}...")
        
        # 3. 測試刷新前幾個Article的互動數據
        print("\n📝 步驟3: 刷新互動數據")
        print("-" * 40)
        
        test_article_ids = article_ids[:3]  # 只測試前3個
        interaction_results = []
        
        for i, article_id in enumerate(test_article_ids, 1):
            print(f"\n{i}. 刷新Article ID: {article_id}")
            
            try:
                # 獲取互動數據
                interaction_data = await cmoney_client.get_article_interactions(
                    login_result.token, 
                    article_id
                )
                
                if interaction_data:
                    result = {
                        "article_id": article_id,
                        "likes": interaction_data.likes,
                        "comments": interaction_data.comments,
                        "shares": interaction_data.shares,
                        "views": interaction_data.views,
                        "engagement_rate": interaction_data.engagement_rate
                    }
                    interaction_results.append(result)
                    
                    print(f"  ✅ 成功")
                    print(f"  - 讚數: {interaction_data.likes}")
                    print(f"  - 留言數: {interaction_data.comments}")
                    print(f"  - 分享數: {interaction_data.shares}")
                    print(f"  - 瀏覽數: {interaction_data.views}")
                    print(f"  - 互動率: {interaction_data.engagement_rate}")
                else:
                    print(f"  ❌ 無法獲取互動數據")
                    
            except Exception as e:
                print(f"  ❌ 刷新失敗: {e}")
            
            # 添加延遲避免API限制
            await asyncio.sleep(1)
        
        # 4. 測試更新Google Sheets
        print(f"\n📝 步驟4: 更新Google Sheets")
        print("-" * 40)
        
        if interaction_results:
            # 準備要寫入的數據
            update_data = []
            
            for result in interaction_results:
                # 計算總互動數
                total_interactions = result["likes"] + result["comments"] + result["shares"]
                
                # 準備行數據
                row_data = [
                    result["article_id"],  # Article ID
                    "",  # Member ID
                    "",  # 暱稱
                    "",  # 標題
                    "",  # 內容
                    "",  # Topic ID
                    "",  # 是否為熱門話題
                    datetime.now().isoformat(),  # 發文時間
                    datetime.now().isoformat(),  # 最後更新時間
                    result["likes"],  # 讚數
                    result["comments"],  # 留言數
                    total_interactions,  # 總互動數
                    result["engagement_rate"],  # 互動率
                    0.0,  # 成長率
                    ""  # 收集錯誤
                ]
                update_data.append(row_data)
            
            # 更新到互動回饋_1hr表格
            try:
                # 讀取現有數據
                existing_data = sheets_client.read_sheet('互動回饋_1hr', 'A:O')
                
                if existing_data:
                    # 更新現有數據
                    for row_data in update_data:
                        article_id = row_data[0]
                        
                        # 查找是否已存在
                        found = False
                        for i, existing_row in enumerate(existing_data[1:], 1):  # 跳過標題行
                            if len(existing_row) > 0 and existing_row[0] == article_id:
                                # 更新現有行
                                existing_data[i] = row_data
                                found = True
                                break
                        
                        if not found:
                            # 添加新行
                            existing_data.append(row_data)
                    
                    # 寫回Google Sheets
                    sheets_client.write_sheet('互動回饋_1hr', existing_data, 'A:O')
                    print(f"✅ 成功更新互動回饋_1hr表格，共 {len(update_data)} 條記錄")
                else:
                    # 創建新表格
                    headers = [
                        'Article ID', 'Member ID', '暱稱', '標題', '生成內文', 'Topic ID',
                        '是否為熱門話題', '發文時間', '最後更新時間', '讚數', '留言數',
                        '總互動數', '互動率', '成長率', '收集錯誤'
                    ]
                    new_data = [headers] + update_data
                    sheets_client.write_sheet('互動回饋_1hr', new_data, 'A:O')
                    print(f"✅ 成功創建互動回饋_1hr表格，共 {len(update_data)} 條記錄")
                    
            except Exception as e:
                print(f"❌ 更新Google Sheets失敗: {e}")
        else:
            print("❌ 沒有互動數據可更新")
        
        # 5. 驗證更新結果
        print(f"\n📝 步驟5: 驗證更新結果")
        print("-" * 40)
        
        try:
            # 重新讀取數據驗證
            updated_data = sheets_client.read_sheet('互動回饋_1hr', 'A:O')
            
            if updated_data and len(updated_data) > 1:
                print(f"✅ 驗證成功，表格中有 {len(updated_data) - 1} 條記錄")
                
                # 顯示前幾條記錄
                for i, row in enumerate(updated_data[1:4], 1):  # 顯示前3條記錄
                    if len(row) >= 10:
                        print(f"  {i}. Article ID: {row[0]}, 讚數: {row[9]}, 留言數: {row[10]}")
            else:
                print("❌ 驗證失敗，沒有找到更新後的數據")
                
        except Exception as e:
            print(f"❌ 驗證失敗: {e}")
        
        print(f"\n✅ 測試完成！")
        print("=" * 60)
        
        # 顯示測試摘要
        print("📊 測試摘要:")
        print(f"  - 總Article ID數: {len(article_ids)}")
        print(f"  - 測試Article數: {len(test_article_ids)}")
        print(f"  - 成功刷新數: {len(interaction_results)}")
        print(f"  - 更新記錄數: {len(update_data) if 'update_data' in locals() else 0}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_interaction_refresh())



