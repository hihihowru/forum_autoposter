#!/usr/bin/env python3
"""
測試 finlab API 的 company basic info 服務
"""
import asyncio
import sys
import os

# 添加路徑以便導入服務
sys.path.append('/Users/williamchen/Documents/n8n-migration-project/docker-container/finlab python/apps/dashboard-api/src')

async def test_company_info_service():
    try:
        print('開始測試 finlab API company basic info 服務...')
        
        # 導入服務
        from services.stock.company_info_service import get_company_info_service
        
        # 確保 finlab 正確導入
        import finlab
        from finlab import data
        
        # 獲取服務實例
        service = get_company_info_service()
        
        # 測試獲取公司基本資料
        print('\n1. 測試獲取公司基本資料...')
        companies = await service.get_company_basic_info()
        print(f'獲取到的公司基本資料數量: {len(companies)}')
        
        if companies:
            print('前5筆資料範例:')
            for i, company in enumerate(companies[:5]):
                print(f'{i+1}. 股票代號: {company.stock_code}')
                print(f'   公司簡稱: {company.company_short_name}')
                print(f'   公司全名: {company.company_full_name}')
                print(f'   產業類別: {company.industry_category}')
                print('---')
        
        # 測試搜尋特定公司
        print('\n2. 測試搜尋台積電...')
        search_results = await service.search_company_by_name('台積電')
        print(f'搜尋結果數量: {len(search_results)}')
        for result in search_results:
            print(f'   找到: {result.company_name} ({result.stock_code}) - {result.industry}')
        
        # 測試根據股票代號獲取資訊
        print('\n3. 測試根據股票代號 2330 獲取資訊...')
        company_by_code = await service.get_company_by_code('2330')
        if company_by_code:
            print(f'   2330 公司資訊: {company_by_code.company_name} - {company_by_code.industry}')
            print(f'   別名: {company_by_code.aliases}')
        else:
            print('   未找到 2330 的公司資訊')
        
        # 測試獲取公司對應表
        print('\n4. 測試獲取公司對應表...')
        mapping = await service.get_company_mapping()
        print(f'對應表數量: {len(mapping)}')
        
        # 顯示前幾個對應
        print('前5個對應範例:')
        for i, (code, company) in enumerate(list(mapping.items())[:5]):
            print(f'{i+1}. {code}: {company.company_name} - {company.industry}')
        
        # 測試統計資訊
        print('\n5. 測試獲取統計資訊...')
        stats = await service.get_statistics()
        print(f'總公司數: {stats.get("total_companies", 0)}')
        print(f'總對應數: {stats.get("total_mappings", 0)}')
        print(f'最後更新: {stats.get("last_updated", "N/A")}')
        
        print('\n產業分布 (前10個):')
        industry_dist = stats.get('industry_distribution', {})
        for i, (industry, count) in enumerate(list(industry_dist.items())[:10]):
            print(f'{i+1}. {industry}: {count} 家')
        
    except Exception as error:
        print(f'測試失敗: {error}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_company_info_service())
