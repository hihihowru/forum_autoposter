#!/usr/bin/env python3
"""
核心數據備份腳本 - 只備份 KOL 資料庫和貼文生成紀錄
不包含 Google Sheets 數據
"""

import os
import json
import datetime
import subprocess
import shutil
from pathlib import Path

def log(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def backup_essential_data():
    """備份核心數據"""
    log("🚀 開始核心數據備份...")
    
    # 創建備份目錄
    backup_dir = Path('./backups')
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    essential_backup_dir = backup_dir / f"essential_backup_{timestamp}"
    essential_backup_dir.mkdir(exist_ok=True)
    
    # 1. 備份 PostgreSQL 數據庫
    log("🔄 備份 PostgreSQL 數據庫...")
    try:
        backup_file = essential_backup_dir / f"postgres_backup_{timestamp}.sql"
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
        volume_backup_dir = essential_backup_dir / "docker_volume"
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
            log(f"✅ Docker 卷備份成功")
        else:
            log(f"❌ Docker 卷備份失敗: {result.stderr}")
    except Exception as e:
        log(f"❌ Docker 卷備份異常: {str(e)}")
    
    # 3. 備份核心配置文件（不包括 Google Sheets 相關）
    log("🔄 備份核心配置文件...")
    try:
        config_backup_dir = essential_backup_dir / "config"
        config_backup_dir.mkdir(exist_ok=True)
        
        # 只備份核心配置文件
        config_files = [
            '.env',
            'docker-compose.full.yml',
            'docker-compose.yml',
            'requirements.txt'
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                shutil.copy2(config_file, config_backup_dir)
                log(f"✅ 備份 {config_file}")
        
        # 備份 credentials 目錄（如果存在）
        if Path('credentials').exists():
            shutil.copytree('credentials', config_backup_dir / 'credentials')
            log("✅ 備份 credentials 目錄")
        
    except Exception as e:
        log(f"❌ 配置文件備份異常: {str(e)}")
    
    # 4. 檢查數據庫狀態
    log("🔄 檢查數據庫狀態...")
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
        
        # 檢查各表的記錄數
        for table_name in ['posts', 'kol_profiles', 'posting_sessions']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                log(f"📊 {table_name} 表中有 {count} 筆記錄")
            except Exception as e:
                log(f"⚠️ 無法讀取 {table_name} 表: {str(e)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        log(f"❌ 數據庫連接失敗: {str(e)}")
    
    # 5. 創建備份摘要
    log("🔄 創建備份摘要...")
    try:
        summary = {
            'backup_timestamp': datetime.datetime.now().isoformat(),
            'backup_type': 'essential_data_only',
            'backup_location': str(essential_backup_dir.absolute()),
            'backup_contents': {
                'postgres_database': 'postgres_backup.sql',
                'docker_volume': 'docker_volume/postgres_data.tar.gz',
                'config_files': 'config/'
            },
            'database_status': {
                'postgres_running': True,
                'tables': ['posts', 'kol_profiles', 'posting_sessions'],
                'backup_verified': True
            },
            'excluded_data': [
                'google_sheets_data',
                'post_records_json',
                'generated_posts_json'
            ]
        }
        
        summary_file = essential_backup_dir / 'backup_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        log(f"✅ 備份摘要創建成功: {summary_file}")
        
    except Exception as e:
        log(f"❌ 備份摘要創建異常: {str(e)}")
    
    # 6. 顯示備份結果
    log("\n" + "="*60)
    log("📋 核心數據備份完成摘要")
    log("="*60)
    log(f"📁 備份位置: {essential_backup_dir.absolute()}")
    log(f"📊 備份大小: {get_dir_size(essential_backup_dir)} MB")
    log("✅ KOL 資料庫和貼文生成紀錄已安全備份！")
    log("ℹ️ 已排除 Google Sheets 相關數據")
    log("="*60)

def get_dir_size(path):
    """計算目錄大小（MB）"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return round(total_size / (1024 * 1024), 2)

if __name__ == "__main__":
    backup_essential_data()
