"""
隨機化內容生成器
生成多個版本的內容並隨機選擇一個，避免模板化
"""

import random
import json
import os
import openai
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RandomContentGenerator:
    """隨機化內容生成器"""
    
    def __init__(self):
        self.logger = logger
        # 🔥 FIX: Strip whitespace and newlines from API key (Railway env var issue)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.api_key = self.api_key.strip()
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

        if self.api_key:
            openai.api_key = self.api_key
            self.logger.info(f"🎯 RandomContentGenerator 初始化完成，使用模型: {self.model}")
        else:
            self.logger.warning("⚠️ OPENAI_API_KEY 未設定，將使用模擬數據")
        
    def generate_randomized_content(
        self,
        original_title: str,
        original_content: str,
        kol_profile: Any,
        posting_type: str = 'analysis',
        stock_name: str = '',
        stock_code: str = '',
        trigger_type: str = None,
        serper_data: Dict = None
    ) -> Dict[str, Any]:
        """
        生成隨機化內容
        
        Args:
            original_title: 原始標題
            original_content: 原始內容
            kol_profile: KOL 配置
            posting_type: 發文類型 ('analysis' 或 'interaction')
            stock_name: 股票名稱
            stock_code: 股票代碼
            serper_data: 新聞數據
            
        Returns:
            包含選中版本和其他版本的字典
        """
        
        self.logger.info(f"🎲 開始隨機化內容生成 - 類型: {posting_type}")
        self.logger.info(f"📊 KOL: {getattr(kol_profile, 'nickname', 'Unknown')} ({getattr(kol_profile, 'serial', 'Unknown')})")
        self.logger.info(f"📈 股票: {stock_name}({stock_code})")
        
        # 生成5個版本
        versions = self._generate_five_versions(
            original_title, original_content, kol_profile, 
            posting_type, stock_name, stock_code, trigger_type, serper_data
        )
        
        # 隨機選擇一個版本 - 使用更好的隨機性
        import time
        # 使用當前時間作為隨機種子的一部分，增加隨機性
        random.seed(int(time.time() * 1000) % 1000000)
        selected_version = random.choice(versions)
        selected_index = versions.index(selected_version)
        
        # 其他4個版本
        alternative_versions = [v for i, v in enumerate(versions) if i != selected_index]
        
        # 記錄日誌
        self._log_generation_results(versions, selected_version, selected_index)
        
        return {
            'selected_version': selected_version,
            'alternative_versions': alternative_versions,
            'generation_metadata': {
                'total_versions': len(versions),
                'selected_index': selected_index,
                'posting_type': posting_type,
                'generated_at': datetime.now().isoformat(),
                'kol_serial': getattr(kol_profile, 'serial', 'Unknown'),
                'stock_code': stock_code
            }
        }
    
    def _generate_five_versions(
        self,
        original_title: str,
        original_content: str,
        kol_profile: Any,
        posting_type: str,
        stock_name: str,
        stock_code: str,
        trigger_type: str = None,
        serper_data: Dict = None
    ) -> List[Dict[str, str]]:
        """生成5個不同版本的內容"""
        
        versions = []
        
        # 獲取 KOL 特色
        kol_nickname = getattr(kol_profile, 'nickname', '分析師')
        kol_persona = getattr(kol_profile, 'persona', '專業')
        tone_style = getattr(kol_profile, 'tone_style', '專業分析')
        common_terms = getattr(kol_profile, 'common_terms', '')
        colloquial_terms = getattr(kol_profile, 'colloquial_terms', '')
        
        self.logger.info(f"🎯 KOL 特色 - 暱稱: {kol_nickname}, 人設: {kol_persona}, 風格: {tone_style}")
        
        for i in range(5):
            version_num = i + 1
            self.logger.info(f"🔄 生成版本 {version_num}/5...")
            
            if posting_type == 'interaction':
                version = self._generate_interaction_version(
                    version_num, kol_nickname, kol_persona, tone_style,
                    common_terms, colloquial_terms, stock_name, stock_code,
                    original_content, serper_data
                )
            else:
                version = self._generate_analysis_version(
                    version_num, kol_nickname, kol_persona, tone_style,
                    common_terms, colloquial_terms, stock_name, stock_code,
                    original_content, trigger_type, serper_data
                )
            
            versions.append(version)
            self.logger.info(f"✅ 版本 {version_num} 生成完成: {version['title'][:50]}...")
        
        return versions
    
    def _generate_analysis_version(
        self,
        version_num: int,
        kol_nickname: str,
        kol_persona: str,
        tone_style: str,
        common_terms: str,
        colloquial_terms: str,
        stock_name: str,
        stock_code: str,
        original_content: str,
        trigger_type: str = None,
        serper_data: Dict = None
    ) -> Dict[str, str]:
        """生成分析發表版本"""
        
        # 不同的分析角度
        analysis_angles = [
            "技術面分析",
            "基本面觀察", 
            "市場情緒解讀",
            "操作策略建議",
            "風險評估提醒"
        ]
        
        angle = analysis_angles[version_num - 1]
        
        # 根據觸發器類型調整提示
        trigger_context = ""
        if trigger_type and trigger_type != "manual":
            if "limit_down" in trigger_type or "跌停" in trigger_type:
                trigger_context = f"注意：{stock_name} 目前處於跌停狀態，請分析跌停原因、風險因素，不要說'值得關注的投資機會'。"
            elif "limit_up" in trigger_type or "漲停" in trigger_type:
                trigger_context = f"注意：{stock_name} 目前處於漲停狀態，請分析漲停原因、後續走勢。"
            elif "volume" in trigger_type:
                trigger_context = f"注意：{stock_name} 出現異常成交量，請重點分析量價關係。"
            elif trigger_type == "manual":
                # 手動發文時，使用通用分析提示
                trigger_context = f"注意：這是手動發文，請根據{stock_name}的當前市場情況進行客觀分析。"
        
        # 構建 Prompt
        prompt = f"""
你是 {kol_nickname}，人設是 {kol_persona}，寫作風格是 {tone_style}。

請針對 {stock_name}({stock_code}) 生成一個分析發表內容，重點是 {angle}。

{trigger_context}

要求：
1. 標題要吸引人，體現你的個人特色
2. 內容要專業但易懂，符合你的風格
3. 避免模板化，要有個人觀點
4. 長度控制在 150-200 字
5. 使用你的常用術語：{common_terms}
6. 可以適當使用口語化表達：{colloquial_terms}
7. 根據股票實際情況調整語調和建議

原始內容參考：
{original_content[:200]}...

請生成標題和內容，格式：
標題：[你的標題]
內容：[你的分析內容]
"""
        
        # 這裡應該調用 LLM API，暫時使用模擬數據
        title, content = self._call_llm_api(prompt, f"analysis_v{version_num}", stock_name, stock_code)

        return {
            'title': title,
            'content': content,
            'version_type': 'analysis',
            'angle': angle,
            'version_number': version_num
        }
    
    def _generate_interaction_version(
        self,
        version_num: int,
        kol_nickname: str,
        kol_persona: str,
        tone_style: str,
        common_terms: str,
        colloquial_terms: str,
        stock_name: str,
        stock_code: str,
        original_content: str,
        serper_data: Dict = None
    ) -> Dict[str, str]:
        """生成互動提問版本"""
        
        # 不同的互動角度
        interaction_angles = [
            "技術指標討論",
            "操作時機詢問",
            "風險控制探討",
            "市場看法交流",
            "投資策略分享"
        ]
        
        angle = interaction_angles[version_num - 1]
        
        # 構建 Prompt
        prompt = f"""
你是 {kol_nickname}，人設是 {kol_persona}，寫作風格是 {tone_style}。

請針對 {stock_name}({stock_code}) 生成一個互動提問內容，重點是 {angle}。

要求：
1. 標題要引發討論，體現你的個人特色
2. 內容要以問題形式，鼓勵讀者互動
3. 避免模板化，要有個人觀點
4. 長度控制在 100-150 字
5. 使用你的常用術語：{common_terms}
6. 可以適當使用口語化表達：{colloquial_terms}

原始內容參考：
{original_content[:200]}...

請生成標題和內容，格式：
標題：[你的標題]
內容：[你的互動提問內容]
"""
        
        # 這裡應該調用 LLM API，暫時使用模擬數據
        title, content = self._call_llm_api(prompt, f"interaction_v{version_num}", stock_name, stock_code)

        return {
            'title': title,
            'content': content,
            'version_type': 'interaction',
            'angle': angle,
            'version_number': version_num
        }

    def _call_llm_api(self, prompt: str, version_id: str, stock_name: str = '', stock_code: str = '') -> tuple[str, str]:
        """調用 LLM API 生成內容"""

        self.logger.info(f"🤖 調用 LLM API 生成 {version_id}...")

        if not self.api_key:
            self.logger.warning("⚠️ 無 API Key，使用模擬數據")
            return self._generate_mock_content(version_id, stock_name, stock_code)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一個專業的金融內容生成助手，能夠根據KOL特色和股票實際情況生成自然、多樣化的內容。請注意：如果股票是跌停，不要說'值得關注的投資機會'，而要分析跌停原因和風險。"},
                    {"role": "user", "content": prompt}
                ],
                "max_completion_tokens": 1000,
                "temperature": 1.0  # GPT-5 只支援預設值 1
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API 錯誤: {response.status_code} - {response.text}")
            
            response_data = response.json()
            generated_content = response_data["choices"][0]["message"]["content"].strip()
            
            # 嘗試從內容中提取標題和內容
            lines = generated_content.split('\n')
            title = ""
            content = ""
            
            for i, line in enumerate(lines):
                if line.strip().startswith('標題：') or line.strip().startswith('標題:'):
                    title = line.replace('標題：', '').replace('標題:', '').strip()
                    # 查找內容行
                    for j in range(i+1, len(lines)):
                        if lines[j].strip().startswith('內容：') or lines[j].strip().startswith('內容:'):
                            # 提取內容，去掉 "內容：" 前綴
                            content_lines = lines[j].replace('內容：', '').replace('內容:', '').strip()
                            # 如果還有後續行，也加入內容
                            if j+1 < len(lines):
                                content_lines += '\n' + '\n'.join(lines[j+1:]).strip()
                            content = content_lines
                            break
                    else:
                        # 如果沒有找到 "內容：" 行，使用剩餘所有行
                        content = '\n'.join(lines[i+1:]).strip()
                    break
                elif i == 0 and len(line.strip()) < 50:  # 第一行可能是標題
                    title = line.strip()
                    content = '\n'.join(lines[1:]).strip()
                    break
            
            if not title:
                title = f"版本 {version_id} - 投資分析"
            if not content:
                content = generated_content
                
            self.logger.info(f"✅ LLM 生成成功: 標題='{title[:30]}...', 內容長度={len(content)}")
            return title, content
            
        except Exception as e:
            self.logger.error(f"❌ LLM API 調用失敗: {e}")
            return self._generate_mock_content(version_id, stock_name, stock_code)

    def _generate_mock_content(self, version_id: str, stock_name: str = '', stock_code: str = '') -> tuple[str, str]:
        """生成模擬內容（備用方案）- 🔥 FIX: Now includes stock name and code"""
        self.logger.warning(f"⚠️ 使用備用模板生成內容: {stock_name}({stock_code})")

        # 🔥 FIX: Include stock name and code in fallback templates
        stock_display = f"{stock_name}({stock_code})" if stock_name and stock_code else "目標標的"

        if "analysis" in version_id:
            title = f"{stock_display} - {random.choice(['深度解析', '專業觀點', '市場觀察', '技術分析', '投資建議'])}"
            content = f"【{stock_display} 分析】\n\n作為專業分析師，我對{stock_name if stock_name else '這檔個股'}有以下觀察：\n\n1. 技術面顯示值得關注的訊號\n2. 基本面需持續追蹤\n3. 市場情緒反映投資人態度\n\n建議投資人密切關注後續發展，適時調整策略。\n\n#{stock_name if stock_name else '投資分析'} #市場觀察"
        else:
            title = f"{stock_display} - {random.choice(['大家怎麼看', '想聽聽意見', '討論一下', '分享觀點', '交流想法'])}"
            content = f"【{stock_display} 討論】\n\n最近{stock_name if stock_name else '這檔個股'}的走勢，想和大家討論一下：\n\n• 你覺得現在的時機如何？\n• 有什麼操作策略可以分享？\n• 風險控制方面有什麼建議？\n\n歡迎留言分享你的看法！\n\n#{stock_name if stock_name else '投資討論'} #策略分享"

        return title, content
    
    def _log_generation_results(
        self, 
        versions: List[Dict], 
        selected_version: Dict, 
        selected_index: int
    ):
        """記錄生成結果"""
        
        self.logger.info("=" * 80)
        self.logger.info("🎲 隨機化內容生成結果")
        self.logger.info("=" * 80)
        
        for i, version in enumerate(versions):
            status = "🎯 選中" if i == selected_index else "📝 備選"
            self.logger.info(f"{status} 版本 {i+1}:")
            self.logger.info(f"   標題: {version['title']}")
            self.logger.info(f"   內容: {version['content']}")
            self.logger.info(f"   類型: {version['version_type']}")
            self.logger.info(f"   角度: {version['angle']}")
            self.logger.info("-" * 40)
        
        self.logger.info(f"🎲 隨機選擇結果: 版本 {selected_index + 1}")
        self.logger.info(f"📊 其他 {len(versions) - 1} 個版本已存儲到 alternative_versions")
        self.logger.info("=" * 80)
