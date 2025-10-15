#!/usr/bin/env python3
"""
發文管理系統數據庫初始化腳本
創建數據庫表結構並同步KOL數據
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

# 數據庫配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/posting_management"
)

def create_database():
    """創建數據庫"""
    try:
        # 連接到postgres默認數據庫來創建新數據庫
        engine = create_engine("postgresql://postgres:password@localhost:5432/postgres")
        
        with engine.connect() as conn:
            # 檢查數據庫是否存在
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = 'posting_management'"
            ))
            
            if not result.fetchone():
                # 創建數據庫
                conn.execute(text("COMMIT"))  # 結束當前事務
                conn.execute(text("CREATE DATABASE posting_management"))
                print("✅ 數據庫 'posting_management' 創建成功")
            else:
                print("ℹ️  數據庫 'posting_management' 已存在")
                
    except Exception as e:
        print(f"❌ 創建數據庫失敗: {e}")
        return False
    
    return True

def run_migrations():
    """運行數據庫遷移"""
    try:
        # 設置Alembic配置
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
        
        # 運行遷移
        command.upgrade(alembic_cfg, "head")
        print("✅ 數據庫遷移完成")
        return True
        
    except Exception as e:
        print(f"❌ 數據庫遷移失敗: {e}")
        return False

def sync_kol_data():
    """同步KOL數據"""
    try:
        print("🔄 開始同步KOL數據...")
        
        # 導入並運行KOL同步服務
        from sync_kol_data import KOLDataSyncService
        
        sync_service = KOLDataSyncService()
        success = sync_service.run_sync()
        
        if success:
            print("✅ KOL數據同步完成")
            return True
        else:
            print("❌ KOL數據同步失敗")
            return False
            
    except Exception as e:
        print(f"❌ KOL數據同步失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 開始初始化發文管理系統數據庫...")
    
    # 1. 創建數據庫
    if not create_database():
        return False
    
    # 2. 運行遷移
    if not run_migrations():
        return False
    
    # 3. 同步KOL數據
    if not sync_kol_data():
        return False
    
    print("🎉 數據庫初始化完成！")
    print(f"📊 數據庫連接: {DATABASE_URL}")
    print("🔗 可以開始使用發文管理系統了")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
