#!/usr/bin/env python3
"""
FinLab API 連接監控腳本
檢查數據調度層的連接狀況和數據可解釋層機制
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
class ConnectionStatus:
    """連接狀態數據結構"""
    service_name: str
    status: str  # "connected", "failed", "timeout"
    response_time: float
    error_message: Optional[str] = None
    data_sample: Optional[Dict] = None

@dataclass
class DataQualityReport:
    """數據質量報告"""
    stock_id: str
    data_completeness: float
    data_freshness: str
    data_consistency: bool
    issues: List[str]

class FinLabConnectionMonitor:
    """FinLab API 連接監控器"""
    
    def __init__(self):
        self.api_key = os.getenv('FINLAB_API_KEY')
        if not self.api_key:
            raise ValueError("缺少 FINLAB_API_KEY 環境變數")
        
        # 測試股票列表
        self.test_stocks = ['2330', '2317', '2454', '3008', '2412', '2881', '1301', '2002', '1216', '2207']
        
        logger.info("FinLab API 連接監控器初始化完成")
    
    async def test_basic_connection(self) -> ConnectionStatus:
        """測試基本連接"""
        start_time = datetime.now()
        
        try:
            import finlab
            from finlab import data
            
            # 測試登入
            finlab.login(self.api_key)
            
            # 測試基本數據獲取
            test_data = data.get('price:收盤價')
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ConnectionStatus(
                service_name="FinLab Basic API",
                status="connected",
                response_time=response_time,
                data_sample={
                    "data_shape": test_data.shape,
                    "columns_count": len(test_data.columns),
                    "latest_date": test_data.index[-1].strftime('%Y-%m-%d') if len(test_data) > 0 else None
                }
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ConnectionStatus(
                service_name="FinLab Basic API",
                status="failed",
                response_time=response_time,
                error_message=str(e)
            )
    
    async def test_ohlc_data_service(self) -> ConnectionStatus:
        """測試 OHLC 數據服務"""
        start_time = datetime.now()
        
        try:
            import finlab
            from finlab import data
            
            # 測試 OHLC 數據獲取
            open_data = data.get('price:開盤價')
            high_data = data.get('price:最高價')
            low_data = data.get('price:最低價')
            close_data = data.get('price:收盤價')
            volume_data = data.get('price:成交股數')
            
            # 檢查數據完整性
            data_checks = {
                "open_data": open_data is not None and not open_data.empty,
                "high_data": high_data is not None and not high_data.empty,
                "low_data": low_data is not None and not low_data.empty,
                "close_data": close_data is not None and not close_data.empty,
                "volume_data": volume_data is not None and not volume_data.empty
            }
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ConnectionStatus(
                service_name="OHLC Data Service",
                status="connected" if all(data_checks.values()) else "partial",
                response_time=response_time,
                data_sample={
                    "data_checks": data_checks,
                    "close_data_shape": close_data.shape if close_data is not None else None,
                    "latest_date": close_data.index[-1].strftime('%Y-%m-%d') if close_data is not None and len(close_data) > 0 else None
                }
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ConnectionStatus(
                service_name="OHLC Data Service",
                status="failed",
                response_time=response_time,
                error_message=str(e)
            )
    
    async def test_revenue_data_service(self) -> ConnectionStatus:
        """測試營收數據服務"""
        start_time = datetime.now()
        
        try:
            import finlab
            from finlab import data
            
            # 測試營收數據獲取
            revenue_data = data.get('revenue:當月營收')
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ConnectionStatus(
                service_name="Revenue Data Service",
                status="connected" if revenue_data is not None and not revenue_data.empty else "failed",
                response_time=response_time,
                data_sample={
                    "revenue_data_shape": revenue_data.shape if revenue_data is not None else None,
                    "latest_date": revenue_data.index[-1].strftime('%Y-%m-%d') if revenue_data is not None and len(revenue_data) > 0 else None
                }
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ConnectionStatus(
                service_name="Revenue Data Service",
                status="failed",
                response_time=response_time,
                error_message=str(e)
            )
    
    async def test_earnings_data_service(self) -> ConnectionStatus:
        """測試財報數據服務"""
        start_time = datetime.now()
        
        try:
            import finlab
            from finlab import data
            
            # 測試財報數據獲取
            eps_data = data.get('fundamental_features:每股盈餘')
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ConnectionStatus(
                service_name="Earnings Data Service",
                status="connected" if eps_data is not None and not eps_data.empty else "failed",
                response_time=response_time,
                data_sample={
                    "eps_data_shape": eps_data.shape if eps_data is not None else None,
                    "latest_date": eps_data.index[-1].strftime('%Y-%m-%d') if eps_data is not None and len(eps_data) > 0 else None
                }
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ConnectionStatus(
                service_name="Earnings Data Service",
                status="failed",
                response_time=response_time,
                error_message=str(e)
            )
    
    async def test_stock_specific_data(self, stock_id: str) -> DataQualityReport:
        """測試特定股票的數據質量"""
        issues = []
        
        try:
            import finlab
            from finlab import data
            
            # 獲取各種數據
            close_data = data.get('price:收盤價')
            revenue_data = data.get('revenue:當月營收')
            eps_data = data.get('fundamental_features:每股盈餘')
            
            # 檢查數據完整性
            data_checks = {
                "price_data": stock_id in close_data.columns if close_data is not None else False,
                "revenue_data": stock_id in revenue_data.columns if revenue_data is not None else False,
                "eps_data": stock_id in eps_data.columns if eps_data is not None else False
            }
            
            data_completeness = sum(data_checks.values()) / len(data_checks)
            
            # 檢查數據新鮮度
            if close_data is not None and stock_id in close_data.columns:
                latest_date = close_data[stock_id].dropna().index[-1]
                days_old = (datetime.now() - latest_date).days
                data_freshness = f"{days_old}天前"
                
                if days_old > 7:
                    issues.append(f"價格數據過舊 ({days_old}天前)")
            else:
                data_freshness = "無數據"
                issues.append("無價格數據")
            
            # 檢查數據一致性
            data_consistency = True
            if close_data is not None and stock_id in close_data.columns:
                stock_close = close_data[stock_id].dropna()
                if len(stock_close) == 0:
                    data_consistency = False
                    issues.append("價格數據為空")
                elif stock_close.isnull().sum() > len(stock_close) * 0.1:
                    data_consistency = False
                    issues.append("價格數據缺失率過高")
            
            return DataQualityReport(
                stock_id=stock_id,
                data_completeness=data_completeness,
                data_freshness=data_freshness,
                data_consistency=data_consistency,
                issues=issues
            )
            
        except Exception as e:
            issues.append(f"數據獲取錯誤: {str(e)}")
            return DataQualityReport(
                stock_id=stock_id,
                data_completeness=0.0,
                data_freshness="錯誤",
                data_consistency=False,
                issues=issues
            )
    
    async def test_docker_ohlc_service(self) -> ConnectionStatus:
        """測試 Docker OHLC 服務"""
        start_time = datetime.now()
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:8001/get_ohlc",
                    params={"stock_id": "2330"},
                    timeout=10.0
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    data = response.json()
                    return ConnectionStatus(
                        service_name="Docker OHLC Service",
                        status="connected",
                        response_time=response_time,
                        data_sample={
                            "data_count": len(data) if isinstance(data, list) else 0,
                            "status_code": response.status_code
                        }
                    )
                else:
                    return ConnectionStatus(
                        service_name="Docker OHLC Service",
                        status="failed",
                        response_time=response_time,
                        error_message=f"HTTP {response.status_code}"
                    )
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return ConnectionStatus(
                service_name="Docker OHLC Service",
                status="failed",
                response_time=response_time,
                error_message=str(e)
            )
    
    async def generate_data_explanation_report(self) -> Dict[str, Any]:
        """生成數據可解釋層報告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "data_quality": {},
            "recommendations": []
        }
        
        # 測試各個數據源
        services = [
            self.test_basic_connection(),
            self.test_ohlc_data_service(),
            self.test_revenue_data_service(),
            self.test_earnings_data_service(),
            self.test_docker_ohlc_service()
        ]
        
        service_results = await asyncio.gather(*services, return_exceptions=True)
        
        for i, result in enumerate(service_results):
            if isinstance(result, Exception):
                service_name = f"Service_{i}"
                report["data_sources"][service_name] = {
                    "status": "error",
                    "error": str(result)
                }
            else:
                report["data_sources"][result.service_name] = {
                    "status": result.status,
                    "response_time": result.response_time,
                    "error": result.error_message,
                    "data_sample": result.data_sample
                }
        
        # 測試股票數據質量
        stock_reports = []
        for stock_id in self.test_stocks[:5]:  # 只測試前5個
            report_result = await self.test_stock_specific_data(stock_id)
            stock_reports.append(report_result)
        
        report["data_quality"] = {
            stock.stock_id: {
                "completeness": stock.data_completeness,
                "freshness": stock.data_freshness,
                "consistency": stock.data_consistency,
                "issues": stock.issues
            }
            for stock in stock_reports
        }
        
        # 生成建議
        failed_services = [name for name, info in report["data_sources"].items() 
                          if info["status"] in ["failed", "error"]]
        
        if failed_services:
            report["recommendations"].append(f"修復失敗的服務: {', '.join(failed_services)}")
        
        low_quality_stocks = [stock_id for stock_id, info in report["data_quality"].items()
                             if info["completeness"] < 0.5]
        
        if low_quality_stocks:
            report["recommendations"].append(f"檢查低質量數據股票: {', '.join(low_quality_stocks)}")
        
        return report
    
    async def run_full_monitoring(self):
        """運行完整監控"""
        print("🔍 FinLab API 連接監控開始...")
        print("=" * 60)
        
        # 生成報告
        report = await self.generate_data_explanation_report()
        
        # 顯示結果
        print("\n📊 數據源連接狀況:")
        print("-" * 40)
        for service_name, info in report["data_sources"].items():
            status_icon = "✅" if info["status"] == "connected" else "❌" if info["status"] == "failed" else "⚠️"
            print(f"{status_icon} {service_name}: {info['status']} ({info['response_time']:.2f}s)")
            if info.get("error"):
                print(f"   錯誤: {info['error']}")
        
        print("\n📈 數據質量報告:")
        print("-" * 40)
        for stock_id, info in report["data_quality"].items():
            quality_icon = "✅" if info["completeness"] >= 0.8 else "⚠️" if info["completeness"] >= 0.5 else "❌"
            print(f"{quality_icon} {stock_id}: 完整性 {info['completeness']:.1%}, 新鮮度 {info['freshness']}")
            if info["issues"]:
                for issue in info["issues"]:
                    print(f"   問題: {issue}")
        
        print("\n💡 建議:")
        print("-" * 40)
        for recommendation in report["recommendations"]:
            print(f"• {recommendation}")
        
        if not report["recommendations"]:
            print("• 所有服務運行正常")
        
        print("\n" + "=" * 60)
        print("🎉 監控完成！")

async def main():
    """主函數"""
    try:
        monitor = FinLabConnectionMonitor()
        await monitor.run_full_monitoring()
    except Exception as e:
        logger.error(f"監控過程中發生錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
