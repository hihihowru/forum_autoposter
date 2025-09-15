#!/usr/bin/env python3
"""
分析 anya TSV 文件中的真實 UGC 標題類型
"""

import re
from collections import Counter, defaultdict

def analyze_title_patterns():
    """分析標題模式"""
    
    # 讀取 TSV 文件
    titles = []
    with open('anya-forumteam-1756973422036-23159383983751583.tsv', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and line != 'title' and line != '""':
                titles.append(line)
    
    print(f"📊 總共分析 {len(titles)} 個標題")
    print("="*60)
    
    # 1. 標題長度分析
    title_lengths = [len(title) for title in titles]
    print(f"📏 標題長度統計:")
    print(f"   平均長度: {sum(title_lengths)/len(title_lengths):.1f} 字")
    print(f"   最短: {min(title_lengths)} 字")
    print(f"   最長: {max(title_lengths)} 字")
    print()
    
    # 2. 表情符號分析
    emoji_pattern = re.compile(r'[😀-🙏🌀-🗿🚀-🛿️]')
    emoji_titles = [title for title in titles if emoji_pattern.search(title)]
    print(f"😊 使用表情符號的標題: {len(emoji_titles)} 個 ({len(emoji_titles)/len(titles)*100:.1f}%)")
    print("   範例:", emoji_titles[:5])
    print()
    
    # 3. 標題類型分類
    title_categories = {
        '營收財報': [],
        '技術分析': [],
        '操作建議': [],
        '市場情緒': [],
        '新聞資訊': [],
        '個人分享': [],
        '問答討論': [],
        '其他': []
    }
    
    # 關鍵詞分類
    keywords = {
        '營收財報': ['營收', '財報', 'EPS', '獲利', '業績', '公告', '快訊'],
        '技術分析': ['突破', '支撐', '壓力', '均線', '技術', 'K線', '趨勢', '洗盤', '做頭'],
        '操作建議': ['買進', '賣出', '加碼', '停損', '分批', '當沖', '操作', '建議'],
        '市場情緒': ['瘋狂', '熱潮', '狂飆', '大漲', '大跌', '恐慌', '興奮', '死氣沉沉'],
        '新聞資訊': ['新聞', '報導', '公告', '合作', '擴產', '布局', '題材'],
        '個人分享': ['我的', '自己', '分享', '經驗', '心得', '操作邏輯'],
        '問答討論': ['?', '？', '什麼', '如何', '為什麼', '該', '嗎']
    }
    
    for title in titles:
        categorized = False
        for category, words in keywords.items():
            if any(word in title for word in words):
                title_categories[category].append(title)
                categorized = True
                break
        if not categorized:
            title_categories['其他'].append(title)
    
    print("📋 標題類型分類:")
    for category, titles_list in title_categories.items():
        if titles_list:
            print(f"   {category}: {len(titles_list)} 個 ({len(titles_list)/len(titles)*100:.1f}%)")
            print(f"      範例: {titles_list[:3]}")
            print()
    
    # 4. 特殊符號分析
    special_chars = {
        '【】': [],
        '《》': [],
        '()': [],
        '💰💎': [],
        '數字+%': [],
        '股票代號': []
    }
    
    for title in titles:
        if '【' in title and '】' in title:
            special_chars['【】'].append(title)
        if '《' in title and '》' in title:
            special_chars['《》'].append(title)
        if '(' in title and ')' in title:
            special_chars['()'].append(title)
        if any(char in title for char in ['💰', '💎', '💵', '💸']):
            special_chars['💰💎'].append(title)
        if re.search(r'\d+%', title):
            special_chars['數字+%'].append(title)
        if re.search(r'\d{4}', title):  # 股票代號通常是4位數字
            special_chars['股票代號'].append(title)
    
    print("🔍 特殊符號分析:")
    for symbol_type, titles_list in special_chars.items():
        if titles_list:
            print(f"   {symbol_type}: {len(titles_list)} 個")
            print(f"      範例: {titles_list[:2]}")
            print()
    
    # 5. 情感詞彙分析
    emotion_words = {
        '正面': ['好棒', '舒服', '開心', '期待', '看好', '強勢', '猛猛的', '棒棒的'],
        '負面': ['爛', '慘', '死', '騙', '狠', '爛透了', '慘兮兮', '沒救'],
        '中性': ['注意', '關注', '提醒', '建議', '分析', '展望']
    }
    
    emotion_counts = defaultdict(int)
    for title in titles:
        for emotion, words in emotion_words.items():
            if any(word in title for word in words):
                emotion_counts[emotion] += 1
    
    print("😊 情感詞彙分析:")
    for emotion, count in emotion_counts.items():
        print(f"   {emotion}: {count} 個 ({count/len(titles)*100:.1f}%)")
    print()
    
    # 6. 網路用語分析
    internet_slang = ['GG', 'GG了', '加油', '舒服', '猛猛的', '棒棒的', '好狠', '不演了', '拭目以待']
    slang_titles = [title for title in titles if any(slang in title for slang in internet_slang)]
    print(f"🌐 網路用語標題: {len(slang_titles)} 個")
    print("   範例:", slang_titles[:5])
    print()
    
    # 7. 標題結構分析
    structure_patterns = {
        '問句': [],
        '感嘆句': [],
        '陳述句': [],
        '指令句': []
    }
    
    for title in titles:
        if title.endswith('?') or title.endswith('？'):
            structure_patterns['問句'].append(title)
        elif title.endswith('!') or title.endswith('！'):
            structure_patterns['感嘆句'].append(title)
        elif any(word in title for word in ['請', '注意', '提醒', '建議']):
            structure_patterns['指令句'].append(title)
        else:
            structure_patterns['陳述句'].append(title)
    
    print("📝 標題結構分析:")
    for structure, titles_list in structure_patterns.items():
        print(f"   {structure}: {len(titles_list)} 個 ({len(titles_list)/len(titles)*100:.1f}%)")
        print(f"      範例: {titles_list[:2]}")
        print()
    
    # 8. 最常見詞彙
    all_words = []
    for title in titles:
        words = re.findall(r'[\u4e00-\u9fff]+', title)  # 中文字
        all_words.extend(words)
    
    word_counts = Counter(all_words)
    print("📊 最常見詞彙 (前20):")
    for word, count in word_counts.most_common(20):
        print(f"   {word}: {count} 次")
    print()
    
    # 9. 總結建議
    print("💡 對 AI 標題生成的建議:")
    print("   1. 真實 UGC 標題長度多樣化，從簡短到詳細都有")
    print("   2. 大量使用表情符號增加情感表達")
    print("   3. 網路用語和口語化表達很常見")
    print("   4. 問句和感嘆句結構增加互動性")
    print("   5. 股票代號、數字、百分比等具體資訊很重要")
    print("   6. 情感詞彙豐富，正面、負面、中性都有")
    print("   7. 特殊符號如【】、《》、() 用於分類和強調")
    print("   8. 個人化表達如'我的'、'分享'增加親近感")

if __name__ == "__main__":
    analyze_title_patterns()
