"""
分析KOL角色設定
從Google Sheets讀取並分析KOL配置
"""

import sys
import os
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.google.sheets_client import GoogleSheetsClient

def analyze_kol_profiles():
    """分析KOL角色設定"""
    try:
        # 初始化Google Sheets客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        print("🎯 讀取KOL角色設定...")
        print("=" * 60)
        
        # 讀取同學會帳號管理表
        kol_data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
        
        if len(kol_data) < 2:
            print("❌ 沒有找到KOL數據")
            return
        
        headers = kol_data[0]
        rows = kol_data[1:]
        
        print(f"📊 找到 {len(rows)} 個KOL角色")
        print(f"📋 欄位數量: {len(headers)}")
        
        # 分析欄位結構
        print("\n🔍 欄位分析:")
        for i, header in enumerate(headers):
            print(f"  {i+1:2d}. {header}")
        
        # 分析KOL角色
        print("\n👥 KOL角色分析:")
        print("-" * 60)
        
        kol_profiles = []
        for i, row in enumerate(rows):
            if len(row) < 10:  # 跳過不完整的行
                continue
                
            # 提取關鍵資訊
            serial = row[0] if len(row) > 0 else ""
            nickname = row[1] if len(row) > 1 else ""
            persona = row[3] if len(row) > 3 else ""
            status = row[9] if len(row) > 9 else ""
            content_type = row[10] if len(row) > 10 else ""
            target_audience = row[12] if len(row) > 12 else ""
            common_words = row[14] if len(row) > 14 else ""
            casual_words = row[15] if len(row) > 15 else ""
            tone_style = row[16] if len(row) > 16 else ""
            typing_habit = row[17] if len(row) > 17 else ""
            background_story = row[18] if len(row) > 18 else ""
            expertise = row[19] if len(row) > 19 else ""
            
            if nickname and persona:  # 只分析有效的KOL
                profile = {
                    'serial': serial,
                    'nickname': nickname,
                    'persona': persona,
                    'status': status,
                    'content_type': content_type,
                    'target_audience': target_audience,
                    'common_words': common_words,
                    'casual_words': casual_words,
                    'tone_style': tone_style,
                    'typing_habit': typing_habit,
                    'background_story': background_story,
                    'expertise': expertise
                }
                kol_profiles.append(profile)
                
                print(f"\n📝 KOL {serial}: {nickname}")
                print(f"   人設: {persona}")
                print(f"   狀態: {status}")
                print(f"   內容類型: {content_type}")
                print(f"   目標受眾: {target_audience}")
                print(f"   常用詞彙: {common_words[:50]}...")
                print(f"   口語化用詞: {casual_words[:50]}...")
                print(f"   語氣風格: {tone_style}")
                print(f"   打字習慣: {typing_habit}")
                print(f"   前導故事: {background_story[:50]}...")
                print(f"   專長領域: {expertise}")
        
        # 分析重複性和差異化
        print("\n🔍 差異化分析:")
        print("-" * 60)
        
        # 按人設分組
        persona_groups = {}
        for profile in kol_profiles:
            persona = profile['persona']
            if persona not in persona_groups:
                persona_groups[persona] = []
            persona_groups[persona].append(profile)
        
        print("📊 人設分佈:")
        for persona, profiles in persona_groups.items():
            print(f"  {persona}: {len(profiles)} 個角色")
            for profile in profiles:
                print(f"    - {profile['nickname']} (序號: {profile['serial']})")
        
        # 檢查重複性
        print("\n⚠️  重複性檢查:")
        duplicate_personas = {k: v for k, v in persona_groups.items() if len(v) > 1}
        if duplicate_personas:
            print("發現重複人設:")
            for persona, profiles in duplicate_personas.items():
                print(f"  {persona}:")
                for profile in profiles:
                    print(f"    - {profile['nickname']} (序號: {profile['serial']})")
        else:
            print("✅ 沒有人設重複")
        
        # 分析語氣風格重複性
        tone_groups = {}
        for profile in kol_profiles:
            tone = profile['tone_style']
            if tone not in tone_groups:
                tone_groups[tone] = []
            tone_groups[tone].append(profile)
        
        print("\n📝 語氣風格分佈:")
        for tone, profiles in tone_groups.items():
            if len(profiles) > 1:
                print(f"  ⚠️  {tone}: {len(profiles)} 個角色")
                for profile in profiles:
                    print(f"    - {profile['nickname']} ({profile['persona']})")
            else:
                print(f"  ✅ {tone}: {profiles[0]['nickname']} ({profiles[0]['persona']})")
        
        return kol_profiles
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")
        return []

if __name__ == "__main__":
    profiles = analyze_kol_profiles()

























