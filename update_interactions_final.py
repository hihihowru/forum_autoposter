#!/usr/bin/env python3
"""
互動數據更新工具 - 最終版本
由於 Google API 認證問題，提供手動更新方案
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

class InteractionDataUpdater:
    """互動數據更新器"""
    
    def __init__(self):
        """初始化"""
        self.cmoney_client = CMoneyClient()
        
        # 初始化 token 快取
        self.cmoney_client._tokens = {}
        
        # 從貼文記錄表獲取的 article_id 列表
        # 這些是從 Google Sheets 中手動獲取的
        self.article_ids_to_update = [
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
    
    def generate_csv_data(self, interaction_results: List[Dict[str, Any]]) -> str:
        """生成 CSV 格式的數據"""
        csv_lines = []
        
        # CSV 標題行
        headers = [
            'article_id', 'member_id', 'nickname', 'title', 'content', 
            'topic_id', 'is_trending_topic', 'post_time', 'last_update_time',
            'likes_count', 'comments_count', 'total_interactions', 
            'engagement_rate', 'growth_rate', 'collection_error',
            'donation_count', 'donation_amount', 'emoji_type', 
            'emoji_counts', 'total_emoji_count'
        ]
        csv_lines.append(','.join(headers))
        
        current_time = datetime.now().isoformat()
        
        for result in interaction_results:
            if result['success']:
                article_id = result['article_id']
                kol_info = result['kol_info']
                interaction_data = result['interaction_data']
                
                # 準備 CSV 行數據
                row_data = [
                    article_id,                                    # article_id
                    kol_info.get('kol_id', ''),                    # member_id
                    kol_info.get('kol_nickname', ''),              # nickname
                    f"貼文 {article_id}",                         # title
                    kol_info.get('content', '')[:100],             # content (截取前100字)
                    kol_info.get('topic_id', ''),                  # topic_id
                    kol_info.get('is_trending', 'FALSE'),          # is_trending_topic
                    kol_info.get('post_timestamp', ''),             # post_time
                    current_time,                                  # last_update_time
                    str(interaction_data['likes']),                # likes_count
                    str(interaction_data['comments']),             # comments_count
                    str(interaction_data['total_interactions']),    # total_interactions
                    str(interaction_data['calculated_engagement_rate']), # engagement_rate
                    '0.0',                                         # growth_rate
                    '',                                            # collection_error
                    str(interaction_data.get('shares', 0)),        # donation_count
                    '0.0',                                         # donation_amount
                    '👍' if interaction_data['emoji_total'] > 0 else '',  # emoji_type
                    str(interaction_data['emoji_details']),        # emoji_counts
                    str(interaction_data['emoji_total'])           # total_emoji_count
                ]
                
                csv_lines.append(','.join(row_data))
        
        return '\n'.join(csv_lines)
    
    def generate_manual_update_instructions(self, interaction_results: List[Dict[str, Any]]) -> str:
        """生成手動更新說明"""
        instructions = []
        instructions.append("=" * 80)
        instructions.append("📋 手動更新「互動回饋即時總表」說明")
        instructions.append("=" * 80)
        instructions.append("")
        instructions.append("由於 Google API 認證問題，請按照以下步驟手動更新：")
        instructions.append("")
        sheets_id = os.getenv('GOOGLE_SHEETS_ID', 'YOUR_SHEETS_ID')
        instructions.append(f"1. 打開 Google Sheets: https://docs.google.com/spreadsheets/d/{sheets_id}/edit")
        instructions.append("2. 切換到「互動回饋即時總表」分頁")
        instructions.append("3. 清空現有數據（保留標題行）")
        instructions.append("4. 將以下數據複製貼上到表格中：")
        instructions.append("")
        
        current_time = datetime.now().isoformat()
        
        for i, result in enumerate(interaction_results, 1):
            if result['success']:
                article_id = result['article_id']
                kol_info = result['kol_info']
                interaction_data = result['interaction_data']
                
                instructions.append(f"第 {i} 行數據:")
                instructions.append(f"  A: {article_id}")
                instructions.append(f"  B: {kol_info.get('kol_id', '')}")
                instructions.append(f"  C: {kol_info.get('kol_nickname', '')}")
                instructions.append(f"  D: 貼文 {article_id}")
                instructions.append(f"  E: {kol_info.get('content', '')[:100]}")
                instructions.append(f"  F: {kol_info.get('topic_id', '')}")
                instructions.append(f"  G: {kol_info.get('is_trending', 'FALSE')}")
                instructions.append(f"  H: {kol_info.get('post_timestamp', '')}")
                instructions.append(f"  I: {current_time}")
                instructions.append(f"  J: {interaction_data['likes']}")
                instructions.append(f"  K: {interaction_data['comments']}")
                instructions.append(f"  L: {interaction_data['total_interactions']}")
                instructions.append(f"  M: {interaction_data['calculated_engagement_rate']}")
                instructions.append(f"  N: 0.0")
                instructions.append(f"  O: ")
                instructions.append(f"  P: {interaction_data.get('shares', 0)}")
                instructions.append(f"  Q: 0.0")
                instructions.append(f"  R: {'👍' if interaction_data['emoji_total'] > 0 else ''}")
                instructions.append(f"  S: {interaction_data['emoji_details']}")
                instructions.append(f"  T: {interaction_data['emoji_total']}")
                instructions.append("")
        
        instructions.append("5. 完成後，數據將自動更新到「互動回饋即時總表」")
        instructions.append("")
        instructions.append("注意：如果 Google API 認證問題解決，可以重新運行自動更新腳本")
        instructions.append("=" * 80)
        
        return "\n".join(instructions)
    
    async def run(self):
        """執行更新流程"""
        try:
            logger.info("🚀 開始更新互動數據...")
            logger.info("=" * 60)
            
            interaction_results = []
            
            # 處理每個 article_id
            for article_id in self.article_ids_to_update:
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
            print("\n" + "=" * 80)
            print("📊 互動數據更新報告")
            print("=" * 80)
            print(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"處理文章數: {len(interaction_results)}")
            print("")
            
            total_interactions = 0
            total_likes = 0
            total_comments = 0
            
            for result in interaction_results:
                if result['success']:
                    article_id = result['article_id']
                    kol_info = result['kol_info']
                    interaction_data = result['interaction_data']
                    
                    print(f"📝 Article {article_id} - {kol_info['kol_nickname']}")
                    print(f"   讚數: {interaction_data['likes']}")
                    print(f"   留言數: {interaction_data['comments']}")
                    print(f"   分享數: {interaction_data['shares']}")
                    print(f"   總互動數: {interaction_data['total_interactions']}")
                    print(f"   互動率: {interaction_data['calculated_engagement_rate']}")
                    print(f"   表情總數: {interaction_data['emoji_total']}")
                    print("")
                    
                    total_interactions += interaction_data['total_interactions']
                    total_likes += interaction_data['likes']
                    total_comments += interaction_data['comments']
                else:
                    print(f"❌ Article {result['article_id']} - {result['error']}")
                    print("")
            
            print("=" * 80)
            print("📈 整體統計:")
            print(f"   總互動數: {total_interactions}")
            print(f"   總讚數: {total_likes}")
            print(f"   總留言數: {total_comments}")
            print(f"   平均互動率: {round(total_interactions / len(interaction_results) / 1000.0, 3) if interaction_results else 0}")
            print("=" * 80)
            
            # 生成手動更新說明
            instructions = self.generate_manual_update_instructions(interaction_results)
            print("\n" + instructions)
            
            # 生成 CSV 數據（可選）
            csv_data = self.generate_csv_data(interaction_results)
            print("\n" + "=" * 80)
            print("📄 CSV 格式數據（可複製到 Excel 或 Google Sheets）:")
            print("=" * 80)
            print(csv_data)
            
            logger.info("✅ 互動數據更新完成！")
            
        except Exception as e:
            logger.error(f"❌ 更新流程失敗: {e}")

async def main():
    """主函數"""
    updater = InteractionDataUpdater()
    await updater.run()

if __name__ == "__main__":
    asyncio.run(main())



