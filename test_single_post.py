#!/usr/bin/env python3
"""
單篇漲停股貼文測試腳本
直接使用CMoneyClient，不使用PublishService
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

class SinglePostTester:
    """單篇貼文測試器"""
    
    def __init__(self):
        # 初始化 Google Sheets 客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 初始化 CMoney 客戶端
        self.cmoney_client = CMoneyClient()
        
        # KOL 登入資訊
        self.kol_credentials = {
            "200": {  # 川川哥
                "email": "forum_200@cmoney.com.tw",
                "password": "N9t1kY3x",
                "member_id": "9505546"
            }
        }
    
    async def test_single_post(self):
        """測試發送單篇漲停股貼文"""
        # 測試貼文
        test_post = {
            'kol_serial': '200',
            'kol_nickname': '川川哥',
            'title': '立凱-KY(5227)漲停！各位先進怎麼看？🚀',
            'content': '立凱-KY(5227)今日強勢漲停！技術面顯示跳空缺口，成交量暴增，MACD指標黃金交叉！這波行情背後的原因值得深入分析。從基本面來看，公司近期在鋰電池材料領域的突破性進展，加上新能源車市場需求持續升溫，為股價提供了強勁支撐。外資買盤動向積極，顯示市場對該股的看好程度。但投資者仍需注意，追高需謹慎，盤勢可能因消息面變化而起起伏伏。建議關注後續的技術面表現和基本面發展。各位先進對這波行情有什麼看法？歡迎留言討論！',
            'keywords': '立凱-KY,5227,鋰電池,新能源',
            'commodity_tags': [{"type":"Stock","key":"5227","bullOrBear":0}]
        }
        
        logger.info("🚀 開始測試單篇漲停股貼文...")
        
        try:
            logger.info(f"📝 發送貼文: {test_post['kol_nickname']} - {test_post['title']}")
            
            # 獲取 KOL 登入資訊
            kol_creds = self.kol_credentials.get(test_post['kol_serial'])
            if not kol_creds:
                logger.error(f"找不到 KOL {test_post['kol_serial']} 的登入資訊")
                return
            
            # 登入 CMoney
            logger.info(f"為 {test_post['kol_nickname']} 登入 CMoney...")
            try:
                token = await self.cmoney_client.login(
                    LoginCredentials(
                        email=kol_creds['email'],
                        password=kol_creds['password']
                    )
                )
                logger.info(f"✅ 登入成功: {test_post['kol_nickname']}")
            except Exception as e:
                logger.error(f"登入失敗: {e}")
                return
            
            # 準備發文內容
            logger.info(f"發送貼文: {test_post['title']}")
            try:
                # 準備文章數據
                article_data = ArticleData(
                    title=test_post['title'],
                    text=test_post['content'],
                    commodity_tags=test_post['commodity_tags']
                )
                
                publish_result = await self.cmoney_client.publish_article(token.token, article_data)
                
                if publish_result.success:
                    logger.info(f"✅ 貼文發送成功:")
                    logger.info(f"   KOL: {test_post['kol_nickname']}")
                    logger.info(f"   標題: {test_post['title']}")
                    logger.info(f"   Article ID: {publish_result.post_id}")
                    logger.info(f"   Article URL: {publish_result.post_url}")
                    logger.info(f"   發文時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 更新 Google Sheets
                    await self.update_sheets_with_result(test_post, publish_result)
                else:
                    logger.error(f"❌ 貼文發送失敗:")
                    logger.error(f"   KOL: {test_post['kol_nickname']}")
                    logger.error(f"   標題: {test_post['title']}")
                    logger.error(f"   錯誤: {publish_result.error_message}")
                    
            except Exception as e:
                logger.error(f"發送貼文時發生錯誤: {e}")
            
        except Exception as e:
            logger.error(f"處理貼文時發生錯誤: {e}")
        
        logger.info("🎯 測試完成！")
    
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
    tester = SinglePostTester()
    await tester.test_single_post()

if __name__ == "__main__":
    asyncio.run(main())
