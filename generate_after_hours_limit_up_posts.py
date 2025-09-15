#!/usr/bin/env python3
"""
盤後漲停股回顧貼文生成器
生成 10篇有量漲停 + 5篇無量漲停 的貼文
"""

import os
import sys
import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.utils.config_manager import ConfigManager

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AfterHoursLimitUpPostGenerator:
    """盤後漲停股貼文生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.config = ConfigManager()
        
        # 初始化 Google Sheets 客戶端
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google-service-account.json')
        spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
        self.sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        self.content_generator = ContentGenerator()
        
        # 股票名稱對應表（修正版）
        self.stock_names = {
            "3665": "貿聯-KY", "3653": "健策", "5314": "世紀鋼", "6753": "龍德造船",
            "8039": "台虹", "3707": "漢磊", "3704": "合勤控", "4303": "信立",
            "1605": "華新", "2353": "宏碁", "5345": "天揚", "2724": "台嘉碩",
            "6264": "精拓科", "8906": "高力", "2380": "虹光"
        }
    
    def _format_volume_amount(self, amount_billion: float) -> str:
        """格式化成交金額顯示"""
        if amount_billion >= 1.0:
            return f"{amount_billion:.4f}億元"
        else:
            amount_million = amount_billion * 100
            return f"{amount_million:.2f}百萬元"
    
    def get_stock_name(self, stock_id: str) -> str:
        """獲取股票名稱"""
        return self.stock_names.get(stock_id, f"股票{stock_id}")
    
    def create_sample_limit_up_stocks(self) -> List[Dict]:
        """創建樣本漲停股票數據（10有量 + 5無量）"""
        # 有量漲停股票（成交金額高到低）
        high_volume_stocks = [
            {"stock_id": "3665", "change_percent": 9.8, "volume_amount": 15.2, "rank": 1},
            {"stock_id": "3653", "change_percent": 9.9, "volume_amount": 12.8, "rank": 2},
            {"stock_id": "5314", "change_percent": 9.7, "volume_amount": 10.5, "rank": 3},
            {"stock_id": "6753", "change_percent": 9.6, "volume_amount": 9.2, "rank": 4},
            {"stock_id": "8039", "change_percent": 9.8, "volume_amount": 8.7, "rank": 5},
            {"stock_id": "3707", "change_percent": 9.9, "volume_amount": 7.3, "rank": 6},
            {"stock_id": "3704", "change_percent": 9.7, "volume_amount": 6.8, "rank": 7},
            {"stock_id": "4303", "change_percent": 9.6, "volume_amount": 5.9, "rank": 8},
            {"stock_id": "1605", "change_percent": 9.8, "volume_amount": 4.2, "rank": 9},
            {"stock_id": "2353", "change_percent": 9.9, "volume_amount": 3.1, "rank": 10}
        ]
        
        # 無量漲停股票（成交金額低到高）
        low_volume_stocks = [
            {"stock_id": "5345", "change_percent": 9.8, "volume_amount": 0.0164, "rank": 1},
            {"stock_id": "2724", "change_percent": 9.9, "volume_amount": 0.0306, "rank": 2},
            {"stock_id": "6264", "change_percent": 9.7, "volume_amount": 0.0326, "rank": 3},
            {"stock_id": "8906", "change_percent": 9.6, "volume_amount": 0.0380, "rank": 4},
            {"stock_id": "2380", "change_percent": 9.8, "volume_amount": 0.0406, "rank": 5}
        ]
        
        return high_volume_stocks + low_volume_stocks
    
    async def generate_post_content(self, stock: Dict, is_high_volume: bool) -> str:
        """生成單篇貼文內容"""
        stock_name = self.get_stock_name(stock["stock_id"])
        volume_formatted = self._format_volume_amount(stock["volume_amount"])
        rank_type = "成交金額排名" if is_high_volume else "成交金額排名（無量）"
        
        # 根據有量/無量選擇不同的內容模板
        if is_high_volume:
            template = f"""📈 盤後漲停股回顧 - {stock_name}({stock["stock_id"]})

🔥 今日漲停亮點：{stock_name}強勢漲停{stock["change_percent"]:.1f}%！

📊 市場焦點：
• 成交金額排名：第{stock["rank"]}名
• 成交金額：{volume_formatted}
• 漲幅：{stock["change_percent"]:.1f}%

💡 投資亮點：
• 市場資金積極進場，顯示強烈買盤
• 成交量放大，支撐股價續漲動能
• 技術面突破，後市可期

🔍 關注重點：
• 明日開盤表現
• 成交量是否持續放大
• 相關產業動態

#漲停股 #盤後回顧 #{stock_name} #成交量大 #市場熱點"""
        else:
            template = f"""📈 盤後漲停股回顧 - {stock_name}({stock["stock_id"]})

💎 無量漲停亮點：{stock_name}無量漲停{stock["change_percent"]:.1f}%！

📊 籌碼分析：
• 成交金額排名（無量）：第{stock["rank"]}名
• 成交金額：{volume_formatted}
• 漲幅：{stock["change_percent"]:.1f}%

💡 投資亮點：
• 籌碼高度集中，賣壓輕微
• 無量上漲，顯示強烈續漲意願
• 技術面強勢，突破關鍵價位

🔍 關注重點：
• 明日成交量變化
• 籌碼集中度維持
• 相關消息面發展

#漲停股 #盤後回顧 #{stock_name} #無量上漲 #籌碼集中"""
        
        return template
    
    async def generate_all_posts(self) -> List[Dict]:
        """生成所有15篇貼文"""
        logger.info("🚀 開始生成盤後漲停股回顧貼文...")
        
        stocks = self.create_sample_limit_up_stocks()
        posts = []
        
        # 生成有量漲停貼文（前10篇）
        logger.info("📈 生成有量漲停貼文（前10篇）...")
        for i, stock in enumerate(stocks[:10]):
            content = await self.generate_post_content(stock, is_high_volume=True)
            post = {
                "post_id": f"limit_up_high_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "stock_id": stock["stock_id"],
                "stock_name": self.get_stock_name(stock["stock_id"]),
                "content": content,
                "type": "有量漲停",
                "volume_rank": stock["rank"],
                "volume_amount": stock["volume_amount"],
                "change_percent": stock["change_percent"],
                "created_at": datetime.now().isoformat(),
                "status": "generated"
            }
            posts.append(post)
            logger.info(f"✅ 生成第{i+1}篇有量漲停貼文：{post['stock_name']}")
        
        # 生成無量漲停貼文（後5篇）
        logger.info("💎 生成無量漲停貼文（後5篇）...")
        for i, stock in enumerate(stocks[10:15]):
            content = await self.generate_post_content(stock, is_high_volume=False)
            post = {
                "post_id": f"limit_up_low_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "stock_id": stock["stock_id"],
                "stock_name": self.get_stock_name(stock["stock_id"]),
                "content": content,
                "type": "無量漲停",
                "volume_rank": stock["rank"],
                "volume_amount": stock["volume_amount"],
                "change_percent": stock["change_percent"],
                "created_at": datetime.now().isoformat(),
                "status": "generated"
            }
            posts.append(post)
            logger.info(f"✅ 生成第{i+1}篇無量漲停貼文：{post['stock_name']}")
        
        logger.info(f"🎉 總共生成 {len(posts)} 篇貼文")
        return posts
    
    async def update_post_records(self, posts: List[Dict]):
        """更新貼文紀錄到 Google Sheets"""
        logger.info("📝 更新貼文紀錄到 Google Sheets...")
        
        try:
            # 準備記錄數據
            records = []
            for post in posts:
                record = [
                    post["post_id"],
                    post["stock_id"],
                    post["stock_name"],
                    post["type"],
                    f"第{post['volume_rank']}名",
                    f"{post['volume_amount']:.4f}億元",
                    f"{post['change_percent']:.1f}%",
                    post["created_at"],
                    post["status"],
                    "盤後漲停股回顧"
                ]
                records.append(record)
            
            # 寫入 Google Sheets
            await self.sheets_client.append_sheet("PostRecords", records)
            logger.info(f"✅ 成功更新 {len(records)} 筆貼文紀錄")
            
        except Exception as e:
            logger.error(f"❌ 更新貼文紀錄失敗：{e}")
            raise
    
    async def run(self):
        """執行完整的貼文生成流程"""
        try:
            logger.info("🎯 開始盤後漲停股回顧貼文生成流程")
            
            # 1. 生成所有貼文
            posts = await self.generate_all_posts()
            
            # 2. 更新貼文紀錄
            await self.update_post_records(posts)
            
            # 3. 顯示結果摘要
            self.show_summary(posts)
            
            logger.info("🎉 盤後漲停股回顧貼文生成完成！")
            
        except Exception as e:
            logger.error(f"❌ 貼文生成流程失敗：{e}")
            raise
    
    def show_summary(self, posts: List[Dict]):
        """顯示結果摘要"""
        print("\n" + "="*60)
        print("📊 盤後漲停股回顧貼文生成摘要")
        print("="*60)
        
        high_volume_count = len([p for p in posts if p["type"] == "有量漲停"])
        low_volume_count = len([p for p in posts if p["type"] == "無量漲停"])
        
        print(f"📈 有量漲停貼文：{high_volume_count} 篇")
        print(f"💎 無量漲停貼文：{low_volume_count} 篇")
        print(f"📝 總貼文數：{len(posts)} 篇")
        print(f"📅 生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📋 貼文清單：")
        for i, post in enumerate(posts, 1):
            volume_formatted = self._format_volume_amount(post["volume_amount"])
            print(f"{i:2d}. {post['stock_name']}({post['stock_id']}) - {post['type']} - 排名第{post['volume_rank']}名 - {volume_formatted}")
        
        print("\n" + "="*60)

async def main():
    """主函數"""
    generator = AfterHoursLimitUpPostGenerator()
    await generator.run()

if __name__ == "__main__":
    asyncio.run(main())
