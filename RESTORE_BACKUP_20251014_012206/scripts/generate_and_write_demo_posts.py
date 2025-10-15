"""
生成示範貼文：
1) 指定單一 demo 話題
2) 指派給 KOL 200/201
3) 使用新的個人化設定生成標題與內容
4) 寫入「貼文記錄表」
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


POST_SHEET = '貼文記錄表'


def main() -> int:
    # Google Sheets client
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
    sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)

    # Services
    loader = KOLSettingsLoader(sheets_client)
    content_generator = create_content_generator()

    # Demo topic
    now_id = datetime.now().strftime('%Y%m%d%H%M%S')
    topic_id = f"demo-{now_id}"
    topic_title = "台股AI伺服器鏈技術與總經雙視角"
    persona_tags = ["技術派", "總經派"]
    industry_tags = ["半導體", "AI"]
    event_tags = ["技術分析", "政策", "景氣"]
    stock_tags = ["台積電"]
    keywords_joined = ", ".join(persona_tags + industry_tags + event_tags + stock_tags)

    # 目標 KOL
    targets = [200, 201]
    used_titles = set()
    post_records = []
    # 動態讀取表頭
    header_rows = sheets_client.read_sheet(POST_SHEET, 'A1:ZZ1')
    headers = header_rows[0] if header_rows else []

    for serial in targets:
        # 取得 KOL 基本資料
        row = loader.get_kol_row_by_serial(str(serial))
        if not row:
            print(f"⚠️ 找不到 KOL {serial} 的資料列")
            continue
        nickname = row.get('暱稱', f'KOL_{serial}')
        persona = row.get('人設', '')
        member_id = row.get('MemberId', '')

        # 生成內容
        req = ContentRequest(
            topic_title=topic_title,
            topic_keywords=keywords_joined,
            kol_persona=persona,
            kol_nickname=nickname,
            content_type="investment",
            target_audience="active_traders",
            market_data={}
        )
        generated = content_generator.generate_complete_content(req, used_titles=list(used_titles))
        if not generated.success:
            print(f"❌ 內容生成失敗 ({serial}): {generated.error_message}")
            continue

        # 更新 used_titles
        if generated.title:
            used_titles.add(generated.title)

        # 準備寫入記錄（依表頭對齊）
        post_id = f"{topic_id}-{serial}"
        row = [''] * len(headers)
        def set_if_exists(col_name: str, value):
            if col_name in headers:
                row[headers.index(col_name)] = value
        set_if_exists('貼文ID', post_id)
        set_if_exists('KOL Serial', str(serial))
        set_if_exists('KOL 暱稱', nickname)
        set_if_exists('KOL ID', member_id)
        set_if_exists('Persona', persona)
        set_if_exists('Content Type', 'investment')
        set_if_exists('已派發TopicIndex', 1)
        set_if_exists('已派發TopicID', topic_id)
        # 部分表可能沒有 已派發TopicTitle 欄位，避免強灌
        set_if_exists('已派發TopicKeywords', keywords_joined)
        set_if_exists('生成內容', generated.content)
        set_if_exists('發文狀態', 'ready_to_post')
        set_if_exists('上次排程時間', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        set_if_exists('發文時間戳記', '')
        set_if_exists('最近錯誤訊息', '')
        set_if_exists('平台發文ID', '')
        set_if_exists('平台發文URL', '')
        set_if_exists('熱門話題標題', topic_title)
        post_records.append(row)
        print(f"✅ 生成完成 {post_id}: {generated.title}")

    if not post_records:
        print("沒有可寫入的記錄")
        return 0

    # 追加到貼文記錄表（欄位對齊）
    sheets_client.append_sheet(POST_SHEET, post_records)
    print(f"已寫入 {len(post_records)} 筆到 {POST_SHEET}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


