#!/usr/bin/env python3
"""
漲停盤中分析觸發器
實時監控漲停股票的盤中表現，生成即時分析快報
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
class IntradayLimitUpStock:
    """盤中漲停股票數據結構"""
    symbol: str
    name: str
    current_price: float
    volume: int
    turnover_rate: float
    limit_up_time: str
    sector: str
    price_change: float
    price_change_percent: float

class LimitUpIntradayTrigger:
    """漲停盤中分析觸發器"""
    
    def __init__(self):
        self.cmoney_client = CMoneyClient()
        self.stock_data_service = StockDataService()
        self.content_generator = ContentGenerator()
        self.sheets_recorder = EnhancedSheetsRecorder()
        self.logger = logging.getLogger(__name__)
        self.monitored_stocks = set()  # 已監控的股票
    
    async def get_intraday_limit_up_stocks(self) -> List[IntradayLimitUpStock]:
        """獲取盤中漲停股票列表"""
        try:
            # 獲取實時漲停股票數據
            limit_up_data = await self.cmoney_client.get_intraday_limit_up_stocks()
            
            stocks = []
            for stock_data in limit_up_data:
                stock = IntradayLimitUpStock(
                    symbol=stock_data.get('symbol'),
                    name=stock_data.get('name'),
                    current_price=stock_data.get('current_price', 0),
                    volume=stock_data.get('volume', 0),
                    turnover_rate=stock_data.get('turnover_rate', 0),
                    limit_up_time=stock_data.get('limit_up_time', ''),
                    sector=stock_data.get('sector', ''),
                    price_change=stock_data.get('price_change', 0),
                    price_change_percent=stock_data.get('price_change_percent', 0)
                )
                stocks.append(stock)
            
            self.logger.info(f"獲取到 {len(stocks)} 檔盤中漲停股票")
            return stocks
            
        except Exception as e:
            self.logger.error(f"獲取盤中漲停股票失敗: {str(e)}")
            return []
    
    async def analyze_intraday_stock(self, stock: IntradayLimitUpStock) -> Dict[str, Any]:
        """分析單檔股票的盤中表現"""
        try:
            # 獲取即時技術指標
            technical_data = await self.stock_data_service.get_realtime_technical_indicators(stock.symbol)
            
            # 獲取即時資金流向
            flow_data = await self.stock_data_service.get_realtime_money_flow(stock.symbol)
            
            # 獲取即時新聞
            news_data = await self.cmoney_client.get_realtime_stock_news(stock.symbol)
            
            analysis = {
                'symbol': stock.symbol,
                'name': stock.name,
                'current_price': stock.current_price,
                'volume': stock.volume,
                'turnover_rate': stock.turnover_rate,
                'price_change': stock.price_change,
                'price_change_percent': stock.price_change_percent,
                'limit_up_time': stock.limit_up_time,
                'technical_indicators': technical_data,
                'money_flow': flow_data,
                'news_count': len(news_data),
                'analysis_time': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"分析盤中股票 {stock.symbol} 失敗: {str(e)}")
            return {}
    
    async def generate_intraday_report(self, analyses: List[Dict[str, Any]]) -> str:
        """生成盤中分析快報"""
        try:
            if not analyses:
                return "目前無盤中漲停股票"
            
            report_parts = []
            report_parts.append("🚀 盤中漲停股票即時快報")
            report_parts.append(f"⏰ 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_parts.append(f"📈 漲停股票數量: {len(analyses)} 檔")
            report_parts.append("")
            
            # 按漲停時間排序
            sorted_analyses = sorted(analyses, key=lambda x: x.get('limit_up_time', ''))
            
            for i, analysis in enumerate(sorted_analyses, 1):
                symbol = analysis.get('symbol', '')
                name = analysis.get('name', '')
                current_price = analysis.get('current_price', 0)
                price_change_percent = analysis.get('price_change_percent', 0)
                limit_up_time = analysis.get('limit_up_time', '')
                volume = analysis.get('volume', 0)
                
                report_parts.append(f"**{i}. {name}({symbol})**")
                report_parts.append(f"   現價: {current_price:.2f} (+{price_change_percent:.2f}%)")
                report_parts.append(f"   漲停時間: {limit_up_time}")
                report_parts.append(f"   成交量: {volume:,}")
                
                # 即時技術指標
                tech_data = analysis.get('technical_indicators', {})
                if tech_data:
                    report_parts.append(f"   技術面: {tech_data.get('trend', 'N/A')}")
                
                # 即時資金流向
                flow_data = analysis.get('money_flow', {})
                if flow_data:
                    report_parts.append(f"   資金流向: {flow_data.get('direction', 'N/A')}")
                
                report_parts.append("")
            
            return "\n".join(report_parts)
            
        except Exception as e:
            self.logger.error(f"生成盤中快報失敗: {str(e)}")
            return "生成盤中快報時發生錯誤"
    
    async def check_new_limit_ups(self, current_stocks: List[IntradayLimitUpStock]) -> List[IntradayLimitUpStock]:
        """檢查新的漲停股票"""
        new_stocks = []
        current_symbols = {stock.symbol for stock in current_stocks}
        
        for stock in current_stocks:
            if stock.symbol not in self.monitored_stocks:
                new_stocks.append(stock)
                self.monitored_stocks.add(stock.symbol)
        
        return new_stocks
    
    async def trigger_intraday_analysis(self):
        """觸發盤中分析流程"""
        try:
            self.logger.info("開始執行漲停盤中分析觸發器")
            
            # 1. 獲取盤中漲停股票
            intraday_stocks = await self.get_intraday_limit_up_stocks()
            if not intraday_stocks:
                self.logger.info("目前無盤中漲停股票")
                return
            
            # 2. 檢查新的漲停股票
            new_limit_ups = await self.check_new_limit_ups(intraday_stocks)
            
            if new_limit_ups:
                self.logger.info(f"發現 {len(new_limit_ups)} 檔新的漲停股票")
                
                # 3. 分析新的漲停股票
                analyses = []
                for stock in new_limit_ups:
                    analysis = await self.analyze_intraday_stock(stock)
                    if analysis:
                        analyses.append(analysis)
                
                # 4. 生成即時快報
                report = await self.generate_intraday_report(analyses)
                
                # 5. 記錄到 Google Sheets
                await self.sheets_recorder.record_trigger_execution(
                    trigger_type="漲停盤中分析",
                    execution_time=datetime.now(),
                    result_summary=f"發現並分析 {len(new_limit_ups)} 檔新漲停股票",
                    detailed_result=report
                )
                
                self.logger.info(f"盤中分析完成，分析 {len(new_limit_ups)} 檔新漲停股票")
            else:
                self.logger.info("無新的漲停股票")
            
        except Exception as e:
            self.logger.error(f"漲停盤中分析觸發器執行失敗: {str(e)}")
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """開始持續監控"""
        self.logger.info(f"開始持續監控，間隔 {interval_seconds} 秒")
        
        while True:
            try:
                await self.trigger_intraday_analysis()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"監控過程中發生錯誤: {str(e)}")
                await asyncio.sleep(interval_seconds)

async def main():
    """主函數"""
    trigger = LimitUpIntradayTrigger()
    
    # 單次執行
    await trigger.trigger_intraday_analysis()
    
    # 或者持續監控（取消註釋以下行）
    # await trigger.start_monitoring(interval_seconds=60)

if __name__ == "__main__":
    asyncio.run(main())


