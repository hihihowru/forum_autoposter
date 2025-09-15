#!/usr/bin/env python3
"""
盤後漲停機器人範例文章生成器
生成三個不同數據組合的範例文章：
1. Serper API + 月營收
2. Serper API + 財報  
3. Serper API + 股價OHLC/成交量變化
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowConfig, WorkflowType
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AfterHoursLimitUpExampleGenerator:
    """盤後漲停範例文章生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.workflow_engine = MainWorkflowEngine()
        logger.info("盤後漲停範例文章生成器初始化完成")
    
    async def generate_example_articles(self):
        """生成三個範例文章"""
        logger.info("開始生成三個範例文章...")
        
        # 範例股票數據
        example_stocks = [
            {
                "stock_id": "4968",
                "stock_name": "立積",
                "change_percent": 9.8,
                "volume_amount": 2.5,  # 2.5億元
                "volume_rank": 15,
                "data_type": "revenue"  # 月營收
            },
            {
                "stock_id": "3491", 
                "stock_name": "昇達科技",
                "change_percent": 9.9,
                "volume_amount": 1.8,  # 1.8億元
                "volume_rank": 25,
                "data_type": "earnings"  # 財報
            },
            {
                "stock_id": "8033",
                "stock_name": "雷虎",
                "change_percent": 9.7,
                "volume_amount": 3.2,  # 3.2億元
                "volume_rank": 8,
                "data_type": "ohlc"  # OHLC/成交量
            }
        ]
        
        generated_articles = []
        
        for i, stock_data in enumerate(example_stocks, 1):
            logger.info(f"生成第 {i} 個範例文章: {stock_data['stock_name']} ({stock_data['data_type']})")
            
            try:
                # 生成文章內容
                article = await self._generate_single_article(stock_data)
                generated_articles.append(article)
                
                logger.info(f"✅ 第 {i} 個範例文章生成完成")
                
            except Exception as e:
                logger.error(f"❌ 第 {i} 個範例文章生成失敗: {e}")
                continue
        
        # 記錄到 Google Sheets
        await self._record_articles_to_sheets(generated_articles)
        
        logger.info(f"🎉 範例文章生成完成，共生成 {len(generated_articles)} 篇文章")
        return generated_articles
    
    async def _generate_single_article(self, stock_data):
        """生成單篇文章"""
        try:
            # 獲取 KOL 設定
            kol_settings = self.workflow_engine.config_manager.get_kol_personalization_settings()
            kol_list = list(kol_settings.keys())
            
            # 隨機選擇一個 KOL
            import random
            kol_serial = random.choice(kol_list)
            kol_config = kol_settings[kol_serial]
            
            # 獲取 Serper API 新聞連結
            news_links = await self.workflow_engine._get_serper_news_links(
                stock_data['stock_id'], 
                stock_data['stock_name']
            )
            
            # 根據數據類型獲取相應的數據
            additional_data = await self._get_additional_data(stock_data)
            
            # 生成文章內容
            content = await self._generate_content_with_data(
                stock_data, kol_config, news_links, additional_data
            )
            
            # 生成標題
            title = await self._generate_title(stock_data, kol_config)
            
            return {
                "stock_id": stock_data['stock_id'],
                "stock_name": stock_data['stock_name'],
                "title": title,
                "content": content,
                "kol_serial": kol_serial,
                "kol_nickname": kol_config.get('persona', '未知'),
                "data_type": stock_data['data_type'],
                "news_links": news_links,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成單篇文章失敗: {e}")
            raise
    
    async def _get_additional_data(self, stock_data):
        """根據數據類型獲取額外數據"""
        data_type = stock_data['data_type']
        
        if data_type == "revenue":
            # 獲取月營收數據
            return await self.workflow_engine._get_finlab_revenue_data(stock_data['stock_id'])
        
        elif data_type == "earnings":
            # 獲取財報數據
            return await self.workflow_engine._get_finlab_earnings_data(stock_data['stock_id'])
        
        elif data_type == "ohlc":
            # 獲取股價OHLC/成交量數據
            return await self.workflow_engine._get_finlab_stock_data(stock_data['stock_id'])
        
        return {}
    
    async def _generate_content_with_data(self, stock_data, kol_config, news_links, additional_data):
        """根據數據類型生成內容"""
        data_type = stock_data['data_type']
        
        # 基礎內容
        base_content = f"{stock_data['stock_name']}({stock_data['stock_id']}) 今日漲停 {stock_data['change_percent']:.1f}%！"
        
        # 根據數據類型添加特定內容
        if data_type == "revenue" and additional_data:
            revenue_content = f"""
月營收表現亮眼：
• 當月營收：{additional_data.get('current_month_revenue_formatted', 'N/A')}
• 月增率：{additional_data.get('mom_growth_pct', 0):.1f}%
• 年增率：{additional_data.get('yoy_growth_pct', 0):.1f}%
• 累計營收：{additional_data.get('ytd_revenue_formatted', 'N/A')}
"""
            base_content += revenue_content
        
        elif data_type == "earnings" and additional_data:
            earnings_content = f"""
財報表現優異：
• EPS：{additional_data.get('eps', 'N/A')}
• 營收：{additional_data.get('revenue_formatted', 'N/A')}
• 毛利率：{additional_data.get('gross_margin', 0):.1f}%
• 營益率：{additional_data.get('operating_margin', 0):.1f}%
"""
            base_content += earnings_content
        
        elif data_type == "ohlc" and additional_data:
            ohlc_content = f"""
技術面表現強勢：
• 開盤價：{additional_data.get('open', 'N/A')}元
• 最高價：{additional_data.get('high', 'N/A')}元
• 最低價：{additional_data.get('low', 'N/A')}元
• 收盤價：{additional_data.get('close', 'N/A')}元
• 成交量：{additional_data.get('volume_formatted', 'N/A')}
• 成交金額：{stock_data['volume_amount']:.2f}億元
"""
            base_content += ohlc_content
        
        # 添加新聞連結
        if news_links:
            base_content += f"\n\n相關新聞連結：\n{news_links}"
        
        return base_content
    
    async def _generate_title(self, stock_data, kol_config):
        """生成標題"""
        # 根據 KOL 風格生成不同標題
        persona = kol_config.get('persona', '未知')
        
        if '技術' in persona:
            return f"{stock_data['stock_name']}技術面突破！"
        elif '八卦' in persona or '爆料' in persona:
            return f"{stock_data['stock_name']}內幕消息曝光！"
        elif '幽默' in persona:
            return f"{stock_data['stock_name']}漲停原因竟然是..."
        else:
            return f"{stock_data['stock_name']}漲停分析"
    
    async def _record_articles_to_sheets(self, articles):
        """將文章記錄到 Google Sheets"""
        try:
            logger.info("開始記錄文章到 Google Sheets...")
            
            # 準備記錄數據
            records = []
            for article in articles:
                record = {
                    "timestamp": article['generated_at'],
                    "status": "ready_to_post",
                    "workflow_type": "after_hours_limit_up",
                    "post_status": "ready_to_post",
                    "priority": "high",
                    "batch_id": f"example_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "kol_serial": article['kol_serial'],
                    "kol_nickname": article['kol_nickname'],
                    "kol_id": article['kol_serial'],
                    "kol_persona": article['kol_nickname'],
                    "stock_id": article['stock_id'],
                    "stock_name": article['stock_name'],
                    "workflow_type_detail": "after_hours_limit_up",
                    "data_source": "price",
                    "analysis_type": "price_analysis",
                    "priority_level": "high",
                    "post_id": f"limit_up_{article['stock_id']}_{datetime.now().strftime('%Y%m%d')}",
                    "title": article['title'],
                    "tags": f"漲停股,{article['stock_name']},price",
                    "has_news": "True" if article['news_links'] else "False",
                    "trigger_type": "limit_up",
                    "content": article['content'],
                    "content_length": len(article['content']),
                    "content_type": "分析",
                    "interaction_count": 0,
                    "post_record_id": f"{article['stock_id']}_{article['kol_serial']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "quality_score": 8.5,
                    "content_category": "stock_analysis",
                    "difficulty_level": "medium",
                    "ai_detection_risk_score": 0.2,
                    "personalization_level": 0.8,
                    "creativity_score": 0.7,
                    "coherence_score": 0.9,
                    "model_used": "gpt-3.5-turbo",
                    "token_count": len(article['content'].split()) * 1.3,
                    "persona": article['kol_nickname'],
                    "engagement_score": 0.8,
                    "data_type": article['data_type']
                }
                records.append(record)
            
            # 記錄到 Google Sheets
            await self.workflow_engine.sheets_client.write_records('貼文紀錄表', records)
            
            logger.info(f"✅ 成功記錄 {len(records)} 篇文章到 Google Sheets")
            
        except Exception as e:
            logger.error(f"❌ 記錄文章到 Google Sheets 失敗: {e}")
            raise

async def main():
    """主函數"""
    try:
        logger.info("🚀 開始執行盤後漲停範例文章生成器")
        
        generator = AfterHoursLimitUpExampleGenerator()
        articles = await generator.generate_example_articles()
        
        # 顯示生成結果
        print("\n" + "="*60)
        print("📊 範例文章生成結果")
        print("="*60)
        
        for i, article in enumerate(articles, 1):
            print(f"\n📝 第 {i} 篇文章:")
            print(f"股票: {article['stock_name']}({article['stock_id']})")
            print(f"數據類型: {article['data_type']}")
            print(f"KOL: {article['kol_nickname']}")
            print(f"標題: {article['title']}")
            print(f"內容長度: {len(article['content'])} 字")
            print(f"新聞連結: {'有' if article['news_links'] else '無'}")
            print("-" * 40)
        
        print(f"\n🎉 總共生成 {len(articles)} 篇範例文章")
        print("✅ 所有文章已記錄到 Google Sheets")
        
    except Exception as e:
        logger.error(f"❌ 執行失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())








