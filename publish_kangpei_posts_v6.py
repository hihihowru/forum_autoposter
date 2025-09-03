#!/usr/bin/env python3
"""
康霈生技貼文發文腳本 V6
最終修正版本，移除 communityTopic 參數
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials, ArticleData

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KangpeiPostPublisherV6:
    """康霈生技貼文發文器 V6"""
    
    def __init__(self):
        # 初始化 Google Sheets 客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 初始化 CMoney 客戶端
        self.cmoney_client = CMoneyClient()
        
        # KOL 登入資訊 - 修正版本
        self.kol_credentials = {
            "200": {  # 川川哥
                "email": "forum_200@cmoney.com.tw",
                "password": "N9t1kY3x",
                "member_id": "9505546"
            },
            "201": {  # 韭割哥
                "email": "forum_201@cmoney.com.tw", 
                "password": "m7C1lR4t",
                "member_id": "9505547"
            }
        }
    
    async def publish_specific_posts(self):
        """發送指定的康霈生技貼文"""
        # 定義要發送的貼文
        posts_to_publish = [
            {
                'kol_serial': '200',
                'kol_nickname': '川川哥',
                'title': '康霈生技(6919)漲停！CBL-514神秘力量嘎到！',
                'content': '康霈生技(6919)今日嘎到漲停！技術面爆量，K棒跳空缺口，MACD背離支撐帶！專業分析指標顯示黃金交叉即將爆發！CBL-514減重新藥題材熱度持續升溫，市場熱議，外資買盤動向強勁！但切記追高需謹慎，盤勢或因消息面變化而起起伏伏！穩了啦，要噴啦，睡醒漲停！風險自負，勿貪！想知道的話，留言告訴我，咱們一起討論一下...',
                'keywords': '康霈生技,6919,減重藥,CBL-514',
                'commodity_tags': [{"type":"Stock","key":"6919","bullOrBear":0}]
            },
            {
                'kol_serial': '201',
                'kol_nickname': '韭割哥',
                'title': '康霈生技(6919)：減重新藥CBL-514引領漲停風潮 📈',
                'content': '近期市場熱議康霈生技(6919)，其股價出現漲停表現，背後的原因何在？讓我們從技術面和基本面進行深入分析。技術面上，康霈生技的減重新藥CBL-514題材一拍即合，引領著漲停風潮。這項新藥的研發進展值得關注，將直接影響公司未來的市場表現。此一利好消息穩定了投資者情緒，成為股價上漲的催化劑。另一方面，外資買盤的動向也值得關注。外資的持續看好往往能帶動股價持續上揚，對康霈生技的長期投資價值有所支撐。綜合分析，建議投資者在關注減重新藥CBL-514的同時，也應注意公司的財務結構、產業競爭力等基本面因素，以全面評估投資價值。然而，投資須謹慎，研發風險、法規風險、競爭風險不可忽視。康霈生技的漲停題材吸引眾多投資者目光，但投資要有耐心，時間將證明一切的價值。📊 💡 💰',
                'keywords': '康霈生技,6919,減重藥,CBL-514',
                'commodity_tags': [{"type":"Stock","key":"6919","bullOrBear":0}]
            }
        ]
        
        logger.info("🚀 開始發送康霈生技貼文...")
        
        for post in posts_to_publish:
            try:
                logger.info(f"📝 發送貼文: {post['kol_nickname']} - {post['title']}")
                
                # 獲取 KOL 登入資訊
                kol_creds = self.kol_credentials.get(post['kol_serial'])
                if not kol_creds:
                    logger.error(f"找不到 KOL {post['kol_serial']} 的登入資訊")
                    continue
                
                # 登入 CMoney
                logger.info(f"為 {post['kol_nickname']} 登入 CMoney...")
                try:
                    token = await self.cmoney_client.login(
                        LoginCredentials(
                            email=kol_creds['email'],
                            password=kol_creds['password']
                        )
                    )
                    logger.info(f"✅ 登入成功: {post['kol_nickname']}")
                except Exception as e:
                    logger.error(f"登入失敗: {e}")
                    continue
                
                # 準備發文內容
                logger.info(f"發送貼文: {post['title']}")
                try:
                    # 準備文章數據 - 只使用 commodityTags，不使用 communityTopic
                    article_data = ArticleData(
                        title=post['title'],
                        text=post['content'],
                        commodity_tags=post['commodity_tags']
                    )
                    
                    publish_result = await self.cmoney_client.publish_article(token.token, article_data)
                    
                    if publish_result.success:
                        logger.info(f"✅ 貼文發送成功:")
                        logger.info(f"   KOL: {post['kol_nickname']}")
                        logger.info(f"   標題: {post['title']}")
                        logger.info(f"   Article ID: {publish_result.post_id}")
                        logger.info(f"   Article URL: {publish_result.post_url}")
                        logger.info(f"   發文時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # 更新 Google Sheets
                        await self.update_sheets_with_result(post, publish_result)
                    else:
                        logger.error(f"❌ 貼文發送失敗:")
                        logger.error(f"   KOL: {post['kol_nickname']}")
                        logger.error(f"   標題: {post['title']}")
                        logger.error(f"   錯誤: {publish_result.error_message}")
                        
                except Exception as e:
                    logger.error(f"發送貼文時發生錯誤: {e}")
                
                logger.info("")
                
                # 等待一下再發下一篇
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"處理貼文時發生錯誤: {e}")
        
        logger.info("🎯 發文流程完成！")
    
    async def update_sheets_with_result(self, post: Dict[str, Any], publish_result):
        """更新 Google Sheets 中的貼文狀態"""
        try:
            # 讀取貼文記錄表
            posts_data = self.sheets_client.read_sheet('貼文記錄表', 'A:AH')
            
            # 找到對應的貼文並更新
            for i, row in enumerate(posts_data):
                if (row[1] == post['kol_serial'] and  # KOL Serial
                    row[8] == post['title']):        # Topic Title
                    
                    # 更新狀態
                    update_data = [
                        'published',  # L: Status
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # M: Scheduled Time
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # N: Post Time
                        '',  # O: Error Message
                        publish_result.post_id,  # P: Platform Post ID
                        publish_result.post_url  # Q: Platform Post URL
                    ]
                    
                    # 寫回 Google Sheets
                    range_name = f'L{i+1}:Q{i+1}'
                    self.sheets_client.write_sheet('貼文記錄表', [update_data], range_name)
                    logger.info(f"✅ 更新 Google Sheets: {post['kol_nickname']} - {publish_result.post_id}")
                    break
                    
        except Exception as e:
            logger.error(f"更新 Google Sheets 失敗: {e}")

async def main():
    """主函數"""
    publisher = KangpeiPostPublisherV6()
    await publisher.publish_specific_posts()

if __name__ == "__main__":
    asyncio.run(main())


