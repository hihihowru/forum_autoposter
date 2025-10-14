#!/usr/bin/env python3
"""
品質檢查標準 Backlog
定義內容品質檢查的具體標準和實現計劃
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class QualityCheckType(Enum):
    """品質檢查類型"""
    TITLE_CHECK = "title_check"
    CONTENT_CHECK = "content_check"
    STOCK_MENTION_CHECK = "stock_mention_check"
    FORMATTING_CHECK = "formatting_check"
    PERSONALIZATION_CHECK = "personalization_check"

@dataclass
class QualityIssue:
    """品質問題"""
    check_type: QualityCheckType
    description: str
    severity: str  # "high", "medium", "low"
    suggestion: str

class QualityCheckStandards:
    """品質檢查標準"""
    
    @staticmethod
    def get_title_check_standards() -> Dict[str, Any]:
        """標題檢查標準"""
        return {
            "forbidden_keywords": [
                "KOL", "派別", "分析師", "專家", "大師",
                "batch", "批量", "自動", "機器人"
            ],
            "required_length": (10, 50),
            "forbidden_patterns": [
                r"【.*KOL.*】",
                r"【.*派別.*】",
                r"【.*分析師.*】"
            ],
            "required_elements": [
                "股票名稱或代號",
                "分析重點"
            ]
        }
    
    @staticmethod
    def get_content_check_standards() -> Dict[str, Any]:
        """內容檢查標準"""
        return {
            "forbidden_patterns": [
                r"根據.*分析.*",
                r"從.*角度.*",
                r"基於.*數據.*",
                r"根據.*顯示.*"
            ],
            "required_elements": [
                "實質分析內容",
                "數據支持",
                "投資觀點"
            ],
            "forbidden_repetitions": [
                "重複的模板化語言",
                "過度使用相同詞彙",
                "機械化的表達方式"
            ],
            "min_content_length": 100,
            "max_content_length": 800
        }
    
    @staticmethod
    def get_stock_mention_check_standards() -> Dict[str, Any]:
        """股票提及檢查標準"""
        return {
            "mention_rules": [
                "股票名稱和代號只能提到其中一個",
                "股票代號使用純數字格式",
                "避免重複提及同一支股票",
                "股票提及要自然融入內容"
            ],
            "forbidden_patterns": [
                r"股票代號.*股票名稱",
                r"股票名稱.*股票代號"
            ],
            "max_mentions": 3
        }
    
    @staticmethod
    def get_formatting_check_standards() -> Dict[str, Any]:
        """格式檢查標準"""
        return {
            "emoji_usage": {
                "max_emoji_count": 5,
                "required_emojis": ["📊", "📈", "📰"],
                "forbidden_emojis": ["🤖", "⚙️", "🔧"]
            },
            "paragraph_structure": {
                "max_sentence_length": 50,
                "min_paragraph_length": 20,
                "max_paragraph_length": 200
            },
            "punctuation": {
                "required_punctuation": [".", "，", "！"],
                "forbidden_punctuation": ["...", "!!!", "???"]
            }
        }
    
    @staticmethod
    def get_personalization_check_standards() -> Dict[str, Any]:
        """個人化檢查標準"""
        return {
            "kol_style_requirements": [
                "符合 KOL 的人設風格",
                "使用 KOL 的關鍵詞",
                "避免 KOL 不喜歡的話題",
                "語氣要符合 KOL 特色"
            ],
            "style_indicators": [
                "個人化表達",
                "獨特觀點",
                "風格一致性"
            ]
        }

class QualityCheckImplementation:
    """品質檢查實現計劃"""
    
    @staticmethod
    def get_implementation_phases() -> List[Dict[str, Any]]:
        """實現階段"""
        return [
            {
                "phase": 1,
                "name": "基礎檢查",
                "checks": [
                    QualityCheckType.TITLE_CHECK,
                    QualityCheckType.STOCK_MENTION_CHECK
                ],
                "priority": "high",
                "estimated_time": "1-2 days"
            },
            {
                "phase": 2,
                "name": "內容品質檢查",
                "checks": [
                    QualityCheckType.CONTENT_CHECK,
                    QualityCheckType.FORMATTING_CHECK
                ],
                "priority": "medium",
                "estimated_time": "2-3 days"
            },
            {
                "phase": 3,
                "name": "個人化檢查",
                "checks": [
                    QualityCheckType.PERSONALIZATION_CHECK
                ],
                "priority": "low",
                "estimated_time": "3-5 days"
            }
        ]
    
    @staticmethod
    def get_check_functions() -> Dict[QualityCheckType, str]:
        """檢查函數映射"""
        return {
            QualityCheckType.TITLE_CHECK: "check_title_quality",
            QualityCheckType.CONTENT_CHECK: "check_content_quality",
            QualityCheckType.STOCK_MENTION_CHECK: "check_stock_mentions",
            QualityCheckType.FORMATTING_CHECK: "check_formatting",
            QualityCheckType.PERSONALIZATION_CHECK: "check_personalization"
        }

class QualityCheckExamples:
    """品質檢查範例"""
    
    @staticmethod
    def get_bad_examples() -> List[Dict[str, str]]:
        """不好的範例"""
        return [
            {
                "title": "【KOL分析師】6732股票分析",
                "content": "根據數據分析顯示，6732股票今日表現亮眼。從技術面角度來看，6732股票具有投資價值。",
                "issues": [
                    "標題提到KOL分析師",
                    "內容過於制式化",
                    "重複提及股票代號"
                ]
            },
            {
                "title": "昇佳電子股票分析報告",
                "content": "昇佳電子(6732)今日漲停，昇佳電子基本面強勁，昇佳電子未來看好。",
                "issues": [
                    "重複提及股票名稱",
                    "內容單調",
                    "缺乏實質分析"
                ]
            }
        ]
    
    @staticmethod
    def get_good_examples() -> List[Dict[str, str]]:
        """好的範例"""
        return [
            {
                "title": "昇佳電子月營收亮眼！年增25%",
                "content": "昇佳電子今日漲停，月營收表現亮眼！\n\n📊 營收數據：\n• 年增率：25%\n• 月增率：8.5%\n• 營收趨勢：upward\n\n營運動能強勁，顯示公司基本面穩健，值得投資人關注。",
                "strengths": [
                    "標題吸引人且不提到KOL",
                    "內容自然流暢",
                    "包含實質數據",
                    "使用適當表情符號"
                ]
            },
            {
                "title": "6732技術分析：大漲9.8%",
                "content": "6732今日大漲9.8%！\n\n📊 技術數據：\n• 漲幅：9.8%\n• 成交量比：1.875倍\n• RSI：65.2\n• MACD：bullish\n\n技術指標顯示多頭趨勢，成交量放大支撐上漲動能。",
                "strengths": [
                    "標題簡潔明確",
                    "只使用股票代號",
                    "包含技術分析",
                    "結構清晰"
                ]
            }
        ]

# 品質檢查標準總結
QUALITY_CHECK_SUMMARY = {
    "title_standards": {
        "不能提到": ["KOL name", "派別", "分析師"],
        "必須包含": ["股票名稱或代號", "分析重點"],
        "長度要求": "10-50字"
    },
    "content_standards": {
        "不能": ["制式化語言", "重複模板", "機械化表達"],
        "必須": ["實質分析", "數據支持", "投資觀點"],
        "長度要求": "100-800字"
    },
    "stock_mention_standards": {
        "規則": ["名稱和代號只能提到其中一個", "代號使用純數字", "避免重複提及"],
        "最大提及次數": 3
    },
    "formatting_standards": {
        "表情符號": "最多5個，必須包含📊📈📰",
        "段落結構": "句子不超過50字，段落20-200字",
        "標點符號": "使用正確的標點符號"
    },
    "personalization_standards": {
        "要求": ["符合KOL人設", "使用關鍵詞", "避免不喜歡話題", "語氣符合特色"]
    }
}

























