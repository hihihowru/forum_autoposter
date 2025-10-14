"""
互動發問內容生成器
跳過個人化模組，直接生成簡短疑問句
"""

import random
from typing import Dict, List, Any

# 簡短疑問句模板
INTERACTION_TEMPLATES = [
    "今天大家怎麼看？",
    "等等開盤",
    "大家有買嗎？",
    "怎麼看這個？",
    "會繼續漲嗎？",
    "有人跟嗎？",
    "你們覺得呢？",
    "怎麼看？",
    "有機會嗎？",
    "大家怎麼想？",
    "會回調嗎？",
    "有人關注嗎？",
    "怎麼看這個走勢？",
    "大家有在關注嗎？",
    "會繼續嗎？",
    "有人買了嗎？",
    "怎麼看這個漲停？",
    "大家覺得如何？",
    "會跌嗎？",
    "有人賣了嗎？"
]

# 表情符號
EMOJIS = ["😂", "😄", "😆", "👍", "👏", "🔥", "💪", "🚀", "📈", "💰"]

def generate_interaction_content(stock_id: str, stock_name: str, 
                               include_questions: bool = True,
                               include_emoji: bool = True,
                               include_hashtag: bool = True) -> Dict[str, Any]:
    """
    生成互動發問內容
    跳過個人化模組，直接生成簡短疑問句
    
    Args:
        stock_id: 股票代碼
        stock_name: 股票名稱
        include_questions: 是否包含問句
        include_emoji: 是否包含表情符號
        include_hashtag: 是否包含標籤
    
    Returns:
        包含標題和內容的字典
    """
    
    # 1. 標題直接使用股票名稱
    title = f"{stock_id}{stock_name}"
    
    # 2. 生成簡短疑問句內容
    content_parts = []
    
    # 選擇一個疑問句模板
    if include_questions:
        question = random.choice(INTERACTION_TEMPLATES)
        content_parts.append(question)
    
    # 添加表情符號
    if include_emoji:
        emoji = random.choice(EMOJIS)
        content_parts.append(emoji)
    
    # 添加標籤
    if include_hashtag:
        hashtag = f"#{stock_id}"
        content_parts.append(hashtag)
    
    # 組合內容（4-10字）
    content = " ".join(content_parts)
    
    # 確保內容長度在合理範圍內
    if len(content) > 15:
        content = content[:15] + "..."
    
    return {
        "title": title,
        "content": content,
        "content_length": len(content),
        "posting_type": "interaction",
        "generation_method": "interaction_shortcut",
        "skipped_personalization": True,
        "include_questions": include_questions,
        "include_emoji": include_emoji,
        "include_hashtag": include_hashtag
    }

def generate_batch_interaction_content(stock_list: List[Dict[str, str]], 
                                     include_questions: bool = True,
                                     include_emoji: bool = True,
                                     include_hashtag: bool = True) -> List[Dict[str, Any]]:
    """
    批量生成互動發問內容
    
    Args:
        stock_list: 股票列表，每個元素包含 stock_id 和 stock_name
        include_questions: 是否包含問句
        include_emoji: 是否包含表情符號
        include_hashtag: 是否包含標籤
    
    Returns:
        互動內容列表
    """
    
    results = []
    
    for stock in stock_list:
        stock_id = stock.get('stock_id', '')
        stock_name = stock.get('stock_name', '')
        
        if stock_id and stock_name:
            content = generate_interaction_content(
                stock_id=stock_id,
                stock_name=stock_name,
                include_questions=include_questions,
                include_emoji=include_emoji,
                include_hashtag=include_hashtag
            )
            results.append(content)
    
    return results

# 測試函數
if __name__ == "__main__":
    # 測試單個股票
    test_stock = {"stock_id": "2330", "stock_name": "台積電"}
    result = generate_interaction_content(
        stock_id=test_stock["stock_id"],
        stock_name=test_stock["stock_name"],
        include_questions=True,
        include_emoji=True,
        include_hashtag=True
    )
    
    print("單個股票測試結果:")
    print(f"標題: {result['title']}")
    print(f"內容: {result['content']}")
    print(f"長度: {result['content_length']} 字")
    print(f"跳過個人化: {result['skipped_personalization']}")
    
    # 測試批量生成
    test_stocks = [
        {"stock_id": "2330", "stock_name": "台積電"},
        {"stock_id": "2317", "stock_name": "鴻海"},
        {"stock_id": "2454", "stock_name": "聯發科"}
    ]
    
    batch_results = generate_batch_interaction_content(
        stock_list=test_stocks,
        include_questions=True,
        include_emoji=True,
        include_hashtag=True
    )
    
    print("\n批量生成測試結果:")
    for i, result in enumerate(batch_results, 1):
        print(f"{i}. {result['title']}: {result['content']} ({result['content_length']}字)")





