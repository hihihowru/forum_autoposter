"""
內容重新生成器
根據品質檢查結果重新生成內容，包括智能參數調整和重試機制
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

from .personalized_prompt_generator import PersonalizedPromptGenerator, PersonalizedPrompt
from .content_quality_checker import ContentQualityChecker, QualityCheckResult, GeneratedPost, QualityIssue

logger = logging.getLogger(__name__)

@dataclass
class RegenerationAttempt:
    """重新生成嘗試記錄"""
    attempt_number: int
    timestamp: datetime
    adjusted_params: Dict[str, Any]
    quality_score: float
    success: bool
    issues_resolved: List[str]
    remaining_issues: List[str]

@dataclass
class RegenerationResult:
    """重新生成結果"""
    original_post: GeneratedPost
    final_post: Optional[GeneratedPost]
    attempts: List[RegenerationAttempt]
    total_attempts: int
    final_success: bool
    final_quality_score: float
    improvements_made: List[str]

class ContentRegenerator:
    """內容重新生成器"""
    
    def __init__(self, prompt_generator: PersonalizedPromptGenerator, 
                 quality_checker: ContentQualityChecker):
        self.prompt_generator = prompt_generator
        self.quality_checker = quality_checker
        self.max_attempts = 3
        
        # 參數調整策略
        self.adjustment_strategies = {
            'content_too_similar': {
                'temperature': lambda x: min(x + 0.2, 1.0),
                'diversity_boost': True,
                'prompt_variation': True
            },
            'insufficient_personalization': {
                'temperature': lambda x: min(x + 0.1, 0.9),
                'persona_emphasis': True,
                'vocabulary_boost': True
            },
            'content_too_short': {
                'min_length_requirement': True,
                'detail_emphasis': True
            },
            'poor_content_quality': {
                'temperature': lambda x: max(x - 0.1, 0.3),
                'quality_emphasis': True
            }
        }
    
    async def regenerate_failed_posts(self, 
                                    original_posts: List[GeneratedPost],
                                    quality_result: QualityCheckResult,
                                    generation_context: Dict[str, Any]) -> List[RegenerationResult]:
        """重新生成品質檢查失敗的貼文"""
        
        if not quality_result.posts_to_regenerate:
            print("✅ 沒有需要重新生成的貼文")
            return []
        
        print(f"\n🔄 開始重新生成 {len(quality_result.posts_to_regenerate)} 篇貼文...")
        
        regeneration_results = []
        
        for post_id in quality_result.posts_to_regenerate:
            # 找到原始貼文
            original_post = next((p for p in original_posts if p.post_id == post_id), None)
            if not original_post:
                continue
            
            print(f"\n🎯 重新生成: {original_post.kol_nickname}")
            
            # 分析該貼文的問題
            post_issues = [issue for issue in quality_result.issues if issue.post_id == post_id]
            print(f"  發現問題: {len(post_issues)} 個")
            for issue in post_issues:
                print(f"    - {issue.issue_type}: {issue.description}")
            
            # 執行重新生成
            result = await self.regenerate_single_post(
                original_post, post_issues, generation_context, original_posts
            )
            
            regeneration_results.append(result)
            
            # 顯示結果
            if result.final_success:
                print(f"  ✅ 重新生成成功 (嘗試 {result.total_attempts} 次)")
                print(f"  📈 品質提升: {result.original_post.generation_params.get('quality_score', 0):.1f} -> {result.final_quality_score:.1f}")
            else:
                print(f"  ❌ 重新生成失敗，需要人工審核")
        
        return regeneration_results
    
    async def regenerate_single_post(self, 
                                   original_post: GeneratedPost,
                                   issues: List[QualityIssue],
                                   generation_context: Dict[str, Any],
                                   all_posts: List[GeneratedPost]) -> RegenerationResult:
        """重新生成單篇貼文"""
        
        attempts = []
        current_post = original_post
        
        for attempt_num in range(1, self.max_attempts + 1):
            print(f"    🔄 嘗試 {attempt_num}/{self.max_attempts}")
            
            try:
                # 調整生成參數
                adjusted_params = self.adjust_generation_params(
                    original_post.generation_params, issues, attempt_num
                )
                
                # 生成改良的 prompt
                improved_prompt = await self.build_improved_prompt(
                    original_post, issues, adjusted_params, attempt_num
                )
                
                # 重新生成內容
                new_content = await self.generate_with_improved_prompt(
                    improved_prompt, adjusted_params
                )
                
                if new_content:
                    # 創建新的貼文對象
                    new_post = GeneratedPost(
                        post_id=original_post.post_id,
                        kol_serial=original_post.kol_serial,
                        kol_nickname=original_post.kol_nickname,
                        persona=original_post.persona,
                        title=new_content.get('title', original_post.title),
                        content=new_content.get('content', original_post.content),
                        topic_title=original_post.topic_title,
                        generation_params=adjusted_params,
                        created_at=datetime.now()
                    )
                    
                    # 快速品質檢查
                    quick_check = await self.quick_quality_check(new_post, all_posts)
                    
                    # 記錄嘗試
                    attempt = RegenerationAttempt(
                        attempt_number=attempt_num,
                        timestamp=datetime.now(),
                        adjusted_params=adjusted_params,
                        quality_score=quick_check.overall_score,
                        success=quick_check.passed,
                        issues_resolved=self.get_resolved_issues(issues, quick_check.issues),
                        remaining_issues=[issue.issue_type for issue in quick_check.issues]
                    )
                    attempts.append(attempt)
                    
                    if quick_check.passed:
                        # 重新生成成功
                        return RegenerationResult(
                            original_post=original_post,
                            final_post=new_post,
                            attempts=attempts,
                            total_attempts=attempt_num,
                            final_success=True,
                            final_quality_score=quick_check.overall_score,
                            improvements_made=self.identify_improvements(original_post, new_post)
                        )
                    
                    # 更新當前貼文和問題
                    current_post = new_post
                    issues = quick_check.issues
                
            except Exception as e:
                logger.error(f"重新生成第 {attempt_num} 次嘗試失敗: {e}")
                print(f"      ❌ 生成失敗: {e}")
                
                # 記錄失敗的嘗試
                attempt = RegenerationAttempt(
                    attempt_number=attempt_num,
                    timestamp=datetime.now(),
                    adjusted_params=adjusted_params,
                    quality_score=0.0,
                    success=False,
                    issues_resolved=[],
                    remaining_issues=[issue.issue_type for issue in issues]
                )
                attempts.append(attempt)
        
        # 所有嘗試都失敗
        return RegenerationResult(
            original_post=original_post,
            final_post=None,
            attempts=attempts,
            total_attempts=self.max_attempts,
            final_success=False,
            final_quality_score=0.0,
            improvements_made=[]
        )
    
    def adjust_generation_params(self, 
                               original_params: Dict[str, Any],
                               issues: List[QualityIssue],
                               attempt_num: int) -> Dict[str, Any]:
        """調整生成參數"""
        
        adjusted = original_params.copy()
        
        # 根據問題類型調整參數
        for issue in issues:
            if issue.issue_type in self.adjustment_strategies:
                strategy = self.adjustment_strategies[issue.issue_type]
                
                # 調整 temperature
                if 'temperature' in strategy and callable(strategy['temperature']):
                    current_temp = adjusted.get('temperature', 0.7)
                    adjusted['temperature'] = strategy['temperature'](current_temp)
                
                # 設置特殊標記
                if 'diversity_boost' in strategy:
                    adjusted['diversity_boost'] = True
                if 'persona_emphasis' in strategy:
                    adjusted['persona_emphasis'] = True
                if 'quality_emphasis' in strategy:
                    adjusted['quality_emphasis'] = True
        
        # 根據嘗試次數進一步調整
        if attempt_num > 1:
            # 增加隨機性
            current_temp = adjusted.get('temperature', 0.7)
            adjusted['temperature'] = min(current_temp + (attempt_num - 1) * 0.1, 1.0)
            
            # 調整其他參數
            adjusted['top_p'] = max(0.8 - (attempt_num - 1) * 0.1, 0.6)
            adjusted['frequency_penalty'] = min(0.1 + (attempt_num - 1) * 0.1, 0.3)
        
        return adjusted
    
    async def build_improved_prompt(self, 
                                  original_post: GeneratedPost,
                                  issues: List[QualityIssue],
                                  adjusted_params: Dict[str, Any],
                                  attempt_num: int) -> PersonalizedPrompt:
        """建構改良的 prompt"""
        
        # 分析問題並建構改進指導
        improvement_instructions = []
        
        for issue in issues:
            if issue.issue_type == 'content_too_similar':
                improvement_instructions.append(
                    f"避免與其他 KOL 相似的表達方式，大量使用 {original_post.kol_nickname} "
                    f"的獨特詞彙和語氣特色，展現明顯的個人風格差異"
                )
            elif issue.issue_type == 'insufficient_personalization':
                improvement_instructions.append(
                    f"強化 {original_post.kol_nickname} 的個人特色，使用更多專屬的語氣、"
                    f"詞彙和表達習慣，讓內容更像真人發文"
                )
            elif issue.issue_type == 'content_too_short':
                improvement_instructions.append(
                    "增加內容深度和具體分析，提供更多有價值的觀點和見解"
                )
            elif issue.issue_type == 'poor_content_quality':
                improvement_instructions.append(
                    "提升內容專業性和分析深度，確保觀點明確且有實際投資價值"
                )
        
        # 重新生成個人化 prompt
        base_prompt = await self.prompt_generator.generate_personalized_prompt(
            original_post.kol_serial,
            original_post.topic_title,
            "",  # keywords
            None  # market_data
        )
        
        # 添加改進指導到 prompt
        enhanced_system_prompt = f"""{base_prompt.system_prompt}

重新生成指導 (第 {attempt_num} 次嘗試):
{chr(10).join(improvement_instructions)}

特別注意:
1. 這次生成的內容必須與之前的版本有明顯差異
2. 強化個人化特徵，避免模板化表達
3. 確保內容品質和專業性
4. 使用更多樣化的詞彙和句式
5. 保持角色的獨特風格和語氣
"""
        
        return PersonalizedPrompt(
            system_prompt=enhanced_system_prompt,
            user_prompt=base_prompt.user_prompt,
            kol_settings=base_prompt.kol_settings,
            market_data=base_prompt.market_data,
            generation_params=adjusted_params,
            created_at=datetime.now()
        )
    
    async def generate_with_improved_prompt(self, 
                                          prompt: PersonalizedPrompt,
                                          params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用改良的 prompt 生成內容"""
        
        from openai import OpenAI
        import os
        
        try:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model=params.get('model', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": prompt.system_prompt},
                    {"role": "user", "content": prompt.user_prompt}
                ],
                temperature=params.get('temperature', 0.7),
                max_tokens=params.get('max_tokens', 800),
                top_p=params.get('top_p', 0.9),
                frequency_penalty=params.get('frequency_penalty', 0.1),
                presence_penalty=params.get('presence_penalty', 0.1)
            )
            
            content = response.choices[0].message.content
            
            # 解析標題和內容
            lines = content.strip().split('\n')
            title = ""
            main_content = ""
            
            for line in lines:
                if line.startswith('標題：'):
                    title = line.replace('標題：', '').strip()
                elif line.startswith('內容：'):
                    main_content = line.replace('內容：', '').strip()
                elif not title and '：' not in line and line.strip():
                    title = line.strip()
                elif title and line.strip():
                    if main_content:
                        main_content += '\n' + line.strip()
                    else:
                        main_content = line.strip()
            
            if not title:
                title = main_content.split('\n')[0][:30] + "..."
            
            return {
                'title': title,
                'content': main_content
            }
            
        except Exception as e:
            logger.error(f"使用改良 prompt 生成內容失敗: {e}")
            return None
    
    async def quick_quality_check(self, 
                                post: GeneratedPost,
                                all_posts: List[GeneratedPost]) -> QualityCheckResult:
        """快速品質檢查"""
        
        # 簡化的品質檢查，只檢查關鍵指標
        issues = []
        
        # 1. 長度檢查
        if len(post.content) < 50:
            issues.append(QualityIssue(
                post_id=post.post_id,
                issue_type='content_too_short',
                severity='high',
                description=f'內容仍然過短：{len(post.content)} 字',
                suggestion='需要增加更多內容'
            ))
        
        # 2. 簡單相似度檢查
        for other_post in all_posts:
            if other_post.post_id != post.post_id:
                similarity = await self.quality_checker.calculate_content_similarity(post, other_post)
                if similarity > 0.75:
                    issues.append(QualityIssue(
                        post_id=post.post_id,
                        issue_type='content_too_similar',
                        severity='high',
                        description=f'與 {other_post.kol_nickname} 仍然相似：{similarity:.2f}',
                        suggestion='需要更大差異化'
                    ))
        
        # 3. 計算簡單品質分數
        base_score = 7.0
        if len(post.content) >= 100:
            base_score += 1.0
        if len(issues) == 0:
            base_score += 2.0
        else:
            base_score -= len(issues) * 1.5
        
        overall_score = max(0.0, min(10.0, base_score))
        
        return QualityCheckResult(
            passed=len(issues) == 0 and overall_score >= 6.0,
            overall_score=overall_score,
            issues=issues,
            posts_to_regenerate=[],
            check_timestamp=datetime.now(),
            detailed_scores={post.post_id: {'overall': overall_score}}
        )
    
    def get_resolved_issues(self, 
                          original_issues: List[QualityIssue],
                          new_issues: List[QualityIssue]) -> List[str]:
        """獲取已解決的問題"""
        
        original_types = {issue.issue_type for issue in original_issues}
        new_types = {issue.issue_type for issue in new_issues}
        
        resolved = original_types - new_types
        return list(resolved)
    
    def identify_improvements(self, 
                            original_post: GeneratedPost,
                            new_post: GeneratedPost) -> List[str]:
        """識別改進點"""
        
        improvements = []
        
        # 長度改進
        if len(new_post.content) > len(original_post.content):
            improvements.append(f"內容長度增加：{len(original_post.content)} -> {len(new_post.content)} 字")
        
        # 標題改進
        if new_post.title != original_post.title:
            improvements.append("標題已重新生成")
        
        # 參數調整
        orig_temp = original_post.generation_params.get('temperature', 0.7)
        new_temp = new_post.generation_params.get('temperature', 0.7)
        if abs(new_temp - orig_temp) > 0.05:
            improvements.append(f"Temperature 調整：{orig_temp:.2f} -> {new_temp:.2f}")
        
        return improvements
