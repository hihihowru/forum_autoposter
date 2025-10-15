#!/usr/bin/env python3
"""
直接更新互動數據到「互動回饋即時總表」
跳過 Google Sheets 讀取，直接使用已知的 article_id 和 CM API
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DirectInteractionUpdater:
    """直接互動數據更新器"""
    
    def __init__(self):
        """初始化"""
        self.cmoney_client = CMoneyClient()
        
        # 初始化 token 快取
        self.cmoney_client._tokens = {}
        
        # 已知的 article_id 列表（從貼文記錄表中獲取）
        self.known_article_ids = [
            "173477844",  # 龜狗一日散戶
            "173477845",  # 板橋大who
            # 可以繼續添加更多 article_id
        ]
        
        # KOL 基本資訊（對應 article_id）
        self.kol_info = {
            "173477844": {
                "kol_id": "9505549",
                "kol_nickname": "龜狗一日散戶",
                "topic_id": "2025-09-02 17:41:13",
                "post_timestamp": "2025-09-02T17:41:09.295405",
                "content": "貼文內容...",
                "is_trending": "FALSE"
            },
            "173477845": {
                "kol_id": "9505550", 
                "kol_nickname": "板橋大who",
                "topic_id": "2025-09-02 17:41:13",
                "post_timestamp": "2025-09-02T17:41:09.704825",
                "content": "貼文內容...",
                "is_trending": "FALSE"
            }
        }
    
    async def get_interaction_data(self, article_id: str) -> Optional[Dict[str, Any]]:
        """透過 CM API 獲取互動數據"""
        try:
            logger.info(f"📝 獲取 Article {article_id} 的互動數據...")
            
            # 使用川川哥的憑證登入
            credentials = LoginCredentials(
                email='forum_200@cmoney.com.tw',
                password=os.getenv('CMONEY_PASSWORD')
            )
            
            # 登入獲取 token
            login_result = await self.cmoney_client.login(credentials)
            
            if not login_result or login_result.is_expired:
                logger.error(f"❌ 登入失敗或 Token 已過期")
                return None
            
            # 獲取互動數據
            interaction_data = await self.cmoney_client.get_article_interactions(
                login_result.token, 
                article_id
            )
            
            if interaction_data:
                # 解析表情數據
                emoji_details = {}
                emoji_total = 0
                
                if hasattr(interaction_data, 'raw_data') and interaction_data.raw_data:
                    emoji_count = interaction_data.raw_data.get('emojiCount', {})
                    if isinstance(emoji_count, dict):
                        emoji_details = emoji_count
                        emoji_total = sum(emoji_count.values())
                
                # 計算總互動數
                total_interactions = (interaction_data.likes + 
                                    interaction_data.comments + 
                                    interaction_data.shares + 
                                    emoji_total)
                
                # 計算互動率 (假設瀏覽數為 1000)
                engagement_rate = round(total_interactions / 1000.0, 3) if total_interactions > 0 else 0.0
                
                result = {
                    'likes': interaction_data.likes,
                    'comments': interaction_data.comments,
                    'shares': interaction_data.shares,
                    'views': interaction_data.views,
                    'engagement_rate': interaction_data.engagement_rate,
                    'emoji_details': emoji_details,
                    'emoji_total': emoji_total,
                    'total_interactions': total_interactions,
                    'calculated_engagement_rate': engagement_rate,
                    'raw_data': interaction_data.raw_data
                }
                
                logger.info(f"✅ Article {article_id} 互動數據: {total_interactions} 次互動")
                return result
            else:
                logger.warning(f"⚠️ 無法獲取 Article {article_id} 的互動數據")
                return None
                
        except Exception as e:
            logger.error(f"❌ 獲取 Article {article_id} 互動數據失敗: {e}")
            return None
    
    def generate_interaction_report(self, interaction_results: List[Dict[str, Any]]) -> str:
        """生成互動數據報告"""
        report = []
        report.append("=" * 80)
        report.append("📊 即時互動數據更新報告")
        report.append("=" * 80)
        report.append(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"處理文章數: {len(interaction_results)}")
        report.append("")
        
        total_interactions = 0
        total_likes = 0
        total_comments = 0
        
        for result in interaction_results:
            if result['success']:
                article_id = result['article_id']
                kol_info = result['kol_info']
                interaction_data = result['interaction_data']
                
                report.append(f"📝 Article {article_id} - {kol_info['kol_nickname']}")
                report.append(f"   讚數: {interaction_data['likes']}")
                report.append(f"   留言數: {interaction_data['comments']}")
                report.append(f"   分享數: {interaction_data['shares']}")
                report.append(f"   總互動數: {interaction_data['total_interactions']}")
                report.append(f"   互動率: {interaction_data['calculated_engagement_rate']}")
                report.append(f"   表情總數: {interaction_data['emoji_total']}")
                report.append("")
                
                total_interactions += interaction_data['total_interactions']
                total_likes += interaction_data['likes']
                total_comments += interaction_data['comments']
            else:
                report.append(f"❌ Article {result['article_id']} - {result['error']}")
                report.append("")
        
        report.append("=" * 80)
        report.append("📈 整體統計:")
        report.append(f"   總互動數: {total_interactions}")
        report.append(f"   總讚數: {total_likes}")
        report.append(f"   總留言數: {total_comments}")
        report.append(f"   平均互動率: {round(total_interactions / len(interaction_results) / 1000.0, 3) if interaction_results else 0}")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    async def run(self):
        """執行更新流程"""
        try:
            logger.info("🚀 開始直接更新互動數據...")
            logger.info("=" * 60)
            
            interaction_results = []
            
            # 處理每個已知的 article_id
            for article_id in self.known_article_ids:
                kol_info = self.kol_info.get(article_id, {})
                
                # 獲取互動數據
                interaction_data = await self.get_interaction_data(article_id)
                
                if interaction_data:
                    result = {
                        'success': True,
                        'article_id': article_id,
                        'kol_info': kol_info,
                        'interaction_data': interaction_data
                    }
                else:
                    result = {
                        'success': False,
                        'article_id': article_id,
                        'error': '無法獲取互動數據'
                    }
                
                interaction_results.append(result)
            
            # 生成報告
            report = self.generate_interaction_report(interaction_results)
            print(report)
            
            # 顯示要更新到 Google Sheets 的數據格式
            logger.info("📋 要更新到「互動回饋即時總表」的數據格式:")
            logger.info("=" * 60)
            
            current_time = datetime.now().isoformat()
            
            for result in interaction_results:
                if result['success']:
                    article_id = result['article_id']
                    kol_info = result['kol_info']
                    interaction_data = result['interaction_data']
                    
                    # 準備行數據（對應 Google Sheets 欄位）
                    row_data = [
                        article_id,                                    # A: article_id
                        kol_info.get('kol_id', ''),                    # B: member_id
                        kol_info.get('kol_nickname', ''),              # C: nickname
                        f"貼文 {article_id}",                         # D: title
                        kol_info.get('content', '')[:100],             # E: content (截取前100字)
                        kol_info.get('topic_id', ''),                  # F: topic_id
                        kol_info.get('is_trending', 'FALSE'),          # G: is_trending_topic
                        kol_info.get('post_timestamp', ''),            # H: post_time
                        current_time,                                  # I: last_update_time
                        interaction_data['likes'],                     # J: likes_count
                        interaction_data['comments'],                  # K: comments_count
                        interaction_data['total_interactions'],         # L: total_interactions
                        interaction_data['calculated_engagement_rate'], # M: engagement_rate
                        0.0,                                           # N: growth_rate (暫時設為0)
                        '',                                            # O: collection_error
                        interaction_data.get('shares', 0),             # P: donation_count (用shares代替)
                        0.0,                                           # Q: donation_amount
                        '👍' if interaction_data['emoji_total'] > 0 else '',  # R: emoji_type
                        str(interaction_data['emoji_details']),         # S: emoji_counts
                        interaction_data['emoji_total']                # T: total_emoji_count
                    ]
                    
                    logger.info(f"Article {article_id} 數據行: {row_data}")
            
            logger.info("✅ 直接互動數據更新完成！")
            logger.info("💡 請手動將上述數據複製到「互動回饋即時總表」中")
            
        except Exception as e:
            logger.error(f"❌ 更新流程失敗: {e}")

async def main():
    """主函數"""
    updater = DirectInteractionUpdater()
    await updater.run()

if __name__ == "__main__":
    asyncio.run(main())



