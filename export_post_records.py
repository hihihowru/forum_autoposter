#!/usr/bin/env python3
"""
導出 post_records 數據為 JSON 文件
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

def export_to_json(local_conn, output_file="post_records_backup.json"):
    """導出數據為 JSON 文件"""
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
            
            # 保存到 JSON 文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(records_list, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 數據已導出到 {output_file}")
            logger.info(f"📊 總共 {len(records_list)} 筆記錄")
            
            # 顯示前幾筆記錄的摘要
            logger.info("📋 前 3 筆記錄摘要:")
            for i, record in enumerate(records_list[:3]):
                logger.info(f"  {i+1}. {record['post_id']}: {record['title'][:50]}... ({record['status']})")
            
            return output_file
            
    except Exception as e:
        logger.error(f"❌ 導出數據失敗: {e}")
        raise

def main():
    """主函數"""
    logger.info("🚀 開始導出 post_records 數據...")
    
    local_conn = None
    
    try:
        # 連接本地數據庫
        logger.info("🔗 連接本地數據庫...")
        local_conn = get_local_db_connection()
        
        # 導出數據
        logger.info("📤 導出數據...")
        output_file = export_to_json(local_conn)
        
        logger.info("🎉 數據導出完成！")
        logger.info(f"📁 文件位置: {os.path.abspath(output_file)}")
        
    except Exception as e:
        logger.error(f"❌ 數據導出失敗: {e}")
        sys.exit(1)
    finally:
        if local_conn:
            local_conn.close()

if __name__ == "__main__":
    main()
