"""
KOL數據同步服務
從Google Sheets同步KOL數據到PostgreSQL數據庫
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.clients.google.sheets_client import GoogleSheetsClient

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 數據庫配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/posting_management"
)

class KOLDataSyncService:
    """KOL數據同步服務"""
    
    def __init__(self):
        # 初始化Google Sheets客戶端
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
        self.sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 初始化數據庫連接
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def read_kol_data_from_sheets(self) -> List[Dict[str, Any]]:
        """從Google Sheets讀取KOL數據"""
        try:
            logger.info("從Google Sheets讀取KOL數據...")
            
            # 讀取同學會帳號管理表
            data = self.sheets_client.read_sheet('同學會帳號管理')
            
            if not data or len(data) < 2:
                logger.warning("沒有找到KOL配置數據")
                return []
            
            headers = data[0]
            rows = data[1:]
            
            logger.info(f"找到 {len(rows)} 個KOL記錄")
            logger.info(f"欄位: {headers}")
            
            # 建立欄位索引映射
            field_map = {}
            for i, header in enumerate(headers):
                if '序號' in header:
                    field_map['serial'] = i
                elif '暱稱' in header:
                    field_map['nickname'] = i
                elif 'Email' in header or '帳號' in header:
                    field_map['email'] = i
                elif '密碼' in header:
                    field_map['password'] = i
                elif 'MemberId' in header:
                    field_map['member_id'] = i
                elif '人設' in header:
                    field_map['persona'] = i
                elif '狀態' in header and i < 20:
                    field_map['status'] = i
                elif 'Topic偏好類別' in header:
                    field_map['topic_preferences'] = i
                elif '禁講類別' in header:
                    field_map['forbidden_categories'] = i
                elif '資料偏好' in header:
                    field_map['data_preferences'] = i
                elif '內容類型' in header:
                    field_map['content_types'] = i
                elif '目標受眾' in header:
                    field_map['target_audience'] = i
                elif '語氣風格' in header:
                    field_map['tone_style'] = i
                elif '常用詞彙' in header:
                    field_map['common_words'] = i
                elif '口語化用詞' in header:
                    field_map['colloquial_words'] = i
                elif '常用打字習慣' in header:
                    field_map['typing_habit'] = i
                elif '前導故事' in header:
                    field_map['background_story'] = i
                elif '專長領域' in header:
                    field_map['expertise_areas'] = i
                elif 'PromptCTA' in header:
                    field_map['signature'] = i
                elif 'QuestionRatio' in header:
                    field_map['question_ratio'] = i
                elif 'ContentLength' in header:
                    field_map['content_length'] = i
                elif 'InteractionStarters' in header:
                    field_map['interaction_starters'] = i
                elif 'RequireFinlabAPI' in header:
                    field_map['require_finlab_api'] = i
                elif 'AllowHashtags' in header:
                    field_map['allow_hashtags'] = i
            
            logger.info(f"欄位映射: {field_map}")
            
            # 解析KOL資料
            kol_profiles = []
            for row_idx, row in enumerate(rows):
                if len(row) < 5:  # 跳過空行
                    continue
                    
                try:
                    # 確保行長度與標題一致
                    padded_row = row + [''] * (len(headers) - len(row))
                    
                    kol_data = {
                        'serial': int(padded_row[field_map.get('serial', 0)]) if field_map.get('serial') and padded_row[field_map['serial']] else None,
                        'nickname': padded_row[field_map.get('nickname', 1)] if field_map.get('nickname') else '',
                        'email': padded_row[field_map.get('email', 2)] if field_map.get('email') else '',
                        'password': padded_row[field_map.get('password', 3)] if field_map.get('password') else '',
                        'member_id': padded_row[field_map.get('member_id', 4)] if field_map.get('member_id') else '',
                        'persona': padded_row[field_map.get('persona', 5)] if field_map.get('persona') else '',
                        'status': padded_row[field_map.get('status', 6)] if field_map.get('status') else 'active',
                        'topic_preferences': self._parse_csv(padded_row[field_map.get('topic_preferences', 7)]) if field_map.get('topic_preferences') else [],
                        'forbidden_categories': self._parse_csv(padded_row[field_map.get('forbidden_categories', 8)]) if field_map.get('forbidden_categories') else [],
                        'data_preferences': self._parse_csv(padded_row[field_map.get('data_preferences', 9)]) if field_map.get('data_preferences') else [],
                        'content_types': self._parse_csv(padded_row[field_map.get('content_types', 10)]) if field_map.get('content_types') else [],
                        'target_audience': padded_row[field_map.get('target_audience', 11)] if field_map.get('target_audience') else '',
                        'tone_style': padded_row[field_map.get('tone_style', 12)] if field_map.get('tone_style') else '',
                        'common_words': self._parse_csv(padded_row[field_map.get('common_words', 13)]) if field_map.get('common_words') else [],
                        'colloquial_words': self._parse_csv(padded_row[field_map.get('colloquial_words', 14)]) if field_map.get('colloquial_words') else [],
                        'typing_habit': padded_row[field_map.get('typing_habit', 15)] if field_map.get('typing_habit') else '',
                        'background_story': padded_row[field_map.get('background_story', 16)] if field_map.get('background_story') else '',
                        'expertise_areas': self._parse_csv(padded_row[field_map.get('expertise_areas', 17)]) if field_map.get('expertise_areas') else [],
                        'signature': padded_row[field_map.get('signature', 18)] if field_map.get('signature') else '',
                        'question_ratio': float(padded_row[field_map.get('question_ratio', 19)]) if field_map.get('question_ratio') and padded_row[field_map['question_ratio']] else 0.5,
                        'content_length': padded_row[field_map.get('content_length', 20)] if field_map.get('content_length') else 'medium',
                        'interaction_starters': self._parse_csv(padded_row[field_map.get('interaction_starters', 21)]) if field_map.get('interaction_starters') else [],
                        'require_finlab_api': padded_row[field_map.get('require_finlab_api', 22)].strip().upper() == 'TRUE' if field_map.get('require_finlab_api') else False,
                        'allow_hashtags': padded_row[field_map.get('allow_hashtags', 23)].strip().upper() == 'TRUE' if field_map.get('allow_hashtags') else True,
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    
                    # 只處理有效的KOL（有序號和暱稱）
                    if kol_data['serial'] and kol_data['nickname']:
                        kol_profiles.append(kol_data)
                        logger.info(f"解析KOL: {kol_data['serial']} - {kol_data['nickname']}")
                    
                except Exception as e:
                    logger.error(f"解析第 {row_idx + 2} 行KOL數據失敗: {e}")
                    continue
            
            logger.info(f"成功解析 {len(kol_profiles)} 個KOL資料")
            return kol_profiles
            
        except Exception as e:
            logger.error(f"從Google Sheets讀取KOL數據失敗: {e}")
            return []
    
    def _parse_csv(self, value: str) -> List[str]:
        """解析CSV格式的字符串"""
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def sync_kols_to_database(self, kol_profiles: List[Dict[str, Any]]) -> bool:
        """將KOL數據同步到數據庫"""
        try:
            logger.info("開始同步KOL數據到數據庫...")
            
            with self.SessionLocal() as db:
                # 清空現有KOL數據
                db.execute(text("DELETE FROM kol_profiles"))
                logger.info("清空現有KOL數據")
                
                # 插入新的KOL數據
                for kol_data in kol_profiles:
                    try:
                        # 構建插入SQL
                        insert_sql = text("""
                            INSERT INTO kol_profiles (
                                serial, nickname, name, persona, style_preference,
                                expertise_areas, activity_level, question_ratio,
                                content_length, interaction_starters, is_active,
                                created_at, updated_at
                            ) VALUES (
                                :serial, :nickname, :name, :persona, :style_preference,
                                :expertise_areas, :activity_level, :question_ratio,
                                :content_length, :interaction_starters, :is_active,
                                :created_at, :updated_at
                            )
                        """)
                        
                        # 準備數據
                        db_data = {
                            'serial': kol_data['serial'],
                            'nickname': kol_data['nickname'],
                            'name': kol_data.get('name', ''),
                            'persona': kol_data['persona'],
                            'style_preference': kol_data.get('tone_style', ''),
                            'expertise_areas': kol_data['expertise_areas'],
                            'activity_level': 'high' if kol_data['status'] == 'active' else 'low',
                            'question_ratio': kol_data['question_ratio'],
                            'content_length': kol_data['content_length'],
                            'interaction_starters': kol_data['interaction_starters'],
                            'is_active': kol_data['status'] == 'active',
                            'created_at': kol_data['created_at'],
                            'updated_at': kol_data['updated_at']
                        }
                        
                        db.execute(insert_sql, db_data)
                        logger.info(f"插入KOL: {kol_data['serial']} - {kol_data['nickname']}")
                        
                    except Exception as e:
                        logger.error(f"插入KOL {kol_data['serial']} 失敗: {e}")
                        continue
                
                db.commit()
                logger.info(f"成功同步 {len(kol_profiles)} 個KOL到數據庫")
                return True
                
        except Exception as e:
            logger.error(f"同步KOL數據到數據庫失敗: {e}")
            return False
    
    def run_sync(self) -> bool:
        """執行完整的同步流程"""
        try:
            logger.info("🚀 開始KOL數據同步流程...")
            
            # 1. 從Google Sheets讀取數據
            kol_profiles = self.read_kol_data_from_sheets()
            if not kol_profiles:
                logger.error("沒有讀取到KOL數據")
                return False
            
            # 2. 同步到數據庫
            success = self.sync_kols_to_database(kol_profiles)
            if success:
                logger.info("✅ KOL數據同步完成！")
                return True
            else:
                logger.error("❌ KOL數據同步失敗")
                return False
                
        except Exception as e:
            logger.error(f"KOL數據同步流程失敗: {e}")
            return False

def main():
    """主函數"""
    try:
        sync_service = KOLDataSyncService()
        success = sync_service.run_sync()
        
        if success:
            print("🎉 KOL數據同步成功！")
            print("📊 現在可以從數據庫讀取KOL數據了")
        else:
            print("❌ KOL數據同步失敗")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 同步服務啟動失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
