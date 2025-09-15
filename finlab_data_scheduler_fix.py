#!/usr/bin/env python3
"""
FinLab API 數據調度層完整修復腳本
使用正確的數據表名稱並實現完整的數據可解釋層機制
"""

import os
import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DataSourceConfig:
    """數據源配置"""
    name: str
    table_name: str
    description: str
    status: str  # "available", "unavailable", "deprecated"

@dataclass
class DataQualityMetrics:
    """數據質量指標"""
    completeness: float
    freshness: str
    consistency: bool
    reliability: float

class FinLabDataScheduler:
    """FinLab API 數據調度層"""
    
    def __init__(self):
        self.api_key = os.getenv('FINLAB_API_KEY')
        if not self.api_key:
            raise ValueError("缺少 FINLAB_API_KEY 環境變數")
        
        # 根據 https://ai.finlab.tw/database/ 更新正確的數據源配置
        self.data_sources = {
            'price': {
                'close': DataSourceConfig('收盤價', 'price:收盤價', '股票收盤價', 'available'),
                'open': DataSourceConfig('開盤價', 'price:開盤價', '股票開盤價', 'available'),
                'high': DataSourceConfig('最高價', 'price:最高價', '股票最高價', 'available'),
                'low': DataSourceConfig('最低價', 'price:最低價', '股票最低價', 'available'),
                'volume': DataSourceConfig('成交股數', 'price:成交股數', '股票成交股數', 'available'),
                'amount': DataSourceConfig('成交金額', 'price:成交金額', '股票成交金額', 'available')
            },
            'revenue': {
                'current_month': DataSourceConfig('當月營收', 'monthly_revenue:當月營收', '當月營收數據', 'available'),
                'previous_month': DataSourceConfig('上月營收', 'monthly_revenue:上月營收', '上月營收數據', 'available'),
                'last_year_same_month': DataSourceConfig('去年當月營收', 'monthly_revenue:去年當月營收', '去年當月營收數據', 'available'),
                'mom_change_pct': DataSourceConfig('上月比較增減(%)', 'monthly_revenue:上月比較增減(%)', '月增率', 'available'),
                'yoy_change_pct': DataSourceConfig('去年同月增減(%)', 'monthly_revenue:去年同月增減(%)', '年增率', 'available'),
                'ytd_revenue': DataSourceConfig('當月累計營收', 'monthly_revenue:當月累計營收', '累計營收數據', 'available'),
                'last_year_ytd': DataSourceConfig('去年累計營收', 'monthly_revenue:去年累計營收', '去年累計營收數據', 'available'),
                'ytd_change_pct': DataSourceConfig('前期比較增減(%)', 'monthly_revenue:前期比較增減(%)', '累計增減率', 'available')
            }
        }
        
        logger.info("FinLab API 數據調度層初始化完成")
    
    async def test_data_source_connection(self, source_config: DataSourceConfig) -> Dict[str, Any]:
        """測試數據源連接"""
        start_time = datetime.now()
        
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取數據
            table_data = data.get(source_config.table_name)
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            if table_data is not None and not table_data.empty:
                return {
                    'status': 'connected',
                    'response_time': response_time,
                    'data_shape': table_data.shape,
                    'columns_count': len(table_data.columns),
                    'latest_date': table_data.index[-1].strftime('%Y-%m-%d') if len(table_data) > 0 else None,
                    'sample_columns': list(table_data.columns[:5])
                }
            else:
                return {
                    'status': 'empty_data',
                    'response_time': response_time,
                    'error': '數據為空'
                }
                
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return {
                'status': 'failed',
                'response_time': response_time,
                'error': str(e)
            }
    
    async def get_stock_ohlc_data(self, stock_id: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """獲取股票 OHLC 數據"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取各種價格數據
            open_data = data.get('price:開盤價')
            high_data = data.get('price:最高價')
            low_data = data.get('price:最低價')
            close_data = data.get('price:收盤價')
            volume_data = data.get('price:成交股數')
            
            if stock_id not in close_data.columns:
                logger.error(f"股票 {stock_id} 不在數據表中")
                return None
            
            # 獲取最近N天的數據
            stock_close = close_data[stock_id].dropna()
            if len(stock_close) < days:
                days = len(stock_close)
            
            recent_data = stock_close.tail(days)
            start_date = recent_data.index[0]
            end_date = recent_data.index[-1]
            
            # 組合 OHLC 數據
            ohlc_data = {
                'stock_id': stock_id,
                'data_points': days,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'latest_data': {
                    'open': float(open_data[stock_id][end_date]),
                    'high': float(high_data[stock_id][end_date]),
                    'low': float(low_data[stock_id][end_date]),
                    'close': float(close_data[stock_id][end_date]),
                    'volume': int(volume_data[stock_id][end_date])
                },
                'price_change': float(close_data[stock_id][end_date] - open_data[stock_id][end_date]),
                'price_change_pct': float((close_data[stock_id][end_date] - open_data[stock_id][end_date]) / open_data[stock_id][end_date] * 100)
            }
            
            return ohlc_data
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} OHLC 數據失敗: {e}")
            return None
    
    async def get_stock_revenue_data(self, stock_id: str) -> Optional[Dict[str, Any]]:
        """獲取股票完整營收數據"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取所有營收相關數據
            revenue_sources = {
                'current_month': data.get('monthly_revenue:當月營收'),
                'previous_month': data.get('monthly_revenue:上月營收'),
                'last_year_same_month': data.get('monthly_revenue:去年當月營收'),
                'mom_change_pct': data.get('monthly_revenue:上月比較增減(%)'),
                'yoy_change_pct': data.get('monthly_revenue:去年同月增減(%)'),
                'ytd_revenue': data.get('monthly_revenue:當月累計營收'),
                'last_year_ytd': data.get('monthly_revenue:去年累計營收'),
                'ytd_change_pct': data.get('monthly_revenue:前期比較增減(%)')
            }
            
            # 檢查股票是否在所有數據表中
            available_data = {}
            for key, data_source in revenue_sources.items():
                if data_source is not None and stock_id in data_source.columns:
                    stock_data = data_source[stock_id].dropna()
                    if len(stock_data) > 0:
                        available_data[key] = {
                            'value': float(stock_data.iloc[-1]),
                            'date': stock_data.index[-1].strftime('%Y-%m-%d'),
                            'data_points': len(stock_data)
                        }
            
            if not available_data:
                logger.error(f"股票 {stock_id} 無任何營收數據")
                return None
            
            # 構建完整的營收報告
            revenue_report = {
                'stock_id': stock_id,
                'data_availability': {key: key in available_data for key in revenue_sources.keys()},
                'latest_data': available_data,
                'summary': {}
            }
            
            # 生成摘要
            if 'current_month' in available_data:
                revenue_report['summary']['current_revenue'] = available_data['current_month']['value']
                revenue_report['summary']['latest_date'] = available_data['current_month']['date']
            
            if 'mom_change_pct' in available_data:
                revenue_report['summary']['mom_growth'] = available_data['mom_change_pct']['value']
            
            if 'yoy_change_pct' in available_data:
                revenue_report['summary']['yoy_growth'] = available_data['yoy_change_pct']['value']
            
            if 'ytd_revenue' in available_data:
                revenue_report['summary']['ytd_revenue'] = available_data['ytd_revenue']['value']
            
            if 'ytd_change_pct' in available_data:
                revenue_report['summary']['ytd_growth'] = available_data['ytd_change_pct']['value']
            
            return revenue_report
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 營收數據失敗: {e}")
            return None
    
    async def assess_data_quality(self, stock_id: str) -> DataQualityMetrics:
        """評估數據質量"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取價格數據
            close_data = data.get('price:收盤價')
            revenue_data = data.get('monthly_revenue:當月營收')
            
            # 檢查數據完整性
            price_available = stock_id in close_data.columns if close_data is not None else False
            revenue_available = stock_id in revenue_data.columns if revenue_data is not None else False
            
            completeness = (price_available + revenue_available) / 2
            
            # 檢查數據新鮮度
            if price_available:
                stock_close = close_data[stock_id].dropna()
                latest_date = stock_close.index[-1]
                days_old = (datetime.now() - latest_date).days
                freshness = f"{days_old}天前"
            else:
                freshness = "無數據"
            
            # 檢查數據一致性
            consistency = True
            if price_available:
                stock_close = close_data[stock_id].dropna()
                if len(stock_close) == 0:
                    consistency = False
                elif stock_close.isnull().sum() > len(stock_close) * 0.1:
                    consistency = False
            
            # 計算可靠性
            reliability = 0.0
            if price_available:
                reliability += 0.6
            if revenue_available:
                reliability += 0.4
            
            return DataQualityMetrics(
                completeness=completeness,
                freshness=freshness,
                consistency=consistency,
                reliability=reliability
            )
            
        except Exception as e:
            logger.error(f"評估股票 {stock_id} 數據質量失敗: {e}")
            return DataQualityMetrics(0.0, "錯誤", False, 0.0)
    
    async def generate_data_explanation_report(self, stock_id: str) -> Dict[str, Any]:
        """生成數據可解釋層報告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'stock_id': stock_id,
            'data_sources': {},
            'data_quality': {},
            'recommendations': []
        }
        
        # 測試各個數據源
        for category, sources in self.data_sources.items():
            for source_name, source_config in sources.items():
                connection_result = await self.test_data_source_connection(source_config)
                report['data_sources'][f"{category}_{source_name}"] = {
                    'name': source_config.name,
                    'table_name': source_config.table_name,
                    'status': source_config.status,
                    'connection': connection_result
                }
        
        # 獲取股票數據
        ohlc_data = await self.get_stock_ohlc_data(stock_id)
        revenue_data = await self.get_stock_revenue_data(stock_id)
        
        # 評估數據質量
        quality_metrics = await self.assess_data_quality(stock_id)
        
        report['stock_data'] = {
            'ohlc': ohlc_data,
            'revenue': revenue_data
        }
        
        report['data_quality'] = {
            'completeness': quality_metrics.completeness,
            'freshness': quality_metrics.freshness,
            'consistency': quality_metrics.consistency,
            'reliability': quality_metrics.reliability
        }
        
        # 生成建議
        if quality_metrics.completeness < 0.5:
            report['recommendations'].append("數據完整性不足，建議檢查數據源配置")
        
        if not quality_metrics.consistency:
            report['recommendations'].append("數據一致性問題，建議檢查數據質量")
        
        if quality_metrics.reliability < 0.8:
            report['recommendations'].append("數據可靠性較低，建議實現備用數據源")
        
        return report
    
    async def run_data_scheduler_test(self):
        """運行數據調度層測試"""
        print("🔧 FinLab API 數據調度層完整測試開始...")
        print("=" * 60)
        
        # 測試股票
        test_stock = '2330'
        
        # 生成報告
        report = await self.generate_data_explanation_report(test_stock)
        
        # 顯示結果
        print(f"\n📊 股票 {test_stock} 數據源狀況:")
        print("-" * 40)
        for source_key, source_info in report['data_sources'].items():
            status_icon = "✅" if source_info['connection']['status'] == 'connected' else "❌"
            print(f"{status_icon} {source_info['name']} ({source_info['table_name']})")
            print(f"   狀態: {source_info['connection']['status']}")
            print(f"   響應時間: {source_info['connection']['response_time']:.2f}s")
            if source_info['connection'].get('error'):
                print(f"   錯誤: {source_info['connection']['error']}")
        
        print(f"\n📈 股票 {test_stock} 數據質量:")
        print("-" * 40)
        quality = report['data_quality']
        print(f"完整性: {quality['completeness']:.1%}")
        print(f"新鮮度: {quality['freshness']}")
        print(f"一致性: {quality['consistency']}")
        print(f"可靠性: {quality['reliability']:.1%}")
        
        if report['stock_data']['ohlc']:
            ohlc = report['stock_data']['ohlc']
            print(f"\n💰 最新價格數據:")
            print(f"   收盤價: {ohlc['latest_data']['close']:.2f}")
            print(f"   漲跌幅: {ohlc['price_change_pct']:.2f}%")
            print(f"   成交量: {ohlc['latest_data']['volume']:,}")
        
        if report['stock_data']['revenue']:
            revenue = report['stock_data']['revenue']
            print(f"\n📊 最新營收數據:")
            if 'current_revenue' in revenue['summary']:
                print(f"   當月營收: {revenue['summary']['current_revenue']:,.0f}")
            if 'latest_date' in revenue['summary']:
                print(f"   日期: {revenue['summary']['latest_date']}")
            if 'yoy_growth' in revenue['summary']:
                print(f"   年增率: {revenue['summary']['yoy_growth']:.2f}%")
            if 'mom_growth' in revenue['summary']:
                print(f"   月增率: {revenue['summary']['mom_growth']:.2f}%")
            if 'ytd_revenue' in revenue['summary']:
                print(f"   累計營收: {revenue['summary']['ytd_revenue']:,.0f}")
            if 'ytd_growth' in revenue['summary']:
                print(f"   累計增減率: {revenue['summary']['ytd_growth']:.2f}%")
            
            print(f"\n📋 營收數據可用性:")
            for key, available in revenue['data_availability'].items():
                status_icon = "✅" if available else "❌"
                print(f"   {status_icon} {key}: {available}")
        
        print(f"\n💡 建議:")
        print("-" * 40)
        for recommendation in report['recommendations']:
            print(f"• {recommendation}")
        
        if not report['recommendations']:
            print("• 數據調度層運行正常")
        
        print("\n" + "=" * 60)
        print("🎉 數據調度層完整測試完成！")

async def main():
    """主函數"""
    try:
        scheduler = FinLabDataScheduler()
        await scheduler.run_data_scheduler_test()
    except Exception as e:
        logger.error(f"數據調度層測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
