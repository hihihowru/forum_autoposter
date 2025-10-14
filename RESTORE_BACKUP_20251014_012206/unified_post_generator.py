#!/usr/bin/env python3
"""
統一貼文生成架構
整合熱門話題和漲停股流程，提供可重用的函數化設計
"""

import asyncio
import json
import logging
import os
import sys
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
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

@dataclass
class PostData:
    """貼文資料結構"""
    post_id: str
    kol_serial: int
    kol_nickname: str
    stock_name: str
    stock_id: str
    topic_id: str
    generated_title: str
    generated_content: str
    commodity_tags: List[Dict[str, Any]]
    status: str = "pending"
    technical_analysis: Optional[Dict] = None
    serper_data: Optional[Dict] = None

@dataclass
class TopicData:
    """話題資料結構"""
    topic_id: str
    title: str
    content: str
    stocks: List[Dict[str, str]]
    classification: Optional[str] = None

class UnifiedPostGenerator:
    """統一貼文生成器"""
    
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
        
        # 載入KOL資料
        self.assignment_service.load_kol_profiles()
        self.kol_profiles = self.assignment_service._kol_profiles
        
        logger.info(f"✅ 統一貼文生成器初始化完成，載入 {len(self.kol_profiles)} 個KOL")
    
    def generate_limit_up_posts(self, limit_up_stocks: List[Dict], 
                               include_technical_analysis: bool = True,
                               technical_analysis_ratio: float = 0.2) -> List[PostData]:
        """
        生成漲停股貼文
        
        Args:
            limit_up_stocks: 漲停股列表
            include_technical_analysis: 是否包含技術分析
            technical_analysis_ratio: 技術分析比例
            
        Returns:
            生成的貼文列表
        """
        logger.info(f"🚀 開始生成 {len(limit_up_stocks)} 篇漲停股貼文...")
        
        # 隨機選擇股票進行技術分析
        technical_count = int(len(limit_up_stocks) * technical_analysis_ratio)
        technical_stocks = random.sample(limit_up_stocks, technical_count) if include_technical_analysis else []
        technical_stock_ids = [stock['id'] for stock in technical_stocks]
        
        generated_posts = []
        
        for i, stock in enumerate(limit_up_stocks):
            try:
                # 分配KOL (確保不重複)
                kol = self.kol_profiles[i % len(self.kol_profiles)]
                
                # 生成標題
                title = self._generate_diverse_title(stock, i)
                
                # 生成內容
                content = self._generate_limit_up_content(stock, kol, stock['id'] in technical_stock_ids)
                
                # 準備commodity tags
                commodity_tags = [{"type": "Stock", "key": stock['id'].replace('.TW', '').replace('.TWO', ''), "bullOrBear": 0}]
                
                # 生成post_id
                post_id = f"limit_up_{stock['id'].replace('.', '_')}_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                post = PostData(
                    post_id=post_id,
                    kol_serial=kol.serial,
                    kol_nickname=kol.nickname,
                    stock_name=stock['name'],
                    stock_id=stock['id'],
                    topic_id='limit_up_stocks',
                    generated_title=title,
                    generated_content=content,
                    commodity_tags=commodity_tags,
                    status='pending'
                )
                
                generated_posts.append(post)
                logger.info(f"✅ 生成第 {i+1}/{len(limit_up_stocks)} 篇貼文: {stock['name']} - {title[:50]}...")
                
            except Exception as e:
                logger.error(f"❌ 生成第 {i+1} 篇貼文失敗: {e}")
        
        logger.info(f"🎯 完成生成 {len(generated_posts)} 篇漲停股貼文！")
        return generated_posts
    
    def generate_trending_topic_posts(self, topics: List[TopicData], 
                                    include_technical_analysis: bool = True,
                                    technical_analysis_ratio: float = 0.3) -> List[PostData]:
        """
        生成熱門話題貼文
        
        Args:
            topics: 話題列表
            include_technical_analysis: 是否包含技術分析
            technical_analysis_ratio: 技術分析比例
            
        Returns:
            生成的貼文列表
        """
        logger.info(f"🚀 開始生成 {len(topics)} 篇熱門話題貼文...")
        
        generated_posts = []
        
        for i, topic in enumerate(topics):
            try:
                # 為每個話題的股票生成貼文
                for j, stock in enumerate(topic.stocks):
                    # 分配KOL
                    kol = self.kol_profiles[(i + j) % len(self.kol_profiles)]
                    
                    # 生成標題
                    title = self._generate_trending_title(topic, stock, i, j)
                    
                    # 生成內容
                    content = self._generate_trending_content(topic, stock, kol, include_technical_analysis)
                    
                    # 準備commodity tags
                    commodity_tags = [{"type": "Stock", "key": stock['id'].replace('.TW', '').replace('.TWO', ''), "bullOrBear": 0}]
                    
                    # 生成post_id
                    post_id = f"trending_{topic.topic_id}_{stock['id'].replace('.', '_')}_{i+1}_{j+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    post = PostData(
                        post_id=post_id,
                        kol_serial=kol.serial,
                        kol_nickname=kol.nickname,
                        stock_name=stock['name'],
                        stock_id=stock['id'],
                        topic_id=topic.topic_id,
                        generated_title=title,
                        generated_content=content,
                        commodity_tags=commodity_tags,
                        status='pending'
                    )
                    
                    generated_posts.append(post)
                    logger.info(f"✅ 生成話題貼文: {topic.title[:30]}... - {stock['name']}")
                
            except Exception as e:
                logger.error(f"❌ 生成話題 {topic.topic_id} 貼文失敗: {e}")
        
        logger.info(f"🎯 完成生成 {len(generated_posts)} 篇熱門話題貼文！")
        return generated_posts
    
    def _generate_diverse_title(self, stock: Dict, index: int) -> str:
        """生成多樣化的標題"""
        stock_name = stock['name']
        stock_id = stock['id'].replace('.TW', '').replace('.TWO', '')
        
        # 隨機選擇標題風格
        styles = ['question', 'exclamation', 'analysis', 'news', 'casual']
        style = random.choice(styles)
        
        # 隨機選擇股票引用方式 - 只使用股名，不使用股號
        stock_references = [
            f"{stock_name}",
            f"{stock_name}",
            f"{stock_name}"
        ]
        stock_ref = random.choice(stock_references)
        
        # 標題模板
        templates = {
            'question': [
                f"{stock_ref}昨日漲停，各位先進怎麼看？",
                f"{stock_ref}昨日這波行情，大家覺得怎麼樣？",
                f"{stock_ref}昨日強勢漲停，後市如何？",
                f"{stock_ref}昨日噴了！各位怎麼看？"
            ],
            'exclamation': [
                f"{stock_ref}昨日漲停！",
                f"{stock_ref}昨日噴了！",
                f"{stock_ref}昨日強勢漲停！",
                f"{stock_ref}昨日飆漲停！"
            ],
            'analysis': [
                f"{stock_ref}昨日漲停背後的資金流向",
                f"{stock_ref}昨日漲停的趨勢研判",
                f"{stock_ref}昨日漲停突破關鍵價位",
                f"{stock_ref}昨日漲停成交量暴增"
            ],
            'news': [
                f"{stock_ref}昨日漲停市場情緒升溫",
                f"{stock_ref}昨日漲停創新高",
                f"{stock_ref}昨日漲停紅K爆量",
                f"{stock_ref}昨日這根K棒..."
            ],
            'casual': [
                f"{stock_ref}昨日漲停潮來了，大家準備好了嗎？",
                f"{stock_ref}昨日這波行情...",
                f"{stock_ref}昨日漲停的節奏",
                f"{stock_ref}昨日這根紅K，各位怎麼解讀？"
            ]
        }
        
        title = random.choice(templates[style])
        
        # 30%機率添加emoji
        if random.random() < 0.3:
            emojis = ["🚀", "📈", "🔥", "💪", "🎯", "⚡", "💎", "🌟"]
            title += f" {random.choice(emojis)}"
        
        return title
    
    def _generate_trending_title(self, topic: TopicData, stock: Dict, topic_index: int, stock_index: int) -> str:
        """生成熱門話題標題"""
        stock_name = stock['name']
        stock_id = stock['id'].replace('.TW', '').replace('.TWO', '')
        
        # 話題相關標題模板
        templates = [
            f"{stock_name}搭上{topic.title[:20]}熱潮",
            f"{stock_name}({stock_id})受惠{topic.title[:15]}題材",
            f"{stock_name}因{topic.title[:15]}大漲",
            f"{stock_name}搭{topic.title[:10]}順風車",
            f"{stock_name}這波{topic.title[:10]}行情",
            f"{stock_name}因{topic.title[:15]}題材發酵"
        ]
        
        title = random.choice(templates)
        
        # 20%機率添加emoji
        if random.random() < 0.2:
            emojis = ["🚀", "📈", "🔥", "💪", "🎯", "⚡"]
            title += f" {random.choice(emojis)}"
        
        return title
    
    def _generate_limit_up_content(self, stock: Dict, kol, include_technical: bool = False) -> str:
        """生成漲停股內容"""
        try:
            # 基礎內容模板 - 標記為昨天分析
            base_content = f"""
📅 **昨日(9/2)分析** 📅

{stock['name']}({stock['id']})昨日強勢漲停！股價從{float(stock['price']) - float(stock['change']):.2f}元飆升至{stock['price']}元，漲幅達{stock['change_pct']}！

從技術面來看，{stock['name']}昨日跳空開高，成交量明顯放大，顯示買盤動能強勁。MACD指標呈現黃金交叉，KD指標也進入超買區間，技術面支撐強勁。

基本面方面，{stock['name']}近期在產業發展上取得重要突破，市場對其未來發展前景看好。外資和法人買盤持續湧入，顯示機構投資者對該股的認同度提升。

⚠️ **提醒：昨日漲停不代表今日表現，投資者需謹慎評估今日開盤後的走勢變化**

不過投資者仍需注意，漲停後可能面臨獲利了結賣壓，建議關注後續的技術面表現和基本面發展。追高需謹慎，投資有風險，入市需謹慎。

各位先進對{stock['name']}昨日這波漲停行情有什麼看法？今日開盤後會如何發展？
"""
            
            # 如果需要技術分析，添加更詳細的技術分析
            if include_technical:
                technical_analysis = f"""

🔍 **昨日技術分析深度解析**：
• 日K線：跳空缺口，突破前期高點
• 成交量：較前日放大{random.randint(2, 5)}倍，量價配合良好
• RSI：{random.randint(65, 85)}，處於強勢區間
• 布林通道：股價突破上軌，顯示強勢
• 支撐位：{float(stock['price']) * 0.95:.2f}元
• 阻力位：{float(stock['price']) * 1.05:.2f}元

⚠️ **今日開盤後需關注：**
• 是否出現獲利了結賣壓
• 成交量是否持續放大
• 技術指標是否維持強勢

建議關注後續的技術面表現，特別是成交量的變化。
"""
                base_content += technical_analysis
            
            return base_content.strip()
            
        except Exception as e:
            logger.error(f"生成內容失敗: {e}")
            return f"📅 **昨日(9/2)分析** 📅\n\n{stock['name']}({stock['id']})昨日漲停！各位先進怎麼看？今日開盤後會如何發展？"
    
    def _generate_trending_content(self, topic: TopicData, stock: Dict, kol, include_technical: bool = False) -> str:
        """生成熱門話題內容"""
        try:
            base_content = f"""
{stock['name']}({stock['id']})搭上{topic.title}熱潮，股價表現亮眼！

從基本面來看，{stock['name']}因{topic.title}題材發酵，市場關注度大幅提升。相關產業發展前景看好，投資者對該股的期待值上升。

技術面方面，{stock['name']}近期成交量明顯放大，顯示買盤動能強勁。MACD指標呈現上升趨勢，KD指標也進入強勢區間，技術面支撐良好。

{topic.title}這個話題持續發酵，相關概念股都有不錯的表現。{stock['name']}作為相關產業的重要標的，值得投資者關注。

不過投資者仍需注意，題材股可能面臨波動風險，建議關注後續的產業發展和公司基本面變化。投資有風險，入市需謹慎。

各位先進對{stock['name']}這波{topic.title}行情有什麼看法？歡迎留言討論！
"""
            
            return base_content.strip()
            
        except Exception as e:
            logger.error(f"生成話題內容失敗: {e}")
            return f"{stock['name']}({stock['id']})搭上{topic.title}熱潮！各位先進怎麼看？"
    
    def save_to_google_sheets(self, posts: List[PostData]) -> bool:
        """保存到Google Sheets"""
        try:
            # 準備數據
            sheet_data = []
            for post in posts:
                row = [
                    post.post_id,
                    post.kol_serial,
                    post.kol_nickname,
                    post.stock_name,
                    post.stock_id,
                    post.topic_id,
                    '',  # G欄位
                    '',  # H欄位
                    post.generated_title,
                    post.generated_content,
                    json.dumps(post.commodity_tags),
                    post.status  # L欄位 - Status
                ]
                sheet_data.append(row)
            
            # 使用append寫入Google Sheets
            self.sheets_client.append_sheet('貼文記錄表', sheet_data)
            logger.info(f"✅ 成功保存 {len(posts)} 篇貼文到Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"保存到Google Sheets失敗: {e}")
            return False
    
    def save_to_json(self, posts: List[PostData], filename: str = None) -> bool:
        """保存到本地JSON文件"""
        try:
            if filename is None:
                filename = f"generated_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 轉換為字典格式
            posts_dict = []
            for post in posts:
                post_dict = {
                    'post_id': post.post_id,
                    'kol_serial': post.kol_serial,
                    'kol_nickname': post.kol_nickname,
                    'stock_name': post.stock_name,
                    'stock_id': post.stock_id,
                    'topic_id': post.topic_id,
                    'generated_title': post.generated_title,
                    'generated_content': post.generated_content,
                    'commodity_tags': post.commodity_tags,
                    'status': post.status,
                    'technical_analysis': post.technical_analysis,
                    'serper_data': post.serper_data
                }
                posts_dict.append(post_dict)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts_dict, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 成功保存到 {filename}")
            return True
            
        except Exception as e:
            logger.error(f"保存JSON文件失敗: {e}")
            return False
    
    def preview_posts(self, posts: List[PostData], count: int = 3) -> None:
        """預覽貼文內容"""
        logger.info(f"\n📋 前{count}篇貼文預覽:")
        for i, post in enumerate(posts[:count]):
            logger.info(f"\n=== 第 {i+1} 篇 ===")
            logger.info(f"KOL: {post.kol_nickname}")
            logger.info(f"股票: {post.stock_name}({post.stock_id})")
            logger.info(f"標題: {post.generated_title}")
            logger.info(f"內容: {post.generated_content[:200]}...")

# 使用範例
def main():
    """主函數 - 使用範例"""
    generator = UnifiedPostGenerator()
    
    # 範例1: 生成漲停股貼文
    limit_up_stocks = [
        {"name": "立凱-KY", "id": "5227.TWO", "price": "32.45", "change": "2.95", "change_pct": "10.00%"},
        {"name": "笙科", "id": "5272.TWO", "price": "23.10", "change": "2.10", "change_pct": "10.00%"},
        {"name": "太欣", "id": "5302.TWO", "price": "9.90", "change": "0.90", "change_pct": "10.00%"}
    ]
    
    posts = generator.generate_limit_up_posts(limit_up_stocks, include_technical_analysis=True)
    
    # 保存到Google Sheets
    generator.save_to_google_sheets(posts)
    
    # 保存到JSON
    generator.save_to_json(posts)
    
    # 預覽貼文
    generator.preview_posts(posts)

if __name__ == "__main__":
    main()
