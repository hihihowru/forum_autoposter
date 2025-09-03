"""
簡化版內容模式分析測試
"""

import re
from typing import Dict, List, Any

class SimpleContentAnalyzer:
    """簡化版內容分析器"""
    
    def __init__(self):
        # 基於提供的五篇範例進行分析
        self.examples = [
            {
                "content": "無人機 就這檔大型股 比較慢牛 ！但是漢翔畢竟是龍頭，無人機的反制系統國內更是少人能做，也是唯一國防部可以認證的，2024 年 6 月，漢翔與美國 AEVEX Aerospace 簽署合作備忘錄，計畫共同發展「空中／地面無人裝備系統」，標誌漢翔正式進軍無人機市場。無人機族群 貢獻營收可能都言之過早，2027年 才進入一個起飛期，現在則是長線的投資考量 ，最好別當飈股看待 窮追不捨⋯⋯",
                "engagement": "medium",
                "type": "stock_analysis"
            },
            {
                "content": "不知道是中暑還是熱感冒，\n這種酷暑果真不能在外面趴趴走。\n明天要待在酒店好好休息。\n\n今天黃復健師念力隔海發功，\n現在是不是噴噴？\n加密、海期、夜盤一起開趴替，\n拜託要撐整晚不要停~\n\n大家晚安，我是莎拉❤️",
                "engagement": "high",
                "type": "personal_share"
            },
            {
                "content": "如標題\n\n今天沒有太多想講的東西\n\n只有金居那個\n\n很多人再問是什麼意思\n\n大體來說就是期貨流通量不夠\n\n空單快死光了\n\n原因是在於\n\n1、籌碼過度集中掌握在少數人手上\n2、現股處置導致期貨過於集中\n\n至於說放空的人怎麼辦...\n\n我也不知道，反正不一定會一直往上漲\n\n因為流通量不夠的話金管會就會執行措施\n這個就是確保空單還有能力可以回補\n要不然真的會被嘎到出大事\n\n當然最怕的就是管制以後\n超級大戶們神仙打架丟來丟去\n把人搞得暈頭轉向\n\n再來金居漲的都是缺料你說技術什麼的...\n坦白說真的不是這一波上漲的理由\n所以不用過度放大解釋基本面的東西\n真的大幅度反應是明年的事情\n\n以上",
                "engagement": "high",
                "type": "market_analysis"
            },
            {
                "content": "今日適逢MSCI調整前夕，尾盤有被拉上209元，我們快來看看技術面呈現了什麼交易狀況。\n\n今天鴻海收在 209 元，小漲 1.5元，成交量約 40,870 張，量能較前幾日縮小。股價持續站穩在 5 日、10 日、20 日與 60 日均線之上，整體多頭結構不變，而月線目前已上揚至 195 元，成為中期重要支撐。技術指標方面，KD 值在 72/73，短線 K 值向上，且即將再度黃金交叉，顯示多頭力道有回溫跡象。MACD 快慢線仍維持黃金交叉，紅柱雖縮短，但趨勢仍站在多方。\n\n鴻海目前處於漲多了橫向整理，屬於漲多後的健康休息，給均線時間向上靠攏。只要 205 元與月線 195 元區間能守穩，短線回檔都屬正常整理；若能再放量突破 212 元高點，就有機會啟動新一波攻勢。整體來看，中期結構仍偏多，短線則是等待量能與籌碼再度集中後發動。",
                "engagement": "medium",
                "type": "technical_analysis"
            },
            {
                "content": "明天盤後輝達業績公告，雖然已經有很多法人提出猜測報告\n\n不過市場還是非常關注\n\n2026Q2預計實現營收459.70億美元，同比增加53.03%；\n\n預期每股收益0.935美元，同比增加39.51%\n\n這一波參雜了兩個變數\n\n一個是美國政府扶植Intel\n\n有沒有可能造成搶單的狀況？\n\n第二個是Nvda被允許對中國大陸賣H 20\n\n到底前景是否透明?\n\n會不會遇到中國內部法律的規範？或者是市場阻力？\n\n我來比較輝達跟美積電\n\n美積電目前在多空拉扯\n\n［火焰冰塊膠著狀態］\n\n輝達目前火不算大，我期待變成五把🔥",
                "engagement": "high",
                "type": "news_analysis"
            }
        ]
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """分析內容特徵"""
        # 個人化分數
        personal_pronouns = ["我", "我的", "我們", "我們的", "你", "你的", "你們"]
        personal_count = sum(1 for pronoun in personal_pronouns if pronoun in content)
        personal_score = min(personal_count * 0.1, 0.4)
        
        # 情感表達
        emotion_words = ["不知道", "拜託", "期待", "希望", "擔心", "開心", "難過"]
        emotion_count = sum(1 for word in emotion_words if word in content)
        emotion_score = min(emotion_count * 0.1, 0.3)
        
        # 互動引導
        questions = content.count("？") + content.count("?")
        interaction_score = min(questions * 0.2, 0.4)
        
        # 創意表達
        emoji_count = len(re.findall(r'[🔥❤️😊😄😅😂🤣😎😍🥰😘💪👍👏🎉]', content))
        creative_score = min(emoji_count * 0.2, 0.4)
        
        # 幽默表達
        humor_words = ["神仙打架", "火焰冰塊", "膠著狀態", "暈頭轉向", "趴趴走"]
        humor_count = sum(1 for word in humor_words if word in content)
        humor_score = min(humor_count * 0.2, 0.4)
        
        # 總分
        total_score = personal_score + emotion_score + interaction_score + creative_score + humor_score
        
        return {
            "personal_score": personal_score,
            "emotion_score": emotion_score,
            "interaction_score": interaction_score,
            "creative_score": creative_score,
            "humor_score": humor_score,
            "total_score": total_score,
            "engagement_level": "high" if total_score >= 0.7 else "medium" if total_score >= 0.4 else "low"
        }
    
    def run_analysis(self):
        """運行分析"""
        print("🎯 內容模式分析結果")
        print("=" * 50)
        
        for i, example in enumerate(self.examples, 1):
            print(f"\n📝 範例 {i}: {example['type']}")
            print("-" * 30)
            print(f"預估互動等級: {example['engagement']}")
            
            result = self.analyze_content(example['content'])
            print(f"個人化分數: {result['personal_score']:.2f}")
            print(f"情感分數: {result['emotion_score']:.2f}")
            print(f"互動分數: {result['interaction_score']:.2f}")
            print(f"創意分數: {result['creative_score']:.2f}")
            print(f"幽默分數: {result['humor_score']:.2f}")
            print(f"總分: {result['total_score']:.2f}")
            print(f"分析等級: {result['engagement_level']}")
        
        print("\n🔍 高互動內容特徵分析")
        print("=" * 50)
        
        high_engagement_examples = [ex for ex in self.examples if ex['engagement'] == 'high']
        medium_engagement_examples = [ex for ex in self.examples if ex['engagement'] == 'medium']
        
        print(f"\n高互動範例 ({len(high_engagement_examples)} 篇):")
        for ex in high_engagement_examples:
            result = self.analyze_content(ex['content'])
            print(f"- {ex['type']}: 總分 {result['total_score']:.2f}")
        
        print(f"\n中等互動範例 ({len(medium_engagement_examples)} 篇):")
        for ex in medium_engagement_examples:
            result = self.analyze_content(ex['content'])
            print(f"- {ex['type']}: 總分 {result['total_score']:.2f}")
        
        print("\n💡 高互動內容的共同特徵:")
        print("1. 個人化表達 - 使用「我」、「我的」等個人代詞")
        print("2. 情感表達 - 分享個人感受和經驗")
        print("3. 互動引導 - 提出問題或邀請讀者參與")
        print("4. 創意表達 - 使用表情符號和生動描述")
        print("5. 幽默元素 - 使用比喻和創意表達")
        print("6. 直接回答 - 針對讀者疑問給出明確答案")
        print("7. 結構化 - 有條理地組織內容")
        
        print("\n📊 具體建議:")
        print("- 多使用「我認為」、「我的看法」等個人化表達")
        print("- 加入「你覺得呢？」、「留言告訴我」等互動元素")
        print("- 使用表情符號增加視覺吸引力")
        print("- 加入創意比喻和幽默表達")
        print("- 直接回答讀者問題，避免過於正式")
        print("- 分享個人經驗和感受")

if __name__ == "__main__":
    analyzer = SimpleContentAnalyzer()
    analyzer.run_analysis()



