#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細 UGC 分析報告生成器
基於智能分析結果生成可操作的建議
"""

import json
import os
from datetime import datetime

def generate_detailed_report():
    """生成詳細分析報告"""
    
    # 找到最新的分析結果文件
    result_files = [f for f in os.listdir('.') if f.startswith('ugc_analysis_results_')]
    if not result_files:
        print("❌ 未找到分析結果文件")
        return
    
    latest_file = max(result_files)
    print(f"📖 讀取分析結果: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("📊 詳細 UGC 分析報告")
    print("="*80)
    
    # 1. 數據概覽
    total_titles = sum(result['title_count'] for result in data['files_analyzed'].values())
    print(f"\n📈 數據概覽:")
    print(f"   總標題數: {total_titles:,}")
    print(f"   分析文件數: {len(data['files_analyzed'])}")
    print(f"   分析時間: {data['analysis_timestamp']}")
    
    # 2. 文件詳細信息
    print(f"\n📁 文件詳細信息:")
    for file_key, file_data in data['files_analyzed'].items():
        print(f"   {file_key}: {file_data['title_count']:,} 個標題")
    
    # 3. 合併統計分析
    combined = data['combined_statistics']
    
    print(f"\n🎯 核心發現:")
    
    # 長度分布
    if 'length_distribution' in combined:
        length_stats = combined['length_distribution']
        print(f"   平均標題長度: {length_stats['avg_length']:.1f} 字")
        print(f"   中位數長度: {length_stats['median_length']:.1f} 字")
        print(f"   長度分布:")
        print(f"     - 短標題 (≤10字): {length_stats['distribution']['short']/length_stats['total_count']*100:.1f}%")
        print(f"     - 中標題 (11-20字): {length_stats['distribution']['medium']/length_stats['total_count']*100:.1f}%")
        print(f"     - 長標題 (>20字): {length_stats['distribution']['long']/length_stats['total_count']*100:.1f}%")
    
    # 表情符號
    if 'emoji_analysis' in combined:
        emoji_stats = combined['emoji_analysis']
        print(f"   表情符號使用率: {emoji_stats['emoji_usage_rate']:.1f}%")
        print(f"   表情符號多樣性: {emoji_stats['emoji_diversity']} 種")
        print(f"   最常見表情符號:")
        for emoji, count in list(emoji_stats['top_emojis'].items())[:5]:
            print(f"     {emoji}: {count} 次")
    
    # 股票代號
    if 'stock_codes' in combined:
        stock_stats = combined['stock_codes']
        print(f"   股票代號使用率: {stock_stats['stock_usage_rate']:.1f}%")
        print(f"   股票代號多樣性: {stock_stats['stock_diversity']} 種")
        print(f"   最常提到的股票:")
        for code, count in list(stock_stats['top_stocks'].items())[:5]:
            print(f"     {code}: {count} 次")
    
    # 4. 詳細模式分析
    print(f"\n🔍 詳細模式分析:")
    
    # 時間模式
    if 'time_patterns' in combined:
        time_stats = combined['time_patterns']
        print(f"   時間元素使用:")
        for pattern, stats in time_stats.items():
            print(f"     - {pattern}: {stats['rate']:.1f}%")
    
    # 數字模式
    if 'number_patterns' in combined:
        number_stats = combined['number_patterns']
        print(f"   數字類型使用:")
        for pattern, stats in number_stats.items():
            print(f"     - {pattern}: {stats['rate']:.1f}%")
    
    # 熱門話題
    if 'topic_analysis' in combined:
        topic_stats = combined['topic_analysis']
        print(f"   熱門話題分布:")
        sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1]['rate'], reverse=True)
        for topic, stats in sorted_topics[:5]:
            print(f"     - {topic}: {stats['rate']:.1f}%")
    
    # 情感分析
    if 'emotion_analysis' in combined:
        emotion_stats = combined['emotion_analysis']
        print(f"   情感強度分布:")
        for emotion, stats in emotion_stats.items():
            print(f"     - {emotion}: {stats['rate']:.1f}%")
    
    # 互動模式
    if 'interaction_patterns' in combined:
        interaction_stats = combined['interaction_patterns']
        print(f"   互動模式使用:")
        for pattern, stats in interaction_stats.items():
            print(f"     - {pattern}: {stats['rate']:.1f}%")
    
    # 專業術語
    if 'professional_terms' in combined:
        professional_stats = combined['professional_terms']
        print(f"   專業術語使用:")
        for term, stats in professional_stats.items():
            print(f"     - {term}: {stats['rate']:.1f}%")
    
    # 5. AI 標題生成建議
    print(f"\n💡 AI 標題生成智能建議:")
    
    recommendations = []
    
    # 基於長度分布
    if 'length_distribution' in combined:
        length_stats = combined['length_distribution']
        medium_rate = length_stats['distribution']['medium'] / length_stats['total_count'] * 100
        recommendations.append(f"1. 重點生成 {medium_rate:.1f}% 的 11-20 字中等長度標題")
        recommendations.append(f"2. 適度生成短標題 ({length_stats['distribution']['short']/length_stats['total_count']*100:.1f}%) 和長標題 ({length_stats['distribution']['long']/length_stats['total_count']*100:.1f}%)")
    
    # 基於表情符號
    if 'emoji_analysis' in combined:
        emoji_stats = combined['emoji_analysis']
        recommendations.append(f"3. 適度使用表情符號，目標使用率 {emoji_stats['emoji_usage_rate']:.1f}%")
        top_emojis = list(emoji_stats['top_emojis'].keys())[:3]
        recommendations.append(f"4. 優先使用常見表情符號: {', '.join(top_emojis)}")
    
    # 基於互動模式
    if 'interaction_patterns' in combined:
        interaction_stats = combined['interaction_patterns']
        exclamation_rate = interaction_stats['exclamation']['rate']
        question_rate = interaction_stats['question']['rate']
        recommendations.append(f"5. 增加互動性：感嘆句 {exclamation_rate:.1f}%，問句 {question_rate:.1f}%")
    
    # 基於專業術語
    if 'professional_terms' in combined:
        professional_stats = combined['professional_terms']
        fundamental_rate = professional_stats['fundamental']['rate']
        technical_rate = professional_stats['technical']['rate']
        sentiment_rate = professional_stats['sentiment']['rate']
        recommendations.append(f"6. 融入專業術語：基本面 {fundamental_rate:.1f}%，技術面 {technical_rate:.1f}%，籌碼面 {sentiment_rate:.1f}%")
    
    # 基於熱門話題
    if 'topic_analysis' in combined:
        topic_stats = combined['topic_analysis']
        sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1]['rate'], reverse=True)
        top_topic = sorted_topics[0]
        recommendations.append(f"7. 關注熱門話題：{top_topic[0]} ({top_topic[1]['rate']:.1f}%)")
    
    # 基於股票代號
    if 'stock_codes' in combined:
        stock_stats = combined['stock_codes']
        recommendations.append(f"8. 適度使用股票代號，目標使用率 {stock_stats['stock_usage_rate']:.1f}%")
    
    for rec in recommendations:
        print(f"   {rec}")
    
    # 6. KOL 擴展建議
    print(f"\n👥 KOL 擴展建議:")
    
    kol_recommendations = [
        "1. 基於情感強度分布設計不同 KOL 性格（正面、負面、中性）",
        "2. 根據互動模式差異化 KOL 表達方式（問句、感嘆句、指令句）",
        "3. 利用專業術語偏好區分 KOL 專業領域（基本面、技術面、籌碼面）",
        "4. 結合熱門話題設計 KOL 專長領域（AI、半導體、航運等）",
        "5. 參考表情符號使用習慣設計 KOL 風格（活潑、專業、幽默）",
        "6. 根據標題長度偏好設計 KOL 表達習慣（簡潔、詳細、平衡）",
        "7. 利用時間元素使用習慣設計 KOL 時效性偏好",
        "8. 結合數字使用習慣設計 KOL 數據偏好（價格、百分比、張數）"
    ]
    
    for rec in kol_recommendations:
        print(f"   {rec}")
    
    # 7. 實際應用建議
    print(f"\n🎯 實際應用建議:")
    
    application_suggestions = [
        "1. 調整 AI 標題生成策略，重點關注 11-20 字中等長度",
        "2. 增加感嘆句和問句比例，提升互動性",
        "3. 適度使用表情符號，特別是 📈🚀🔥 等投資相關表情",
        "4. 融入專業術語，提升可信度和專業度",
        "5. 關注熱門話題，增加時效性和相關性",
        "6. 適度使用股票代號和具體數字，增加具體性",
        "7. 平衡情感表達，避免過度極端",
        "8. 為不同 KOL 設計差異化的表達風格"
    ]
    
    for suggestion in application_suggestions:
        print(f"   {suggestion}")
    
    # 8. 數據質量評估
    print(f"\n📊 數據質量評估:")
    
    quality_metrics = []
    
    if 'length_distribution' in combined:
        length_stats = combined['length_distribution']
        if length_stats['avg_length'] > 30:
            quality_metrics.append("⚠️ 平均標題長度較長，可能需要簡化")
        else:
            quality_metrics.append("✅ 標題長度分布合理")
    
    if 'emoji_analysis' in combined:
        emoji_stats = combined['emoji_analysis']
        if emoji_stats['emoji_usage_rate'] < 1:
            quality_metrics.append("⚠️ 表情符號使用率較低，可適當增加")
        else:
            quality_metrics.append("✅ 表情符號使用適度")
    
    if 'stock_codes' in combined:
        stock_stats = combined['stock_codes']
        if stock_stats['stock_usage_rate'] < 2:
            quality_metrics.append("⚠️ 股票代號使用率較低，可適當增加")
        else:
            quality_metrics.append("✅ 股票代號使用適度")
    
    for metric in quality_metrics:
        print(f"   {metric}")
    
    print(f"\n✅ 詳細分析報告生成完成！")
    print(f"📁 原始數據文件: {latest_file}")

if __name__ == "__main__":
    generate_detailed_report()
