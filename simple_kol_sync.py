#!/usr/bin/env python3
"""
簡化版KOL數據同步服務
直接使用已知的KOL數據，不依賴Google Sheets
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 數據庫配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/posting_management"
)

class SimpleKOLDataSyncService:
    """簡化版KOL數據同步服務"""
    
    def __init__(self):
        # 初始化數據庫連接
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def get_known_kol_data(self) -> List[Dict[str, Any]]:
        """獲取已知的KOL數據"""
        return [
            {
                'serial': 200,
                'nickname': '川川哥',
                'name': '川川哥',
                'persona': '技術派',
                'style_preference': '自信直球，有時會狂妄，有時又碎碎念',
                'expertise_areas': ['技術分析', '圖表解讀'],
                'activity_level': 'high',
                'question_ratio': 0.6,
                'content_length': 'short',
                'interaction_starters': ['你們覺得呢', '還能追嗎', '要進場嗎'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 201,
                'nickname': '韭割哥',
                'name': '韭割哥',
                'persona': '總經派',
                'style_preference': '犀利批判，數據驅動的冷靜分析師',
                'expertise_areas': ['數據分析', '統計建模', '政策解讀'],
                'activity_level': 'high',
                'question_ratio': 0.4,
                'content_length': 'long',
                'interaction_starters': ['你怎麼看', '數據怎麼說', '模型預測'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 202,
                'nickname': '梅川褲子',
                'name': '梅川褲子',
                'persona': '消息派',
                'style_preference': '神秘兮兮，喜歡賣關子',
                'expertise_areas': ['消息面', '內線', '市場傳聞'],
                'activity_level': 'high',
                'question_ratio': 0.7,
                'content_length': 'medium',
                'interaction_starters': ['你信嗎', '有內線嗎', '真的假的'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 203,
                'nickname': '龜狗一日散戶',
                'name': '龜狗一日散戶',
                'persona': '散戶派',
                'style_preference': '自嘲式幽默，散戶心聲',
                'expertise_areas': ['散戶心理', '情緒管理'],
                'activity_level': 'high',
                'question_ratio': 0.7,
                'content_length': 'short',
                'interaction_starters': ['今天又', '散戶的悲哀', '被割了'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 204,
                'nickname': '板橋大who',
                'name': '板橋大who',
                'persona': '地方派',
                'style_preference': '親切在地，地方色彩濃厚',
                'expertise_areas': ['地方企業', '區域經濟'],
                'activity_level': 'high',
                'question_ratio': 0.5,
                'content_length': 'medium',
                'interaction_starters': ['板橋這邊', '在地人說', '新北地區'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 205,
                'nickname': '八卦護城河',
                'name': '八卦護城河',
                'persona': '八卦派',
                'style_preference': '八卦熱情，喜歡分享內幕',
                'expertise_areas': ['八卦消息', '內幕情報'],
                'activity_level': 'high',
                'question_ratio': 0.8,
                'content_length': 'medium',
                'interaction_starters': ['聽說', '八卦一下', '內幕消息'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 206,
                'nickname': '小道爆料王',
                'name': '小道爆料王',
                'persona': '爆料派',
                'style_preference': '神秘爆料，獨家消息',
                'expertise_areas': ['獨家消息', '內幕爆料'],
                'activity_level': 'high',
                'question_ratio': 0.2,
                'content_length': 'medium',
                'interaction_starters': ['獨家爆料', '內幕消息', '小道消息'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 207,
                'nickname': '信號宅神',
                'name': '信號宅神',
                'persona': '技術派',
                'style_preference': '技術宅，信號分析',
                'expertise_areas': ['技術指標', '信號分析'],
                'activity_level': 'high',
                'question_ratio': 0.4,
                'content_length': 'medium',
                'interaction_starters': ['信號來了', '指標顯示', '技術分析'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 208,
                'nickname': '長線韭韭',
                'name': '長線韭韭',
                'persona': '價值派',
                'style_preference': '穩健長線，價值投資',
                'expertise_areas': ['價值投資', '基本面分析'],
                'activity_level': 'high',
                'question_ratio': 0.3,
                'content_length': 'long',
                'interaction_starters': ['長線持有', '價值投資', '基本面'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 209,
                'nickname': '報爆哥_209',
                'name': '報爆哥_209',
                'persona': '新聞派',
                'style_preference': '新聞導向，客觀分析',
                'expertise_areas': ['新聞分析', '市場報導'],
                'activity_level': 'high',
                'question_ratio': 0.5,
                'content_length': 'medium',
                'interaction_starters': ['新聞說', '報導指出', '分析顯示'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 210,
                'nickname': '數據獵人',
                'name': '數據獵人',
                'persona': '數據派',
                'style_preference': '數據驅動，客觀分析',
                'expertise_areas': ['數據分析', '統計建模'],
                'activity_level': 'high',
                'question_ratio': 0.3,
                'content_length': 'long',
                'interaction_starters': ['數據顯示', '統計表明', '分析結果'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'serial': 150,
                'nickname': '隔日沖獵人',
                'name': '隔日沖獵人',
                'persona': '短線派',
                'style_preference': '短線操作，快進快出',
                'expertise_areas': ['短線交易', '隔日沖'],
                'activity_level': 'high',
                'question_ratio': 0.6,
                'content_length': 'short',
                'interaction_starters': ['隔日沖', '短線操作', '當沖'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    
    def create_kol_table(self):
        """創建KOL表"""
        try:
            with self.SessionLocal() as db:
                # 創建KOL表
                create_table_sql = text("""
                    CREATE TABLE IF NOT EXISTS kol_profiles (
                        id SERIAL PRIMARY KEY,
                        serial INTEGER UNIQUE NOT NULL,
                        nickname VARCHAR(100) NOT NULL,
                        name VARCHAR(100),
                        persona VARCHAR(50),
                        style_preference TEXT,
                        expertise_areas TEXT[],
                        activity_level VARCHAR(20),
                        question_ratio FLOAT,
                        content_length VARCHAR(20),
                        interaction_starters TEXT[],
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                db.execute(create_table_sql)
                db.commit()
                logger.info("✅ KOL表創建成功")
                
        except Exception as e:
            logger.error(f"❌ 創建KOL表失敗: {e}")
            raise
    
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
                        
                        db.execute(insert_sql, kol_data)
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
            
            # 1. 創建表
            self.create_kol_table()
            
            # 2. 獲取KOL數據
            kol_profiles = self.get_known_kol_data()
            logger.info(f"獲取到 {len(kol_profiles)} 個KOL資料")
            
            # 3. 同步到數據庫
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
        sync_service = SimpleKOLDataSyncService()
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
