#!/usr/bin/env python3
"""
排程來源追蹤欄位遷移腳本
"""

import os
import sys
import psycopg2
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.append('/app')

def migrate_schedule_source_tracking():
    """遷移排程來源追蹤欄位"""
    
    # 資料庫連接參數
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres-db:5432/finlab")
    
    try:
        # 連接資料庫
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ 成功連接到資料庫")
        
        # 檢查欄位是否已存在
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'schedule_tasks' 
        AND column_name IN ('source_type', 'source_batch_id', 'source_experiment_id', 'source_feature_name', 'created_by')
        """
        
        cursor = conn.cursor()
        cursor.execute(check_query)
        existing_columns = cursor.fetchall()
        existing_column_names = [row[0] for row in existing_columns]
        
        print(f"📋 現有欄位: {existing_column_names}")
        
        # 需要新增的欄位
        columns_to_add = [
            ('source_type', 'VARCHAR'),
            ('source_batch_id', 'VARCHAR'),
            ('source_experiment_id', 'VARCHAR'),
            ('source_feature_name', 'VARCHAR'),
            ('created_by', 'VARCHAR DEFAULT \'system\'')
        ]
        
        # 新增缺失的欄位
        for column_name, column_type in columns_to_add:
            if column_name not in existing_column_names:
                alter_query = f"ALTER TABLE schedule_tasks ADD COLUMN {column_name} {column_type}"
                try:
                    cursor.execute(alter_query)
                    conn.commit()
                    print(f"✅ 成功新增欄位: {column_name}")
                except Exception as e:
                    print(f"❌ 新增欄位失敗 {column_name}: {e}")
                    conn.rollback()
            else:
                print(f"⏭️ 欄位已存在: {column_name}")
        
        # 驗證欄位是否正確新增
        cursor.execute(check_query)
        final_check = cursor.fetchall()
        final_column_names = [row[0] for row in final_check]
        print(f"📋 最終欄位: {final_column_names}")
        
        # 關閉連接
        cursor.close()
        conn.close()
        print("✅ 遷移完成")
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        raise

if __name__ == "__main__":
    migrate_schedule_source_tracking()
