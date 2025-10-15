#!/usr/bin/env python3
"""
第四隻觸發器貼文生成器
生成盤後漲停股回顧貼文並更新到貼文紀錄
"""

import os
import sys
import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
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

@dataclass
class LimitUpStock:
    """漲停股票資料結構"""
    stock_id: str
    stock_name: str
    change_percent: float
    volume_amount: float
    volume_rank: int
    rank_type: str

@dataclass
class GeneratedPostRecord:
    """生成的貼文記錄"""
    post_id: str
    kol_serial: str
    kol_nickname: str
    kol_id: str
    persona: str
    content_type: str
    topic_index: int
    topic_id: str
    topic_title: str
    topic_keywords: str
    content: str
    status: str
    scheduled_time: str
    post_time: str
    error_message: str
    platform_post_id: str
    platform_post_url: str
    trending_topic_title: str

class LimitUpPostGenerator:
    """漲停股貼文生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.config_manager = ConfigManager()
        self.sheets_client = GoogleSheetsClient(
            credentials_file=self.config_manager.get_config().google.credentials_file,
            spreadsheet_id=self.config_manager.get_config().google.spreadsheet_id
        )
        self.content_generator = ContentGenerator()
        
        # 股票名稱對應表（修正版）
        self.stock_names = {
            "3665": "貿聯-KY", "3653": "健策", "5314": "世紀鋼", "6753": "龍德造船",
            "8039": "台虹", "3707": "漢磊", "3704": "合勤控", "4303": "信立",
            "1605": "華新", "2353": "宏碁", "5345": "天揚", "2724": "台嘉碩",
            "6264": "精拓科", "8906": "高力", "2380": "虹光"
        }
        
        logger.info("漲停股貼文生成器初始化完成")
    
    def get_limit_up_stocks(self) -> List[LimitUpStock]:
        """獲取今日漲停股票列表（模擬數據）"""
        # 這裡使用模擬數據，實際應該調用 Finlab API
        stocks = [
            # 有量漲停（成交金額高到低）
            LimitUpStock("3665", "貿聯-KY", 9.62, 86.3432, 1, "成交金額排名"),
            LimitUpStock("3653", "健策", 9.93, 59.4404, 2, "成交金額排名"),
            LimitUpStock("5314", "世紀鋼", 9.91, 31.8937, 3, "成交金額排名"),
            LimitUpStock("6753", "龍德造船", 9.78, 31.4252, 4, "成交金額排名"),
            LimitUpStock("8039", "台虹", 10.00, 20.2122, 5, "成交金額排名"),
            LimitUpStock("3707", "漢磊", 9.83, 15.3369, 6, "成交金額排名"),
            LimitUpStock("3704", "合勤控", 9.98, 14.4642, 7, "成交金額排名"),
            LimitUpStock("4303", "信立", 9.99, 11.6107, 8, "成交金額排名"),
            LimitUpStock("1605", "華新", 9.89, 10.3519, 9, "成交金額排名"),
            LimitUpStock("2353", "宏碁", 10.00, 9.5462, 10, "成交金額排名"),
            
            # 無量漲停（成交金額低到高）
            LimitUpStock("5345", "天揚", 9.95, 0.0164, 1, "成交金額排名（無量）"),
            LimitUpStock("2724", "台嘉碩", 9.95, 0.0306, 2, "成交金額排名（無量）"),
            LimitUpStock("6264", "精拓科", 10.00, 0.0326, 3, "成交金額排名（無量）"),
            LimitUpStock("8906", "高力", 10.00, 0.0380, 4, "成交金額排名（無量）"),
            LimitUpStock("2380", "虹光", 9.97, 0.0406, 5, "成交金額排名（無量）")
        ]
        
        return stocks
    
    def format_volume_amount(self, amount_billion: float) -> str:
        """格式化成交金額顯示"""
        if amount_billion >= 1.0:
            return f"{amount_billion:.4f}億元"
        else:
            amount_million = amount_billion * 100
            return f"{amount_million:.2f}百萬元"
    
    def get_kol_settings(self) -> List[Dict[str, Any]]:
        """獲取 KOL 設定"""
        try:
            kol_settings = self.config_manager.get_kol_personalization_settings()
            return [
                {
                    'serial': serial,
                    'nickname': settings['persona'],
                    'member_id': settings.get('member_id', ''),
                    'persona': settings['persona'],
                    'settings': settings
                }
                for serial, settings in kol_settings.items()
            ]
        except Exception as e:
            logger.error(f"獲取 KOL 設定失敗: {e}")
            # 返回預設 KOL
            return [
                {
                    'serial': '200',
                    'nickname': '川川哥',
                    'member_id': '9505548',
                    'persona': '新聞派',
                    'settings': {'persona': '新聞派', 'content_length': 'medium'}
                }
            ]
    
    async def generate_post_for_stock(self, stock: LimitUpStock, kol: Dict[str, Any]) -> Optional[GeneratedPostRecord]:
        """為特定股票和 KOL 生成貼文"""
        try:
            logger.info(f"為 {kol['nickname']} 生成 {stock.stock_name} 貼文")
            
            # 格式化成交金額
            formatted_volume = self.format_volume_amount(stock.volume_amount)
            
            # 建構話題標題和關鍵字
            topic_title = f"{stock.stock_name}({stock.stock_id}) 今日漲停！{stock.rank_type}第{stock.volume_rank}名"
            topic_keywords = f"{stock.stock_name},{stock.stock_id},漲停,成交金額,{stock.rank_type}"
            
            # 創建內容生成請求
            content_request = ContentRequest(
                topic_title=topic_title,
                topic_keywords=topic_keywords,
                kol_persona=kol['persona'],
                kol_nickname=kol['nickname'],
                content_type="investment",
                target_audience="active_traders",
                market_data={
                    'stock_id': stock.stock_id,
                    'stock_name': stock.stock_name,
                    'change_percent': stock.change_percent,
                    'volume_amount': formatted_volume,
                    'volume_rank': stock.volume_rank,
                    'rank_type': stock.rank_type
                }
            )
            
            # 生成內容
            result = self.content_generator.generate_complete_content(content_request)
            
            if not result.success:
                logger.error(f"內容生成失敗: {result.error_message}")
                return None
            
            # 生成貼文記錄
            post_id = f"limit_up_{stock.stock_id}_{kol['serial']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            post_record = GeneratedPostRecord(
                post_id=post_id,
                kol_serial=kol['serial'],
                kol_nickname=kol['nickname'],
                kol_id=kol['member_id'],
                persona=kol['persona'],
                content_type="investment",
                topic_index=1,
                topic_id=f"limit_up_{stock.stock_id}_{datetime.now().strftime('%Y%m%d')}",
                topic_title=topic_title,
                topic_keywords=topic_keywords,
                content=result.content,
                status="ready_to_post",
                scheduled_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                post_time="",
                error_message="",
                platform_post_id="",
                platform_post_url="",
                trending_topic_title="盤後漲停股回顧"
            )
            
            logger.info(f"✅ 成功生成 {kol['nickname']} 的 {stock.stock_name} 貼文")
            return post_record
            
        except Exception as e:
            logger.error(f"生成貼文失敗: {e}")
            return None
    
    async def update_post_records(self, posts: List[GeneratedPostRecord]):
        """更新貼文記錄到 Google Sheets"""
        try:
            logger.info(f"開始更新 {len(posts)} 筆貼文記錄")
            
            # 準備記錄數據
            records = []
            for post in posts:
                record = [
                    post.post_id,           # A: 貼文ID
                    post.kol_serial,        # B: KOL Serial
                    post.kol_nickname,      # C: KOL 暱稱
                    post.kol_id,            # D: KOL ID
                    post.persona,           # E: Persona
                    post.content_type,      # F: Content Type
                    post.topic_index,       # G: 已派發TopicIndex
                    post.topic_id,          # H: 已派發TopicID
                    post.topic_title,       # I: 已派發TopicTitle
                    post.topic_keywords,    # J: 已派發TopicKeywords
                    post.content,           # K: 生成內容
                    post.status,            # L: 發文狀態
                    post.scheduled_time,    # M: 上次排程時間
                    post.post_time,         # N: 發文時間戳記
                    post.error_message,     # O: 最近錯誤訊息
                    post.platform_post_id,  # P: 平台發文ID
                    post.platform_post_url, # Q: 平台發文URL
                    post.trending_topic_title # R: 熱門話題標題
                ]
                records.append(record)
            
            # 寫入 Google Sheets
            await self.sheets_client.append_sheet("PostRecords", records)
            
            logger.info(f"✅ 成功更新 {len(posts)} 筆貼文記錄到 Google Sheets")
            
        except Exception as e:
            logger.error(f"更新貼文記錄失敗: {e}")
            raise
    
    async def run(self):
        """執行完整的貼文生成流程"""
        try:
            logger.info("🚀 開始執行第四隻觸發器貼文生成流程")
            
            # 步驟1: 獲取漲停股票
            stocks = self.get_limit_up_stocks()
            logger.info(f"📈 獲取到 {len(stocks)} 檔漲停股票")
            
            # 步驟2: 獲取 KOL 設定
            kol_settings = self.get_kol_settings()
            logger.info(f"👥 獲取到 {len(kol_settings)} 個 KOL 設定")
            
            # 步驟3: 生成貼文
            generated_posts = []
            
            for i, stock in enumerate(stocks):
                # 選擇 KOL（簡單輪流分配）
                kol = kol_settings[i % len(kol_settings)]
                
                # 生成貼文
                post_record = await self.generate_post_for_stock(stock, kol)
                
                if post_record:
                    generated_posts.append(post_record)
                    print(f"✅ 第 {i+1} 篇: {kol['nickname']} - {stock.stock_name}({stock.stock_id})")
                    print(f"   標題: {post_record.topic_title}")
                    print(f"   內容長度: {len(post_record.content)} 字")
                    print(f"   成交金額: {self.format_volume_amount(stock.volume_amount)}")
                    print("-" * 50)
                else:
                    print(f"❌ 第 {i+1} 篇生成失敗: {stock.stock_name}")
            
            # 步驟4: 更新貼文記錄
            if generated_posts:
                await self.update_post_records(generated_posts)
                print(f"\n🎉 貼文生成完成！總共生成 {len(generated_posts)} 篇貼文")
                print(f"📊 已更新到貼文記錄表")
            else:
                print("❌ 沒有成功生成任何貼文")
            
        except Exception as e:
            logger.error(f"貼文生成流程執行失敗: {e}")
            raise

async def main():
    """主函數"""
    try:
        generator = LimitUpPostGenerator()
        await generator.run()
        
    except Exception as e:
        logger.error(f"主程序執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
