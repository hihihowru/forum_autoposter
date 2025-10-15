#!/usr/bin/env python3
"""
KOL 數據初始化腳本
確保 PostgreSQL 中有完整的 KOL 數據，即使重建容器也不會丟失
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 完整的 KOL 數據 - 基於硬編碼設定
KOL_DATA = {
    "200": {
        "serial": "200",
        "nickname": "川川哥",
        "persona": "技術派",
        "email": "forum_200@cmoney.com.tw",
        "password": "D8k9mN2p",
        "member_id": "9505546",
        "status": "active",
        "owner": "威廉用",
        "notes": "技術分析專家，專精均線分析、MACD、KD指標",
        "post_times": "09:00,15:00",
        "target_audience": "技術分析愛好者",
        "interaction_threshold": 0.6,
        "common_terms": "黃金交叉,均線糾結,三角收斂,K棒爆量,跳空缺口,支撐帶,壓力線,MACD背離",
        "colloquial_terms": "穩了啦,爆啦,嘎到,要噴啦,破線啦,睡醒漲停",
        "tone_style": "直接但有料，有時會狂妄，有時又碎碎念",
        "typing_habit": "省略號分隔，不愛標點符號，全部用省略號串起來",
        "backstory": "專精技術分析的股市老手，語氣直接但有料",
        "expertise": "技術分析,均線分析,MACD,KD指標",
        "data_source": "finlab_api",
        "model_id": "gpt-4",
        "model_temp": 0.7,
        "max_tokens": 500
    },
    "201": {
        "serial": "201",
        "nickname": "韭割哥",
        "persona": "總經派",
        "email": "forum_201@cmoney.com.tw", 
        "password": "D8k9mN2p",
        "member_id": "9505547",
        "status": "active",
        "owner": "威廉用",
        "notes": "總經分析專家，專精基本面分析、政策解讀",
        "post_times": "09:00,15:00",
        "target_audience": "基本面投資者",
        "interaction_threshold": 0.6,
        "common_terms": "通膨壓力,利率決策,CPI,GDP成長,失業率,美元指數,資金寬鬆",
        "colloquial_terms": "通膨炸裂,要升息啦,撐不住了,別太樂觀,慢慢加碼,長線投資",
        "tone_style": "沉穩理性，但常用比較說教的語氣",
        "typing_habit": "全形標點符號，長句分析，邏輯清晰",
        "backstory": "專精總經分析的投資老手，沉穩理性",
        "expertise": "總經分析,基本面分析,政策解讀",
        "data_source": "news_api",
        "model_id": "gpt-4",
        "model_temp": 0.6,
        "max_tokens": 600
    },
    "202": {
        "serial": "202",
        "nickname": "梅川褲子",
        "persona": "新聞派",
        "email": "forum_202@cmoney.com.tw",
        "password": "D8k9mN2p", 
        "member_id": "9505548",
        "status": "active",
        "owner": "威廉用",
        "notes": "新聞分析專家，敏銳的財經新聞分析師",
        "post_times": "09:00,15:00",
        "target_audience": "新聞追蹤者",
        "interaction_threshold": 0.6,
        "common_terms": "爆新聞啦,風向轉了,盤中爆炸,快訊快訊,漲停新聞,政策護航",
        "colloquial_terms": "現在就進,看漲,衝第一,蹭題材啦,來不及啦,有人知道嗎",
        "tone_style": "語氣急躁，常常快打快收，看起來像新聞狗",
        "typing_habit": "不愛空格，爆Emoji，驚嘆號狂刷，打字很急",
        "backstory": "敏銳的財經新聞分析師，語氣急躁",
        "expertise": "新聞分析,市場情緒,即時資訊",
        "data_source": "news_api",
        "model_id": "gpt-4",
        "model_temp": 0.8,
        "max_tokens": 400
    },
    "203": {
        "serial": "203",
        "nickname": "龜狗一日散戶",
        "persona": "籌碼派",
        "email": "forum_203@cmoney.com.tw",
        "password": "D8k9mN2p",
        "member_id": "9505549", 
        "status": "active",
        "owner": "威廉用",
        "notes": "籌碼面分析專家，專精資金流向和大戶動向",
        "post_times": "09:00,15:00",
        "target_audience": "籌碼面投資者",
        "interaction_threshold": 0.6,
        "common_terms": "外資持股,融資餘額,大戶持股,籌碼集中,資金流向,當沖比例,投信持股,自營商",
        "colloquial_terms": "籌碼面觀察,資金流向分析,籌碼結構,短期震盪,長期支撐,減碼跡象,進場意願",
        "tone_style": "直接務實，專注資金流向和大戶動向",
        "typing_habit": "省略號分隔句子，表達節奏感，短句居多",
        "backstory": "專精籌碼面分析的投資老手，直接務實",
        "expertise": "籌碼面分析,外資動向,融資融券",
        "data_source": "finlab_api",
        "model_id": "gpt-4",
        "model_temp": 0.6,
        "max_tokens": 500
    },
    "204": {
        "serial": "204",
        "nickname": "板橋大who",
        "persona": "情緒派",
        "email": "forum_204@cmoney.com.tw",
        "password": "D8k9mN2p",
        "member_id": "9505550",
        "status": "active",
        "owner": "威廉用",
        "notes": "情緒分析專家，專精市場情緒分析",
        "post_times": "09:00,15:00",
        "target_audience": "情緒面投資者",
        "interaction_threshold": 0.6,
        "common_terms": "恐慌貪婪指數,社群討論熱度,新聞情緒,投資人心理,市場情緒,情緒傾向,討論熱度",
        "colloquial_terms": "情緒面解讀,市場情緒,投資人心理,情緒狀態,情緒波動,情緒指標,情緒分析",
        "tone_style": "活潑開朗，善於解讀投資人心理",
        "typing_habit": "感嘆號和問號較多，語氣活潑，中等長度",
        "backstory": "專精市場情緒分析的投資老手，活潑開朗",
        "expertise": "情緒分析,社群討論,恐慌貪婪指數",
        "data_source": "sentiment_api",
        "model_id": "gpt-4",
        "model_temp": 0.7,
        "max_tokens": 450
    }
}

def init_kol_data():
    """初始化 KOL 數據到 PostgreSQL"""
    try:
        print("🔄 開始初始化 KOL 數據...")
        print(f"📊 準備初始化 {len(KOL_DATA)} 個 KOL")
        
        # 使用 psycopg2 直接連接數據庫
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # 數據庫連接
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="posting_management",
            user="postgres",
            password="password"
        )
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 檢查表是否存在
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'kol_profiles'
            );
        """)
        
        table_exists = cur.fetchone()['exists']
        
        if not table_exists:
            print("❌ kol_profiles 表不存在，請先啟動 posting-service 創建表結構")
            return False
        
        # 清空現有數據
        print("🗑️ 清空現有 KOL 數據...")
        cur.execute("DELETE FROM kol_profiles")
        conn.commit()
        print("✅ 現有 KOL 數據已清空")
        
        # 插入新的 KOL 數據
        print("➕ 插入新的 KOL 數據...")
        
        for kol_serial, kol_data in KOL_DATA.items():
            try:
                # 準備插入語句 - 只插入必要的欄位
                insert_sql = """
                    INSERT INTO kol_profiles (
                        serial, nickname, member_id, persona, status, owner, email, password, 
                        whitelist, notes, post_times, target_audience, interaction_threshold,
                        common_terms, colloquial_terms, tone_style, typing_habit, backstory,
                        expertise, data_source, model_id, model_temp, max_tokens,
                        created_time, last_updated, total_posts, published_posts, 
                        avg_interaction_rate
                    ) VALUES (
                        %(serial)s, %(nickname)s, %(member_id)s, %(persona)s, %(status)s, 
                        %(owner)s, %(email)s, %(password)s, %(whitelist)s, %(notes)s, 
                        %(post_times)s, %(target_audience)s, %(interaction_threshold)s,
                        %(common_terms)s, %(colloquial_terms)s, %(tone_style)s, %(typing_habit)s, 
                        %(backstory)s, %(expertise)s, %(data_source)s, %(model_id)s, 
                        %(model_temp)s, %(max_tokens)s, %(created_time)s, %(last_updated)s,
                        %(total_posts)s, %(published_posts)s, %(avg_interaction_rate)s
                    )
                """
                
                # 準備數據
                insert_data = {
                    **kol_data,
                    "whitelist": True,
                    "created_time": datetime.now(),
                    "last_updated": datetime.now(),
                    "total_posts": 0,
                    "published_posts": 0,
                    "avg_interaction_rate": 0.0
                }
                
                cur.execute(insert_sql, insert_data)
                print(f"✅ 成功創建 KOL: {kol_data['nickname']} (Serial: {kol_serial})")
                
            except Exception as e:
                print(f"❌ 創建 KOL {kol_data['nickname']} 失敗: {e}")
                conn.rollback()
                return False
        
        # 提交事務
        conn.commit()
        
        # 驗證數據
        print("\n🔍 驗證初始化的數據...")
        cur.execute("SELECT COUNT(*) FROM kol_profiles")
        count = cur.fetchone()['count']
        print(f"📈 數據庫中現有 {count} 個 KOL")
        
        cur.execute("SELECT serial, nickname, persona FROM kol_profiles ORDER BY serial")
        kols = cur.fetchall()
        
        for kol in kols:
            print(f"  - {kol['nickname']} ({kol['persona']}) - Serial: {kol['serial']}")
        
        cur.close()
        conn.close()
        
        print("\n🎉 KOL 數據初始化完成！")
        print("💾 數據已永久保存到 PostgreSQL volume，重啟容器不會丟失")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化 KOL 數據失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_kol_data()
    if success:
        print("\n✅ 初始化成功！現在可以安全地重啟服務了。")
    else:
        print("\n❌ 初始化失敗！請檢查錯誤信息。")
        sys.exit(1)
