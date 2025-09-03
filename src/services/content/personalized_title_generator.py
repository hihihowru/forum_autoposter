#!/usr/bin/env python3
"""
個人化標題生成器
提供更強烈的個人風格差異
"""

import random
from typing import Dict, List, Any

class PersonalizedTitleGenerator:
    """個人化標題生成器"""
    
    def __init__(self):
        # 不同persona的標題風格模板
        self.title_templates = {
            "技術派": {
                "開場詞": [
                    "技術面看", "K線密碼", "圖表說話", "指標顯示", "技術分析",
                    "均線突破", "MACD轉向", "KD交叉", "布林通道", "RSI背離"
                ],
                "情緒詞": [
                    "爆量突破", "背離確認", "黃金交叉", "死亡交叉", "支撐測試",
                    "壓力突破", "動能轉強", "動能轉弱", "趨勢確立", "趨勢反轉"
                ],
                "結尾詞": [
                    "來了", "確認", "到位", "突破", "回調", "整理", "震盪", "盤整"
                ],
                "標點符號": ["！", "...", "？", "～", "→"]
            },
            "新聞派": {
                "開場詞": [
                    "突發", "重磅", "最新", "獨家", "內幕", "爆料", "震撼",
                    "驚人", "意外", "驚爆", "震撼", "重磅", "獨家"
                ],
                "情緒詞": [
                    "大漲", "暴跌", "狂飆", "崩盤", "暴漲", "跳水", "飆升",
                    "重挫", "狂跌", "暴漲", "暴跌", "飆升", "重挫"
                ],
                "結尾詞": [
                    "真相", "內幕", "原因", "影響", "後果", "機會", "風險",
                    "轉機", "危機", "機遇", "挑戰", "變數"
                ],
                "標點符號": ["！", "？", "！？", "？！", "→", "..." ]
            },
            "總經派": {
                "開場詞": [
                    "總經面", "基本面", "宏觀", "政策面", "經濟面", "產業面",
                    "景氣面", "資金面", "利率面", "通膨面", "就業面"
                ],
                "情緒詞": [
                    "支撐", "壓力", "轉機", "危機", "機會", "風險", "變數",
                    "利多", "利空", "中性", "樂觀", "謹慎", "觀望"
                ],
                "結尾詞": [
                    "支撐", "壓力", "轉機", "危機", "機會", "風險", "變數",
                    "利多", "利空", "中性", "樂觀", "謹慎", "觀望"
                ],
                "標點符號": ["：", "→", "...", "？", "！"]
            },
            "情緒派": {
                "開場詞": [
                    "哇", "天啊", "太誇張", "不敢相信", "震驚", "驚呆",
                    "嚇死", "太瘋狂", "太刺激", "太震撼", "太意外"
                ],
                "情緒詞": [
                    "瘋狂", "刺激", "震撼", "意外", "驚喜", "驚嚇", "興奮",
                    "緊張", "焦慮", "興奮", "激動", "冷靜", "淡定"
                ],
                "結尾詞": [
                    "了", "啦", "嗎", "呢", "吧", "啊", "喔", "耶", "嗚"
                ],
                "標點符號": ["！", "？", "！？", "？！", "～", "..." ]
            }
        }
        
        # 股票名稱替換詞
        self.stock_replacements = {
            "台積電": ["台積", "TSMC", "護國神山", "半導體龍頭"],
            "鴻海": ["鴻海", "富士康", "代工龍頭", "電子代工"],
            "聯發科": ["聯發科", "MTK", "IC設計", "手機晶片"],
            "台達電": ["台達電", "電源管理", "節能龍頭"],
            "中華電": ["中華電", "電信龍頭", "穩健標的"],
            "國泰金": ["國泰金", "金融龍頭", "金控一哥"],
            "富邦金": ["富邦金", "金控二哥", "金融巨頭"],
            "長榮": ["長榮", "航運龍頭", "貨櫃航運"],
            "陽明": ["陽明", "航運二哥", "貨櫃航運"],
            "漢翔": ["漢翔", "航太龍頭", "國防工業"],
            "雷虎": ["雷虎", "無人機", "航太概念"],
            "南亞": ["南亞", "塑膠龍頭", "石化產業"],
            "所羅門": ["所羅門", "AI概念", "機器視覺"],
            "台股指數": ["大盤", "台股", "指數", "加權指數", "TWA00"]
        }
        
        # 話題關鍵詞替換
        self.topic_replacements = {
            "高檔震盪": ["高檔整理", "高點震盪", "高點盤整", "高檔盤整"],
            "開高走平": ["開高走低", "開高走弱", "開高走軟", "開高走跌"],
            "內外資分歧": ["內外資對立", "內外資不同調", "內外資分歧", "內外資對峙"],
            "技術面分析": ["技術分析", "技術面", "技術指標", "技術走勢"],
            "大盤走勢": ["大盤動向", "大盤方向", "大盤趨勢", "大盤走勢"]
        }
    
    def generate_personalized_title(self, 
                                   topic_title: str, 
                                   persona: str, 
                                   stock_names: List[str] = None) -> str:
        """生成個人化標題"""
        
        # 根據persona選擇標題模板
        templates = self.title_templates.get(persona, self.title_templates["技術派"])
        
        # 隨機選擇標題結構
        title_structure = random.choice([
            "開場詞 + 情緒詞 + 結尾詞",
            "開場詞 + 股票名 + 情緒詞",
            "情緒詞 + 股票名 + 結尾詞",
            "開場詞 + 話題關鍵詞 + 結尾詞",
            "股票名 + 情緒詞 + 結尾詞"
        ])
        
        # 處理話題標題
        processed_topic = self._process_topic_title(topic_title)
        
        # 處理股票名稱
        if stock_names:
            stock_name = random.choice(stock_names)
            processed_stock = self._process_stock_name(stock_name)
        else:
            processed_stock = "台股"
        
        # 根據結構生成標題
        if title_structure == "開場詞 + 情緒詞 + 結尾詞":
            title = f"{random.choice(templates['開場詞'])}{random.choice(templates['情緒詞'])}{random.choice(templates['結尾詞'])}"
        elif title_structure == "開場詞 + 股票名 + 情緒詞":
            title = f"{random.choice(templates['開場詞'])}{processed_stock}{random.choice(templates['情緒詞'])}"
        elif title_structure == "情緒詞 + 股票名 + 結尾詞":
            title = f"{random.choice(templates['情緒詞'])}{processed_stock}{random.choice(templates['結尾詞'])}"
        elif title_structure == "開場詞 + 話題關鍵詞 + 結尾詞":
            title = f"{random.choice(templates['開場詞'])}{processed_topic}{random.choice(templates['結尾詞'])}"
        elif title_structure == "股票名 + 情緒詞 + 結尾詞":
            title = f"{processed_stock}{random.choice(templates['情緒詞'])}{random.choice(templates['結尾詞'])}"
        
        # 添加標點符號
        title += random.choice(templates['標點符號'])
        
        # 確保標題不重複
        title = self._ensure_title_uniqueness(title, persona)
        
        return title
    
    def _process_topic_title(self, topic_title: str) -> str:
        """處理話題標題，替換關鍵詞"""
        
        processed = topic_title
        
        for original, replacements in self.topic_replacements.items():
            if original in processed:
                processed = processed.replace(original, random.choice(replacements))
        
        return processed
    
    def _process_stock_name(self, stock_name: str) -> str:
        """處理股票名稱，使用替換詞"""
        
        for original, replacements in self.stock_replacements.items():
            if stock_name == original:
                return random.choice(replacements)
        
        return stock_name
    
    def _ensure_title_uniqueness(self, title: str, persona: str) -> str:
        """確保標題獨特性"""
        
        # 添加隨機元素
        uniqueness_modifiers = [
            "最新", "獨家", "重磅", "突發", "震撼", "驚人",
            "2024", "今天", "本週", "本月", "最新", "獨家"
        ]
        
        # 30%機率添加獨特性修飾詞
        if random.random() < 0.3:
            modifier = random.choice(uniqueness_modifiers)
            title = f"{modifier}！{title}"
        
        return title

# 創建全局實例
personalized_title_generator = PersonalizedTitleGenerator()


