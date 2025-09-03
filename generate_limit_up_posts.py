"""
漲停股貼文生成和發布腳本
專門處理今天漲停的股票，生成貼文並發布
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.services.assign.assignment_service import AssignmentService
from src.services.publish.publish_service import PublishService
from clients.google.sheets_client import GoogleSheetsClient

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
    change_percent: float = 9.8

class LimitUpPostGenerator:
    """漲停股貼文生成器"""
    
    def __init__(self):
        """初始化"""
        self.content_generator = ContentGenerator()
        self.assignment_service = AssignmentService()
        self.publish_service = PublishService()
        
        # 初始化 Google Sheets 客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        print("🚀 漲停股貼文生成器初始化完成")
    
    def create_limit_up_topic(self, stock: LimitUpStock) -> Dict[str, Any]:
        """為漲停股票創建話題"""
        return {
            "id": f"limit_up_{stock.stock_id}_{datetime.now().strftime('%Y%m%d')}",
            "title": f"{stock.stock_name}({stock.stock_id}) 漲停！",
            "content": f"{stock.stock_name}今日以{stock.limit_up_price}元漲停，漲幅{stock.change_percent}%，從{stock.previous_close}元大漲至{stock.limit_up_price}元。",
            "stock_symbols": [stock.stock_id],
            "topic_type": "limit_up",
            "created_at": datetime.now().isoformat()
        }
    
    async def generate_posts_for_limit_up_stocks(self, limit_up_stocks: List[LimitUpStock]) -> List[Dict[str, Any]]:
        """為漲停股票生成貼文"""
        
        print(f"\n📈 開始處理 {len(limit_up_stocks)} 檔漲停股票")
        print("=" * 60)
        
        # 步驟1: 載入KOL配置
        print("\n👥 步驟1: 載入KOL配置...")
        self.assignment_service.load_kol_profiles()
        print(f"✅ 載入 {len(self.assignment_service._kol_profiles)} 個KOL配置")
        
        # 步驟2: 為每檔漲停股票生成貼文
        print("\n✍️ 步驟2: 生成貼文...")
        all_posts = []
        
        for i, stock in enumerate(limit_up_stocks, 1):
            print(f"\n📊 處理第 {i} 檔漲停股票: {stock.stock_name}({stock.stock_id})")
            
            # 創建話題
            topic = self.create_limit_up_topic(stock)
            
            # 為每個KOL生成貼文
            kol_posts = await self._generate_posts_for_topic(topic, stock)
            all_posts.extend(kol_posts)
            
            print(f"  ✅ 為 {stock.stock_name} 生成 {len(kol_posts)} 篇貼文")
        
        print(f"\n🎉 貼文生成完成！共生成 {len(all_posts)} 篇貼文")
        return all_posts
    
    async def _generate_posts_for_topic(self, topic: Dict[str, Any], stock: LimitUpStock) -> List[Dict[str, Any]]:
        """為單個話題生成貼文"""
        
        posts = []
        used_titles = set()
        
        # 為每個KOL生成貼文
        for kol in self.assignment_service._kol_profiles:
            if not kol.enabled:
                continue
                
            try:
                print(f"  🎭 為 {kol.nickname} 生成貼文...")
                
                # 創建內容生成請求
                content_request = ContentRequest(
                    topic_title=topic["title"],
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
                        "event_type": "limit_up"
                    }
                )
                
                # 生成內容
                generated = self.content_generator.generate_complete_content(
                    content_request, 
                    used_titles=list(used_titles)
                )
                
                if generated.success:
                    post = {
                        "post_id": f"{topic['id']}-{kol.serial}",
                        "kol_serial": kol.serial,
                        "kol_nickname": kol.nickname,
                        "kol_persona": kol.persona,
                        "topic_id": topic["id"],
                        "topic_title": topic["title"],
                        "stock_id": stock.stock_id,
                        "stock_name": stock.stock_name,
                        "generated_title": generated.title,
                        "generated_content": generated.content,
                        "generated_hashtags": generated.hashtags,
                        "content_length": len(generated.content),
                        "created_at": datetime.now().isoformat(),
                        "status": "ready_to_post"
                    }
                    
                    posts.append(post)
                    if generated.title:
                        used_titles.add(generated.title)
                    
                    print(f"    ✅ 生成成功: {generated.title[:30]}...")
                else:
                    print(f"    ❌ 生成失敗: {generated.error_message}")
                    
            except Exception as e:
                print(f"    ❌ 生成異常: {e}")
                continue
        
        return posts
    
    async def display_generated_posts(self, posts: List[Dict[str, Any]]):
        """顯示生成的貼文"""
        
        print(f"\n📝 準備發文內容 ({len(posts)} 篇)")
        print("=" * 80)
        
        for i, post in enumerate(posts, 1):
            print(f"\n【第 {i} 篇】")
            print(f"Post ID: {post['post_id']}")
            print(f"KOL: {post['kol_nickname']} ({post['kol_persona']})")
            print(f"股票: {post['stock_name']}({post['stock_id']})")
            print(f"話題: {post['topic_title']}")
            print(f"標題: {post['generated_title']}")
            print(f"內容長度: {post['content_length']} 字")
            print(f"內容預覽: {post['generated_content'][:100]}...")
            print(f"標籤: {post['generated_hashtags']}")
            print("-" * 80)
    
    async def publish_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """發布貼文"""
        
        print(f"\n📤 開始發布 {len(posts)} 篇貼文")
        print("=" * 60)
        
        # 確認發文
        confirm = input("是否開始發文？(y/N): ").strip().lower()
        
        if confirm != 'y':
            print("取消發文")
            return []
        
        # KOL 登入憑證
        kol_credentials = {
            200: {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x"},
            201: {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t"},
            202: {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p"}
        }
        
        # 登入需要的KOL
        kol_serials = list(set([post['kol_serial'] for post in posts]))
        print(f"\n🔐 登入 {len(kol_serials)} 個KOL帳號...")
        
        for kol_serial in kol_serials:
            if kol_serial in kol_credentials:
                print(f"登入 KOL {kol_serial}...")
                success = await self.publish_service.login_kol(
                    kol_serial,
                    kol_credentials[kol_serial]["email"],
                    kol_credentials[kol_serial]["password"]
                )
                if success:
                    print(f"✅ KOL {kol_serial} 登入成功")
                else:
                    print(f"❌ KOL {kol_serial} 登入失敗")
        
        # 發文
        results = []
        success_count = 0
        
        for i, post in enumerate(posts, 1):
            print(f"\n📤 發文第 {i} 篇: {post['post_id']}")
            print(f"KOL: {post['kol_nickname']}")
            print(f"標題: {post['generated_title']}")
            
            try:
                result = await self.publish_service.publish_post(
                    kol_serial=post['kol_serial'],
                    title=post['generated_title'],
                    content=post['generated_content'],
                    topic_id=post['topic_id']
                )
                
                if result and result.success:
                    print(f"✅ 發文成功: {result.post_id}")
                    success_count += 1
                    
                    # 更新結果
                    post_result = {
                        **post,
                        "published": True,
                        "article_id": result.post_id,
                        "article_url": result.post_url,
                        "published_at": datetime.now().isoformat(),
                        "error_message": None
                    }
                else:
                    print(f"❌ 發文失敗: {result.error_message if result else 'Unknown error'}")
                    
                    post_result = {
                        **post,
                        "published": False,
                        "article_id": None,
                        "article_url": None,
                        "published_at": None,
                        "error_message": result.error_message if result else 'Unknown error'
                    }
                
                results.append(post_result)
                
                # 間隔2分鐘
                if i < len(posts):
                    print("等待 2 分鐘...")
                    await asyncio.sleep(120)
                    
            except Exception as e:
                print(f"❌ 發文異常: {e}")
                post_result = {
                    **post,
                    "published": False,
                    "article_id": None,
                    "article_url": None,
                    "published_at": None,
                    "error_message": str(e)
                }
                results.append(post_result)
        
        print(f"\n🎉 發文完成！成功發文 {success_count}/{len(posts)} 篇")
        return results
    
    async def save_results_to_sheets(self, results: List[Dict[str, Any]]):
        """將結果保存到Google Sheets"""
        
        if not results:
            return
        
        print(f"\n💾 保存結果到Google Sheets...")
        
        try:
            # 準備數據
            sheet_data = []
            for result in results:
                row = [
                    result['post_id'],
                    result['kol_serial'],
                    result['kol_nickname'],
                    result['kol_persona'],
                    result['topic_id'],
                    result['topic_title'],
                    result['stock_id'],
                    result['stock_name'],
                    result['generated_title'],
                    result['generated_content'],
                    result['generated_hashtags'],
                    result['status'],
                    result.get('published', False),
                    result.get('published_at', ''),
                    result.get('error_message', ''),
                    result.get('article_id', ''),
                    result.get('article_url', ''),
                    result['created_at']
                ]
                sheet_data.append(row)
            
            # 寫入Google Sheets
            await self.sheets_client.append_rows('貼文記錄表', sheet_data)
            print(f"✅ 成功保存 {len(results)} 筆記錄到Google Sheets")
            
        except Exception as e:
            print(f"❌ 保存到Google Sheets失敗: {e}")

async def main():
    """主函數"""
    
    # 示例：今天的漲停股票（您可以替換為實際的漲停股票）
    limit_up_stocks = [
        LimitUpStock(
            stock_id="2330",
            stock_name="台積電",
            limit_up_price=580.0,
            previous_close=528.0,
            change_percent=9.8
        ),
        LimitUpStock(
            stock_id="2317",
            stock_name="鴻海",
            limit_up_price=105.0,
            previous_close=95.5,
            change_percent=9.9
        ),
        LimitUpStock(
            stock_id="2454",
            stock_name="聯發科",
            limit_up_price=890.0,
            previous_close=810.0,
            change_percent=9.9
        )
    ]
    
    print("🎯 漲停股貼文生成和發布系統")
    print("=" * 60)
    print(f"📊 處理 {len(limit_up_stocks)} 檔漲停股票:")
    for stock in limit_up_stocks:
        print(f"  - {stock.stock_name}({stock.stock_id}): {stock.previous_close} → {stock.limit_up_price} (+{stock.change_percent}%)")
    
    # 確認開始
    confirm = input(f"\n是否開始生成貼文？(y/N): ").strip().lower()
    if confirm != 'y':
        print("取消操作")
        return
    
    try:
        # 初始化生成器
        generator = LimitUpPostGenerator()
        
        # 生成貼文
        posts = await generator.generate_posts_for_limit_up_stocks(limit_up_stocks)
        
        if not posts:
            print("❌ 沒有生成任何貼文")
            return
        
        # 顯示生成的貼文
        await generator.display_generated_posts(posts)
        
        # 發布貼文
        results = await generator.publish_posts(posts)
        
        # 保存結果
        await generator.save_results_to_sheets(results)
        
        print("\n🎉 漲停股貼文處理完成！")
        
    except Exception as e:
        print(f"❌ 流程失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
