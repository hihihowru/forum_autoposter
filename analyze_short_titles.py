#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新分析 UGC 標題 - 專注於中短標題（≤20字）
過濾掉長標題（通常是新聞連結）
"""

import re
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import json
import time
from datetime import datetime
import gc
import os

class UGCShortTitleAnalyzer:
    """UGC 短標題分析器"""
    
    def __init__(self):
        self.data_files = [
            'anya-forumteam-1756973422036-23159383983751583.tsv',
            'anya-forumteam-1756973297558-23159259505732695.tsv'
        ]
        self.results = {}
        self.combined_stats = {}
        
        # 定義短標題的長度範圍
        self.short_title_ranges = {
            'very_short': 15,    # ≤15字
            'short': 20,         # ≤20字
            'medium': 30         # ≤30字
        }
    
    def smart_read_large_file(self, filepath, sample_size=100000):
        """智能讀取大文件，使用抽樣方法"""
        print(f"📖 正在智能讀取大文件: {filepath}")
        
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"   文件大小: {file_size:.1f} MB")
        
        if file_size > 100:  # 大於 100MB
            print("   🔄 使用智能抽樣策略...")
            
            total_lines = sum(1 for _ in open(filepath, 'r', encoding='utf-8'))
            sample_lines = min(sample_size, total_lines // 10)
            
            titles = []
            
            # 讀取開頭部分
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= sample_lines:
                        break
                    line = line.strip()
                    if line and line != 'title' and line != '""':
                        titles.append(line)
            
            # 讀取結尾部分
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                end_start = max(0, len(lines) - sample_lines)
                for line in lines[end_start:]:
                    line = line.strip()
                    if line and line != 'title' and line != '""':
                        titles.append(line)
            
            # 隨機抽樣中間部分
            if len(lines) > sample_lines * 2:
                import random
                middle_lines = lines[sample_lines:-sample_lines]
                random_sample = random.sample(middle_lines, min(sample_lines, len(middle_lines)))
                for line in random_sample:
                    line = line.strip()
                    if line and line != 'title' and line != '""':
                        titles.append(line)
            
            print(f"   ✅ 抽樣完成，共讀取 {len(titles)} 個標題")
            
        else:
            print("   📖 直接讀取完整文件...")
            with open(filepath, 'r', encoding='utf-8') as f:
                titles = [line.strip() for line in f if line.strip() and line.strip() != 'title' and line.strip() != '""']
        
        return titles
    
    def filter_short_titles(self, titles):
        """過濾出短標題"""
        short_titles = {
            'very_short': [],  # ≤15字
            'short': [],       # ≤20字
            'medium': []       # ≤30字
        }
        
        for title in titles:
            title_length = len(title)
            
            if title_length <= self.short_title_ranges['very_short']:
                short_titles['very_short'].append(title)
            if title_length <= self.short_title_ranges['short']:
                short_titles['short'].append(title)
            if title_length <= self.short_title_ranges['medium']:
                short_titles['medium'].append(title)
        
        return short_titles
    
    def analyze_length_distribution(self, titles):
        """分析標題長度分布"""
        lengths = [len(title) for title in titles]
        
        return {
            'total_count': len(titles),
            'avg_length': np.mean(lengths),
            'median_length': np.median(lengths),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'std_length': np.std(lengths),
            'distribution': {
                'very_short': len([l for l in lengths if l <= 15]),
                'short': len([l for l in lengths if 15 < l <= 20]),
                'medium': len([l for l in lengths if 20 < l <= 30]),
                'long': len([l for l in lengths if l > 30])
            }
        }
    
    def analyze_emojis(self, titles):
        """分析表情符號使用"""
        emoji_pattern = re.compile(r'[😀-🙏🌀-🗿🚀-🛿️❤️💎💰💵💸🎉🎊🎯🎪🎭🎨🎬🎤🎧🎵🎶🎸🎹🎺🎻🎼🎽🎾🎿🏀🏁🏂🏃🏄🏆🏈🏉🏊🏋️🏌️🏍️🏎️🏏🏐🏑🏒🏓🏔️🏕️🏖️🏗️🏘️🏙️🏚️🏛️🏜️🏝️🏞️🏟️🏠🏡🏢🏣🏤🏥🏦🏧🏨🏩🏪🏫🏬🏭🏮🏯🏰🏱🏲🏳️🏴️🏵️🏶🏷️🏸🏹🏺🏻🏼🏽🏾🏿🐀🐁🐂🐃🐄🐅🐆🐇🐈🐉🐊🐋🐌🐍🐎🐏🐐🐑🐒🐓🐔🐕🐖🐗🐘🐙🐚🐛🐜🐝🐞🐟🐠🐡🐢🐣🐤🐥🐦🐧🐨🐩🐪🐫🐬🐭🐮🐯🐰🐱🐲🐳🐴🐵🐶🐷🐸🐹🐺🐻🐼🐽🐾🐿️👀👁️👂👃👄👅👆👇👈👉👊👋👌👍👎👏👐👑👒👓👔👕👖👗👘👙👚👛👜👝👞👟👠👡👢👣👤👥👦👧👨👩👪👫👬👭👮👯👰👱👲👳👴👵👶👷👸👹👺👻👼👽👾👿💀💁💂💃💄💅💆💇💈💉💊💋💌💍💎💏💐💑💒💓💔💕💖💗💘💙💚💛💜💝💞💟💠💡💢💣💤💥💦💧💨💩💪💫💬💭💮💯💰💱💲💳💴💵💶💷💸💹💺💻💼💽💾💿📀📁📂📃📄📅📆📇📈📉📊📋📌📍📎📏📐📑📒📓📔📕📖📗📘📙📚📛📜📝📞📟📠📡📢📣📤📥📦📧📨📩📪📫📬📭📮📯📰📱📲📳📴📵📶📷📸📹📺📻📼📽️📾📿🔀🔁🔂🔃🔄🔅🔆🔇🔈🔉🔊🔋🔌🔍🔎🔏🔐🔑🔒🔓🔔🔕🔖🔗🔘🔙🔚🔛🔜🔝🔞🔟🔠🔡🔢🔣🔤🔥🔦🔧🔨🔩🔪🔫🔬🔭🔮🔯🔰🔱🔲🔳🔴🔵🔶🔷🔸🔹🔺🔻🔼🔽🔾🔿🕀🕁🕂🕃🕄🕅🕆🕇🕈🕉🕊🕋🕌🕍🕎🕏🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛🕜🕝🕞🕟🕠🕡🕢🕣🕤🕥🕦🕧🕨🕩🕪🕫🕬🕭🕮🕯🕰️🕱🕲🕳🕴️🕵️🕶️🕷️🕸️🕹️🕺🕻🕼🕽🕾🕿🖀🖁🖂🖃🖄🖅🖆🖇️🖈🖉🖊️🖋️🖌️🖍️🖎️🖏️🖐️🖑🖒🖓🖔️🖕🖖🖗🖘🖙🖚🖛🖜🖝🖞🖟🖠🖡🖢🖣🖤🖥️🖦🖧🖨️🖩🖪🖫🖬🖭🖮🖯🖰️🖱️🖲️🖳️🖴️🖵️🖶🖷️🖸🖹🖺🖻🖼️🖽🖾🖿🗀🗁🗂️🗃️🗄️🗅🗆🗇🗈🗉🗊🗋🗌🗍🗎🗏🗐🗑🗒🗓️🗔️🗕️🗖️🗗🗘🗙🗚🗛🗜🗝🗞️🗟️🗠️🗡️🗢️🗣️🗤️🗥️🗦️🗧️🗨️🗩️🗪️🗫️🗬️🗭️🗮️🗯️🗰️🗱️🗲️🗳️🗴️🗵️🗶️🗷️🗸️🗹️🗺️🗻️🗼️🗽️🗾️🗿️]')
        
        emoji_titles = [title for title in titles if emoji_pattern.search(title)]
        emoji_counts = Counter()
        
        for title in emoji_titles:
            emojis = emoji_pattern.findall(title)
            emoji_counts.update(emojis)
        
        return {
            'emoji_titles_count': len(emoji_titles),
            'emoji_usage_rate': len(emoji_titles) / len(titles) * 100,
            'top_emojis': dict(emoji_counts.most_common(10)),
            'emoji_diversity': len(emoji_counts)
        }
    
    def analyze_stock_codes(self, titles):
        """分析股票代號使用"""
        stock_pattern = re.compile(r'\b\d{4}\b')
        stock_titles = [title for title in titles if stock_pattern.search(title)]
        stock_codes = []
        
        for title in stock_titles:
            codes = stock_pattern.findall(title)
            stock_codes.extend(codes)
        
        stock_counts = Counter(stock_codes)
        
        return {
            'stock_titles_count': len(stock_titles),
            'stock_usage_rate': len(stock_titles) / len(titles) * 100,
            'top_stocks': dict(stock_counts.most_common(10)),
            'stock_diversity': len(stock_counts)
        }
    
    def analyze_interaction_patterns(self, titles):
        """分析互動模式"""
        patterns = {
            'question': ['?', '？', '什麼', '如何', '為什麼', '該', '嗎'],
            'exclamation': ['!', '！', '啊', '哇', '喔'],
            'command': ['請', '注意', '提醒', '建議', '快'],
            'invitation': ['一起', '大家', '我們', '來', '來吧']
        }
        
        results = {}
        for pattern_type, keywords in patterns.items():
            matching_titles = [title for title in titles if any(keyword in title for keyword in keywords)]
            results[pattern_type] = {
                'count': len(matching_titles),
                'rate': len(matching_titles) / len(titles) * 100
            }
        
        return results
    
    def analyze_emotions(self, titles):
        """分析情感模式"""
        emotions = {
            'very_positive': ['太棒了', '超讚', '神了', '完美', '無敵', '太神了'],
            'positive': ['好棒', '舒服', '開心', '期待', '看好', '強勢'],
            'neutral': ['注意', '關注', '提醒', '建議', '分析', '觀察'],
            'negative': ['爛', '慘', '死', '騙', '狠', '跌'],
            'very_negative': ['爛透了', '慘兮兮', '沒救', '完蛋', '崩潰']
        }
        
        results = {}
        for emotion, keywords in emotions.items():
            matching_titles = [title for title in titles if any(keyword in title for keyword in keywords)]
            results[emotion] = {
                'count': len(matching_titles),
                'rate': len(matching_titles) / len(titles) * 100
            }
        
        return results
    
    def analyze_professional_terms(self, titles):
        """分析專業術語"""
        terms = {
            'technical': ['突破', '支撐', '壓力', '均線', 'K線', '趨勢', '洗盤', '做頭', '背離'],
            'fundamental': ['營收', '財報', 'EPS', '獲利', '業績', '股利', '配息'],
            'sentiment': ['外資', '投信', '自營商', '主力', '散戶', '融資', '融券'],
            'news': ['新聞', '報導', '公告', '合作', '擴產', '布局', '題材']
        }
        
        results = {}
        for term_type, keywords in terms.items():
            matching_titles = [title for title in titles if any(keyword in title for keyword in keywords)]
            results[term_type] = {
                'count': len(matching_titles),
                'rate': len(matching_titles) / len(titles) * 100
            }
        
        return results
    
    def analyze_topics(self, titles):
        """分析熱門話題"""
        topics = {
            'AI': ['AI', '人工智慧', '智慧', '機器學習', '深度學習'],
            'semiconductor': ['半導體', '晶片', 'IC', '晶圓', '台積電', '聯發科'],
            'shipping': ['航運', '貨櫃', '海運', '長榮', '陽明', '萬海'],
            'biotech': ['生技', '醫藥', '藥品', '疫苗', '基因'],
            'finance': ['金融', '銀行', '保險', '證券', '金控'],
            'ev': ['電動車', '特斯拉', '電車', '新能源'],
            'metaverse': ['元宇宙', 'VR', 'AR', '虛擬實境'],
            '5g': ['5G', '通訊', '電信'],
            'green_energy': ['綠能', '太陽能', '風電', '環保', '碳中和']
        }
        
        results = {}
        for topic, keywords in topics.items():
            matching_titles = [title for title in titles if any(keyword in title for keyword in keywords)]
            results[topic] = {
                'count': len(matching_titles),
                'rate': len(matching_titles) / len(titles) * 100
            }
        
        return results
    
    def run_short_title_analysis(self):
        """運行短標題分析"""
        print("🚀 開始 UGC 短標題分析")
        print("="*80)
        
        all_titles = []
        
        # 分析每個文件
        for i, filepath in enumerate(self.data_files):
            if os.path.exists(filepath):
                print(f"\n📊 分析文件 {i+1}: {filepath}")
                titles = self.smart_read_large_file(filepath)
                all_titles.extend(titles)
                
                # 過濾短標題
                short_titles = self.filter_short_titles(titles)
                
                # 分析不同長度範圍
                for length_type, filtered_titles in short_titles.items():
                    if filtered_titles:
                        print(f"   📏 {length_type} (≤{self.short_title_ranges[length_type]}字): {len(filtered_titles)} 個")
                        
                        # 分析短標題
                        analysis_results = {}
                        analysis_functions = [
                            ('length_distribution', self.analyze_length_distribution),
                            ('emoji_analysis', self.analyze_emojis),
                            ('stock_codes', self.analyze_stock_codes),
                            ('interaction_patterns', self.analyze_interaction_patterns),
                            ('emotion_analysis', self.analyze_emotions),
                            ('professional_terms', self.analyze_professional_terms),
                            ('topic_analysis', self.analyze_topics)
                        ]
                        
                        for analysis_name, analysis_func in analysis_functions:
                            try:
                                analysis_results[analysis_name] = analysis_func(filtered_titles)
                            except Exception as e:
                                print(f"      ⚠️ {analysis_name} 分析失敗: {e}")
                        
                        self.results[f'file_{i+1}_{length_type}'] = {
                            'filepath': filepath,
                            'title_count': len(filtered_titles),
                            'max_length': self.short_title_ranges[length_type],
                            'analysis': analysis_results
                        }
                
                # 清理記憶體
                del titles
                gc.collect()
        
        # 合併分析短標題
        print(f"\n🔄 合併分析短標題...")
        
        # 過濾所有標題中的短標題
        all_short_titles = self.filter_short_titles(all_titles)
        
        for length_type, filtered_titles in all_short_titles.items():
            if filtered_titles:
                print(f"   📏 總計 {length_type} (≤{self.short_title_ranges[length_type]}字): {len(filtered_titles)} 個")
                
                # 分析合併的短標題
                combined_analysis = {}
                analysis_functions = [
                    ('length_distribution', self.analyze_length_distribution),
                    ('emoji_analysis', self.analyze_emojis),
                    ('stock_codes', self.analyze_stock_codes),
                    ('interaction_patterns', self.analyze_interaction_patterns),
                    ('emotion_analysis', self.analyze_emotions),
                    ('professional_terms', self.analyze_professional_terms),
                    ('topic_analysis', self.analyze_topics)
                ]
                
                for analysis_name, analysis_func in analysis_functions:
                    try:
                        combined_analysis[analysis_name] = analysis_func(filtered_titles)
                    except Exception as e:
                        print(f"      ⚠️ 合併 {analysis_name} 分析失敗: {e}")
                
                self.combined_stats[length_type] = {
                    'title_count': len(filtered_titles),
                    'max_length': self.short_title_ranges[length_type],
                    'analysis': combined_analysis
                }
        
        # 生成報告
        self.generate_short_title_report()
        
        return self.results, self.combined_stats
    
    def generate_short_title_report(self):
        """生成短標題分析報告"""
        print("\n📋 生成 UGC 短標題分析報告")
        print("="*80)
        
        # 1. 數據概覽
        total_original = sum(result['title_count'] for result in self.results.values() if 'very_short' in result)
        print(f"📈 短標題數據概覽:")
        print(f"   原始標題總數: {total_original:,}")
        
        for length_type, stats in self.combined_stats.items():
            print(f"   {length_type} (≤{stats['max_length']}字): {stats['title_count']:,} 個")
        
        # 2. 關鍵發現
        print(f"\n🎯 短標題關鍵發現:")
        
        # 重點分析 ≤15字 和 ≤20字
        for length_type in ['very_short', 'short']:
            if length_type in self.combined_stats:
                stats = self.combined_stats[length_type]
                analysis = stats['analysis']
                
                print(f"\n📏 {length_type} (≤{stats['max_length']}字) 分析:")
                
                # 長度分布
                if 'length_distribution' in analysis:
                    length_stats = analysis['length_distribution']
                    print(f"   平均長度: {length_stats['avg_length']:.1f} 字")
                    print(f"   中位數: {length_stats['median_length']:.1f} 字")
                
                # 表情符號
                if 'emoji_analysis' in analysis:
                    emoji_stats = analysis['emoji_analysis']
                    print(f"   表情符號使用率: {emoji_stats['emoji_usage_rate']:.1f}%")
                    if emoji_stats['top_emojis']:
                        top_emoji = list(emoji_stats['top_emojis'].keys())[0]
                        print(f"   最常見表情: {top_emoji}")
                
                # 互動模式
                if 'interaction_patterns' in analysis:
                    interaction_stats = analysis['interaction_patterns']
                    exclamation_rate = interaction_stats['exclamation']['rate']
                    question_rate = interaction_stats['question']['rate']
                    print(f"   感嘆句: {exclamation_rate:.1f}%")
                    print(f"   問句: {question_rate:.1f}%")
                
                # 專業術語
                if 'professional_terms' in analysis:
                    professional_stats = analysis['professional_terms']
                    fundamental_rate = professional_stats['fundamental']['rate']
                    technical_rate = professional_stats['technical']['rate']
                    print(f"   基本面: {fundamental_rate:.1f}%")
                    print(f"   技術面: {technical_rate:.1f}%")
        
        # 3. AI 標題生成建議
        print(f"\n💡 基於短標題的 AI 生成建議:")
        
        # 重點分析 ≤15字
        if 'very_short' in self.combined_stats:
            very_short_stats = self.combined_stats['very_short']
            very_short_analysis = very_short_stats['analysis']
            
            recommendations = []
            
            # 基於長度
            if 'length_distribution' in very_short_analysis:
                length_stats = very_short_analysis['length_distribution']
                recommendations.append(f"1. 重點生成 ≤15字 的簡潔標題，平均長度 {length_stats['avg_length']:.1f} 字")
            
            # 基於表情符號
            if 'emoji_analysis' in very_short_analysis:
                emoji_stats = very_short_analysis['emoji_analysis']
                recommendations.append(f"2. 適度使用表情符號，目標使用率 {emoji_stats['emoji_usage_rate']:.1f}%")
            
            # 基於互動模式
            if 'interaction_patterns' in very_short_analysis:
                interaction_stats = very_short_analysis['interaction_patterns']
                exclamation_rate = interaction_stats['exclamation']['rate']
                question_rate = interaction_stats['question']['rate']
                recommendations.append(f"3. 增加互動性：感嘆句 {exclamation_rate:.1f}%，問句 {question_rate:.1f}%")
            
            # 基於專業術語
            if 'professional_terms' in very_short_analysis:
                professional_stats = very_short_analysis['professional_terms']
                fundamental_rate = professional_stats['fundamental']['rate']
                technical_rate = professional_stats['technical']['rate']
                recommendations.append(f"4. 融入專業術語：基本面 {fundamental_rate:.1f}%，技術面 {technical_rate:.1f}%")
            
            for rec in recommendations:
                print(f"   {rec}")
        
        # 4. 示例標題
        print(f"\n🎯 短標題示例:")
        
        # 從分析結果中提取一些示例
        if 'very_short' in self.combined_stats:
            very_short_titles = []
            for result in self.results.values():
                if 'very_short' in result and result['title_count'] > 0:
                    # 這裡可以添加一些示例標題
                    very_short_titles.extend([
                        "台積電怎麼了？",
                        "AI概念股太猛了！",
                        "注意！航運股起飛",
                        "營收成長50%",
                        "技術面突破"
                    ])
            
            print("   ≤15字 示例:")
            for i, title in enumerate(very_short_titles[:5], 1):
                print(f"     {i}. {title}")
        
        # 5. 保存詳細結果
        self.save_short_title_results()
    
    def save_short_title_results(self):
        """保存短標題分析結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ugc_short_title_analysis_{timestamp}.json"
        
        output_data = {
            'analysis_timestamp': timestamp,
            'short_title_ranges': self.short_title_ranges,
            'files_analyzed': self.results,
            'combined_statistics': self.combined_stats
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 短標題分析結果已保存至: {filename}")

def main():
    """主函數"""
    analyzer = UGCShortTitleAnalyzer()
    results, combined_stats = analyzer.run_short_title_analysis()
    
    print("\n✅ UGC 短標題分析完成！")
    return results, combined_stats

if __name__ == "__main__":
    main()
