"""
KOL 設定載入器
從 Google Sheets 的「同學會帳號管理」讀取欄位，並轉換為程式可用的設定結構
"""

import os
import logging
from typing import Dict, Any, List, Optional

from clients.google.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)


DEFAULT_SHEET_NAME = '同學會帳號管理'


class KOLSettingsLoader:
    """從 Google Sheets 載入 KOL 設定的工具類別"""

    def __init__(self, sheets_client: Optional[GoogleSheetsClient] = None):
        if sheets_client is not None:
            self.sheets_client = sheets_client
        else:
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', './credentials/google-service-account.json')
            spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
            self.sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)

    def _read_all_rows(self, sheet_name: str = DEFAULT_SHEET_NAME) -> List[List[str]]:
        values = self.sheets_client.read_sheet(sheet_name)
        return values or []

    def _read_header(self, sheet_name: str = DEFAULT_SHEET_NAME) -> List[str]:
        rows = self._read_all_rows(sheet_name)
        return rows[0] if rows else []

    def _find_row_by(self, key: str, value: str, sheet_name: str = DEFAULT_SHEET_NAME) -> Optional[Dict[str, str]]:
        rows = self._read_all_rows(sheet_name)
        if not rows:
            return None
        header = rows[0]
        # 找到 key 欄位索引
        try:
            key_index = header.index(key)
        except ValueError:
            logger.warning(f"找不到欄位: {key}")
            return None

        for r in rows[1:]:
            if key_index < len(r) and str(r[key_index]).strip() == str(value).strip():
                # 對齊長度
                r = r + [''] * (len(header) - len(r))
                return {header[i]: r[i] for i in range(len(header))}
        return None

    def get_kol_row_by_serial(self, kol_serial: str, sheet_name: str = DEFAULT_SHEET_NAME) -> Optional[Dict[str, str]]:
        return self._find_row_by('序號', str(kol_serial), sheet_name)

    def get_kol_row_by_nickname(self, nickname: str, sheet_name: str = DEFAULT_SHEET_NAME) -> Optional[Dict[str, str]]:
        return self._find_row_by('暱稱', nickname, sheet_name)

    @staticmethod
    def _split_csv(val: str) -> List[str]:
        if not val:
            return []
        parts = [p.strip() for p in val.split(',') if p.strip()]
        return parts

    @staticmethod
    def _split_style_examples(val: str) -> List[str]:
        if not val:
            return []
        # 以 | 分隔三個範例
        parts = [p.strip() for p in val.split('|') if p.strip()]
        return parts

    def build_kol_config_dict(self, row: Dict[str, str]) -> Dict[str, Any]:
        """將一列資料轉換為 ContentGenerator 可用的配置字典（覆蓋預設）"""
        if not row:
            return {}

        # 基本對應（若有）
        kol_config: Dict[str, Any] = {
            'content_type': row.get('內容類型', ''),
            'target_audience': row.get('目標受眾', ''),
            'tone_style': row.get('語氣風格', ''),
            'common_words': row.get('常用詞彙', ''),
            'casual_words': row.get('口語化用詞', ''),
            'typing_habit': row.get('常用打字習慣', ''),
            'background_story': row.get('前導故事', ''),
            'expertise': row.get('專長領域', ''),
            'ending_style': row.get('PromptCTA', '') or row.get('結尾風格', ''),
            'paragraph_spacing': row.get('ParagraphStyle', ''),
        }

        # 標題與個性化擴充欄位
        kol_config.update({
            'signature_openers': self._split_csv(row.get('TitleOpeners', '')),
            'signature_patterns': self._split_csv(row.get('TitleSignaturePatterns', '')),
            'tail_word': row.get('TitleTailWord', ''),
            'banned_generic_phrases_override': self._split_csv(row.get('TitleBannedWords', '')),
            'title_style_examples': self._split_style_examples(row.get('TitleStyleExamples', '')),
            'title_retry_max': int(row.get('TitleRetryMax', '3') or '3'),
            'question_ratio': float(row.get('QuestionRatio', '0') or '0'),
            'interaction_starters': self._split_csv(row.get('InteractionStarters', '')),
            'allow_hashtags': (row.get('AllowHashtags', '').strip().upper() == 'TRUE'),
        })

        # 內容長度
        content_length = row.get('ContentLength', '').strip().lower()
        if content_length in ('short', 'medium', 'long'):
            kol_config['content_length'] = content_length

        # Finlab 需求
        kol_config['finlab_api_needed'] = (row.get('RequireFinlabAPI', '').strip().upper() == 'TRUE')

        # Tone 數值（若提供，覆蓋）
        def _as_int(v: str, default_val: int) -> int:
            try:
                return int(v)
            except Exception:
                return default_val

        tone_map = {
            'formal_level': _as_int(row.get('ToneFormal', ''), 0),
            'emotion_intensity': _as_int(row.get('ToneEmotion', ''), 0),
            'confidence_level': _as_int(row.get('ToneConfidence', ''), 0),
            'urgency_level': _as_int(row.get('ToneUrgency', ''), 0),
            'interaction_level': _as_int(row.get('ToneInteraction', ''), 0),
        }
        # 僅在提供了任一數值時才設置 tone_vector
        if any(v > 0 for v in tone_map.values()):
            kol_config['tone_vector_override'] = tone_map

        return kol_config


