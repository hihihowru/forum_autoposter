"""
測試 OHLC 緩存機制
"""

import os
import sys
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加路徑以導入本地模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import finlab
from src.services.data.ohlc_cache_manager import OHLCCacheManager
from src.services.analysis.enhanced_technical_analyzer import EnhancedTechnicalAnalyzer

class OHLCCacheTester:
    """OHLC 緩存測試器"""
    
    def __init__(self):
        # 確保 Finlab API Key 已設定
        finlab_key = os.getenv('FINLAB_API_KEY')
        if not finlab_key:
            raise ValueError("❌ 未找到 FINLAB_API_KEY 環境變數，請先設定")
        
        # 登入 Finlab
        try:
            finlab.login(finlab_key)
            print("✅ Finlab API 登入成功")
        except Exception as e:
            raise ValueError(f"❌ Finlab API 登入失敗: {e}")
        
        self.cache_manager = OHLCCacheManager()
        self.analyzer = EnhancedTechnicalAnalyzer()
        
        print("🚀 OHLC 緩存測試器初始化完成")
    
    async def test_cache_performance(self):
        """測試緩存性能"""
        
        print("\n" + "="*80)
        print("📊 OHLC 緩存機制性能測試")
        print("🎯 目標：驗證同一天數據只抓取一次，大幅減少 API 調用")
        print("="*80)
        
        # 測試股票
        test_stocks = ['2330', '2317', '0050']
        
        print(f"\n📋 測試股票: {', '.join(test_stocks)}")
        
        # 第一次調用 - 會從 API 獲取並緩存
        print(f"\n🚀 第一次調用（預期：從 API 獲取）")
        start_time = time.time()
        
        first_results = {}
        for stock_id in test_stocks:
            try:
                df = self.cache_manager.get_stock_ohlc(stock_id, days=60)
                if df is not None:
                    first_results[stock_id] = len(df)
                    print(f"  ✅ {stock_id}: {len(df)} 個交易日")
                else:
                    print(f"  ❌ {stock_id}: 無數據")
            except Exception as e:
                print(f"  ❌ {stock_id}: 錯誤 - {e}")
        
        first_duration = time.time() - start_time
        print(f"⏱️ 第一次調用耗時: {first_duration:.2f} 秒")
        
        # 第二次調用 - 應該使用緩存
        print(f"\n🔄 第二次調用（預期：使用緩存）")
        start_time = time.time()
        
        second_results = {}
        for stock_id in test_stocks:
            try:
                df = self.cache_manager.get_stock_ohlc(stock_id, days=60)
                if df is not None:
                    second_results[stock_id] = len(df)
                    print(f"  ✅ {stock_id}: {len(df)} 個交易日")
                else:
                    print(f"  ❌ {stock_id}: 無數據")
            except Exception as e:
                print(f"  ❌ {stock_id}: 錯誤 - {e}")
        
        second_duration = time.time() - start_time
        print(f"⏱️ 第二次調用耗時: {second_duration:.2f} 秒")
        
        # 性能分析
        print(f"\n📈 性能分析:")
        if second_duration > 0:
            speedup = first_duration / second_duration
            print(f"  📊 加速比: {speedup:.1f}x")
            print(f"  ⚡ 時間節省: {((first_duration - second_duration) / first_duration * 100):.1f}%")
        
        # 數據一致性檢查
        print(f"\n🔍 數據一致性檢查:")
        for stock_id in test_stocks:
            if stock_id in first_results and stock_id in second_results:
                if first_results[stock_id] == second_results[stock_id]:
                    print(f"  ✅ {stock_id}: 數據一致 ({first_results[stock_id]} 筆)")
                else:
                    print(f"  ❌ {stock_id}: 數據不一致 ({first_results[stock_id]} vs {second_results[stock_id]})")
    
    async def test_technical_analysis_with_cache(self):
        """測試技術分析使用緩存"""
        
        print(f"\n📊 技術分析緩存整合測試")
        print("-" * 50)
        
        test_stock = '2330'
        
        print(f"🔬 分析股票: {test_stock}")
        
        start_time = time.time()
        
        try:
            analysis_result = await self.analyzer.get_enhanced_stock_analysis(test_stock, "台積電")
            
            if analysis_result:
                print(f"✅ 技術分析成功:")
                print(f"  📊 綜合評分: {analysis_result.overall_score:.1f}/10")
                print(f"  🎯 信心度: {analysis_result.confidence_score:.1f}%")
                print(f"  📈 有效指標: {len(analysis_result.effective_indicators)} 個")
                print(f"  💰 當前價格: {analysis_result.current_price:.2f}")
            else:
                print(f"❌ 技術分析失敗")
        
        except Exception as e:
            print(f"❌ 技術分析錯誤: {e}")
        
        duration = time.time() - start_time
        print(f"⏱️ 技術分析耗時: {duration:.2f} 秒")
    
    def test_cache_status(self):
        """測試緩存狀態"""
        
        print(f"\n📋 緩存狀態檢查")
        print("-" * 50)
        
        try:
            status = self.cache_manager.get_cache_status()
            
            print(f"📂 緩存目錄: {status['cache_dir']}")
            print(f"📁 緩存文件數: {status['file_count']}")
            print(f"💾 總大小: {status['total_size_mb']} MB")
            
            if status['cache_files']:
                print(f"\n📋 緩存文件詳情:")
                for file_info in status['cache_files']:
                    print(f"  📄 {file_info['filename']}: {file_info['size_mb']} MB ({file_info['modified']})")
            else:
                print(f"📭 無緩存文件")
        
        except Exception as e:
            print(f"❌ 獲取緩存狀態失敗: {e}")

async def main():
    """主函數"""
    
    print("🚀 OHLC 緩存機制測試開始")
    
    try:
        tester = OHLCCacheTester()
        
        # 測試緩存性能
        await tester.test_cache_performance()
        
        # 測試技術分析整合
        await tester.test_technical_analysis_with_cache()
        
        # 測試緩存狀態
        tester.test_cache_status()
        
        print("\n" + "="*80)
        print("🎉 OHLC 緩存機制測試完成！")
        print("✨ 主要特色:")
        print("  💾 本地 CSV 緩存存儲")
        print("  ⚡ 同一天數據只抓取一次")
        print("  📊 大幅減少 API 流量消耗")
        print("  🔄 自動檢查緩存有效性")
        print("  🧹 自動清理過期緩存")
        
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())
