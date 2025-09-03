"""
內容品質檢查器
檢查生成內容的品質，包括相似度、長度、個人化特徵等
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

@dataclass
class QualityIssue:
    """品質問題"""
    post_id: str
    issue_type: str
    severity: str  # high, medium, low
    description: str
    suggestion: str
    score: float = 0.0
    similar_to: Optional[str] = None

@dataclass
class QualityCheckResult:
    """品質檢查結果"""
    passed: bool
    overall_score: float
    issues: List[QualityIssue]
    posts_to_regenerate: List[str]
    check_timestamp: datetime
    detailed_scores: Dict[str, Dict[str, float]]

@dataclass
class GeneratedPost:
    """生成的貼文"""
    post_id: str
    kol_serial: str
    kol_nickname: str
    persona: str
    title: str
    content: str
    topic_title: str
    topic_id: str  # 完整的 topic ID
    generation_params: Dict[str, Any]
    created_at: datetime

class ContentQualityChecker:
    """內容品質檢查器"""
    
    def __init__(self):
        self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # 品質閾值設定
        self.similarity_threshold = 0.75
        self.min_length_threshold = 50
        self.max_length_threshold = 600
        self.personalization_threshold = 0.6
        self.overall_quality_threshold = 6.0
        
        # 檢查權重
        self.check_weights = {
            'length': 0.2,
            'similarity': 0.3,
            'personalization': 0.3,
            'content_quality': 0.2
        }
    
    async def check_batch_quality(self, posts: List[GeneratedPost]) -> QualityCheckResult:
        """檢查一批貼文的整體品質"""
        
        print(f"\n🔍 開始品質檢查 ({len(posts)} 篇貼文)...")
        
        all_issues = []
        posts_to_regenerate = []
        detailed_scores = {}
        
        # 1. 個別貼文檢查
        for post in posts:
            post_issues, post_scores = await self.check_individual_post(post)
            all_issues.extend(post_issues)
            detailed_scores[post.post_id] = post_scores
            
            # 檢查是否需要重新生成
            if post_scores['overall'] < self.overall_quality_threshold:
                posts_to_regenerate.append(post.post_id)
        
        # 2. 批次相似度檢查
        similarity_issues = await self.check_batch_similarity(posts)
        all_issues.extend(similarity_issues)
        
        # 更新需要重新生成的貼文
        for issue in similarity_issues:
            if issue.post_id not in posts_to_regenerate:
                posts_to_regenerate.append(issue.post_id)
            if issue.similar_to and issue.similar_to not in posts_to_regenerate:
                posts_to_regenerate.append(issue.similar_to)
        
        # 3. 計算整體品質分數
        overall_score = self.calculate_overall_score(detailed_scores, len(all_issues))
        
        # 4. 生成檢查結果
        result = QualityCheckResult(
            passed=len(posts_to_regenerate) == 0,
            overall_score=overall_score,
            issues=all_issues,
            posts_to_regenerate=list(set(posts_to_regenerate)),  # 去重
            check_timestamp=datetime.now(),
            detailed_scores=detailed_scores
        )
        
        # 5. 顯示檢查結果
        self.display_check_results(result, posts)
        
        return result
    
    async def check_individual_post(self, post: GeneratedPost) -> tuple[List[QualityIssue], Dict[str, float]]:
        """檢查單篇貼文品質"""
        
        issues = []
        scores = {}
        
        # 1. 長度檢查
        length_score, length_issues = self.check_content_length(post)
        scores['length'] = length_score
        issues.extend(length_issues)
        
        # 2. 個人化特徵檢查
        personalization_score, personalization_issues = await self.check_personalization_features(post)
        scores['personalization'] = personalization_score
        issues.extend(personalization_issues)
        
        # 3. 內容品質檢查
        content_score, content_issues = await self.check_content_quality(post)
        scores['content_quality'] = content_score
        issues.extend(content_issues)
        
        # 4. 計算總分
        overall_score = (
            length_score * self.check_weights['length'] +
            personalization_score * self.check_weights['personalization'] +
            content_score * self.check_weights['content_quality']
        )
        scores['overall'] = overall_score
        
        return issues, scores
    
    def check_content_length(self, post: GeneratedPost) -> tuple[float, List[QualityIssue]]:
        """檢查內容長度"""
        
        content_length = len(post.content)
        issues = []
        
        # 基礎長度檢查
        if content_length < self.min_length_threshold:
            issues.append(QualityIssue(
                post_id=post.post_id,
                issue_type='content_too_short',
                severity='high',
                description=f'內容過短：{content_length} 字 (最少需要 {self.min_length_threshold} 字)',
                suggestion='增加分析深度和具體觀點',
                score=content_length / self.min_length_threshold * 10
            ))
            return content_length / self.min_length_threshold * 10, issues
        
        if content_length > self.max_length_threshold:
            issues.append(QualityIssue(
                post_id=post.post_id,
                issue_type='content_too_long',
                severity='medium',
                description=f'內容過長：{content_length} 字 (建議不超過 {self.max_length_threshold} 字)',
                suggestion='精簡表達，突出重點',
                score=8.0
            ))
            return 8.0, issues
        
        # 根據預期長度計算分數
        if 100 <= content_length <= 400:
            return 10.0, issues
        else:
            return 8.0, issues
    
    async def check_personalization_features(self, post: GeneratedPost) -> tuple[float, List[QualityIssue]]:
        """檢查個人化特徵"""
        
        # 使用 LLM 分析個人化程度
        personalization_prompt = f"""
請評估以下貼文的個人化程度：

KOL: {post.kol_nickname} ({post.persona})
標題: {post.title}
內容: {post.content}

評估維度（1-10分）：
1. 語氣風格是否符合 {post.persona} 特色
2. 用詞是否具有個人特色
3. 表達方式是否自然不做作
4. 專業角度是否突出
5. 整體是否像真人發文

請回傳 JSON 格式：
{{
  "style_score": 8,
  "vocabulary_score": 7,
  "naturalness_score": 9,
  "expertise_score": 8,
  "authenticity_score": 7,
  "overall_score": 7.8,
  "issues": ["語氣可以更口語化", "缺少專業術語"],
  "strengths": ["觀點明確", "邏輯清晰"]
}}
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是專業的內容分析師，擅長評估文章的個人化程度。"},
                    {"role": "user", "content": personalization_prompt}
                ],
                temperature=0.1
            )
            
            analysis = json.loads(response.choices[0].message.content)
            overall_score = analysis.get('overall_score', 5.0)
            
            issues = []
            if overall_score < self.personalization_threshold * 10:
                issues.append(QualityIssue(
                    post_id=post.post_id,
                    issue_type='insufficient_personalization',
                    severity='high' if overall_score < 5.0 else 'medium',
                    description=f'個人化程度不足：{overall_score}/10',
                    suggestion=f"改進建議：{', '.join(analysis.get('issues', []))}",
                    score=overall_score
                ))
            
            return overall_score, issues
            
        except Exception as e:
            logger.error(f"個人化檢查失敗: {e}")
            return 5.0, []
    
    async def check_content_quality(self, post: GeneratedPost) -> tuple[float, List[QualityIssue]]:
        """檢查內容品質"""
        
        quality_prompt = f"""
請評估以下投資分析文章的品質：

標題: {post.title}
內容: {post.content}

評估標準（1-10分）：
1. 內容是否有實質分析價值
2. 觀點是否明確且有邏輯
3. 是否適合投資討論
4. 語言表達是否流暢
5. 是否有明顯的 AI 生成痕跡

請回傳 JSON 格式：
{{
  "analysis_value": 8,
  "logical_coherence": 7,
  "investment_relevance": 9,
  "language_fluency": 8,
  "human_like": 6,
  "overall_score": 7.6,
  "major_issues": ["過於模板化", "缺乏具體數據"],
  "improvement_suggestions": ["增加具體案例", "使用更多專業術語"]
}}
"""
        
        try:
            print(f"    🤖 調用 LLM 進行品質評估...")
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是專業的投資內容評審師。"},
                    {"role": "user", "content": quality_prompt}
                ],
                temperature=0.1,
                timeout=20.0  # 增加超時設定
            )
            
            response_content = response.choices[0].message.content
            print(f"    📝 LLM 回應長度: {len(response_content)} 字符")
            
            try:
                analysis = json.loads(response_content)
                overall_score = analysis.get('overall_score', 5.0)
                print(f"    ✅ JSON 解析成功，評分: {overall_score}")
            except json.JSONDecodeError as je:
                print(f"    ⚠️ JSON 解析失敗: {je}")
                print(f"    📄 原始回應: {response_content[:200]}...")
                # 嘗試從文字中提取分數
                score_match = re.search(r'overall_score[\'\"]*:\s*([0-9.]+)', response_content)
                overall_score = float(score_match.group(1)) if score_match else 5.0
                analysis = {'overall_score': overall_score, 'improvement_suggestions': []}
            
            issues = []
            if overall_score < 6.0:
                issues.append(QualityIssue(
                    post_id=post.post_id,
                    issue_type='poor_content_quality',
                    severity='high' if overall_score < 4.0 else 'medium',
                    description=f'內容品質不佳：{overall_score}/10',
                    suggestion=f"改進建議：{', '.join(analysis.get('improvement_suggestions', []))}",
                    score=overall_score
                ))
            
            return overall_score, issues
            
        except Exception as e:
            logger.error(f"內容品質檢查失敗: {e}")
            return 5.0, []
    
    async def check_batch_similarity(self, posts: List[GeneratedPost]) -> List[QualityIssue]:
        """檢查批次相似度"""
        
        similarity_issues = []
        
        for i, post1 in enumerate(posts):
            for j, post2 in enumerate(posts[i+1:], i+1):
                similarity_score = await self.calculate_content_similarity(post1, post2)
                
                if similarity_score > self.similarity_threshold:
                    similarity_issues.append(QualityIssue(
                        post_id=post1.post_id,
                        issue_type='content_too_similar',
                        severity='high',
                        description=f'與 {post2.kol_nickname} 內容過於相似：{similarity_score:.2f}',
                        suggestion=f'重新生成以增加差異化，避免重複表達',
                        score=similarity_score,
                        similar_to=post2.post_id
                    ))
        
        return similarity_issues
    
    async def calculate_content_similarity(self, post1: GeneratedPost, post2: GeneratedPost) -> float:
        """計算內容相似度"""
        
        # 簡單的詞彙重疊計算
        words1 = set(re.findall(r'\w+', post1.content.lower()))
        words2 = set(re.findall(r'\w+', post2.content.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard_similarity = len(intersection) / len(union)
        
        # 結構相似度檢查
        structure_similarity = self.check_structure_similarity(post1, post2)
        
        # 綜合相似度
        overall_similarity = (jaccard_similarity * 0.7 + structure_similarity * 0.3)
        
        return overall_similarity
    
    def check_structure_similarity(self, post1: GeneratedPost, post2: GeneratedPost) -> float:
        """檢查結構相似度"""
        
        # 檢查句子數量相似度
        sentences1 = len(re.findall(r'[。！？]', post1.content))
        sentences2 = len(re.findall(r'[。！？]', post2.content))
        
        sentence_similarity = 1 - abs(sentences1 - sentences2) / max(sentences1, sentences2, 1)
        
        # 檢查段落結構
        paragraphs1 = len(post1.content.split('\n\n'))
        paragraphs2 = len(post2.content.split('\n\n'))
        
        paragraph_similarity = 1 - abs(paragraphs1 - paragraphs2) / max(paragraphs1, paragraphs2, 1)
        
        # 檢查標題模式
        title_pattern_similarity = 0.0
        if post1.title.startswith('【') and post2.title.startswith('【'):
            title_pattern_similarity = 0.5
        
        return (sentence_similarity + paragraph_similarity + title_pattern_similarity) / 3
    
    def calculate_overall_score(self, detailed_scores: Dict[str, Dict[str, float]], 
                               issue_count: int) -> float:
        """計算整體品質分數"""
        
        if not detailed_scores:
            return 0.0
        
        # 計算平均分數
        total_score = 0
        valid_posts = 0
        
        for post_id, scores in detailed_scores.items():
            if 'overall' in scores:
                total_score += scores['overall']
                valid_posts += 1
        
        if valid_posts == 0:
            return 0.0
        
        average_score = total_score / valid_posts
        
        # 根據問題數量調整分數
        issue_penalty = min(issue_count * 0.5, 3.0)
        final_score = max(0.0, average_score - issue_penalty)
        
        return final_score
    
    def display_check_results(self, result: QualityCheckResult, posts: List[GeneratedPost]):
        """顯示檢查結果"""
        
        print(f"\n📊 品質檢查結果:")
        print(f"  整體評分: {result.overall_score:.1f}/10")
        print(f"  檢查狀態: {'✅ 通過' if result.passed else '❌ 未通過'}")
        print(f"  發現問題: {len(result.issues)} 個")
        print(f"  需要重新生成: {len(result.posts_to_regenerate)} 篇")
        
        if result.issues:
            print("\n🔍 問題詳情:")
            for issue in result.issues:
                severity_icon = "🔴" if issue.severity == "high" else "🟡" if issue.severity == "medium" else "🟢"
                post_name = next((p.kol_nickname for p in posts if p.post_id == issue.post_id), issue.post_id)
                print(f"  {severity_icon} {post_name}: {issue.description}")
                if issue.suggestion:
                    print(f"    💡 建議: {issue.suggestion}")
        
        if result.detailed_scores:
            print("\n📈 詳細評分:")
            for post_id, scores in result.detailed_scores.items():
                post_name = next((p.kol_nickname for p in posts if p.post_id == post_id), post_id)
                print(f"  {post_name}: 整體 {scores.get('overall', 0):.1f} "
                      f"(長度 {scores.get('length', 0):.1f}, "
                      f"個人化 {scores.get('personalization', 0):.1f}, "
                      f"品質 {scores.get('content_quality', 0):.1f})")
    
    def get_regeneration_guidance(self, post_id: str, issues: List[QualityIssue]) -> Dict[str, Any]:
        """獲取重新生成指導"""
        
        post_issues = [issue for issue in issues if issue.post_id == post_id]
        
        guidance = {
            'priority_fixes': [],
            'suggested_changes': [],
            'parameter_adjustments': {}
        }
        
        for issue in post_issues:
            if issue.severity == 'high':
                guidance['priority_fixes'].append(issue.description)
                guidance['suggested_changes'].append(issue.suggestion)
            
            # 根據問題類型調整參數
            if issue.issue_type == 'content_too_similar':
                guidance['parameter_adjustments']['temperature'] = 0.8
                guidance['parameter_adjustments']['diversity_boost'] = True
            elif issue.issue_type == 'insufficient_personalization':
                guidance['parameter_adjustments']['persona_emphasis'] = True
            elif issue.issue_type == 'content_too_short':
                guidance['parameter_adjustments']['min_length_boost'] = True
        
        return guidance
