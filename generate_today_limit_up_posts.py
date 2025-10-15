#!/usr/bin/env python3
"""
手動輸入今日 (9/9) 漲停股票數據生成貼文
"""

import os
import sys
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder, EnhancedPostRecord
from src.services.content.content_generator import ContentGenerator, ContentRequest
from smart_api_allocator import SmartAPIAllocator, StockAnalysis

# 手動輸入的今日 (9/9) 漲停股票數據
TODAY_LIMIT_UP_STOCKS = [
    {
        "stock_id": "2429",
        "stock_name": "銘旺科",
        "change_percent": 10.00,
        "volume_amount": 2.6625,  # 億
        "current_price": 137.50,
        "prev_price": 127.00,
        "is_high_volume": True
    },
    {
        "stock_id": "8467",
        "stock_name": "波力-KY",
        "change_percent": 10.00,
        "volume_amount": 1.2544,  # 億
        "current_price": 198.00,
        "prev_price": 187.50,
        "is_high_volume": True
    },
    {
        "stock_id": "8021",
        "stock_name": "尖點",
        "change_percent": 9.98,
        "volume_amount": 62.8226,  # 億
        "current_price": 99.20,
        "prev_price": 92.20,
        "is_high_volume": True
    }
]

async def generate_today_limit_up_posts():
    """生成今日 (9/9) 漲停股票貼文"""
    print("🚀 今日 (9/9) 漲停股票貼文生成")
    print("=" * 80)

    # 1. 初始化組件
    print("\n📋 步驟 1: 初始化組件...")
    sheets_recorder = EnhancedSheetsRecorder()
    content_generator = ContentGenerator()
    smart_allocator = SmartAPIAllocator()
    
    print("✅ 所有組件初始化完成")
    
    # 2. 使用手動輸入的今日漲停股票數據
    print(f"\n📋 步驟 2: 使用今日 (9/9) 漲停股票數據...")
    print(f"✅ 手動輸入 {len(TODAY_LIMIT_UP_STOCKS)} 檔今日漲停股票")
    
    # 只取前3檔進行測試
    stocks_for_processing = TODAY_LIMIT_UP_STOCKS[:3]
    for stock in stocks_for_processing:
        print(f"  - {stock['stock_name']}({stock['stock_id']}): 漲幅 {stock['change_percent']:.2f}%, 成交金額 {stock['volume_amount']:.2f}億")
    
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
            "assigned_apis": stock.assigned_apis,
            "current_price": next((s['current_price'] for s in stocks_for_processing if s['stock_id'] == stock.stock_id), 0),
            "prev_price": next((s['prev_price'] for s in stocks_for_processing if s['stock_id'] == stock.stock_id), 0)
        }
        stocks_data.append(stock_dict)
    
    # 4. 生成內容
    print("\n📋 步驟 4: 生成內容...")
    
    generated_posts = []
    for i, stock_data in enumerate(stocks_data):
        print(f"\n📝 處理第 {i+1} 篇貼文: {stock_data['stock_name']}({stock_data['stock_id']})")
        
        # 構建增強的市場數據
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
            }
        }
        
        # 構建內容請求
        content_request = ContentRequest(
            topic_title=f"{stock_data['stock_name']}({stock_data['stock_id']}) 今日漲停分析",
            topic_keywords=f"{stock_data['stock_name']}, {stock_data['stock_id']}, 漲停, 今日分析, 隔日沖",
            kol_persona="隔日沖獵人",
            kol_nickname="隔日沖獵人",
            content_type="AFTER_HOURS_LIMIT_UP",
            target_audience="day_traders,swing_traders",
            market_data=enhanced_market_data
        )
        
        # 生成內容
        generated_content = content_generator.generate_complete_content(content_request)
        
        if generated_content.success:
            # 移除 Markdown 格式（** 等）
            clean_content = generated_content.content.replace('**', '').replace('*', '').replace('##', '').replace('#', '')
            
            post_data = {
                "post_id": f"after_hours_{stock_data['stock_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "kol_serial": "150",
                "kol_nickname": "隔日沖獵人",
                "kol_id": "9505496",
                "persona": "隔日沖獵人",
                "content_type": "AFTER_HOURS_LIMIT_UP",
                "topic_id": f"after_hours_{stock_data['stock_id']}_{datetime.now().strftime('%Y%m%d')}",
                "topic_title": f"{stock_data['stock_name']}({stock_data['stock_id']}) 今日漲停分析",
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
                "topic_keywords": f"{stock_data['stock_name']}, {stock_data['stock_id']}, 漲停, 今日分析, 隔日沖",
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
                'content': clean_content
            })
            
            print(f"✅ 生成第 {i+1} 篇貼文: {stock_data['stock_name']}({stock_data['stock_id']}) - 隔日沖獵人")
            print(f"  📝 標題: {generated_content.title}")
            print(f"  📄 內容長度: {len(clean_content)} 字")
            print(f"  🔧 使用API: {', '.join(stock_data['assigned_apis'])}")
        else:
            print(f"❌ 生成失敗: {generated_content.error_message}")
    
    # 5. 顯示結果
    print(f"\n🎉 今日 (9/9) 漲停股票貼文生成完成！")
    print("=" * 80)
    print(f"📊 處理股票: {len(stocks_for_processing)} 檔")
    print(f"🤖 使用KOL: 隔日沖獵人 (序號: 150)")
    print(f"📝 生成貼文: {len(generated_posts)} 篇")
    print(f"🔧 智能調配: ✅ 完成")
    print(f"📄 內容生成: ✅ 完成")
    print(f"📊 記錄保存: ✅ 完成")
    
    # 顯示生成的完整貼文內容
    print(f"\n📄 生成的完整貼文內容:")
    print("=" * 80)
    
    for i, post in enumerate(generated_posts, 1):
        print(f"\n📝 第 {i} 篇貼文:")
        print(f"標題: {post['title']}")
        print(f"股票: {post['stock_name']}({post['stock_id']})")
        print(f"內容:")
        print(post['content'])
        print("-" * 60)
    
    return generated_posts

async def main():
    """主執行函數"""
    await generate_today_limit_up_posts()

if __name__ == "__main__":
    asyncio.run(main())
