#!/usr/bin/env python3
"""
更新已發布的漲停股貼文狀態
"""

from src.clients.google.sheets_client import GoogleSheetsClient

def update_published_limit_up_posts():
    """更新已發布的漲停股貼文狀態"""
    sheets_client = GoogleSheetsClient(
        "./credentials/google-service-account.json",
        "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    # 已發布的漲停股貼文資訊（從日誌中獲取）
    published_posts = [
        {"row": 6, "post_id": "limit_up_5272_TWO_2_20250903_100745", "article_id": "173493660"},
        {"row": 7, "post_id": "limit_up_5302_TWO_3_20250903_100745", "article_id": "173493707"},
        {"row": 8, "post_id": "limit_up_6735_TWO_4_20250903_100745", "article_id": "173493746"},
        {"row": 9, "post_id": "limit_up_3284_TWO_5_20250903_100745", "article_id": "173493785"},
        {"row": 10, "post_id": "limit_up_4976_TW_6_20250903_100745", "article_id": "173493851"},
        {"row": 11, "post_id": "limit_up_6919_TW_7_20250903_100745", "article_id": "173493913"},
        {"row": 12, "post_id": "limit_up_1256_TW_8_20250903_100745", "article_id": "173493965"},
        {"row": 13, "post_id": "limit_up_8038_TWO_9_20250903_100745", "article_id": "173494020"},
        {"row": 15, "post_id": "limit_up_4743_TWO_11_20250903_100745", "article_id": "173494103"},
        {"row": 16, "post_id": "limit_up_6237_TWO_12_20250903_100745", "article_id": "173494148"},
        {"row": 17, "post_id": "limit_up_6854_TW_13_20250903_100745", "article_id": "173494194"},
    ]
    
    # 更新狀態
    for post in published_posts:
        try:
            # 更新狀態為 published
            sheets_client.update_cell('貼文記錄表', f"L{post['row']}", 'published')
            # 更新文章ID
            sheets_client.update_cell('貼文記錄表', f"G{post['row']}", post['article_id'])
            print(f"✅ 更新第{post['row']}行: {post['post_id']} -> published (ID: {post['article_id']})")
        except Exception as e:
            print(f"❌ 更新第{post['row']}行失敗: {e}")
    
    # 更新失敗的貼文
    try:
        sheets_client.update_cell('貼文記錄表', 'L14', 'failed')
        sheets_client.update_cell('貼文記錄表', 'G14', 'KOL 209登入失敗')
        print("✅ 更新第14行: 金居 -> failed")
    except Exception as e:
        print(f"❌ 更新第14行失敗: {e}")

if __name__ == "__main__":
    update_published_limit_up_posts()








