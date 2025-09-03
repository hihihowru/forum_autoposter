#!/usr/bin/env python3
"""
檢查 Google Sheets 結構並添加測試數據
"""

import os
import sys
from datetime import datetime, timedelta
import random
import uuid

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.google.sheets_client import GoogleSheetsClient

def check_sheets_structure():
    """檢查 Google Sheets 結構"""
    try:
        # 初始化 Google Sheets 客戶端
        credentials_file = './credentials/google-service-account.json'
        spreadsheet_id = '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        
        client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        print("🔍 檢查 Google Sheets 結構...")
        print("=" * 60)
        
        # 1. 檢查同學會帳號管理表
        print("\n📋 同學會帳號管理表結構:")
        print("-" * 40)
        try:
            kol_headers = client.read_sheet('同學會帳號管理', 'A1:AZ1')
            if kol_headers:
                headers = kol_headers[0]
                print(f"欄位數量: {len(headers)}")
                for i, header in enumerate(headers, 1):
                    print(f"{i:2d}. {header}")
            else:
                print("❌ 無法讀取同學會帳號管理表")
        except Exception as e:
            print(f"❌ 讀取同學會帳號管理表失敗: {e}")
        
        # 2. 檢查貼文記錄表
        print("\n📝 貼文記錄表結構:")
        print("-" * 40)
        try:
            post_headers = client.read_sheet('貼文記錄表', 'A1:AZ1')
            if post_headers:
                headers = post_headers[0]
                print(f"欄位數量: {len(headers)}")
                for i, header in enumerate(headers, 1):
                    print(f"{i:2d}. {header}")
            else:
                print("❌ 無法讀取貼文記錄表")
        except Exception as e:
            print(f"❌ 讀取貼文記錄表失敗: {e}")
        
        # 3. 檢查現有數據
        print("\n📊 現有數據統計:")
        print("-" * 40)
        
        # 同學會帳號管理表數據
        try:
            kol_data = client.read_sheet('同學會帳號管理', 'A:AZ')
            print(f"同學會帳號管理表: {len(kol_data)} 行 (包含標題)")
            if len(kol_data) > 1:
                print(f"  - 實際數據: {len(kol_data) - 1} 筆")
        except Exception as e:
            print(f"❌ 讀取同學會帳號管理表數據失敗: {e}")
        
        # 貼文記錄表數據
        try:
            post_data = client.read_sheet('貼文記錄表', 'A:AZ')
            print(f"貼文記錄表: {len(post_data)} 行 (包含標題)")
            if len(post_data) > 1:
                print(f"  - 實際數據: {len(post_data) - 1} 筆")
        except Exception as e:
            print(f"❌ 讀取貼文記錄表數據失敗: {e}")
        
        # 4. 檢查互動回饋表是否存在
        print("\n📈 互動回饋表檢查:")
        print("-" * 40)
        
        interaction_tables = ['互動回饋_1hr', '互動回饋_1day', '互動回饋_7days']
        for table_name in interaction_tables:
            try:
                data = client.read_sheet(table_name, 'A1:Z1')
                if data:
                    print(f"✅ {table_name}: 存在")
                    headers = data[0]
                    print(f"   欄位數量: {len(headers)}")
                    print(f"   欄位: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
                else:
                    print(f"❌ {table_name}: 不存在或為空")
            except Exception as e:
                print(f"❌ {table_name}: 不存在 ({e})")
        
        return client
        
    except Exception as e:
        print(f"❌ 檢查 Google Sheets 結構失敗: {e}")
        return None

def create_interaction_tables(client):
    """創建互動回饋表"""
    print("\n🛠️ 創建互動回饋表...")
    print("=" * 60)
    
    # 互動回饋表欄位定義
    interaction_headers = [
        'article_id',           # 文章ID
        'member_id',           # KOL會員ID
        'nickname',            # KOL暱稱
        'title',               # 文章標題
        'content',             # 文章內容
        'topic_id',            # 話題ID
        'is_trending_topic',   # 是否為熱門話題
        'post_time',           # 發文時間
        'last_update_time',    # 最後更新時間
        'likes_count',         # 按讚數
        'comments_count',      # 留言數
        'total_interactions',  # 總互動數
        'engagement_rate',     # 互動率
        'growth_rate',         # 成長率
        'collection_error'     # 收集錯誤訊息
    ]
    
    interaction_tables = ['互動回饋_1hr', '互動回饋_1day', '互動回饋_7days']
    
    for table_name in interaction_tables:
        try:
            # 檢查表是否存在
            existing_data = client.read_sheet(table_name, 'A1:Z1')
            if existing_data:
                print(f"✅ {table_name}: 已存在")
                continue
            
            # 創建表 (通過寫入標題行)
            print(f"📝 創建 {table_name}...")
            result = client.write_sheet(table_name, [interaction_headers], 'A1:O1')
            print(f"✅ {table_name}: 創建成功")
            
        except Exception as e:
            print(f"❌ 創建 {table_name} 失敗: {e}")

def generate_mock_interaction_data():
    """生成模擬互動數據"""
    print("\n🎲 生成模擬互動數據...")
    print("=" * 60)
    
    # KOL 基線數據
    kol_baseline = {
        "9505546": {"base_likes": 45, "base_comments": 8, "multiplier": 1.2},  # 川川哥
        "9505547": {"base_likes": 38, "base_comments": 12, "multiplier": 1.0}, # 韭割哥
        "9505548": {"base_likes": 52, "base_comments": 15, "multiplier": 1.4}, # 梅川褲子
        "9505549": {"base_likes": 41, "base_comments": 18, "multiplier": 1.1}, # 龜狗一日
        "9505550": {"base_likes": 48, "base_comments": 22, "multiplier": 1.3}, # 板橋大who
    }
    
    # 生成測試數據
    mock_data = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(20):  # 生成20筆測試數據
        # 隨機選擇KOL
        kol_id = random.choice(list(kol_baseline.keys()))
        baseline = kol_baseline[kol_id]
        
        # 生成文章ID
        article_id = f"{uuid.uuid4()}-{kol_id}"
        
        # 生成互動數據
        likes = int(baseline["base_likes"] * baseline["multiplier"] * random.uniform(0.8, 1.2))
        comments = int(baseline["base_comments"] * baseline["multiplier"] * random.uniform(0.8, 1.2))
        total_interactions = likes + comments
        engagement_rate = round(total_interactions / 1000, 3)  # 假設1000次瀏覽
        
        # 生成時間
        post_time = base_time + timedelta(hours=i*2)
        update_time = post_time + timedelta(hours=1)
        
        mock_data.append([
            article_id,                    # article_id
            kol_id,                       # member_id
            f"KOL_{kol_id}",              # nickname
            f"測試文章標題_{i+1}",          # title
            f"這是第{i+1}篇測試文章的內容",  # content
            f"topic_{i+1}",               # topic_id
            "TRUE" if random.random() > 0.7 else "FALSE",  # is_trending_topic
            post_time.isoformat() + "Z",  # post_time
            update_time.isoformat() + "Z", # last_update_time
            likes,                        # likes_count
            comments,                     # comments_count
            total_interactions,           # total_interactions
            engagement_rate,              # engagement_rate
            round(random.uniform(0.1, 0.5), 2),  # growth_rate
            ""                            # collection_error
        ])
    
    return mock_data

def append_mock_data_to_sheets(client):
    """將模擬數據添加到 Google Sheets"""
    print("\n📤 添加模擬數據到 Google Sheets...")
    print("=" * 60)
    
    # 生成模擬數據
    mock_data = generate_mock_interaction_data()
    
    # 互動回饋表
    interaction_tables = ['互動回饋_1hr', '互動回饋_1day', '互動回饋_7days']
    
    for table_name in interaction_tables:
        try:
            print(f"📝 添加數據到 {table_name}...")
            
            # 為不同時間週期調整數據
            adjusted_data = []
            for row in mock_data:
                adjusted_row = row.copy()
                
                # 根據時間週期調整互動數
                if table_name == '互動回饋_1hr':
                    # 1小時後數據 (基數)
                    pass
                elif table_name == '互動回饋_1day':
                    # 1日後數據 (增加30-50%)
                    likes = int(int(row[9]) * random.uniform(1.3, 1.5))
                    comments = int(int(row[10]) * random.uniform(1.2, 1.4))
                    adjusted_row[9] = likes
                    adjusted_row[10] = comments
                    adjusted_row[11] = likes + comments
                elif table_name == '互動回饋_7days':
                    # 7日後數據 (增加60-80%)
                    likes = int(int(row[9]) * random.uniform(1.6, 1.8))
                    comments = int(int(row[10]) * random.uniform(1.5, 1.7))
                    adjusted_row[9] = likes
                    adjusted_row[10] = comments
                    adjusted_row[11] = likes + comments
                
                adjusted_data.append(adjusted_row)
            
            # 追加數據
            result = client.append_sheet(table_name, adjusted_data)
            print(f"✅ {table_name}: 成功添加 {len(adjusted_data)} 筆數據")
            
        except Exception as e:
            print(f"❌ 添加數據到 {table_name} 失敗: {e}")

def add_test_posts_to_sheet(client):
    """添加測試貼文到貼文記錄表"""
    print("\n📝 添加測試貼文到貼文記錄表...")
    print("=" * 60)
    
    try:
        # 讀取現有標題
        headers = client.read_sheet('貼文記錄表', 'A1:Q1')
        if not headers:
            print("❌ 無法讀取貼文記錄表標題")
            return
        
        header_row = headers[0]
        print(f"貼文記錄表欄位: {', '.join(header_row)}")
        
        # 生成測試貼文數據
        test_posts = []
        base_time = datetime.now() - timedelta(days=3)
        
        kol_data = [
            {"serial": "200", "nickname": "川川哥", "id": "9505546", "persona": "技術派"},
            {"serial": "201", "nickname": "韭割哥", "id": "9505547", "persona": "總經派"},
            {"serial": "202", "nickname": "梅川褲子", "id": "9505548", "persona": "新聞派"},
        ]
        
        for i in range(10):  # 生成10筆測試貼文
            kol = random.choice(kol_data)
            post_id = f"{uuid.uuid4()}-{kol['serial']}"
            topic_id = f"topic_{i+1}"
            
            post_time = base_time + timedelta(hours=i*3)
            
            test_post = [
                post_id,                           # 貼文ID
                kol["serial"],                     # KOL Serial
                kol["nickname"],                   # KOL 暱稱
                kol["id"],                         # KOL ID
                kol["persona"],                    # Persona
                "technical,chart",                 # Content Type
                str(i),                            # 已派發TopicIndex
                topic_id,                          # 已派發TopicID
                f"測試話題標題_{i+1}",              # 已派發TopicTitle
                "技術派,籌碼派",                    # 已派發TopicKeywords
                f"這是第{i+1}篇測試貼文的生成內容",  # 生成內容
                "已發布" if random.random() > 0.2 else "待發布",  # 發文狀態
                post_time.isoformat() + "Z",       # 上次排程時間
                post_time.isoformat() + "Z" if random.random() > 0.2 else "",  # 發文時間戳記
                "",                                # 最近錯誤訊息
                f"post_{i+1}" if random.random() > 0.2 else "",  # 平台發文ID
                f"https://example.com/post/{i+1}" if random.random() > 0.2 else "",  # 平台發文URL
            ]
            
            test_posts.append(test_post)
        
        # 追加測試貼文
        result = client.append_sheet('貼文記錄表', test_posts)
        print(f"✅ 貼文記錄表: 成功添加 {len(test_posts)} 筆測試貼文")
        
    except Exception as e:
        print(f"❌ 添加測試貼文失敗: {e}")

def main():
    """主函數"""
    print("🚀 Google Sheets 結構檢查和數據添加工具")
    print("=" * 60)
    
    # 1. 檢查結構
    client = check_sheets_structure()
    if not client:
        print("❌ 無法連接到 Google Sheets")
        return
    
    # 2. 創建互動回饋表
    create_interaction_tables(client)
    
    # 3. 添加模擬互動數據
    append_mock_data_to_sheets(client)
    
    # 4. 添加測試貼文
    add_test_posts_to_sheet(client)
    
    print("\n✅ 所有操作完成！")
    print("=" * 60)
    print("📊 現在您可以:")
    print("1. 檢查 Google Sheets 中的數據")
    print("2. 開始實作 Dashboard API")
    print("3. 測試儀表板功能")

if __name__ == "__main__":
    main()
