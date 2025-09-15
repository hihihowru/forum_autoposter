#!/usr/bin/env python3
"""
股票提及個人化管理器
為不同KOL角色定義不同的股票提及方式，避免統一的格式
"""

import os
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class StockMentionStyle:
    """股票提及風格設定"""
    primary_formats: List[str]  # 主要提及格式
    secondary_formats: List[str]  # 次要提及格式
    frequency_weights: Dict[str, float]  # 各格式的使用頻率權重
    context_modifiers: Dict[str, str]  # 上下文修飾詞

class StockMentionPersonalizer:
    """股票提及個人化管理器"""
    
    def __init__(self):
        # 定義不同KOL的股票提及風格
        self.kol_stock_styles = {
            "川川哥": StockMentionStyle(
                primary_formats=[
                    "{name}",
                    "{name}({code})",
                    "{code}",
                    "這檔{name}"
                ],
                secondary_formats=[
                    "{name}這檔",
                    "{code}這支",
                    "這支{name}",
                    "{name}這支"
                ],
                frequency_weights={
                    "{name}": 0.4,
                    "{name}({code})": 0.2,
                    "{code}": 0.3,
                    "這檔{name}": 0.1
                },
                context_modifiers={
                    "技術分析": "這檔{name}",
                    "新聞評論": "{name}({code})",
                    "一般提及": "{name}",
                    "強調": "{name}({code})"
                }
            ),
            
            "韭割哥": StockMentionStyle(
                primary_formats=[
                    "{name}",
                    "{name}這檔",
                    "這檔{name}",
                    "{code}"
                ],
                secondary_formats=[
                    "{name}({code})",
                    "這支{name}",
                    "{code}這支",
                    "{name}這支"
                ],
                frequency_weights={
                    "{name}": 0.5,
                    "{name}這檔": 0.2,
                    "這檔{name}": 0.2,
                    "{code}": 0.1
                },
                context_modifiers={
                    "技術分析": "{name}這檔",
                    "新聞評論": "{name}",
                    "一般提及": "{name}",
                    "強調": "{name}({code})"
                }
            ),
            
            "梅川褲子": StockMentionStyle(
                primary_formats=[
                    "{name}",
                    "{code}",
                    "{name}({code})",
                    "這檔{name}"
                ],
                secondary_formats=[
                    "{name}這檔",
                    "這支{name}",
                    "{code}這支",
                    "{name}這支"
                ],
                frequency_weights={
                    "{name}": 0.3,
                    "{code}": 0.4,
                    "{name}({code})": 0.2,
                    "這檔{name}": 0.1
                },
                context_modifiers={
                    "技術分析": "{code}",
                    "新聞評論": "{name}",
                    "一般提及": "{name}",
                    "強調": "{name}({code})"
                }
            ),
            
            "八卦護城河": StockMentionStyle(
                primary_formats=[
                    "{name}",
                    "{name}({code})",
                    "這檔{name}",
                    "{name}這檔"
                ],
                secondary_formats=[
                    "{code}",
                    "這支{name}",
                    "{code}這支",
                    "{name}這支"
                ],
                frequency_weights={
                    "{name}": 0.4,
                    "{name}({code})": 0.3,
                    "這檔{name}": 0.2,
                    "{name}這檔": 0.1
                },
                context_modifiers={
                    "技術分析": "{name}",
                    "新聞評論": "{name}({code})",
                    "一般提及": "{name}",
                    "強調": "{name}({code})"
                }
            ),
            
            "長線韭韭": StockMentionStyle(
                primary_formats=[
                    "{name}",
                    "{name}這檔",
                    "這檔{name}",
                    "{name}({code})"
                ],
                secondary_formats=[
                    "{code}",
                    "這支{name}",
                    "{code}這支",
                    "{name}這支"
                ],
                frequency_weights={
                    "{name}": 0.5,
                    "{name}這檔": 0.2,
                    "這檔{name}": 0.2,
                    "{name}({code})": 0.1
                },
                context_modifiers={
                    "技術分析": "{name}這檔",
                    "新聞評論": "{name}",
                    "一般提及": "{name}",
                    "強調": "{name}({code})"
                }
            ),
            
            "數據獵人": StockMentionStyle(
                primary_formats=[
                    "{name}({code})",
                    "{code}",
                    "{name}",
                    "這檔{name}"
                ],
                secondary_formats=[
                    "{name}這檔",
                    "這支{name}",
                    "{code}這支",
                    "{name}這支"
                ],
                frequency_weights={
                    "{name}({code})": 0.4,
                    "{code}": 0.3,
                    "{name}": 0.2,
                    "這檔{name}": 0.1
                },
                context_modifiers={
                    "技術分析": "{code}",
                    "新聞評論": "{name}({code})",
                    "一般提及": "{name}({code})",
                    "強調": "{name}({code})"
                }
            )
        }
        
        # 預設風格（用於未定義的KOL）
        self.default_style = StockMentionStyle(
            primary_formats=[
                "{name}",
                "{name}({code})",
                "{code}",
                "這檔{name}"
            ],
            secondary_formats=[
                "{name}這檔",
                "這支{name}",
                "{code}這支",
                "{name}這支"
            ],
            frequency_weights={
                "{name}": 0.4,
                "{name}({code})": 0.3,
                "{code}": 0.2,
                "這檔{name}": 0.1
            },
            context_modifiers={
                "技術分析": "{name}",
                "新聞評論": "{name}({code})",
                "一般提及": "{name}",
                "強調": "{name}({code})"
            }
        )
    
    def get_stock_mention_style(self, kol_nickname: str) -> StockMentionStyle:
        """獲取KOL的股票提及風格"""
        return self.kol_stock_styles.get(kol_nickname, self.default_style)
    
    def format_stock_mention(self, stock_name: str, stock_code: str, 
                           kol_nickname: str, context: str = "一般提及") -> str:
        """格式化股票提及"""
        style = self.get_stock_mention_style(kol_nickname)
        
        # 根據上下文選擇格式
        if context in style.context_modifiers:
            format_template = style.context_modifiers[context]
        else:
            # 根據頻率權重隨機選擇
            formats = list(style.frequency_weights.keys())
            weights = list(style.frequency_weights.values())
            format_template = random.choices(formats, weights=weights)[0]
        
        return format_template.format(name=stock_name, code=stock_code)
    
    def get_stock_mention_variations(self, stock_name: str, stock_code: str, 
                                   kol_nickname: str, count: int = 3) -> List[str]:
        """獲取股票提及的變體"""
        style = self.get_stock_mention_style(kol_nickname)
        
        # 合併主要和次要格式
        all_formats = style.primary_formats + style.secondary_formats
        
        # 去重並限制數量
        unique_formats = list(dict.fromkeys(all_formats))
        selected_formats = unique_formats[:count]
        
        variations = []
        for format_template in selected_formats:
            variations.append(format_template.format(name=stock_name, code=stock_code))
        
        return variations
    
    def update_kol_stock_style(self, kol_nickname: str, 
                              primary_formats: List[str] = None,
                              secondary_formats: List[str] = None,
                              frequency_weights: Dict[str, float] = None,
                              context_modifiers: Dict[str, str] = None):
        """更新KOL的股票提及風格"""
        if kol_nickname not in self.kol_stock_styles:
            self.kol_stock_styles[kol_nickname] = StockMentionStyle(
                primary_formats=[],
                secondary_formats=[],
                frequency_weights={},
                context_modifiers={}
            )
        
        current_style = self.kol_stock_styles[kol_nickname]
        
        if primary_formats:
            current_style.primary_formats = primary_formats
        if secondary_formats:
            current_style.secondary_formats = secondary_formats
        if frequency_weights:
            current_style.frequency_weights = frequency_weights
        if context_modifiers:
            current_style.context_modifiers = context_modifiers
    
    def get_all_kol_styles(self) -> Dict[str, Dict[str, Any]]:
        """獲取所有KOL的風格設定"""
        styles = {}
        for kol_name, style in self.kol_stock_styles.items():
            styles[kol_name] = {
                "primary_formats": style.primary_formats,
                "secondary_formats": style.secondary_formats,
                "frequency_weights": style.frequency_weights,
                "context_modifiers": style.context_modifiers
            }
        return styles

# 使用範例
if __name__ == "__main__":
    personalizer = StockMentionPersonalizer()
    
    # 測試不同KOL的股票提及方式
    test_stocks = [
        ("金像電", "2368"),
        ("台積電", "2330"),
        ("鴻海", "2317")
    ]
    
    test_kols = ["川川哥", "韭割哥", "梅川褲子", "八卦護城河", "長線韭韭", "數據獵人"]
    
    print("🎯 股票提及個人化測試")
    print("=" * 60)
    
    for kol in test_kols:
        print(f"\n👤 {kol} 的股票提及風格:")
        for stock_name, stock_code in test_stocks:
            # 不同上下文的提及方式
            contexts = ["技術分析", "新聞評論", "一般提及", "強調"]
            for context in contexts:
                mention = personalizer.format_stock_mention(stock_name, stock_code, kol, context)
                print(f"  {context}: {mention}")
            
            # 變體
            variations = personalizer.get_stock_mention_variations(stock_name, stock_code, kol, 3)
            print(f"  變體: {', '.join(variations)}")
            print()
    
    print("✅ 測試完成！")
