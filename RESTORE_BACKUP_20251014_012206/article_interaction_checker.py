"""
Article ID互動數據檢查函數
簡化版本，可以直接調用檢查指定Article ID的互動數據
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

async def check_article_interaction(article_id: str, 
                                  email: str = 'forum_200@cmoney.com.tw', 
                                  password: str = 'N9t1kY3x') -> Dict[str, Any]:
    """
    檢查指定Article ID的互動數據
    
    Args:
        article_id: 文章ID
        email: KOL登入Email (預設使用川川哥)
        password: KOL登入密碼 (預設使用川川哥)
        
    Returns:
        檢查結果字典，包含:
        - success: 是否成功
        - article_id: 文章ID
        - interaction_data: 互動數據
        - error: 錯誤訊息
    """
    result = {
        "success": False,
        "article_id": article_id,
        "interaction_data": None,
        "error": None,
        "check_time": datetime.now().isoformat()
    }
    
    try:
        # 初始化CMoney客戶端
        client = CMoneyClient()
        
        # 登入憑證
        credentials = LoginCredentials(email=email, password=password)
        
        # 登入獲取token
        login_result = await client.login(credentials)
        
        if not login_result or login_result.is_expired:
            result["error"] = "登入失敗或Token已過期"
            return result
        
        # 獲取互動數據
        interaction_data = await client.get_article_interactions(
            login_result.token, 
            article_id
        )
        
        if interaction_data:
            result["success"] = True
            result["interaction_data"] = {
                "post_id": interaction_data.post_id,
                "member_id": interaction_data.member_id,
                "likes": interaction_data.likes,
                "comments": interaction_data.comments,
                "shares": interaction_data.shares,
                "views": interaction_data.views,
                "engagement_rate": interaction_data.engagement_rate,
                "emoji_count": interaction_data.raw_data.get('emojiCount', {}) if interaction_data.raw_data else {},
                "comment_count": interaction_data.raw_data.get('commentCount', 0) if interaction_data.raw_data else 0,
                "interested_count": interaction_data.raw_data.get('interestedCount', 0) if interaction_data.raw_data else 0,
                "collected_count": interaction_data.raw_data.get('collectedCount', 0) if interaction_data.raw_data else 0
            }
        else:
            result["error"] = "無法獲取互動數據"
            
    except Exception as e:
        result["error"] = str(e)
    
    return result

async def check_multiple_articles(article_ids: list, 
                                 email: str = 'forum_200@cmoney.com.tw', 
                                 password: str = 'N9t1kY3x') -> Dict[str, Any]:
    """
    檢查多個Article ID的互動數據
    
    Args:
        article_ids: 文章ID列表
        email: KOL登入Email
        password: KOL登入密碼
        
    Returns:
        檢查結果字典，包含每個Article ID的結果
    """
    results = {
        "total_count": len(article_ids),
        "successful_count": 0,
        "failed_count": 0,
        "results": [],
        "check_time": datetime.now().isoformat()
    }
    
    for article_id in article_ids:
        result = await check_article_interaction(article_id, email, password)
        results["results"].append(result)
        
        if result["success"]:
            results["successful_count"] += 1
        else:
            results["failed_count"] += 1
        
        # 添加延遲避免API限制
        await asyncio.sleep(0.5)
    
    return results

def print_interaction_summary(result: Dict[str, Any]):
    """
    打印互動數據摘要
    
    Args:
        result: check_article_interaction的返回結果
    """
    if result["success"]:
        data = result["interaction_data"]
        print(f"✅ Article ID {result['article_id']} 互動數據:")
        print(f"  - 文章ID: {data['post_id']}")
        print(f"  - 會員ID: {data['member_id']}")
        print(f"  - 讚數: {data['likes']}")
        print(f"  - 留言數: {data['comments']}")
        print(f"  - 分享數: {data['shares']}")
        print(f"  - 瀏覽數: {data['views']}")
        print(f"  - 互動率: {data['engagement_rate']}")
        
        if data['emoji_count']:
            print(f"  - 表情符號:")
            for emoji, count in data['emoji_count'].items():
                if count > 0:
                    print(f"    * {emoji}: {count}")
    else:
        print(f"❌ Article ID {result['article_id']} 檢查失敗: {result['error']}")

# 使用範例
async def example_usage():
    """使用範例"""
    print("🧪 Article ID互動數據檢查範例")
    print("=" * 50)
    
    # 範例1: 檢查單個Article ID
    print("\n📝 範例1: 檢查單個Article ID")
    article_id = "173337593"
    result = await check_article_interaction(article_id)
    print_interaction_summary(result)
    
    # 範例2: 檢查多個Article ID
    print("\n📝 範例2: 檢查多個Article ID")
    article_ids = ["173337593", "173337594", "173337595"]
    results = await check_multiple_articles(article_ids)
    
    print(f"\n📊 批量檢查結果:")
    print(f"  - 總數: {results['total_count']}")
    print(f"  - 成功: {results['successful_count']}")
    print(f"  - 失敗: {results['failed_count']}")
    
    for result in results["results"]:
        print_interaction_summary(result)

if __name__ == "__main__":
    asyncio.run(example_usage())













