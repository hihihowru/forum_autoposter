#!/usr/bin/env python3
"""
遷移 post_records 數據從本地到 Railway
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_local_db_connection():
    """獲取本地數據庫連接"""
    try:
        # 本地數據庫連接
        local_db_url = "postgresql://postgres:password@localhost:5432/posting_management"
        return psycopg2.connect(local_db_url)
    except Exception as e:
        logger.error(f"❌ 連接本地數據庫失敗: {e}")
        raise

def get_railway_db_connection():
    """獲取 Railway 數據庫連接"""
    try:
        # Railway 數據庫連接
        railway_db_url = os.getenv("DATABASE_URL")
        if not railway_db_url:
            raise Exception("未找到 DATABASE_URL 環境變數")
        
        # Railway PostgreSQL URL 格式轉換
        if railway_db_url.startswith("postgres://"):
            railway_db_url = railway_db_url.replace("postgres://", "postgresql://", 1)
        
        return psycopg2.connect(railway_db_url)
    except Exception as e:
        logger.error(f"❌ 連接 Railway 數據庫失敗: {e}")
        raise

def export_local_data(local_conn):
    """從本地數據庫導出數據"""
    try:
        with local_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 獲取所有 post_records
            cursor.execute("SELECT * FROM post_records ORDER BY created_at")
            records = cursor.fetchall()
            
            logger.info(f"📊 從本地數據庫導出 {len(records)} 筆記錄")
            return records
    except Exception as e:
        logger.error(f"❌ 導出本地數據失敗: {e}")
        raise

def import_to_railway(railway_conn, records):
    """導入數據到 Railway 數據庫"""
    try:
        with railway_conn.cursor() as cursor:
            # 清空現有數據（如果有的話）
            cursor.execute("DELETE FROM post_records")
            logger.info("🗑️ 清空 Railway 數據庫中的現有數據")
            
            # 批量插入數據
            insert_sql = """
                INSERT INTO post_records (
                    post_id, created_at, updated_at, session_id, kol_serial, kol_nickname, 
                    kol_persona, stock_code, stock_name, title, content, content_md, 
                    status, reviewer_notes, approved_by, approved_at, scheduled_at, 
                    published_at, cmoney_post_id, cmoney_post_url, publish_error, 
                    views, likes, comments, shares, topic_id, topic_title, 
                    technical_analysis, serper_data, quality_score, ai_detection_score, 
                    risk_level, generation_params, commodity_tags, alternative_versions
                ) VALUES (
                    %(post_id)s, %(created_at)s, %(updated_at)s, %(session_id)s, 
                    %(kol_serial)s, %(kol_nickname)s, %(kol_persona)s, %(stock_code)s, 
                    %(stock_name)s, %(title)s, %(content)s, %(content_md)s, %(status)s, 
                    %(reviewer_notes)s, %(approved_by)s, %(approved_at)s, %(scheduled_at)s, 
                    %(published_at)s, %(cmoney_post_id)s, %(cmoney_post_url)s, 
                    %(publish_error)s, %(views)s, %(likes)s, %(comments)s, %(shares)s, 
                    %(topic_id)s, %(topic_title)s, %(technical_analysis)s, %(serper_data)s, 
                    %(quality_score)s, %(ai_detection_score)s, %(risk_level)s, 
                    %(generation_params)s, %(commodity_tags)s, %(alternative_versions)s
                )
            """
            
            # 轉換記錄為字典格式
            records_dict = []
            for record in records:
                record_dict = dict(record)
                # 處理 JSON 字段
                for json_field in ['technical_analysis', 'serper_data', 'generation_params', 'commodity_tags', 'alternative_versions']:
                    if record_dict.get(json_field):
                        if isinstance(record_dict[json_field], str):
                            try:
                                record_dict[json_field] = json.loads(record_dict[json_field])
                            except:
                                record_dict[json_field] = None
                        elif not isinstance(record_dict[json_field], dict):
                            record_dict[json_field] = None
                    else:
                        record_dict[json_field] = None
                
                records_dict.append(record_dict)
            
            # 批量插入
            cursor.executemany(insert_sql, records_dict)
            railway_conn.commit()
            
            logger.info(f"✅ 成功導入 {len(records_dict)} 筆記錄到 Railway 數據庫")
            
            # 驗證導入結果
            cursor.execute("SELECT COUNT(*) FROM post_records")
            count = cursor.fetchone()[0]
            logger.info(f"📊 Railway 數據庫中現有 {count} 筆記錄")
            
    except Exception as e:
        logger.error(f"❌ 導入數據到 Railway 失敗: {e}")
        railway_conn.rollback()
        raise

def main():
    """主函數"""
    logger.info("🚀 開始遷移 post_records 數據...")
    
    local_conn = None
    railway_conn = None
    
    try:
        # 連接數據庫
        logger.info("🔗 連接本地數據庫...")
        local_conn = get_local_db_connection()
        
        logger.info("🔗 連接 Railway 數據庫...")
        railway_conn = get_railway_db_connection()
        
        # 導出本地數據
        logger.info("📤 導出本地數據...")
        records = export_local_data(local_conn)
        
        # 導入到 Railway
        logger.info("📥 導入數據到 Railway...")
        import_to_railway(railway_conn, records)
        
        logger.info("🎉 數據遷移完成！")
        
    except Exception as e:
        logger.error(f"❌ 數據遷移失敗: {e}")
        sys.exit(1)
    finally:
        if local_conn:
            local_conn.close()
        if railway_conn:
            railway_conn.close()

if __name__ == "__main__":
    main()
