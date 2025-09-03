"""
話題處理服務
負責處理話題分配、內容生成和更新貼文記錄表
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from services.assign.assignment_service import AssignmentService, TopicData, TaskAssignment
from services.content.content_generator import create_content_generator, ContentRequest
from clients.google.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)

@dataclass
class ProcessedTopic:
    """處理後的話題"""
    topic_id: str
    title: str
    content: str
    assignments: List[TaskAssignment]
    generated_content: Optional[Dict[str, Any]] = None  # {kol_serial: GeneratedContent}
    classification: Optional[Any] = None

class TopicProcessor:
    """話題處理器"""
    
    def __init__(self, sheets_client: GoogleSheetsClient):
        """
        初始化話題處理器
        
        Args:
            sheets_client: Google Sheets 客戶端
        """
        self.sheets_client = sheets_client
        self.assignment_service = AssignmentService(sheets_client)
        self.content_generator = create_content_generator()
        
        logger.info("話題處理器初始化完成")
    
    def _generate_post_id(self, topic_id: str, kol_serial: int, topic_title: str) -> str:
        """
        生成貼文ID
        
        Args:
            topic_id: 話題ID（來自 trending API）
            kol_serial: KOL序號
            topic_title: 話題標題
            
        Returns:
            貼文ID
        """
        # 統一使用 topic_id + kol_serial 格式
        return f"{topic_id}-{kol_serial}"
    
    def _check_duplicate_post(self, post_id: str) -> bool:
        """
        檢查貼文ID是否已存在
        
        Args:
            post_id: 貼文ID
            
        Returns:
            True if duplicate, False otherwise
        """
        try:
            # 讀取現有貼文記錄
            existing_data = self.sheets_client.read_sheet('貼文記錄表', 'A:A')
            existing_ids = [row[0] for row in existing_data[1:] if row]  # 跳過標題行
            
            return post_id in existing_ids
        except Exception as e:
            logger.error(f"檢查重複貼文失敗: {e}")
            return False
    
    def process_topics(self, topics: List[Dict[str, Any]]) -> List[ProcessedTopic]:
        """
        處理話題列表
        
        Args:
            topics: 話題列表，每個話題包含 id, title, content
            
        Returns:
            處理後的話題列表
        """
        processed_topics = []
        
        # 載入 KOL 配置
        self.assignment_service.load_kol_profiles()
        logger.info(f"載入了 {len(self.assignment_service._kol_profiles)} 個 KOL")
        
        for topic_data in topics:
            try:
                processed_topic = self._process_single_topic(topic_data)
                processed_topics.append(processed_topic)
                
                # 更新到貼文記錄表
                self._update_post_records(processed_topic)
                
            except Exception as e:
                logger.error(f"處理話題失敗 {topic_data.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"成功處理了 {len(processed_topics)} 個話題")
        return processed_topics
    
    def _process_single_topic(self, topic_data: Dict[str, Any]) -> ProcessedTopic:
        """
        處理單個話題
        
        Args:
            topic_data: 話題數據
            
        Returns:
            處理後的話題
        """
        topic_id = topic_data.get('id', '')
        title = topic_data.get('title', '')
        content = topic_data.get('content', '')
        
        logger.info(f"開始處理話題: {title}")
        
        # 步驟1: 話題分類
        classification = self.assignment_service.classify_topic(topic_id, title, content)
        logger.info(f"話題分類完成: {classification.persona_tags}")
        
        # 步驟2: 創建 TopicData 物件
        topic = TopicData(
            topic_id=topic_id,
            title=title,
            input_index=1,  # 暫時設為1
            persona_tags=classification.persona_tags,
            industry_tags=classification.industry_tags,
            event_tags=classification.event_tags,
            stock_tags=classification.stock_tags,
            classification=classification
        )
        
        # 步驟3: 分配 KOL
        assignments = self.assignment_service.assign_topics([topic], max_assignments_per_topic=3)
        logger.info(f"分配了 {len(assignments)} 個 KOL")
        
        # 步驟4: 生成內容
        generated_content = {}
        used_titles = set()  # 確保同一話題下不同 KOL 的標題不重複
        for assignment in assignments:
            try:
                # 根據 kol_serial 找到對應的 KOL 物件
                kol = next((k for k in self.assignment_service._kol_profiles if k.serial == assignment.kol_serial), None)
                if not kol:
                    logger.error(f"找不到 KOL serial {assignment.kol_serial}")
                    continue
                
                content_request = ContentRequest(
                    topic_title=title,
                    topic_keywords=", ".join(topic.persona_tags + topic.industry_tags + topic.event_tags),
                    kol_persona=kol.persona,
                    kol_nickname=kol.nickname,
                    content_type="investment",
                    target_audience="active_traders",
                    market_data={}  # 暫時為空
                )
                
                generated = self.content_generator.generate_complete_content(content_request, used_titles=list(used_titles))
                if generated.success:
                    generated_content[assignment.kol_serial] = generated  # 存儲完整的 GeneratedContent 物件
                    if generated.title:
                        used_titles.add(generated.title)
                    logger.info(f"為 KOL {kol.nickname} 生成內容成功")
                else:
                    logger.error(f"為 KOL {kol.nickname} 生成內容失敗: {generated.error_message}")
                    
            except Exception as e:
                logger.error(f"為 KOL serial {assignment.kol_serial} 生成內容時發生錯誤: {e}")
                continue
        
        return ProcessedTopic(
            topic_id=topic_id,
            title=title,
            content=content,
            assignments=assignments,
            generated_content=generated_content,
            classification=classification
        )
    
    def _update_post_records(self, processed_topic: ProcessedTopic):
        """
        更新貼文記錄表
        
        Args:
            processed_topic: 處理後的話題
        """
        try:
            # 準備要寫入的數據
            records_to_write = []
            
            for assignment in processed_topic.assignments:
                # 根據 kol_serial 找到對應的 KOL 物件
                kol = next((k for k in self.assignment_service._kol_profiles if k.serial == assignment.kol_serial), None)
                if not kol:
                    logger.error(f"找不到 KOL serial {assignment.kol_serial}")
                    continue
                
                generated_data = processed_topic.generated_content.get(assignment.kol_serial)
                if generated_data:
                    generated_title = generated_data.title
                    generated_full_content = generated_data.content
                else:
                    generated_title = ""
                    generated_full_content = ""
                
                # 生成貼文ID：如果是特定股票話題，使用股票代號-序號格式
                post_id = self._generate_post_id(processed_topic.topic_id, assignment.kol_serial, processed_topic.title)
                
                # 檢查是否重複
                if self._check_duplicate_post(post_id):
                    logger.warning(f"貼文ID {post_id} 已存在，跳過此記錄")
                    continue
                
                record = [
                    post_id,  # 貼文ID
                    assignment.kol_serial,  # KOL Serial
                    kol.nickname,  # KOL 暱稱
                    kol.member_id,  # KOL ID
                    kol.persona,  # Persona
                    "investment",  # Content Type
                    1,  # 已派發TopicIndex
                    processed_topic.topic_id,  # 已派發TopicID
                    generated_title,  # 已派發TopicTitle (使用生成的標題)
                    ", ".join(processed_topic.classification.persona_tags + processed_topic.classification.industry_tags + processed_topic.classification.event_tags + processed_topic.classification.stock_tags),  # 已派發TopicKeywords
                    generated_full_content,  # 生成內容
                    "ready_to_post",  # 發文狀態
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 上次排程時間
                    "",  # 發文時間戳記
                    "",  # 最近錯誤訊息
                    "",  # 平台發文ID
                    "",  # 平台發文URL
                    processed_topic.title  # 熱門話題標題 (新增欄位)
                ]
                
                records_to_write.append(record)
            
            # 寫入 Google Sheets
            if records_to_write:
                # 找到最後一行
                existing_data = self.sheets_client.read_sheet('貼文記錄表', 'A:R')  # 更新為 A:R 包含新欄位
                start_row = len(existing_data) + 1
                
                # 寫入新記錄
                range_name = f'A{start_row}:R{start_row + len(records_to_write) - 1}'  # 更新為 A:R
                self.sheets_client.write_sheet('貼文記錄表', records_to_write, range_name)
                
                logger.info(f"成功更新 {len(records_to_write)} 筆記錄到貼文記錄表")
            
        except Exception as e:
            logger.error(f"更新貼文記錄表失敗: {e}")
            raise

# 工廠函數
def create_topic_processor(sheets_client: GoogleSheetsClient) -> TopicProcessor:
    """創建話題處理器實例"""
    return TopicProcessor(sheets_client)
