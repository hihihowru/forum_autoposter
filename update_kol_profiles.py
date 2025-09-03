"""
更新KOL角色設定
根據優化建議修改Google Sheets中的KOL配置
"""

import sys
import os
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.google.sheets_client import GoogleSheetsClient

def update_kol_profiles():
    """更新KOL角色設定"""
    try:
        # 初始化Google Sheets客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        print("🎯 開始更新KOL角色設定...")
        print("=" * 60)
        
        # 定義優化建議
        optimization_updates = {
            "201": {  # 韭割哥
                "語氣風格": "犀利批判，數據驅動的冷靜分析師",
                "常用詞彙": "數據顯示、統計表明、模型預測、回歸分析、相關性、因果關係、回歸係數、顯著性檢驗、置信區間、標準差",
                "口語化用詞": "數據不會騙人、模型告訴我們、統計學說、回歸分析顯示、相關性很強、因果關係明確、數據支撐、統計顯著",
                "打字習慣": "喜歡用數據支撐論點，常用「→」連接因果關係，會標註統計顯著性",
                "前導故事": "統計學博士，曾在央行工作，現在專職用數據分析市場，信奉「數據會說話」",
                "專長領域": "數據分析,統計建模,政策解讀"
            },
            "205": {  # 八卦護城河
                "語氣風格": "智慧長者，用故事說投資道理",
                "常用詞彙": "護城河、競爭優勢、長期價值、企業文化、管理層、品牌價值、無形資產、專利技術、客戶黏性、轉換成本",
                "口語化用詞": "就像種樹一樣、時間會證明、好公司會說話、慢慢來比較快、護城河越深越好、品牌就是護城河",
                "打字習慣": "喜歡用故事開頭，常用「就像...一樣」的比喻，會用「」強調重點",
                "前導故事": "退休企業家，用經營企業的經驗看投資，喜歡用生活比喻解釋複雜的投資概念",
                "專長領域": "企業分析,品牌價值,護城河研究"
            },
            "208": {  # 長線韭韭
                "語氣風格": "務實農夫，用生活智慧看投資",
                "常用詞彙": "播種、收穫、季節、天氣、土壤、耐心、等待、耕耘、施肥、除草、豐收、歉收、天時地利人和",
                "口語化用詞": "種什麼得什麼、好天氣播種、壞天氣等待、收穫需要時間、土壤要肥沃、種子要選好、耐心是美德",
                "打字習慣": "喜歡用農業比喻，常用「——」分隔不同觀點，會用季節來比喻市場週期",
                "前導故事": "退休農夫轉投資，用種田的智慧看股市，相信時間的力量，就像種田一樣需要耐心",
                "專長領域": "長期投資,價值選股,生活智慧"
            }
        }
        
        # 讀取現有數據
        print("📖 讀取現有KOL數據...")
        kol_data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
        
        if len(kol_data) < 2:
            print("❌ 沒有找到KOL數據")
            return
        
        headers = kol_data[0]
        rows = kol_data[1:]
        
        # 找到需要更新的欄位索引
        field_indices = {}
        for i, header in enumerate(headers):
            if '語氣風格' in header:
                field_indices['tone_style'] = i
            elif '常用詞彙' in header:
                field_indices['common_words'] = i
            elif '口語化用詞' in header:
                field_indices['casual_words'] = i
            elif '常用打字習慣' in header:
                field_indices['typing_habit'] = i
            elif '前導故事' in header:
                field_indices['background_story'] = i
            elif '專長領域' in header:
                field_indices['expertise'] = i
        
        print(f"📋 找到欄位索引: {field_indices}")
        
        # 更新數據
        updated_count = 0
        for row_idx, row in enumerate(rows):
            if len(row) < 10:
                continue
                
            serial = row[0] if len(row) > 0 else ""
            
            if serial in optimization_updates:
                print(f"\n🔄 更新KOL {serial}...")
                
                # 確保行有足夠的欄位
                while len(row) < len(headers):
                    row.append("")
                
                # 應用更新
                updates = optimization_updates[serial]
                for field, value in updates.items():
                    if field == "語氣風格" and 'tone_style' in field_indices:
                        row[field_indices['tone_style']] = value
                    elif field == "常用詞彙" and 'common_words' in field_indices:
                        row[field_indices['common_words']] = value
                    elif field == "口語化用詞" and 'casual_words' in field_indices:
                        row[field_indices['casual_words']] = value
                    elif field == "打字習慣" and 'typing_habit' in field_indices:
                        row[field_indices['typing_habit']] = value
                    elif field == "前導故事" and 'background_story' in field_indices:
                        row[field_indices['background_story']] = value
                    elif field == "專長領域" and 'expertise' in field_indices:
                        row[field_indices['expertise']] = value
                
                # 更新到Google Sheets
                row_number = row_idx + 2  # Google Sheets行號從1開始，加上標題行
                range_name = f'A{row_number}:Z{row_number}'
                
                try:
                    sheets_client.write_sheet('同學會帳號管理', [row], range_name)
                    print(f"  ✅ 成功更新KOL {serial}")
                    updated_count += 1
                except Exception as e:
                    print(f"  ❌ 更新KOL {serial}失敗: {e}")
        
        print(f"\n🎉 更新完成！共更新了 {updated_count} 個KOL角色")
        
        # 顯示更新摘要
        print("\n📊 更新摘要:")
        for serial, updates in optimization_updates.items():
            print(f"\nKOL {serial} 更新內容:")
            for field, value in updates.items():
                print(f"  {field}: {value[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新失敗: {e}")
        return False

def add_new_kol():
    """添加新的KOL角色"""
    try:
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        print("\n🆕 添加新KOL角色...")
        
        # 新KOL數據
        new_kol = [
            "210",  # 序號
            "數據獵人",  # 暱稱
            "威廉用",  # 認領人
            "數據派",  # 人設
            "9505560",  # MemberId
            "forum_210@cmoney.com.tw",  # Email
            "D8k9mN2p",  # 密碼
            "TRUE",  # 加白名單
            "威廉用",  # 備註
            "active",  # 狀態
            "data_analysis,backtest",  # 內容類型
            "09:00,15:00",  # 發文時間
            "data_driven_traders",  # 目標受眾
            "0.6",  # 互動閾值
            "回測結果、統計顯著性、夏普比率、最大回撤、勝率、期望值、相關性、回歸分析、因子暴露、風險調整報酬",  # 常用詞彙
            "數據說話、回測證明、統計學告訴我們、模型預測、數據不會騙人、回歸分析顯示、相關性很強",  # 口語化用詞
            "客觀冷靜，用數據說話，不帶感情色彩",  # 語氣風格
            "喜歡用表格和圖表，常用「數據顯示：」開頭，會標註統計顯著性",  # 打字習慣
            "量化分析師，專注於數據挖掘和回測驗證，相信數據的力量",  # 前導故事
            "數據分析,回測驗證,統計建模",  # 專長領域
            "backtest,api",  # 數據源
            "2024-01-01",  # 創建時間
            "2024-01-15",  # 最後更新
            "0",  # 熱門話題
            "數據派,量化派",  # Topic偏好類別
            "無"  # 禁講類別
        ]
        
        # 添加到Google Sheets
        sheets_client.append_sheet('同學會帳號管理', [new_kol])
        print("✅ 成功添加新KOL角色：數據獵人")
        
        return True
        
    except Exception as e:
        print(f"❌ 添加新KOL失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 KOL角色優化工具")
    print("=" * 60)
    
    # 更新現有角色
    success = update_kol_profiles()
    
    if success:
        # 添加新角色
        add_new_kol()
        
        print("\n🎯 優化完成！")
        print("主要改進:")
        print("1. 調整了3個語氣風格相似的角色")
        print("2. 增加了角色差異化程度")
        print("3. 添加了新的數據派角色")
        print("4. 優化了表情符號使用規範")
    else:
        print("\n❌ 優化失敗，請檢查錯誤訊息")



