"""
遷移腳本：為「同學會帳號管理」新增 KOL 個人化欄位

步驟：
1) 讀取現有表頭
2) 比對缺少欄位並追加到表頭末尾
3) 寫回表頭
4) 重新讀取並驗證
"""

import os
import sys
from typing import List

# 將專案根目錄與 src 加入路徑，確保可以 import src/ 內模組
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from clients.google.sheets_client import GoogleSheetsClient


SHEET_NAME = '同學會帳號管理'

# 需新增的最終精簡欄位集合（避免重複、可直接被程式讀取）
DESIRED_COLUMNS: List[str] = [
    # 標題個性化
    'TitleOpeners',
    'TitleSignaturePatterns',
    'TitleTailWord',
    'TitleBannedWords',
    'TitleStyleExamples',
    'TitleRetryMax',

    # 語氣數值化
    'ToneFormal',
    'ToneEmotion',
    'ToneConfidence',
    'ToneUrgency',
    'ToneInteraction',

    # 發文型態控制
    'QuestionRatio',
    'ContentLength',  # short/medium/long
    'InteractionStarters',

    # 資料控制
    'RequireFinlabAPI',
    'AllowHashtags',
]


def _excel_col_name(n: int) -> str:
    """1-based index to Excel column label"""
    name = ''
    while n > 0:
        n, rem = divmod(n - 1, 26)
        name = chr(65 + rem) + name
    return name


def main() -> int:
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')

    client = GoogleSheetsClient(credentials_file, spreadsheet_id)

    # 1) 讀表頭
    rows = client.read_sheet(SHEET_NAME, 'A1:ZZ1')
    header = rows[0] if rows else []

    # 2) 計算缺少欄位
    existing = set(header)
    missing = [c for c in DESIRED_COLUMNS if c not in existing]

    if not header:
        print('⚠️ 表頭為空，無法安全遷移。請先在 Google Sheets 建立既有欄位後再執行。')
        return 1

    if not missing:
        print('✅ 無需遷移，所有欄位已存在。')
        return 0

    print(f'🛠️ 需新增欄位 ({len(missing)}): {", ".join(missing)}')

    # 3) 追加並寫回表頭
    new_header = header + missing
    last_col = _excel_col_name(len(new_header))
    client.write_sheet(SHEET_NAME, [new_header], f'A1:{last_col}1')

    # 4) 驗證
    rows2 = client.read_sheet(SHEET_NAME, 'A1:ZZ1')
    header2 = rows2[0] if rows2 else []
    missing_after = [c for c in DESIRED_COLUMNS if c not in set(header2)]

    if missing_after:
        print(f'❌ 驗證失敗，仍缺少欄位: {", ".join(missing_after)}')
        return 2

    print('✅ 遷移完成並驗證成功。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


