"""
檢查今日熱門話題是否有標記股標

流程：
1) 登入 CMoney（使用環境變數或預設測試帳號）
2) 呼叫 Trending API 取得話題
3) 檢查每筆 raw_data 是否包含與股票相關欄位
4) 也用正則檢查標題中是否含台股四碼代號
"""

import os
import re
import sys
import asyncio
from typing import Any, Dict

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials


def extract_possible_stock_tags(raw: Dict[str, Any]) -> Dict[str, Any]:
    found = []
    # 掃描常見欄位
    candidate_keys = [
        'relatedStockSymbols', 'stocks', 'stockSymbols', 'commodityTags', 'tags', 'symbols',
        'relatedStocks', 'stockCodes', 'tickers', 'commodities'
    ]
    for key in candidate_keys:
        if key in raw and raw[key]:
            found.append({key: raw[key]})
    
    # 也檢查所有包含 'stock' 或 'symbol' 或 'commodity' 的欄位
    for key, value in raw.items():
        if any(keyword in key.lower() for keyword in ['stock', 'symbol', 'commodity', 'ticker']) and value:
            if not any(key in match for match in found):
                found.append({key: value})
    
    return { 'raw_matches': found, 'all_keys': list(raw.keys()) }


def title_has_ticker(title: str) -> bool:
    # 台股常見四碼代號檢查（避免誤判，前後允許括號/空白/非數字）
    return re.search(r'(?:^|[^\d])(\d{4})(?:[^\d]|$)', title) is not None


async def main() -> int:
    email = os.getenv('CMONEY_EMAIL', 'forum_200@cmoney.com.tw')
    password = os.getenv('CMONEY_PASSWORD', 'N9t1kY3x')

    client = CMoneyClient()
    try:
        print("\n📈 取得今日熱門話題並檢查股標")
        print("=" * 60)

        token = await client.login(LoginCredentials(email=email, password=password))
        topics = await client.get_trending_topics(token.token)

        print(f"✅ 獲取到 {len(topics)} 個熱門話題（僅顯示前 10 筆）\n")
        for i, t in enumerate(topics[:10], 1):
            print(f"{i}. {t.title}")
            print(f"   - ID: {t.id}")
            
            # 呼叫特定話題詳細資訊 API
            try:
                topic_detail = await client.get_topic_detail(token.token, t.id)
                if topic_detail:
                    print(f"   - 話題詳細資訊:")
                    print(f"     name: {topic_detail.get('name', 'N/A')}")
                    print(f"     description: {topic_detail.get('description', 'N/A')}")
                    
                    # 檢查 relatedStockSymbols
                    related_stocks = topic_detail.get('relatedStockSymbols', [])
                    if related_stocks:
                        print(f"   - ✅ 找到股標資訊: {len(related_stocks)} 個")
                        for stock in related_stocks:
                            print(f"     - type: {stock.get('type', 'N/A')}, key: {stock.get('key', 'N/A')}")
                    else:
                        print(f"   - ❌ 無股標資訊")
                    
                    # 顯示完整詳細資料
                    print(f"   - 🔍 完整詳細資料:")
                    for key, value in topic_detail.items():
                        print(f"     {key}: {value}")
                else:
                    print(f"   - ❌ 無法取得話題詳細資訊")
            except Exception as e:
                print(f"   - ❌ 取得話題詳細資訊失敗: {e}")
            print()

        return 0
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        return 1
    finally:
        client.close()


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))


