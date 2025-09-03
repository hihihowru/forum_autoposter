"""
AI偵測服務
專門分析留言和內容，偵測是否被識別為AI生成
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class AIDetectionResult:
    """AI偵測結果"""
    content_id: str
    detection_score: float  # 0-1，越高表示越可能被識別為AI
    detection_signals: List[str]
    confidence: float
    risk_level: str  # 'low', 'medium', 'high'
    recommendations: List[str]
    analyzed_at: datetime

@dataclass
class CommentAnalysis:
    """留言分析結果"""
    comment_id: str
    content: str
    ai_detection_score: float
    sentiment_score: float
    quality_score: float
    suspicious_patterns: List[str]
    analyzed_at: datetime

class AIDetectionService:
    """AI偵測服務"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # AI偵測模式庫
        self.ai_patterns = {
            'language_patterns': [
                r'根據.*分析',
                r'基於.*數據',
                r'綜合.*來看',
                r'總結.*來說',
                r'首先.*其次.*最後',
                r'總而言之',
                r'綜上所述',
                r'從.*角度.*來看',
                r'考慮到.*因素',
                r'在.*情況下'
            ],
            'structure_patterns': [
                r'^##.*$',  # 過多標題
                r'^\d+\.\s',  # 過多編號列表
                r'^[•·▪▫]\s',  # 過多項目符號
                r'^###.*$',  # 過多子標題
            ],
            'emotion_patterns': [
                r'我認為.*是.*的',
                r'從.*角度.*分析',
                r'數據顯示.*',
                r'統計表明.*',
                r'研究指出.*',
                r'分析結果.*',
                r'根據.*研究.*',
                r'基於.*統計.*'
            ],
            'ai_keywords': [
                '人工智慧', 'AI', '機器人', 'bot', '自動生成',
                'chatgpt', 'gpt', 'claude', 'bard', 'copilot',
                '看起來像ai', '感覺是ai', 'ai生成', '機器寫的',
                '程式生成', '自動化', '演算法', '模型'
            ]
        }
        
        # 人類特徵模式庫
        self.human_patterns = {
            'personal_indicators': [
                '我覺得', '我認為', '我的看法', '個人覺得',
                '我個人', '我自己', '我這邊', '我這裡',
                '我朋友', '我同事', '我家人', '我同學',
                '我昨天', '我剛才', '我剛剛', '我現在',
                '我記得', '我想起', '我想到', '我發現'
            ],
            'casual_expressions': [
                '哈哈', '呵呵', '嘿嘿', '嘻嘻',
                '靠', '幹', '靠北', '靠腰',
                '真的假的', '真假', '真的嗎',
                '太扯了', '太誇張', '太猛了',
                '笑死', '笑爛', '笑爆', '笑翻',
                'GG', 'gg', 'GG了', 'gg了'
            ],
            'typing_habits': [
                '...', '。。。', '...', '...',
                '!!!', '！！！', '!!!', '!!!',
                '???', '？？？', '???', '???',
                '==', '= =', '==', '==',
                'XD', 'xd', 'XD', 'xd',
                'Orz', 'orz', 'Orz', 'orz'
            ],
            'incomplete_thoughts': [
                r'然後.*就.*',
                r'結果.*就.*',
                r'後來.*就.*',
                r'然後.*',
                r'結果.*',
                r'後來.*',
                r'不過.*',
                r'但是.*',
                r'可是.*',
                r'只是.*'
            ]
        }
    
    async def detect_ai_content(self, content: str, content_id: str = None) -> AIDetectionResult:
        """
        偵測內容是否為AI生成
        
        Args:
            content: 要分析的內容
            content_id: 內容ID
            
        Returns:
            AI偵測結果
        """
        try:
            detection_signals = []
            ai_score = 0.0
            
            # 1. 語言模式分析
            language_score, language_signals = self._analyze_language_patterns(content)
            ai_score += language_score * 0.3
            detection_signals.extend(language_signals)
            
            # 2. 結構模式分析
            structure_score, structure_signals = self._analyze_structure_patterns(content)
            ai_score += structure_score * 0.2
            detection_signals.extend(structure_signals)
            
            # 3. 情感表達分析
            emotion_score, emotion_signals = self._analyze_emotion_patterns(content)
            ai_score += emotion_score * 0.2
            detection_signals.extend(emotion_signals)
            
            # 4. 人類特徵分析
            human_score, human_signals = self._analyze_human_patterns(content)
            ai_score -= human_score * 0.3  # 人類特徵會降低AI分數
            
            # 5. 關鍵詞分析
            keyword_score, keyword_signals = self._analyze_ai_keywords(content)
            ai_score += keyword_score * 0.2
            detection_signals.extend(keyword_signals)
            
            # 6. 使用OpenAI進行深度分析
            openai_score, openai_signals = await self._analyze_with_openai(content)
            ai_score += openai_score * 0.1
            detection_signals.extend(openai_signals)
            
            # 確保分數在0-1之間
            ai_score = max(0, min(1, ai_score))
            
            # 計算風險等級
            risk_level = self._calculate_risk_level(ai_score)
            
            # 生成建議
            recommendations = self._generate_recommendations(ai_score, detection_signals)
            
            return AIDetectionResult(
                content_id=content_id or f"content_{datetime.now().timestamp()}",
                detection_score=ai_score,
                detection_signals=detection_signals,
                confidence=0.8,  # 可以根據多個分析結果計算
                risk_level=risk_level,
                recommendations=recommendations,
                analyzed_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"AI偵測失敗: {e}")
            return AIDetectionResult(
                content_id=content_id or f"content_{datetime.now().timestamp()}",
                detection_score=0.5,
                detection_signals=['分析失敗'],
                confidence=0.0,
                risk_level='medium',
                recommendations=['重新分析'],
                analyzed_at=datetime.now()
            )
    
    def _analyze_language_patterns(self, content: str) -> Tuple[float, List[str]]:
        """分析語言模式"""
        signals = []
        score = 0.0
        
        for pattern in self.ai_patterns['language_patterns']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score += 0.1
                signals.append(f"發現AI語言模式: {pattern}")
        
        return min(score, 1.0), signals
    
    def _analyze_structure_patterns(self, content: str) -> Tuple[float, List[str]]:
        """分析結構模式"""
        signals = []
        score = 0.0
        
        lines = content.split('\n')
        
        # 檢查標題密度
        title_count = sum(1 for line in lines if re.match(r'^#+\s', line.strip()))
        if title_count > len(lines) * 0.3:
            score += 0.3
            signals.append("標題密度過高，結構過於正式")
        
        # 檢查列表密度
        list_count = sum(1 for line in lines if re.match(r'^\d+\.\s|^[•·▪▫]\s', line.strip()))
        if list_count > len(lines) * 0.4:
            score += 0.2
            signals.append("列表密度過高，結構過於規整")
        
        # 檢查段落長度一致性
        paragraph_lengths = [len(line.strip()) for line in lines if line.strip() and not re.match(r'^#+\s', line.strip())]
        if paragraph_lengths:
            length_variance = np.var(paragraph_lengths) if len(paragraph_lengths) > 1 else 0
            if length_variance < 100:  # 段落長度過於一致
                score += 0.2
                signals.append("段落長度過於一致，缺乏自然變化")
        
        return min(score, 1.0), signals
    
    def _analyze_emotion_patterns(self, content: str) -> Tuple[float, List[str]]:
        """分析情感表達模式"""
        signals = []
        score = 0.0
        
        # 檢查客觀表達
        objective_count = sum(1 for pattern in self.ai_patterns['emotion_patterns'] 
                            if re.search(pattern, content, re.IGNORECASE))
        if objective_count > 2:
            score += 0.3
            signals.append("過多客觀表達，缺乏個人情感")
        
        # 檢查情感詞彙
        emotion_words = ['開心', '難過', '興奮', '失望', '驚訝', '憤怒', '害怕', '焦慮']
        emotion_count = sum(1 for word in emotion_words if word in content)
        if emotion_count == 0 and len(content) > 100:
            score += 0.2
            signals.append("缺乏情感詞彙，表達過於理性")
        
        return min(score, 1.0), signals
    
    def _analyze_human_patterns(self, content: str) -> Tuple[float, List[str]]:
        """分析人類特徵"""
        signals = []
        score = 0.0
        
        # 檢查個人化表達
        personal_count = sum(1 for pattern in self.human_patterns['personal_indicators'] 
                           if pattern in content)
        if personal_count > 0:
            score += 0.2
            signals.append("包含個人化表達")
        
        # 檢查隨意表達
        casual_count = sum(1 for pattern in self.human_patterns['casual_expressions'] 
                         if pattern in content)
        if casual_count > 0:
            score += 0.2
            signals.append("包含隨意表達")
        
        # 檢查打字習慣
        typing_count = sum(1 for pattern in self.human_patterns['typing_habits'] 
                         if pattern in content)
        if typing_count > 0:
            score += 0.1
            signals.append("包含人類打字習慣")
        
        # 檢查不完整思維
        incomplete_count = sum(1 for pattern in self.human_patterns['incomplete_thoughts'] 
                             if re.search(pattern, content))
        if incomplete_count > 0:
            score += 0.1
            signals.append("包含不完整思維表達")
        
        return min(score, 1.0), signals
    
    def _analyze_ai_keywords(self, content: str) -> Tuple[float, List[str]]:
        """分析AI相關關鍵詞"""
        signals = []
        score = 0.0
        
        content_lower = content.lower()
        for keyword in self.ai_patterns['ai_keywords']:
            if keyword.lower() in content_lower:
                score += 0.3
                signals.append(f"包含AI相關關鍵詞: {keyword}")
        
        return min(score, 1.0), signals
    
    async def _analyze_with_openai(self, content: str) -> Tuple[float, List[str]]:
        """使用OpenAI進行深度分析"""
        try:
            prompt = f"""
請分析以下內容是否可能是AI生成的，並給出0-1的分數（0表示很可能是人類寫的，1表示很可能是AI生成的）。

分析重點：
1. 語言是否過於正式或結構化
2. 是否缺乏個人化表達
3. 情感表達是否自然
4. 是否有明顯的AI生成特徵

內容：
{content}

請只回答一個0-1之間的分數，不要其他解釋。
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(score_text)
            
            signals = []
            if score > 0.7:
                signals.append("OpenAI分析顯示高AI生成可能性")
            elif score > 0.4:
                signals.append("OpenAI分析顯示中等AI生成可能性")
            
            return score, signals
            
        except Exception as e:
            logger.error(f"OpenAI分析失敗: {e}")
            return 0.0, []
    
    def _calculate_risk_level(self, score: float) -> str:
        """計算風險等級"""
        if score >= 0.7:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, score: float, signals: List[str]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        if score >= 0.7:
            recommendations.extend([
                "建議大幅調整內容風格，增加更多個人化表達",
                "減少過於正式的語言結構",
                "增加更多情感表達和個人觀點",
                "使用更隨意的語言風格"
            ])
        elif score >= 0.4:
            recommendations.extend([
                "建議適度調整內容風格",
                "增加一些個人化元素",
                "減少過於客觀的表達方式"
            ])
        else:
            recommendations.append("內容風格良好，保持現狀")
        
        return recommendations
    
    async def analyze_comments(self, comments: List[Dict]) -> List[CommentAnalysis]:
        """分析留言列表"""
        analyses = []
        
        for comment in comments:
            try:
                content = comment.get('content', '')
                comment_id = comment.get('id', f"comment_{datetime.now().timestamp()}")
                
                # AI偵測
                ai_detection = await self.detect_ai_content(content, comment_id)
                
                # 情感分析
                sentiment_score = self._analyze_sentiment(content)
                
                # 品質分析
                quality_score = self._analyze_comment_quality(content)
                
                # 可疑模式
                suspicious_patterns = self._detect_suspicious_patterns(content)
                
                analysis = CommentAnalysis(
                    comment_id=comment_id,
                    content=content,
                    ai_detection_score=ai_detection.detection_score,
                    sentiment_score=sentiment_score,
                    quality_score=quality_score,
                    suspicious_patterns=suspicious_patterns,
                    analyzed_at=datetime.now()
                )
                
                analyses.append(analysis)
                
            except Exception as e:
                logger.error(f"分析留言失敗: {e}")
                continue
        
        return analyses
    
    def _analyze_sentiment(self, content: str) -> float:
        """分析情感分數"""
        positive_words = ['好', '棒', '讚', '厲害', '支持', '認同', '同意', '喜歡', '愛']
        negative_words = ['爛', '差', '反對', '不同意', '質疑', '懷疑', '討厭', '恨', '垃圾']
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        if positive_count + negative_count == 0:
            return 0.5
        
        return (positive_count - negative_count) / (positive_count + negative_count) * 0.5 + 0.5
    
    def _analyze_comment_quality(self, content: str) -> float:
        """分析留言品質"""
        if len(content) < 5:
            return 0.1
        
        quality_score = 0.0
        
        # 長度分數
        length_score = min(len(content) / 100, 1.0) * 0.3
        quality_score += length_score
        
        # 內容豐富度
        if any(char in content for char in ['？', '?', '！', '!']):
            quality_score += 0.2
        
        # 具體資訊
        if any(word in content for word in ['股價', '技術', '基本面', '分析', '數據', '財報']):
            quality_score += 0.3
        
        # 有意義討論
        if len(content.split()) >= 3:
            quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    def _detect_suspicious_patterns(self, content: str) -> List[str]:
        """偵測可疑模式"""
        patterns = []
        
        # 檢查是否包含AI相關關鍵詞
        for keyword in self.ai_patterns['ai_keywords']:
            if keyword.lower() in content.lower():
                patterns.append(f"包含AI關鍵詞: {keyword}")
        
        # 檢查過於正式的表達
        formal_patterns = ['根據', '基於', '綜合分析', '總結來說']
        formal_count = sum(1 for pattern in formal_patterns if pattern in content)
        if formal_count >= 2:
            patterns.append("過於正式的表達方式")
        
        # 檢查缺乏個人化
        personal_indicators = ['我覺得', '我認為', '我的看法', '個人覺得']
        if not any(indicator in content for indicator in personal_indicators):
            patterns.append("缺乏個人化表達")
        
        return patterns
    
    async def batch_analyze_content(self, content_list: List[Dict]) -> List[AIDetectionResult]:
        """批量分析內容"""
        results = []
        
        for content_data in content_list:
            try:
                content = content_data.get('content', '')
                content_id = content_data.get('id', f"content_{datetime.now().timestamp()}")
                
                result = await self.detect_ai_content(content, content_id)
                results.append(result)
                
                # 避免API調用過於頻繁
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"批量分析失敗: {e}")
                continue
        
        return results
    
    def get_detection_summary(self, results: List[AIDetectionResult]) -> Dict[str, Any]:
        """獲取偵測摘要"""
        if not results:
            return {}
        
        scores = [r.detection_score for r in results]
        risk_levels = [r.risk_level for r in results]
        
        return {
            'total_analyzed': len(results),
            'average_score': sum(scores) / len(scores),
            'high_risk_count': risk_levels.count('high'),
            'medium_risk_count': risk_levels.count('medium'),
            'low_risk_count': risk_levels.count('low'),
            'high_risk_percentage': risk_levels.count('high') / len(results) * 100,
            'common_signals': self._get_common_signals(results)
        }
    
    def _get_common_signals(self, results: List[AIDetectionResult]) -> List[str]:
        """獲取常見信號"""
        all_signals = []
        for result in results:
            all_signals.extend(result.detection_signals)
        
        # 統計信號頻率
        signal_count = {}
        for signal in all_signals:
            signal_count[signal] = signal_count.get(signal, 0) + 1
        
        # 返回最常見的信號
        common_signals = sorted(signal_count.items(), key=lambda x: x[1], reverse=True)
        return [signal for signal, count in common_signals[:5] if count > 1]

