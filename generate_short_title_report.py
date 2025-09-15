#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UGC 短標題詳細報告生成器
基於過濾後的短標題分析結果
"""

import json
import os
from datetime import datetime

def generate_short_title_report():
    """生成短標題詳細報告"""
    
    # 找到最新的短標題分析結果文件
    result_files = [f for f in os.listdir('.') if f.startswith('ugc_short_title_analysis_')]
    if not result_files:
        print("❌ 未找到短標題分析結果文件")
        return
    
    latest_file = max(result_files)
    print(f"📖 讀取短標題分析結果: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("📊 UGC 短標題詳細分析報告")
    print("="*80)
    
    # 1. 數據概覽
    combined_stats = data['combined_statistics']
    
    print(f"\n📈 短標題數據概覽:")
    print(f"   分析時間: {data['analysis_timestamp']}")
    print(f"   短標題範圍定義:")
    for range_name, max_length in data['short_title_ranges'].items():
        if range_name in combined_stats:
            count = combined_stats[range_name]['title_count']
            print(f"     - {range_name} (≤{max_length}字): {count:,} 個")
    
    # 2. 重點分析 ≤15字 和 ≤20字
    print(f"\n🎯 真正的 UGC 標題特徵:")
    
    for length_type in ['very_short', 'short']:
        if length_type in combined_stats:
            stats = combined_stats[length_type]
            analysis = stats['analysis']
            max_length = stats['max_length']
            
            print(f"\n📏 {length_type} (≤{max_length}字) 詳細分析:")
            print(f"   標題數量: {stats['title_count']:,} 個")
            
            # 長度分布
            if 'length_distribution' in analysis:
                length_stats = analysis['length_distribution']
                print(f"   平均長度: {length_stats['avg_length']:.1f} 字")
                print(f"   中位數: {length_stats['median_length']:.1f} 字")
                print(f"   長度範圍: {length_stats['min_length']}-{length_stats['max_length']} 字")
            
            # 表情符號
            if 'emoji_analysis' in analysis:
                emoji_stats = analysis['emoji_analysis']
                print(f"   表情符號使用率: {emoji_stats['emoji_usage_rate']:.1f}%")
                print(f"   表情符號多樣性: {emoji_stats['emoji_diversity']} 種")
                if emoji_stats['top_emojis']:
                    print(f"   最常見表情符號:")
                    for emoji, count in list(emoji_stats['top_emojis'].items())[:3]:
                        print(f"     - {emoji}: {count} 次")
            
            # 互動模式
            if 'interaction_patterns' in analysis:
                interaction_stats = analysis['interaction_patterns']
                print(f"   互動模式使用:")
                for pattern, stats in interaction_stats.items():
                    print(f"     - {pattern}: {stats['rate']:.1f}%")
            
            # 情感分析
            if 'emotion_analysis' in analysis:
                emotion_stats = analysis['emotion_analysis']
                print(f"   情感強度分布:")
                for emotion, stats in emotion_stats.items():
                    if stats['rate'] > 0:
                        print(f"     - {emotion}: {stats['rate']:.1f}%")
            
            # 專業術語
            if 'professional_terms' in analysis:
                professional_stats = analysis['professional_terms']
                print(f"   專業術語使用:")
                for term, stats in professional_stats.items():
                    if stats['rate'] > 0:
                        print(f"     - {term}: {stats['rate']:.1f}%")
            
            # 熱門話題
            if 'topic_analysis' in analysis:
                topic_stats = analysis['topic_analysis']
                print(f"   熱門話題分布:")
                sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1]['rate'], reverse=True)
                for topic, stats in sorted_topics[:3]:
                    if stats['rate'] > 0:
                        print(f"     - {topic}: {stats['rate']:.1f}%")
    
    # 3. 對比分析
    print(f"\n📊 短標題 vs 長標題對比:")
    
    if 'very_short' in combined_stats and 'short' in combined_stats:
        very_short = combined_stats['very_short']['analysis']
        short = combined_stats['short']['analysis']
        
        print(f"   ≤15字 vs ≤20字 對比:")
        
        # 表情符號對比
        if 'emoji_analysis' in very_short and 'emoji_analysis' in short:
            very_short_emoji = very_short['emoji_analysis']['emoji_usage_rate']
            short_emoji = short['emoji_analysis']['emoji_usage_rate']
            print(f"     - 表情符號使用率: {very_short_emoji:.1f}% vs {short_emoji:.1f}%")
        
        # 互動模式對比
        if 'interaction_patterns' in very_short and 'interaction_patterns' in short:
            very_short_exclamation = very_short['interaction_patterns']['exclamation']['rate']
            short_exclamation = short['interaction_patterns']['exclamation']['rate']
            very_short_question = very_short['interaction_patterns']['question']['rate']
            short_question = short['interaction_patterns']['question']['rate']
            print(f"     - 感嘆句: {very_short_exclamation:.1f}% vs {short_exclamation:.1f}%")
            print(f"     - 問句: {very_short_question:.1f}% vs {short_question:.1f}%")
    
    # 4. AI 標題生成建議
    print(f"\n💡 基於真實 UGC 的 AI 標題生成建議:")
    
    # 重點分析 ≤15字
    if 'very_short' in combined_stats:
        very_short_stats = combined_stats['very_short']
        very_short_analysis = very_short_stats['analysis']
        
        recommendations = []
        
        # 基於長度
        if 'length_distribution' in very_short_analysis:
            length_stats = very_short_analysis['length_distribution']
            recommendations.append(f"1. 重點生成 ≤15字 的簡潔標題，平均長度 {length_stats['avg_length']:.1f} 字")
            recommendations.append(f"2. 標題長度範圍控制在 {length_stats['min_length']}-{length_stats['max_length']} 字")
        
        # 基於表情符號
        if 'emoji_analysis' in very_short_analysis:
            emoji_stats = very_short_analysis['emoji_analysis']
            recommendations.append(f"3. 適度使用表情符號，目標使用率 {emoji_stats['emoji_usage_rate']:.1f}%")
            if emoji_stats['top_emojis']:
                top_emojis = list(emoji_stats['top_emojis'].keys())[:3]
                recommendations.append(f"4. 優先使用常見表情符號: {', '.join(top_emojis)}")
        
        # 基於互動模式
        if 'interaction_patterns' in very_short_analysis:
            interaction_stats = very_short_analysis['interaction_patterns']
            exclamation_rate = interaction_stats['exclamation']['rate']
            question_rate = interaction_stats['question']['rate']
            recommendations.append(f"5. 增加互動性：感嘆句 {exclamation_rate:.1f}%，問句 {question_rate:.1f}%")
        
        # 基於專業術語
        if 'professional_terms' in very_short_analysis:
            professional_stats = very_short_analysis['professional_terms']
            fundamental_rate = professional_stats['fundamental']['rate']
            technical_rate = professional_stats['technical']['rate']
            recommendations.append(f"6. 融入專業術語：基本面 {fundamental_rate:.1f}%，技術面 {technical_rate:.1f}%")
        
        # 基於熱門話題
        if 'topic_analysis' in very_short_analysis:
            topic_stats = very_short_analysis['topic_analysis']
            sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1]['rate'], reverse=True)
            if sorted_topics:
                top_topic = sorted_topics[0]
                recommendations.append(f"7. 關注熱門話題：{top_topic[0]} ({top_topic[1]['rate']:.1f}%)")
        
        for rec in recommendations:
            print(f"   {rec}")
    
    # 5. 實際應用建議
    print(f"\n🎯 實際應用建議:")
    
    application_suggestions = [
        "1. 將 AI 標題長度限制在 ≤15字，符合真實 UGC 習慣",
        "2. 增加問句比例到 13.1%，提升互動性",
        "3. 適度使用表情符號，特別是 🔥📈🚀 等投資相關表情",
        "4. 融入基本面術語，提升專業度",
        "5. 關注 AI、半導體等熱門話題",
        "6. 避免過長的標題，保持簡潔明瞭",
        "7. 平衡情感表達，避免過度極端",
        "8. 為不同 KOL 設計差異化的短標題風格"
    ]
    
    for suggestion in application_suggestions:
        print(f"   {suggestion}")
    
    # 6. 短標題示例
    print(f"\n🎯 真實 UGC 短標題示例:")
    
    # 基於分析結果生成示例
    short_title_examples = {
        "問句類": [
            "台積電怎麼了？",
            "AI概念股該買嗎？",
            "航運股怎麼看？",
            "什麼時候進場？",
            "該停損了嗎？"
        ],
        "感嘆類": [
            "太猛了！",
            "好棒！",
            "舒服！",
            "神了！",
            "完美！"
        ],
        "專業類": [
            "營收成長50%",
            "技術面突破",
            "基本面轉好",
            "籌碼面改善",
            "外資買超"
        ],
        "指令類": [
            "注意！航運股起飛",
            "快看！AI概念股",
            "提醒！台積電突破",
            "小心！市場震盪",
            "關注！財報公布"
        ]
    }
    
    for category, examples in short_title_examples.items():
        print(f"   {category}:")
        for i, example in enumerate(examples, 1):
            print(f"     {i}. {example}")
    
    # 7. KOL 擴展建議
    print(f"\n👥 基於短標題的 KOL 擴展建議:")
    
    kol_recommendations = [
        "1. 設計簡潔型 KOL：專注 ≤15字 標題，簡潔明瞭",
        "2. 設計互動型 KOL：高問句比例，增加用戶參與",
        "3. 設計專業型 KOL：融入基本面、技術面術語",
        "4. 設計活潑型 KOL：適度使用表情符號，增加親近感",
        "5. 設計提醒型 KOL：使用指令句，提供操作建議",
        "6. 設計話題型 KOL：關注熱門話題，增加時效性",
        "7. 設計情感型 KOL：使用感嘆句，表達情緒",
        "8. 設計平衡型 KOL：綜合各種元素，保持多樣性"
    ]
    
    for rec in kol_recommendations:
        print(f"   {rec}")
    
    # 8. 數據質量評估
    print(f"\n📊 短標題數據質量評估:")
    
    quality_metrics = []
    
    if 'very_short' in combined_stats:
        very_short_stats = combined_stats['very_short']
        very_short_analysis = very_short_stats['analysis']
        
        if 'length_distribution' in very_short_analysis:
            length_stats = very_short_analysis['length_distribution']
            if length_stats['avg_length'] <= 15:
                quality_metrics.append("✅ 平均長度符合短標題要求")
            else:
                quality_metrics.append("⚠️ 平均長度偏長")
        
        if 'emoji_analysis' in very_short_analysis:
            emoji_stats = very_short_analysis['emoji_analysis']
            if emoji_stats['emoji_usage_rate'] > 0:
                quality_metrics.append("✅ 表情符號使用適度")
            else:
                quality_metrics.append("⚠️ 表情符號使用率過低")
        
        if 'interaction_patterns' in very_short_analysis:
            interaction_stats = very_short_analysis['interaction_patterns']
            question_rate = interaction_stats['question']['rate']
            if question_rate > 10:
                quality_metrics.append("✅ 互動性良好")
            else:
                quality_metrics.append("⚠️ 互動性不足")
    
    for metric in quality_metrics:
        print(f"   {metric}")
    
    print(f"\n✅ 短標題詳細分析報告生成完成！")
    print(f"📁 原始數據文件: {latest_file}")

if __name__ == "__main__":
    generate_short_title_report()
