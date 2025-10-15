#!/usr/bin/env python3
"""
互動數據總結報告
"""

import asyncio
from src.clients.google.sheets_client import GoogleSheetsClient

async def generate_summary():
    """生成互動數據總結"""
    sheets_client = GoogleSheetsClient(
        credentials_file='credentials/google-service-account.json',
        spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
    )
    
    # 讀取互動數據
    data = sheets_client.read_sheet('互動回饋_1hr', 'A:O')
    
    print("=" * 60)
    print("📊 即時互動數據總結報告")
    print("=" * 60)
    
    if len(data) <= 1:
        print("❌ 沒有找到互動數據")
        return
    
    # 統計數據
    total_posts = len(data) - 1  # 減去標題行
    total_interactions = 0
    total_likes = 0
    total_comments = 0
    
    print(f"📈 總貼文數: {total_posts}")
    print()
    
    print("📋 各貼文互動詳情:")
    print("-" * 60)
    
    for i, row in enumerate(data[1:], start=1):
        if len(row) >= 15 and row[0]:  # 確保有 Article ID
            article_id = row[0]
            kol_name = row[2]
            title = row[3][:30] + "..." if len(row[3]) > 30 else row[3]
            likes = int(row[9]) if row[9] else 0
            comments = int(row[10]) if row[10] else 0
            total_post_interactions = int(row[11]) if row[11] else 0
            engagement_rate = row[12]
            update_time = row[8]
            
            total_interactions += total_post_interactions
            total_likes += likes
            total_comments += comments
            
            print(f"{i}. {kol_name}")
            print(f"   Article ID: {article_id}")
            print(f"   標題: {title}")
            print(f"   讚數: {likes} | 留言數: {comments} | 總互動: {total_post_interactions}")
            print(f"   互動率: {engagement_rate}")
            print(f"   更新時間: {update_time}")
            print()
    
    print("=" * 60)
    print("📊 整體統計:")
    print(f"   總讚數: {total_likes}")
    print(f"   總留言數: {total_comments}")
    print(f"   總互動數: {total_interactions}")
    print(f"   平均每篇互動: {total_interactions/total_posts:.1f}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(generate_summary())
