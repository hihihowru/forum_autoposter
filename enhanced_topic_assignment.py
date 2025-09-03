"""
增強版話題分派系統
整合個人化 prompting、品質檢查、重新生成、Google Sheets 記錄等新功能
重點：完整展示流程但不實際發文，所有數據都記錄到 Google Sheets
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加路徑以導入本地模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.content.personalized_prompt_generator import PersonalizedPromptGenerator
from src.services.content.content_quality_checker import ContentQualityChecker, GeneratedPost
from src.services.content.content_regenerator import ContentRegenerator
from src.services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder

# 導入現有服務
from src.clients.cmoney.cmoney_client import CMoneyClient
from src.services.assign.assignment_service import AssignmentService
from src.services.classification.topic_classifier import TopicClassifier
from src.clients.google.sheets_client import GoogleSheetsClient

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedTopicAssignmentSystem:
    """增強版話題分派系統"""
    
    def __init__(self):
        # 初始化現有服務
        credentials_file = "credentials/google-service-account.json"
        spreadsheet_id = "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        self.sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        self.cmoney_client = CMoneyClient()
        self.assignment_service = AssignmentService(self.sheets_client)
        self.topic_classifier = TopicClassifier()
        
        # 初始化新功能服務
        self.prompt_generator = PersonalizedPromptGenerator()
        self.quality_checker = ContentQualityChecker()
        self.regenerator = ContentRegenerator(self.prompt_generator, self.quality_checker)
        self.enhanced_recorder = EnhancedSheetsRecorder(self.sheets_client)
        
        print("🚀 增強版話題分派系統已初始化")
        print("✨ 新功能：個人化 Prompting、品質檢查、自動重新生成、完整記錄")
    
    async def run_enhanced_workflow(self):
        """執行增強版工作流程"""
        
        print("\n" + "="*60)
        print("🎯 開始增強版話題分派流程")
        print("📝 重點：展示完整流程 + Google Sheets 記錄，但不實際發文")
        print("="*60)
        
        try:
            # 步驟 1: 獲取熱門話題
            print("\n📈 步驟 1: 獲取熱門話題")
            topics = await self.get_trending_topics()
            if not topics:
                print("❌ 無法獲取熱門話題")
                return
            
            print(f"✅ 獲取到 {len(topics)} 個熱門話題")
            for i, topic in enumerate(topics[:3], 1):
                print(f"  {i}. {topic.get('title', '無標題')}")
            
            # 步驟 2: 話題分類
            print("\n🔍 步驟 2: 話題分類與分析")
            classified_topics = []
            
            for i, topic in enumerate(topics[:3]):  # 只處理前3個話題
                print(f"\n  分析話題 {i+1}: {topic.get('title', '無標題')}")
                
                classification = await self.topic_classifier.classify_topic(
                    topic.get('title', ''),
                    topic.get('keywords', [])
                )
                
                topic['classification'] = classification
                classified_topics.append(topic)
                
                print(f"    🏷️ 分類: {classification.get('persona_tags', [])}")
                print(f"    🏢 行業: {classification.get('industry_tags', [])}")
            
            # 步驟 3: KOL 分派
            print("\n👥 步驟 3: KOL 分派")
            all_assignments = []
            
            for topic in classified_topics:
                assignments = await self.assignment_service.assign_topics([topic])
                all_assignments.extend(assignments)
                
                print(f"  話題: {topic.get('title', '無標題')[:50]}...")
                for assignment in assignments:
                    kol_info = assignment.get('kol_profile', {})
                    print(f"    👤 分派給: {kol_info.get('nickname', 'Unknown')} (序號: {kol_info.get('serial', 'Unknown')})")
            
            print(f"\n✅ 總共產生 {len(all_assignments)} 個分派")
            
            # 步驟 4: 個人化內容生成
            print("\n🎭 步驟 4: 個人化內容生成")
            generated_posts = await self.generate_personalized_content(all_assignments)
            
            if not generated_posts:
                print("❌ 內容生成失敗")
                return
            
            print(f"✅ 成功生成 {len(generated_posts)} 篇內容")
            
            # 步驟 5: 內容品質檢查
            print("\n🔍 步驟 5: 內容品質檢查")
            quality_result = await self.quality_checker.check_batch_quality(generated_posts)
            
            # 步驟 6: 重新生成 (如果需要)
            regeneration_results = []
            if not quality_result.passed:
                print("\n🔄 步驟 6: 內容重新生成")
                generation_context = {
                    'trigger_source': 'trending_topics',
                    'data_sources_used': ['cmoney_api', 'openai_gpt'],
                    'content_length_type': 'medium'
                }
                
                regeneration_results = await self.regenerator.regenerate_failed_posts(
                    generated_posts, quality_result, generation_context
                )
                
                # 更新貼文列表
                for regen_result in regeneration_results:
                    if regen_result.final_success and regen_result.final_post:
                        for i, post in enumerate(generated_posts):
                            if post.post_id == regen_result.original_post.post_id:
                                generated_posts[i] = regen_result.final_post
                                generated_posts[i].regeneration_count = regen_result.total_attempts
                                generated_posts[i].quality_improvements = regen_result.improvements_made
                                break
            
            # 步驟 7: 記錄到 Google Sheets
            print("\n📊 步驟 7: 記錄到 Google Sheets")
            await self.record_to_google_sheets(generated_posts, all_assignments, quality_result, regeneration_results)
            
            # 步驟 8: 顯示最終預覽
            print("\n👀 步驟 8: 最終內容預覽")
            self.display_final_preview(generated_posts)
            
            # 步驟 9: 用戶確認 (模擬)
            print("\n✋ 步驟 9: 用戶確認環節")
            print("🚫 因為是測試模式，不會實際發文")
            print("📝 所有數據已記錄到 Google Sheets，請檢查確認")
            
            # 顯示 Google Sheets 連結
            print(f"\n🔗 請檢查 Google Sheets:")
            print(f"   📋 貼文記錄表: https://docs.google.com/spreadsheets/d/148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s/edit#gid=0")
            
            # 顯示統計資料
            await self.display_statistics()
            
        except Exception as e:
            logger.error(f"增強版工作流程執行失敗: {e}")
            print(f"❌ 工作流程執行失敗: {e}")
    
    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """獲取熱門話題"""
        
        try:
            # 登入 CMoney
            if not await self.cmoney_client.login():
                print("❌ CMoney 登入失敗")
                return []
            
            # 獲取熱門話題
            topics = await self.cmoney_client.get_trending_topics()
            
            if not topics:
                print("⚠️ 未獲取到熱門話題")
                return []
            
            return topics
            
        except Exception as e:
            logger.error(f"獲取熱門話題失敗: {e}")
            return []
    
    async def generate_personalized_content(self, assignments: List[Dict[str, Any]]) -> List[GeneratedPost]:
        """生成個人化內容"""
        
        generated_posts = []
        
        for i, assignment in enumerate(assignments):
            try:
                kol_profile = assignment.get('kol_profile', {})
                topic_data = assignment.get('topic_data', {})
                
                kol_serial = str(kol_profile.get('serial', ''))
                kol_nickname = kol_profile.get('nickname', f'KOL_{kol_serial}')
                
                print(f"\n  🎭 為 {kol_nickname} 生成個人化內容...")
                
                # 生成個人化 prompt
                personalized_prompt = await self.prompt_generator.generate_personalized_prompt(
                    kol_serial=kol_serial,
                    topic_title=topic_data.get('title', ''),
                    topic_keywords=', '.join(topic_data.get('keywords', [])),
                    market_data=None
                )
                
                # 使用 prompt 生成內容
                content_result = await self.generate_content_with_prompt(personalized_prompt)
                
                if content_result:
                    # 建立貼文物件
                    post = GeneratedPost(
                        post_id=f"topic_{i+1}_kol_{kol_serial}",
                        kol_serial=kol_serial,
                        kol_nickname=kol_nickname,
                        persona=personalized_prompt.kol_settings.persona,
                        title=content_result.get('title', ''),
                        content=content_result.get('content', ''),
                        topic_title=topic_data.get('title', ''),
                        generation_params=personalized_prompt.generation_params,
                        created_at=datetime.now()
                    )
                    
                    generated_posts.append(post)
                    print(f"    ✅ 生成成功: {post.title[:50]}...")
                else:
                    print(f"    ❌ 生成失敗")
                    
            except Exception as e:
                logger.error(f"為 {kol_profile.get('nickname', 'Unknown')} 生成內容失敗: {e}")
                print(f"    ❌ 生成失敗: {e}")
        
        return generated_posts
    
    async def generate_content_with_prompt(self, prompt) -> Optional[Dict[str, str]]:
        """使用 prompt 生成內容"""
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = await client.chat.completions.create(
                model=prompt.generation_params.get('model', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": prompt.system_prompt},
                    {"role": "user", "content": prompt.user_prompt}
                ],
                temperature=prompt.generation_params.get('temperature', 0.7),
                max_tokens=prompt.generation_params.get('max_tokens', 800)
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
            logger.error(f"使用 prompt 生成內容失敗: {e}")
            return None
    
    async def record_to_google_sheets(self, 
                                    posts: List[GeneratedPost],
                                    assignments: List[Dict[str, Any]],
                                    quality_result,
                                    regeneration_results: List):
        """記錄到 Google Sheets"""
        
        try:
            print("  📊 準備寫入 Google Sheets...")
            
            for i, post in enumerate(posts):
                # 準備記錄數據
                assignment = assignments[i] if i < len(assignments) else {}
                topic_data = assignment.get('topic_data', {})
                
                post_data = {
                    'post_id': post.post_id,
                    'kol_serial': post.kol_serial,
                    'kol_nickname': post.kol_nickname,
                    'kol_member_id': assignment.get('kol_profile', {}).get('member_id', ''),
                    'kol_persona': post.persona,
                    'topic_id': topic_data.get('id', ''),
                    'topic_title': topic_data.get('title', ''),
                    'topic_keywords': topic_data.get('keywords', []),
                    'generated_title': post.title,
                    'generated_content': post.content,
                    'regeneration_count': getattr(post, 'regeneration_count', 0),
                    'quality_improvements': getattr(post, 'quality_improvements', [])
                }
                
                generation_context = {
                    'topic_index': i + 1,
                    'trigger_source': 'trending_topics',
                    'trigger_event_id': f'trending_{datetime.now().strftime("%Y%m%d_%H%M")}',
                    'data_sources_used': ['cmoney_api', 'openai_gpt'],
                    'data_sources_status': 'cmoney:success,openai:success',
                    'agent_decision_log': f'自動分派給 {post.kol_nickname}',
                    'content_length_type': 'medium',
                    'kol_weight_settings': {},
                    'kol_settings_version': 'v1.0',
                    'tone_vector': post.generation_params.get('temperature', 0.7),
                    'generation_params': post.generation_params
                }
                
                # 獲取該貼文的品質檢查結果
                quality_data = {
                    'check_rounds': 1,
                    'overall_score': quality_result.detailed_scores.get(post.post_id, {}).get('overall', 0.0),
                    'issues': [issue for issue in quality_result.issues if issue.post_id == post.post_id]
                }
                
                # 記錄到 Google Sheets
                success = await self.enhanced_recorder.record_enhanced_post(
                    post_data, generation_context, quality_data
                )
                
                if success:
                    print(f"    ✅ 記錄成功: {post.kol_nickname}")
                else:
                    print(f"    ❌ 記錄失敗: {post.kol_nickname}")
            
            print("  📝 Google Sheets 記錄完成")
            
        except Exception as e:
            logger.error(f"記錄到 Google Sheets 失敗: {e}")
            print(f"  ❌ Google Sheets 記錄失敗: {e}")
    
    def display_final_preview(self, posts: List[GeneratedPost]):
        """顯示最終預覽"""
        
        print(f"\n📋 最終生成內容預覽 ({len(posts)} 篇):")
        print("-" * 80)
        
        for i, post in enumerate(posts, 1):
            print(f"\n📄 貼文 {i}: {post.kol_nickname} ({post.persona})")
            print(f"標題: {post.title}")
            print(f"內容: {post.content[:100]}...")
            print(f"字數: {len(post.content)} 字")
            print(f"品質分數: {post.generation_params.get('quality_score', '未知')}")
            
            if hasattr(post, 'regeneration_count') and post.regeneration_count > 0:
                print(f"🔄 重新生成: {post.regeneration_count} 次")
        
        print("-" * 80)
    
    async def display_statistics(self):
        """顯示統計資料"""
        
        try:
            stats = await self.enhanced_recorder.get_generation_statistics()
            
            if stats:
                print(f"\n📊 生成統計:")
                print(f"  總貼文數: {stats.get('total_posts', 0)}")
                print(f"  平均品質分數: {stats.get('quality_stats', {}).get('average_score', 0):.1f}/10")
                print(f"  重新生成率: {stats.get('quality_stats', {}).get('regeneration_rate', 0)*100:.1f}%")
                
                print(f"\n📈 KOL 分布:")
                for kol, count in stats.get('by_kol', {}).items():
                    print(f"  {kol}: {count} 篇")
                
                print(f"\n📊 內容長度分布:")
                for category, count in stats.get('by_length_category', {}).items():
                    print(f"  {category}: {count} 篇")
        
        except Exception as e:
            logger.error(f"顯示統計資料失敗: {e}")

async def main():
    """主函數"""
    
    print("🚀 啟動增強版話題分派系統")
    
    # 檢查環境變數
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 錯誤: 未找到 OPENAI_API_KEY 環境變數")
        return
    
    try:
        # 建立系統實例
        system = EnhancedTopicAssignmentSystem()
        
        # 執行完整工作流程
        await system.run_enhanced_workflow()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用戶中斷執行")
    except Exception as e:
        logger.error(f"系統執行失敗: {e}")
        print(f"❌ 系統執行失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())
