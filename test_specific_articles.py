"""
測試特定Article ID的互動數據抓取
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from article_interaction_checker import check_multiple_articles, print_interaction_summary

async def test_specific_articles():
    """測試您提供的特定Article ID"""
    
    # 您提供的Article ID列表
    article_ids = [
        "173345934", "173346052", "173346170", "173346308",
        "173346581", "173346990",
        "173347107", "173346681",
        "173347344", "173347504",
        "173345583", "173345697", "173347212"
    ]
    
    print("🧪 測試特定Article ID互動數據抓取")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📝 測試Article ID數量: {len(article_ids)}")
    
    print(f"\n📋 Article ID列表:")
    for i, article_id in enumerate(article_ids, 1):
        print(f"  {i:2d}. {article_id}")
    
    print(f"\n🚀 開始批量測試...")
    print("=" * 60)
    
    # 批量檢查
    results = await check_multiple_articles(article_ids)
    
    # 顯示結果摘要
    print(f"\n📊 測試結果摘要:")
    print(f"  - 總測試數: {results['total_count']}")
    print(f"  - 成功數: {results['successful_count']}")
    print(f"  - 失敗數: {results['failed_count']}")
    print(f"  - 成功率: {results['successful_count']/results['total_count']:.1%}")
    
    # 詳細結果
    print(f"\n📝 詳細結果:")
    print("-" * 60)
    
    successful_articles = []
    failed_articles = []
    
    for i, result in enumerate(results["results"], 1):
        article_id = result["article_id"]
        print(f"\n{i:2d}. Article ID: {article_id}")
        
        if result["success"]:
            data = result["interaction_data"]
            print(f"    ✅ 成功")
            print(f"    - 會員ID: {data['member_id']}")
            print(f"    - 留言數: {data['comments']}")
            print(f"    - 讚數: {data['likes']}")
            print(f"    - 分享數: {data['shares']}")
            print(f"    - 瀏覽數: {data['views']}")
            print(f"    - 互動率: {data['engagement_rate']}")
            
            # 顯示表情符號
            if data['emoji_count']:
                active_emojis = {k: v for k, v in data['emoji_count'].items() if v > 0}
                if active_emojis:
                    print(f"    - 表情符號: {active_emojis}")
            
            successful_articles.append({
                "article_id": article_id,
                "data": data
            })
        else:
            print(f"    ❌ 失敗: {result['error']}")
            failed_articles.append({
                "article_id": article_id,
                "error": result["error"]
            })
    
    # 成功和失敗的Article ID列表
    print(f"\n✅ 成功的Article ID ({len(successful_articles)}個):")
    for article in successful_articles:
        data = article["data"]
        print(f"  - {article['article_id']}: {data['comments']}留言, {data['likes']}讚, {data['shares']}分享")
    
    if failed_articles:
        print(f"\n❌ 失敗的Article ID ({len(failed_articles)}個):")
        for article in failed_articles:
            print(f"  - {article['article_id']}: {article['error']}")
    
    # 互動數據統計
    if successful_articles:
        print(f"\n📈 互動數據統計:")
        total_comments = sum(article["data"]["comments"] for article in successful_articles)
        total_likes = sum(article["data"]["likes"] for article in successful_articles)
        total_shares = sum(article["data"]["shares"] for article in successful_articles)
        total_views = sum(article["data"]["views"] for article in successful_articles)
        
        print(f"  - 總留言數: {total_comments}")
        print(f"  - 總讚數: {total_likes}")
        print(f"  - 總分享數: {total_shares}")
        print(f"  - 總瀏覽數: {total_views}")
        
        # 平均互動數據
        avg_comments = total_comments / len(successful_articles)
        avg_likes = total_likes / len(successful_articles)
        avg_shares = total_shares / len(successful_articles)
        avg_views = total_views / len(successful_articles)
        
        print(f"\n📊 平均互動數據:")
        print(f"  - 平均留言數: {avg_comments:.1f}")
        print(f"  - 平均讚數: {avg_likes:.1f}")
        print(f"  - 平均分享數: {avg_shares:.1f}")
        print(f"  - 平均瀏覽數: {avg_views:.1f}")
        
        # 找出互動最高的文章
        best_article = max(successful_articles, key=lambda x: x["data"]["engagement_rate"])
        print(f"\n🏆 互動最高的文章:")
        print(f"  - Article ID: {best_article['article_id']}")
        print(f"  - 互動率: {best_article['data']['engagement_rate']}")
        print(f"  - 留言數: {best_article['data']['comments']}")
        print(f"  - 讚數: {best_article['data']['likes']}")
    
    print(f"\n✅ 測試完成！")
    print("=" * 60)
    
    return {
        "successful_articles": successful_articles,
        "failed_articles": failed_articles,
        "summary": results
    }

if __name__ == "__main__":
    asyncio.run(test_specific_articles())











