"""
話題分類服務
使用 OpenAI GPT 模型對話題進行自動分類
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from openai import OpenAI
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class TopicClassification:
    """話題分類結果"""
    topic_id: str
    title: str
    content: str
    
    # 人設標籤 (對應 KOL 人設)
    persona_tags: List[str]
    
    # 產業標籤
    industry_tags: List[str]
    
    # 事件標籤
    event_tags: List[str]
    
    # 股票相關標籤
    stock_tags: List[str]
    
    # 分類信心度
    confidence_score: float
    
    # 原始回應
    raw_response: Optional[Dict[str, Any]] = None

class TopicClassifier:
    """話題分類器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化分類器
        
        Args:
            api_key: OpenAI API 金鑰
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API 金鑰未設置")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # 模型配置
        self.model = "gpt-4o-mini"
        self.temperature = 0.3  # 較低溫度確保一致性
        self.max_tokens = 1000
        
        # 載入 KOL 分類配置
        self.kol_categories = self._load_kol_categories()
        
        logger.info("話題分類器初始化完成")
    
    def _load_kol_categories(self) -> Dict[str, Any]:
        """載入 KOL 分類配置"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 'config', 'kol_categories.json'
            )
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 提取分類名稱列表
            return {
                "persona_categories": [cat["name"] for cat in config["persona_categories"]],
                "industry_categories": [cat["name"] for cat in config["industry_categories"]],
                "event_categories": [cat["name"] for cat in config["event_categories"]],
                "stock_categories": [cat["name"] for cat in config["stock_categories"]],
                "full_config": config  # 保留完整配置供其他用途
            }
            
        except Exception as e:
            logger.warning(f"無法載入 KOL 分類配置，使用默認配置: {e}")
            return {
                "persona_categories": [
                    "技術派", "總經派", "新聞派", "籌碼派", 
                    "情緒派", "價值派", "消息派", "量化派"
                ],
                "industry_categories": [
                    "半導體", "金融", "傳產", "科技", "生技", 
                    "能源", "消費", "地產", "航運", "鋼鐵"
                ],
                "event_categories": [
                    "法說會", "財報", "月營收", "政策", "併購", 
                    "增資", "減資", "除權息", "股東會", "董事會"
                ],
                "stock_categories": [
                    "台積電", "聯發科", "鴻海", "中華電", "台塑",
                    "中鋼", "長榮", "陽明", "萬海", "富邦金"
                ]
            }
    
    def classify_topic(self, topic_id: str, title: str, content: str) -> TopicClassification:
        """
        對話題進行分類
        
        Args:
            topic_id: 話題ID
            title: 話題標題
            content: 話題內容
            
        Returns:
            分類結果
        """
        try:
            logger.info(f"開始分類話題: {title}")
            
            # 構建分類 prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(title, content)
            
            # 調用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # 解析回應
            result = json.loads(response.choices[0].message.content)
            
            # 創建分類結果
            classification = TopicClassification(
                topic_id=topic_id,
                title=title,
                content=content,
                persona_tags=result.get("persona_tags", []),
                industry_tags=result.get("industry_tags", []),
                event_tags=result.get("event_tags", []),
                stock_tags=result.get("stock_tags", []),
                confidence_score=result.get("confidence_score", 0.0),
                raw_response=result
            )
            
            logger.info(f"話題分類完成: {title} -> {classification.persona_tags}")
            return classification
            
        except Exception as e:
            logger.error(f"話題分類失敗: {e}")
            # 返回默認分類
            return self._create_default_classification(topic_id, title, content)
    
    def _build_system_prompt(self) -> str:
        """構建系統提示詞"""
        return f"""
你是一個專業的投資話題分類專家。你的任務是分析投資相關的話題，並將其分類到合適的標籤中。

## 分類標準

### 人設標籤 (persona_tags) - 對應 KOL 人設
{json.dumps(self.kol_categories["persona_categories"], ensure_ascii=False, indent=2)}

### 產業標籤 (industry_tags)
{json.dumps(self.kol_categories["industry_categories"], ensure_ascii=False, indent=2)}

### 事件標籤 (event_tags)
{json.dumps(self.kol_categories["event_categories"], ensure_ascii=False, indent=2)}

### 股票標籤 (stock_tags)
{json.dumps(self.kol_categories["stock_categories"], ensure_ascii=False, indent=2)}

## 分類規則

1. **人設標籤**：根據話題的分析角度和內容風格選擇
   - 技術派：涉及技術分析、圖表、指標
   - 總經派：涉及總體經濟、政策、利率
   - 新聞派：涉及新聞事件、突發消息
   - 籌碼派：涉及資金流向、主力動向
   - 情緒派：涉及市場情緒、投資心理
   - 價值派：涉及基本面、估值、長期投資
   - 消息派：涉及內幕消息、小道消息
   - 量化派：涉及數據分析、回測、模型

2. **產業標籤**：根據話題涉及的主要產業
3. **事件標籤**：根據話題涉及的事件類型
4. **股票標籤**：根據話題涉及的主要股票

## 輸出格式

請以 JSON 格式輸出分類結果：
```json
{{
    "persona_tags": ["技術派", "籌碼派"],
    "industry_tags": ["半導體"],
    "event_tags": ["法說會"],
    "stock_tags": ["台積電"],
    "confidence_score": 0.85
}}
```

## 注意事項

- 每個標籤類別可以選擇多個標籤
- 選擇最相關的標籤，不要過度標記
- confidence_score 範圍 0.0-1.0，表示分類信心度
- 如果話題不明確，可以選擇較少的標籤
"""
    
    def _build_user_prompt(self, title: str, content: str) -> str:
        """構建用戶提示詞"""
        return f"""
請分析以下投資話題並進行分類：

**標題**: {title}

**內容**: {content}

請根據上述分類標準，為這個話題選擇合適的標籤。
"""
    
    def _create_default_classification(self, topic_id: str, title: str, content: str) -> TopicClassification:
        """創建默認分類結果"""
        return TopicClassification(
            topic_id=topic_id,
            title=title,
            content=content,
            persona_tags=["新聞派"],  # 默認分類
            industry_tags=[],
            event_tags=[],
            stock_tags=[],
            confidence_score=0.1
        )
    
    def batch_classify(self, topics: List[Dict[str, str]]) -> List[TopicClassification]:
        """
        批量分類話題
        
        Args:
            topics: 話題列表，每個話題包含 id, title, content
            
        Returns:
            分類結果列表
        """
        results = []
        
        for topic in topics:
            try:
                classification = self.classify_topic(
                    topic_id=topic.get("id", ""),
                    title=topic.get("title", ""),
                    content=topic.get("content", "")
                )
                results.append(classification)
                
                # 避免 API 調用過於頻繁
                import time
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"批量分類失敗: {e}")
                continue
        
        logger.info(f"批量分類完成，處理了 {len(results)} 個話題")
        return results

# 工廠函數
def create_topic_classifier() -> TopicClassifier:
    """創建話題分類器實例"""
    return TopicClassifier()
