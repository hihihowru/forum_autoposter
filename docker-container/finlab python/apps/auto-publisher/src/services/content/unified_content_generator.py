#!/usr/bin/env python3
"""
統一內容生成引擎
解決batch create AI味問題，提供深度個人化和多樣性控制
"""

import os
import sys
import asyncio
import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.api_integration.openai_api_client import OpenAIAPIClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ContentStructureType(Enum):
    """內容結構類型"""
    NARRATIVE = "narrative"  # 敘述型
    ANALYTICAL = "analytical"  # 分析型
    INTERACTIVE = "interactive"  # 互動型
    STORYTELLING = "storytelling"  # 故事型
    DEBATE = "debate"  # 辯論型

class EmotionalTone(Enum):
    """情緒基調"""
    EXCITED = "excited"  # 興奮
    CAUTIOUS = "cautious"  # 謹慎
    CONFIDENT = "confident"  # 自信
    HUMOROUS = "humorous"  # 幽默
    SERIOUS = "serious"  # 嚴肅
    OPTIMISTIC = "optimistic"  # 樂觀

@dataclass
class KOLPersonaInsights:
    """KOL人設深度洞察"""
    personality_traits: List[str]
    communication_style: str
    expertise_areas: List[str]
    unique_expressions: List[str]
    interaction_patterns: List[str]
    emotional_range: List[str]
    personal_stories: List[str]
    technical_depth: str
    humor_style: str
    risk_tolerance: str

@dataclass
class RandomizationParams:
    """隨機化參數"""
    content_structure: ContentStructureType
    expression_style: str
    interaction_elements: List[str]
    timeline_context: str
    emotional_tone: EmotionalTone
    technical_depth: str
    personal_story_integration: bool
    humor_intensity: float
    question_ratio: float
    data_emphasis: str

@dataclass
class ContentGenerationRequest:
    """內容生成請求"""
    kol_profile: Dict[str, Any]
    trigger_data: Dict[str, Any]
    market_data: Dict[str, Any]
    topic_title: str
    topic_keywords: str
    stock_data: Optional[Dict[str, Any]] = None

class KOLPersonaAnalyzer:
    """KOL人設深度分析器"""
    
    def __init__(self):
        self.personality_mapping = {
            "技術派": {
                "traits": ["理性", "數據導向", "技術分析", "圖表解讀"],
                "communication": "直接、專業、技術性強",
                "expertise": ["技術分析", "圖表解讀", "指標分析"],
                "expressions": ["這根K棒", "支撐壓力", "黃金交叉", "背離"],
                "interactions": ["大家怎麼看", "技術面分析", "圖表說話"],
                "emotional_range": ["冷靜", "自信", "謹慎"],
                "stories": ["曾經靠技術分析翻身", "半夜盯圖到三點"],
                "technical_depth": "high",
                "humor_style": "技術梗",
                "risk_tolerance": "medium"
            },
            "總經派": {
                "traits": ["宏觀思維", "數據分析", "政策解讀", "理性"],
                "communication": "學術性、數據支撐、邏輯清晰",
                "expertise": ["總體經濟", "政策分析", "數據解讀"],
                "expressions": ["數據顯示", "統計表明", "模型預測", "相關性"],
                "interactions": ["合理嗎", "值得投資嗎", "該怎麼看"],
                "emotional_range": ["冷靜", "理性", "謹慎"],
                "stories": ["統計學博士", "曾在央行工作"],
                "technical_depth": "very_high",
                "humor_style": "學術梗",
                "risk_tolerance": "low"
            },
            "新聞派": {
                "traits": ["敏銳", "急躁", "快節奏", "資訊導向"],
                "communication": "快速、直接、情緒化",
                "expertise": ["新聞分析", "趨勢解讀", "即時資訊"],
                "expressions": ["爆新聞啦", "風向轉了", "快訊", "先卡位"],
                "interactions": ["跟上", "快留言", "有人知道嗎"],
                "emotional_range": ["興奮", "急躁", "樂觀"],
                "stories": ["半夜盯彭博", "提前爆料被推爆"],
                "technical_depth": "low",
                "humor_style": "網路梗",
                "risk_tolerance": "high"
            },
            "籌碼派": {
                "traits": ["嘲諷", "幽默", "散戶視角", "實戰經驗"],
                "communication": "嘲諷幽默、邊嘴邊提醒",
                "expertise": ["籌碼分析", "券商進出", "三大法人"],
                "expressions": ["被倒貨啦", "三大法人又賣", "散戶GG"],
                "interactions": ["幫解讀", "看不懂法人在幹嘛"],
                "emotional_range": ["嘲諷", "幽默", "無奈"],
                "stories": ["當沖爆掉", "靠分析籌碼翻身"],
                "technical_depth": "medium",
                "humor_style": "嘲諷梗",
                "risk_tolerance": "medium"
            }
        }
    
    def analyze_kol(self, kol_profile: Dict[str, Any]) -> KOLPersonaInsights:
        """深度分析KOL人設"""
        persona = kol_profile.get('persona', '技術派')
        base_profile = self.personality_mapping.get(persona, self.personality_mapping['技術派'])
        
        # 添加個人化元素
        nickname = kol_profile.get('nickname', '')
        personal_elements = self._extract_personal_elements(nickname, persona)
        
        return KOLPersonaInsights(
            personality_traits=base_profile['traits'] + personal_elements['traits'],
            communication_style=base_profile['communication'],
            expertise_areas=base_profile['expertise'] + personal_elements['expertise'],
            unique_expressions=base_profile['expressions'] + personal_elements['expressions'],
            interaction_patterns=base_profile['interactions'] + personal_elements['interactions'],
            emotional_range=base_profile['emotional_range'] + personal_elements['emotions'],
            personal_stories=base_profile['stories'] + personal_elements['stories'],
            technical_depth=base_profile['technical_depth'],
            humor_style=base_profile['humor_style'],
            risk_tolerance=base_profile['risk_tolerance']
        )
    
    def _extract_personal_elements(self, nickname: str, persona: str) -> Dict[str, List[str]]:
        """提取個人化元素"""
        # 根據暱稱和角色提取個人特色
        personal_elements = {
            'traits': [],
            'expertise': [],
            'expressions': [],
            'interactions': [],
            'emotions': [],
            'stories': []
        }
        
        # 基於暱稱的個人化
        if '川' in nickname:
            personal_elements['expressions'].extend(['川普插三劍', '穩了啦'])
            personal_elements['stories'].append('川川哥的投資哲學')
        elif '韭' in nickname:
            personal_elements['expressions'].extend(['韭菜收割', '被割了'])
            personal_elements['interactions'].extend(['別被割', '小心陷阱'])
        elif '梅川' in nickname:
            personal_elements['expressions'].extend(['梅川褲子', '褲子掉了'])
            personal_elements['humor_style'] = '諧音梗'
        
        return personal_elements

class MultiDimensionalRandomizer:
    """多維度隨機化引擎"""
    
    def __init__(self):
        self.structure_templates = {
            ContentStructureType.NARRATIVE: [
                "開場描述 → 深入分析 → 個人觀點 → 互動結尾",
                "數據開頭 → 故事展開 → 專業分析 → 幽默結尾",
                "疑問開場 → 逐步解答 → 深度洞察 → 討論引導"
            ],
            ContentStructureType.ANALYTICAL: [
                "數據呈現 → 技術分析 → 基本面分析 → 風險提醒",
                "市場背景 → 個股分析 → 同業比較 → 投資建議",
                "趨勢觀察 → 原因分析 → 影響評估 → 後市展望"
            ],
            ContentStructureType.INTERACTIVE: [
                "問題開場 → 數據支撐 → 觀點分享 → 討論邀請",
                "情境設定 → 分析過程 → 結論分享 → 互動引導",
                "熱點關注 → 個人看法 → 經驗分享 → 交流邀請"
            ],
            ContentStructureType.STORYTELLING: [
                "故事開場 → 市場連結 → 深度分析 → 啟發結尾",
                "個人經歷 → 市場觀察 → 專業分析 → 經驗分享",
                "歷史回顧 → 現況分析 → 未來展望 → 智慧總結"
            ],
            ContentStructureType.DEBATE: [
                "觀點提出 → 論據支撐 → 反駁思考 → 結論分享",
                "爭議話題 → 多角度分析 → 個人立場 → 討論邀請",
                "市場分歧 → 各方觀點 → 個人判斷 → 辯論引導"
            ]
        }
        
        self.expression_styles = [
            "直白直接", "委婉含蓄", "幽默風趣", "專業嚴謹", "親切自然"
        ]
        
        self.interaction_elements = [
            "疑問句", "經驗分享", "數據引用", "個人觀點", "討論邀請",
            "幽默調侃", "專業建議", "風險提醒", "機會提示", "情感共鳴"
        ]
    
    def generate_params(self, kol_insights: KOLPersonaInsights) -> RandomizationParams:
        """生成隨機化參數"""
        
        # 根據KOL特色選擇適合的結構類型
        suitable_structures = self._get_suitable_structures(kol_insights)
        content_structure = random.choice(suitable_structures)
        
        # 根據KOL情緒範圍選擇基調
        emotional_tone = random.choice([
            EmotionalTone.EXCITED, EmotionalTone.CONFIDENT, 
            EmotionalTone.HUMOROUS, EmotionalTone.OPTIMISTIC
        ])
        
        # 隨機化其他參數
        expression_style = random.choice(self.expression_styles)
        interaction_elements = random.sample(self.interaction_elements, random.randint(2, 4))
        
        # 根據KOL特色調整技術深度
        technical_depth = self._adjust_technical_depth(kol_insights.technical_depth)
        
        # 個人故事整合機率
        personal_story_integration = random.random() < 0.3
        
        # 幽默強度
        humor_intensity = random.uniform(0.3, 0.8) if kol_insights.humor_style else 0.1
        
        # 問題比例
        question_ratio = random.uniform(0.2, 0.6)
        
        # 數據強調程度
        data_emphasis = random.choice(["high", "medium", "low"])
        
        return RandomizationParams(
            content_structure=content_structure,
            expression_style=expression_style,
            interaction_elements=interaction_elements,
            timeline_context=self._generate_timeline_context(),
            emotional_tone=emotional_tone,
            technical_depth=technical_depth,
            personal_story_integration=personal_story_integration,
            humor_intensity=humor_intensity,
            question_ratio=question_ratio,
            data_emphasis=data_emphasis
        )
    
    def _get_suitable_structures(self, kol_insights: KOLPersonaInsights) -> List[ContentStructureType]:
        """根據KOL特色選擇適合的結構類型"""
        suitable = []
        
        if "理性" in kol_insights.personality_traits:
            suitable.extend([ContentStructureType.ANALYTICAL, ContentStructureType.DEBATE])
        
        if "幽默" in kol_insights.personality_traits or "嘲諷" in kol_insights.personality_traits:
            suitable.extend([ContentStructureType.STORYTELLING, ContentStructureType.INTERACTIVE])
        
        if "急躁" in kol_insights.personality_traits or "快速" in kol_insights.personality_traits:
            suitable.extend([ContentStructureType.INTERACTIVE, ContentStructureType.NARRATIVE])
        
        # 確保至少有一種結構
        if not suitable:
            suitable = [ContentStructureType.NARRATIVE]
        
        return suitable
    
    def _adjust_technical_depth(self, base_depth: str) -> str:
        """調整技術深度"""
        depth_levels = ["low", "medium", "high", "very_high"]
        current_index = depth_levels.index(base_depth)
        
        # 隨機調整，但保持在合理範圍內
        adjustment = random.randint(-1, 1)
        new_index = max(0, min(len(depth_levels) - 1, current_index + adjustment))
        
        return depth_levels[new_index]
    
    def _generate_timeline_context(self) -> str:
        """生成時間線上下文"""
        contexts = [
            "盤中觀察", "收盤總結", "隔夜思考", "週末反思", 
            "月初展望", "月中檢視", "月底回顧", "即時分析"
        ]
        return random.choice(contexts)

class ContentQualityController:
    """內容品質控制檢查器"""
    
    def __init__(self):
        self.ai_patterns = [
            "首先", "然後", "最後", "總而言之", "綜上所述",
            "各位小伙伴們", "大家好", "今天我們來聊聊",
            "###", "##", "**", "📰", "📈", "💰"
        ]
        
        self.personalization_indicators = [
            "個人經驗", "我的看法", "我覺得", "我認為",
            "曾經", "之前", "那時候", "記得"
        ]
    
    async def optimize_content(self, content: str, kol_insights: KOLPersonaInsights) -> str:
        """優化內容品質"""
        
        # 1. 移除AI生成痕跡
        content = self._remove_ai_patterns(content)
        
        # 2. 增強個人化元素
        content = self._enhance_personalization(content, kol_insights)
        
        # 3. 優化互動元素
        content = self._optimize_interactions(content, kol_insights)
        
        # 4. 調整語氣和風格
        content = self._adjust_tone(content, kol_insights)
        
        return content
    
    def _remove_ai_patterns(self, content: str) -> str:
        """移除AI生成痕跡"""
        for pattern in self.ai_patterns:
            content = content.replace(pattern, "")
        
        # 移除過多的標點符號
        content = content.replace("...", "…")
        content = content.replace("!!!", "!")
        
        return content.strip()
    
    def _enhance_personalization(self, content: str, kol_insights: KOLPersonaInsights) -> str:
        """增強個人化元素"""
        
        # 添加個人化表達
        if random.random() < 0.3:  # 30%機率添加個人化元素
            personal_expression = random.choice(kol_insights.unique_expressions)
            if personal_expression not in content:
                content = f"{personal_expression}，{content}"
        
        # 添加個人故事
        if random.random() < 0.2:  # 20%機率添加個人故事
            story = random.choice(kol_insights.personal_stories)
            content = f"記得{story}，{content}"
        
        return content
    
    def _optimize_interactions(self, content: str, kol_insights: KOLPersonaInsights) -> str:
        """優化互動元素"""
        
        # 確保有互動元素
        interaction_count = sum(1 for pattern in kol_insights.interaction_patterns if pattern in content)
        
        if interaction_count == 0:
            # 添加互動元素
            interaction = random.choice(kol_insights.interaction_patterns)
            content = f"{content}\n\n{interaction}？"
        
        return content
    
    def _adjust_tone(self, content: str, kol_insights: KOLPersonaInsights) -> str:
        """調整語氣和風格"""
        
        # 根據KOL特色調整語氣
        if "幽默" in kol_insights.personality_traits:
            # 添加幽默元素
            humor_expressions = ["笑死", "真的假的", "太扯了", "這什麼鬼"]
            if random.random() < 0.3:
                humor = random.choice(humor_expressions)
                content = content.replace("。", f"，{humor}。", 1)
        
        return content

class UnifiedContentGenerator:
    """統一內容生成引擎"""
    
    def __init__(self):
        self.openai_client = OpenAIAPIClient()
        self.kol_analyzer = KOLPersonaAnalyzer()
        self.randomizer = MultiDimensionalRandomizer()
        self.quality_controller = ContentQualityController()
        
        logger.info("統一內容生成引擎初始化完成")
    
    async def generate_content(self, request: ContentGenerationRequest) -> Dict[str, Any]:
        """生成統一高品質內容"""
        
        try:
            logger.info(f"🎯 開始為 {request.kol_profile.get('nickname')} 生成內容")
            
            # 1. 深度KOL分析
            kol_insights = self.kol_analyzer.analyze_kol(request.kol_profile)
            logger.info(f"📊 KOL分析完成: {kol_insights.communication_style}")
            
            # 2. 多維度隨機化
            randomization_params = self.randomizer.generate_params(kol_insights)
            logger.info(f"🎲 隨機化參數: {randomization_params.content_structure.value}")
            
            # 3. 生成個人化Prompt
            system_prompt, user_prompt = self._build_personalized_prompts(
                request, kol_insights, randomization_params
            )
            
            # 4. 調用OpenAI API
            content = await self._call_openai_api(system_prompt, user_prompt, randomization_params)
            
            # 5. 品質控制優化
            optimized_content = await self.quality_controller.optimize_content(content, kol_insights)
            
            # 6. 生成標題
            title = await self._generate_title(request, kol_insights, randomization_params)
            
            logger.info(f"✅ 內容生成完成: {len(optimized_content)}字")
            
            return {
                "title": title,
                "content": optimized_content,
                "kol_insights": kol_insights,
                "randomization_params": randomization_params,
                "generation_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "content_length": len(optimized_content),
                    "personalization_score": self._calculate_personalization_score(optimized_content, kol_insights),
                    "interaction_score": self._calculate_interaction_score(optimized_content)
                }
            }
            
        except Exception as e:
            logger.error(f"內容生成失敗: {e}")
            return None
    
    def _build_personalized_prompts(self, request: ContentGenerationRequest, 
                                  kol_insights: KOLPersonaInsights,
                                  randomization_params: RandomizationParams) -> Tuple[str, str]:
        """建構個人化Prompt"""
        
        # 系統Prompt
        system_prompt = f"""你是{request.kol_profile.get('nickname')}，一個{kol_insights.communication_style}的投資分析師。

個人特色：
- 性格特質：{', '.join(kol_insights.personality_traits)}
- 專業領域：{', '.join(kol_insights.expertise_areas)}
- 獨特表達：{', '.join(kol_insights.unique_expressions)}
- 互動風格：{', '.join(kol_insights.interaction_patterns)}
- 幽默風格：{kol_insights.humor_style}
- 技術深度：{kol_insights.technical_depth}

寫作要求：
1. 完全按照你的個人風格和表達習慣
2. 避免AI生成痕跡，要像真人發文
3. 要有個人觀點和經驗分享
4. 適當使用幽默和互動元素
5. 保持專業性的同時要有親和力
6. 不要使用制式化的開頭和結尾
7. 避免使用markdown格式和特殊符號
8. 內容要自然流暢，像在跟朋友聊天"""

        # 用戶Prompt
        user_prompt = f"""請為以下內容寫一篇貼文：

主題：{request.topic_title}
關鍵詞：{request.topic_keywords}

內容結構：{randomization_params.content_structure.value}
表達風格：{randomization_params.expression_style}
情緒基調：{randomization_params.emotional_tone.value}
技術深度：{randomization_params.technical_depth}
時間線：{randomization_params.timeline_context}

特殊要求：
- 互動元素：{', '.join(randomization_params.interaction_elements)}
- 個人故事整合：{'是' if randomization_params.personal_story_integration else '否'}
- 幽默強度：{randomization_params.humor_intensity}
- 問題比例：{randomization_params.question_ratio}

請用你的風格寫一篇自然、有趣、有深度的貼文，避免AI味，要像真人發文。"""

        return system_prompt, user_prompt
    
    async def _call_openai_api(self, system_prompt: str, user_prompt: str, 
                             randomization_params: RandomizationParams) -> str:
        """調用OpenAI API"""
        
        try:
            # 使用現有的OpenAI客戶端
            response = await self.openai_client.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model="gpt-4o",
                temperature=0.7 + (randomization_params.humor_intensity * 0.3),
                max_tokens=800 if randomization_params.content_structure == ContentStructureType.INTERACTIVE else 1000
            )
            
            return response
            
        except Exception as e:
            logger.error(f"OpenAI API調用失敗: {e}")
            return "內容生成失敗，請稍後再試。"
    
    async def _generate_title(self, request: ContentGenerationRequest, 
                            kol_insights: KOLPersonaInsights,
                            randomization_params: RandomizationParams) -> str:
        """生成個人化標題"""
        
        title_templates = [
            f"🎯 {request.topic_title} - {random.choice(kol_insights.unique_expressions)}",
            f"💡 {random.choice(kol_insights.interaction_patterns)} - {request.topic_title}",
            f"🚀 {randomization_params.timeline_context} - {request.topic_title}",
            f"📊 {request.topic_title} - {random.choice(kol_insights.personality_traits)}分析",
            f"⚡ {request.topic_title} - {random.choice(kol_insights.unique_expressions)}"
        ]
        
        return random.choice(title_templates)
    
    def _calculate_personalization_score(self, content: str, kol_insights: KOLPersonaInsights) -> float:
        """計算個人化分數"""
        score = 0.0
        
        # 檢查個人化指標
        for indicator in self.quality_controller.personalization_indicators:
            if indicator in content:
                score += 0.1
        
        # 檢查KOL獨特表達
        for expression in kol_insights.unique_expressions:
            if expression in content:
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_interaction_score(self, content: str) -> float:
        """計算互動分數"""
        interaction_indicators = ["？", "大家", "你們", "怎麼看", "覺得", "認為"]
        score = 0.0
        
        for indicator in interaction_indicators:
            score += content.count(indicator) * 0.1
        
        return min(score, 1.0)

# 工廠函數
def create_unified_content_generator() -> UnifiedContentGenerator:
    """創建統一內容生成器實例"""
    return UnifiedContentGenerator()

if __name__ == "__main__":
    # 測試用例
    async def test_generator():
        generator = create_unified_content_generator()
        
        request = ContentGenerationRequest(
            kol_profile={
                "nickname": "川川哥",
                "persona": "技術派"
            },
            trigger_data={"type": "limit_up"},
            market_data={"stock": "2330"},
            topic_title="台積電漲停分析",
            topic_keywords="台積電,漲停,技術分析"
        )
        
        result = await generator.generate_content(request)
        if result:
            print(f"標題: {result['title']}")
            print(f"內容: {result['content']}")
            print(f"個人化分數: {result['generation_metadata']['personalization_score']}")
            print(f"互動分數: {result['generation_metadata']['interaction_score']}")
    
    asyncio.run(test_generator())
