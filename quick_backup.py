#!/usr/bin/env python3
"""
快速備份腳本 - 確保 KOL 資料庫和貼文生成紀錄安全
"""

import os
import json
import datetime
import subprocess
from pathlib import Path

def log(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def quick_backup():
    """快速備份關鍵數據"""
    log("🚀 開始快速備份...")
    
    # 創建備份目錄
    backup_dir = Path('./backups')
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. 備份 PostgreSQL 數據庫
    log("🔄 備份 PostgreSQL 數據庫...")
    try:
        backup_file = backup_dir / f"postgres_backup_{timestamp}.sql"
        cmd = [
            'pg_dump',
            '-h', 'localhost',
            '-p', '5432',
            '-U', 'postgres',
            '-d', 'posting_management',
            '--verbose',
            '--clean',
            '--create',
            '-f', str(backup_file)
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = 'password'
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            log(f"✅ PostgreSQL 備份成功: {backup_file}")
        else:
            log(f"❌ PostgreSQL 備份失敗: {result.stderr}")
    except Exception as e:
        log(f"❌ PostgreSQL 備份異常: {str(e)}")
    
    # 2. 備份 Docker 卷
    log("🔄 備份 Docker 卷...")
    try:
        volume_backup_dir = backup_dir / f"docker_volume_{timestamp}"
        volume_backup_dir.mkdir(exist_ok=True)
        
        cmd = [
            'docker', 'run', '--rm',
            '-v', 'n8n-migration-project_postgres_data:/data',
            '-v', f'{volume_backup_dir.absolute()}:/backup',
            'alpine',
            'tar', 'czf', '/backup/postgres_data.tar.gz', '-C', '/data', '.'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            log(f"✅ Docker 卷備份成功: {volume_backup_dir}")
        else:
            log(f"❌ Docker 卷備份失敗: {result.stderr}")
    except Exception as e:
        log(f"❌ Docker 卷備份異常: {str(e)}")
    
    # 3. 檢查數據庫連接和數據
    log("🔄 檢查數據庫連接...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='posting_management',
            user='postgres',
            password='password'
        )
        cursor = conn.cursor()
        
        # 檢查表是否存在
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        log(f"✅ 數據庫連接成功，找到 {len(tables)} 個表")
        
        # 檢查 post_records 表的記錄數
        try:
            cursor.execute("SELECT COUNT(*) FROM post_records")
            count = cursor.fetchone()[0]
            log(f"📊 post_records 表中有 {count} 筆記錄")
        except Exception as e:
            log(f"⚠️ 無法讀取 post_records 表: {str(e)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        log(f"❌ 數據庫連接失敗: {str(e)}")
    
    log("✅ 快速備份完成！")
    log(f"📁 備份位置: {backup_dir.absolute()}")

if __name__ == "__main__":
    quick_backup()
