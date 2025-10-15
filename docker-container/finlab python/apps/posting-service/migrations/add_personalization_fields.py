#!/usr/bin/env python3
"""
數據庫遷移腳本：添加個人化機率分布欄位到 kol_profiles 表
"""

import psycopg2
import json
import logging

# 設置日誌
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def run_migration():
    """執行數據庫遷移"""
    try:
        # 連接數據庫
        conn = psycopg2.connect(
            host='postgres-db',
            port=5432,
            database='posting_management',
            user='postgres',
            password='password'
        )
        cursor = conn.cursor()
        
        logger.info("🔧 開始執行個人化機率分布欄位遷移...")
        
        # 添加個人化機率分布欄位的 SQL 語句
        migration_sql = """
        -- 添加個人化機率分布欄位
        ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS content_style_probabilities JSON;
        ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS analysis_depth_probabilities JSON;
        ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS content_length_probabilities JSON;
        """
        
        # 執行遷移
        cursor.execute(migration_sql)
        conn.commit()
        
        logger.info("✅ 個人化機率分布欄位遷移完成")
        
        # 為現有KOL設置預設機率分布
        default_content_style = {
            "technical": 0.3,
            "casual": 0.4,
            "professional": 0.2,
            "humorous": 0.1
        }
        
        default_analysis_depth = {
            "basic": 0.2,
            "detailed": 0.5,
            "comprehensive": 0.3
        }
        
        default_content_length = {
            "short": 0.1,
            "medium": 0.4,
            "long": 0.3,
            "extended": 0.15,
            "comprehensive": 0.05,
            "thorough": 0.0
        }
        
        # 更新所有KOL的機率分布
        update_sql = """
        UPDATE kol_profiles 
        SET 
            content_style_probabilities = %s,
            analysis_depth_probabilities = %s,
            content_length_probabilities = %s
        WHERE content_style_probabilities IS NULL
        """
        
        cursor.execute(update_sql, (
            json.dumps(default_content_style),
            json.dumps(default_analysis_depth),
            json.dumps(default_content_length)
        ))
        conn.commit()
        
        logger.info("✅ 預設機率分布設置完成")
        
        # 關閉連接
        cursor.close()
        conn.close()
        
        print("🎉 個人化機率分布欄位遷移成功完成！")
        
    except Exception as e:
        logger.error(f"❌ 遷移失敗: {e}")
        print(f"❌ 遷移失敗: {e}")

if __name__ == "__main__":
    run_migration()













