#!/usr/bin/env python3
"""
發文管理系統數據庫初始化腳本
用於創建數據庫表結構和初始數據
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
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

def create_initial_data():
    """創建初始數據"""
    try:
        from src.models.posting_models import Base, KOLProfile, PromptTemplate, SystemConfig
        from src.database import get_db
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            # 檢查是否已有數據
            if db.query(KOLProfile).count() > 0:
                print("ℹ️  初始數據已存在，跳過創建")
                return True
            
            # 創建默認KOL檔案
            default_kols = [
                KOLProfile(
                    serial=200,
                    nickname="川川哥",
                    persona="技術派",
                    style_preference="confident",
                    expertise_areas=["技術分析", "圖表解讀"],
                    activity_level="high",
                    question_ratio=0.6,
                    content_length="short",
                    interaction_starters=["你們覺得呢", "還能追嗎", "要進場嗎"]
                ),
                KOLProfile(
                    serial=201,
                    nickname="韭割哥",
                    persona="總經派",
                    style_preference="analytical",
                    expertise_areas=["數據分析", "統計建模", "政策解讀"],
                    activity_level="medium",
                    question_ratio=0.4,
                    content_length="long",
                    interaction_starters=["你怎麼看", "數據怎麼說", "模型預測"]
                ),
                KOLProfile(
                    serial=202,
                    nickname="梅川褲子",
                    persona="消息派",
                    style_preference="mysterious",
                    expertise_areas=["消息面", "內線", "市場傳聞"],
                    activity_level="high",
                    question_ratio=0.7,
                    content_length="medium",
                    interaction_starters=["你信嗎", "有內線嗎", "真的假的"]
                )
            ]
            
            for kol in default_kols:
                db.add(kol)
            
            # 創建默認Prompt模板
            default_templates = [
                PromptTemplate(
                    name="股票價格基本分析",
                    description="用於股票價格數據的基本分析",
                    data_source="stock_price",
                    template="分析{stock_name}({stock_code})的股價表現，包括：\n1. 當前價格：{current_price}\n2. 漲跌幅：{price_change}%\n3. 成交量：{volume}\n4. 技術分析：{technical_analysis}",
                    variables=["stock_name", "stock_code", "current_price", "price_change", "volume", "technical_analysis"],
                    technical_indicators=["MACD", "RSI", "MA"]
                ),
                PromptTemplate(
                    name="月營收分析",
                    description="用於月營收數據分析",
                    data_source="monthly_revenue",
                    template="分析{stock_name}的月營收表現：\n1. 本月營收：{revenue}\n2. 月增率：{mom_growth}%\n3. 年增率：{yoy_growth}%\n4. 營收趨勢：{revenue_trend}",
                    variables=["stock_name", "revenue", "mom_growth", "yoy_growth", "revenue_trend"]
                )
            ]
            
            for template in default_templates:
                db.add(template)
            
            # 創建系統配置
            system_configs = [
                SystemConfig(
                    key="default_content_length",
                    value="medium",
                    description="默認內容長度"
                ),
                SystemConfig(
                    key="max_posts_per_session",
                    value=10,
                    description="每個會話最大發文數量"
                ),
                SystemConfig(
                    key="auto_approve_threshold",
                    value=0.8,
                    description="自動審核通過的品質分數閾值"
                )
            ]
            
            for config in system_configs:
                db.add(config)
            
            db.commit()
            print("✅ 初始數據創建完成")
            return True
            
    except Exception as e:
        print(f"❌ 創建初始數據失敗: {e}")
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
    
    # 3. 創建初始數據
    if not create_initial_data():
        return False
    
    print("🎉 數據庫初始化完成！")
    print(f"📊 數據庫連接: {DATABASE_URL}")
    print("🔗 可以開始使用發文管理系統了")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
