#!/usr/bin/env python3
"""
FinLab API 數據調度層修復腳本 - 更新主工作流程引擎
將正確的數據表名稱整合到主工作流程中
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinLabDataIntegration:
    """FinLab API 數據整合器 - 用於主工作流程"""
    
    def __init__(self):
        self.api_key = os.getenv('FINLAB_API_KEY')
        if not self.api_key:
            raise ValueError("缺少 FINLAB_API_KEY 環境變數")
        
        logger.info("FinLab API 數據整合器初始化完成")
    
    async def get_finlab_revenue_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取 FinLab 營收數據 - 使用正確的數據表名稱"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取營收相關數據
            revenue_data = data.get('monthly_revenue:當月營收')
            mom_growth_data = data.get('monthly_revenue:上月比較增減(%)')
            yoy_growth_data = data.get('monthly_revenue:去年同月增減(%)')
            
            if stock_id not in revenue_data.columns:
                logger.warning(f"⚠️ 股票 {stock_id} 不在營收數據表中")
                return None
            
            # 獲取最新數據
            stock_revenue = revenue_data[stock_id].dropna()
            if len(stock_revenue) == 0:
                logger.warning(f"⚠️ 股票 {stock_id} 無營收數據")
                return None
            
            latest_date = stock_revenue.index[-1]
            latest_revenue = stock_revenue.iloc[-1]
            
            # 獲取增長率數據
            mom_growth = 0.0
            yoy_growth = 0.0
            
            if mom_growth_data is not None and stock_id in mom_growth_data.columns:
                stock_mom = mom_growth_data[stock_id].dropna()
                if len(stock_mom) > 0:
                    mom_growth = float(stock_mom.iloc[-1])
            
            if yoy_growth_data is not None and stock_id in yoy_growth_data.columns:
                stock_yoy = yoy_growth_data[stock_id].dropna()
                if len(stock_yoy) > 0:
                    yoy_growth = float(stock_yoy.iloc[-1])
            
            logger.info(f"✅ 獲取到 {stock_name} 營收數據")
            
            return {
                'revenue': float(latest_revenue),
                'yoy_growth': yoy_growth,
                'mom_growth': mom_growth,
                'period': latest_date.strftime('%Y-%m'),
                'date': latest_date.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} 營收數據失敗: {e}")
            return None
    
    async def get_finlab_earnings_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取 FinLab 財報數據 - 使用正確的財報數據表"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取財報相關數據
            eps_data = data.get('fundamental_features:每股稅後淨利')
            revenue_growth_data = data.get('fundamental_features:營收成長率')
            profit_growth_data = data.get('fundamental_features:稅後淨利成長率')
            operating_profit_data = data.get('fundamental_features:營業利益')
            net_profit_data = data.get('fundamental_features:歸屬母公司淨利')
            gross_margin_data = data.get('fundamental_features:營業毛利率')
            net_margin_data = data.get('fundamental_features:稅後淨利率')
            
            if stock_id not in eps_data.columns:
                logger.warning(f"⚠️ 股票 {stock_id} 不在財報數據表中")
                return None
            
            # 獲取最新數據
            stock_eps = eps_data[stock_id].dropna()
            if len(stock_eps) == 0:
                logger.warning(f"⚠️ 股票 {stock_id} 無財報數據")
                return None
            
            latest_date = stock_eps.index[-1]
            latest_eps = stock_eps.iloc[-1]
            
            # 獲取其他財報數據
            earnings_data = {
                'eps': float(latest_eps),
                'period': str(latest_date),
                'date': str(latest_date)  # 財報數據的日期格式是字符串
            }
            
            # 獲取增長率數據
            if revenue_growth_data is not None and stock_id in revenue_growth_data.columns:
                stock_revenue_growth = revenue_growth_data[stock_id].dropna()
                if len(stock_revenue_growth) > 0:
                    earnings_data['revenue_growth'] = float(stock_revenue_growth.iloc[-1])
            
            if profit_growth_data is not None and stock_id in profit_growth_data.columns:
                stock_profit_growth = profit_growth_data[stock_id].dropna()
                if len(stock_profit_growth) > 0:
                    earnings_data['profit_growth'] = float(stock_profit_growth.iloc[-1])
            
            # 獲取利潤數據
            if operating_profit_data is not None and stock_id in operating_profit_data.columns:
                stock_operating_profit = operating_profit_data[stock_id].dropna()
                if len(stock_operating_profit) > 0:
                    earnings_data['operating_profit'] = float(stock_operating_profit.iloc[-1])
            
            if net_profit_data is not None and stock_id in net_profit_data.columns:
                stock_net_profit = net_profit_data[stock_id].dropna()
                if len(stock_net_profit) > 0:
                    earnings_data['net_profit'] = float(stock_net_profit.iloc[-1])
            
            # 獲取利潤率數據
            if gross_margin_data is not None and stock_id in gross_margin_data.columns:
                stock_gross_margin = gross_margin_data[stock_id].dropna()
                if len(stock_gross_margin) > 0:
                    earnings_data['gross_margin'] = float(stock_gross_margin.iloc[-1])
            
            if net_margin_data is not None and stock_id in net_margin_data.columns:
                stock_net_margin = net_margin_data[stock_id].dropna()
                if len(stock_net_margin) > 0:
                    earnings_data['net_margin'] = float(stock_net_margin.iloc[-1])
            
            logger.info(f"✅ 獲取到 {stock_name} 財報數據")
            
            return earnings_data
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} 財報數據失敗: {e}")
            return None
    
    async def get_finlab_stock_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取 FinLab 股票數據"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取價格數據
            open_data = data.get('price:開盤價')
            high_data = data.get('price:最高價')
            low_data = data.get('price:最低價')
            close_data = data.get('price:收盤價')
            volume_data = data.get('price:成交股數')
            
            if stock_id not in close_data.columns:
                logger.warning(f"⚠️ 股票 {stock_id} 不在價格數據表中")
                return None
            
            # 獲取最新數據
            stock_close = close_data[stock_id].dropna()
            if len(stock_close) == 0:
                logger.warning(f"⚠️ 股票 {stock_id} 無價格數據")
                return None
            
            latest_date = stock_close.index[-1]
            
            # 組合 OHLC 數據
            stock_data = {
                'date': latest_date.strftime('%Y-%m-%d'),
                'open': float(open_data[stock_id][latest_date]),
                'high': float(high_data[stock_id][latest_date]),
                'low': float(low_data[stock_id][latest_date]),
                'close': float(close_data[stock_id][latest_date]),
                'volume': int(volume_data[stock_id][latest_date]),
                'daily_change': float(close_data[stock_id][latest_date] - open_data[stock_id][latest_date]),
                'daily_change_pct': float((close_data[stock_id][latest_date] - open_data[stock_id][latest_date]) / open_data[stock_id][latest_date] * 100)
            }
            
            logger.info(f"✅ 獲取到 {stock_name} 股票數據")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} 股票數據失敗: {e}")
            return None
    
    async def test_integration(self):
        """測試數據整合"""
        print("🔧 FinLab API 數據整合測試開始...")
        print("=" * 60)
        
        # 測試股票
        test_stock = '2330'
        test_name = '台積電'
        
        print(f"\n📊 測試股票: {test_name} ({test_stock})")
        print("-" * 40)
        
        # 測試營收數據
        print("💰 測試營收數據...")
        revenue_data = await self.get_finlab_revenue_data(test_stock, test_name)
        if revenue_data:
            print(f"✅ 營收數據成功:")
            print(f"   當月營收: {revenue_data['revenue']:,.0f}")
            print(f"   年增率: {revenue_data['yoy_growth']:.2f}%")
            print(f"   月增率: {revenue_data['mom_growth']:.2f}%")
            print(f"   期間: {revenue_data['period']}")
        else:
            print("❌ 營收數據失敗")
        
        # 測試財報數據
        print("\n📈 測試財報數據...")
        earnings_data = await self.get_finlab_earnings_data(test_stock, test_name)
        if earnings_data:
            print(f"✅ 財報數據成功:")
            print(f"   EPS: {earnings_data['eps']:.2f}")
            print(f"   期間: {earnings_data['period']}")
            if 'revenue_growth' in earnings_data:
                print(f"   營收成長率: {earnings_data['revenue_growth']:.2f}%")
            if 'profit_growth' in earnings_data:
                print(f"   淨利成長率: {earnings_data['profit_growth']:.2f}%")
            if 'operating_profit' in earnings_data:
                print(f"   營業利益: {earnings_data['operating_profit']:,.0f}")
            if 'net_profit' in earnings_data:
                print(f"   歸屬母公司淨利: {earnings_data['net_profit']:,.0f}")
            if 'gross_margin' in earnings_data:
                print(f"   營業毛利率: {earnings_data['gross_margin']:.2f}%")
            if 'net_margin' in earnings_data:
                print(f"   稅後淨利率: {earnings_data['net_margin']:.2f}%")
        else:
            print("❌ 財報數據失敗")
        
        # 測試股票數據
        print("\n📊 測試股票數據...")
        stock_data = await self.get_finlab_stock_data(test_stock, test_name)
        if stock_data:
            print(f"✅ 股票數據成功:")
            print(f"   收盤價: {stock_data['close']:.2f}")
            print(f"   漲跌幅: {stock_data['daily_change_pct']:.2f}%")
            print(f"   成交量: {stock_data['volume']:,}")
            print(f"   日期: {stock_data['date']}")
        else:
            print("❌ 股票數據失敗")
        
        print("\n" + "=" * 60)
        print("🎉 數據整合測試完成！")

async def main():
    """主函數"""
    try:
        integration = FinLabDataIntegration()
        await integration.test_integration()
    except Exception as e:
        logger.error(f"數據整合測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
