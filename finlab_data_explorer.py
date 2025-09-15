#!/usr/bin/env python3
"""
FinLab API 數據表探索腳本
探索可用的數據表和正確的數據表名稱
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

class FinLabDataExplorer:
    """FinLab API 數據表探索器"""
    
    def __init__(self):
        self.api_key = os.getenv('FINLAB_API_KEY')
        if not self.api_key:
            raise ValueError("缺少 FINLAB_API_KEY 環境變數")
        
        logger.info("FinLab API 數據表探索器初始化完成")
    
    def explore_available_tables(self):
        """探索可用的數據表"""
        print("🔍 探索 FinLab API 可用的數據表...")
        print("=" * 60)
        
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 測試不同的數據表名稱
            test_tables = [
                # 價格相關
                'price:收盤價',
                'price:開盤價',
                'price:最高價',
                'price:最低價',
                'price:成交股數',
                'price:成交金額',
                
                # 營收相關
                'revenue:當月營收',
                'revenue:營收',
                'revenue:月營收',
                'revenue:累計營收',
                'revenue:年營收',
                
                # 財報相關
                'fundamental_features:每股盈餘',
                'fundamental_features:EPS',
                'fundamental_features:每股盈餘(元)',
                'fundamental_features:營業收入',
                'fundamental_features:營業利益',
                'fundamental_features:稅後淨利',
                
                # 其他可能的表名
                'monthly_revenue:當月營收',
                'monthly_revenue:營收',
                'earnings:每股盈餘',
                'earnings:EPS',
                'financial:營收',
                'financial:每股盈餘'
            ]
            
            available_tables = []
            failed_tables = []
            
            for table_name in test_tables:
                try:
                    print(f"📊 測試數據表: {table_name}")
                    table_data = data.get(table_name)
                    
                    if table_data is not None and not table_data.empty:
                        available_tables.append({
                            'name': table_name,
                            'shape': table_data.shape,
                            'columns_count': len(table_data.columns),
                            'sample_columns': list(table_data.columns[:5]),
                            'latest_date': table_data.index[-1].strftime('%Y-%m-%d') if len(table_data) > 0 else None
                        })
                        print(f"✅ 成功: {table_name} - 形狀: {table_data.shape}")
                    else:
                        failed_tables.append(table_name)
                        print(f"❌ 失敗: {table_name} - 數據為空")
                        
                except Exception as e:
                    failed_tables.append(table_name)
                    print(f"❌ 失敗: {table_name} - 錯誤: {str(e)}")
            
            print("\n📋 可用的數據表:")
            print("-" * 40)
            for table in available_tables:
                print(f"✅ {table['name']}")
                print(f"   形狀: {table['shape']}")
                print(f"   列數: {table['columns_count']}")
                print(f"   樣本列: {table['sample_columns']}")
                print(f"   最新日期: {table['latest_date']}")
                print()
            
            print("📋 失敗的數據表:")
            print("-" * 40)
            for table in failed_tables:
                print(f"❌ {table}")
            
            return available_tables, failed_tables
            
        except Exception as e:
            logger.error(f"探索數據表時發生錯誤: {e}")
            return [], []
    
    def test_stock_data_availability(self, stock_id: str = '2330'):
        """測試特定股票的數據可用性"""
        print(f"\n🔍 測試股票 {stock_id} 的數據可用性...")
        print("-" * 40)
        
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取價格數據
            close_data = data.get('price:收盤價')
            
            if close_data is not None and stock_id in close_data.columns:
                stock_data = close_data[stock_id].dropna()
                print(f"✅ 價格數據可用")
                print(f"   數據點數: {len(stock_data)}")
                print(f"   最新日期: {stock_data.index[-1].strftime('%Y-%m-%d')}")
                print(f"   最新價格: {stock_data.iloc[-1]:.2f}")
                
                # 檢查最近30天的數據
                recent_data = stock_data.tail(30)
                print(f"   最近30天數據點: {len(recent_data)}")
                
                if len(recent_data) < 20:
                    print(f"⚠️  警告: 最近30天數據不足 (只有{len(recent_data)}個數據點)")
            else:
                print(f"❌ 價格數據不可用")
            
            # 嘗試獲取營收數據
            revenue_tables = [
                'revenue:當月營收',
                'revenue:營收',
                'revenue:月營收',
                'monthly_revenue:當月營收',
                'monthly_revenue:營收'
            ]
            
            revenue_found = False
            for table_name in revenue_tables:
                try:
                    revenue_data = data.get(table_name)
                    if revenue_data is not None and stock_id in revenue_data.columns:
                        stock_revenue = revenue_data[stock_id].dropna()
                        if len(stock_revenue) > 0:
                            print(f"✅ 營收數據可用 (表: {table_name})")
                            print(f"   數據點數: {len(stock_revenue)}")
                            print(f"   最新日期: {stock_revenue.index[-1].strftime('%Y-%m-%d')}")
                            print(f"   最新營收: {stock_revenue.iloc[-1]:,.0f}")
                            revenue_found = True
                            break
                except:
                    continue
            
            if not revenue_found:
                print(f"❌ 營收數據不可用")
            
            # 嘗試獲取財報數據
            earnings_tables = [
                'fundamental_features:每股盈餘',
                'fundamental_features:EPS',
                'earnings:每股盈餘',
                'earnings:EPS'
            ]
            
            earnings_found = False
            for table_name in earnings_tables:
                try:
                    earnings_data = data.get(table_name)
                    if earnings_data is not None and stock_id in earnings_data.columns:
                        stock_earnings = earnings_data[stock_id].dropna()
                        if len(stock_earnings) > 0:
                            print(f"✅ 財報數據可用 (表: {table_name})")
                            print(f"   數據點數: {len(stock_earnings)}")
                            print(f"   最新日期: {stock_earnings.index[-1].strftime('%Y-%m-%d')}")
                            print(f"   最新EPS: {stock_earnings.iloc[-1]:.2f}")
                            earnings_found = True
                            break
                except:
                    continue
            
            if not earnings_found:
                print(f"❌ 財報數據不可用")
                
        except Exception as e:
            logger.error(f"測試股票數據時發生錯誤: {e}")
    
    def generate_data_explanation_layer(self):
        """生成數據可解釋層報告"""
        print("\n📊 數據可解釋層報告")
        print("=" * 60)
        
        # 探索可用數據表
        available_tables, failed_tables = self.explore_available_tables()
        
        # 測試股票數據
        self.test_stock_data_availability()
        
        # 生成建議
        print("\n💡 數據可解釋層建議:")
        print("-" * 40)
        
        if available_tables:
            print("✅ 可用的數據源:")
            for table in available_tables:
                print(f"   • {table['name']} ({table['shape'][0]} 行, {table['shape'][1]} 列)")
        
        if failed_tables:
            print("❌ 需要修復的數據源:")
            for table in failed_tables:
                print(f"   • {table}")
        
        print("\n🔧 建議的修復步驟:")
        print("1. 檢查 FinLab API 文檔，確認正確的數據表名稱")
        print("2. 更新數據調度層中的數據表名稱")
        print("3. 實現數據備用方案（如使用其他數據源）")
        print("4. 添加數據驗證機制")
        print("5. 實現數據緩存機制以提高性能")

async def main():
    """主函數"""
    try:
        explorer = FinLabDataExplorer()
        explorer.generate_data_explanation_layer()
    except Exception as e:
        logger.error(f"探索過程中發生錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
