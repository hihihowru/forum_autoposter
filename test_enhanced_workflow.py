"""
測試增強版工作流程
使用模擬數據測試完整流程，重點展示新功能和 Google Sheets 記錄
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
from src.clients.google.sheets_client import GoogleSheetsClient

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockEnhancedWorkflow:
    """模擬增強版工作流程"""
    
    def __init__(self):
        # 初始化服務
        credentials_file = "credentials/google-service-account.json"
        spreadsheet_id = "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        self.sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 初始化新功能服務
        self.prompt_generator = PersonalizedPromptGenerator()
        self.quality_checker = ContentQualityChecker()
        self.regenerator = ContentRegenerator(self.prompt_generator, self.quality_checker)
        self.enhanced_recorder = EnhancedSheetsRecorder(self.sheets_client)
        
        print("🚀 測試版增強工作流程已初始化")
        print("✨ 新功能：個人化 Prompting、品質檢查、自動重新生成、完整記錄")
    
    async def run_test_workflow(self):
        """執行測試工作流程"""
        
        print("\n" + "="*60)
        print("🧪 開始測試增強版功能")
        print("📝 重點：展示新功能 + Google Sheets 記錄")
        print("="*60)
        
        try:
            # 步驟 1: 使用模擬話題數據
            print("\n📈 步驟 1: 使用模擬熱門話題")
            mock_topics = self.get_mock_topics()
            
            print(f"✅ 模擬 {len(mock_topics)} 個熱門話題")
            for i, topic in enumerate(mock_topics, 1):
                print(f"  {i}. {topic['title']}")
            
            # 步驟 2: 模擬話題分派
            print("\n👥 步驟 2: 模擬 KOL 分派")
            mock_assignments = self.get_mock_assignments(mock_topics)
            
            print(f"✅ 總共產生 {len(mock_assignments)} 個分派")
            for assignment in mock_assignments:
                kol_info = assignment['kol_profile']
                print(f"  👤 {kol_info['nickname']} (序號: {kol_info['serial']}) - {assignment['topic_data']['title'][:50]}...")
            
            # 步驟 3: 個人化內容生成
            print("\n🎭 步驟 3: 個人化內容生成")
            generated_posts = await self.generate_personalized_content(mock_assignments)
            
            if not generated_posts:
                print("❌ 內容生成失敗")
                return
            
            print(f"✅ 成功生成 {len(generated_posts)} 篇內容")
            
            # 步驟 4: 內容品質檢查
            print("\n🔍 步驟 4: 內容品質檢查")
            quality_result = await self.quality_checker.check_batch_quality(generated_posts)
            
            # 步驟 5: 重新生成 (如果需要)
            regeneration_results = []
            if not quality_result.passed:
                print("\n🔄 步驟 5: 內容重新生成")
                generation_context = {
                    'trigger_source': 'trending_topics',
                    'data_sources_used': ['mock_data', 'openai_gpt'],
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
            
            # 步驟 6: 記錄到 Google Sheets
            print("\n📊 步驟 6: 記錄到 Google Sheets")
            await self.record_to_google_sheets(generated_posts, mock_assignments, quality_result, regeneration_results)
            
            # 步驟 7: 顯示最終預覽
            print("\n👀 步驟 7: 最終內容預覽")
            self.display_final_preview(generated_posts)
            
            # 步驟 8: 測試完成
            print("\n✅ 步驟 8: 測試完成")
            print("🚫 測試模式，不實際發文")
            print("📝 所有數據已記錄到 Google Sheets")
            
            # 顯示 Google Sheets 連結
            print(f"\n🔗 請檢查 Google Sheets:")
            print(f"   📋 貼文記錄表: https://docs.google.com/spreadsheets/d/148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s/edit#gid=0")
            
            # 顯示統計資料
            await self.display_statistics()
            
        except Exception as e:
            logger.error(f"測試工作流程執行失敗: {e}")
            print(f"❌ 工作流程執行失敗: {e}")
    
    def get_mock_topics(self) -> List[Dict[str, Any]]:
        """獲取模擬話題數據"""
        
        return [
            {
                'id': 'topic_001',
                'title': '台積電第三季財報超預期，AI 需求持續強勁',
                'keywords': ['台積電', '2330', 'AI', '財報', '半導體'],
                'classification': {
                    'persona_tags': ['技術派', '總經派'],
                    'industry_tags': ['半導體', 'AI'],
                    'investment_type': 'stock_analysis'
                }
            },
            {
                'id': 'topic_002', 
                'title': '聯準會升息預期降溫，美股科技股反彈',
                'keywords': ['聯準會', '升息', '美股', '科技股', '利率'],
                'classification': {
                    'persona_tags': ['總經派', '新聞派'],
                    'industry_tags': ['總體經濟', '美股'],
                    'investment_type': 'macro_analysis'
                }
            },
            {
                'id': 'topic_003',
                'title': '電動車概念股表現亮眼，特斯拉交車數創新高',
                'keywords': ['電動車', '特斯拉', '概念股', '交車數'],
                'classification': {
                    'persona_tags': ['技術派', '新聞派'],
                    'industry_tags': ['電動車', '汽車'],
                    'investment_type': 'sector_analysis'
                }
            }
        ]
    
    def get_mock_assignments(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """模擬 KOL 分派"""
        
        mock_kols = [
            {'serial': '200', 'nickname': '川川哥', 'member_id': '1001', 'persona': '技術派'},
            {'serial': '202', 'nickname': '梅川褲子', 'member_id': '1002', 'persona': '新聞派'},
            {'serial': '201', 'nickname': '韭割哥', 'member_id': '1003', 'persona': '總經派'}
        ]
        
        assignments = []
        for i, topic in enumerate(topics):
            kol = mock_kols[i % len(mock_kols)]
            assignments.append({
                'topic_data': topic,
                'kol_profile': kol
            })
        
        return assignments
    
    async def generate_personalized_content(self, assignments: List[Dict[str, Any]]) -> List[GeneratedPost]:
        """生成個人化內容"""
        
        generated_posts = []
        
        for i, assignment in enumerate(assignments):
            try:
                kol_profile = assignment['kol_profile']
                topic_data = assignment['topic_data']
                
                kol_serial = str(kol_profile['serial'])
                kol_nickname = kol_profile['nickname']
                
                print(f"\n  🎭 為 {kol_nickname} 生成個人化內容...")
                
                # 生成個人化 prompt
                personalized_prompt = await self.prompt_generator.generate_personalized_prompt(
                    kol_serial=kol_serial,
                    topic_title=topic_data['title'],
                    topic_keywords=', '.join(topic_data['keywords']),
                    market_data=None
                )
                
                # 使用 prompt 生成內容
                content_result = await self.generate_content_with_prompt(personalized_prompt)
                
                if content_result:
                    # 建立貼文物件 - 使用正確的貼文ID格式: {話題ID}-{KOL序號}
                    post_id = f"{topic_data['id']}-{kol_serial}"
                    post = GeneratedPost(
                        post_id=post_id,
                        kol_serial=kol_serial,
                        kol_nickname=kol_nickname,
                        persona=personalized_prompt.kol_settings.persona,
                        title=content_result.get('title', ''),
                        content=content_result.get('content', ''),
                        topic_title=topic_data['title'],
                        generation_params=personalized_prompt.generation_params,
                        created_at=datetime.now()
                    )
                    
                    generated_posts.append(post)
                    print(f"    ✅ 生成成功: {post.title[:50]}...")
                else:
                    print(f"    ❌ 生成失敗")
                    
            except Exception as e:
                logger.error(f"為 {kol_profile['nickname']} 生成內容失敗: {e}")
                print(f"    ❌ 生成失敗: {e}")
        
        return generated_posts
    
    async def generate_content_with_prompt(self, prompt) -> Optional[Dict[str, str]]:
        """使用 prompt 生成內容"""
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
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
                    'trigger_source': 'test_workflow',
                    'trigger_event_id': f'test_{datetime.now().strftime("%Y%m%d_%H%M")}',
                    'data_sources_used': ['mock_data', 'openai_gpt'],
                    'data_sources_status': 'mock:success,openai:success',
                    'agent_decision_log': f'測試模式自動分派給 {post.kol_nickname}',
                    'content_length_type': 'medium',
                    'kol_weight_settings': {},
                    'kol_settings_version': 'v1.0_test',
                    'tone_vector': post.generation_params.get('temperature', 0.7),
                    'generation_params': post.generation_params
                }
                
                # 獲取該貼文的品質檢查結果
                post_issues = [issue for issue in quality_result.issues if issue.post_id == post.post_id]
                quality_data = {
                    'check_rounds': 1,
                    'overall_score': quality_result.detailed_scores.get(post.post_id, {}).get('overall', 0.0),
                    'issues': [{'type': issue.issue_type, 'description': issue.description} for issue in post_issues]
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
    
    print("🧪 啟動測試版增強工作流程")
    
    # 檢查環境變數
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 錯誤: 未找到 OPENAI_API_KEY 環境變數")
        return
    
    try:
        # 建立測試系統實例
        system = MockEnhancedWorkflow()
        
        # 執行測試工作流程
        await system.run_test_workflow()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用戶中斷執行")
    except Exception as e:
        logger.error(f"測試系統執行失敗: {e}")
        print(f"❌ 測試系統執行失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())
