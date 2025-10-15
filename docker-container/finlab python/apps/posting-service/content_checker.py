import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import openai
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentChecker:
    """智能內容檢查和修復器"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        load_dotenv('../../../../.env')
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if self.api_key:
            # 清除可能的代理設置
            for key in list(os.environ.keys()):
                if 'proxy' in key.lower():
                    del os.environ[key]
            
            openai.api_key = self.api_key
            logger.info(f"Content Checker 初始化完成，使用模型: {self.model}")
        else:
            logger.warning("OPENAI_API_KEY 未設定，將使用基本檢查")
    
    def check_and_fix_content(self, content: str, stock_name: str, stock_code: str, 
                             kol_persona: str = "technical", kol_serial: str = None) -> Dict[str, Any]:
        """檢查並修復內容"""
        
        try:
            # 1. 基本格式檢查
            basic_issues = self._check_basic_format(content)
            
            # 2. 如果有 API Key，使用 LLM 進行深度修復和個人化調整
            if self.api_key:
                fixed_content = self._llm_fix_and_personalize_content(
                    content, stock_name, stock_code, basic_issues, kol_persona, kol_serial
                )
                return {
                    "original_content": content,
                    "fixed_content": fixed_content,
                    "issues_found": basic_issues,
                    "fix_method": "llm_enhanced_personalized",
                    "success": True
                }
            else:
                # 3. 基本修復
                fixed_content = self._basic_fix_content(content)
                return {
                    "original_content": content,
                    "fixed_content": fixed_content,
                    "issues_found": basic_issues,
                    "fix_method": "basic",
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Content Checker 處理失敗: {e}")
            return {
                "original_content": content,
                "fixed_content": content,
                "issues_found": [],
                "fix_method": "none",
                "success": False,
                "error": str(e)
            }
    
    def _check_basic_format(self, content: str) -> list:
        """檢查基本格式問題"""
        issues = []
        
        # 檢查 emoji
        emoji_pattern = r'[📰📊⚠️🚀✅❌🔍💡🎯📝🔑🤖]'
        if re.search(emoji_pattern, content):
            issues.append("contains_emoji")
        
        # 檢查 Markdown 格式
        markdown_patterns = [
            r'\*\*[^*]+\*\*',  # **bold**
            r'##\s+',          # ## headers
            r'###\s+',         # ### headers
            r'\[([^\]]+)\]\([^)]+\)'  # [link](url)
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, content):
                issues.append("contains_markdown")
                break
        
        # 檢查新聞摘要格式
        if "【新聞摘要】" in content or "相關新聞：" in content:
            issues.append("contains_news_summary")
        
        # 檢查新聞來源
        if "新聞來源" in content or "閱讀更多" in content:
            issues.append("contains_news_sources")
        
        return issues
    
    def _basic_fix_content(self, content: str) -> str:
        """基本格式修復"""
        fixed = content
        
        # 移除 emoji
        emoji_pattern = r'[📰📊⚠️🚀✅❌🔍💡🎯📝🔑🤖]'
        fixed = re.sub(emoji_pattern, '', fixed)
        
        # 移除 Markdown 格式
        fixed = re.sub(r'\*\*([^*]+)\*\*', r'\1', fixed)  # **bold** -> bold
        fixed = re.sub(r'##\s+', '', fixed)  # ## headers
        fixed = re.sub(r'###\s+', '', fixed)  # ### headers
        
        # 移除連結格式
        fixed = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', fixed)
        
        # 清理多餘空白
        fixed = re.sub(r'\n\s*\n\s*\n', '\n\n', fixed)
        fixed = fixed.strip()
        
        return fixed
    
    def _get_kol_personality_profile(self, kol_serial: str, kol_persona: str) -> Dict[str, Any]:
        """獲取 KOL 個人化設定"""
        
        # KOL 個人化設定資料庫
        kol_profiles = {
            "150": {
                "name": "川川哥",
                "persona": "技術派",
                "style": {
                    "tone": "直接但有料，有時狂妄，有時碎碎念",
                    "punctuation": "大量使用省略號，不愛標點符號",
                    "vocabulary": ["黃金交叉", "均線糾結", "三角收斂", "K棒爆量", "跳空缺口", "支撐帶", "壓力線", "MACD背離"],
                    "casual_expressions": ["穩了啦", "爆啦", "嘎到", "要噴啦", "破線啦", "睡醒漲停"],
                    "ending_style": "想知道的話，留言告訴我，咱們一起討論一下..."
                }
            },
            "151": {
                "name": "韭割哥",
                "persona": "基本面",
                "style": {
                    "tone": "理性分析，數據導向",
                    "punctuation": "標準標點符號",
                    "vocabulary": ["營收成長", "獲利能力", "產業前景", "競爭優勢", "估值合理"],
                    "casual_expressions": ["值得關注", "前景看好", "風險可控"],
                    "ending_style": "投資有風險，請謹慎評估"
                }
            },
            "152": {
                "name": "消息面達人",
                "persona": "news_driven",
                "style": {
                    "tone": "敏銳洞察，快速反應",
                    "punctuation": "感嘆號較多",
                    "vocabulary": ["政策利多", "市場情緒", "資金流向", "題材發酵"],
                    "casual_expressions": ["重磅消息", "市場炸鍋", "資金湧入"],
                    "ending_style": "持續關注後續發展"
                }
            }
        }
        
        # 預設設定
        default_profile = {
            "name": f"KOL-{kol_serial}",
            "persona": kol_persona,
            "style": {
                "tone": "專業客觀",
                "punctuation": "標準標點符號",
                "vocabulary": [],
                "casual_expressions": [],
                "ending_style": "投資有風險，請謹慎評估"
            }
        }
        
        return kol_profiles.get(kol_serial, default_profile)
    
    def _llm_fix_and_personalize_content(self, content: str, stock_name: str, stock_code: str, 
                                        issues: list, kol_persona: str, kol_serial: str) -> str:
        """使用 LLM 進行深度內容修復和個人化調整"""
        
        # 獲取 KOL 個人化設定
        kol_profile = self._get_kol_personality_profile(kol_serial, kol_persona)
        
        issues_desc = {
            "contains_emoji": "包含表情符號",
            "contains_markdown": "包含 Markdown 格式",
            "contains_news_summary": "包含新聞摘要",
            "contains_news_sources": "包含新聞來源連結"
        }
        
        issues_text = "、".join([issues_desc.get(issue, issue) for issue in issues])
        
        # 構建個人化提示
        personalization_guide = f"""
KOL 個人化設定：
- 名稱：{kol_profile['name']}
- 人設：{kol_profile['persona']}
- 語氣風格：{kol_profile['style']['tone']}
- 標點符號風格：{kol_profile['style']['punctuation']}
- 專業詞彙：{', '.join(kol_profile['style']['vocabulary'][:5])}
- 口語表達：{', '.join(kol_profile['style']['casual_expressions'][:3])}
- 結尾風格：{kol_profile['style']['ending_style']}
"""
        
        prompt = f"""
請修復以下股票分析內容的格式問題，並根據 KOL 個人化設定調整內容風格：

股票：{stock_name}({stock_code})
發現的問題：{issues_text}

{personalization_guide}

原始內容：
{content}

修復和個人化要求：
1. 移除所有表情符號 (emoji)
2. 移除所有 Markdown 格式 (**、##、###、[連結](url) 等)
3. 移除新聞摘要部分（【新聞摘要】、相關新聞：等）
4. 移除新聞來源連結部分
5. 只保留結構化分析部分：
   - 漲停原因分析
   - 題材面
   - 基本面
   - 技術面
   - 籌碼面
   - 操作建議
   - 風險提醒
6. 根據 KOL 個人化設定調整內容風格：
   - 使用 {kol_profile['name']} 的語氣和表達方式
   - 採用 {kol_profile['style']['punctuation']} 的標點符號風格
   - 適當使用專業詞彙和口語表達
   - 結尾使用 {kol_profile['style']['ending_style']}
7. 保持內容的專業性和可讀性
8. 確保內容長度適中（800-1200字）
9. 使用純文字格式，只使用換行符分隔

請直接輸出修復和個人化後的內容，不要包含額外的說明。
"""
        
        try:
            # 清除可能的代理設置
            import os
            for key in list(os.environ.keys()):
                if 'proxy' in key.lower():
                    del os.environ[key]
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是{kol_profile['name']}，一個專業的股票分析內容修復專家，專門處理格式問題並調整個人化風格。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            fixed_content = response.choices[0].message.content.strip()
            logger.info(f"LLM 內容修復完成，長度: {len(fixed_content)} 字")
            return fixed_content
            
        except Exception as e:
            logger.error(f"LLM 內容修復失敗: {e}")
            return self._basic_fix_content(content)
    
    def enhance_content_quality(self, content: str, stock_name: str, stock_code: str, 
                               kol_persona: str = "technical") -> Dict[str, Any]:
        """使用 LLM 提升內容質量"""
        
        if not self.api_key:
            return {
                "original_content": content,
                "enhanced_content": content,
                "enhancement_method": "none",
                "success": False,
                "error": "No API key available"
            }
        
        persona_instructions = {
            "technical": "技術分析專家，專注於技術指標、圖表形態、成交量分析",
            "fundamental": "基本面分析專家，專注於財務數據、產業前景、競爭優勢",
            "news_driven": "消息面分析專家，專注於新聞事件、政策變化、市場情緒",
            "mixed": "綜合分析專家，平衡技術面、基本面、消息面分析"
        }
        
        persona_desc = persona_instructions.get(kol_persona, "綜合分析專家")
        
        prompt = f"""
請優化以下股票分析內容，使其更加專業和有說服力：

股票：{stock_name}({stock_code})
KOL 人設：{persona_desc}

原始內容：
{content}

優化要求：
1. 保持原有的結構化分析格式
2. 提升內容的專業性和深度
3. 增強分析的邏輯性和說服力
4. 優化語言表達，使其更加生動有趣
5. 確保內容符合 {persona_desc} 的風格
6. 保持內容長度在 800-1200 字
7. 移除任何格式問題（emoji、Markdown 等）
8. 確保內容適合 Cmoney 平台發布

請直接輸出優化後的內容，不要包含額外的說明。
"""
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是一個專業的股票分析內容優化專家，專精於 {persona_desc}。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            enhanced_content = response.choices[0].message.content.strip()
            logger.info(f"內容質量提升完成，長度: {len(enhanced_content)} 字")
            
            return {
                "original_content": content,
                "enhanced_content": enhanced_content,
                "enhancement_method": "llm_enhanced",
                "success": True,
                "length_change": len(enhanced_content) - len(content)
            }
            
        except Exception as e:
            logger.error(f"內容質量提升失敗: {e}")
            return {
                "original_content": content,
                "enhanced_content": content,
                "enhancement_method": "none",
                "success": False,
                "error": str(e)
            }
