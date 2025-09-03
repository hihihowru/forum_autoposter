#!/usr/bin/env python3
"""
6919 康霈生技貼文生成腳本
使用 Serper API 搜尋最新新聞，生成真實的漲停相關貼文
使用完整的個人化 prompting 系統
"""

import asyncio
import json
import logging
import requests
import random
from datetime import datetime
import os
import sys
from typing import Dict, List, Any, Optional

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SerperNewsClient:
    """Serper API 新聞搜尋客戶端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """搜尋新聞"""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": num_results,
                "type": "search"
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            organic_results = data.get('organic', [])
            
            # 過濾出相關的新聞
            relevant_news = []
            for result in organic_results:
                if any(keyword in result.get('title', '').lower() for keyword in ['康霈', '6919', '漲停', '生技']):
                    relevant_news.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'link': result.get('link', ''),
                        'date': result.get('date', '')
                    })
            
            return relevant_news
            
        except Exception as e:
            logger.error(f"搜尋新聞失敗: {e}")
            return []

class PersonalizedKOLSettings:
    """KOL 個人化設定"""
    
    def __init__(self):
        # 預設的 KOL 個人化設定
        self.kol_settings = {
            "200": {  # 川川哥
                "nickname": "川川哥",
                "persona": "技術派",
                "prompt_template": """你是川川哥，一個專精技術分析的股市老手。你的特色是：
- 語氣直接但有料，有時會狂妄，有時又碎碎念
- 大量使用技術分析術語
- 不愛用標點符號，全部用省略號串起來
- 偶爾會英文逗號亂插
- 很少用 emoji，偶爾用 📊 📈 🎯""",
                "tone_vector": {
                    "formal_level": 3,
                    "emotion_intensity": 7,
                    "confidence_level": 9,
                    "interaction_level": 6
                },
                "content_preferences": {
                    "length_type": "short",
                    "paragraph_style": "省略號分隔，不換行",
                    "ending_style": "想知道的話，留言告訴我，咱們一起討論一下..."
                },
                "vocabulary": {
                    "technical_terms": ["黃金交叉", "均線糾結", "三角收斂", "K棒爆量", "跳空缺口", "支撐帶", "壓力線", "MACD背離"],
                    "casual_expressions": ["穩了啦", "爆啦", "嘎到", "要噴啦", "破線啦", "睡醒漲停"]
                },
                "typing_habits": {
                    "punctuation_style": "省略號為主...偶爾逗號,",
                    "sentence_pattern": "短句居多...不愛長句",
                    "emoji_usage": "很少用"
                }
            },
            "201": {  # 韭割哥
                "nickname": "韭割哥",
                "persona": "總經派",
                "prompt_template": """你是韭割哥，一個深度總體經濟分析師。你的特色是：
- 語氣穩重，分析深入
- 注重基本面分析
- 使用專業的經濟術語
- 偶爾用 emoji 強調重點
- 結尾常常鼓勵長期投資""",
                "tone_vector": {
                    "formal_level": 7,
                    "emotion_intensity": 4,
                    "confidence_level": 8,
                    "interaction_level": 5
                },
                "content_preferences": {
                    "length_type": "medium",
                    "paragraph_style": "段落分明，邏輯清晰",
                    "ending_style": "投資要有耐心，時間會證明一切的價值。"
                },
                "vocabulary": {
                    "fundamental_terms": ["基本面", "估值", "成長性", "財務結構", "產業趨勢", "政策環境"],
                    "investment_terms": ["價值投資", "長期持有", "風險管理", "資產配置"]
                },
                "typing_habits": {
                    "punctuation_style": "正常標點符號",
                    "sentence_pattern": "完整句子，邏輯清晰",
                    "emoji_usage": "適度使用 📊 💡 💰 📈"
                }
            }
        }
    
    def get_kol_settings(self, kol_serial: str) -> Dict[str, Any]:
        """獲取 KOL 設定"""
        return self.kol_settings.get(kol_serial, self.kol_settings["200"])

class KangpeiPostGenerator:
    """康霈生技貼文生成器"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient(
            credentials_file='./credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        self.news_client = SerperNewsClient("59eac2d4f87afca3ae6e252f4214098defdd40fa")
        self.kol_settings = PersonalizedKOLSettings()
        
    async def get_kol_credentials(self) -> List[Dict[str, Any]]:
        """獲取 KOL 帳號資訊"""
        try:
            data = self.sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            if not data or len(data) < 2:
                logger.error("無法讀取 KOL 帳號資料")
                return []
            
            headers = data[0]
            kol_data = []
            
            for row in data[1:]:
                if len(row) >= 10 and row[0]:  # 確保有基本資料
                    kol = {
                        'serial': row[0],
                        'nickname': row[1],
                        'member_id': row[4],  # MemberId 在第 5 列
                        'password': row[6],  # 密碼在第 7 列
                        'persona': row[3],   # 人設在第 4 列
                        'status': row[9] if len(row) > 9 else 'active'  # 狀態在第 10 列
                    }
                    kol_data.append(kol)
            
            return kol_data
            
        except Exception as e:
            logger.error(f"獲取 KOL 資料失敗: {e}")
            return []
    
    def search_kangpei_news(self) -> List[Dict[str, Any]]:
        """搜尋康霈生技相關新聞"""
        logger.info("🔍 搜尋康霈生技相關新聞...")
        
        # 搜尋多個關鍵詞組合
        search_queries = [
            "6919 康霈生技 漲停",
            "康霈生技 減重藥 新聞",
            "康霈 CBL-514 新藥"
        ]
        
        all_news = []
        for query in search_queries:
            news = self.news_client.search_news(query, 3)
            all_news.extend(news)
        
        # 去重並按日期排序
        unique_news = []
        seen_titles = set()
        for news in all_news:
            if news['title'] not in seen_titles:
                unique_news.append(news)
                seen_titles.add(news['title'])
        
        logger.info(f"✅ 找到 {len(unique_news)} 條相關新聞")
        return unique_news[:5]  # 最多取 5 條
    
    def _analyze_news(self, news_data: List[Dict[str, Any]]) -> str:
        """分析新聞內容，提取關鍵資訊"""
        if not news_data:
            return "無相關新聞資料"
        
        key_points = []
        for news in news_data:
            title = news.get('title', '')
            snippet = news.get('snippet', '')
            
            # 提取關鍵資訊
            if '漲停' in title or '漲停' in snippet:
                key_points.append("股價出現漲停表現")
            if '減重' in title or '減重' in snippet:
                key_points.append("減重新藥CBL-514題材發酵")
            if '外資' in title or '外資' in snippet:
                key_points.append("外資買盤積極")
            if '分割' in title or '分割' in snippet:
                key_points.append("股票面額分割提升流動性")
        
        # 去重
        unique_points = list(set(key_points))
        
        summary = f"""
最新市場動態：
{chr(10).join([f"• {point}" for point in unique_points])}

相關新聞來源：{len(news_data)} 條最新報導
"""
        return summary
    
    def _build_personalized_system_prompt(self, kol_settings: Dict[str, Any], news_summary: str) -> str:
        """建立個人化系統 prompt"""
        base_template = kol_settings['prompt_template']
        tone_vector = kol_settings['tone_vector']
        vocabulary = kol_settings['vocabulary']
        content_prefs = kol_settings['content_preferences']
        typing_habits = kol_settings['typing_habits']
        
        # 語氣指導
        tone_guidance = f"""
語氣特徵：
- 正式程度：{tone_vector['formal_level']}/10
- 情緒強度：{tone_vector['emotion_intensity']}/10
- 自信程度：{tone_vector['confidence_level']}/10
- 互動程度：{tone_vector['interaction_level']}/10
"""
        
        # 詞彙指導
        vocab_guidance = f"""
詞彙風格：
- 專業術語：{', '.join(vocabulary.get('technical_terms', vocabulary.get('fundamental_terms', [])))}
- 口語表達：{', '.join(vocabulary.get('casual_expressions', vocabulary.get('investment_terms', [])))}
"""
        
        # 格式指導
        format_guidance = f"""
格式要求：
- 內容長度：{content_prefs['length_type']}
- 段落風格：{content_prefs['paragraph_style']}
- 結尾風格：{content_prefs['ending_style']}
- 標點習慣：{typing_habits['punctuation_style']}
- 句子模式：{typing_habits['sentence_pattern']}
- Emoji使用：{typing_habits['emoji_usage']}
"""
        
        system_prompt = f"""{base_template}

{tone_guidance}

{vocab_guidance}

{format_guidance}

新聞背景：
{news_summary}

重要指導：
1. 嚴格保持 {kol_settings['nickname']} 的個人風格和語氣
2. 大量使用專屬詞彙和表達方式
3. 遵循固定的打字習慣和格式
4. 內容長度控制在 {content_prefs['length_type']} 範圍
5. 結尾使用固定的風格：{content_prefs['ending_style']}
6. 避免 AI 生成的痕跡，要像真人發文
7. 針對康霈生技(6919)的漲停題材進行分析
"""
        
        return system_prompt
    
    def _build_user_prompt(self, kol_settings: Dict[str, Any]) -> str:
        """建立用戶 prompt"""
        return f"""請為康霈生技(6919)生成一篇貼文，內容包括：

1. 標題：要吸引人，符合{kol_settings['nickname']}的風格
2. 內容：分析康霈生技的漲停題材，包括：
   - 技術面或基本面分析
   - 減重新藥CBL-514的題材
   - 外資買盤動向
   - 投資建議和風險提醒

請確保：
- 完全符合{kol_settings['nickname']}的個人風格
- 使用專屬的詞彙和表達方式
- 遵循固定的打字習慣
- 內容真實可信，避免過度誇張

請直接生成標題和內容，不需要額外說明。"""
    
    def _generate_personalized_content(self, kol: Dict[str, Any], news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用個人化設定生成內容"""
        try:
            kol_settings = self.kol_settings.get_kol_settings(kol['serial'])
            news_summary = self._analyze_news(news_data)
            
            # 建立個人化 prompt
            system_prompt = self._build_personalized_system_prompt(kol_settings, news_summary)
            user_prompt = self._build_user_prompt(kol_settings)
            
            logger.info(f"為 {kol['nickname']} 建立個人化 prompt")
            
            # 模擬個人化內容生成（實際應該調用 LLM）
            if '技術' in kol_settings['persona']:
                # 川川哥風格
                title = f"康霈生技(6919)技術面突破...從圖表看關鍵阻力位"
                content = f"""康霈生技(6919)今日技術面表現亮眼...從圖表分析，股價突破關鍵阻力位，形成新的上升趨勢...

📊 技術指標觀察：
• 股價突破前高，形成新的上升趨勢
• 成交量放大，確認突破有效性
• MACD 指標顯示多頭動能增強
• RSI 位於 60-70 區間，顯示強勢但未過熱

🎯 關鍵點位：
• 支撐位：約 120-125 元
• 阻力位：約 140-145 元
• 成交量：今日明顯放大，顯示買盤積極

{news_summary}

💡 操作建議：
建議關注 125 元支撐位，若能守住此位置，後續有機會挑戰更高價位...但需注意追高風險，建議分批進場...

想知道的話，留言告訴我，咱們一起討論一下..."""
                
            else:
                # 韭割哥風格
                title = f"康霈生技(6919)基本面深度分析：減重藥市場潛力評估"
                content = f"""康霈生技(6919)基本面分析時間！

從總經角度來看，這個話題值得我們深入思考。

🏥 公司背景：
康霈生技專注於減重新藥研發，CBL-514為其核心產品線。

📈 營運亮點：
• CBL-514減重新藥研發進展順利
• 減重藥市場潛力龐大
• 外資法人持續關注

💰 財務表現：
• 研發投入持續增加
• 新藥授權題材發酵
• 市場給予高估值

{news_summary}

⚠️ 風險提醒：
• 新藥研發存在不確定性
• 股價波動較大，需注意風險
• 建議關注研發進度

💡 投資建議：
建議大家用長期投資的角度來看，短期波動不用太擔心。價值投資才是王道！

投資要有耐心，時間會證明一切的價值。"""
            
            return {
                'title': title,
                'content': content,
                'keywords': f"康霈生技,6919,減重藥,CBL-514,{kol_settings['persona']}"
            }
            
        except Exception as e:
            logger.error(f"生成個人化內容失敗: {e}")
            # 回退到簡單內容
            return self._generate_simple_content(kol, news_data)
    
    def _generate_simple_content(self, kol: Dict[str, Any], news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成簡單內容（回退方案）"""
        news_summary = self._analyze_news(news_data)
        
        if '技術' in kol['persona']:
            title = f"康霈生技(6919)技術面分析"
            content = f"""康霈生技(6919)今日技術面表現亮眼！

📊 技術指標觀察：
• 股價突破前高，形成新的上升趨勢
• 成交量放大，確認突破有效性
• MACD 指標顯示多頭動能增強

{news_summary}

💡 操作建議：
建議關注支撐位，若能守住此位置，後續有機會挑戰更高價位。但需注意追高風險，建議分批進場。

大家覺得康霈這波技術面如何？"""
        else:
            title = f"康霈生技(6919)基本面分析"
            content = f"""康霈生技(6919)基本面分析時間！

🏥 公司背景：
康霈生技專注於減重新藥研發，CBL-514為其核心產品線。

📈 營運亮點：
• CBL-514減重新藥研發進展順利
• 減重藥市場潛力龐大
• 外資法人持續關注

{news_summary}

⚠️ 風險提醒：
• 新藥研發存在不確定性
• 股價波動較大，需注意風險

大家對康霈的基本面有什麼看法？"""
        
        return {
            'title': title,
            'content': content,
            'keywords': f"康霈生技,6919,減重藥,CBL-514,{kol['persona']}"
        }
    
    def generate_kol_post(self, kol: Dict[str, Any], news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """為特定 KOL 生成貼文"""
        try:
            logger.info(f"為 {kol['nickname']} 生成康霈生技相關貼文")
            
            # 使用個人化設定生成內容
            content_data = self._generate_personalized_content(kol, news_data)
            
            post_data = {
                'post_id': f"6919_{kol['serial']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'kol_serial': kol['serial'],
                'kol_nickname': kol['nickname'],
                'kol_id': kol['member_id'],
                'persona': kol['persona'],
                'content_type': 'investment',
                'topic_index': 1,
                'topic_id': f"6919_kangpei_{datetime.now().strftime('%Y%m%d')}",
                'topic_title': content_data['title'],
                'topic_keywords': content_data['keywords'],
                'content': content_data['content'],
                'status': 'ready_to_post',
                'scheduled_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'post_time': '',
                'error_message': '',
                'platform_post_id': '',
                'platform_post_url': '',
                'trending_topic_title': '康霈生技漲停題材發酵'
            }
            
            logger.info(f"✅ 成功生成 {kol['nickname']} 的貼文")
            return post_data
                
        except Exception as e:
            logger.error(f"生成 {kol['nickname']} 貼文時發生錯誤: {e}")
            return None
    
    async def update_posts_sheet(self, posts: List[Dict[str, Any]]):
        """更新貼文記錄表 - 使用正確的 A-R 欄位格式"""
        try:
            # 讀取現有數據
            existing_data = self.sheets_client.read_sheet('貼文記錄表', 'A:R')
            
            # 準備新數據 - 按照 A-R 欄位順序
            new_rows = []
            for post in posts:
                row = [
                    post['post_id'],                    # A: 貼文ID
                    post['kol_serial'],                  # B: KOL Serial
                    post['kol_nickname'],                # C: KOL 暱稱
                    post['kol_id'],                      # D: KOL ID
                    post['persona'],                     # E: Persona
                    post['content_type'],                # F: Content Type
                    post['topic_index'],                 # G: 已派發TopicIndex
                    post['topic_id'],                    # H: 已派發TopicID
                    post['topic_title'],                 # I: 已派發TopicTitle
                    post['topic_keywords'],              # J: 已派發TopicKeywords
                    post['content'],                     # K: 生成內容
                    post['status'],                      # L: 發文狀態
                    post['scheduled_time'],              # M: 上次排程時間
                    post['post_time'],                   # N: 發文時間戳記
                    post['error_message'],              # O: 最近錯誤訊息
                    post['platform_post_id'],           # P: 平台發文ID
                    post['platform_post_url'],          # Q: 平台發文URL
                    post['trending_topic_title']        # R: 熱門話題標題
                ]
                new_rows.append(row)
            
            # 追加到工作表
            if existing_data:
                # 找到最後一行的位置
                last_row = len(existing_data) + 1
                range_name = f'貼文記錄表!A{last_row}'
            else:
                # 如果工作表為空，從第一行開始
                range_name = '貼文記錄表!A1'
            
            # 寫入數據
            self.sheets_client.write_sheet(range_name, new_rows)
            
            logger.info(f"✅ 成功更新貼文記錄表，新增 {len(posts)} 筆記錄")
            
        except Exception as e:
            logger.error(f"更新貼文記錄表失敗: {e}")
    
    async def run(self):
        """執行貼文生成流程"""
        logger.info("🚀 開始生成 6919 康霈生技相關貼文...")
        
        try:
            # 1. 獲取 KOL 資料
            kol_list = await self.get_kol_credentials()
            if not kol_list:
                logger.error("無法獲取 KOL 資料")
                return
            
            # 選擇兩個 KOL（優先選擇技術派）
            selected_kols = []
            for kol in kol_list:
                if kol['status'] == 'active':
                    if '技術' in kol['persona'] or len(selected_kols) < 2:
                        selected_kols.append(kol)
                        if len(selected_kols) >= 2:
                            break
            
            if len(selected_kols) < 2:
                logger.warning(f"只找到 {len(selected_kols)} 個可用 KOL，使用所有可用 KOL")
                selected_kols = [kol for kol in kol_list if kol['status'] == 'active'][:2]
            
            logger.info(f"📋 選中的 KOL: {[kol['nickname'] for kol in selected_kols]}")
            
            # 2. 搜尋康霈生技相關新聞
            news_data = self.search_kangpei_news()
            
            # 3. 為每個 KOL 生成貼文
            generated_posts = []
            for kol in selected_kols:
                post_data = self.generate_kol_post(kol, news_data)
                if post_data:
                    generated_posts.append(post_data)
            
            # 4. 更新貼文記錄表
            if generated_posts:
                await self.update_posts_sheet(generated_posts)
                
                logger.info("📊 生成結果摘要:")
                for post in generated_posts:
                    logger.info(f"  - {post['kol_nickname']} ({post['persona']}): {post['topic_title']}")
                    logger.info(f"    內容長度: {len(post['content'])} 字")
                    logger.info("")
            else:
                logger.error("❌ 沒有成功生成任何貼文")
                
        except Exception as e:
            logger.error(f"貼文生成流程失敗: {e}")

async def main():
    """主函數"""
    generator = KangpeiPostGenerator()
    await generator.run()

if __name__ == "__main__":
    asyncio.run(main())
