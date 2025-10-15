#!/usr/bin/env python3
"""
緊急修復：將內存中的貼文數據遷移到 PostgreSQL 數據庫
確保數據不會丟失
"""

import json
import psycopg2
from datetime import datetime
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 數據庫連接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'posting_management',
    'user': 'postgres',
    'password': 'password'
}

def connect_to_database():
    """連接到 PostgreSQL 數據庫"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"❌ 數據庫連接失敗: {e}")
        return None

def migrate_posts_to_database():
    """將內存中的貼文數據遷移到 PostgreSQL 數據庫"""
    logger.info("🚀 開始緊急數據遷移...")
    
    # 1. 從 posting-service API 獲取所有貼文數據
    import requests
    try:
        response = requests.get('http://localhost:8001/posts')
        if response.status_code == 200:
            posts_data = response.json()
            posts = posts_data.get('posts', [])
            logger.info(f"📊 從 API 獲取到 {len(posts)} 筆貼文數據")
        else:
            logger.error(f"❌ API 請求失敗: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ 無法從 API 獲取數據: {e}")
        return False
    
    # 2. 連接到數據庫
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 3. 清空現有的 posts 表（確保乾淨的遷移）
        logger.info("🧹 清空現有的 posts 表...")
        cursor.execute("DELETE FROM posts")
        conn.commit()
        
        # 4. 插入所有貼文數據
        logger.info(f"💾 開始插入 {len(posts)} 筆貼文到數據庫...")
        
        for i, post in enumerate(posts):
            try:
                # 準備插入數據
                insert_data = {
                    'session_id': post.get('session_id'),
                    'title': post.get('title', ''),
                    'content': post.get('content', ''),
                    'status': post.get('status', 'draft'),
                    'kol_serial': post.get('kol_serial'),
                    'kol_nickname': post.get('kol_nickname', ''),
                    'kol_persona': post.get('kol_persona', ''),
                    'stock_code': post.get('stock_code', ''),
                    'stock_name': post.get('stock_name', ''),
                    'topic_id': post.get('topic_id'),
                    'topic_title': post.get('topic_title'),
                    'cmoney_post_id': post.get('cmoney_post_id'),
                    'cmoney_post_url': post.get('cmoney_post_url'),
                    'views': post.get('views', 0),
                    'likes': post.get('likes', 0),
                    'comments': post.get('comments', 0),
                    'shares': post.get('shares', 0),
                    'reviewer_notes': post.get('reviewer_notes'),
                    'approved_by': post.get('approved_by'),
                    'quality_score': post.get('quality_score'),
                    'ai_detection_score': post.get('ai_detection_score'),
                    'risk_level': post.get('risk_level'),
                    'publish_error': post.get('publish_error'),
                    'technical_analysis': json.dumps(post.get('technical_analysis')) if post.get('technical_analysis') else None,
                    'serper_data': json.dumps(post.get('serper_data')) if post.get('serper_data') else None,
                    'generation_params': post.get('generation_params', '{}'),
                    'commodity_tags': json.dumps(post.get('commodity_tags')) if post.get('commodity_tags') else None,
                    'created_at': post.get('created_at', datetime.now().isoformat()),
                    'updated_at': post.get('updated_at', datetime.now().isoformat()),
                    'approved_at': post.get('approved_at'),
                    'scheduled_at': post.get('scheduled_at'),
                    'published_at': post.get('published_at')
                }
                
                # 執行插入
                insert_query = """
                INSERT INTO posts (
                    session_id, title, content, status, kol_serial, kol_nickname, kol_persona,
                    stock_code, stock_name, topic_id, topic_title, cmoney_post_id, cmoney_post_url,
                    views, likes, comments, shares, reviewer_notes, approved_by, quality_score,
                    ai_detection_score, risk_level, publish_error, technical_analysis, serper_data,
                    generation_params, commodity_tags, created_at, updated_at, approved_at,
                    scheduled_at, published_at
                ) VALUES (
                    %(session_id)s, %(title)s, %(content)s, %(status)s, %(kol_serial)s, %(kol_nickname)s, %(kol_persona)s,
                    %(stock_code)s, %(stock_name)s, %(topic_id)s, %(topic_title)s, %(cmoney_post_id)s, %(cmoney_post_url)s,
                    %(views)s, %(likes)s, %(comments)s, %(shares)s, %(reviewer_notes)s, %(approved_by)s, %(quality_score)s,
                    %(ai_detection_score)s, %(risk_level)s, %(publish_error)s, %(technical_analysis)s, %(serper_data)s,
                    %(generation_params)s, %(commodity_tags)s, %(created_at)s, %(updated_at)s, %(approved_at)s,
                    %(scheduled_at)s, %(published_at)s
                )
                """
                
                cursor.execute(insert_query, insert_data)
                logger.info(f"✅ 插入貼文 {i+1}/{len(posts)}: {post.get('title', 'No Title')}")
                
            except Exception as e:
                logger.error(f"❌ 插入貼文 {i+1} 失敗: {e}")
                continue
        
        # 5. 提交事務
        conn.commit()
        logger.info(f"🎉 成功遷移 {len(posts)} 筆貼文到 PostgreSQL 數據庫！")
        
        # 6. 驗證遷移結果
        cursor.execute("SELECT COUNT(*) FROM posts")
        count = cursor.fetchone()[0]
        logger.info(f"📊 數據庫中現在有 {count} 筆貼文記錄")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 數據遷移失敗: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def verify_migration():
    """驗證遷移結果"""
    logger.info("🔍 驗證數據遷移結果...")
    
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 檢查總數
        cursor.execute("SELECT COUNT(*) FROM posts")
        total_count = cursor.fetchone()[0]
        
        # 檢查狀態分布
        cursor.execute("SELECT status, COUNT(*) FROM posts GROUP BY status")
        status_counts = cursor.fetchall()
        
        # 檢查最近創建的記錄
        cursor.execute("SELECT title, status, created_at FROM posts ORDER BY created_at DESC LIMIT 5")
        recent_posts = cursor.fetchall()
        
        logger.info(f"📊 總貼文數: {total_count}")
        logger.info(f"📊 狀態分布: {dict(status_counts)}")
        logger.info(f"📊 最近 5 筆貼文:")
        for post in recent_posts:
            logger.info(f"   - {post[0]} ({post[1]}) - {post[2]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 驗證失敗: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚨 緊急數據遷移開始...")
    print("=" * 60)
    
    # 執行遷移
    success = migrate_posts_to_database()
    
    if success:
        print("✅ 數據遷移成功！")
        print("=" * 60)
        
        # 驗證結果
        verify_migration()
        print("=" * 60)
        print("🎉 所有貼文數據已安全存儲到 PostgreSQL 數據庫！")
        print("💡 現在您的數據不會因為服務重啟而丟失")
    else:
        print("❌ 數據遷移失敗！")
        print("🚨 請立即檢查並修復問題！")
