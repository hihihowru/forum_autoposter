#!/usr/bin/env python3
"""
重新生成22篇漲停股貼文（標記為昨天分析）
"""

from unified_post_generator import UnifiedPostGenerator

def main():
    """主函數"""
    print("🚀 重新生成22篇漲停股貼文（標記為昨天分析）")
    print("=" * 60)
    
    generator = UnifiedPostGenerator()
    
    # 22隻漲停股資料
    limit_up_stocks = [
        {"name": "立凱-KY", "id": "5227.TWO", "price": "32.45", "change": "2.95", "change_pct": "10.00%"},
        {"name": "笙科", "id": "5272.TWO", "price": "23.10", "change": "2.10", "change_pct": "10.00%"},
        {"name": "太欣", "id": "5302.TWO", "price": "9.90", "change": "0.90", "change_pct": "10.00%"},
        {"name": "美達科技", "id": "6735.TWO", "price": "69.30", "change": "6.30", "change_pct": "10.00%"},
        {"name": "太普高", "id": "3284.TWO", "price": "23.15", "change": "2.10", "change_pct": "9.98%"},
        {"name": "佳凌", "id": "4976.TW", "price": "49.05", "change": "4.45", "change_pct": "9.98%"},
        {"name": "康霈*", "id": "6919.TW", "price": "231.50", "change": "21.00", "change_pct": "9.98%"},
        {"name": "鮮活果汁-KY", "id": "1256.TW", "price": "143.50", "change": "13.00", "change_pct": "9.96%"},
        {"name": "長園科", "id": "8038.TWO", "price": "57.40", "change": "5.20", "change_pct": "9.96%"},
        {"name": "金居", "id": "8358.TWO", "price": "215.50", "change": "19.50", "change_pct": "9.95%"},
        {"name": "合一", "id": "4743.TWO", "price": "78.50", "change": "7.10", "change_pct": "9.94%"},
        {"name": "驊訊", "id": "6237.TWO", "price": "50.90", "change": "4.60", "change_pct": "9.94%"},
        {"name": "錼創科技-KY創", "id": "6854.TW", "price": "183.00", "change": "16.50", "change_pct": "9.91%"},
        {"name": "醣聯", "id": "4168.TWO", "price": "26.15", "change": "2.35", "change_pct": "9.87%"},
        {"name": "東友", "id": "5438.TWO", "price": "25.60", "change": "2.30", "change_pct": "9.87%"},
        {"name": "宏旭-KY", "id": "2243.TW", "price": "15.60", "change": "1.40", "change_pct": "9.86%"},
        {"name": "豐達科", "id": "3004.TW", "price": "145.00", "change": "13.00", "change_pct": "9.85%"},
        {"name": "沛亨", "id": "6291.TWO", "price": "156.50", "change": "14.00", "change_pct": "9.82%"},
        {"name": "順藥", "id": "6535.TWO", "price": "224.50", "change": "20.00", "change_pct": "9.78%"},
        {"name": "江興鍛", "id": "4528.TWO", "price": "19.10", "change": "1.70", "change_pct": "9.77%"},
        {"name": "友勁", "id": "6142.TW", "price": "10.80", "change": "0.96", "change_pct": "9.76%"},
        {"name": "義隆", "id": "2458.TW", "price": "131.00", "change": "11.50", "change_pct": "9.62%"}
    ]
    
    # 生成貼文
    posts = generator.generate_limit_up_posts(
        limit_up_stocks, 
        include_technical_analysis=True,
        technical_analysis_ratio=0.2  # 20%包含技術分析
    )
    
    # 預覽前3篇貼文
    generator.preview_posts(posts, count=3)
    
    # 保存到Google Sheets
    success = generator.save_to_google_sheets(posts)
    if success:
        print("✅ 成功保存到Google Sheets")
    
    # 保存到JSON
    generator.save_to_json(posts, "generated_limit_up_posts_v3.json")
    
    print(f"\n📊 生成結果:")
    print(f"總貼文數: {len(posts)} 篇")
    print(f"技術分析: {len([p for p in posts if '技術分析深度解析' in p.generated_content])} 篇")
    print(f"標記為昨天分析: 全部")
    
    print("\n🎯 貼文生成完成！可以開始每分鐘發文了。")

if __name__ == "__main__":
    main()








