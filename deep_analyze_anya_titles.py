#!/usr/bin/env python3
"""
深入分析 anya TSV 文件 - 更全面的 UGC 標題分析
"""

import re
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def deep_analyze_titles():
    """深入分析標題模式"""
    
    # 讀取 TSV 文件
    print("📖 正在讀取數據...")
    df = pd.read_csv('anya-forumteam-1756973422036-23159383983751583.tsv', sep='\t')
    
    # 清理數據
    titles = df['title'].dropna().tolist()
    titles = [title for title in titles if title and title != 'title' and title != '""']
    
    print(f"📊 總共分析 {len(titles)} 個標題")
    print("="*80)
    
    # 1. 標題長度深度分析
    title_lengths = [len(title) for title in titles]
    print("📏 標題長度深度分析:")
    print(f"   平均長度: {sum(title_lengths)/len(title_lengths):.1f} 字")
    print(f"   中位數: {sorted(title_lengths)[len(title_lengths)//2]} 字")
    print(f"   最短: {min(title_lengths)} 字")
    print(f"   最長: {max(title_lengths)} 字")
    
    # 長度分布
    short_titles = [t for t in titles if len(t) <= 10]
    medium_titles = [t for t in titles if 10 < len(t) <= 20]
    long_titles = [t for t in titles if len(t) > 20]
    
    print(f"   短標題 (≤10字): {len(short_titles)} 個 ({len(short_titles)/len(titles)*100:.1f}%)")
    print(f"   中標題 (11-20字): {len(medium_titles)} 個 ({len(medium_titles)/len(titles)*100:.1f}%)")
    print(f"   長標題 (>20字): {len(long_titles)} 個 ({len(long_titles)/len(titles)*100:.1f}%)")
    print()
    
    # 2. 表情符號詳細分析
    emoji_pattern = re.compile(r'[😀-🙏🌀-🗿🚀-🛿️❤️💎💰💵💸🎉🎊🎯🎪🎭🎨🎬🎤🎧🎵🎶🎸🎹🎺🎻🎼🎽🎾🎿🏀🏁🏂🏃🏄🏆🏈🏉🏊🏋️🏌️🏍️🏎️🏏🏐🏑🏒🏓🏔️🏕️🏖️🏗️🏘️🏙️🏚️🏛️🏜️🏝️🏞️🏟️🏠🏡🏢🏣🏤🏥🏦🏧🏨🏩🏪🏫🏬🏭🏮🏯🏰🏱🏲🏳️🏴️🏵️🏶🏷️🏸🏹🏺🏻🏼🏽🏾🏿🐀🐁🐂🐃🐄🐅🐆🐇🐈🐉🐊🐋🐌🐍🐎🐏🐐🐑🐒🐓🐔🐕🐖🐗🐘🐙🐚🐛🐜🐝🐞🐟🐠🐡🐢🐣🐤🐥🐦🐧🐨🐩🐪🐫🐬🐭🐮🐯🐰🐱🐲🐳🐴🐵🐶🐷🐸🐹🐺🐻🐼🐽🐾🐿️👀👁️👂👃👄👅👆👇👈👉👊👋👌👍👎👏👐👑👒👓👔👕👖👗👘👙👚👛👜👝👞👟👠👡👢👣👤👥👦👧👨👩👪👫👬👭👮👯👰👱👲👳👴👵👶👷👸👹👺👻👼👽👾👿💀💁💂💃💄💅💆💇💈💉💊💋💌💍💎💏💐💑💒💓💔💕💖💗💘💙💚💛💜💝💞💟💠💡💢💣💤💥💦💧💨💩💪💫💬💭💮💯💰💱💲💳💴💵💶💷💸💹💺💻💼💽💾💿📀📁📂📃📄📅📆📇📈📉📊📋📌📍📎📏📐📑📒📓📔📕📖📗📘📙📚📛📜📝📞📟📠📡📢📣📤📥📦📧📨📩📪📫📬📭📮📯📰📱📲📳📴📵📶📷📸📹📺📻📼📽️📾📿🔀🔁🔂🔃🔄🔅🔆🔇🔈🔉🔊🔋🔌🔍🔎🔏🔐🔑🔒🔓🔔🔕🔖🔗🔘🔙🔚🔛🔜🔝🔞🔟🔠🔡🔢🔣🔤🔥🔦🔧🔨🔩🔪🔫🔬🔭🔮🔯🔰🔱🔲🔳🔴🔵🔶🔷🔸🔹🔺🔻🔼🔽🔾🔿🕀🕁🕂🕃🕄🕅🕆🕇🕈🕉🕊🕋🕌🕍🕎🕏🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛🕜🕝🕞🕟🕠🕡🕢🕣🕤🕥🕦🕧🕨🕩🕪🕫🕬🕭🕮🕯🕰️🕱🕲🕳🕴️🕵️🕶️🕷️🕸️🕹️🕺🕻🕼🕽🕾🕿🖀🖁🖂🖃🖄🖅🖆🖇️🖈🖉🖊️🖋️🖌️🖍️🖎️🖏️🖐️🖑🖒🖓🖔️🖕🖖🖗🖘🖙🖚🖛🖜🖝🖞🖟🖠🖡🖢🖣🖤🖥️🖦🖧🖨️🖩🖪🖫🖬🖭🖮🖯🖰️🖱️🖲️🖳️🖴️🖵️🖶🖷️🖸🖹🖺🖻🖼️🖽🖾🖿🗀🗁🗂️🗃️🗄️🗅🗆🗇🗈🗉🗊🗋🗌🗍🗎🗏🗐🗑🗒🗓️🗔️🗕️🗖️🗗🗘🗙🗚🗛🗜🗝🗞️🗟️🗠️🗡️🗢️🗣️🗤️🗥️🗦️🗧️🗨️🗩️🗪️🗫️🗬️🗭️🗮️🗯️🗰️🗱️🗲️🗳️🗴️🗵️🗶️🗷️🗸️🗹️🗺️🗻️🗼️🗽️🗾️🗿️]')
    
    emoji_titles = [title for title in titles if emoji_pattern.search(title)]
    emoji_counts = Counter()
    for title in emoji_titles:
        emojis = emoji_pattern.findall(title)
        emoji_counts.update(emojis)
    
    print("😊 表情符號詳細分析:")
    print(f"   使用表情符號的標題: {len(emoji_titles)} 個 ({len(emoji_titles)/len(titles)*100:.1f}%)")
    print("   最常見表情符號:")
    for emoji, count in emoji_counts.most_common(10):
        print(f"     {emoji}: {count} 次")
    print()
    
    # 3. 股票代號分析
    stock_code_pattern = re.compile(r'\b\d{4}\b')
    stock_titles = [title for title in titles if stock_code_pattern.search(title)]
    stock_codes = []
    for title in stock_titles:
        codes = stock_code_pattern.findall(title)
        stock_codes.extend(codes)
    
    stock_code_counts = Counter(stock_codes)
    print("📈 股票代號分析:")
    print(f"   包含股票代號的標題: {len(stock_titles)} 個 ({len(stock_titles)/len(titles)*100:.1f}%)")
    print("   最常提到的股票代號:")
    for code, count in stock_code_counts.most_common(10):
        print(f"     {code}: {count} 次")
    print()
    
    # 4. 時間相關分析
    time_patterns = {
        '日期': re.compile(r'\d{1,2}/\d{1,2}'),
        '月份': re.compile(r'\d{1,2}月'),
        '年份': re.compile(r'20\d{2}'),
        '時間': re.compile(r'\d{1,2}:\d{2}')
    }
    
    time_titles = defaultdict(list)
    for title in titles:
        for time_type, pattern in time_patterns.items():
            if pattern.search(title):
                time_titles[time_type].append(title)
    
    print("⏰ 時間相關分析:")
    for time_type, titles_list in time_titles.items():
        print(f"   {time_type}: {len(titles_list)} 個 ({len(titles_list)/len(titles)*100:.1f}%)")
    print()
    
    # 5. 數字分析
    number_patterns = {
        '百分比': re.compile(r'\d+%'),
        '價格': re.compile(r'\d+\.?\d*元'),
        '張數': re.compile(r'\d+張'),
        '萬': re.compile(r'\d+萬'),
        '億': re.compile(r'\d+億'),
        '點數': re.compile(r'\d+點')
    }
    
    number_titles = defaultdict(list)
    for title in titles:
        for number_type, pattern in number_patterns.items():
            if pattern.search(title):
                number_titles[number_type].append(title)
    
    print("🔢 數字類型分析:")
    for number_type, titles_list in number_titles.items():
        print(f"   {number_type}: {len(titles_list)} 個 ({len(titles_list)/len(titles)*100:.1f}%)")
    print()
    
    # 6. 熱門話題分析
    hot_topics = {
        'AI': ['AI', '人工智慧', '智慧'],
        '半導體': ['半導體', '晶片', 'IC', '晶圓'],
        '航運': ['航運', '貨櫃', '海運'],
        '生技': ['生技', '醫藥', '藥品'],
        '金融': ['金融', '銀行', '保險'],
        '電動車': ['電動車', '特斯拉', '電車'],
        '元宇宙': ['元宇宙', 'VR', 'AR'],
        '5G': ['5G', '通訊'],
        '綠能': ['綠能', '太陽能', '風電', '環保']
    }
    
    topic_counts = defaultdict(int)
    for title in titles:
        for topic, keywords in hot_topics.items():
            if any(keyword in title for keyword in keywords):
                topic_counts[topic] += 1
    
    print("🔥 熱門話題分析:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {topic}: {count} 個 ({count/len(titles)*100:.1f}%)")
    print()
    
    # 7. 情感強度分析
    emotion_intensity = {
        '極度正面': ['太棒了', '超讚', '神了', '完美', '無敵'],
        '正面': ['好棒', '舒服', '開心', '期待', '看好'],
        '中性': ['注意', '關注', '提醒', '建議', '分析'],
        '負面': ['爛', '慘', '死', '騙', '狠'],
        '極度負面': ['爛透了', '慘兮兮', '沒救', '完蛋', '崩潰']
    }
    
    intensity_counts = defaultdict(int)
    for title in titles:
        for intensity, words in emotion_intensity.items():
            if any(word in title for word in words):
                intensity_counts[intensity] += 1
    
    print("😊 情感強度分析:")
    for intensity, count in intensity_counts.items():
        print(f"   {intensity}: {count} 個 ({count/len(titles)*100:.1f}%)")
    print()
    
    # 8. 互動性分析
    interaction_patterns = {
        '問句': ['?', '？', '什麼', '如何', '為什麼', '該', '嗎'],
        '感嘆': ['!', '！', '啊', '哇', '喔'],
        '指令': ['請', '注意', '提醒', '建議', '快'],
        '邀請': ['一起', '大家', '我們', '來', '來吧']
    }
    
    interaction_counts = defaultdict(int)
    for title in titles:
        for pattern_type, keywords in interaction_patterns.items():
            if any(keyword in title for keyword in keywords):
                interaction_counts[pattern_type] += 1
    
    print("💬 互動性分析:")
    for pattern_type, count in interaction_counts.items():
        print(f"   {pattern_type}: {count} 個 ({count/len(titles)*100:.1f}%)")
    print()
    
    # 9. 專業度分析
    professional_terms = {
        '技術分析': ['突破', '支撐', '壓力', '均線', 'K線', '趨勢', '洗盤', '做頭', '背離'],
        '基本面': ['營收', '財報', 'EPS', '獲利', '業績', '股利', '配息'],
        '籌碼面': ['外資', '投信', '自營商', '主力', '散戶', '融資', '融券'],
        '消息面': ['新聞', '報導', '公告', '合作', '擴產', '布局', '題材']
    }
    
    professional_counts = defaultdict(int)
    for title in titles:
        for term_type, keywords in professional_terms.items():
            if any(keyword in title for keyword in keywords):
                professional_counts[term_type] += 1
    
    print("📊 專業度分析:")
    for term_type, count in professional_counts.items():
        print(f"   {term_type}: {count} 個 ({count/len(titles)*100:.1f}%)")
    print()
    
    # 10. 總結建議
    print("💡 對 AI 標題生成的深度建議:")
    print("   1. 標題長度應該多樣化，重點關注 11-20 字的中等長度")
    print("   2. 適度使用表情符號，特別是 😱👏😌❤️ 等常見表情")
    print("   3. 大量使用股票代號，增加具體性和可信度")
    print("   4. 融入時間元素，增加時效性")
    print("   5. 使用具體數字，如價格、百分比、張數等")
    print("   6. 關注熱門話題，特別是 AI、半導體、航運等")
    print("   7. 平衡情感強度，避免過度極端")
    print("   8. 增加互動性，使用問句、感嘆句、指令句")
    print("   9. 融入專業術語，提升可信度")
    print("   10. 使用網路用語，增加親近感")
    
    # 11. 生成示例標題
    print("\n🎯 基於分析的標題示例:")
    print("   問句類: '台積電(2330)今天怎麼了？'")
    print("   感嘆類: 'AI概念股太猛了！😱'")
    print("   指令類: '注意！航運股要起飛了'")
    print("   數據類: '營收成長50%，股價飆升！'")
    print("   專業類: '技術面突破，籌碼面轉好'")
    print("   互動類: '大家一起來討論吧！'")

if __name__ == "__main__":
    deep_analyze_titles()
