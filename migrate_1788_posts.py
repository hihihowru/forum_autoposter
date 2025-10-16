#!/usr/bin/env python3
"""
遷移 1788 筆 post_records 從本地到 Railway
確保所有欄位和數據完全一致
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
    """獲取本地數據庫連接 (n8n-migration-project)"""
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
        # Railway 數據庫連接 - 使用環境變數或直接指定
        railway_db_url = os.getenv("RAILWAY_DATABASE_URL", "postgresql://postgres:IIhZsyFLGLWQRcDrXGWsEQqPGPijfqJo@postgres.railway.internal:5432/railway")
        
        # 如果使用外部連接，需要替換 internal 為 public
        if "railway.internal" in railway_db_url:
            # 嘗試使用 Railway 的外部連接
            railway_db_url = railway_db_url.replace("postgres.railway.internal", "containers-us-west-1.railway.app")
            railway_db_url = railway_db_url.replace(":5432", ":5432")
        
        return psycopg2.connect(railway_db_url)
    except Exception as e:
        logger.error(f"❌ 連接 Railway 數據庫失敗: {e}")
        logger.error("請確保 Railway 數據庫可以從外部訪問")
        raise

def export_local_data(local_conn):
    """從本地數據庫導出所有 post_records"""
    try:
        with local_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 獲取所有 post_records
            cursor.execute("SELECT * FROM post_records ORDER BY created_at")
            records = cursor.fetchall()
            
            logger.info(f"📊 從本地數據庫導出 {len(records)} 筆記錄")
            
            # 轉換為可序列化的格式
            records_list = []
            for record in records:
                record_dict = dict(record)
                # 處理 datetime 對象
                for key, value in record_dict.items():
                    if isinstance(value, datetime):
                        record_dict[key] = value.isoformat()
                    elif value is None:
                        record_dict[key] = None
                
                records_list.append(record_dict)
            
            return records_list
            
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
            
            # 轉換記錄格式
            records_dict = []
            for record in records:
                record_dict = dict(record)
                
                # 處理 datetime 字符串
                for datetime_field in ['created_at', 'updated_at', 'approved_at', 'scheduled_at', 'published_at']:
                    if record_dict.get(datetime_field):
                        if isinstance(record_dict[datetime_field], str):
                            try:
                                record_dict[datetime_field] = datetime.fromisoformat(record_dict[datetime_field].replace('Z', '+00:00'))
                            except:
                                record_dict[datetime_field] = None
                        elif not isinstance(record_dict[datetime_field], datetime):
                            record_dict[datetime_field] = None
                    else:
                        record_dict[datetime_field] = None
                
                # 處理 JSON 字段 - 確保是字符串格式
                for json_field in ['technical_analysis', 'serper_data', 'generation_params', 'commodity_tags', 'alternative_versions']:
                    if record_dict.get(json_field):
                        if isinstance(record_dict[json_field], (dict, list)):
                            # 如果是字典或列表，轉換為 JSON 字符串
                            try:
                                record_dict[json_field] = json.dumps(record_dict[json_field], ensure_ascii=False)
                            except:
                                record_dict[json_field] = None
                        elif isinstance(record_dict[json_field], str):
                            # 如果已經是字符串，保持不變
                            pass
                        else:
                            record_dict[json_field] = None
                    else:
                        record_dict[json_field] = None
                
                records_dict.append(record_dict)
            
            # 批量插入
            logger.info(f"📥 開始插入 {len(records_dict)} 筆記錄到 Railway...")
            cursor.executemany(insert_sql, records_dict)
            railway_conn.commit()
            
            logger.info(f"✅ 成功導入 {len(records_dict)} 筆記錄到 Railway 數據庫")
            
            # 驗證導入結果
            cursor.execute("SELECT COUNT(*) FROM post_records")
            count = cursor.fetchone()[0]
            logger.info(f"📊 Railway 數據庫中現有 {count} 筆記錄")
            
            # 顯示狀態統計
            cursor.execute("SELECT status, COUNT(*) FROM post_records GROUP BY status")
            status_stats = cursor.fetchall()
            logger.info("📊 狀態統計:")
            for status, count in status_stats:
                logger.info(f"  {status}: {count} 筆")
            
            # 顯示前幾筆記錄的摘要
            cursor.execute("SELECT post_id, title, status, created_at FROM post_records ORDER BY created_at DESC LIMIT 5")
            sample_records = cursor.fetchall()
            logger.info("📋 前 5 筆記錄摘要:")
            for record in sample_records:
                logger.info(f"  {record[0]}: {record[1][:50]}... ({record[2]}) - {record[3]}")
            
    except Exception as e:
        logger.error(f"❌ 導入數據到 Railway 失敗: {e}")
        railway_conn.rollback()
        raise

def main():
    """主函數"""
    logger.info("🚀 開始遷移 1788 筆 post_records 數據...")
    
    local_conn = None
    railway_conn = None
    
    try:
        # 連接本地數據庫
        logger.info("🔗 連接本地數據庫 (n8n-migration-project)...")
        local_conn = get_local_db_connection()
        
        # 連接 Railway 數據庫
        logger.info("🔗 連接 Railway 數據庫...")
        railway_conn = get_railway_db_connection()
        
        # 導出本地數據
        logger.info("📤 導出本地數據...")
        records = export_local_data(local_conn)
        
        if len(records) != 1788:
            logger.warning(f"⚠️ 預期 1788 筆記錄，實際導出 {len(records)} 筆")
        
        # 導入到 Railway
        logger.info("📥 導入數據到 Railway...")
        import_to_railway(railway_conn, records)
        
        logger.info("🎉 數據遷移完成！")
        logger.info("🔍 請測試 Railway 的 /posts 端點確認數據已正確遷移")
        
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
