"""
快速漲停股貼文生成腳本
直接輸入漲停股票，快速生成貼文並發布
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent / "src"))

from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.services.assign.assignment_service import AssignmentService
from src.services.publish.publish_service import PublishService

class QuickLimitUpGenerator:
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.assignment_service = AssignmentService()
        self.publish_service = PublishService()
        print("🚀 快速漲停股貼文生成器初始化完成")
    
    async def process_limit_up_stocks(self, stocks_data):
        """處理漲停股票數據"""
        print(f"\n📈 開始處理 {len(stocks_data)} 檔漲停股票")
        
        # 載入KOL配置
        self.assignment_service.load_kol_profiles()
        print(f"✅ 載入 {len(self.assignment_service._kol_profiles)} 個KOL")
        
        all_posts = []
        
        for stock_data in stocks_data:
            stock_id = stock_data['stock_id']
            stock_name = stock_data['stock_name']
            limit_up_price = stock_data['limit_up_price']
            previous_close = stock_data['previous_close']
            
            print(f"\n📊 處理: {stock_name}({stock_id})")
            
            topic_title = f"{stock_name}({stock_id}) 漲停！"
            change_percent = ((limit_up_price - previous_close) / previous_close) * 100
            
            # 為每個KOL生成貼文
            for kol in self.assignment_service._kol_profiles:
                if not kol.enabled:
                    continue
                
                try:
                    content_request = ContentRequest(
                        topic_title=topic_title,
                        topic_keywords=f"漲停,{stock_name},{stock_id},技術分析",
                        kol_persona=kol.persona,
                        kol_nickname=kol.nickname,
                        content_type="limit_up_analysis",
                        target_audience="active_traders"
                    )
                    
                    generated = self.content_generator.generate_complete_content(content_request)
                    
                    if generated.success:
                        post = {
                            "kol_serial": kol.serial,
                            "kol_nickname": kol.nickname,
                            "stock_id": stock_id,
                            "stock_name": stock_name,
                            "title": generated.title,
                            "content": generated.content,
                            "topic_id": f"limit_up_{stock_id}_{datetime.now().strftime('%Y%m%d')}"
                        }
                        all_posts.append(post)
                        print(f"  ✅ {kol.nickname}: {generated.title[:30]}...")
                    
                except Exception as e:
                    print(f"  ❌ {kol.nickname} 生成失敗: {e}")
        
        return all_posts
    
    async def display_posts(self, posts):
        """顯示生成的貼文"""
        print(f"\n📝 生成 {len(posts)} 篇貼文:")
        print("=" * 60)
        
        for i, post in enumerate(posts, 1):
            print(f"\n【第 {i} 篇】")
            print(f"KOL: {post['kol_nickname']}")
            print(f"股票: {post['stock_name']}({post['stock_id']})")
            print(f"標題: {post['title']}")
            print(f"內容: {post['content'][:100]}...")
            print("-" * 40)
    
    async def publish_posts(self, posts):
        """發布貼文"""
        confirm = input("\n是否開始發文？(y/N): ").strip().lower()
        if confirm != 'y':
            print("取消發文")
            return
        
        # KOL登入憑證
        credentials = {
            200: {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x"},
            201: {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t"},
            202: {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p"}
        }
        
        # 登入KOL
        kol_serials = list(set([post['kol_serial'] for post in posts]))
        for kol_serial in kol_serials:
            if kol_serial in credentials:
                success = await self.publish_service.login_kol(
                    kol_serial,
                    credentials[kol_serial]["email"],
                    credentials[kol_serial]["password"]
                )
                print(f"{'✅' if success else '❌'} KOL {kol_serial} 登入")
        
        # 發文
        success_count = 0
        for i, post in enumerate(posts, 1):
            print(f"\n📤 發文第 {i} 篇: {post['kol_nickname']}")
            
            try:
                result = await self.publish_service.publish_post(
                    kol_serial=post['kol_serial'],
                    title=post['title'],
                    content=post['content'],
                    topic_id=post['topic_id']
                )
                
                if result and result.success:
                    print(f"✅ 發文成功: {result.post_id}")
                    success_count += 1
                else:
                    print(f"❌ 發文失敗: {result.error_message if result else 'Unknown error'}")
                
                # 間隔2分鐘
                if i < len(posts):
                    print("等待 2 分鐘...")
                    await asyncio.sleep(120)
                    
            except Exception as e:
                print(f"❌ 發文異常: {e}")
        
        print(f"\n🎉 發文完成！成功 {success_count}/{len(posts)} 篇")

async def main():
    print("🎯 快速漲停股貼文生成系統")
    print("=" * 40)
    
    # 示例：今天的漲停股票（您可以替換為實際的漲停股票）
    limit_up_stocks = [
        {
            "stock_id": "2330",
            "stock_name": "台積電",
            "limit_up_price": 580.0,
            "previous_close": 528.0
        },
        {
            "stock_id": "2317", 
            "stock_name": "鴻海",
            "limit_up_price": 105.0,
            "previous_close": 95.5
        },
        {
            "stock_id": "2454",
            "stock_name": "聯發科", 
            "limit_up_price": 890.0,
            "previous_close": 810.0
        }
    ]
    
    print("📊 今天的漲停股票:")
    for stock in limit_up_stocks:
        change_percent = ((stock['limit_up_price'] - stock['previous_close']) / stock['previous_close']) * 100
        print(f"  - {stock['stock_name']}({stock['stock_id']}): {stock['previous_close']} → {stock['limit_up_price']} (+{change_percent:.1f}%)")
    
    try:
        generator = QuickLimitUpGenerator()
        
        # 生成貼文
        posts = await generator.process_limit_up_stocks(limit_up_stocks)
        if not posts:
            print("❌ 沒有生成貼文")
            return
        
        # 顯示貼文
        await generator.display_posts(posts)
        
        # 發布貼文
        await generator.publish_posts(posts)
        
        print("\n🎉 完成！")
        
    except Exception as e:
        print(f"❌ 失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())











