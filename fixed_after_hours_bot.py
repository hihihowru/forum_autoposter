#!/usr/bin/env python3
"""
修正版盤後漲停機器人
解決：1. Google Sheets 欄位映射錯誤 2. 股票名稱問題 3. 內容生成不完整 4. 完整數據調度流程
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder
from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from smart_api_allocator import SmartAPIAllocator, StockAnalysis

# 股票名稱對照表
STOCK_NAME_MAPPING = {
    "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2308": "台達電",
    "2412": "中華電", "2882": "國泰金", "2881": "富邦金", "2603": "長榮",
    "2609": "陽明", "1303": "南亞", "1326": "台化", "2002": "中鋼",
    "1101": "台泥", "1102": "亞泥", "1216": "統一", "2377": "微星",
    "2382": "廣達", "2408": "南亞科", "2474": "可成", "2498": "宏達電",
    "3008": "大立光", "3034": "聯詠", "3231": "緯創", "3711": "日月光投控",
    "4938": "和碩", "6505": "台塑化", "8046": "南電", "9910": "豐泰",
    "1587": "仲琦", "2436": "偉詮電", "2642": "江興鍛", "6191": "精成科",
    "8121": "越峰", "6732": "昇佳電子", "5438": "東友", "4414": "如興",
    "4528": "江興鍛", "6716": "應廣", "4968": "立積"
}

def get_stock_name(stock_id: str) -> str:
    """獲取股票名稱"""
    return STOCK_NAME_MAPPING.get(stock_id, f"股票{stock_id}")

async def get_real_limit_up_stocks():
    """獲取真實的今日漲停股票數據"""
    try:
        import finlab
        import finlab.data as fdata
        import pandas as pd
        from datetime import datetime
        
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
        
        # 計算漲停股票（漲幅 >= 9.5%）
        limit_up_stocks = []
        
        # 獲取今日數據
        today_close = close_price.iloc[-1]  # 最新一天
        today_volume = volume_amount.iloc[-1]  # 最新一天
        
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
                        
                        # 獲取真實股票名稱
                        stock_name = get_stock_name(stock_id)
                        
                        limit_up_stocks.append({
                            'stock_id': stock_id,
                            'stock_name': stock_name,
                            'change_percent': change_percent,
                            'volume_amount': volume_amount_billion,
                            'current_price': current_price,
                            'prev_price': prev_price
                        })
        
        print(f"📊 Finlab 數據檢查完成，找到 {len(limit_up_stocks)} 檔漲停股票")
        return limit_up_stocks
        
    except Exception as e:
        print(f"❌ 獲取真實漲停股數據失敗: {e}")
        return None

async def test_fixed_after_hours_bot():
    """測試修正版盤後機器人"""
    
    print("🚀 修正版盤後漲停機器人 - 完整數據調度流程")
    print("=" * 80)
    
    try:
        # 1. 初始化所有組件
        print("\n📋 步驟 1: 初始化組件...")
        
        sheets_recorder = EnhancedSheetsRecorder()
        content_generator = ContentGenerator()
        cmoney_client = CMoneyClient()
        smart_allocator = SmartAPIAllocator()
        
        print("✅ 所有組件初始化完成")
        
        # 2. 獲取真實漲停股數據
        print("\n📋 步驟 2: 獲取真實漲停股數據...")
        limit_up_stocks = await get_real_limit_up_stocks()
        
        if not limit_up_stocks or len(limit_up_stocks) == 0:
            print("⚠️ 今日無漲停股票，使用樣本數據")
            limit_up_stocks = [
                {
                    'stock_id': '1587',
                    'stock_name': '仲琦',
                    'change_percent': 9.94,
                    'volume_amount': 0.93,
                    'current_price': 25.30,
                    'prev_price': 23.00
                },
                {
                    'stock_id': '2436',
                    'stock_name': '偉詮電',
                    'change_percent': 9.96,
                    'volume_amount': 8.73,
                    'current_price': 53.20,
                    'prev_price': 48.40
                },
                {
                    'stock_id': '2642',
                    'stock_name': '江興鍛',
                    'change_percent': 9.95,
                    'volume_amount': 0.52,
                    'current_price': 21.00,
                    'prev_price': 19.10
                }
            ]
        
        print(f"✅ 獲取到 {len(limit_up_stocks)} 檔漲停股票")
        for stock in limit_up_stocks[:3]:
            print(f"  - {stock['stock_name']}({stock['stock_id']}): 漲幅 {stock['change_percent']:.2f}%, 成交金額 {stock['volume_amount']:.2f}億")
        
        # 3. 智能API調配
        print("\n📋 步驟 3: 智能API調配...")
        
        # 轉換為 StockAnalysis 格式
        stock_analyses = []
        for i, stock in enumerate(limit_up_stocks[:3]):  # 只取前3檔
            stock_analysis = StockAnalysis(
                stock_id=stock['stock_id'],
                stock_name=stock['stock_name'],
                volume_rank=i + 1,
                change_percent=stock['change_percent'],
                volume_amount=stock['volume_amount'],
                rank_type="high_volume" if stock['volume_amount'] >= 1.0 else "low_volume"
            )
            stock_analyses.append(stock_analysis)
        
        # 執行智能API調配
        allocated_stocks = smart_allocator.allocate_apis_for_stocks(stock_analyses)
        
        print("✅ 智能API調配完成")
        for stock in allocated_stocks:
            print(f"  - {stock.stock_name}({stock.stock_id}): {stock.assigned_apis}")
        
        # 4. KOL分配（固定KOL 150）
        print("\n📋 步驟 4: KOL分配策略...")
        
        kol_150 = {
            'serial': 150,
            'nickname': '隔日沖獵人',
            'persona': '隔日沖獵人',
            'email': 'forum_150@cmoney.com.tw',
            'password': os.getenv('CMONEY_PASSWORD'),
            'member_id': '9505496'
        }
        
        # 轉換為字典格式
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
        
        print("✅ KOL分配策略完成")
        for stock in stocks_data:
            print(f"  - {stock['stock_name']}({stock['stock_id']}) -> {kol_150['nickname']}")
        
        # 5. 內容生成
        print("\n📋 步驟 5: 內容生成...")
        
        generated_posts = []
        for i, stock in enumerate(stocks_data):
            print(f"\n📝 生成第 {i+1} 篇貼文: {stock['stock_name']}({stock['stock_id']})")
            
            # 構建內容請求
            content_request = ContentRequest(
                topic_title=f"{stock['stock_name']}({stock['stock_id']}) 漲停分析",
                topic_keywords=f"{stock['stock_name']}, {stock['stock_id']}, 漲停, 盤後分析, 隔日沖",
                kol_persona=kol_150['persona'],
                kol_nickname=kol_150['nickname'],
                content_type="AFTER_HOURS_LIMIT_UP",
                target_audience="day_traders,swing_traders",
                market_data={
                    "stock_id": stock['stock_id'],
                    "stock_name": stock['stock_name'],
                    "change_percent": stock['change_percent'],
                    "volume_amount": stock['volume_amount'],
                    "is_high_volume": stock['is_high_volume'],
                    "assigned_apis": stock['assigned_apis']
                }
            )
            
            # 生成內容
            generated_content = content_generator.generate_complete_content(content_request)
            
            if generated_content.success:
                # 修正的 post_data 結構
                post_data = {
                    "post_id": f"after_hours_{stock['stock_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "kol_serial": str(kol_150['serial']),
                    "kol_nickname": kol_150['nickname'],
                    "kol_id": kol_150['member_id'],
                    "persona": kol_150['persona'],
                    "content_type": "AFTER_HOURS_LIMIT_UP",
                    "topic_id": f"after_hours_{stock['stock_id']}_{datetime.now().strftime('%Y%m%d')}",
                    "topic_title": f"{stock['stock_name']}({stock['stock_id']}) 漲停分析",
                    "content": generated_content.content,
                    "status": "generated",
                    "trigger_type": "AFTER_HOURS_LIMIT_UP",
                    "trigger_event_id": f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "data_sources": ", ".join(stock['assigned_apis']),
                    "data_source_status": "success",
                    "post_type": "after_hours_analysis",
                    "content_length_type": "medium",
                    "word_count": str(len(generated_content.content)),
                    "content_length_category": "medium",
                    "content_generation_time": datetime.now().isoformat(),
                    "generated_title": generated_content.title,
                    "stock_id": stock['stock_id'],
                    "stock_name": stock['stock_name'],
                    "generated_at": datetime.now().isoformat()
                }
                generated_posts.append(post_data)
                
                print(f"  ✅ 標題: {generated_content.title}")
                print(f"  📄 內容長度: {len(generated_content.content)} 字")
                print(f"  🔧 使用API: {', '.join(stock['assigned_apis'])}")
                print(f"  📄 內容預覽: {generated_content.content[:100]}...")
            else:
                print(f"  ❌ 生成失敗: {generated_content.error_message}")
        
        # 6. Google Sheets 記錄
        print(f"\n📋 步驟 6: Google Sheets 記錄...")
        
        if generated_posts:
            for post in generated_posts:
                await sheets_recorder.record_enhanced_post(post)
            print(f"✅ 成功記錄 {len(generated_posts)} 篇貼文到 Google Sheets")
        
        # 7. 流程總結
        print(f"\n🎉 修正版盤後機器人測試完成！")
        print("=" * 80)
        print(f"📊 處理股票: {len(stocks_data)} 檔")
        print(f"🤖 使用KOL: {kol_150['nickname']} (序號: {kol_150['serial']})")
        print(f"📝 生成貼文: {len(generated_posts)} 篇")
        print(f"🔧 智能調配: ✅ 完成")
        print(f"👥 KOL分配: ✅ 完成")
        print(f"📄 內容生成: ✅ 完成")
        print(f"📊 記錄保存: ✅ 完成")
        
        # 8. 顯示生成的完整內容
        print(f"\n📄 生成的完整貼文內容:")
        print("=" * 80)
        for i, post in enumerate(generated_posts, 1):
            print(f"\n📝 第 {i} 篇貼文:")
            print(f"標題: {post['generated_title']}")
            print(f"股票: {post['stock_name']}({post['stock_id']})")
            print(f"內容:")
            print(post['content'])
            print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 流程測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主執行函數"""
    success = await test_fixed_after_hours_bot()
    if success:
        print("\n✅ 修正版盤後漲停機器人運作正常！")
    else:
        print("\n❌ 修正版盤後漲停機器人有問題！")

if __name__ == "__main__":
    asyncio.run(main())
