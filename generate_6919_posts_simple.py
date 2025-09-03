#!/usr/bin/env python3
"""
6919 股票貼文生成腳本 (簡化版)
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

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Simple6919PostGenerator:
    """簡化版 6919 股票貼文生成器"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient(
            credentials_file='./credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        
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
                        'member_id': row[4],  # MemberId 在第 5 列
                        'password': row[6],  # 密碼在第 7 列
                        'persona': row[3],   # 人設在第 4 列
                        'status': row[9] if len(row) > 9 else 'active'  # 狀態在第 10 列
                    }
                    kol_data.append(kol)
            
            return kol_data
            
        except Exception as e:
            logger.error(f"獲取 KOL 資料失敗: {e}")
            return []
    
    def generate_6919_topics(self) -> List[Dict[str, Any]]:
        """生成 6919 相關話題"""
        topics = [
            {
                'title': '世紀鋼(6919)技術面分析：支撐位與阻力位關鍵點位',
                'keywords': '世紀鋼,6919,技術分析,支撐位,阻力位,鋼鐵股',
                'content_type': 'technical',
                'analysis_angle': '技術面分析',
                'content': '''世紀鋼(6919)今日表現亮眼，從技術面來看，目前股價在關鍵支撐位附近震盪。

📊 技術指標觀察：
• MACD 指標顯示多頭趨勢正在形成
• RSI 位於 45-55 區間，顯示股價處於合理位置
• 布林通道中軌提供良好支撐

🎯 關鍵點位：
• 支撐位：約 85-87 元
• 阻力位：約 92-95 元
• 成交量：今日放大，顯示買盤積極

💡 操作建議：
建議關注 87 元支撐位，若能守住此位置，後續有機會挑戰 92 元阻力位。

大家覺得世紀鋼這波技術面如何？有在關注這檔鋼鐵股嗎？'''
            },
            {
                'title': '6919世紀鋼基本面觀察：鋼鐵產業復甦跡象',
                'keywords': '世紀鋼,6919,基本面,鋼鐵產業,營收,獲利',
                'content_type': 'fundamental',
                'analysis_angle': '基本面分析',
                'content': '''世紀鋼(6919)基本面分析時間！

🏭 產業背景：
世紀鋼為台灣主要鋼構製造商，專注於風力發電、建築鋼構等領域。

📈 營運亮點：
• 風力發電訂單持續成長
• 建築鋼構需求穩定
• 原物料成本控制得當

💰 財務表現：
• 營收年增率維持正成長
• 毛利率穩定在 15-20% 區間
• 負債比率控制在合理範圍

🔍 投資價值：
目前本益比約 12-15 倍，相較同業具備投資價值。

大家對世紀鋼的基本面有什麼看法？看好鋼鐵產業的復甦嗎？'''
            },
            {
                'title': '世紀鋼(6919)量價關係：成交量放大背後的意義',
                'keywords': '世紀鋼,6919,成交量,量價關係,技術指標',
                'content_type': 'technical',
                'analysis_angle': '量價分析',
                'content': '''世紀鋼(6919)今日成交量明顯放大，讓我們來分析一下量價關係！

📊 量價分析：
• 股價上漲 + 成交量放大 = 健康的多頭訊號
• 今日成交量較前 5 日均量增加約 30%
• 價量配合良好，顯示買盤積極

🎯 技術解讀：
• 突破前高時成交量配合，確認突破有效性
• 量能持續放大，顯示資金持續流入
• 短期內有望挑戰更高價位

⚠️ 注意事項：
• 需觀察後續量能是否持續
• 避免追高，建議分批進場

大家有注意到世紀鋼的量價變化嗎？對後續走勢有什麼預期？'''
            }
        ]
        return topics
    
    def generate_kol_post(self, kol: Dict[str, Any], topic: Dict[str, Any]) -> Dict[str, Any]:
        """為特定 KOL 生成貼文"""
        try:
            logger.info(f"為 {kol['nickname']} 生成 6919 相關貼文")
            
            # 根據 KOL 人設調整內容
            adjusted_content = self._adjust_content_for_persona(
                topic['content'], 
                kol['persona'], 
                kol['nickname']
            )
            
            # 生成 hashtags
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
                'content': adjusted_content,
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
                
        except Exception as e:
            logger.error(f"生成 {kol['nickname']} 貼文時發生錯誤: {e}")
            return None
    
    def _adjust_content_for_persona(self, content: str, persona: str, nickname: str) -> str:
        """根據 KOL 人設調整內容"""
        if '技術' in persona:
            # 技術派：更注重技術指標和數據
            adjusted = content.replace('大家覺得', f'各位技術派的朋友們，{nickname}想問')
            adjusted = adjusted.replace('大家對', f'技術分析愛好者們，{nickname}想了解')
            adjusted = adjusted.replace('大家有注意到', f'技術指標觀察者們，{nickname}想請教')
        elif '籌碼' in persona:
            # 籌碼派：更注重資金流向和籌碼面
            adjusted = content.replace('技術面', '籌碼面')
            adjusted = adjusted.replace('技術指標', '籌碼指標')
            adjusted = adjusted.replace('大家覺得', f'籌碼派的朋友們，{nickname}想問')
        else:
            # 一般分析：保持原內容
            adjusted = content.replace('大家覺得', f'{nickname}想問大家')
            adjusted = adjusted.replace('大家對', f'{nickname}想了解大家對')
            adjusted = adjusted.replace('大家有注意到', f'{nickname}想請教大家')
        
        return adjusted
    
    def _generate_6919_hashtags(self, content_type: str) -> str:
        """生成 6919 相關的 hashtags"""
        base_tags = [
            "#6919", "#世紀鋼", "#台股", "#鋼鐵股", "#commoditytags"
        ]
        
        if content_type == 'technical':
            base_tags.extend(["#技術分析", "#K線", "#MACD", "#RSI", "#量價關係"])
        elif content_type == 'fundamental':
            base_tags.extend(["#基本面", "#營收", "#獲利", "#產業分析", "#財務分析"])
        
        # 添加鋼鐵相關標籤
        base_tags.extend(["#鋼鐵", "#製造業", "#原物料", "#風力發電"])
        
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
            
            # 選擇兩個 KOL（優先選擇技術派）
            selected_kols = []
            for kol in kol_list:
                if kol['status'] == 'active':  # 檢查 active 狀態
                    if '技術' in kol['persona'] or len(selected_kols) < 2:
                        selected_kols.append(kol)
                        if len(selected_kols) >= 2:
                            break
            
            if len(selected_kols) < 2:
                logger.warning(f"只找到 {len(selected_kols)} 個可用 KOL，使用所有可用 KOL")
                selected_kols = [kol for kol in kol_list if kol['status'] == 'active'][:2]
            
            logger.info(f"📋 選中的 KOL: {[kol['nickname'] for kol in selected_kols]}")
            
            # 2. 生成話題
            topics = self.generate_6919_topics()
            
            # 3. 為每個 KOL 生成貼文
            generated_posts = []
            for i, kol in enumerate(selected_kols):
                topic = topics[i % len(topics)]  # 循環使用話題
                
                post_data = self.generate_kol_post(kol, topic)
                if post_data:
                    generated_posts.append(post_data)
            
            # 4. 更新貼文記錄表
            if generated_posts:
                await self.update_posts_sheet(generated_posts)
                
                logger.info("📊 生成結果摘要:")
                for post in generated_posts:
                    logger.info(f"  - {post['kol_nickname']} ({post['persona']}): {post['topic_title']}")
                    logger.info(f"    Hashtags: {post['hashtags']}")
                    logger.info(f"    內容長度: {len(post['content'])} 字")
                    logger.info("")
            else:
                logger.error("❌ 沒有成功生成任何貼文")
                
        except Exception as e:
            logger.error(f"貼文生成流程失敗: {e}")

async def main():
    """主函數"""
    generator = Simple6919PostGenerator()
    await generator.run()

if __name__ == "__main__":
    asyncio.run(main())
