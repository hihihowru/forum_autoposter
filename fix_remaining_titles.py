#!/usr/bin/env python3
"""
修正剩餘貼文的標題問題
"""

from src.clients.google.sheets_client import GoogleSheetsClient

def fix_remaining_post_titles():
    """修正剩餘貼文的標題問題"""
    sheets_client = GoogleSheetsClient(
        "./credentials/google-service-account.json",
        "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    # 修正標題（移除股票代號）
    title_fixes = [
        {"row": 18, "old_title": "6291O昨日漲停潮來了，大家準備好了嗎？ 📈", "new_title": "沛亨昨日漲停潮來了，大家準備好了嗎？ 📈"},
        {"row": 19, "old_title": "6535O昨日噴了！", "new_title": "順藥昨日噴了！"},
        {"row": 20, "old_title": "4528O昨日強勢漲停！", "new_title": "江興鍛昨日強勢漲停！"},
        {"row": 21, "old_title": "6142昨日漲停創新高", "new_title": "友勁昨日漲停創新高"},
        {"row": 22, "old_title": "義隆昨日漲停背後的資金流向 📈", "new_title": "義隆昨日漲停背後的資金流向 📈"}
    ]
    
    # 更新標題
    for fix in title_fixes:
        try:
            sheets_client.update_cell('貼文記錄表', f"I{fix['row']}", fix['new_title'])
            print(f"✅ 修正第{fix['row']}行標題: {fix['old_title'][:20]}... -> {fix['new_title'][:20]}...")
        except Exception as e:
            print(f"❌ 修正第{fix['row']}行標題失敗: {e}")

if __name__ == "__main__":
    fix_remaining_post_titles()
