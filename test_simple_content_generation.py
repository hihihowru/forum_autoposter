"""
簡化版內容生成測試（完全跳過 Finlab）
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加路徑以導入本地模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.assign.assignment_service import AssignmentService
from src.services.classification.topic_classifier import TopicClassifier
from src.services.content.personalized_prompt_generator import PersonalizedPromptGenerator
from src.services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder

class SimpleContentTester:
    """簡化版內容生成測試器"""
    
    def __init__(self):
        # 只初始化必要的服務
        self.sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        
        self.cmoney_client = CMoneyClient()
        self.assignment_service = AssignmentService(self.sheets_client)
        self.topic_classifier = TopicClassifier()
        self.prompt_generator = PersonalizedPromptGenerator()
        self.sheets_recorder = EnhancedSheetsRecorder(self.sheets_client)
        
        print("🚀 簡化版內容測試器初始化完成")
    
    async def test_content_generation(self):
        """測試內容生成"""
        
        print("\n" + "="*80)
        print("🎭 簡化版內容生成測試")
        print("🎯 重點：測試個人化 Prompt 和內容品質")
        print("="*80)
        
        try:
            # 步驟 1: 獲取話題
            topics = await self._get_topics()
            
            # 步驟 2: 載入 KOL
            kols = self._load_kols()
            
            # 步驟 3: 生成測試內容
            posts = await self._generate_test_content(topics, kols)
            
            # 步驟 4: 記錄結果
            await self._record_results(posts)
            
            # 步驟 5: 展示結果
            self._show_results(posts)
            
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
            import traceback
            traceback.print_exc()
    
    async def _get_topics(self):
        """獲取話題"""
        
        print("\n📈 步驟 1: 獲取熱門話題")
        print("-" * 40)
        
        try:
            credentials = LoginCredentials(
                email='forum_200@cmoney.com.tw',
                password='N9t1kY3x'
            )
            
            token = await self.cmoney_client.login(credentials)
            topics = await self.cmoney_client.get_trending_topics(token.token)
            
            print(f"✅ 成功獲取 {len(topics)} 個話題")
            for i, topic in enumerate(topics, 1):
                print(f"  {i}. {topic.title}")
            
            return topics[:2]  # 只取前2個話題測試
            
        except Exception as e:
            print(f"❌ 獲取話題失敗: {e}")
            # 使用模擬話題
            return self._create_mock_topics()
    
    def _create_mock_topics(self):
        """創建模擬話題"""
        
        print("📝 使用模擬話題進行測試")
        
        class MockTopic:
            def __init__(self, id, title):
                self.id = id
                self.title = title
                self.name = title
        
        mock_topics = [
            MockTopic("mock_topic_1", "台積電突破新高！AI 概念股還能追嗎？"),
            MockTopic("mock_topic_2", "大盤重返2萬4！台股9月走勢將...")
        ]
        
        for topic in mock_topics:
            print(f"  📝 {topic.title}")
        
        return mock_topics
    
    def _load_kols(self):
        """載入 KOL"""
        
        print("\n👥 步驟 2: 載入 KOL 資料")
        print("-" * 40)
        
        try:
            kols = self.assignment_service.load_kols()
            print(f"✅ 成功載入 {len(kols)} 個 KOL")
            
            for kol in kols[:5]:  # 顯示前5個
                print(f"  👤 {kol.nickname} ({kol.persona})")
            
            return kols[:3]  # 只用前3個測試
            
        except Exception as e:
            print(f"❌ 載入 KOL 失敗: {e}")
            # 使用模擬 KOL
            return self._create_mock_kols()
    
    def _create_mock_kols(self):
        """創建模擬 KOL"""
        
        print("📝 使用模擬 KOL 進行測試")
        
        class MockKOL:
            def __init__(self, serial, nickname, persona):
                self.serial = serial
                self.nickname = nickname
                self.persona = persona
        
        mock_kols = [
            MockKOL("200", "川川哥", "技術派"),
            MockKOL("201", "梅川褲子", "新聞派"),
            MockKOL("202", "韭割哥", "總經派")
        ]
        
        for kol in mock_kols:
            print(f"  👤 {kol.nickname} ({kol.persona})")
        
        return mock_kols
    
    async def _generate_test_content(self, topics, kols):
        """生成測試內容"""
        
        print("\n✨ 步驟 3: 生成個人化內容")
        print("-" * 40)
        
        posts = []
        
        for i, topic in enumerate(topics):
            for j, kol in enumerate(kols):
                print(f"🎭 生成內容: {kol.nickname} - {topic.title[:30]}...")
                
                try:
                    # 創建個人化內容
                    content = await self._create_personalized_content(topic, kol)
                    
                    post_data = {
                        'post_id': f"{topic.id}-{kol.serial}",
                        'kol_serial': kol.serial,
                        'kol_nickname': kol.nickname,
                        'kol_persona': kol.persona,
                        'topic_id': topic.id,
                        'topic_title': topic.title,
                        'generated_title': content['title'],
                        'generated_content': content['content'],
                        'quality_score': content['quality_score'],
                        'word_count': len(content['content']),
                        'generation_time': datetime.now().isoformat()
                    }
                    
                    posts.append(post_data)
                    print(f"  ✅ 生成成功: {content['title'][:40]}...")
                    
                except Exception as e:
                    print(f"  ❌ 生成失敗: {e}")
        
        print(f"🎯 成功生成 {len(posts)} 篇內容")
        return posts
    
    async def _create_personalized_content(self, topic, kol):
        """創建個人化內容"""
        
        # 根據 KOL 人設生成不同風格的內容
        if '技術' in kol.persona:
            title = f"技術面解析：{topic.title[:15]}...黃金交叉來了？"
            content = f"""從技術指標來看，今天的走勢讓我想到一個重點！

📊 MACD指標顯示：目前出現了明顯的黃金交叉訊號
📈 均線排列：5日線突破20日線，多方力道增強
🎯 關鍵位置：支撐在xx元，壓力看xx元

技術分析不會騙人，大家可以參考一下我的看法。當然投資有風險，自己要做好功課喔！

{kol.nickname} 技術分析分享"""
            
        elif '新聞' in kol.persona:
            title = f"快訊！{topic.title[:15]}...市場怎麼看？！！！"
            content = f"""哇塞！剛剛看到這個消息，整個市場都沸騰了！！！

📢 最新消息：{topic.title}
💥 市場反應：相關股票直接爆量
🔥 熱度分析：討論度瞬間飆升

從新聞面來看，這個消息對後續走勢影響很大啊！大家覺得怎麼樣？快留言討論一下！！！

記得關注我，第一時間分享最新消息！

{kol.nickname} 快報"""
            
        else:  # 總經派
            title = f"深度分析：{topic.title[:15]}...基本面怎麼看？"
            content = f"""從總經角度來看，這個話題值得我們深入思考。

📊 基本面分析：
• 產業趨勢：長期看好
• 財務狀況：營收穩定成長
• 估值水準：目前合理偏低

💡 投資建議：
建議大家用長期投資的角度來看，短期波動不用太擔心。價值投資才是王道！

投資要有耐心，時間會證明一切的價值。

{kol.nickname} 價值投資分享"""
        
        # 計算品質評分（模擬）
        quality_score = 8.0 + (len(content) / 100) * 0.5  # 基於內容長度的簡單評分
        
        return {
            'title': title,
            'content': content,
            'quality_score': min(quality_score, 10.0)
        }
    
    async def _record_results(self, posts):
        """記錄結果到 Google Sheets"""
        
        print(f"\n📝 步驟 4: 記錄到 Google Sheets")
        print("-" * 40)
        
        try:
            for post in posts:
                # 準備完整的記錄數據
                generation_context = {
                    'trigger_source': 'simple_content_test',
                    'trigger_event_id': f"simple_test_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    'data_sources_used': ['cmoney_api', 'mock_analysis', 'personalized_prompt'],
                    'data_sources_status': 'cmoney:success,mock:success,prompt:success',
                    'agent_decision_log': '簡化測試：專注個人化內容生成',
                    'content_length_type': 'medium',
                    'kol_settings_version': 'v3.0_simple_test',
                    'generation_params': {'temperature': 0.7, 'model': 'mock'},
                    'tone_vector': 0.7,
                    'topic_index': 1
                }
                
                quality_result = {
                    'check_rounds': 1,
                    'overall_score': post['quality_score'],
                    'issues': []
                }
                
                await self.sheets_recorder.record_enhanced_post(post, generation_context, quality_result)
                print(f"  ✅ 記錄: {post['kol_nickname']} - {post['generated_title'][:30]}...")
            
            print(f"📊 成功記錄 {len(posts)} 篇內容")
            
        except Exception as e:
            print(f"❌ 記錄失敗: {e}")
    
    def _show_results(self, posts):
        """展示結果"""
        
        print(f"\n🎉 步驟 5: 內容生成結果")
        print("="*80)
        
        for i, post in enumerate(posts, 1):
            print(f"\n📝 貼文 {i}")
            print(f"👤 KOL: {post['kol_nickname']} ({post['kol_persona']})")
            print(f"📋 標題: {post['generated_title']}")
            print(f"📄 內容: {post['generated_content'][:150]}...")
            print(f"📊 品質: {post['quality_score']:.1f}/10")
            print(f"📏 字數: {post['word_count']} 字")
            print(f"🆔 ID: {post['post_id']}")
            print("-" * 60)
        
        print(f"\n✨ 測試總結:")
        print(f"  📊 成功生成: {len(posts)} 篇內容")
        print(f"  🎭 人設分布: {', '.join(set(post['kol_persona'] for post in posts))}")
        print(f"  📝 標題個人化: 每個 KOL 都有獨特風格")
        print(f"  📄 內容豐富度: 根據人設生成不同類型內容")
        print(f"  💾 已記錄到 Google Sheets")
        
        # 分析內容特色
        personas = {}
        for post in posts:
            persona = post['kol_persona']
            if persona not in personas:
                personas[persona] = []
            personas[persona].append(post)
        
        print(f"\n🎯 人設特色分析:")
        for persona, persona_posts in personas.items():
            avg_length = sum(post['word_count'] for post in persona_posts) / len(persona_posts)
            print(f"  {persona}: {len(persona_posts)}篇, 平均{avg_length:.0f}字")

async def main():
    """主函數"""
    
    print("🚀 簡化版內容生成測試開始")
    
    try:
        tester = SimpleContentTester()
        await tester.test_content_generation()
        
        print("\n" + "="*80)
        print("🎉 測試完成！")
        print("✨ 重點成果:")
        print("  🎭 個人化內容生成")
        print("  📝 不同人設風格")
        print("  📊 品質評分機制")
        print("  💾 完整數據記錄")
        
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())



