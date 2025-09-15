#!/usr/bin/env python3
"""
恢復 KOL 數據到數據庫
從硬編碼的 KOL 設定中恢復數據到 PostgreSQL
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 硬編碼的 KOL 數據
KOL_DATA = {
    "200": {
        "nickname": "川川哥",
        "persona": "技術派",
        "email": "forum_200@cmoney.com.tw",
        "password": "D8k9mN2p",
        "member_id": "9505546",
        "expertise_areas": "技術分析,均線分析,MACD,KD指標",
        "model_id": "gpt-4",
        "total_posts": 0,
        "avg_interaction_rate": 0.0,
        "last_post_time": None,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "201": {
        "nickname": "韭割哥",
        "persona": "總經派",
        "email": "forum_201@cmoney.com.tw", 
        "password": "D8k9mN2p",
        "member_id": "9505547",
        "expertise_areas": "總經分析,基本面分析,政策解讀",
        "model_id": "gpt-4",
        "total_posts": 0,
        "avg_interaction_rate": 0.0,
        "last_post_time": None,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "202": {
        "nickname": "梅川褲子",
        "persona": "新聞派",
        "email": "forum_202@cmoney.com.tw",
        "password": "D8k9mN2p", 
        "member_id": "9505548",
        "expertise_areas": "新聞分析,市場情緒,即時資訊",
        "model_id": "gpt-4",
        "total_posts": 0,
        "avg_interaction_rate": 0.0,
        "last_post_time": None,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "203": {
        "nickname": "龜狗一日散戶",
        "persona": "籌碼派",
        "email": "forum_203@cmoney.com.tw",
        "password": "D8k9mN2p",
        "member_id": "9505549", 
        "expertise_areas": "籌碼面分析,外資動向,融資融券",
        "model_id": "gpt-4",
        "total_posts": 0,
        "avg_interaction_rate": 0.0,
        "last_post_time": None,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    "204": {
        "nickname": "板橋大who",
        "persona": "情緒派",
        "email": "forum_204@cmoney.com.tw",
        "password": "D8k9mN2p",
        "member_id": "9505550",
        "expertise_areas": "情緒分析,社群討論,恐慌貪婪指數",
        "model_id": "gpt-4", 
        "total_posts": 0,
        "avg_interaction_rate": 0.0,
        "last_post_time": None,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
}

async def restore_kol_data():
    """恢復 KOL 數據到數據庫"""
    try:
        # 導入數據庫服務
        from docker_container.finlab_python.apps.posting_service.kol_database_service import get_kol_database_service
        
        print("🔄 開始恢復 KOL 數據...")
        print(f"📊 準備恢復 {len(KOL_DATA)} 個 KOL")
        
        kol_service = get_kol_database_service()
        
        # 清空現有的 KOL 數據
        print("🗑️ 清空現有 KOL 數據...")
        await kol_service.clear_all_kols()
        
        # 插入新的 KOL 數據
        print("➕ 插入新的 KOL 數據...")
        for kol_serial, kol_data in KOL_DATA.items():
            try:
                kol_profile = await kol_service.create_kol_profile(
                    member_id=kol_data["member_id"],
                    email=kol_data["email"],
                    password=kol_data["password"],
                    persona=kol_data["persona"],
                    expertise_areas=kol_data["expertise_areas"],
                    model_id=kol_data["model_id"],
                    total_posts=kol_data["total_posts"],
                    avg_interaction_rate=kol_data["avg_interaction_rate"],
                    last_post_time=kol_data["last_post_time"],
                    is_active=kol_data["is_active"],
                    created_at=kol_data["created_at"],
                    updated_at=kol_data["updated_at"]
                )
                print(f"✅ 成功創建 KOL: {kol_data['nickname']} (Serial: {kol_serial})")
                
            except Exception as e:
                print(f"❌ 創建 KOL {kol_data['nickname']} 失敗: {e}")
        
        # 驗證數據
        print("\n🔍 驗證恢復的數據...")
        all_kols = await kol_service.get_all_kols()
        print(f"📈 數據庫中現有 {len(all_kols)} 個 KOL")
        
        for kol in all_kols:
            print(f"  - {kol.nickname} ({kol.persona}) - Member ID: {kol.member_id}")
            
        print("\n🎉 KOL 數據恢復完成！")
        
    except Exception as e:
        print(f"❌ 恢復 KOL 數據失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(restore_kol_data())

