"""
測試增強版內容分析器
"""

import asyncio
from src.services.learning.enhanced_content_analyzer import EnhancedContentAnalyzer

async def test_enhanced_analyzer():
    """測試增強版分析器"""
    analyzer = EnhancedContentAnalyzer()
    
    # 測試內容
    test_content = """
    台積電今天收在580元，我覺得這個價位還算合理。
    
    從技術面來看，目前站穩在月線之上，KD指標也呈現黃金交叉。
    不過我個人認為，短線可能會有回檔壓力。
    
    你覺得呢？歡迎留言分享你的看法！
    
    期待明天能有好表現 🔥
    """
    
    print("🎯 增強版內容分析器測試")
    print("=" * 50)
    
    # 分析內容
    features = await analyzer.analyze_content(test_content, "test_content")
    
    print(f"📝 內容分析結果:")
    print(f"個人化分數: {features.personal_score:.2f}")
    print(f"情感分數: {features.emotion_score:.2f}")
    print(f"互動分數: {features.interaction_score:.2f}")
    print(f"創意分數: {features.creative_score:.2f}")
    print(f"幽默分數: {features.humor_score:.2f}")
    print(f"直接回答分數: {features.direct_answer_score:.2f}")
    print(f"結構分數: {features.structure_score:.2f}")
    print(f"總互動分數: {features.total_engagement_score:.2f}")
    print(f"互動等級: {features.engagement_level}")
    
    print(f"\n🔍 詳細分析:")
    print(f"個人代詞: {features.personal_pronouns}")
    print(f"情感詞彙: {features.emotion_words}")
    print(f"問題: {features.questions}")
    print(f"創意元素: {features.creative_elements}")
    print(f"幽默元素: {features.humor_elements}")
    
    # 生成優化建議
    optimization = await analyzer.generate_optimization_suggestions(features)
    
    print(f"\n💡 優化建議:")
    print(f"當前分數: {optimization.current_score:.2f}")
    print(f"目標分數: {optimization.target_score:.2f}")
    print(f"改善潛力: {optimization.improvement_potential:.2f}")
    print(f"預期改善: {optimization.expected_improvement:.2f}")
    
    print(f"\n具體建議:")
    for rec in optimization.specific_recommendations:
        print(f"  - {rec}")
    
    print(f"\n優先行動:")
    for action in optimization.priority_actions:
        print(f"  - {action}")
    
    # 與高互動範例比較
    comparison = await analyzer.compare_with_high_engagement_examples(test_content)
    
    print(f"\n📊 與高互動範例比較:")
    if comparison.get("most_similar_example"):
        example = comparison["most_similar_example"]
        print(f"最相似範例: {example['type']}")
        print(f"相似度: {example['similarity']:.2f}")
        print(f"描述: {example['description']}")
    
    print(f"\n🎯 高互動技巧:")
    tips = analyzer.get_high_engagement_tips()
    for i, tip in enumerate(tips, 1):
        print(f"{i}. {tip}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_analyzer())

























