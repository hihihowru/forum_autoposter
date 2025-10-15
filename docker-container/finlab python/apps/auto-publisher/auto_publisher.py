#!/usr/bin/env python3
"""
自動發文服務 - 持續運行在 Docker 容器中
"""

import os
import sys
import asyncio
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append('/app')
sys.path.append('/app/src')

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.assign.assignment_service import AssignmentService, TopicData
from src.services.classification.topic_classifier import TopicClassifier
from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.services.publish.publish_service import PublishService

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoPublisher:
    """自動發文服務"""
    
    def __init__(self):
        """初始化服務"""
        self.sheets_client = GoogleSheetsClient(
            credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        self.cmoney_client = CMoneyClient()
        self.assignment_service = AssignmentService(self.sheets_client)
        self.topic_classifier = TopicClassifier()
        self.content_generator = ContentGenerator()
        self.publish_service = PublishService(self.sheets_client)
        
        # KOL 憑證
        self.kol_credentials = {
            200: {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x"},
            201: {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t"},
            202: {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p"},
            203: {"email": "forum_203@cmoney.com.tw", "password": "y7O3cL9k"},
            204: {"email": "forum_204@cmoney.com.tw", "password": "f4E9sC8w"},
            205: {"email": "forum_205@cmoney.com.tw", "password": "Z5u6dL9o"}
        }
        
        # 運行狀態
        self.is_running = False
        self.last_run_time = None
        
    async def login_kols(self):
        """登入所有 KOL"""
        logger.info("開始登入 KOL...")
        
        success_count = 0
        for kol_serial, creds in self.kol_credentials.items():
            try:
                success = await self.publish_service.login_kol(
                    kol_serial, creds["email"], creds["password"]
                )
                if success:
                    logger.info(f"✅ KOL {kol_serial} 登入成功")
                    success_count += 1
                else:
                    logger.warning(f"❌ KOL {kol_serial} 登入失敗")
            except Exception as e:
                logger.error(f"❌ KOL {kol_serial} 登入異常: {e}")
        
        logger.info(f"KOL 登入完成: {success_count}/{len(self.kol_credentials)} 成功")
        return success_count > 0
    
    async def fetch_and_process_topics(self):
        """獲取並處理熱門話題"""
        try:
            logger.info("開始獲取熱門話題...")
            
            # 使用川川哥的憑證獲取熱門話題
            credentials = LoginCredentials(
                email='forum_200@cmoney.com.tw',
                password='N9t1kY3x'
            )
            
            token = await self.cmoney_client.login(credentials)
            topics = await self.cmoney_client.get_trending_topics(token.token)
            
            logger.info(f"獲取到 {len(topics)} 個熱門話題")
            
            if not topics:
                logger.warning("沒有獲取到熱門話題")
                return []
            
            # 處理前3個話題
            processed_topics = []
            for topic in topics[:3]:
                try:
                    # 話題分類
                    classification = self.topic_classifier.classify_topic(
                        topic.id, topic.title, topic.name
                    )
                    
                    # 創建 TopicData 物件
                    topic_data = TopicData(
                        topic_id=topic.id,
                        title=topic.title,
                        input_index=0,
                        persona_tags=classification.persona_tags,
                        industry_tags=classification.industry_tags,
                        event_tags=classification.event_tags,
                        stock_tags=classification.stock_tags,
                        classification=classification
                    )
                    
                    processed_topics.append(topic_data)
                    logger.info(f"處理話題: {topic.title}")
                    
                except Exception as e:
                    logger.error(f"處理話題失敗 {topic.title}: {e}")
                    continue
            
            return processed_topics
            
        except Exception as e:
            logger.error(f"獲取話題失敗: {e}")
            return []
    
    async def generate_and_publish_content(self, topics):
        """生成內容並發文"""
        try:
            # 載入 KOL 配置
            self.assignment_service.load_kol_profiles()
            active_kols = [kol for kol in self.assignment_service._kol_profiles if kol.enabled]
            logger.info(f"載入了 {len(active_kols)} 個活躍的 KOL")
            
            published_count = 0
            
            for topic_data in topics:
                try:
                    # 分派 KOL
                    assignments = self.assignment_service.assign_topics(
                        [topic_data], max_assignments_per_topic=2
                    )
                    
                    logger.info(f"話題 {topic_data.title} 分派給 {len(assignments)} 個 KOL")
                    
                    # 準備發文記錄
                    post_records = []
                    
                    for assignment in assignments:
                        try:
                            # 找到對應的 KOL
                            kol = next((k for k in self.assignment_service._kol_profiles 
                                      if k.serial == assignment.kol_serial), None)
                            if not kol:
                                continue
                            
                            # 生成內容
                            content_request = ContentRequest(
                                topic_title=topic_data.title,
                                topic_keywords=", ".join(
                                    topic_data.persona_tags + 
                                    topic_data.industry_tags + 
                                    topic_data.event_tags
                                ),
                                kol_persona=kol.persona,
                                kol_nickname=kol.nickname,
                                content_type="investment",
                                target_audience="active_traders"
                            )
                            
                            generated = self.content_generator.generate_complete_content(content_request)
                            
                            if not generated.success:
                                logger.error(f"內容生成失敗: {generated.error_message}")
                                continue
                            
                            # 生成 post ID
                            post_id = f"{topic_data.topic_id}-{assignment.kol_serial}"
                            
                            # 準備發文記錄
                            record = [
                                post_id,  # 貼文ID
                                assignment.kol_serial,  # KOL Serial
                                kol.nickname,  # KOL 暱稱
                                kol.member_id,  # KOL ID
                                kol.persona,  # Persona
                                "investment",  # Content Type
                                1,  # 已派發TopicIndex
                                topic_data.topic_id,  # 已派發TopicID
                                generated.title,  # 已派發TopicTitle (使用生成的標題)
                                ", ".join(topic_data.persona_tags + topic_data.industry_tags + topic_data.event_tags + topic_data.stock_tags),  # 已派發TopicKeywords
                                generated.content,  # 生成內容
                                "ready_to_post",  # 發文狀態
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 上次排程時間
                                "",  # 發文時間戳記
                                "",  # 最近錯誤訊息
                                "",  # 平台發文ID
                                "",  # 平台發文URL
                                topic_data.title  # 熱門話題標題
                            ]
                            
                            post_records.append(record)
                            
                            logger.info(f"準備發文: {post_id} - {generated.title}")
                            
                        except Exception as e:
                            logger.error(f"準備發文記錄異常 {assignment.kol_serial}: {e}")
                            continue
                    
                    # 將準備發文的記錄寫入 Google Sheets
                    if post_records:
                        try:
                            # 讀取現有數據以找到最後一行
                            existing_data = self.sheets_client.read_sheet('貼文記錄表', 'A:R')
                            start_row = len(existing_data) + 1
                            
                            # 寫入新記錄
                            range_name = f'A{start_row}:R{start_row + len(post_records) - 1}'
                            self.sheets_client.write_sheet('貼文記錄表', post_records, range_name)
                            
                            logger.info(f"✅ 成功寫入 {len(post_records)} 筆準備發文記錄到 Google Sheets")
                            
                        except Exception as e:
                            logger.error(f"寫入 Google Sheets 失敗: {e}")
                    
                    # 現在開始發文
                    for i, assignment in enumerate(assignments):
                        try:
                            # 找到對應的 KOL
                            kol = next((k for k in self.assignment_service._kol_profiles 
                                      if k.serial == assignment.kol_serial), None)
                            if not kol:
                                continue
                            
                            # 生成內容（重新生成以確保一致性）
                            content_request = ContentRequest(
                                topic_title=topic_data.title,
                                topic_keywords=", ".join(
                                    topic_data.persona_tags + 
                                    topic_data.industry_tags + 
                                    topic_data.event_tags
                                ),
                                kol_persona=kol.persona,
                                kol_nickname=kol.nickname,
                                content_type="investment",
                                target_audience="active_traders"
                            )
                            
                            generated = self.content_generator.generate_complete_content(content_request)
                            
                            if not generated.success:
                                logger.error(f"內容生成失敗: {generated.error_message}")
                                continue
                            
                            # 發文
                            post_id = f"{topic_data.topic_id}-{assignment.kol_serial}"
                            logger.info(f"發文: {post_id} - {generated.title}")
                            
                            result = await self.publish_service.publish_post(
                                kol_serial=assignment.kol_serial,
                                title=generated.title,
                                content=generated.content,
                                topic_id=topic_data.topic_id
                            )
                            
                            if result and result.success:
                                logger.info(f"✅ 發文成功: {post_id} -> {result.post_id}")
                                published_count += 1
                                
                                # 間隔2分鐘
                                if i < len(assignments) - 1:
                                    logger.info("等待 2 分鐘...")
                                    await asyncio.sleep(120)
                            else:
                                logger.error(f"❌ 發文失敗: {post_id}")
                                
                        except Exception as e:
                            logger.error(f"發文異常 {assignment.kol_serial}: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"處理話題異常 {topic_data.title}: {e}")
                    continue
            
            logger.info(f"發文完成，共發文 {published_count} 篇")
            return published_count
            
        except Exception as e:
            logger.error(f"發文流程失敗: {e}")
            return 0
    
    async def run_cycle(self):
        """運行一個週期"""
        try:
            logger.info("=" * 50)
            logger.info("開始新的發文週期")
            logger.info("=" * 50)
            
            # 登入 KOL
            if not await self.login_kols():
                logger.error("KOL 登入失敗，跳過此週期")
                return
            
            # 獲取並處理話題
            topics = await self.fetch_and_process_topics()
            if not topics:
                logger.warning("沒有話題可處理，跳過此週期")
                return
            
            # 生成內容並發文
            published_count = await self.generate_and_publish_content(topics)
            
            self.last_run_time = datetime.now()
            logger.info(f"發文週期完成，發文 {published_count} 篇")
            
        except Exception as e:
            logger.error(f"發文週期失敗: {e}")
    
    async def start(self):
        """啟動自動發文服務"""
        logger.info("🚀 自動發文服務啟動")
        self.is_running = True
        
        while self.is_running:
            try:
                # 檢查是否應該運行（每小時運行一次）
                now = datetime.now()
                if (self.last_run_time is None or 
                    now - self.last_run_time >= timedelta(hours=1)):
                    
                    await self.run_cycle()
                else:
                    # 等待到下次運行時間
                    next_run = self.last_run_time + timedelta(hours=1)
                    wait_seconds = (next_run - now).total_seconds()
                    logger.info(f"等待 {wait_seconds/60:.1f} 分鐘到下次運行")
                    await asyncio.sleep(min(wait_seconds, 300))  # 最多等待5分鐘
                    
            except KeyboardInterrupt:
                logger.info("收到停止信號，正在關閉服務...")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"服務運行異常: {e}")
                await asyncio.sleep(60)  # 異常時等待1分鐘
        
        logger.info("自動發文服務已停止")

async def main():
    """主函數"""
    # 啟動自動發文服務
    publisher = AutoPublisher()
    await publisher.start()

if __name__ == "__main__":
    asyncio.run(main())
