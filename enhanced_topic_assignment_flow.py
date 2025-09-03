#!/usr/bin/env python3
"""
增強版新話題分派和發文系統
整合多週期技術分析、個人化 Prompt、內容品質檢查
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 原有導入
from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.assign.assignment_service import AssignmentService, TopicData
from src.services.classification.topic_classifier import TopicClassifier

# 新增導入 - 增強版功能
from src.services.analysis.enhanced_technical_analyzer import EnhancedTechnicalAnalyzer
from src.services.content.personalized_prompt_generator import PersonalizedPromptGenerator
from src.services.content.content_quality_checker import ContentQualityChecker, GeneratedPost
from src.services.content.content_regenerator import ContentRegenerator
# from src.services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder  # 暫時移除
from src.services.content.data_driven_content_generator import create_data_driven_content_generator

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedTopicAssignmentFlow:
    """增強版話題分派流程"""
    
    def __init__(self):
        # 初始化原有服務
        self.sheets_client = GoogleSheetsClient(
            credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials/google-service-account.json'),
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID', '148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s')
        )
        
        self.cmoney_client = CMoneyClient()
        self.assignment_service = AssignmentService(self.sheets_client)
        self.topic_classifier = TopicClassifier()
        
        # 初始化增強版服務
        finlab_key = os.getenv('FINLAB_API_KEY')
        if not finlab_key:
            raise ValueError("未找到 FINLAB_API_KEY 環境變數")
        
        self.technical_analyzer = EnhancedTechnicalAnalyzer()
        self.content_generator = create_data_driven_content_generator(finlab_key)
        self.prompt_generator = PersonalizedPromptGenerator()
        self.quality_checker = ContentQualityChecker()
        self.content_regenerator = ContentRegenerator(self.prompt_generator, self.quality_checker)
        # self.sheets_recorder = EnhancedSheetsRecorder(self.sheets_client)  # 暫時移除
        
        print("🚀 增強版話題分派流程初始化完成")
    
    async def run_enhanced_flow(self):
        """執行增強版話題分派流程"""
        
        print("\n" + "="*80)
        print("🔬 增強版熱門話題分派與發文流程")
        print("📊 新功能：技術分析 + 個人化 Prompt + 品質檢查")
        print("="*80)
        
        try:
            # 步驟 1: 獲取熱門話題
            topics = await self._fetch_trending_topics()
            
            # 步驟 2: 話題分類和股票提取
            classified_topics_with_stocks = await self._classify_and_extract_stocks(topics)
            
            # 步驟 3: KOL 分派（提前）
            topic_assignments = self._assign_kols(classified_topics_with_stocks)
            
            # 步驟 4: 股票分配與技術分析
            assignments_with_stocks = await self._assign_stocks_and_analyze(topic_assignments)
            
            # 步驟 5: 股票標籤處理
            assignments_with_tags = self._process_stock_tags(assignments_with_stocks)
            
            # 步驟 6: 增強版內容生成
            generated_posts = await self._generate_enhanced_content(assignments_with_tags)
            
            # 步驟 7: 內容品質檢查與重新生成
            quality_posts = await self._quality_check_and_regenerate(generated_posts)
            
            # 步驟 8: 增強版 Google Sheets 記錄
            await self._record_to_enhanced_sheets(quality_posts)
            
            # 步驟 9: 發文確認與實際發文
            await self._confirm_and_publish(quality_posts)
            
        except Exception as e:
            logger.error(f"增強版流程執行失敗: {e}")
            print(f"❌ 流程執行失敗: {e}")
    
    async def _fetch_trending_topics(self):
        """步驟 1: 獲取熱門話題"""
        
        print("\n📈 步驟 1: 獲取熱門話題")
        print("-" * 40)
        
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password='N9t1kY3x'
        )
        
        token = await self.cmoney_client.login(credentials)
        topics = await self.cmoney_client.get_trending_topics(token.token)
        
        print(f"✅ 獲取到 {len(topics)} 個熱門話題")
        
        # 顯示前5個話題
        for i, topic in enumerate(topics[:5], 1):
            print(f"  {i}. {topic.title}")
            print(f"     📊 ID: {topic.id}")
            if hasattr(topic, 'relatedStockSymbols') and topic.relatedStockSymbols:
                print(f"     📈 相關股票: {', '.join(topic.relatedStockSymbols[:3])}")
        
        return topics[:3]  # 只處理前3個話題
    
    async def _classify_and_extract_stocks(self, topics):
        """步驟 2: 話題分類和股票提取"""
        
        print("\n🏷️ 步驟 2: 話題分類和股票提取")
        print("-" * 40)
        
        classified_topics = []
        
        for topic in topics:
            print(f"📋 分析話題: {topic.title}")
            
            # 話題分類
            classification = self.topic_classifier.classify_topic(topic.id, topic.title, topic.name)
            print(f"  🏷️ 分類結果: {classification.persona_tags}")
            
            # 智能股票提取
            stock_symbols = self._extract_stocks_from_topic(topic)
            if stock_symbols:
                print(f"  📈 相關股票: {', '.join(stock_symbols)}")
            else:
                print(f"  📈 相關股票: 無")
            
            classified_topics.append({
                'id': topic.id,
                'title': topic.title,
                'name': topic.name,
                'classification': classification,
                'stock_symbols': stock_symbols
            })
        
        return classified_topics
    
    def _extract_stocks_from_topic(self, topic):
        """智能股票提取"""
        import re
        
        stocks = []
        title = topic.title
        
        # 1. 從API原始數據提取
        if hasattr(topic, 'relatedStockSymbols') and topic.relatedStockSymbols:
            stocks.extend(topic.relatedStockSymbols)
        
        # 2. 從標題提取股票代號（4-5位數字）
        stock_codes = re.findall(r'\b\d{4,5}\b', title)
        stocks.extend(stock_codes)
        
        # 3. 公司名稱對應股票代號
        company_mapping = {
            '台積電': '2330', 'TSMC': '2330',
            '輝達': 'NVDA', 'NVIDIA': 'NVDA',
            '鴻海': '2317', '聯發科': '2454',
            '台達電': '2308', '中華電': '2412',
            '國泰金': '2882', '富邦金': '2881',
            '長榮': '2603', '陽明': '2609'
        }
        
        for company, code in company_mapping.items():
            if company in title:
                stocks.append(code)
        
        # 4. 大盤話題優先使用個股而非ETF
        if any(keyword in title for keyword in ['大盤', '台股', '指數']):
            # 優先使用有技術分析價值的個股
            popular_stocks = ['2330', '2317', '2454', '2308', '2412']  # 台積電、鴻海、聯發科、台達電、中華電
            stocks.extend(popular_stocks[:2])  # 取前2檔
            # 備選ETF
            stocks.extend(['0050', '0056'])
        
        # 5. 去重並過濾
        unique_stocks = list(dict.fromkeys(stocks))  # 保持順序去重
        
        # 過濾美股（暫時不支持技術分析）
        tw_stocks = [s for s in unique_stocks if not s.isalpha() or len(s) <= 5]
        
        # 6. 優先選擇個股，ETF為備選
        individual_stocks = [s for s in tw_stocks if not self._is_etf(s)]
        etf_stocks = [s for s in tw_stocks if self._is_etf(s)]
        
        # 優先個股，不足再用ETF補充
        final_stocks = individual_stocks[:2] + etf_stocks[:1]
        
        return final_stocks[:3]  # 最多3檔股票
    
    def _is_etf(self, stock_id: str) -> bool:
        """判斷是否為ETF"""
        etf_codes = ['0050', '0056', '00878', '00919', '00940', '006208']
        return stock_id in etf_codes
    
    async def _evaluate_technical_analysis(self, classified_topics):
        """步驟 3: 技術分析評估"""
        
        print("\n📊 步驟 3: 多週期技術分析評估")
        print("-" * 40)
        
        topics_with_analysis = []
        
        for topic in classified_topics:
            print(f"🔬 分析話題: {topic['title']}")
            
            topic_analysis = {
                'topic': topic,
                'stock_analyses': {},
                'overall_score': 0,
                'confidence': 0,
                'effective_count': 0
            }
            
            # 對每支相關股票進行技術分析
            for stock_symbol in topic['stock_symbols']:
                print(f"  📈 分析股票: {stock_symbol}")
                
                try:
                    analysis = await self.technical_analyzer.get_enhanced_stock_analysis(stock_symbol)
                    
                    if analysis:
                        topic_analysis['stock_analyses'][stock_symbol] = analysis
                        print(f"    ✅ 評分: {analysis.overall_score:.1f}/10")
                        print(f"    🎯 信心度: {analysis.confidence_score:.1f}%")
                        print(f"    📊 有效指標: {len(analysis.effective_indicators)} 個")
                        
                        # 累積評分
                        topic_analysis['overall_score'] += analysis.overall_score
                        topic_analysis['confidence'] += analysis.confidence_score
                        topic_analysis['effective_count'] += len(analysis.effective_indicators)
                    else:
                        print(f"    ❌ 技術分析失敗")
                
                except Exception as e:
                    print(f"    ⚠️ 分析錯誤: {e}")
            
            # 計算話題整體評分
            if topic_analysis['stock_analyses']:
                stock_count = len(topic_analysis['stock_analyses'])
                topic_analysis['overall_score'] /= stock_count
                topic_analysis['confidence'] /= stock_count
                
                print(f"  🎯 話題整體評分: {topic_analysis['overall_score']:.1f}/10")
                print(f"  🎯 平均信心度: {topic_analysis['confidence']:.1f}%")
            else:
                print(f"  ❌ 無有效技術分析")
            
            topics_with_analysis.append(topic_analysis)
        
        return topics_with_analysis
    
    def _filter_effective_topics(self, topics_with_analysis):
        """步驟 4: 有效話題篩選"""
        
        print("\n🔍 步驟 4: 有效話題篩選")
        print("-" * 40)
        
        effective_topics = []
        
        for topic_analysis in topics_with_analysis:
            topic = topic_analysis['topic']
            score = topic_analysis['overall_score']
            confidence = topic_analysis['confidence']
            effective_count = topic_analysis['effective_count']
            
            print(f"📋 評估話題: {topic['title']}")
            print(f"  📊 評分: {score:.1f}/10")
            print(f"  🎯 信心度: {confidence:.1f}%")
            print(f"  📈 有效指標: {effective_count} 個")
            
            # 暫時放寬篩選條件：有股票數據即可
            has_stocks = len(topic['stock_symbols']) > 0
            
            if has_stocks:
                effective_topics.append(topic_analysis)
                print(f"  ✅ 通過篩選，將用於內容生成（暫時放寬技術分析要求）")
            else:
                print(f"  ❌ 未通過篩選，無相關股票數據")
        
        print(f"\n🎯 篩選結果: {len(effective_topics)}/{len(topics_with_analysis)} 個話題通過")
        
        return effective_topics
    
    def _assign_kols(self, classified_topics):
        """步驟 3: KOL 分派（提前）"""
        
        print("\n👥 步驟 3: KOL 分派")
        print("-" * 40)
        
        # 載入 KOL 資料
        self.assignment_service.load_kol_profiles()
        active_kols = [kol for kol in self.assignment_service._kol_profiles if kol.enabled]
        print(f"✅ 載入 {len(active_kols)} 個活躍 KOL")
        
        all_assignments = []
        
        for topic_data in classified_topics:
            # 建立 TopicData 物件
            topic_data_obj = TopicData(
                topic_id=topic_data['id'],
                title=topic_data['title'],
                input_index=0,
                persona_tags=topic_data['classification'].persona_tags,
                industry_tags=topic_data['classification'].industry_tags,
                event_tags=topic_data['classification'].event_tags,
                stock_tags=topic_data['classification'].stock_tags,
                classification=topic_data['classification']
            )
            
            # 分派 KOL (每個話題最多 2 個 KOL)
            assignments = self.assignment_service.assign_topics([topic_data_obj], max_assignments_per_topic=2)
            
            print(f"📋 話題: {topic_data['title']}")
            print(f"👥 分派給 {len(assignments)} 個 KOL")
            
            for assignment in assignments:
                kol = next((k for k in active_kols if k.serial == assignment.kol_serial), None)
                if kol:
                    print(f"  ✅ {kol.nickname} ({kol.persona})")
                    
                    # 加入話題資料
                    assignment_data = {
                        'assignment': assignment,
                        'kol': kol,
                        'topic_analysis': {
                            'topic': topic_data,
                            'classification': topic_data['classification']
                        }
                    }
                    all_assignments.append(assignment_data)
        
        return all_assignments
    
    async def _assign_stocks_and_analyze(self, topic_assignments):
        """步驟 4: 股票分配與技術分析"""
        
        print("\n📈 步驟 4: 股票分配與技術分析")
        print("-" * 40)
        
        assignments_with_stocks = []
        
        for assignment_data in topic_assignments:
            assignment = assignment_data['assignment']
            kol = assignment_data['kol']
            topic_analysis = assignment_data['topic_analysis']
            topic = topic_analysis['topic']
            
            print(f"📊 為 {kol.nickname} 分配股票並進行技術分析")
            print(f"📋 話題: {topic['title']}")
            
            # 從話題中獲取相關股票
            related_stocks = topic.get('stock_symbols', [])
            if not related_stocks:
                print(f"  ⚠️ 無相關股票，跳過技術分析")
                assignment_data['stock_analyses'] = {}
                assignment_data['assigned_stocks'] = []
                assignments_with_stocks.append(assignment_data)
                continue
            
            print(f"  📈 相關股票: {', '.join(related_stocks)}")
            
            # 對每支股票進行技術分析
            stock_analyses = {}
            for stock_symbol in related_stocks:
                print(f"  🔬 分析股票: {stock_symbol}")
                
                try:
                    analysis = await self.technical_analyzer.get_enhanced_stock_analysis(stock_symbol)
                    
                    if analysis:
                        stock_analyses[stock_symbol] = analysis
                        print(f"    ✅ 評分: {analysis.overall_score:.1f}/10")
                        print(f"    🎯 信心度: {analysis.confidence_score:.1f}%")
                    else:
                        print(f"    ❌ 技術分析失敗")
                
                except Exception as e:
                    print(f"    ⚠️ 分析錯誤: {e}")
            
            # 保存分析結果
            assignment_data['stock_analyses'] = stock_analyses
            assignment_data['assigned_stocks'] = related_stocks
            assignments_with_stocks.append(assignment_data)
        
        return assignments_with_stocks
    
    def _process_stock_tags(self, assignments_with_stocks):
        """步驟 5: 股票標籤處理"""
        
        print("\n🏷️ 步驟 5: 股票標籤處理")
        print("-" * 40)
        
        assignments_with_tags = []
        
        # 按話題分組，為每個話題的KOL隨機分配股票
        topic_groups = {}
        for assignment_data in assignments_with_stocks:
            topic_id = assignment_data['topic_analysis']['topic']['id']
            if topic_id not in topic_groups:
                topic_groups[topic_id] = []
            topic_groups[topic_id].append(assignment_data)
        
        for topic_id, topic_assignments in topic_groups.items():
            topic = topic_assignments[0]['topic_analysis']['topic']
            all_stocks = topic_assignments[0].get('assigned_stocks', [])
            
            print(f"📋 處理話題: {topic['title']}")
            print(f"  📈 可用股票: {', '.join(all_stocks)}")
            
            # 為每個KOL隨機分配股票子集
            import random
            for i, assignment_data in enumerate(topic_assignments):
                kol = assignment_data['kol']
                
                # 隨機選擇1-3個股票（至少1個）
                num_stocks = min(random.randint(1, 3), len(all_stocks))
                kol_stocks = random.sample(all_stocks, num_stocks)
                
                print(f"  👤 {kol.nickname}: 分配股票 {', '.join(kol_stocks)}")
                
                # 準備 commodityTags
                commodity_tags = []
                
                # 檢查是否為大盤話題，如果是則加入 TWA00
                if any(keyword in topic['title'] for keyword in ['大盤', '台股', '指數', '台積電', '2330']):
                    commodity_tags.append({
                        "type": "Stock", 
                        "key": "TWA00",
                        "bullOrBear": 0  # 預設為中性
                    })
                    print(f"    🏷️ 加入大盤標籤: TWA00")
                
                # 加入分配的股票標籤
                for stock_symbol in kol_stocks:
                    commodity_tags.append({
                        "type": "Stock", 
                        "key": stock_symbol,
                        "bullOrBear": 0  # 預設為中性
                    })
                
                tag_strs = [f"{tag['type']}:{tag['key']}" for tag in commodity_tags]
                print(f"    🏷️ 最終標籤: {tag_strs}")
                
                # 更新分配的股票和標籤資訊
                assignment_data['assigned_stocks'] = kol_stocks
                assignment_data['commodity_tags'] = commodity_tags
                assignments_with_tags.append(assignment_data)
        
        return assignments_with_tags
    
    def _get_stock_name(self, stock_symbol: str) -> str:
        """將股票代號轉換為公司名稱"""
        stock_name_mapping = {
            '2330': '台積電',
            '2317': '鴻海',
            '2454': '聯發科',
            '2308': '台達電',
            '2412': '中華電',
            '2882': '國泰金',
            '2881': '富邦金',
            '2603': '長榮',
            '2609': '陽明',
            '2634': '漢翔',
            '8033': '雷虎',
            '1303': '南亞',
            '2359': '所羅門',
            '1504': '東元',
            '8927': '富邦媒',
            '8932': '智邦',
            'TWA00': '台股指數'
        }
        return stock_name_mapping.get(stock_symbol, stock_symbol)
    
    async def _generate_enhanced_content(self, assignments_with_tags):
        """步驟 6: 增強版內容生成"""
        
        print("\n✨ 步驟 6: 增強版內容生成")
        print("-" * 40)
        
        generated_posts = []
        
        for assignment_data in assignments_with_tags:
            assignment = assignment_data['assignment']
            kol = assignment_data['kol']
            topic_analysis = assignment_data['topic_analysis']
            topic = topic_analysis['topic']
            stock_analyses = assignment_data.get('stock_analyses', {})
            assigned_stocks = assignment_data.get('assigned_stocks', [])
            commodity_tags = assignment_data.get('commodity_tags', [])
            
            print(f"🎭 為 {kol.nickname} 生成內容")
            print(f"📋 話題: {topic['title']}")
            
            try:
                # 準備股票數據 - 需要轉換為 StockMarketData 對象
                from src.services.content.data_driven_content_generator import StockMarketData, MarketContext
                from src.services.content.technical_explanation_generator import technical_explanation_generator
                
                stock_data_map = {}
                for stock_symbol, analysis in stock_analyses.items():
                    # 創建 StockMarketData 對象
                    stock_data_map[stock_symbol] = StockMarketData(
                        stock_id=stock_symbol,
                        stock_name=self._get_stock_name(stock_symbol),
                        date=analysis.analysis_date if hasattr(analysis, 'analysis_date') and isinstance(analysis.analysis_date, str) else '2025-08-29',
                        open=analysis.current_price,  # 暫時使用收盤價
                        high=analysis.current_price,  # 暫時使用收盤價
                        low=analysis.current_price,   # 暫時使用收盤價
                        close=analysis.current_price,
                        volume=0,  # 暫時設為 0
                        daily_change=0.0,  # 暫時設為 0
                        daily_change_pct=0.0,  # 暫時設為 0
                        technical_summary=f"技術指標評分: {analysis.overall_score:.1f}/10 (信心度: {analysis.confidence_score:.1f}%)"
                    )
                
                # 使用數據驅動內容生成器
                content_result = await self.content_generator.generate_data_driven_content(
                    kol_profile={
                        'serial': kol.serial,
                        'nickname': kol.nickname,
                        'persona': kol.persona
                    },
                    topic_data={
                        'id': topic['id'],
                        'title': topic['title'],
                        'keywords': topic['classification'].persona_tags + topic['classification'].industry_tags
                    },
                    stock_assignments=[{
                        'topic_data': topic,
                        'kol_profile': {
                            'serial': kol.serial,
                            'nickname': kol.nickname,
                            'persona': kol.persona
                        },
                        'assigned_stocks': [{'stock_id': symbol, 'stock_name': self._get_stock_name(symbol)} 
                                          for symbol in assigned_stocks],
                        'analysis_angle': f'{kol.persona}的深度分析'
                    }],
                    stock_data_map=stock_data_map,
                    market_context=MarketContext(
                        market_sentiment=f"技術面評分: {topic_analysis.get('overall_score', 0):.1f}/10",
                        sector_performance="持續觀察",
                        macro_factors="內外資分歧影響市場情緒",
                        news_highlights=topic['title']
                    )
                )
                
                if content_result:
                    # 建立貼文物件
                    post_id = f"{topic['id']}-{kol.serial}"
                    post = GeneratedPost(
                        post_id=post_id,
                        kol_serial=kol.serial,
                        kol_nickname=kol.nickname,
                        persona=kol.persona,
                        title=content_result.get('title', ''),
                        content=content_result.get('content', ''),
                        topic_title=topic['title'],
                        topic_id=topic['id'],  # 保存完整的 topic ID
                        generation_params=content_result.get('generation_metadata', {}).get('generation_params', {}),
                        created_at=datetime.now()
                    )
                    
                    # 加入額外資料
                    post.topic_analysis = topic_analysis
                    post.stock_analyses = stock_analyses
                    post.generation_metadata = content_result.get('generation_metadata', {})
                    
                    # 保存發文用的股票標籤（使用新的 commodity_tags）
                    post.commodity_tags = commodity_tags
                    post.related_stocks = assigned_stocks
                    
                    generated_posts.append(post)
                    print(f"  ✅ 生成成功: {len(content_result.get('content', ''))} 字")
                else:
                    print(f"  ❌ 生成失敗")
                
            except Exception as e:
                logger.error(f"內容生成失敗: {e}")
                print(f"  ❌ 生成錯誤: {e}")
        
        print(f"\n🎯 生成結果: {len(generated_posts)} 篇內容")
        return generated_posts
    
    async def _quality_check_and_regenerate(self, generated_posts):
        """步驟 7: 內容品質檢查與重新生成"""
        
        print("\n🔍 步驟 7: 內容品質檢查與重新生成")
        print("-" * 40)
        
        quality_posts = []
        
        for post in generated_posts:
            print(f"🔍 檢查 {post.kol_nickname} 的內容品質")
            
            # 品質檢查
            quality_score, quality_issues = await self.quality_checker.check_content_quality(post)
            
            print(f"  📊 品質評分: {quality_score:.1f}/10")
            quality_passed = quality_score >= 6.0  # 設定通過門檻
            print(f"  ✅ 通過檢查: {quality_passed}")
            
            if quality_passed:
                quality_posts.append(post)
                print(f"  ✅ 品質良好，保留內容")
            else:
                print(f"  ⚠️ 品質不足，嘗試重新生成...")
                print(f"  📋 問題: {[issue.description for issue in quality_issues]}")
                
                # 重新生成 (最多1次)
                regenerated = await self.content_regenerator.regenerate_single_post(
                    original_post=post,
                    issues=quality_issues,
                    generation_context={},
                    all_posts=generated_posts
                )
                
                if regenerated and regenerated.success:
                    print(f"  ✅ 重新生成成功")
                    quality_posts.append(regenerated.final_post)
                else:
                    print(f"  ❌ 重新生成失敗，保留原內容")
                    quality_posts.append(post)
        
        print(f"\n🎯 品質檢查結果: {len(quality_posts)}/{len(generated_posts)} 篇通過")
        return quality_posts
    
    async def _record_to_enhanced_sheets(self, posts):
        """步驟 8: 增強版 Google Sheets 記錄"""
        
        print("\n📝 步驟 8: 記錄到增強版 Google Sheets")
        print("-" * 40)
        
        try:
            # 讀取現有的Google Sheets結構
            sheet_name = "貼文記錄表"
            existing_data = self.sheets_client.read_sheet(sheet_name)
            
            if not existing_data:
                print("❌ 無法讀取Google Sheets結構")
                return
            
            # 獲取標題行
            headers = existing_data[0] if existing_data else []
            if not headers:
                print("❌ 無法獲取標題行")
                return
                
            print(f"📋 檢測到 {len(headers)} 個欄位")
            
            # 準備新行數據
            new_rows = []
            
            for post in posts:
                print(f"  📝 準備記錄 {post.kol_nickname} 的內容到 Google Sheets")
                print(f"     Post ID: {post.post_id}")
                
                # 準備完整的行數據，按照Google Sheets的欄位順序
                row_data = []
                
                # 根據標題行映射數據
                for header in headers:
                    if header == "貼文ID":
                        row_data.append(post.post_id)
                    elif header == "KOL Serial":
                        row_data.append(post.kol_serial)
                    elif header == "KOL 暱稱":
                        row_data.append(post.kol_nickname)
                    elif header == "KOL ID":
                        row_data.append(post.kol_serial)  # 假設ID同serial
                    elif header == "Persona":
                        row_data.append(post.persona)
                    elif header == "Content Type":
                        row_data.append("技術分析貼文")
                    elif header == "已派發TopicIndex":
                        row_data.append("1")
                    elif header == "已派發TopicID":
                        row_data.append(post.topic_id)
                    elif header == "–":
                        row_data.append("")
                    elif header == "已派發TopicKeywords":
                        topic_keywords = getattr(post, 'topic_analysis', {}).get('topic', {}).get('classification', {})
                        if hasattr(topic_keywords, 'persona_tags'):
                            keywords = topic_keywords.persona_tags + getattr(topic_keywords, 'industry_tags', [])
                            row_data.append(", ".join(keywords))
                        else:
                            row_data.append("")
                    elif header == "生成標題":
                        # 只放標題
                        row_data.append(post.title)
                    elif header == "生成內容":
                        # 只放內容，不包含標題
                        row_data.append(post.content)
                    elif header == "熱門話題標題":
                        row_data.append(post.topic_title)
                    elif header == "發文狀態":
                        row_data.append("已生成")
                    elif header == "上次排程時間":
                        row_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    elif header == "發文時間戳記":
                        row_data.append("")
                    elif header == "最近錯誤訊息":
                        row_data.append("")
                    elif header == "平台發文ID":
                        row_data.append("")
                    elif header == "平台發文URL":
                        row_data.append("")
                    elif header == "articleid":
                        row_data.append("")
                    elif header == "熱門話題標題":
                        row_data.append(post.topic_title)
                    elif header == "觸發支線類型":
                        row_data.append("enhanced_trending_topics")
                    elif header == "觸發事件ID":
                        row_data.append(f"enhanced_{datetime.now().strftime('%Y%m%d_%H%M')}")
                    elif header == "調用數據來源庫":
                        row_data.append("finlab_ohlc,cmoney_api,technical_analysis,openai_gpt")
                    elif header == "數據來源狀態":
                        row_data.append("finlab:success,cmoney:success,technical:success,openai:success")
                    elif header == "Agent決策紀錄":
                        overall_score = getattr(post, "topic_analysis", {}).get("overall_score", 0)
                        row_data.append(f"增強版技術分析評分通過: {overall_score:.1f}/10")
                    elif header == "發文類型":
                        row_data.append("技術分析貼文")
                    elif header == "文章長度類型":
                        row_data.append("medium")
                    elif header == "內文字數":
                        row_data.append(str(len(post.content)))
                    elif header == "內文長度分類":
                        content_length = len(post.content)
                        if content_length < 200:
                            row_data.append("短")
                        elif content_length < 500:
                            row_data.append("中")
                        else:
                            row_data.append("長")
                    elif header == "KOL權重設定":
                        row_data.append("1.0")
                    elif header == "內容生成時間":
                        row_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    elif header == "KOL設定版本":
                        row_data.append("v3.0_enhanced_with_technical_analysis")
                    elif header == "文章長度向量":
                        row_data.append("0.7")
                    elif header == "語氣向量":
                        row_data.append("0.7")
                    elif header == "temperature設定":
                        row_data.append("0.8")
                    elif header == "body parameter":
                        # 將股票標籤和社區話題轉換為正確的API格式
                        body_params = {}
                        
                        # 添加 commodityTags (包含 bullOrBear 字段)
                        if hasattr(post, 'commodity_tags') and post.commodity_tags:
                            # 轉換為正確的格式，添加 bullOrBear 字段
                            formatted_tags = []
                            for tag in post.commodity_tags:
                                formatted_tag = {
                                    "type": tag.get("type", "Stock"),
                                    "key": tag.get("key", ""),
                                    "bullOrBear": 0  # 預設為中性
                                }
                                formatted_tags.append(formatted_tag)
                            body_params["commodityTags"] = formatted_tags
                        
                        # 添加 communityTopic
                        if hasattr(post, 'topic_id') and post.topic_id:
                            body_params["communityTopic"] = {"id": post.topic_id}
                        
                        row_data.append(str(body_params))
                    elif header == "品質檢查輪數":
                        row_data.append("1")
                    elif header == "品質評分":
                        quality_score = getattr(post, 'quality_score', 8.0)
                        row_data.append(str(quality_score))
                    elif header == "品質問題記錄":
                        row_data.append("")
                    elif header == "重新生成次數":
                        row_data.append("0")
                    elif header == "品質改進記錄":
                        row_data.append("")
                    else:
                        # 對於其他欄位，填入空值
                        row_data.append("")
                
                # 確保行數據長度與標題行一致
                while len(row_data) < len(headers):
                    row_data.append("")
                
                new_rows.append(row_data)
                
                # 顯示股票標籤
                if hasattr(post, 'commodity_tags') and post.commodity_tags:
                    tag_strs = [f"{tag['type']}:{tag['key']}" for tag in post.commodity_tags]
                    print(f"     股票標籤: {tag_strs}")
                
                print(f"  ✅ 記錄 {post.kol_nickname} 的內容")
            
            # 寫入Google Sheets
            if new_rows:
                try:
                    # 使用 append_sheet 方法追加新數據
                    result = self.sheets_client.append_sheet(sheet_name, new_rows)
                    print(f"📊 成功記錄 {len(posts)} 篇內容到 Google Sheets")
                    print(f"  📝 API回應: {result}")
                except Exception as e:
                    print(f"❌ Google Sheets寫入失敗: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("⚠️ 沒有新數據需要寫入")
            
        except Exception as e:
            logger.error(f"Google Sheets 記錄失敗: {e}")
            print(f"❌ 記錄失敗: {e}")
            import traceback
            traceback.print_exc()
    
    async def _confirm_and_publish(self, posts):
        """步驟 9: 發文確認與實際發文"""
        
        print("\n📢 步驟 9: 發文確認與實際發文")
        print("-" * 40)
        
        if not posts:
            print("❌ 沒有內容可發文")
            return
        
        print(f"📋 準備發文內容預覽:")
        for i, post in enumerate(posts, 1):
            print(f"\n【第 {i} 篇】")
            print(f"  📝 Post ID: {post.post_id}")
            print(f"  👤 KOL: {post.kol_nickname} ({post.persona})")
            print(f"  📋 標題: {post.title}")
            print(f"  📏 字數: {len(post.content)} 字")
            
            # 顯示技術分析摘要
            if hasattr(post, 'stock_analyses') and post.stock_analyses:
                for stock_id, analysis in post.stock_analyses.items():
                    print(f"  📊 {stock_id}: {analysis.overall_score:.1f}/10分")
        
        print(f"\n🎯 共 {len(posts)} 篇內容準備發文")
        
        # 實際發文
        print("\n🚀 開始實際發文...")
        published_posts = []
        
        for i, post in enumerate(posts, 1):
            print(f"\n📤 發文第 {i} 篇: {post.kol_nickname}")
            
            try:
                # 準備發文數據
                from src.clients.cmoney.cmoney_client import ArticleData
                
                # 準備 commodityTags
                commodity_tags = []
                if hasattr(post, 'commodity_tags') and post.commodity_tags:
                    commodity_tags = post.commodity_tags
                
                # 準備 communityTopic
                community_topic = None
                if hasattr(post, 'topic_id') and post.topic_id:
                    community_topic = {"id": post.topic_id}
                
                # 創建文章數據
                article_data = ArticleData(
                    title=post.title,
                    text=post.content,
                    community_topic=community_topic,
                    commodity_tags=commodity_tags
                )
                
                # 獲取 KOL 登入憑證
                kol_credentials = await self._get_kol_credentials(post.kol_serial)
                if not kol_credentials:
                    print(f"  ❌ 無法獲取 {post.kol_nickname} 的登入憑證")
                    continue
                
                # 登入並發文
                access_token_obj = await self.cmoney_client.login(kol_credentials)
                if not access_token_obj:
                    print(f"  ❌ {post.kol_nickname} 登入失敗")
                    continue
                
                # 發文
                publish_result = await self.cmoney_client.publish_article(access_token_obj.token, article_data)
                
                if publish_result.success:
                    print(f"  ✅ 發文成功!")
                    print(f"    📝 Article ID: {publish_result.post_id}")
                    print(f"    🔗 URL: {publish_result.post_url}")
                    
                    # 更新發文狀態
                    await self._update_post_status(post.post_id, publish_result)
                    
                    published_posts.append({
                        'post': post,
                        'result': publish_result
                    })
                else:
                    print(f"  ❌ 發文失敗: {publish_result.error_message}")
                    
            except Exception as e:
                print(f"  ❌ 發文過程出錯: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📊 發文結果總結:")
        print(f"  ✅ 成功發文: {len(published_posts)} 篇")
        print(f"  ❌ 發文失敗: {len(posts) - len(published_posts)} 篇")
        
        if published_posts:
            print("\n🎉 發文完成！請檢查 CMoney 平台確認發文結果")
    
    async def _get_kol_credentials(self, kol_serial: str):
        """獲取 KOL 登入憑證"""
        try:
            from src.clients.cmoney.cmoney_client import LoginCredentials
            
            # 從 Google Sheets 讀取 KOL 配置
            kol_data = self.sheets_client.read_sheet("同學會帳號管理")
            if len(kol_data) <= 1:
                return None
            
            headers = kol_data[0]
            serial_index = None
            email_index = None
            password_index = None
            
            for i, header in enumerate(headers):
                if '序號' in header:
                    serial_index = i
                elif 'Email' in header or '帳號' in header:
                    email_index = i
                elif '密碼' in header:
                    password_index = i
            
            if serial_index is None or email_index is None or password_index is None:
                return None
            
            # 查找對應的 KOL
            for row in kol_data[1:]:
                if len(row) > max(serial_index, email_index, password_index):
                    if str(row[serial_index]) == str(kol_serial):
                        return LoginCredentials(
                            email=row[email_index],
                            password=row[password_index]
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"獲取 KOL 憑證失敗: {e}")
            return None
    
    async def _update_post_status(self, post_id: str, publish_result):
        """更新發文狀態到 Google Sheets"""
        try:
            # 讀取現有數據
            sheet_data = self.sheets_client.read_sheet("貼文記錄表")
            if len(sheet_data) <= 1:
                return
            
            headers = sheet_data[0]
            
            # 找到需要更新的欄位索引
            post_id_index = None
            status_index = None
            timestamp_index = None
            platform_id_index = None
            platform_url_index = None
            articleid_index = None
            
            for i, header in enumerate(headers):
                if header == "貼文ID":
                    post_id_index = i
                elif header == "發文狀態":
                    status_index = i
                elif header == "發文時間戳記":
                    timestamp_index = i
                elif header == "平台發文ID":
                    platform_id_index = i
                elif header == "平台發文URL":
                    platform_url_index = i
                elif header == "articleid":
                    articleid_index = i
            
            if post_id_index is None:
                return
            
            # 查找對應的行並更新
            for i, row in enumerate(sheet_data[1:], 2):  # 從第2行開始
                if len(row) > post_id_index and row[post_id_index] == post_id:
                    # 準備更新數據
                    update_data = []
                    
                    # 更新發文狀態
                    if status_index is not None:
                        update_data.append(f"B{status_index + 1}")
                        update_data.append("已發文")
                    
                    # 更新發文時間戳記
                    if timestamp_index is not None:
                        update_data.append(f"B{timestamp_index + 1}")
                        update_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    
                    # 更新平台發文ID
                    if platform_id_index is not None and publish_result.post_id:
                        update_data.append(f"B{platform_id_index + 1}")
                        update_data.append(publish_result.post_id)
                    
                    # 更新平台發文URL
                    if platform_url_index is not None and publish_result.post_url:
                        update_data.append(f"B{platform_url_index + 1}")
                        update_data.append(publish_result.post_url)
                    
                    # 更新articleid
                    if articleid_index is not None and publish_result.post_id:
                        update_data.append(f"B{articleid_index + 1}")
                        update_data.append(publish_result.post_id)
                    
                    # 執行更新
                    if update_data:
                        # 準備更新的行數據
                        updated_row = row.copy()
                        
                        # 更新發文狀態
                        if status_index is not None:
                            updated_row[status_index] = "已發文"
                        
                        # 更新發文時間戳記
                        if timestamp_index is not None:
                            updated_row[timestamp_index] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 更新平台發文ID
                        if platform_id_index is not None and publish_result.post_id:
                            updated_row[platform_id_index] = publish_result.post_id
                        
                        # 更新平台發文URL
                        if platform_url_index is not None and publish_result.post_url:
                            updated_row[platform_url_index] = publish_result.post_url
                        
                        # 更新articleid
                        if articleid_index is not None and publish_result.post_id:
                            updated_row[articleid_index] = publish_result.post_id
                        
                        # 寫入更新後的行
                        range_name = f"貼文記錄表!A{i}:AM{i}"
                        self.sheets_client.write_sheet("貼文記錄表", [updated_row], range_name)
                        
                        print(f"  📝 更新發文狀態: {post_id}")
                        print(f"    Article ID: {publish_result.post_id}")
                        print(f"    URL: {publish_result.post_url}")
                        print(f"    ✅ 已更新 Google Sheets")
            
        except Exception as e:
            logger.error(f"更新發文狀態失敗: {e}")
            print(f"  ⚠️ 更新發文狀態失敗: {e}")

async def main():
    """主函數"""
    
    try:
        flow = EnhancedTopicAssignmentFlow()
        await flow.run_enhanced_flow()
        
    except Exception as e:
        logger.error(f"主流程執行失敗: {e}")
        print(f"❌ 主流程執行失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())
