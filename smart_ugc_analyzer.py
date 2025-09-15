#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能分析大型 UGC 數據集 - 多文件融合分析
支持大數據處理和 KOL 擴展
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

class SmartUGCAnalyzer:
    """智能 UGC 分析器"""
    
    def __init__(self):
        self.data_files = [
            'anya-forumteam-1756973422036-23159383983751583.tsv',  # 第一個文件
            'anya-forumteam-1756973297558-23159259505732695.tsv'   # 新的大文件
        ]
        self.results = {}
        self.combined_stats = {}
        
        # 預定義的分析模式
        self.analysis_patterns = {
            'length_distribution': self.analyze_length_distribution,
            'emoji_analysis': self.analyze_emojis,
            'stock_codes': self.analyze_stock_codes,
            'time_patterns': self.analyze_time_patterns,
            'number_patterns': self.analyze_number_patterns,
            'topic_analysis': self.analyze_topics,
            'emotion_analysis': self.analyze_emotions,
            'interaction_patterns': self.analyze_interaction_patterns,
            'professional_terms': self.analyze_professional_terms,
            'kol_patterns': self.analyze_kol_patterns,
            'content_clustering': self.analyze_content_clustering
        }
    
    def smart_read_large_file(self, filepath, sample_size=100000):
        """智能讀取大文件，使用抽樣方法"""
        print(f"📖 正在智能讀取大文件: {filepath}")
        
        # 獲取文件大小
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"   文件大小: {file_size:.1f} MB")
        
        # 根據文件大小決定抽樣策略
        if file_size > 100:  # 大於 100MB
            print("   🔄 使用智能抽樣策略...")
            
            # 讀取前 10% 和後 10% 的數據
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
            # 小文件直接讀取
            print("   📖 直接讀取完整文件...")
            with open(filepath, 'r', encoding='utf-8') as f:
                titles = [line.strip() for line in f if line.strip() and line.strip() != 'title' and line.strip() != '""']
        
        return titles
    
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
                'short': len([l for l in lengths if l <= 10]),
                'medium': len([l for l in lengths if 10 < l <= 20]),
                'long': len([l for l in lengths if l > 20])
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
    
    def analyze_time_patterns(self, titles):
        """分析時間模式"""
        time_patterns = {
            'date': re.compile(r'\d{1,2}/\d{1,2}'),
            'month': re.compile(r'\d{1,2}月'),
            'year': re.compile(r'20\d{2}'),
            'time': re.compile(r'\d{1,2}:\d{2}')
        }
        
        results = {}
        for pattern_name, pattern in time_patterns.items():
            matching_titles = [title for title in titles if pattern.search(title)]
            results[pattern_name] = {
                'count': len(matching_titles),
                'rate': len(matching_titles) / len(titles) * 100
            }
        
        return results
    
    def analyze_number_patterns(self, titles):
        """分析數字模式"""
        number_patterns = {
            'percentage': re.compile(r'\d+%'),
            'price': re.compile(r'\d+\.?\d*元'),
            'shares': re.compile(r'\d+張'),
            'ten_thousand': re.compile(r'\d+萬'),
            'hundred_million': re.compile(r'\d+億'),
            'points': re.compile(r'\d+點')
        }
        
        results = {}
        for pattern_name, pattern in number_patterns.items():
            matching_titles = [title for title in titles if pattern.search(title)]
            results[pattern_name] = {
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
    
    def analyze_kol_patterns(self, titles):
        """分析 KOL 模式（為未來擴展準備）"""
        # 這裡可以分析不同 KOL 的發文模式
        # 目前先分析一些通用的 KOL 特徵
        kol_patterns = {
            'personal_pronoun': ['我的', '自己', '我'],
            'experience_share': ['分享', '經驗', '心得', '操作'],
            'expert_opinion': ['分析', '看法', '觀點', '建議'],
            'community_interaction': ['大家', '一起', '我們', '來']
        }
        
        results = {}
        for pattern_type, keywords in kol_patterns.items():
            matching_titles = [title for title in titles if any(keyword in title for keyword in keywords)]
            results[pattern_type] = {
                'count': len(matching_titles),
                'rate': len(matching_titles) / len(titles) * 100
            }
        
        return results
    
    def analyze_content_clustering(self, titles):
        """內容聚類分析"""
        # 簡單的內容類型分類
        content_types = {
            'news_announcement': ['公告', '快訊', '新聞', '報導'],
            'analysis_report': ['分析', '報告', '研究', '觀察'],
            'trading_advice': ['建議', '操作', '買進', '賣出'],
            'market_sentiment': ['情緒', '氛圍', '熱度', '瘋狂'],
            'personal_share': ['分享', '心得', '經驗', '我的'],
            'question_discussion': ['?', '？', '什麼', '如何']
        }
        
        results = {}
        for content_type, keywords in content_types.items():
            matching_titles = [title for title in titles if any(keyword in title for keyword in keywords)]
            results[content_type] = {
                'count': len(matching_titles),
                'rate': len(matching_titles) / len(titles) * 100
            }
        
        return results
    
    def run_comprehensive_analysis(self):
        """運行全面分析"""
        print("🚀 開始智能 UGC 數據分析")
        print("="*80)
        
        all_titles = []
        
        # 分析每個文件
        for i, filepath in enumerate(self.data_files):
            if os.path.exists(filepath):
                print(f"\n📊 分析文件 {i+1}: {filepath}")
                titles = self.smart_read_large_file(filepath)
                all_titles.extend(titles)
                
                # 單文件分析
                file_results = {}
                for analysis_name, analysis_func in self.analysis_patterns.items():
                    try:
                        file_results[analysis_name] = analysis_func(titles)
                    except Exception as e:
                        print(f"   ⚠️ {analysis_name} 分析失敗: {e}")
                
                self.results[f'file_{i+1}'] = {
                    'filepath': filepath,
                    'title_count': len(titles),
                    'analysis': file_results
                }
                
                # 清理記憶體
                del titles
                gc.collect()
        
        # 合併分析
        print(f"\n🔄 合併分析 {len(all_titles)} 個標題...")
        self.combined_stats = {}
        
        for analysis_name, analysis_func in self.analysis_patterns.items():
            try:
                self.combined_stats[analysis_name] = analysis_func(all_titles)
            except Exception as e:
                print(f"   ⚠️ 合併 {analysis_name} 分析失敗: {e}")
        
        # 生成報告
        self.generate_report()
        
        return self.results, self.combined_stats
    
    def generate_report(self):
        """生成分析報告"""
        print("\n📋 生成智能分析報告")
        print("="*80)
        
        # 1. 數據概覽
        total_titles = sum(result['title_count'] for result in self.results.values())
        print(f"📊 數據概覽:")
        print(f"   總標題數: {total_titles:,}")
        print(f"   分析文件數: {len(self.results)}")
        
        # 2. 關鍵發現
        print(f"\n🎯 關鍵發現:")
        
        # 長度分布
        if 'length_distribution' in self.combined_stats:
            length_stats = self.combined_stats['length_distribution']
            print(f"   平均標題長度: {length_stats['avg_length']:.1f} 字")
            print(f"   短標題比例: {length_stats['distribution']['short']/length_stats['total_count']*100:.1f}%")
            print(f"   中標題比例: {length_stats['distribution']['medium']/length_stats['total_count']*100:.1f}%")
            print(f"   長標題比例: {length_stats['distribution']['long']/length_stats['total_count']*100:.1f}%")
        
        # 表情符號
        if 'emoji_analysis' in self.combined_stats:
            emoji_stats = self.combined_stats['emoji_analysis']
            print(f"   表情符號使用率: {emoji_stats['emoji_usage_rate']:.1f}%")
        
        # 股票代號
        if 'stock_codes' in self.combined_stats:
            stock_stats = self.combined_stats['stock_codes']
            print(f"   股票代號使用率: {stock_stats['stock_usage_rate']:.1f}%")
        
        # 3. AI 標題生成建議
        print(f"\n💡 AI 標題生成智能建議:")
        
        # 基於數據的建議
        recommendations = self.generate_ai_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # 4. KOL 擴展建議
        print(f"\n👥 KOL 擴展建議:")
        kol_recommendations = self.generate_kol_recommendations()
        for i, rec in enumerate(kol_recommendations, 1):
            print(f"   {i}. {rec}")
        
        # 5. 保存詳細結果
        self.save_detailed_results()
    
    def generate_ai_recommendations(self):
        """基於分析生成 AI 建議"""
        recommendations = []
        
        # 基於長度分布
        if 'length_distribution' in self.combined_stats:
            length_stats = self.combined_stats['length_distribution']
            medium_rate = length_stats['distribution']['medium'] / length_stats['total_count'] * 100
            recommendations.append(f"重點生成 {medium_rate:.1f}% 的 11-20 字中等長度標題")
        
        # 基於表情符號
        if 'emoji_analysis' in self.combined_stats:
            emoji_stats = self.combined_stats['emoji_analysis']
            recommendations.append(f"適度使用表情符號，目標使用率 {emoji_stats['emoji_usage_rate']:.1f}%")
        
        # 基於互動模式
        if 'interaction_patterns' in self.combined_stats:
            interaction_stats = self.combined_stats['interaction_patterns']
            exclamation_rate = interaction_stats['exclamation']['rate']
            question_rate = interaction_stats['question']['rate']
            recommendations.append(f"增加互動性：感嘆句 {exclamation_rate:.1f}%，問句 {question_rate:.1f}%")
        
        # 基於專業術語
        if 'professional_terms' in self.combined_stats:
            professional_stats = self.combined_stats['professional_terms']
            fundamental_rate = professional_stats['fundamental']['rate']
            technical_rate = professional_stats['technical']['rate']
            recommendations.append(f"融入專業術語：基本面 {fundamental_rate:.1f}%，技術面 {technical_rate:.1f}%")
        
        return recommendations
    
    def generate_kol_recommendations(self):
        """生成 KOL 擴展建議"""
        recommendations = [
            "基於情感強度分布設計不同 KOL 性格",
            "根據互動模式差異化 KOL 表達方式",
            "利用專業術語偏好區分 KOL 專業領域",
            "結合熱門話題設計 KOL 專長領域",
            "參考表情符號使用習慣設計 KOL 風格"
        ]
        
        return recommendations
    
    def save_detailed_results(self):
        """保存詳細分析結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ugc_analysis_results_{timestamp}.json"
        
        output_data = {
            'analysis_timestamp': timestamp,
            'files_analyzed': self.results,
            'combined_statistics': self.combined_stats
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 詳細結果已保存至: {filename}")

def main():
    """主函數"""
    analyzer = SmartUGCAnalyzer()
    results, combined_stats = analyzer.run_comprehensive_analysis()
    
    print("\n✅ 智能 UGC 分析完成！")
    return results, combined_stats

if __name__ == "__main__":
    main()
