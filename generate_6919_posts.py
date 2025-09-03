#!/usr/bin/env python3
"""
6919 股票貼文生成腳本
為兩個 KOL 生成與 6919 相關的貼文，包含技術派分析
"""

import asyncio
import json
import logging
from datetime import datetime
import os
import sys
from typing import Dict, List, Any

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.google.sheets_client import GoogleSheetsClient
from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from services.content.enhanced_prompt_generator import EnhancedPromptGenerator
from services.content.content_generator import ContentGenerator
from services.stock.technical_analyzer import TechnicalAnalyzer
from services.stock.finlab_client import FinlabClient

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Stock6919PostGenerator:
    """6919 股票貼文生成器"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient(
            credentials_file='./credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        self.cmoney_client = CMoneyClient()
        self.prompt_generator = EnhancedPromptGenerator()
        self.content_generator = ContentGenerator()
        self.technical_analyzer = TechnicalAnalyzer()
        self.finlab_client = FinlabClient()
        
    async def get_kol_credentials(self) -> List[Dict[str, Any]]:
        """獲取 KOL 帳號資訊"""
        try:
            data = self.sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            if not data or len(data) < 2:
                logger.error("無法讀取 KOL 帳號資料")
                return []
            
            headers = data[0]
            kol_data = []
            
            for row in data[1:]:
                if len(row) >= 5 and row[0]:  # 確保有基本資料
                    kol = {
                        'serial': row[0],
                        'nickname': row[1],
                        'member_id': row[2],
                        'password': row[3],
                        'persona': row[4] if len(row) > 4 else '一般',
                        'status': row[5] if len(row) > 5 else '啟用'
                    }
                    kol_data.append(kol)
            
            return kol_data
            
        except Exception as e:
            logger.error(f"獲取 KOL 資料失敗: {e}")
            return []
    
    async def get_stock_6919_data(self) -> Dict[str, Any]:
        """獲取 6919 股票數據"""
        try:
            # 獲取技術分析數據
            technical_data = await self.technical_analyzer.get_enhanced_stock_analysis('6919')
            
            # 獲取 Finlab 數據
            finlab_data = await self.finlab_client.get_stock_data('6919')
            
            # 組合股票數據
            stock_data = {
                'symbol': '6919',
                'name': '世紀鋼',
                'technical_analysis': technical_data,
                'finlab_data': finlab_data,
                'current_price': technical_data.get('current_price', 0),
                'change_percent': technical_data.get('change_percent', 0),
                'volume': technical_data.get('volume', 0),
                'market_cap': technical_data.get('market_cap', 0)
            }
            
            logger.info(f"成功獲取 6919 股票數據")
            return stock_data
            
        except Exception as e:
            logger.error(f"獲取 6919 股票數據失敗: {e}")
            return {}
    
    def generate_6919_topics(self) -> List[Dict[str, Any]]:
        """生成 6919 相關話題"""
        topics = [
            {
                'title': '世紀鋼(6919)技術面分析：支撐位與阻力位關鍵點位',
                'keywords': '世紀鋼,6919,技術分析,支撐位,阻力位,鋼鐵股',
                'content_type': 'technical',
                'analysis_angle': '技術面分析'
            },
            {
                'title': '6919世紀鋼基本面觀察：鋼鐵產業復甦跡象',
                'keywords': '世紀鋼,6919,基本面,鋼鐵產業,營收,獲利',
                'content_type': 'fundamental',
                'analysis_angle': '基本面分析'
            },
            {
                'title': '世紀鋼(6919)量價關係：成交量放大背後的意義',
                'keywords': '世紀鋼,6919,成交量,量價關係,技術指標',
                'content_type': 'technical',
                'analysis_angle': '量價分析'
            }
        ]
        return topics
    
    async def generate_kol_post(self, kol: Dict[str, Any], topic: Dict[str, Any], stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """為特定 KOL 生成貼文"""
        try:
            logger.info(f"為 {kol['nickname']} 生成 6919 相關貼文")
            
            # 準備股票摘要
            stock_summary = self._prepare_stock_summary(stock_data)
            
            # 生成增強版 Prompt
            enhanced_prompt = self.prompt_generator.generate_enhanced_prompt(
                kol_serial=kol['serial'],
                kol_nickname=kol['nickname'],
                persona=kol['persona'],
                topic_title=topic['title'],
                stock_data=stock_summary,
                market_context="台股今日震盪整理，鋼鐵股表現相對強勢",
                stock_names=['6919', '世紀鋼']
            )
            
            # 生成內容
            content_result = await self.content_generator.generate_complete_content(
                request={
                    'kol_nickname': kol['nickname'],
                    'persona': kol['persona'],
                    'topic_title': topic['title'],
                    'topic_keywords': topic['keywords'],
                    'content_type': topic['content_type'],
                    'stock_data': stock_data
                }
            )
            
            if content_result and content_result.success:
                # 添加 commoditytags
                hashtags = self._generate_6919_hashtags(topic['content_type'])
                
                post_data = {
                    'post_id': f"6919_{kol['serial']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'kol_serial': kol['serial'],
                    'kol_nickname': kol['nickname'],
                    'kol_id': kol['member_id'],
                    'persona': kol['persona'],
                    'content_type': topic['content_type'],
                    'topic_id': f"6919_{topic['content_type']}",
                    'topic_title': topic['title'],
                    'content': content_result.content,
                    'status': '待發布',
                    'post_time': datetime.now().isoformat(),
                    'platform_post_id': '',
                    'platform_post_url': '',
                    'post_type': 'analysis',
                    'content_length': 'medium',
                    'kol_weight_settings': json.dumps({
                        'post_types': {
                            'technical': {'weight': 0.8, 'style': '技術派', 'description': '技術分析為主'},
                            'fundamental': {'weight': 0.6, 'style': '基本面', 'description': '基本面分析'}
                        }
                    }),
                    'content_generation_time': datetime.now().isoformat(),
                    'kol_settings_version': 'v2.0',
                    'hashtags': hashtags,
                    'stock_symbol': '6919',
                    'stock_name': '世紀鋼',
                    'analysis_angle': topic['analysis_angle']
                }
                
                logger.info(f"✅ 成功生成 {kol['nickname']} 的貼文")
                return post_data
            else:
                logger.error(f"❌ 生成 {kol['nickname']} 貼文失敗")
                return None
                
        except Exception as e:
            logger.error(f"生成 {kol['nickname']} 貼文時發生錯誤: {e}")
            return None
    
    def _prepare_stock_summary(self, stock_data: Dict[str, Any]) -> str:
        """準備股票摘要"""
        if not stock_data:
            return "無股票數據"
        
        summary = f"""
股票代號：{stock_data.get('symbol', '6919')}
股票名稱：{stock_data.get('name', '世紀鋼')}
當前價格：{stock_data.get('current_price', 'N/A')}
漲跌幅：{stock_data.get('change_percent', 'N/A')}%
成交量：{stock_data.get('volume', 'N/A')}
市值：{stock_data.get('market_cap', 'N/A')}
"""
        
        # 添加技術分析數據
        technical = stock_data.get('technical_analysis', {})
        if technical:
            summary += f"""
技術指標：
- MACD：{technical.get('macd', 'N/A')}
- RSI：{technical.get('rsi', 'N/A')}
- 布林通道：{technical.get('bollinger', 'N/A')}
- 支撐位：{technical.get('support', 'N/A')}
- 阻力位：{technical.get('resistance', 'N/A')}
"""
        
        return summary
    
    def _generate_6919_hashtags(self, content_type: str) -> str:
        """生成 6919 相關的 hashtags"""
        base_tags = [
            "#6919", "#世紀鋼", "#台股", "#鋼鐵股", "#commoditytags"
        ]
        
        if content_type == 'technical':
            base_tags.extend(["#技術分析", "#K線", "#MACD", "#RSI"])
        elif content_type == 'fundamental':
            base_tags.extend(["#基本面", "#營收", "#獲利", "#產業分析"])
        
        # 添加鋼鐵相關標籤
        base_tags.extend(["#鋼鐵", "#製造業", "#原物料"])
        
        return " ".join(base_tags)
    
    async def update_posts_sheet(self, posts: List[Dict[str, Any]]):
        """更新貼文記錄表"""
        try:
            # 讀取現有數據
            existing_data = self.sheets_client.read_sheet('貼文記錄表', 'A:Z')
            
            # 準備新數據
            new_rows = []
            for post in posts:
                row = [
                    post['post_id'],
                    post['kol_serial'],
                    post['kol_nickname'],
                    post['kol_id'],
                    post['persona'],
                    post['content_type'],
                    post['topic_id'],
                    post['topic_title'],
                    post['content'],
                    post['status'],
                    post['post_time'],
                    post['platform_post_id'],
                    post['platform_post_url'],
                    post['post_type'],
                    post['content_length'],
                    post['kol_weight_settings'],
                    post['content_generation_time'],
                    post['kol_settings_version'],
                    post['hashtags'],
                    post['stock_symbol'],
                    post['stock_name'],
                    post['analysis_angle']
                ]
                new_rows.append(row)
            
            # 追加到工作表
            if existing_data:
                # 找到最後一行的位置
                last_row = len(existing_data) + 1
                range_name = f'貼文記錄表!A{last_row}'
            else:
                # 如果工作表為空，從第一行開始
                range_name = '貼文記錄表!A1'
            
            # 寫入數據
            self.sheets_client.write_sheet(range_name, new_rows)
            
            logger.info(f"✅ 成功更新貼文記錄表，新增 {len(posts)} 筆記錄")
            
        except Exception as e:
            logger.error(f"更新貼文記錄表失敗: {e}")
    
    async def run(self):
        """執行貼文生成流程"""
        logger.info("🚀 開始生成 6919 相關貼文...")
        
        try:
            # 1. 獲取 KOL 資料
            kol_list = await self.get_kol_credentials()
            if not kol_list:
                logger.error("無法獲取 KOL 資料")
                return
            
            # 選擇兩個 KOL（包含技術派）
            selected_kols = []
            for kol in kol_list:
                if kol['status'] == '啟用':
                    if '技術' in kol['persona'] or len(selected_kols) < 2:
                        selected_kols.append(kol)
                        if len(selected_kols) >= 2:
                            break
            
            if len(selected_kols) < 2:
                logger.warning(f"只找到 {len(selected_kols)} 個可用 KOL，使用所有可用 KOL")
                selected_kols = [kol for kol in kol_list if kol['status'] == '啟用'][:2]
            
            logger.info(f"📋 選中的 KOL: {[kol['nickname'] for kol in selected_kols]}")
            
            # 2. 獲取 6919 股票數據
            stock_data = await self.get_stock_6919_data()
            if not stock_data:
                logger.error("無法獲取 6919 股票數據")
                return
            
            # 3. 生成話題
            topics = self.generate_6919_topics()
            
            # 4. 為每個 KOL 生成貼文
            generated_posts = []
            for i, kol in enumerate(selected_kols):
                topic = topics[i % len(topics)]  # 循環使用話題
                
                post_data = await self.generate_kol_post(kol, topic, stock_data)
                if post_data:
                    generated_posts.append(post_data)
            
            # 5. 更新貼文記錄表
            if generated_posts:
                await self.update_posts_sheet(generated_posts)
                
                logger.info("📊 生成結果摘要:")
                for post in generated_posts:
                    logger.info(f"  - {post['kol_nickname']}: {post['topic_title']}")
                    logger.info(f"    Hashtags: {post['hashtags']}")
            else:
                logger.error("❌ 沒有成功生成任何貼文")
                
        except Exception as e:
            logger.error(f"貼文生成流程失敗: {e}")

async def main():
    """主函數"""
    generator = Stock6919PostGenerator()
    await generator.run()

if __name__ == "__main__":
    asyncio.run(main())


