#!/usr/bin/env python3
"""
Enhanced Sheets Recorder
用於記錄增強的貼文數據到 Google Sheets
"""

import os
import asyncio
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, Optional
from clients.google.sheets_client import GoogleSheetsClient

@dataclass
class EnhancedPostRecord:
    """增強的貼文記錄數據結構"""
    # 基本資訊
    post_id: str
    kol_serial: str
    kol_nickname: str
    kol_id: str
    persona: str
    content_type: str
    topic_id: str
    topic_title: str
    content: str
    status: str
    
    # 平台資訊
    platform_post_id: str = ""
    platform_post_url: str = ""
    
    # 觸發資訊
    trigger_type: str = ""
    trigger_event_id: str = ""
    
    # 數據來源
    data_sources: str = ""
    data_source_status: str = ""
    
    # Agent 決策
    agent_decision_record: str = ""
    
    # 內容屬性
    post_type: str = ""
    content_length_type: str = ""
    word_count: str = ""
    content_length_category: str = ""
    
    # KOL 設定
    kol_weight_settings: str = ""
    content_generation_time: str = ""
    kol_settings_version: str = ""
    
    # 向量設定
    length_vector: str = ""
    tone_vector: str = ""
    temperature_setting: str = ""
    body_parameter: str = ""
    
    # 品質控制
    quality_check_rounds: str = ""
    quality_score: str = ""
    quality_issues: str = ""
    regeneration_count: str = ""
    quality_improvements: str = ""

class EnhancedSheetsRecorder:
    """增強的 Google Sheets 記錄器"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        )
        
        # 欄位映射 (A-AH)
        self.column_mapping = {
            'post_id': 'A',
            'kol_serial': 'B', 
            'kol_nickname': 'C',
            'kol_id': 'D',
            'persona': 'E',
            'content_type': 'F',
            'topic_index': 'G',
            'topic_id': 'H',
            'topic_keywords': 'I',
            'generated_title': 'J',
            'status': 'K',
            'scheduled_time': 'L',
            'post_time': 'M',
            'error_message': 'N',
            'platform_post_id': 'O',
            'platform_post_url': 'P',
            'topic_title': 'Q',
            'trigger_type': 'R',
            'trigger_event_id': 'S',
            'data_sources': 'T',
            'data_source_status': 'U',
            'agent_decision_record': 'V',
            'post_type': 'W',
            'content_length_type': 'X',
            'word_count': 'Y',
            'content_length_category': 'Z',
            'kol_weight_settings': 'AA',
            'content_generation_time': 'AB',
            'kol_settings_version': 'AC',
            'length_vector': 'AD',
            'tone_vector': 'AE',
            'temperature_setting': 'AF',
            'body_parameter': 'AG',
            'quality_check_rounds': 'AH'
        }
    
    async def record_enhanced_post(self, record_data: Dict[str, Any]) -> bool:
        """記錄增強的貼文數據"""
        try:
            # 建立 EnhancedPostRecord 物件
            record = EnhancedPostRecord(
                post_id=record_data.get('post_id', ''),
                kol_serial=record_data.get('kol_serial', ''),
                kol_nickname=record_data.get('kol_nickname', ''),
                kol_id=record_data.get('kol_id', ''),
                persona=record_data.get('persona', ''),
                content_type=record_data.get('content_type', ''),
                topic_id=record_data.get('topic_id', ''),
                topic_title=record_data.get('topic_title', ''),
                content=record_data.get('content', ''),
                status=record_data.get('status', ''),
                platform_post_id=record_data.get('platform_post_id', ''),
                platform_post_url=record_data.get('platform_post_url', ''),
                trigger_type=record_data.get('trigger_type', ''),
                trigger_event_id=record_data.get('trigger_event_id', ''),
                data_sources=record_data.get('data_sources', ''),
                data_source_status=record_data.get('data_source_status', ''),
                agent_decision_record=record_data.get('agent_decision_record', ''),
                post_type=record_data.get('post_type', ''),
                content_length_type=record_data.get('content_length_type', ''),
                word_count=record_data.get('word_count', ''),
                content_length_category=record_data.get('content_length_category', ''),
                kol_weight_settings=record_data.get('kol_weight_settings', ''),
                content_generation_time=record_data.get('content_generation_time', ''),
                kol_settings_version=record_data.get('kol_settings_version', ''),
                length_vector=record_data.get('length_vector', ''),
                tone_vector=record_data.get('tone_vector', ''),
                temperature_setting=record_data.get('temperature_setting', ''),
                body_parameter=record_data.get('body_parameter', ''),
                quality_check_rounds=record_data.get('quality_check_rounds', ''),
                quality_score=record_data.get('quality_score', ''),
                quality_issues=record_data.get('quality_issues', ''),
                regeneration_count=record_data.get('regeneration_count', ''),
                quality_improvements=record_data.get('quality_improvements', '')
            )
            
            # 轉換為 Google Sheets 行格式
            row_data = self.convert_record_to_row(record)
            
            # 寫入 Google Sheets
            await self.sheets_client.append_sheet("貼文記錄表", [row_data])
            
            print(f"✅ 成功記錄貼文: {record.post_id}")
            return True
            
        except Exception as e:
            print(f"❌ 記錄貼文失敗: {e}")
            return False
    
    def convert_record_to_row(self, record: EnhancedPostRecord) -> list:
        """將 EnhancedPostRecord 轉換為 Google Sheets 行格式"""
        # 按照 A-AH 的順序建立行數據
        row = [None] * 34  # A-AH 共34欄
        
        # 映射欄位到正確位置
        field_mapping = [
            'post_id', 'kol_serial', 'kol_nickname', 'kol_id', 'persona',
            'content_type', 'topic_index', 'topic_id', 'topic_keywords', 'generated_title',
            'status', 'scheduled_time', 'post_time', 'error_message', 'platform_post_id',
            'platform_post_url', 'topic_title', 'trigger_type', 'trigger_event_id',
            'data_sources', 'data_source_status', 'agent_decision_record', 'post_type',
            'content_length_type', 'word_count', 'content_length_category', 'kol_weight_settings',
            'content_generation_time', 'kol_settings_version', 'length_vector', 'tone_vector',
            'temperature_setting', 'body_parameter', 'quality_check_rounds', 'quality_score'
        ]
        
        for i, field in enumerate(field_mapping):
            if hasattr(record, field):
                value = getattr(record, field, '')
                row[i] = value if value is not None else ''
        
        return row
    
    async def update_post_status(self, post_id: str, status: str, platform_data: Dict[str, str] = None):
        """更新貼文狀態"""
        try:
            # 讀取現有數據
            sheet_data = await self.sheets_client.read_sheet("貼文記錄表")
            
            # 找到對應的貼文
            for i, row in enumerate(sheet_data):
                if row[0] == post_id:  # post_id 在第一欄
                    # 更新狀態
                    row[10] = status  # status 在第11欄 (K)
                    
                    if platform_data:
                        row[14] = platform_data.get('platform_post_id', '')  # O
                        row[15] = platform_data.get('platform_post_url', '')  # P
                        row[12] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # M
                    
                    # 寫回 Google Sheets
                    await self.sheets_client.write_sheet("貼文記錄表", sheet_data)
                    print(f"✅ 成功更新貼文狀態: {post_id} -> {status}")
                    return True
            
            print(f"❌ 找不到貼文: {post_id}")
            return False
            
        except Exception as e:
            print(f"❌ 更新貼文狀態失敗: {e}")
            return False
