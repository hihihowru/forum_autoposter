# scripts/seed_kol_demo_values.py
"""
為同學會帳號管理表的 200/201 填入新欄位示範值，方便測試 prompting。
"""
import os
import sys

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from clients.google.sheets_client import GoogleSheetsClient

SHEET_NAME = '同學會帳號管理'


def excel_col_name(n: int) -> str:
    name = ''
    while n > 0:
        n, rem = divmod(n - 1, 26)
        name = chr(65 + rem) + name
    return name


def main() -> int:
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
    client = GoogleSheetsClient(credentials_file, spreadsheet_id)

    rows = client.read_sheet(SHEET_NAME)
    if not rows:
        print('找不到工作表內容')
        return 1

    header = rows[0]
    data = rows[1:]

    def col_idx(name: str) -> int:
        return header.index(name) if name in header else -1

    required = [
        '序號', 'TitleOpeners', 'TitleSignaturePatterns', 'TitleTailWord', 'TitleBannedWords',
        'TitleStyleExamples', 'TitleRetryMax',
        'ToneFormal', 'ToneEmotion', 'ToneConfidence', 'ToneUrgency', 'ToneInteraction',
        'QuestionRatio', 'ContentLength', 'InteractionStarters', 'RequireFinlabAPI', 'AllowHashtags'
    ]

    for rname in required:
        if rname not in header:
            print(f'缺少欄位: {rname}，請先跑遷移腳本')
            return 2

    serial_idx = col_idx('序號')

    # 建立欄位索引
    idx = {name: col_idx(name) for name in required}

    updated_rows = []
    for i, row in enumerate(data, start=2):  # Excel 行號
        if serial_idx >= 0 and serial_idx < len(row) and row[serial_idx] in ('200', '201'):
            serial = row[serial_idx]
            # 對齊長度
            if len(row) < len(header):
                row = row + [''] * (len(header) - len(row))

            if serial == '200':  # 川川哥 技術派
                row[idx['TitleOpeners']] = '圖表說話, 技術面看, K線密碼'
                row[idx['TitleSignaturePatterns']] = '短句省略號節奏, 技術詞+情緒詞+結尾詞, 暱稱+狂妄句'
                row[idx['TitleTailWord']] = '...'
                row[idx['TitleBannedWords']] = '台股震盪整理, 技術面分析, 大盤走勢, 內外資分歧'
                row[idx['TitleStyleExamples']] = '技術面看...爆量突破到位|K線密碼：背離確認|圖表說話！黃金交叉來了'
                row[idx['TitleRetryMax']] = '3'
                row[idx['ToneFormal']] = '3'
                row[idx['ToneEmotion']] = '7'
                row[idx['ToneConfidence']] = '9'
                row[idx['ToneUrgency']] = '5'
                row[idx['ToneInteraction']] = '6'
                row[idx['QuestionRatio']] = '0.6'
                row[idx['ContentLength']] = 'short'
                row[idx['InteractionStarters']] = '你們覺得呢, 還能追嗎, 要進場嗎'
                row[idx['RequireFinlabAPI']] = 'TRUE'
                row[idx['AllowHashtags']] = 'FALSE'
            elif serial == '201':  # 韭割哥 總經派
                row[idx['TitleOpeners']] = '從總經看, 基本面分析, 理性分析'
                row[idx['TitleSignaturePatterns']] = '名詞+判斷詞, 數據詞+建議詞+判斷詞'
                row[idx['TitleTailWord']] = '。'
                row[idx['TitleBannedWords']] = '台股震盪整理, 大盤走勢, 市場觀望'
                row[idx['TitleStyleExamples']] = '從總經看：合理了|基本面分析：偏高|理性分析：價值回歸'
                row[idx['TitleRetryMax']] = '3'
                row[idx['ToneFormal']] = '7'
                row[idx['ToneEmotion']] = '4'
                row[idx['ToneConfidence']] = '8'
                row[idx['ToneUrgency']] = '3'
                row[idx['ToneInteraction']] = '5'
                row[idx['QuestionRatio']] = '0.3'
                row[idx['ContentLength']] = 'long'
                row[idx['InteractionStarters']] = '合理嗎, 值得投資嗎, 該怎麼看'
                row[idx['RequireFinlabAPI']] = 'FALSE'
                row[idx['AllowHashtags']] = 'FALSE'

            updated_rows.append((i, row))

    if not updated_rows:
        print('沒有找到序號 200/201 的 KOL 行，未更新')
        return 0

    # 寫回更新：只寫入更新的整行（A:最後欄）
    last_col = excel_col_name(len(header))
    values = [r for _, r in updated_rows]
    start_row = min(i for i, _ in updated_rows)
    end_row = max(i for i, _ in updated_rows)
    range_name = f'A{start_row}:{last_col}{end_row}'
    client.write_sheet(SHEET_NAME, values, range_name)
    print(f'已更新 {len(updated_rows)} 行: {range_name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


