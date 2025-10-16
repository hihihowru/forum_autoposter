#!/usr/bin/env python3
"""
插入測試數據到 post_records 表
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import uuid

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def insert_test_records(railway_conn):
    """插入測試記錄"""
    try:
        with railway_conn.cursor() as cursor:
            # 創建一些測試記錄
            test_records = [
                {
                    'post_id': str(uuid.uuid4()),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'session_id': 1,
                    'kol_serial': 200,
                    'kol_nickname': 'KOL-200',
                    'kol_persona': '技術分析專家',
                    'stock_code': '2330',
                    'stock_name': '台積電',
                    'title': '台積電(2330) 技術面分析與操作建議',
                    'content': '台積電今日表現強勢，技術指標顯示多頭趨勢明確...',
                    'content_md': '## 台積電(2330) 技術面分析\n\n台積電今日表現強勢...',
                    'status': 'draft',
                    'reviewer_notes': None,
                    'approved_by': None,
                    'approved_at': None,
                    'scheduled_at': None,
                    'published_at': None,
                    'cmoney_post_id': None,
                    'cmoney_post_url': None,
                    'publish_error': None,
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                    'topic_id': 'tech_analysis',
                    'topic_title': '技術分析',
                    'technical_analysis': json.dumps({'rsi': 65, 'macd': 'bullish', 'support': 580}),
                    'serper_data': json.dumps({'search_volume': 1000, 'trend': 'up'}),
                    'quality_score': 8.5,
                    'ai_detection_score': 0.95,
                    'risk_level': 'medium',
                    'generation_params': json.dumps({'model': 'gpt-4', 'temperature': 0.7}),
                    'commodity_tags': json.dumps(['半導體', '科技股', '龍頭股']),
                    'alternative_versions': json.dumps({'version_1': '短線操作', 'version_2': '長線投資'})
                },
                {
                    'post_id': str(uuid.uuid4()),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'session_id': 1,
                    'kol_serial': 201,
                    'kol_nickname': 'KOL-201',
                    'kol_persona': '基本面分析師',
                    'stock_code': '2317',
                    'stock_name': '鴻海',
                    'title': '鴻海(2317) 財報分析與投資價值評估',
                    'content': '鴻海最新財報顯示營收成長穩定，獲利能力持續改善...',
                    'content_md': '## 鴻海(2317) 財報分析\n\n鴻海最新財報顯示...',
                    'status': 'approved',
                    'reviewer_notes': '內容品質良好，建議發布',
                    'approved_by': 'admin',
                    'approved_at': datetime.now(),
                    'scheduled_at': None,
                    'published_at': None,
                    'cmoney_post_id': None,
                    'cmoney_post_url': None,
                    'publish_error': None,
                    'views': 150,
                    'likes': 12,
                    'comments': 3,
                    'shares': 2,
                    'topic_id': 'fundamental_analysis',
                    'topic_title': '基本面分析',
                    'technical_analysis': json.dumps({'pe_ratio': 12.5, 'pb_ratio': 1.2, 'roe': 8.5}),
                    'serper_data': json.dumps({'search_volume': 800, 'trend': 'stable'}),
                    'quality_score': 9.0,
                    'ai_detection_score': 0.98,
                    'risk_level': 'low',
                    'generation_params': json.dumps({'model': 'gpt-4', 'temperature': 0.5}),
                    'commodity_tags': json.dumps(['電子製造', '代工', '蘋果概念股']),
                    'alternative_versions': json.dumps({'version_1': '保守投資', 'version_2': '價值投資'})
                },
                {
                    'post_id': str(uuid.uuid4()),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'session_id': 2,
                    'kol_serial': 202,
                    'kol_nickname': 'KOL-202',
                    'kol_persona': '短線交易員',
                    'stock_code': '2454',
                    'stock_name': '聯發科',
                    'title': '聯發科(2454) 短線操作機會分析',
                    'content': '聯發科近期股價波動加大，短線操作機會浮現...',
                    'content_md': '## 聯發科(2454) 短線操作\n\n聯發科近期股價波動...',
                    'status': 'published',
                    'reviewer_notes': None,
                    'approved_by': 'admin',
                    'approved_at': datetime.now(),
                    'scheduled_at': datetime.now(),
                    'published_at': datetime.now(),
                    'cmoney_post_id': 'cmoney_12345',
                    'cmoney_post_url': 'https://cmoney.tw/post/12345',
                    'publish_error': None,
                    'views': 300,
                    'likes': 25,
                    'comments': 8,
                    'shares': 5,
                    'topic_id': 'short_term_trading',
                    'topic_title': '短線交易',
                    'technical_analysis': json.dumps({'rsi': 45, 'macd': 'neutral', 'resistance': 650}),
                    'serper_data': json.dumps({'search_volume': 1200, 'trend': 'volatile'}),
                    'quality_score': 7.5,
                    'ai_detection_score': 0.92,
                    'risk_level': 'high',
                    'generation_params': json.dumps({'model': 'gpt-4', 'temperature': 0.8}),
                    'commodity_tags': json.dumps(['IC設計', '手機晶片', '5G']),
                    'alternative_versions': json.dumps({'version_1': '激進操作', 'version_2': '穩健操作'})
                }
            ]
            
            # 插入記錄
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
            
            cursor.executemany(insert_sql, test_records)
            railway_conn.commit()
            
            logger.info(f"✅ 成功插入 {len(test_records)} 筆測試記錄")
            
            # 驗證插入結果
            cursor.execute("SELECT COUNT(*) FROM post_records")
            count = cursor.fetchone()[0]
            logger.info(f"📊 數據庫中現有 {count} 筆記錄")
            
            # 顯示狀態統計
            cursor.execute("SELECT status, COUNT(*) FROM post_records GROUP BY status")
            status_stats = cursor.fetchall()
            logger.info("📊 狀態統計:")
            for status, count in status_stats:
                logger.info(f"  {status}: {count} 筆")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ 插入測試記錄失敗: {e}")
        railway_conn.rollback()
        raise

def main():
    """主函數"""
    logger.info("🚀 開始插入測試數據到 post_records...")
    
    railway_conn = None
    
    try:
        # 連接 Railway 數據庫
        logger.info("🔗 連接 Railway 數據庫...")
        railway_conn = get_railway_db_connection()
        
        # 插入測試記錄
        logger.info("📥 插入測試記錄...")
        insert_test_records(railway_conn)
        
        logger.info("🎉 測試數據插入完成！")
        
    except Exception as e:
        logger.error(f"❌ 插入測試數據失敗: {e}")
        sys.exit(1)
    finally:
        if railway_conn:
            railway_conn.close()

if __name__ == "__main__":
    main()
