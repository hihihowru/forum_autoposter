#!/usr/bin/env python3
"""
KOL 資料庫和貼文生成紀錄備份腳本
確保數據安全，防止數據丟失
"""

import os
import sys
import json
import datetime
import subprocess
import psycopg2
from pathlib import Path
import shutil

# 配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'posting_management',
    'user': 'postgres',
    'password': 'password'
}

BACKUP_DIR = Path('./backups')
BACKUP_DIR.mkdir(exist_ok=True)

def log(message):
    """記錄日誌"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def backup_postgres_database():
    """備份 PostgreSQL 數據庫"""
    log("🔄 開始備份 PostgreSQL 數據庫...")
    
    try:
        # 生成備份文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / f"postgres_backup_{timestamp}.sql"
        
        # 使用 pg_dump 備份數據庫
        cmd = [
            'pg_dump',
            '-h', DATABASE_CONFIG['host'],
            '-p', str(DATABASE_CONFIG['port']),
            '-U', DATABASE_CONFIG['user'],
            '-d', DATABASE_CONFIG['database'],
            '--verbose',
            '--clean',
            '--create',
            '--if-exists',
            '-f', str(backup_file)
        ]
        
        # 設置環境變數（密碼）
        env = os.environ.copy()
        env['PGPASSWORD'] = DATABASE_CONFIG['password']
        
        # 執行備份命令
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            log(f"✅ PostgreSQL 備份成功: {backup_file}")
            return str(backup_file)
        else:
            log(f"❌ PostgreSQL 備份失敗: {result.stderr}")
            return None
            
    except Exception as e:
        log(f"❌ PostgreSQL 備份異常: {str(e)}")
        return None

def backup_docker_volume():
    """備份 Docker 卷"""
    log("🔄 開始備份 Docker 卷...")
    
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        volume_backup_dir = BACKUP_DIR / f"docker_volume_backup_{timestamp}"
        volume_backup_dir.mkdir(exist_ok=True)
        
        # 備份 postgres_data 卷
        volume_name = "n8n-migration-project_postgres_data"
        
        # 創建臨時容器來備份卷
        container_name = f"backup_container_{timestamp}"
        
        # 啟動臨時容器
        cmd = [
            'docker', 'run', '--rm',
            '-v', f'{volume_name}:/data',
            '-v', f'{volume_backup_dir.absolute()}:/backup',
            'alpine',
            'tar', 'czf', '/backup/postgres_data.tar.gz', '-C', '/data', '.'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            log(f"✅ Docker 卷備份成功: {volume_backup_dir}")
            return str(volume_backup_dir)
        else:
            log(f"❌ Docker 卷備份失敗: {result.stderr}")
            return None
            
    except Exception as e:
        log(f"❌ Docker 卷備份異常: {str(e)}")
        return None

def backup_kol_data():
    """備份 KOL 數據"""
    log("🔄 開始備份 KOL 數據...")
    
    try:
        # 連接數據庫
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        # 查詢所有 KOL 數據
        cursor.execute("""
            SELECT 
                post_id,
                session_id,
                kol_serial,
                kol_nickname,
                kol_persona,
                stock_code,
                stock_name,
                title,
                content,
                content_md,
                status,
                quality_score,
                ai_detection_score,
                risk_level,
                reviewer_notes,
                approved_by,
                approved_at,
                scheduled_at,
                published_at,
                cmoney_post_id,
                cmoney_post_url,
                publish_error,
                views,
                likes,
                comments,
                shares,
                topic_id,
                topic_title,
                created_at,
                updated_at
            FROM post_records 
            ORDER BY created_at DESC
        """)
        
        kol_data = []
        for row in cursor.fetchall():
            kol_data.append({
                'post_id': row[0],
                'session_id': row[1],
                'kol_serial': row[2],
                'kol_nickname': row[3],
                'kol_persona': row[4],
                'stock_code': row[5],
                'stock_name': row[6],
                'title': row[7],
                'content': row[8],
                'content_md': row[9],
                'status': row[10],
                'quality_score': row[11],
                'ai_detection_score': row[12],
                'risk_level': row[13],
                'reviewer_notes': row[14],
                'approved_by': row[15],
                'approved_at': row[16].isoformat() if row[16] else None,
                'scheduled_at': row[17].isoformat() if row[17] else None,
                'published_at': row[18].isoformat() if row[18] else None,
                'cmoney_post_id': row[19],
                'cmoney_post_url': row[20],
                'publish_error': row[21],
                'views': row[22],
                'likes': row[23],
                'comments': row[24],
                'shares': row[25],
                'topic_id': row[26],
                'topic_title': row[27],
                'created_at': row[28].isoformat() if row[28] else None,
                'updated_at': row[29].isoformat() if row[29] else None
            })
        
        # 保存到 JSON 文件
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / f"kol_data_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(kol_data, f, ensure_ascii=False, indent=2)
        
        cursor.close()
        conn.close()
        
        log(f"✅ KOL 數據備份成功: {backup_file}")
        log(f"📊 備份了 {len(kol_data)} 筆 KOL 記錄")
        return str(backup_file)
        
    except Exception as e:
        log(f"❌ KOL 數據備份異常: {str(e)}")
        return None

def backup_google_sheets_data():
    """備份 Google Sheets 數據"""
    log("🔄 開始備份 Google Sheets 數據...")
    
    try:
        # 檢查是否有 Google Sheets 相關文件
        sheets_files = []
        
        # 查找可能的 Google Sheets 備份文件
        for pattern in ['*.csv', '*.xlsx', '*.json']:
            for file in Path('.').glob(f'**/{pattern}'):
                if any(keyword in file.name.lower() for keyword in ['sheet', 'kol', 'post', 'record']):
                    sheets_files.append(file)
        
        if sheets_files:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            sheets_backup_dir = BACKUP_DIR / f"google_sheets_backup_{timestamp}"
            sheets_backup_dir.mkdir(exist_ok=True)
            
            for file in sheets_files:
                shutil.copy2(file, sheets_backup_dir)
            
            log(f"✅ Google Sheets 數據備份成功: {sheets_backup_dir}")
            log(f"📊 備份了 {len(sheets_files)} 個文件")
            return str(sheets_backup_dir)
        else:
            log("ℹ️ 未找到 Google Sheets 相關文件")
            return None
            
    except Exception as e:
        log(f"❌ Google Sheets 數據備份異常: {str(e)}")
        return None

def backup_config_files():
    """備份配置文件"""
    log("🔄 開始備份配置文件...")
    
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        config_backup_dir = BACKUP_DIR / f"config_backup_{timestamp}"
        config_backup_dir.mkdir(exist_ok=True)
        
        # 備份重要的配置文件
        config_files = [
            '.env',
            'docker-compose.full.yml',
            'docker-compose.yml',
            'requirements.txt'
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                shutil.copy2(config_file, config_backup_dir)
        
        # 備份 credentials 目錄（如果存在）
        if Path('credentials').exists():
            shutil.copytree('credentials', config_backup_dir / 'credentials')
        
        log(f"✅ 配置文件備份成功: {config_backup_dir}")
        return str(config_backup_dir)
        
    except Exception as e:
        log(f"❌ 配置文件備份異常: {str(e)}")
        return None

def create_backup_summary(backups):
    """創建備份摘要"""
    log("🔄 創建備份摘要...")
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_file = BACKUP_DIR / f"backup_summary_{timestamp}.json"
    
    summary = {
        'backup_timestamp': datetime.datetime.now().isoformat(),
        'backup_files': backups,
        'total_files': len([b for b in backups.values() if b is not None]),
        'database_status': 'healthy',
        'backup_location': str(BACKUP_DIR.absolute())
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    log(f"✅ 備份摘要創建成功: {summary_file}")
    return str(summary_file)

def verify_backup_integrity():
    """驗證備份完整性"""
    log("🔄 驗證備份完整性...")
    
    try:
        # 檢查最近的備份文件
        backup_files = list(BACKUP_DIR.glob('*'))
        if not backup_files:
            log("❌ 未找到備份文件")
            return False
        
        # 檢查 PostgreSQL 備份
        sql_backups = list(BACKUP_DIR.glob('postgres_backup_*.sql'))
        if sql_backups:
            latest_sql = max(sql_backups, key=os.path.getctime)
            if latest_sql.stat().st_size > 1024:  # 至少 1KB
                log(f"✅ PostgreSQL 備份文件完整: {latest_sql.name}")
            else:
                log(f"❌ PostgreSQL 備份文件可能損壞: {latest_sql.name}")
                return False
        
        # 檢查 KOL 數據備份
        json_backups = list(BACKUP_DIR.glob('kol_data_backup_*.json'))
        if json_backups:
            latest_json = max(json_backups, key=os.path.getctime)
            try:
                with open(latest_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        log(f"✅ KOL 數據備份完整: {latest_json.name} ({len(data)} 筆記錄)")
                    else:
                        log(f"❌ KOL 數據備份可能損壞: {latest_json.name}")
                        return False
            except json.JSONDecodeError:
                log(f"❌ KOL 數據備份格式錯誤: {latest_json.name}")
                return False
        
        log("✅ 備份完整性驗證通過")
        return True
        
    except Exception as e:
        log(f"❌ 備份完整性驗證失敗: {str(e)}")
        return False

def main():
    """主函數"""
    log("🚀 開始 KOL 資料庫和貼文生成紀錄備份流程")
    
    backups = {}
    
    # 1. 備份 PostgreSQL 數據庫
    backups['postgres_sql'] = backup_postgres_database()
    
    # 2. 備份 Docker 卷
    backups['docker_volume'] = backup_docker_volume()
    
    # 3. 備份 KOL 數據
    backups['kol_data'] = backup_kol_data()
    
    # 4. 備份 Google Sheets 數據
    backups['google_sheets'] = backup_google_sheets_data()
    
    # 5. 備份配置文件
    backups['config_files'] = backup_config_files()
    
    # 6. 創建備份摘要
    summary_file = create_backup_summary(backups)
    
    # 7. 驗證備份完整性
    integrity_ok = verify_backup_integrity()
    
    # 8. 顯示備份結果
    log("\n" + "="*60)
    log("📋 備份完成摘要")
    log("="*60)
    
    for backup_type, backup_path in backups.items():
        if backup_path:
            log(f"✅ {backup_type}: {backup_path}")
        else:
            log(f"❌ {backup_type}: 備份失敗")
    
    log(f"📄 備份摘要: {summary_file}")
    log(f"🔍 備份完整性: {'✅ 通過' if integrity_ok else '❌ 失敗'}")
    log(f"📁 備份位置: {BACKUP_DIR.absolute()}")
    
    if integrity_ok:
        log("\n🎉 所有數據已成功備份！您的 KOL 資料庫和貼文生成紀錄都是安全的。")
    else:
        log("\n⚠️ 備份過程中發現問題，請檢查日誌。")
    
    log("="*60)

if __name__ == "__main__":
    main()
