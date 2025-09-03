"""
驗證腳本：讀取 Google Sheets 的 KOL 設定並列印關鍵欄位
用於確認遷移後欄位是否能正確被載入
"""

import os
import sys
from pprint import pprint

# 將專案根目錄與 src 加入路徑
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from services.kol.kol_settings_loader import KOLSettingsLoader


def main() -> int:
    loader = KOLSettingsLoader()

    # 可調整要驗證的序號
    target_serials = os.getenv('VERIFY_KOL_SERIALS', '200,201,202').split(',')
    target_serials = [s.strip() for s in target_serials if s.strip()]

    for serial in target_serials:
        print(f"\n=== 檢查 KOL 序號 {serial} ===")
        row = loader.get_kol_row_by_serial(serial)
        if not row:
            print("找不到該 KOL 的資料列")
            continue

        config = loader.build_kol_config_dict(row)
        keys_to_show = [
            'content_type', 'target_audience', 'tone_style', 'common_words', 'casual_words',
            'typing_habit', 'background_story', 'expertise', 'ending_style', 'paragraph_spacing',
            'signature_openers', 'signature_patterns', 'tail_word',
            'banned_generic_phrases_override', 'title_style_examples', 'title_retry_max',
            'question_ratio', 'interaction_starters', 'allow_hashtags', 'content_length',
            'finlab_api_needed', 'tone_vector_override'
        ]
        summary = {k: config.get(k) for k in keys_to_show}
        pprint(summary)

    print("\n驗證完成")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


