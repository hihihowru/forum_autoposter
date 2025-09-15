#!/usr/bin/env python3
"""
OpenAI API 客戶端
用於內容生成和個人化提示詞處理
"""

import os
import aiohttp
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ContentGenerationRequest:
    """內容生成請求"""
    stock_id: str
    stock_name: str
    analysis_type: str
    kol_profile: Dict[str, Any]
    stock_data: Optional[Dict[str, Any]] = None
    news_data: Optional[Dict[str, Any]] = None
    target_length: int = 300
    content_style: str = "分析"

@dataclass
class ContentGenerationResult:
    """內容生成結果"""
    title: str
    content: str
    tokens_used: int
    model_used: str
    generation_time: datetime
    quality_score: float
    personalization_score: float

class OpenAIAPIClient:
    """OpenAI API 客戶端"""
    
    def __init__(self):
        """初始化 OpenAI API 客戶端"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("缺少 OPENAI_API_KEY 環境變數")
        
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.session = None
        self.default_model = "gpt-3.5-turbo"
        
        logger.info("OpenAI API 客戶端初始化完成")
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    def _get_title_guidance_by_style(self, title_style: str) -> str:
        """根據標題風格獲取特定的標題指導"""
        title_guidances = {
            "question": """
標題風格：問句類（13.1%）
- 使用疑問句形式，增加互動性
- 示例：「這波漲勢能持續多久？」「背後原因究竟是什麼？」「市場情緒為何如此熱烈？」
- 避免重複使用「怎麼了？」「為什麼？」等常見問句
- 可以嘗試：「這檔股票在搞什麼？」「市場瘋了嗎？」「投資人到底在想什麼？」
""",
            "exclamation": """
標題風格：感嘆類（5.1%）
- 使用感嘆句形式，表達強烈情緒
- 示例：「太瘋狂了！」「這波操作太神了！」「市場情緒燃燒天際！」
- 避免重複使用「太猛了！」「好棒！」等常見感嘆
- 可以嘗試：「這檔股票要起飛了！」「市場情緒炸裂！」「投資人瘋狂了！」
""",
            "command": """
標題風格：指令類（3.1%）
- 使用指令句形式，提供明確指引
- 示例：「注意！航運股起飛」「快看！AI概念股」「提醒！台積電突破」
- 避免重複使用「注意！」「提醒！」等常見指令
- 可以嘗試：「快看！這檔股票要爆發」「注意！市場風向轉變」「提醒！技術面突破」
""",
            "professional": """
標題風格：專業類（2.9%）
- 使用專業術語，突出專業性
- 示例：「營收成長50%」「技術面突破」「基本面轉好」
- 避免重複使用「營收成長」「基本面轉好」等常見專業詞
- 可以嘗試：「獲利能力大幅提升」「技術指標全面轉強」「營運效率顯著改善」
""",
            "topic": """
標題風格：話題類（AI 1.3%）
- 關注熱門話題，緊跟時事
- 示例：「AI概念股爆發」「半導體熱潮」「金融股轉強」
- 避免重複使用「市場情緒」「技術面」等常見話題
- 可以嘗試：「產業趨勢明朗化」「政策利多發酵」「資金流向明確」
""",
            "emoji": """
標題風格：表情符號類（3.5%）
- 適度使用表情符號，增加視覺效果
- 示例：「🔥 營收爆發！」「📈 技術突破！」「❤️ 基本面轉好！」
- 避免重複使用「🔥」「📈」等常見表情
- 可以嘗試：「🚀 股價起飛！」「💎 價值發現！」「⚡ 動能爆發！」
""",
            "humorous": """
標題風格：幽默類（搞笑比喻）
- 使用搞笑比喻和幽默表達
- 示例：「股價像火箭一樣衝上天！」「這檔股票要起飛了！」
- 避免重複使用「韭菜」「火箭」等常見比喻
- 可以嘗試：「這檔股票要開掛了！」「市場情緒像過山車！」「投資人瘋狂搶購！」
""",
            "alert": """
標題風格：提醒類（指令句 3.1%）
- 使用提醒句形式，提供風險提醒
- 示例：「注意！市場震盪」「提醒！技術面轉弱」「關注！財報公布」
- 避免重複使用「注意！」「提醒！」等常見提醒
- 可以嘗試：「快看！這檔股票要爆發」「關注！市場風向轉變」「留意！技術面突破」
""",
            "concise": """
標題風格：簡潔類（≤15字）
- 簡潔明瞭，重點突出
- 示例：「營收成長」「技術突破」「基本面轉好」
- 避免重複使用常見簡潔詞彙
- 可以嘗試：「獲利提升」「動能增強」「趨勢明朗」
""",
            "balanced": """
標題風格：平衡類（綜合型）
- 綜合多種風格，保持平衡
- 根據內容靈活選擇問句、感嘆句、專業術語
- 避免過度偏向某一風格
- 可以嘗試：「這波漲勢背後的原因」「市場情緒為何如此熱烈」「技術面突破的意義」
"""
        }
        
    def _create_personalized_prompt(self, request: ContentGenerationRequest) -> str:
        """創建個人化提示詞（基於真實 UGC 數據分析）"""
        kol = request.kol_profile
        
        # 獲取 KOL 的標題風格
        title_style = kol.get('title_style', 'balanced')
        
        # 根據標題風格生成特定的標題指導
        title_guidance = self._get_title_guidance_by_style(title_style)
        
        # 基礎提示詞模板
        base_prompt = f"""
你是一位專業的股票分析師，需要為 KOL "{kol.get('persona', '專業分析師')}" 生成一篇關於 {request.stock_name}({request.stock_id}) 的股票分析文章。

KOL 個人化設定：
- 人設：{kol.get('persona', '專業分析師')}
- 寫作風格：{kol.get('writing_style', '專業分析')}
- 語氣：{kol.get('tone', '專業')}
- 關鍵詞：{', '.join(kol.get('key_phrases', []))}
- 避免話題：{', '.join(kol.get('avoid_topics', []))}
- 標題風格：{title_style}

分析類型：{request.analysis_type}
目標長度：{request.target_length} 字
內容風格：{request.content_style}

重要要求：
1. 標題格式：
   - 不要有「標題：」前綴
   - 不要有 ## 或 ### 符號
   - 不要有【】符號
   - 不要提到 KOL 名字或派別
   - 不要包含股票名稱（因為已經在貼文中 tag 股票代號）
   - 不要包含股票代號
   - 長度嚴格控制在 ≤15字（平均 11.0 字）
   - 重點描述漲停原因、市場情緒或產業動態

{title_guidance}

2. 內容要求：
   - 不要有「內容：」前綴
   - 避免制式化的「投資建議」、「風險提醒」
   - 內容要自然流暢，符合 KOL 風格
   - 股票名稱和代號只提到其中一個
   - 股票代號使用純數字格式
   - 避免重複的格式和用詞

3. 數據格式：
   - 成交量用「張數」表示（1000股 = 1張）
   - 營收用「百萬」或「億」為單位
   - 財報數據用「億」為單位
   - 技術指標要可解釋

4. 新聞整合：
   - 如果有漲停相關新聞，要分析漲停原因
   - 整合 Serper API 搜尋到的相關新聞
   - 分析上漲動能和市場情緒
"""

        # 根據分析類型添加特定要求
        if request.analysis_type == "revenue":
            base_prompt += """
營收分析重點：
- 分析月營收表現（用百萬/億為單位）
- 比較年增率和月增率
- 分析營收趨勢和動能
- 結合漲停原因分析
- 避免制式化投資建議
"""
        elif request.analysis_type == "earnings":
            base_prompt += """
財報分析重點：
- 分析 EPS 表現（用元為單位）
- 分析毛利率和淨利率（用%表示）
- 比較獲利能力
- 結合漲停原因分析
- 避免制式化投資建議
"""
        elif request.analysis_type in ["news_3", "news_2"]:
            base_prompt += """
新聞分析重點：
- 整合 Serper API 搜尋到的相關新聞
- 分析漲停原因和市場情緒
- 分析上漲動能和相關消息
- 避免制式化投資建議
- 重點分析新聞對股價的影響
"""
        elif request.analysis_type == "price":
            base_prompt += """
技術分析重點：
- 分析股價走勢和漲停原因
- 分析技術指標（成交量用張數）
- 結合 Serper API 新聞分析
- 分析上漲動能和市場情緒
- 避免制式化投資建議
"""

        # 添加股票數據（如果有）
        if request.stock_data:
            # 轉換數據格式
            formatted_data = self._format_stock_data(request.stock_data)
            base_prompt += f"""
股票數據（已格式化）：
{json.dumps(formatted_data, ensure_ascii=False, indent=2)}
"""

        # 添加新聞數據（如果有）
        if request.news_data and request.news_data.get('has_news', False):
            news_info = f"""
相關新聞（{request.news_data.get('news_count', 0)}則）：
"""
            # 添加新聞標題
            if request.news_data.get('news_titles'):
                news_info += "新聞標題：\n"
                for i, title in enumerate(request.news_data['news_titles'][:3], 1):
                    news_info += f"{i}. {title}\n"
            
            # 添加新聞摘要
            if request.news_data.get('news_summaries'):
                news_info += "\n新聞摘要：\n"
                for i, summary in enumerate(request.news_data['news_summaries'][:3], 1):
                    news_info += f"{i}. {summary[:100]}...\n"
            
            # 添加漲停原因
            if request.news_data.get('limit_up_reason'):
                news_info += f"\n漲停原因分析：{request.news_data['limit_up_reason']}\n"
            
            base_prompt += news_info + """
請重點分析：
1. 漲停原因和相關新聞
2. 上漲動能和市場情緒
3. 相關產業消息
4. 對股價的影響
"""
        else:
            base_prompt += """
注意：目前沒有找到相關新聞，請基於技術面和市場情緒進行分析。
"""

        base_prompt += """
請直接生成標題和內容，不要有任何前綴標記。

標題要求（基於真實 UGC 數據分析）：
- 長度：嚴格控制在 ≤15字（平均 11.0 字）
- 絕對不要包含股票名稱或代號（因為已經在貼文中 tag）
- 不要包含媒體名稱、前綴符號（##、###、【】等）

標題風格分布（基於真實 UGC 數據）：
1. 問句類（13.1%）："怎麼了？"、"該買嗎？"、"怎麼看？"
2. 感嘆類（5.1%）："太猛了！"、"好棒！"、"舒服！"
3. 指令類（3.1%）："注意！"、"快看！"、"提醒！"
4. 專業類（2.9%）："營收成長"、"技術突破"、"基本面轉好"

表情符號使用（3.5%）：適度使用 🔥📈❤️ 等投資相關表情

互動性要求：
- 問句比例：13.1%（如："台積電怎麼了？"、"AI概念股該買嗎？"）
- 感嘆句比例：5.1%（如："太猛了！"、"好棒！"）
- 指令句比例：3.1%（如："注意！航運股起飛"）

專業術語融入：
- 基本面：2.9%（營收、財報、EPS）
- 籌碼面：2.8%（外資、主力、融資）
- 技術面：0.9%（突破、支撐、均線）

熱門話題關注：
- AI：1.3%（最熱門話題）
- 半導體：0.9%
- 金融：0.7%

真實 UGC 標題示例：
問句類：「台積電怎麼了？」「AI概念股該買嗎？」「航運股怎麼看？」
感嘆類：「太猛了！」「好棒！」「舒服！」「神了！」
專業類：「營收成長50%」「技術面突破」「基本面轉好」
指令類：「注意！航運股起飛」「快看！AI概念股」「提醒！台積電突破」

內容要求：
- 自然流暢，符合 KOL 風格
- 避免制式化語言
- 不要重複標題內容
- 使用繁體中文

請直接輸出：
[標題]
[內容]
"""

        return base_prompt
    
    def _format_stock_data(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化股票數據"""
        formatted = stock_data.copy()
        
        # 轉換成交量為張數
        if 'volume' in formatted:
            volume_shares = formatted['volume']
            volume_units = volume_shares / 1000  # 1000股 = 1張
            formatted['volume_units'] = f"{volume_units:,.0f}張"
        
        # 轉換營收為百萬/億
        if 'revenue' in formatted:
            revenue = formatted['revenue']
            if revenue >= 100000000:  # 1億以上
                formatted['revenue_formatted'] = f"{revenue/100000000:.2f}億元"
            else:
                formatted['revenue_formatted'] = f"{revenue/1000000:.2f}百萬元"
        
        # 轉換 EPS 為元
        if 'eps' in formatted:
            formatted['eps_formatted'] = f"{formatted['eps']:.2f}元"
        
        # 轉換毛利率和淨利率為百分比
        if 'gross_margin' in formatted:
            formatted['gross_margin_formatted'] = f"{formatted['gross_margin']:.2f}%"
        if 'net_margin' in formatted:
            formatted['net_margin_formatted'] = f"{formatted['net_margin']:.2f}%"
        
        return formatted
    
    async def generate_content(self, request: ContentGenerationRequest) -> Optional[ContentGenerationResult]:
        """生成內容"""
        try:
            prompt = self._create_personalized_prompt(request)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.default_model,
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一位專業的股票分析師，擅長生成個人化的股票分析內容。重要：標題絕對不能包含股票名稱或代號，因為已經在貼文中 tag 了。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': request.target_length * 2,  # 預留足夠的 token
                'temperature': 0.7,
                'top_p': 0.9,
                'frequency_penalty': 0.1,
                'presence_penalty': 0.1
            }
            
            async with self.session.post(self.base_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        
                        # 解析標題和內容
                        title, content_text = self._parse_title_and_content(content)
                        
                        # 計算品質評分
                        quality_score = self._calculate_quality_score(title, content_text, request)
                        
                        # 計算個人化評分
                        personalization_score = self._calculate_personalization_score(content_text, request.kol_profile)
                        
                        return ContentGenerationResult(
                            title=title,
                            content=content_text,
                            tokens_used=data['usage']['total_tokens'],
                            model_used=self.default_model,
                            generation_time=datetime.now(),
                            quality_score=quality_score,
                            personalization_score=personalization_score
                        )
                
                logger.warning(f"OpenAI API 生成失敗: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI API 生成時發生錯誤: {e}")
            return None
    
    def _parse_title_and_content(self, content: str) -> tuple[str, str]:
        """解析標題和內容"""
        lines = content.split('\n')
        title = ""
        content_text = ""
        
        # 特殊處理：如果內容包含制表符分隔的格式
        if len(lines) == 1 and '\t' in lines[0]:
            parts = lines[0].split('\t')
            if len(parts) >= 2:
                # 第一部分是標記，第二部分包含標題和內容
                if parts[0].strip() == '標題':
                    title_content_part = parts[1].strip()
                    # 在標題內容部分中尋找 "內容" 的位置
                    content_pos = title_content_part.find('內容')
                    if content_pos > 0:
                        title = title_content_part[:content_pos].strip()
                        content_text = title_content_part[content_pos:].strip()
                        # 移除內容中的 "內容" 前綴
                        if content_text.startswith('內容'):
                            content_text = content_text[2:].strip()
                    else:
                        # 如果沒有找到 "內容"，整個第二部分作為標題
                        title = title_content_part
                else:
                    # 如果不是 "標題" 標記，按正常流程處理
                    pass
            else:
                # 如果分割後只有一個部分，按正常流程處理
                pass
        
        # 如果沒有通過特殊處理得到結果，使用正常流程
        if not title and not content_text:
            # 清理內容，移除不必要的標記
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # 移除標題：、內容：等前綴
                if line.startswith('標題：'):
                    line = line[3:].strip()
                elif line.startswith('內容：'):
                    line = line[3:].strip()
                elif line.startswith('標題\t'):
                    line = line[2:].strip()
                elif line.startswith('內容\t'):
                    line = line[2:].strip()
                
                # 移除媒體名稱前綴
                media_prefixes = ['財訊快報：', '鉅亨網：', '奇摩股市：', '經濟日報：', '工商時報：']
                for prefix in media_prefixes:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                
                if line:
                    cleaned_lines.append(line)
            
            # 特殊處理：如果第一行包含 "標題" 和 "內容"，需要分離
            if cleaned_lines and '標題' in cleaned_lines[0] and '內容' in cleaned_lines[0]:
                first_line = cleaned_lines[0]
                # 尋找 "內容" 的位置
                content_pos = first_line.find('內容')
                if content_pos > 0:
                    title_part = first_line[:content_pos].strip()
                    content_part = first_line[content_pos:].strip()
                    
                    # 移除標題中的 "標題" 前綴
                    if title_part.startswith('標題'):
                        title_part = title_part[2:].strip()
                    
                    # 移除內容中的 "內容" 前綴
                    if content_part.startswith('內容'):
                        content_part = content_part[2:].strip()
                    
                    cleaned_lines[0] = title_part
                    if content_part:
                        cleaned_lines.insert(1, content_part)
            
            # 尋找標題（第一行或較短的行）
            for i, line in enumerate(cleaned_lines):
                if not title and len(line) <= 30 and not line.startswith('•') and not line.startswith('-'):
                    title = line
                else:
                    if content_text:
                        content_text += '\n' + line
                    else:
                        content_text = line
            
            # 如果沒有找到標題，從內容中提取
            if not title and content_text:
                # 取第一句作為標題
                sentences = content_text.split('。')
                if sentences:
                    first_sentence = sentences[0].strip()
                    if len(first_sentence) <= 25:
                        title = first_sentence
                    else:
                        title = first_sentence[:25] + "..."
        
        # 確保標題不包含股票代號和公司名稱
        if title:
            # 移除標題中的股票代號格式
            import re
            title = re.sub(r'\([0-9]+\)', '', title)  # 移除 (1234) 格式
            title = re.sub(r'[0-9]{4}', '', title)   # 移除純數字代號
            
            # 移除常見的股票名稱（根據您提供的列表）
            stock_names = [
                '昇陽半導體', '朋程', '龍德造船', '立積', '昇達科技', '康霈生技', 
                '世紀鋼', '懷特', '南茂', '訊舟', '雷虎', '富邦金', '昇佳電子'
            ]
            for stock_name in stock_names:
                title = title.replace(stock_name, '').strip()
            
            # 移除多餘的標點符號
            title = re.sub(r'^[：:]\s*', '', title)  # 移除開頭的冒號
            title = re.sub(r'\s+', ' ', title)  # 多個空格變單個空格
            title = title.strip()
        
        # 如果標題太長，截斷
        if title and len(title) > 25:
            title = title[:25] + "..."
        
        # 確保內容不包含標題
        if content_text and title and content_text.startswith(title):
            content_text = content_text[len(title):].strip()
            if content_text.startswith('。'):
                content_text = content_text[1:].strip()
        
        return title, content_text
    
    def _calculate_quality_score(self, title: str, content: str, request: ContentGenerationRequest) -> float:
        """計算品質評分"""
        score = 8.0  # 基礎分數
        
        # 標題檢查
        if title:
            if 15 <= len(title) <= 25:
                score += 1.0
            if not any(keyword in title for keyword in ['##', '###', '【', '】', '標題：', 'KOL', '派別', '分析師']):
                score += 1.0
            if not any(keyword in title for keyword in ['投資建議', '風險提醒']):
                score += 0.5
        
        # 內容檢查
        if content:
            if len(content) >= request.target_length * 0.8:
                score += 0.5
            if request.stock_name in content or request.stock_id in content:
                score += 0.5
            if not content.count(request.stock_name) > 3:  # 避免重複提及
                score += 0.5
            if '張數' in content or '百萬' in content or '億' in content:
                score += 0.5
        
        return min(score, 10.0)
    
    def _calculate_personalization_score(self, content: str, kol_profile: Dict[str, Any]) -> float:
        """計算個人化評分"""
        score = 7.0  # 基礎分數
        
        # 檢查關鍵詞使用
        key_phrases = kol_profile.get('key_phrases', [])
        if key_phrases:
            used_phrases = sum(1 for phrase in key_phrases if phrase in content)
            score += min(used_phrases * 0.5, 2.0)
        
        # 檢查避免話題
        avoid_topics = kol_profile.get('avoid_topics', [])
        if avoid_topics:
            avoided_count = sum(1 for topic in avoid_topics if topic not in content)
            score += min(avoided_count * 0.3, 1.0)
        
        return min(score, 10.0)
    
    async def generate_multiple_content(self, requests: List[ContentGenerationRequest]) -> List[ContentGenerationResult]:
        """批量生成內容"""
        tasks = [self.generate_content(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾掉錯誤結果
        valid_results = []
        for result in results:
            if isinstance(result, ContentGenerationResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"內容生成失敗: {result}")
        
        return valid_results
