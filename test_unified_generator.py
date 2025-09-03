#!/usr/bin/env python3
"""
測試統一貼文生成架構
"""

from unified_post_generator import UnifiedPostGenerator, TopicData

def test_limit_up_generation():
    """測試漲停股貼文生成"""
    print("🚀 測試漲停股貼文生成...")
    
    generator = UnifiedPostGenerator()
    
    # 22隻漲停股資料
    limit_up_stocks = [
        {"name": "立凱-KY", "id": "5227.TWO", "price": "32.45", "change": "2.95", "change_pct": "10.00%"},
        {"name": "笙科", "id": "5272.TWO", "price": "23.10", "change": "2.10", "change_pct": "10.00%"},
        {"name": "太欣", "id": "5302.TWO", "price": "9.90", "change": "0.90", "change_pct": "10.00%"},
        {"name": "美達科技", "id": "6735.TWO", "price": "69.30", "change": "6.30", "change_pct": "10.00%"},
        {"name": "太普高", "id": "3284.TWO", "price": "23.15", "change": "2.10", "change_pct": "9.98%"}
    ]
    
    posts = generator.generate_limit_up_posts(
        limit_up_stocks, 
        include_technical_analysis=True,
        technical_analysis_ratio=0.4
    )
    
    # 預覽貼文
    generator.preview_posts(posts, count=3)
    
    # 保存到Google Sheets
    success = generator.save_to_google_sheets(posts)
    if success:
        print("✅ 成功保存到Google Sheets")
    
    # 保存到JSON
    generator.save_to_json(posts, "test_limit_up_posts.json")
    
    return posts

def test_trending_topic_generation():
    """測試熱門話題貼文生成"""
    print("\n🚀 測試熱門話題貼文生成...")
    
    generator = UnifiedPostGenerator()
    
    # 範例話題資料
    topics = [
        TopicData(
            topic_id="ai_chip_boom",
            title="AI晶片需求爆發",
            content="AI晶片市場需求持續增長，相關概念股表現亮眼",
            stocks=[
                {"name": "台積電", "id": "2330.TW"},
                {"name": "聯發科", "id": "2454.TW"},
                {"name": "瑞昱", "id": "2379.TW"}
            ]
        ),
        TopicData(
            topic_id="green_energy",
            title="綠能政策利多",
            content="政府推動綠能政策，相關產業受惠",
            stocks=[
                {"name": "中興電", "id": "1513.TW"},
                {"name": "華城", "id": "1519.TW"}
            ]
        )
    ]
    
    posts = generator.generate_trending_topic_posts(
        topics,
        include_technical_analysis=True,
        technical_analysis_ratio=0.3
    )
    
    # 預覽貼文
    generator.preview_posts(posts, count=3)
    
    # 保存到JSON
    generator.save_to_json(posts, "test_trending_posts.json")
    
    return posts

def main():
    """主函數"""
    print("🧪 統一貼文生成架構測試")
    print("=" * 50)
    
    # 測試漲停股生成
    limit_up_posts = test_limit_up_generation()
    
    # 測試熱門話題生成
    trending_posts = test_trending_topic_generation()
    
    print(f"\n📊 測試結果:")
    print(f"漲停股貼文: {len(limit_up_posts)} 篇")
    print(f"熱門話題貼文: {len(trending_posts)} 篇")
    print(f"總計: {len(limit_up_posts) + len(trending_posts)} 篇")
    
    print("\n✅ 統一貼文生成架構測試完成！")

if __name__ == "__main__":
    main()
