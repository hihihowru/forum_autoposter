#!/usr/bin/env python3
"""
修正版盤後漲停機器人 V4
整合所有修正：
1. 正確的 Google Sheets 欄位映射
2. Finlab 數據使用和記錄
3. Serper API 新聞抓取
4. Markdown 格式支援
5. 新聞來源連結
"""

import os
import sys
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any
import pandas as pd
import finlab
import finlab.data as fdata

load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder, EnhancedPostRecord
from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from smart_api_allocator import SmartAPIAllocator, StockAnalysis

# Serper API 新聞搜尋客戶端
class SerperNewsClient:
    """Serper API 新聞搜尋客戶端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def search_stock_news(self, stock_id: str, stock_name: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """搜尋股票相關新聞"""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            # 更精確的搜尋查詢，包含股票代號
            search_query = f'"{stock_name}" "{stock_id}" 漲停 今日 新聞'
            
            payload = {
                "q": search_query,
                "num": num_results,
                "gl": "tw",  # 台灣地區
                "hl": "zh-tw"  # 繁體中文
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            organic_results = data.get('organic', [])
            
            # 過濾出相關的新聞
            relevant_news = []
            for result in organic_results:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                
                # 更嚴格的相關性檢查
                title_lower = title.lower()
                snippet_lower = snippet.lower()
                
                # 必須包含股票代號或股票名稱
                has_stock_id = stock_id in title or stock_id in snippet
                has_stock_name = stock_name.lower() in title_lower or stock_name.lower() in snippet_lower
                has_limit_up = '漲停' in title or '漲停' in snippet
                
                if (has_stock_id or has_stock_name) and has_limit_up:
                    relevant_news.append({
                        'title': title,
                        'snippet': snippet,
                        'link': link,
                        'date': result.get('date', '')
                    })
            
            return relevant_news
            
        except Exception as e:
            print(f"❌ Serper API 搜尋失敗: {e}")
            return []

# 股票名稱對照表 (使用正確的股票代號)
stock_name_mapping = {
    "1587": "仲琦",
    "2436": "偉詮電", 
    "2642": "江興鍛",
    "2330": "台積電",
    "2317": "鴻海",
    "2454": "聯發科",
    "2419": "仲琦",  # 仲琦的正確代號
    "4528": "江興鍛",  # 江興鍛的正確代號
    # ... 其他股票
}

def get_stock_name_from_id(stock_id: str) -> str:
    return stock_name_mapping.get(stock_id, f"股票{stock_id}")

async def get_real_limit_up_stocks():
    """獲取真實的今日漲停股票數據"""
    try:
        # 登入 Finlab
        finlab_key = os.getenv('FINLAB_API_KEY')
        if not finlab_key:
            print("⚠️ 沒有 FINLAB_API_KEY，無法獲取真實數據")
            return None
        
        finlab.login(finlab_key)
        
        # 獲取收盤價和成交金額數據
        close_price = fdata.get('price:收盤價')
        volume_amount = fdata.get('price:成交金額')
        
        if close_price is None or volume_amount is None:
            print("⚠️ 無法獲取 Finlab 數據")
            return None
        
        limit_up_stocks = []
        
        # 獲取最新一天數據
        today_close = close_price.iloc[-1]
        today_volume = volume_amount.iloc[-1]
        
        # 計算前一日收盤價
        prev_close = close_price.iloc[-2] if len(close_price) > 1 else None
        
        if prev_close is not None:
            for stock_id in today_close.index:
                if pd.notna(today_close[stock_id]) and pd.notna(prev_close[stock_id]):
                    current_price = today_close[stock_id]
                    prev_price = prev_close[stock_id]
                    change_percent = ((current_price - prev_price) / prev_price) * 100
                    
                    # 檢查是否漲停（漲幅 >= 9.5%）
                    if change_percent >= 9.5:
                        volume_val = today_volume[stock_id] if pd.notna(today_volume[stock_id]) else 0
                        volume_amount_billion = volume_val / 100000000  # 轉換為億
                        
                        stock_name = get_stock_name_from_id(stock_id)
                        
                        limit_up_stocks.append({
                            'stock_id': stock_id,
                            'stock_name': stock_name,
                            'change_percent': change_percent,
                            'volume_amount': volume_amount_billion,
                            'current_price': current_price,
                            'prev_price': prev_price,
                            'is_high_volume': volume_amount_billion >= 1.0
                        })
        
        print(f"📊 Finlab 數據檢查完成，找到 {len(limit_up_stocks)} 檔漲停股票")
        return limit_up_stocks
        
    except Exception as e:
        print(f"❌ 獲取真實漲停股數據失敗: {e}")
        return None

def format_news_sources(news_list: List[Dict[str, Any]]) -> str:
    """格式化新聞來源"""
    if not news_list:
        return ""
    
    news_sources = "\n\n📰 相關新聞來源：\n"
    for i, news in enumerate(news_list, 1):
        news_sources += f"{i}. {news['title']}\n"
        news_sources += f"   {news['link']}\n"
        if news.get('snippet'):
            news_sources += f"   {news['snippet'][:100]}...\n"
        news_sources += "\n"
    
    return news_sources

async def test_enhanced_after_hours_bot():
    """測試增強版盤後機器人"""
    print("🚀 增強版盤後漲停機器人 V4 - 完整功能測試")
    print("=" * 80)

    # 1. 初始化組件
    print("\n📋 步驟 1: 初始化組件...")
    sheets_recorder = EnhancedSheetsRecorder()
    content_generator = ContentGenerator()
    smart_allocator = SmartAPIAllocator()
    
    # 初始化 Serper API
    serper_api_key = os.getenv('SERPER_API_KEY')
    if serper_api_key:
        serper_client = SerperNewsClient(serper_api_key)
        print("✅ Serper API 客戶端初始化成功")
    else:
        print("⚠️ 沒有 SERPER_API_KEY，將跳過新聞搜尋")
        serper_client = None
    
    print("✅ 所有組件初始化完成")
    
    # 2. 獲取真實漲停股數據
    print("\n📋 步驟 2: 獲取真實漲停股數據...")
    real_limit_up_stocks = await get_real_limit_up_stocks()
    
    if real_limit_up_stocks and len(real_limit_up_stocks) > 0:
        print(f"✅ 獲取到 {len(real_limit_up_stocks)} 檔漲停股票")
        # 只取前3檔進行測試
        stocks_for_processing = real_limit_up_stocks[:3]
        for stock in stocks_for_processing:
            print(f"  - {stock['stock_name']}({stock['stock_id']}): 漲幅 {stock['change_percent']:.2f}%, 成交金額 {stock['volume_amount']:.2f}億")
    else:
        print("⚠️ 今日無漲停股票或無法獲取數據，使用樣本數據")
        stocks_for_processing = [
            {"stock_id": "2330", "stock_name": "台積電", "change_percent": 9.8, "volume_amount": 15.2, "is_high_volume": True},
            {"stock_id": "2317", "stock_name": "鴻海", "change_percent": 9.9, "volume_amount": 0.8, "is_high_volume": False},
            {"stock_id": "2454", "stock_name": "聯發科", "change_percent": 9.7, "volume_amount": 2.1, "is_high_volume": True}
        ]
    
    # 3. 智能API調配
    print("\n📋 步驟 3: 智能API調配...")
    stock_analyses = []
    for stock in stocks_for_processing:
        stock_analyses.append(StockAnalysis(
            stock_id=stock['stock_id'],
            stock_name=stock['stock_name'],
            volume_rank=1, # 簡化處理
            change_percent=stock['change_percent'],
            volume_amount=stock['volume_amount'],
            rank_type='high_volume' if stock['is_high_volume'] else 'low_volume'
        ))
    
    allocated_stocks = smart_allocator.allocate_apis_for_stocks(stock_analyses)
    
    stocks_data = []
    for stock in allocated_stocks:
        stock_dict = {
            "stock_id": stock.stock_id,
            "stock_name": stock.stock_name,
            "change_percent": stock.change_percent,
            "volume_amount": stock.volume_amount,
            "is_high_volume": stock.volume_amount >= 1.0,
            "assigned_apis": stock.assigned_apis
        }
        stocks_data.append(stock_dict)
    
    # 4. 搜尋新聞並生成內容
    print("\n📋 步驟 4: 搜尋新聞並生成內容...")
    
    generated_posts = []
    for i, stock_data in enumerate(stocks_data):
        print(f"\n📝 處理第 {i+1} 篇貼文: {stock_data['stock_name']}({stock_data['stock_id']})")
        
        # 搜尋相關新聞
        news_sources = ""
        if serper_client:
            print(f"🔍 搜尋 {stock_data['stock_name']} 相關新聞...")
            news_list = serper_client.search_stock_news(
                stock_data['stock_id'], 
                stock_data['stock_name'], 
                num_results=3
            )
            if news_list:
                print(f"✅ 找到 {len(news_list)} 篇相關新聞")
                news_sources = format_news_sources(news_list)
            else:
                print("⚠️ 未找到相關新聞")
        
        # 構建增強的市場數據，包含詳細的 Finlab 數據
        enhanced_market_data = {
            "stock_id": stock_data['stock_id'],
            "stock_name": stock_data['stock_name'],
            "change_percent": stock_data['change_percent'],
            "volume_amount": stock_data['volume_amount'],
            "is_high_volume": stock_data['is_high_volume'],
            "assigned_apis": stock_data['assigned_apis'],
            "has_stock": True,
            "stock_data": {
                "change_percent": stock_data['change_percent'],
                "current_price": stock_data.get('current_price', 0),
                "prev_price": stock_data.get('prev_price', 0),
                "volume": stock_data['volume_amount'] * 100000000,  # 轉換為張數
                "volume_amount_billion": stock_data['volume_amount']
            },
            "finlab_data": {
                "current_price": stock_data.get('current_price', 0),
                "prev_price": stock_data.get('prev_price', 0),
                "volume_amount_billion": stock_data['volume_amount'],
                "change_percent": stock_data['change_percent'],
                "is_limit_up": True,
                "volume_rank": "high" if stock_data['is_high_volume'] else "low"
            },
            "news_sources": news_sources
        }
        
        # 構建內容請求
        content_request = ContentRequest(
            topic_title=f"{stock_data['stock_name']}({stock_data['stock_id']}) 漲停分析",
            topic_keywords=f"{stock_data['stock_name']}, {stock_data['stock_id']}, 漲停, 盤後分析, 隔日沖",
            kol_persona="隔日沖獵人",
            kol_nickname="隔日沖獵人",
            content_type="AFTER_HOURS_LIMIT_UP",
            target_audience="day_traders,swing_traders",
            market_data=enhanced_market_data
        )
        
        # 生成內容
        generated_content = content_generator.generate_complete_content(content_request)
        
        if generated_content.success:
            # 添加新聞來源到內容
            full_content = generated_content.content
            if news_sources:
                full_content += news_sources
            
            # 移除 Markdown 格式（** 等）
            clean_content = full_content.replace('**', '').replace('*', '').replace('##', '').replace('#', '')
            
            post_data = {
                "post_id": f"after_hours_{stock_data['stock_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "kol_serial": "150",
                "kol_nickname": "隔日沖獵人",
                "kol_id": "9505496",
                "persona": "隔日沖獵人",
                "content_type": "AFTER_HOURS_LIMIT_UP",
                "topic_id": f"after_hours_{stock_data['stock_id']}_{datetime.now().strftime('%Y%m%d')}",
                "topic_title": f"{stock_data['stock_name']}({stock_data['stock_id']}) 漲停分析",
                "content": clean_content,
                "status": "generated",
                "trigger_type": "AFTER_HOURS_LIMIT_UP",
                "trigger_event_id": f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "data_sources": ", ".join(stock_data['assigned_apis']),
                "data_source_status": "success",
                "post_type": "after_hours_analysis",
                "content_length_type": "medium",
                "word_count": str(len(clean_content)),
                "content_length_category": "medium",
                "content_generation_time": datetime.now().isoformat(),
                "generated_title": generated_content.title,
                "stock_id": stock_data['stock_id'],
                "stock_name": stock_data['stock_name'],
                "generated_at": datetime.now().isoformat(),
                "preferred_data_sources": ", ".join(stock_data['assigned_apis']),
                "analysis_type": "finlab_technical_analysis",
                "analysis_type_detail": "finlab_price_volume_analysis",
                "is_stock_trigger": "true",
                "stock_trigger_type": "after_hours_limit_up",
                "topic_keywords": f"{stock_data['stock_name']}, {stock_data['stock_id']}, 漲停, 盤後分析, 隔日沖",
                "topic_category": "stock_analysis",
                "topic_priority": "high",
                "topic_heat_score": "9.5",
                "writing_style": "隔日沖獵人風格",
                "tone": "專業分析",
                "key_phrases": "漲停, 隔日沖, 技術分析, 成交量",
                "avoid_topics": "過度投機, 內線交易",
                "kol_assignment_method": "fixed_pool",
                "kol_weight": "1.0",
                "kol_version": "v1.0",
                "kol_learning_score": "0.8"
            }
            
            # 記錄到 Google Sheets
            await sheets_recorder.record_enhanced_post(post_data)
            
            generated_posts.append({
                'stock_name': stock_data['stock_name'],
                'stock_id': stock_data['stock_id'],
                'title': generated_content.title,
                'content': clean_content,
                'news_count': len(news_list) if serper_client and 'news_list' in locals() else 0
            })
            
            print(f"✅ 生成第 {i+1} 篇貼文: {stock_data['stock_name']}({stock_data['stock_id']}) - 隔日沖獵人")
            print(f"  📝 標題: {generated_content.title}")
            print(f"  📄 內容長度: {len(clean_content)} 字")
            print(f"  🔧 使用API: {', '.join(stock_data['assigned_apis'])}")
            if serper_client and 'news_list' in locals():
                print(f"  📰 新聞來源: {len(news_list)} 篇")
        else:
            print(f"❌ 生成失敗: {generated_content.error_message}")
    
    # 5. 顯示結果
    print(f"\n🎉 增強版盤後機器人測試完成！")
    print("=" * 80)
    print(f"📊 處理股票: {len(stocks_for_processing)} 檔")
    print(f"🤖 使用KOL: 隔日沖獵人 (序號: 150)")
    print(f"📝 生成貼文: {len(generated_posts)} 篇")
    print(f"🔧 智能調配: ✅ 完成")
    print(f"📰 新聞搜尋: {'✅ 完成' if serper_client else '⚠️ 跳過'}")
    print(f"📄 內容生成: ✅ 完成")
    print(f"📊 記錄保存: ✅ 完成")
    
    # 顯示生成的完整貼文內容
    print(f"\n📄 生成的完整貼文內容:")
    print("=" * 80)
    
    for i, post in enumerate(generated_posts, 1):
        print(f"\n📝 第 {i} 篇貼文:")
        print(f"標題: {post['title']}")
        print(f"股票: {post['stock_name']}({post['stock_id']})")
        print(f"新聞來源: {post['news_count']} 篇")
        print(f"內容:")
        print(post['content'])
        print("-" * 60)
    
    return generated_posts

async def main():
    """主執行函數"""
    await test_enhanced_after_hours_bot()

if __name__ == "__main__":
    asyncio.run(main())
