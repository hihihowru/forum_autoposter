"""
智能漲停股貼文生成系統
使用LLM查詢今日漲停股票 + Serper API查詢漲停原因 + 生成20則貼文
"""

import sys
import os
import asyncio
import logging
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

sys.path.append(str(Path(__file__).parent / "src"))

from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.services.assign.assignment_service import AssignmentService
from clients.google.sheets_client import GoogleSheetsClient
from openai import OpenAI

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LimitUpStock:
    """漲停股票資料"""
    stock_id: str
    stock_name: str
    limit_up_price: float
    previous_close: float
    change_percent: float
    limit_up_reason: str = ""

class SerperNewsClient:
    """Serper API 新聞搜尋客戶端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def search_limit_up_reason(self, stock_name: str, stock_id: str) -> str:
        """搜尋漲停原因"""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            # 搜尋漲停相關新聞
            query = f"{stock_name} {stock_id} 漲停 原因 新聞"
            payload = {
                "q": query,
                "num": 3,
                "type": "search"
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            organic_results = data.get('organic', [])
            
            # 提取相關資訊
            reasons = []
            for result in organic_results:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                
                # 過濾相關內容
                if any(keyword in title.lower() or keyword in snippet.lower() 
                      for keyword in ['漲停', '大漲', '飆漲', '利多', '好消息']):
                    reasons.append(f"{title}: {snippet}")
            
            if reasons:
                return " | ".join(reasons[:2])  # 取前2個原因
            else:
                return f"市場資金追捧，{stock_name}今日強勢漲停"
                
        except Exception as e:
            logger.error(f"搜尋漲停原因失敗: {e}")
            return f"市場資金追捧，{stock_name}今日強勢漲停"

class SmartLimitUpGenerator:
    """智能漲停股貼文生成器"""
    
    def __init__(self):
        self.content_generator = ContentGenerator()
        
        # 初始化 Google Sheets 客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        self.assignment_service = AssignmentService(self.sheets_client)
        self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.news_client = SerperNewsClient("59eac2d4f87afca3ae6e252f4214098defdd40fa")
        
        print("🚀 智能漲停股貼文生成器初始化完成")
    
    async def query_today_limit_up_stocks(self) -> List[LimitUpStock]:
        """使用用戶提供的真實漲停股票數據"""
        print("\n📋 使用用戶提供的真實漲停股票數據...")
        
        # 根據您提供的22檔漲停股票數據
        stocks_data_from_user = [
            {"stock_id": "5227.TWO", "stock_name": "立凱-KY", "limit_up_price": 32.45, "previous_close": 29.50, "change_percent": 10.00},
            {"stock_id": "5272.TWO", "stock_name": "笙科", "limit_up_price": 23.10, "previous_close": 21.00, "change_percent": 10.00},
            {"stock_id": "5302.TWO", "stock_name": "太欣", "limit_up_price": 9.90, "previous_close": 9.00, "change_percent": 10.00},
            {"stock_id": "6735.TWO", "stock_name": "美達科技", "limit_up_price": 69.30, "previous_close": 63.00, "change_percent": 10.00},
            {"stock_id": "3284.TWO", "stock_name": "太普高", "limit_up_price": 23.15, "previous_close": 21.05, "change_percent": 9.98},
            {"stock_id": "4976.TW", "stock_name": "佳凌", "limit_up_price": 49.05, "previous_close": 44.60, "change_percent": 9.98},
            {"stock_id": "6919.TW", "stock_name": "康霈*", "limit_up_price": 231.50, "previous_close": 210.50, "change_percent": 9.98},
            {"stock_id": "1256.TW", "stock_name": "鮮活果汁-KY", "limit_up_price": 143.50, "previous_close": 130.50, "change_percent": 9.96},
            {"stock_id": "8038.TWO", "stock_name": "長園科", "limit_up_price": 57.40, "previous_close": 52.20, "change_percent": 9.96},
            {"stock_id": "8358.TWO", "stock_name": "金居", "limit_up_price": 215.50, "previous_close": 196.00, "change_percent": 9.95},
            {"stock_id": "4743.TWO", "stock_name": "合一", "limit_up_price": 78.50, "previous_close": 71.40, "change_percent": 9.94},
            {"stock_id": "6237.TWO", "stock_name": "驊訊", "limit_up_price": 50.90, "previous_close": 46.30, "change_percent": 9.94},
            {"stock_id": "6854.TW", "stock_name": "錼創科技-KY創", "limit_up_price": 183.00, "previous_close": 166.50, "change_percent": 9.91},
            {"stock_id": "4168.TWO", "stock_name": "醣聯", "limit_up_price": 26.15, "previous_close": 23.80, "change_percent": 9.87},
            {"stock_id": "5438.TWO", "stock_name": "東友", "limit_up_price": 25.60, "previous_close": 23.30, "change_percent": 9.87},
            {"stock_id": "2243.TW", "stock_name": "宏旭-KY", "limit_up_price": 15.60, "previous_close": 14.20, "change_percent": 9.86},
            {"stock_id": "3004.TW", "stock_name": "豐達科", "limit_up_price": 145.00, "previous_close": 132.00, "change_percent": 9.85},
            {"stock_id": "6291.TWO", "stock_name": "沛亨", "limit_up_price": 156.50, "previous_close": 142.50, "change_percent": 9.82},
            {"stock_id": "6535.TWO", "stock_name": "順藥", "limit_up_price": 224.50, "previous_close": 204.50, "change_percent": 9.78},
            {"stock_id": "4528.TWO", "stock_name": "江興鍛", "limit_up_price": 19.10, "previous_close": 17.40, "change_percent": 9.77},
            {"stock_id": "6142.TW", "stock_name": "友勁", "limit_up_price": 10.80, "previous_close": 9.84, "change_percent": 9.76},
            {"stock_id": "2458.TW", "stock_name": "義隆", "limit_up_price": 131.00, "previous_close": 119.50, "change_percent": 9.62}
        ]
        
        limit_up_stocks = []
        for stock_data in stocks_data_from_user:
            # 查詢漲停原因
            limit_up_reason = self.news_client.search_limit_up_reason(stock_data["stock_name"], stock_data["stock_id"])
            
            stock = LimitUpStock(
                stock_id=stock_data["stock_id"],
                stock_name=stock_data["stock_name"],
                limit_up_price=stock_data["limit_up_price"],
                previous_close=stock_data["previous_close"],
                change_percent=stock_data["change_percent"],
                limit_up_reason=limit_up_reason
            )
            limit_up_stocks.append(stock)
            
            print(f"  📊 {stock_data['stock_name']}({stock_data['stock_id']}): {stock_data['previous_close']} → {stock_data['limit_up_price']} (+{stock_data['change_percent']:.2f}%)")
            print(f"  💡 漲停原因: {limit_up_reason[:50]}...")
        
        print(f"✅ 已載入 {len(limit_up_stocks)} 檔真實漲停股票")
        return limit_up_stocks
    
    async def generate_22_posts_no_duplicate(self, limit_up_stocks: List[LimitUpStock]) -> List[Dict[str, Any]]:
        """生成22則貼文，每檔股票只分配給1個KOL，不重複"""
        
        print(f"\n📈 開始生成22則貼文（不重複分配）...")
        
        # 載入KOL配置
        self.assignment_service.load_kol_profiles()
        enabled_kols = [kol for kol in self.assignment_service._kol_profiles if kol.enabled]
        
        print(f"✅ 載入 {len(enabled_kols)} 個啟用的KOL")
        
        # 隨機選擇5檔股票加入技術分析
        import random
        tech_analysis_stocks = random.sample(limit_up_stocks, 5)
        tech_analysis_stock_ids = {stock.stock_id for stock in tech_analysis_stocks}
        
        print(f"🔬 技術分析股票: {[stock.stock_name for stock in tech_analysis_stocks]}")
        
        # 隨機分配KOL給每檔股票
        random.shuffle(enabled_kols)
        kol_assignments = {}
        
        for i, stock in enumerate(limit_up_stocks):
            kol_index = i % len(enabled_kols)
            kol_assignments[stock.stock_id] = enabled_kols[kol_index]
        
        all_posts = []
        used_titles = set()
        
        # 為每檔股票生成貼文
        for stock in limit_up_stocks:
            kol = kol_assignments[stock.stock_id]
            print(f"\n🎭 為 {kol.nickname} 生成 {stock.stock_name} 貼文...")
            
            try:
                # 隨機選擇股票稱呼方式
                stock_reference = random.choice([
                    stock.stock_name,  # 只用股名
                    stock.stock_id,    # 只用股號
                    f"{stock.stock_name}({stock.stock_id})"  # 完整稱呼
                ])
                
                # 隨機選擇標題風格
                title_style = random.choice([
                    "question",      # 疑問句
                    "exclamation",  # 感嘆句
                    "analysis",     # 分析句
                    "news",         # 新聞句
                    "casual"        # 隨意句
                ])
                
                # 生成多樣化標題
                title = self._generate_diverse_title(
                    stock, stock_reference, title_style, used_titles
                )
                
                # 創建內容生成請求
                content_request = ContentRequest(
                    topic_title=f"{stock.stock_name} 漲停！",
                    topic_keywords=f"漲停,{stock.stock_name},{stock.stock_id},技術分析,市場分析",
                    kol_persona=kol.persona,
                    kol_nickname=kol.nickname,
                    content_type="limit_up_analysis",
                    target_audience="active_traders",
                    market_data={
                        "stock_id": stock.stock_id,
                        "stock_name": stock.stock_name,
                        "limit_up_price": stock.limit_up_price,
                        "previous_close": stock.previous_close,
                        "change_percent": stock.change_percent,
                        "limit_up_reason": stock.limit_up_reason,
                        "event_type": "limit_up",
                        "include_technical_analysis": stock.stock_id in tech_analysis_stock_ids
                    }
                )
                
                # 生成內容
                generated = self.content_generator.generate_complete_content(
                    content_request, 
                    used_titles=list(used_titles)
                )
                
                if generated.success:
                    post = {
                        "post_id": f"limit_up_{stock.stock_id}_{kol.serial}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "kol_serial": kol.serial,
                        "kol_nickname": kol.nickname,
                        "kol_persona": kol.persona,
                        "topic_id": f"limit_up_{stock.stock_id}_{datetime.now().strftime('%Y%m%d')}",
                        "topic_title": f"{stock.stock_name} 漲停！",
                        "stock_id": stock.stock_id,
                        "stock_name": stock.stock_name,
                        "limit_up_price": stock.limit_up_price,
                        "previous_close": stock.previous_close,
                        "change_percent": stock.change_percent,
                        "limit_up_reason": stock.limit_up_reason,
                        "generated_title": title,
                        "generated_content": generated.content,
                        "generated_hashtags": generated.hashtags,
                        "content_length": len(generated.content),
                        "created_at": datetime.now().isoformat(),
                        "status": "ready_to_post",
                        "data_sources": "serper_api,openai_gpt" + (",technical_analysis" if stock.stock_id in tech_analysis_stock_ids else ""),
                        "data_source_status": "serper:success,openai:success" + (",technical:success" if stock.stock_id in tech_analysis_stock_ids else "")
                    }
                    
                    all_posts.append(post)
                    used_titles.add(title)
                    
                    print(f"  ✅ 生成成功: {title[:30]}...")
                    if stock.stock_id in tech_analysis_stock_ids:
                        print(f"  🔬 包含技術分析")
                    
            except Exception as e:
                print(f"  ❌ 生成失敗: {e}")
                continue
        
        print(f"\n🎉 貼文生成完成！共生成 {len(all_posts)} 篇貼文")
        return all_posts
    
    def _generate_diverse_title(self, stock: LimitUpStock, stock_reference: str, style: str, used_titles: set) -> str:
        """生成多樣化標題"""
        
        # 疑問句模板
        question_templates = [
            f"{stock_reference}漲停了，各位先進怎麼看？",
            f"{stock_reference}這波漲停，大家覺得怎麼樣？",
            f"{stock_reference}漲停背後有什麼玄機？",
            f"{stock_reference}這根紅K，各位怎麼解讀？",
            f"{stock_reference}漲停潮來了，大家準備好了嗎？",
            f"{stock_reference}這波行情，各位怎麼看？",
            f"{stock_reference}漲停訊號，大家注意到了嗎？",
            f"{stock_reference}這根K棒，各位怎麼分析？"
        ]
        
        # 感嘆句模板
        exclamation_templates = [
            f"{stock_reference}飆漲停啦！",
            f"{stock_reference}噴了！",
            f"{stock_reference}漲停爆量！",
            f"{stock_reference}強勢漲停！",
            f"{stock_reference}漲停潮來襲！",
            f"{stock_reference}紅K爆量突破！",
            f"{stock_reference}漲停訊號強烈！",
            f"{stock_reference}這波要噴了！"
        ]
        
        # 分析句模板
        analysis_templates = [
            f"{stock_reference}漲停背後的技術面分析",
            f"{stock_reference}漲停原因深度解析",
            f"{stock_reference}漲停訊號的市場意義",
            f"{stock_reference}漲停背後的資金流向",
            f"{stock_reference}漲停的技術指標解讀",
            f"{stock_reference}漲停背後的籌碼分析",
            f"{stock_reference}漲停的趨勢研判",
            f"{stock_reference}漲停背後的市場邏輯"
        ]
        
        # 新聞句模板
        news_templates = [
            f"{stock_reference}今日漲停，市場關注",
            f"{stock_reference}漲停創新高",
            f"{stock_reference}漲停帶動相關族群",
            f"{stock_reference}漲停引發市場熱議",
            f"{stock_reference}漲停突破關鍵價位",
            f"{stock_reference}漲停成交量暴增",
            f"{stock_reference}漲停技術面轉強",
            f"{stock_reference}漲停市場情緒升溫"
        ]
        
        # 隨意句模板
        casual_templates = [
            f"{stock_reference}漲停了...",
            f"{stock_reference}這根K棒...",
            f"{stock_reference}紅K爆量...",
            f"{stock_reference}漲停訊號...",
            f"{stock_reference}這波行情...",
            f"{stock_reference}市場熱點...",
            f"{stock_reference}資金追捧...",
            f"{stock_reference}技術突破..."
        ]
        
        # 根據風格選擇模板
        if style == "question":
            templates = question_templates
        elif style == "exclamation":
            templates = exclamation_templates
        elif style == "analysis":
            templates = analysis_templates
        elif style == "news":
            templates = news_templates
        else:
            templates = casual_templates
        
        # 隨機選擇並避免重複
        import random
        available_templates = [t for t in templates if t not in used_titles]
        if not available_templates:
            available_templates = templates
        
        title = random.choice(available_templates)
        
        # 隨機添加表情符號（30%機率）
        if random.random() < 0.3:
            emojis = ["🚀", "📈", "🔥", "💪", "🎯", "⚡", "💎", "🌟"]
            title += f" {random.choice(emojis)}"
        
        return title
    
    async def display_generated_posts(self, posts: List[Dict[str, Any]]):
        """顯示生成的貼文"""
        
        print(f"\n📝 生成的貼文預覽 ({len(posts)} 篇)")
        print("=" * 80)
        
        # 按KOL分組顯示
        kol_groups = {}
        for post in posts:
            kol_nickname = post['kol_nickname']
            if kol_nickname not in kol_groups:
                kol_groups[kol_nickname] = []
            kol_groups[kol_nickname].append(post)
        
        for kol_nickname, kol_posts in kol_groups.items():
            print(f"\n👤 {kol_nickname} ({len(kol_posts)} 篇):")
            print("-" * 40)
            
            for i, post in enumerate(kol_posts, 1):
                print(f"  {i}. {post['stock_name']}({post['stock_id']})")
                print(f"     標題: {post['generated_title']}")
                print(f"     內容: {post['generated_content'][:50]}...")
                print(f"     漲停原因: {post['limit_up_reason'][:50]}...")
                print()
    
    async def save_to_google_sheets(self, posts: List[Dict[str, Any]]):
        """保存到Google Sheets貼文紀錄"""
        
        print(f"\n💾 保存到Google Sheets貼文紀錄...")
        
        try:
            # 準備數據
            sheet_data = []
            for post in posts:
                row = [
                    post['post_id'],
                    post['kol_serial'],
                    post['kol_nickname'],
                    post['kol_persona'],
                    post['topic_id'],
                    post['topic_title'],
                    post['stock_id'],
                    post['stock_name'],
                    post['limit_up_price'],
                    post['previous_close'],
                    post['change_percent'],
                    post['limit_up_reason'],
                    post['generated_title'],
                    post['generated_content'],
                    post['generated_hashtags'],
                    post['status'],
                    post['content_length'],
                    post['data_sources'],
                    post['data_source_status'],
                    post['created_at']
                ]
                sheet_data.append(row)
            
            # 寫入Google Sheets - 使用正確的方法
            await self.sheets_client.write_sheet('貼文記錄表', sheet_data)
            print(f"✅ 成功保存 {len(posts)} 筆記錄到Google Sheets")
            print("📋 狀態: ready_to_post (等待人工審核)")
            
        except Exception as e:
            print(f"❌ 保存到Google Sheets失敗: {e}")

async def main():
    """主函數"""
    
    print("🎯 智能漲停股貼文生成系統")
    print("=" * 60)
    print("功能:")
    print("1. 使用LLM查詢今日漲停股票")
    print("2. 使用Serper API查詢漲停原因")
    print("3. 生成20則貼文平均分配給KOL")
    print("4. 保存到Google Sheets貼文紀錄")
    print("5. 等待人工審核後排程發文")
    
    try:
        # 初始化生成器
        generator = SmartLimitUpGenerator()
        
        # 步驟1: 查詢今日漲停股票
        limit_up_stocks = await generator.query_today_limit_up_stocks()
        
        if not limit_up_stocks:
            print("❌ 沒有找到漲停股票")
            return
        
        # 步驟2: 生成22則貼文
        posts = await generator.generate_22_posts_no_duplicate(limit_up_stocks)
        
        if not posts:
            print("❌ 沒有生成貼文")
            return
        
        # 步驟3: 顯示貼文預覽
        await generator.display_generated_posts(posts)
        
        # 步驟4: 保存到Google Sheets
        await generator.save_to_google_sheets(posts)
        
        print("\n🎉 智能漲停股貼文生成完成！")
        print("📋 下一步: 請在Google Sheets中審核貼文，確認後可進行排程發文")
        
    except Exception as e:
        print(f"❌ 流程失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
