#!/usr/bin/env python3
"""
整合個人化內容生成到主流程
確保不同腳本生成的內容都符合該腳本需求的貼文
"""

import os
import sys
import asyncio
from typing import Dict, List, Any, Optional

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowConfig, WorkflowType
from src.services.content.personalized_content_generator import (
    PersonalizedContentGenerator, 
    PersonalizedContentRequest,
    PostType,
    ContentLength
)
from src.clients.google.sheets_client import GoogleSheetsClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EnhancedMainWorkflowEngine(MainWorkflowEngine):
    """增強版主工作流程引擎 - 整合個人化內容生成"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        
        # 初始化個人化內容生成器
        self.personalized_content_generator = PersonalizedContentGenerator()
        
        logger.info("增強版主工作流程引擎初始化完成")
    
    async def _execute_intraday_surge_stocks_workflow(self, config: WorkflowConfig, result):
        """執行盤中急漲股工作流程（使用個人化內容生成）"""
        
        logger.info("🚀 開始執行盤中急漲股工作流程（個人化內容生成版）")
        
        try:
            # 1. 獲取股票數據
            stock_data = self._get_real_stock_data()
            
            if not stock_data:
                logger.warning("❌ 無法獲取股票數據")
                return
            
            # 2. 按成交金額排序
            sorted_stocks = sorted(stock_data, key=lambda x: x['volume_amount'], reverse=True)
            
            # 3. 選擇要處理的股票（取前17支）
            selected_stocks = sorted_stocks[:17]
            
            # 4. 獲取KOL設定
            kol_profiles = self._get_kol_profiles()
            
            # 5. 使用個人化內容生成器生成內容
            generated_posts = []
            
            for i, stock in enumerate(selected_stocks):
                try:
                    # 選擇KOL
                    kol_profile = self._select_kol_for_stock(stock, kol_profiles, i)
                    
                    # 準備個人化內容生成請求
                    request = PersonalizedContentRequest(
                        kol_nickname=kol_profile.get('nickname', ''),
                        topic_title=f"{stock['stock_name']}盤中急漲分析",
                        topic_keywords=f"{stock['stock_name']},{stock['stock_id']},盤中急漲,漲停",
                        trigger_type="intraday_surge_smart",
                        stock_data={
                            'stock_id': stock['stock_id'],
                            'stock_name': stock['stock_name'],
                            'price': stock['price'],
                            'change': stock['change'],
                            'change_percent': stock['change_percent'],
                            'volume_amount': stock['volume_amount'],
                            'volume_shares': stock['volume_shares']
                        },
                        market_data={
                            'stock_id': stock['stock_id'],
                            'stock_name': stock['stock_name'],
                            'price': stock['price'],
                            'change': stock['change'],
                            'change_percent': stock['change_percent']
                        }
                    )
                    
                    # 生成個人化內容
                    logger.info(f"🎯 為 {stock['stock_name']}({stock['stock_id']}) 生成個人化內容...")
                    content_result = await self.personalized_content_generator.generate_personalized_content(request)
                    
                    if content_result:
                        # 記錄到Google Sheets
                        await self._record_personalized_post_to_sheets(
                            stock, kol_profile, content_result, "intraday_surge_smart"
                        )
                        
                        generated_posts.append({
                            'stock': stock,
                            'kol': kol_profile,
                            'content_result': content_result
                        })
                        
                        result.total_posts_generated += 1
                        logger.info(f"✅ {stock['stock_name']} 個人化內容生成成功")
                        logger.info(f"   文章類型: {content_result.post_type.value}")
                        logger.info(f"   內容長度: {content_result.content_length.value}")
                        logger.info(f"   品質分數: {content_result.quality_score:.2f}")
                        logger.info(f"   個人化分數: {content_result.personalization_score:.2f}")
                    else:
                        logger.warning(f"❌ {stock['stock_name']} 個人化內容生成失敗")
                
                except Exception as e:
                    logger.error(f"❌ 處理 {stock['stock_name']} 時發生錯誤: {e}")
                    continue
            
            result.generated_posts = generated_posts
            logger.info(f"🎉 盤中急漲股工作流程完成，共生成 {len(generated_posts)} 篇個人化貼文")
            
        except Exception as e:
            logger.error(f"❌ 盤中急漲股工作流程執行失敗: {e}")
            raise
    
    async def _execute_after_hours_limit_up_workflow(self, config: WorkflowConfig, result):
        """執行盤後漲停股工作流程（使用個人化內容生成）"""
        
        logger.info("🚀 開始執行盤後漲停股工作流程（個人化內容生成版）")
        
        try:
            # 1. 獲取股票數據
            stock_data = self._get_real_stock_data()
            
            if not stock_data:
                logger.warning("❌ 無法獲取股票數據")
                return
            
            # 2. 按成交金額排序
            sorted_stocks = sorted(stock_data, key=lambda x: x['volume_amount'], reverse=True)
            
            # 3. 分類為高量和低量
            high_volume_stocks = []
            low_volume_stocks = []
            
            for stock in sorted_stocks:
                if stock['volume_amount'] >= 1.0:  # 1億元以上
                    high_volume_stocks.append(stock)
                else:
                    low_volume_stocks.append(stock)
            
            logger.info(f"📊 高量股票: {len(high_volume_stocks)} 支")
            logger.info(f"📊 低量股票: {len(low_volume_stocks)} 支")
            
            # 4. 選擇要處理的股票（高量前10，低量前5）
            selected_stocks = high_volume_stocks[:10] + low_volume_stocks[:5]
            
            # 5. 獲取KOL設定
            kol_profiles = self._get_kol_profiles()
            
            # 6. 使用個人化內容生成器生成內容
            generated_posts = []
            
            for i, stock in enumerate(selected_stocks):
                try:
                    # 選擇KOL
                    kol_profile = self._select_kol_for_stock(stock, kol_profiles, i)
                    
                    # 判斷是否為高量
                    is_high_volume = stock['volume_amount'] >= 1.0
                    
                    # 準備個人化內容生成請求
                    request = PersonalizedContentRequest(
                        kol_nickname=kol_profile.get('nickname', ''),
                        topic_title=f"{stock['stock_name']}盤後漲停分析",
                        topic_keywords=f"{stock['stock_name']},{stock['stock_id']},盤後漲停,漲停",
                        trigger_type="after_hours_limit_up_smart",
                        stock_data={
                            'stock_id': stock['stock_id'],
                            'stock_name': stock['stock_name'],
                            'price': stock['price'],
                            'change': stock['change'],
                            'change_percent': stock['change_percent'],
                            'volume_amount': stock['volume_amount'],
                            'volume_shares': stock['volume_shares'],
                            'is_high_volume': is_high_volume
                        },
                        market_data={
                            'stock_id': stock['stock_id'],
                            'stock_name': stock['stock_name'],
                            'price': stock['price'],
                            'change': stock['change'],
                            'change_percent': stock['change_percent'],
                            'volume_amount': stock['volume_amount'],
                            'is_high_volume': is_high_volume
                        }
                    )
                    
                    # 生成個人化內容
                    logger.info(f"🎯 為 {stock['stock_name']}({stock['stock_id']}) 生成個人化內容...")
                    content_result = await self.personalized_content_generator.generate_personalized_content(request)
                    
                    if content_result:
                        # 記錄到Google Sheets
                        await self._record_personalized_post_to_sheets(
                            stock, kol_profile, content_result, "after_hours_limit_up_smart"
                        )
                        
                        generated_posts.append({
                            'stock': stock,
                            'kol': kol_profile,
                            'content_result': content_result
                        })
                        
                        result.total_posts_generated += 1
                        logger.info(f"✅ {stock['stock_name']} 個人化內容生成成功")
                        logger.info(f"   文章類型: {content_result.post_type.value}")
                        logger.info(f"   內容長度: {content_result.content_length.value}")
                        logger.info(f"   品質分數: {content_result.quality_score:.2f}")
                        logger.info(f"   個人化分數: {content_result.personalization_score:.2f}")
                    else:
                        logger.warning(f"❌ {stock['stock_name']} 個人化內容生成失敗")
                
                except Exception as e:
                    logger.error(f"❌ 處理 {stock['stock_name']} 時發生錯誤: {e}")
                    continue
            
            result.generated_posts = generated_posts
            logger.info(f"🎉 盤後漲停股工作流程完成，共生成 {len(generated_posts)} 篇個人化貼文")
            
        except Exception as e:
            logger.error(f"❌ 盤後漲停股工作流程執行失敗: {e}")
            raise
    
    def _get_kol_profiles(self) -> List[Dict[str, Any]]:
        """獲取KOL設定"""
        try:
            kol_data = self.sheets_client.read_sheet("KOL 角色紀錄表")
            if not kol_data or len(kol_data) <= 1:
                return []
            
            kol_profiles = []
            for row in kol_data[1:]:  # 跳過標題行
                if len(row) >= 4:
                    kol_profiles.append({
                        "serial": row[0],
                        "nickname": row[1],
                        "persona": row[3],
                        "email": row[5] if len(row) > 5 else "",
                        "password": row[6] if len(row) > 6 else ""
                    })
            
            return kol_profiles
            
        except Exception as e:
            logger.error(f"❌ 獲取KOL設定失敗: {e}")
            return []
    
    def _select_kol_for_stock(self, stock: Dict[str, Any], kol_profiles: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """為股票選擇KOL"""
        if not kol_profiles:
            return {
                "serial": "200",
                "nickname": "川川哥",
                "persona": "技術派"
            }
        
        # 輪流分配KOL
        selected_kol = kol_profiles[index % len(kol_profiles)]
        return selected_kol
    
    async def _record_personalized_post_to_sheets(self, stock: Dict[str, Any], kol_profile: Dict[str, Any], 
                                                content_result, trigger_type: str):
        """記錄個人化貼文到Google Sheets"""
        
        try:
            # 準備記錄數據
            record_data = {
                "test_post_id": f"personalized_{stock['stock_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "trigger_type": trigger_type,
                "status": "ready_to_post",
                "kol_serial": kol_profile.get("serial", ""),
                "kol_nickname": kol_profile.get("nickname", ""),
                "stock_id": stock['stock_id'],
                "stock_name": stock['stock_name'],
                "title": content_result.title,
                "content": content_result.content,
                "post_type": content_result.post_type.value,
                "content_length": content_result.content_length.value,
                "word_count": content_result.word_count,
                "quality_score": content_result.quality_score,
                "personalization_score": content_result.personalization_score,
                "generation_metadata": content_result.generation_metadata,
                "kol_settings": content_result.kol_settings,
                "technical_analysis": content_result.technical_analysis
            }
            
            # 記錄到Google Sheets
            await self._add_personalized_post_record_to_sheets(record_data)
            
            logger.info(f"📝 {stock['stock_name']} 個人化貼文記錄到Google Sheets成功")
            
        except Exception as e:
            logger.error(f"❌ 記錄 {stock['stock_name']} 個人化貼文到Google Sheets失敗: {e}")
    
    async def _add_personalized_post_record_to_sheets(self, record_data: Dict[str, Any]):
        """添加個人化貼文記錄到Google Sheets"""
        
        try:
            # 準備行數據
            row_data = [
                record_data.get("test_post_id", ""),
                record_data.get("trigger_type", ""),
                datetime.now().isoformat(),
                "personalized_generator",
                record_data.get("status", ""),
                "",  # publish_time
                "",  # articleid
                "",  # platform_post_url
                "",  # publish_status
                record_data.get("kol_serial", ""),
                record_data.get("kol_nickname", ""),
                "",  # topic_id
                "",  # topic_title
                "",  # topic_keywords
                "",  # commodity_tags
                "",  # market_data
                "",  # analysis_angle
                "",  # data_sources
                "",  # generation_metadata
                record_data.get("stock_id", ""),
                record_data.get("stock_name", ""),
                "",  # stock_price
                "",  # stock_change
                "",  # stock_change_percent
                "",  # volume_amount
                "",  # volume_shares
                "",  # topic_id
                "",  # topic_title
                "",  # topic_keywords
                record_data.get("title", ""),
                record_data.get("content", ""),
                "",  # stock_trigger_type
                record_data.get("post_type", ""),
                record_data.get("content_length", ""),
                record_data.get("word_count", 0),
                record_data.get("quality_score", 0),
                record_data.get("personalization_score", 0),
                str(record_data.get("generation_metadata", {})),
                str(record_data.get("kol_settings", {})),
                str(record_data.get("technical_analysis", {}))
            ]
            
            # 添加到Google Sheets
            self.sheets_client.append_row("貼文紀錄表", row_data)
            
        except Exception as e:
            logger.error(f"❌ 添加個人化貼文記錄失敗: {e}")
            raise

async def main():
    """主執行函數"""
    
    print("🚀 啟動增強版主工作流程引擎（個人化內容生成）")
    
    try:
        # 初始化增強版引擎
        engine = EnhancedMainWorkflowEngine()
        
        # 配置工作流程
        config = WorkflowConfig(
            workflow_type=WorkflowType.INTRADAY_SURGE_STOCKS,
            max_posts_per_topic=17,
            enable_content_generation=True,
            enable_publishing=False,  # 先不發布，只生成內容
            enable_learning=True,
            enable_quality_check=True,
            enable_sheets_recording=True,
            retry_on_failure=True,
            max_retries=3
        )
        
        # 執行工作流程
        result = await engine.execute_workflow(config)
        
        if result.success:
            print(f"✅ 工作流程執行成功!")
            print(f"📊 生成貼文: {result.total_posts_generated}")
            print(f"⏱️ 執行時間: {result.execution_time:.2f}秒")
            
            # 顯示生成結果摘要
            if result.generated_posts:
                print("\n📝 個人化內容生成摘要:")
                for i, post in enumerate(result.generated_posts, 1):
                    stock = post['stock']
                    kol = post['kol']
                    content_result = post['content_result']
                    
                    print(f"{i}. {stock['stock_name']}({stock['stock_id']}) - {kol['nickname']}")
                    print(f"   標題: {content_result.title}")
                    print(f"   文章類型: {content_result.post_type.value}")
                    print(f"   內容長度: {content_result.content_length.value}")
                    print(f"   字數: {content_result.word_count}")
                    print(f"   品質分數: {content_result.quality_score:.2f}")
                    print(f"   個人化分數: {content_result.personalization_score:.2f}")
                    print()
        else:
            print(f"❌ 工作流程執行失敗")
            print(f"錯誤: {result.errors}")
    
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


