#!/usr/bin/env python3
"""
更新 KOL Profiles 的 prompt_style 欄位
給每個 KOL 獨特的寫作風格，避免模板化內容

執行方式:
    python3 update_kol_styles.py
"""

import psycopg2
import os

# 資料庫配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'autordsproxyreadwrite.cfuatt5w99vy.ap-southeast-1.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'kol_system'),
    'user': os.getenv('DB_USER', 'kol_admin'),
    'password': os.getenv('DB_PASSWORD', 'finlab2024')
}

# KOL 風格設定
KOL_STYLES = {
    '200': {
        'nickname': '川川哥',
        'style': '''我是技術派交易員，專注K線、均線、成交量分析。
說話簡潔有力，不廢話。
開頭直接點出關鍵技術訊號（例：「突破60日均線」、「量縮整理」）。
用數字說話（例：「54元支撐」、「目標60元」）。
不用「為何關注」、「專業看法」這種標題格式，直接融入段落。
每段2-3句，不超過4行。'''
    },
    '201': {
        'nickname': '阿明老師',
        'style': '''我是基本面研究員，關注財報、產業趨勢、營運數據。
寫作風格專業嚴謹但易懂，會用比喻解釋複雜概念。
開頭先講產業大環境，再聚焦個股。
善用「值得注意的是」、「從數據來看」、「關鍵在於」等轉折語。
段落之間有邏輯遞進關係（背景→分析→結論）。
每段3-5句，強調因果關係。'''
    },
    '202': {
        'nickname': '股市小白',
        'style': '''我是散戶投資人，用一般人聽得懂的話講股票。
說話輕鬆但不隨便，偶爾用日常比喻（例：「這支票像在盤整洗三溫暖」）。
開頭會問問題或提出觀察（例：「最近有沒有注意到...」、「這檔票很有趣」）。
避免太多專業術語，用「簡單說就是」、「白話來講」幫讀者理解。
會提醒風險，但不說教（例：「當然啦，投資還是要自己判斷」）。
每段2-4句，語氣親切。'''
    }
}

def update_kol_styles():
    """更新 KOL prompt_style 欄位"""
    conn = None
    try:
        # 連接資料庫
        print("🔌 連接資料庫...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 更新每個 KOL
        for serial, config in KOL_STYLES.items():
            print(f"\n📝 更新 KOL {serial} - {config['nickname']}")
            print(f"   風格長度: {len(config['style'])} 字元")

            cursor.execute("""
                UPDATE kol_profiles
                SET prompt_style = %s,
                    last_updated = NOW()
                WHERE serial = %s
            """, (config['style'], serial))

            print(f"   ✅ 更新成功")

        # 提交變更
        conn.commit()
        print("\n💾 變更已提交")

        # 查詢更新結果
        print("\n📊 查詢更新結果:")
        cursor.execute("""
            SELECT
                serial,
                nickname,
                persona,
                CASE
                    WHEN LENGTH(prompt_style) > 50
                    THEN LEFT(prompt_style, 50) || '...'
                    ELSE prompt_style
                END as style_preview,
                LENGTH(prompt_style) as style_length
            FROM kol_profiles
            WHERE serial IN ('200', '201', '202')
            ORDER BY serial
        """)

        results = cursor.fetchall()
        print("\n| Serial | Nickname | Persona     | Style Preview                              | Length |")
        print("|--------|----------|-------------|-----------------------------------------------|--------|")
        for row in results:
            serial, nickname, persona, preview, length = row
            print(f"| {serial:6} | {nickname:8} | {persona:11} | {preview:45} | {length:6} |")

        print("\n✅ 所有 KOL 風格設定已更新完成！")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        if conn:
            conn.rollback()
            print("🔙 變更已回滾")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("\n🔌 資料庫連接已關閉")

if __name__ == "__main__":
    print("=" * 80)
    print("🎨 KOL Prompt Style 更新工具")
    print("=" * 80)
    update_kol_styles()
