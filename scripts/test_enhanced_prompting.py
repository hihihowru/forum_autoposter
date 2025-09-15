"""
測試增強版個人化 prompting 系統
使用真實 OpenAI API 生成川川哥和韭割哥的差異化內容
"""

import os
import sys
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from clients.google.sheets_client import GoogleSheetsClient
from services.kol.kol_settings_loader import KOLSettingsLoader
from services.content.content_generator import create_content_generator, ContentRequest


def test_enhanced_prompting():
    print("🧪 測試增強版個人化 prompting 系統")
    print("=" * 60)
    
    # 檢查 API Key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key.startswith('your_'):
        print("❌ 請設置有效的 OPENAI_API_KEY 環境變數")
        return False
    
    # Google Sheets client
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
    sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
    
    # Services
    loader = KOLSettingsLoader(sheets_client)
    content_generator = create_content_generator()
    
    # Test topic
    topic_title = "AI 晶片概念股技術突破與政策利多"
    topic_keywords = "技術派, 總經派, AI, 半導體, 技術突破, 政策利多, 台積電"
    
    # Test KOLs
    test_kols = [
        {'serial': '200', 'expected_style': '技術派短文、省略號風格'},
        {'serial': '201', 'expected_style': '總經派長文、數據驅動'}
    ]
    
    used_titles = set()
    results = []
    
    for kol_info in test_kols:
        serial = kol_info['serial']
        expected = kol_info['expected_style']
        
        print(f"\n🎭 測試 KOL {serial} ({expected})")
        print("-" * 40)
        
        # 取得 KOL 資料
        row = loader.get_kol_row_by_serial(serial)
        if not row:
            print(f"❌ 找不到 KOL {serial}")
            continue
            
        nickname = row.get('暱稱', f'KOL_{serial}')
        persona = row.get('人設', '')
        
        # 生成內容
        req = ContentRequest(
            topic_title=topic_title,
            topic_keywords=topic_keywords,
            kol_persona=persona,
            kol_nickname=nickname,
            content_type="investment",
            target_audience="active_traders",
            market_data={}
        )
        
        try:
            generated = content_generator.generate_complete_content(req, used_titles=list(used_titles))
            
            if generated.success:
                # 更新 used_titles
                if generated.title:
                    used_titles.add(generated.title)
                
                print(f"✅ 生成成功")
                print(f"標題: {generated.title}")
                print(f"內容長度: {len(generated.content)} 字")
                print(f"內容預覽: {generated.content[:100]}...")
                
                results.append({
                    'kol': nickname,
                    'serial': serial,
                    'title': generated.title,
                    'content': generated.content,
                    'success': True
                })
            else:
                print(f"❌ 生成失敗: {generated.error_message}")
                results.append({
                    'kol': nickname,
                    'serial': serial,
                    'success': False,
                    'error': generated.error_message
                })
                
        except Exception as e:
            print(f"❌ 生成異常: {e}")
            results.append({
                'kol': nickname,
                'serial': serial,
                'success': False,
                'error': str(e)
            })
    
    # 分析結果
    print(f"\n📊 結果分析")
    print("=" * 60)
    
    successful = [r for r in results if r.get('success', False)]
    
    if len(successful) >= 2:
        # 檢查標題差異
        titles = [r['title'] for r in successful]
        print(f"標題差異檢查:")
        for i, title in enumerate(titles):
            print(f"  {i+1}. {title}")
        
        title_similarity = len(set(titles)) == len(titles)
        print(f"標題去重: {'✅ 通過' if title_similarity else '❌ 失敗'}")
        
        # 檢查內容長度差異
        lengths = [len(r['content']) for r in successful]
        length_diff = max(lengths) - min(lengths)
        print(f"內容長度差異: {length_diff} 字 ({'✅ 有差異' if length_diff > 50 else '❌ 差異小'})")
        
        # 檢查是否包含名字
        name_check = all('【' not in r['title'] for r in successful)
        print(f"標題無名字: {'✅ 通過' if name_check else '❌ 仍有【】格式'}")
        
        return len(successful) == len(test_kols) and title_similarity and name_check
    else:
        print("❌ 生成成功數量不足，無法進行比較")
        return False


def main() -> int:
    success = test_enhanced_prompting()
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())










