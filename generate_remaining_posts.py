#!/usr/bin/env python3
"""
重新生成剩餘的貼文（修正標題問題）
"""

from unified_post_generator import UnifiedPostGenerator

def main():
    """主函數"""
    print("🚀 重新生成剩餘的貼文（修正標題問題）")
    print("=" * 60)
    
    generator = UnifiedPostGenerator()
    
    # 剩餘的9隻漲停股資料
    remaining_stocks = [
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
        remaining_stocks, 
        include_technical_analysis=True,
        technical_analysis_ratio=0.2
    )
    
    # 預覽前3篇貼文
    generator.preview_posts(posts, count=3)
    
    # 保存到Google Sheets（使用append）
    success = generator.save_to_google_sheets(posts)
    if success:
        print("✅ 成功保存到Google Sheets")
    
    # 保存到JSON
    generator.save_to_json(posts, "remaining_limit_up_posts.json")
    
    print(f"\n📊 生成結果:")
    print(f"總貼文數: {len(posts)} 篇")
    print(f"技術分析: {len([p for p in posts if '技術分析深度解析' in p.generated_content])} 篇")
    print(f"標記為昨天分析: 全部")
    
    print("\n🎯 剩餘貼文生成完成！")

if __name__ == "__main__":
    main()






















