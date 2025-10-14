#!/usr/bin/env python3
"""
漲停盤後分析觸發器
分析當日漲停股票的盤後表現，生成深度分析報告
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass

from src.clients.cmoney.cmoney_client import CMoneyClient
from src.services.data.stock_data_service import StockDataService
from src.services.content.content_generator import ContentGenerator
from src.services.sheets.enhanced_sheets_recorder import EnhancedSheetsRecorder

@dataclass
class LimitUpStock:
    """漲停股票數據結構"""
    symbol: str
    name: str
    close_price: float
    volume: int
    turnover_rate: float
    limit_up_time: str
    sector: str
    market_cap: float

class LimitUpAfterHoursTrigger:
    """漲停盤後分析觸發器"""
    
    def __init__(self):
        self.cmoney_client = CMoneyClient()
        self.stock_data_service = StockDataService()
        self.content_generator = ContentGenerator()
        self.sheets_recorder = EnhancedSheetsRecorder()
        self.logger = logging.getLogger(__name__)
    
    async def get_limit_up_stocks(self) -> List[LimitUpStock]:
        """獲取當日漲停股票列表"""
        try:
            # 獲取漲停股票數據
            limit_up_data = await self.cmoney_client.get_limit_up_stocks()
            
            stocks = []
            for stock_data in limit_up_data:
                stock = LimitUpStock(
                    symbol=stock_data.get('symbol'),
                    name=stock_data.get('name'),
                    close_price=stock_data.get('close_price', 0),
                    volume=stock_data.get('volume', 0),
                    turnover_rate=stock_data.get('turnover_rate', 0),
                    limit_up_time=stock_data.get('limit_up_time', ''),
                    sector=stock_data.get('sector', ''),
                    market_cap=stock_data.get('market_cap', 0)
                )
                stocks.append(stock)
            
            self.logger.info(f"獲取到 {len(stocks)} 檔漲停股票")
            return stocks
            
        except Exception as e:
            self.logger.error(f"獲取漲停股票失敗: {str(e)}")
            return []
    
    async def analyze_stock_after_hours(self, stock: LimitUpStock) -> Dict[str, Any]:
        """分析單檔股票的盤後表現"""
        try:
            # 獲取技術指標數據
            technical_data = await self.stock_data_service.get_technical_indicators(stock.symbol)
            
            # 獲取資金流向數據
            flow_data = await self.stock_data_service.get_money_flow(stock.symbol)
            
            # 獲取相關新聞
            news_data = await self.cmoney_client.get_stock_news(stock.symbol)
            
            analysis = {
                'symbol': stock.symbol,
                'name': stock.name,
                'close_price': stock.close_price,
                'volume': stock.volume,
                'turnover_rate': stock.turnover_rate,
                'technical_indicators': technical_data,
                'money_flow': flow_data,
                'news_count': len(news_data),
                'analysis_time': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"分析股票 {stock.symbol} 失敗: {str(e)}")
            return {}
    
    async def generate_analysis_report(self, analyses: List[Dict[str, Any]]) -> str:
        """生成盤後分析報告"""
        try:
            if not analyses:
                return "今日無漲停股票"
            
            report_parts = []
            report_parts.append("📊 今日漲停股票盤後分析報告")
            report_parts.append(f"📅 分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            report_parts.append(f"📈 漲停股票數量: {len(analyses)} 檔")
            report_parts.append("")
            
            # 按成交量排序
            sorted_analyses = sorted(analyses, key=lambda x: x.get('volume', 0), reverse=True)
            
            for i, analysis in enumerate(sorted_analyses[:5], 1):  # 只分析前5檔
                symbol = analysis.get('symbol', '')
                name = analysis.get('name', '')
                volume = analysis.get('volume', 0)
                turnover_rate = analysis.get('turnover_rate', 0)
                
                report_parts.append(f"**{i}. {name}({symbol})**")
                report_parts.append(f"   成交量: {volume:,}")
                report_parts.append(f"   換手率: {turnover_rate:.2f}%")
                
                # 技術指標分析
                tech_data = analysis.get('technical_indicators', {})
                if tech_data:
                    report_parts.append(f"   技術面: {tech_data.get('trend', 'N/A')}")
                
                # 資金流向分析
                flow_data = analysis.get('money_flow', {})
                if flow_data:
                    report_parts.append(f"   資金流向: {flow_data.get('direction', 'N/A')}")
                
                report_parts.append("")
            
            return "\n".join(report_parts)
            
        except Exception as e:
            self.logger.error(f"生成分析報告失敗: {str(e)}")
            return "生成分析報告時發生錯誤"
    
    async def trigger_after_hours_analysis(self):
        """觸發盤後分析流程"""
        try:
            self.logger.info("開始執行漲停盤後分析觸發器")
            
            # 1. 獲取漲停股票
            limit_up_stocks = await self.get_limit_up_stocks()
            if not limit_up_stocks:
                self.logger.info("今日無漲停股票，跳過分析")
                return
            
            # 2. 分析每檔股票
            analyses = []
            for stock in limit_up_stocks:
                analysis = await self.analyze_stock_after_hours(stock)
                if analysis:
                    analyses.append(analysis)
            
            # 3. 生成分析報告
            report = await self.generate_analysis_report(analyses)
            
            # 4. 記錄到 Google Sheets
            await self.sheets_recorder.record_trigger_execution(
                trigger_type="漲停盤後分析",
                execution_time=datetime.now(),
                result_summary=f"分析 {len(analyses)} 檔漲停股票",
                detailed_result=report
            )
            
            self.logger.info(f"漲停盤後分析完成，分析 {len(analyses)} 檔股票")
            
        except Exception as e:
            self.logger.error(f"漲停盤後分析觸發器執行失敗: {str(e)}")

async def main():
    """主函數"""
    trigger = LimitUpAfterHoursTrigger()
    await trigger.trigger_after_hours_analysis()

if __name__ == "__main__":
    asyncio.run(main())


