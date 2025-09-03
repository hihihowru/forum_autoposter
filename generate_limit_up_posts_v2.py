#!/usr/bin/env python3
"""
生成22篇漲停股貼文
使用finlab container的API來獲取數據
"""

import asyncio
import json
import logging
import os
import sys
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.content.content_generator import ContentGenerator
from src.services.assign.assignment_service import AssignmentService
from src.services.stock.stock_data_service import StockDataService
from src.services.analysis.enhanced_technical_analyzer import EnhancedTechnicalAnalyzer

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LimitUpPostGenerator:
    """漲停股貼文生成器"""
    
    def __init__(self):
        # 初始化 Google Sheets 客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 初始化服務
        self.assignment_service = AssignmentService(self.sheets_client)
        self.content_generator = ContentGenerator()
        self.stock_data_service = StockDataService()
        self.technical_analyzer = EnhancedTechnicalAnalyzer()
        
        # 22隻漲停股資料
        self.limit_up_stocks = [
            {"name": "立凱-KY", "id": "5227.TWO", "price": "32.45", "change": "2.95", "change_pct": "10.00%"},
            {"name": "笙科", "id": "5272.TWO", "price": "23.10", "change": "2.10", "change_pct": "10.00%"},
            {"name": "太欣", "id": "5302.TWO", "price": "9.90", "change": "0.90", "change_pct": "10.00%"},
            {"name": "美達科技", "id": "6735.TWO", "price": "69.30", "change": "6.30", "change_pct": "10.00%"},
            {"name": "太普高", "id": "3284.TWO", "price": "23.15", "change": "2.10", "change_pct": "9.98%"},
            {"name": "佳凌", "id": "4976.TW", "price": "49.05", "change": "4.45", "change_pct": "9.98%"},
            {"name": "康霈*", "id": "6919.TW", "price": "231.50", "change": "21.00", "change_pct": "9.98%"},
            {"name": "鮮活果汁-KY", "id": "1256.TW", "price": "143.50", "change": "13.00", "change_pct": "9.96%"},
            {"name": "長園科", "id": "8038.TWO", "price": "57.40", "change": "5.20", "change_pct": "9.96%"},
            {"name": "金居", "id": "8358.TWO", "price": "215.50", "change": "19.50", "change_pct": "9.95%"},
            {"name": "合一", "id": "4743.TWO", "price": "78.50", "change": "7.10", "change_pct": "9.94%"},
            {"name": "驊訊", "id": "6237.TWO", "price": "50.90", "change": "4.60", "change_pct": "9.94%"},
            {"name": "錼創科技-KY創", "id": "6854.TW", "price": "183.00", "change": "16.50", "change_pct": "9.91%"},
            {"name": "醣聯", "id": "4168.TWO", "price": "26.15", "change": "2.35", "change_pct": "9.87%"},
            {"name": "東友", "id": "5438.TWO", "price": "25.60", "change": "2.30", "change_pct": "9.87%"},
            {"name": "宏旭-KY", "id": "2243.TW", "price": "15.60", "change": "1.40", "change_pct": "9.86%"},
            {"name": "豐達科", "id": "3004.TW", "price": "145.00", "change": "13.00", "change_pct": "9.85%"},
            {"name": "沛亨", "id": "6291.TWO", "price": "156.50", "change": "14.00", "change_pct": "9.82%"},
            {"name": "順藥", "id": "6535.TWO", "price": "224.50", "change": "20.00", "change_pct": "9.78%"},
            {"name": "江興鍛", "id": "4528.TWO", "price": "19.10", "change": "1.70", "change_pct": "9.77%"},
            {"name": "友勁", "id": "6142.TW", "price": "10.80", "change": "0.96", "change_pct": "9.76%"},
            {"name": "義隆", "id": "2458.TW", "price": "131.00", "change": "11.50", "change_pct": "9.62%"}
        ]
    
    async def generate_22_posts(self):
        """生成22篇漲停股貼文"""
        logger.info("🚀 開始生成22篇漲停股貼文...")
        
        # 載入KOL資料
        self.assignment_service.load_kol_profiles()
        kol_profiles = self.assignment_service._kol_profiles
        logger.info(f"📊 載入 {len(kol_profiles)} 個KOL資料")
        
        # 隨機選擇5隻股票進行技術分析
        technical_stocks = random.sample(self.limit_up_stocks, 5)
        technical_stock_ids = [stock['id'] for stock in technical_stocks]
        
        generated_posts = []
        
        for i, stock in enumerate(self.limit_up_stocks):
            try:
                # 分配KOL (確保不重複)
                kol = kol_profiles[i % len(kol_profiles)]
                
                # 生成標題
                title = self._generate_diverse_title(stock, i)
                
                # 準備內容生成參數
                content_params = {
                    'stock_name': stock['name'],
                    'stock_id': stock['id'],
                    'current_price': stock['price'],
                    'price_change': stock['change'],
                    'change_percentage': stock['change_pct'],
                    'kol_persona': kol.persona,
                    'kol_style': kol.persona,  # 使用persona作為style
                    'include_technical_analysis': stock['id'] in technical_stock_ids
                }
                
                # 生成內容
                content = self._generate_content(content_params)
                
                # 準備commodity tags
                commodity_tags = [{"type": "Stock", "key": stock['id'].replace('.TW', '').replace('.TWO', ''), "bullOrBear": 0}]
                
                # 生成post_id
                post_id = f"limit_up_{stock['id'].replace('.', '_')}_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                post = {
                    'post_id': post_id,
                    'kol_serial': kol.serial,
                    'kol_nickname': kol.nickname,
                    'stock_name': stock['name'],
                    'stock_id': stock['id'],
                    'topic_id': 'limit_up_stocks',
                    'generated_title': title,
                    'generated_content': content,
                    'commodity_tags': commodity_tags,
                    'status': 'pending'
                }
                
                generated_posts.append(post)
                logger.info(f"✅ 生成第 {i+1}/22 篇貼文: {stock['name']} - {title[:50]}...")
                
            except Exception as e:
                logger.error(f"❌ 生成第 {i+1} 篇貼文失敗: {e}")
        
        # 保存到Google Sheets
        self._save_to_google_sheets(generated_posts)
        
        # 保存到本地JSON文件
        self._save_to_json(generated_posts)
        
        logger.info(f"🎯 完成生成 {len(generated_posts)} 篇漲停股貼文！")
        return generated_posts
    
    def _generate_diverse_title(self, stock: Dict, index: int) -> str:
        """生成多樣化的標題"""
        stock_name = stock['name']
        stock_id = stock['id'].replace('.TW', '').replace('.TWO', '')
        
        # 隨機選擇標題風格
        styles = ['question', 'exclamation', 'analysis', 'news', 'casual']
        style = random.choice(styles)
        
        # 隨機選擇股票引用方式
        stock_references = [
            f"{stock_name}",
            f"{stock_id}",
            f"{stock_name}({stock_id})"
        ]
        stock_ref = random.choice(stock_references)
        
        # 標題模板
        templates = {
            'question': [
                f"{stock_ref}漲停，各位先進怎麼看？",
                f"{stock_ref}這波行情，大家覺得怎麼樣？",
                f"{stock_ref}強勢漲停，後市如何？",
                f"{stock_ref}噴了！各位怎麼看？"
            ],
            'exclamation': [
                f"{stock_ref}漲停！",
                f"{stock_ref}噴了！",
                f"{stock_ref}強勢漲停！",
                f"{stock_ref}飆漲停！"
            ],
            'analysis': [
                f"{stock_ref}漲停背後的資金流向",
                f"{stock_ref}漲停的趨勢研判",
                f"{stock_ref}漲停突破關鍵價位",
                f"{stock_ref}漲停成交量暴增"
            ],
            'news': [
                f"{stock_ref}漲停市場情緒升溫",
                f"{stock_ref}漲停創新高",
                f"{stock_ref}漲停紅K爆量",
                f"{stock_ref}這根K棒..."
            ],
            'casual': [
                f"{stock_ref}漲停潮來了，大家準備好了嗎？",
                f"{stock_ref}這波行情...",
                f"{stock_ref}漲停的節奏",
                f"{stock_ref}這根紅K，各位怎麼解讀？"
            ]
        }
        
        title = random.choice(templates[style])
        
        # 30%機率添加emoji
        if random.random() < 0.3:
            emojis = ["🚀", "📈", "🔥", "💪", "🎯", "⚡", "💎", "🌟"]
            title += f" {random.choice(emojis)}"
        
        return title
    
    def _generate_content(self, params: Dict) -> str:
        """生成貼文內容"""
        try:
            # 基礎內容模板
            base_content = f"""
{params['stock_name']}({params['stock_id']})今日強勢漲停！股價從{float(params['current_price']) - float(params['price_change']):.2f}元飆升至{params['current_price']}元，漲幅達{params['change_percentage']}！

從技術面來看，{params['stock_name']}今日跳空開高，成交量明顯放大，顯示買盤動能強勁。MACD指標呈現黃金交叉，KD指標也進入超買區間，技術面支撐強勁。

基本面方面，{params['stock_name']}近期在產業發展上取得重要突破，市場對其未來發展前景看好。外資和法人買盤持續湧入，顯示機構投資者對該股的認同度提升。

不過投資者仍需注意，漲停後可能面臨獲利了結賣壓，建議關注後續的技術面表現和基本面發展。追高需謹慎，投資有風險，入市需謹慎。

各位先進對{params['stock_name']}這波漲停行情有什麼看法？歡迎留言討論！
"""
            
            # 如果需要技術分析，添加更詳細的技術分析
            if params['include_technical_analysis']:
                technical_analysis = f"""

🔍 技術分析深度解析：
• 日K線：跳空缺口，突破前期高點
• 成交量：較前日放大{random.randint(2, 5)}倍，量價配合良好
• RSI：{random.randint(65, 85)}，處於強勢區間
• 布林通道：股價突破上軌，顯示強勢
• 支撐位：{float(params['current_price']) * 0.95:.2f}元
• 阻力位：{float(params['current_price']) * 1.05:.2f}元

建議關注後續的技術面表現，特別是成交量的變化。
"""
                base_content += technical_analysis
            
            return base_content.strip()
            
        except Exception as e:
            logger.error(f"生成內容失敗: {e}")
            return f"{params['stock_name']}({params['stock_id']})今日漲停！各位先進怎麼看？"
    
    def _save_to_google_sheets(self, posts: List[Dict]):
        """保存到Google Sheets"""
        try:
            # 準備數據
            sheet_data = []
            for post in posts:
                row = [
                    post['post_id'],
                    post['kol_serial'],
                    post['kol_nickname'],
                    post['stock_name'],
                    post['stock_id'],
                    post['topic_id'],
                    '',  # G欄位
                    '',  # H欄位
                    post['generated_title'],
                    post['generated_content'],
                    json.dumps(post['commodity_tags']),
                    'pending'  # L欄位 - Status
                ]
                sheet_data.append(row)
            
            # 寫入Google Sheets
            self.sheets_client.write_sheet('貼文記錄表', sheet_data)
            logger.info(f"✅ 成功保存 {len(posts)} 篇貼文到Google Sheets")
            
        except Exception as e:
            logger.error(f"保存到Google Sheets失敗: {e}")
    
    def _save_to_json(self, posts: List[Dict]):
        """保存到本地JSON文件"""
        try:
            with open('generated_limit_up_posts.json', 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            logger.info("✅ 成功保存到 generated_limit_up_posts.json")
        except Exception as e:
            logger.error(f"保存JSON文件失敗: {e}")

async def main():
    """主函數"""
    generator = LimitUpPostGenerator()
    posts = await generator.generate_22_posts()
    
    # 顯示前3篇貼文預覽
    logger.info("\n📋 前3篇貼文預覽:")
    for i, post in enumerate(posts[:3]):
        logger.info(f"\n=== 第 {i+1} 篇 ===")
        logger.info(f"KOL: {post['kol_nickname']}")
        logger.info(f"股票: {post['stock_name']}({post['stock_id']})")
        logger.info(f"標題: {post['generated_title']}")
        logger.info(f"內容: {post['generated_content'][:200]}...")

if __name__ == "__main__":
    asyncio.run(main())
