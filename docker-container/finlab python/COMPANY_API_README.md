# 公司基本資料 API 使用指南

## 📋 概述

公司基本資料 API 提供了完整的公司資訊查詢功能，包括：
- 公司基本資料獲取
- 股票代號與公司名稱對應
- 智能搜尋功能
- 產業分類查詢
- 本地快取機制

## 🚀 快速開始

### 1. 環境設定

```bash
# 設定 FinLab API 金鑰
export FINLAB_API_KEY=your_finlab_api_key

# 安裝依賴
pip install finlab pandas httpx fastapi
```

### 2. 基本使用

```python
from src.services.stock.company_info_service import create_company_info_service

# 創建服務實例
service = create_company_info_service()

# 獲取公司基本資料
companies = await service.get_company_basic_info()
print(f"總共 {len(companies)} 家公司")

# 搜尋公司
results = await service.search_company_by_name("台積電")
for company in results:
    print(f"{company.company_name}({company.stock_code}) - {company.industry}")
```

## 🔧 API 端點

### 後端 API 端點

| 端點 | 方法 | 描述 |
|------|------|------|
| `/api/company/basic-info` | GET | 獲取公司基本資料 |
| `/api/company/mapping` | GET | 獲取公司名稱代號對應表 |
| `/api/company/search` | GET | 搜尋公司 |
| `/api/company/code/{stock_code}` | GET | 根據股票代號獲取公司資訊 |
| `/api/company/industry/{industry}` | GET | 根據產業獲取公司列表 |
| `/api/company/statistics` | GET | 獲取統計資訊 |
| `/api/company/refresh` | POST | 重新整理快取 |

### 前端服務

```typescript
import companyInfoService from './services/companyInfoService';

// 搜尋公司
const results = await companyInfoService.searchCompanyByName("台積電");

// 智能搜尋
const smartResults = await companyInfoService.smartSearch("台積電");

// 獲取統計資訊
const stats = await companyInfoService.getStatistics();
```

## 📊 資料結構

### CompanyInfo
```python
@dataclass
class CompanyInfo:
    stock_code: str                    # 股票代號
    company_short_name: str           # 公司簡稱
    company_full_name: str            # 公司全名
    industry_category: str            # 產業類別
    market_type: Optional[str]        # 市場類型
    listing_date: Optional[str]       # 上市日期
    capital: Optional[float]          # 資本額
    ceo: Optional[str]                # 執行長
    address: Optional[str]            # 地址
    phone: Optional[str]              # 電話
    website: Optional[str]            # 網站
```

### CompanyMapping
```python
@dataclass
class CompanyMapping:
    stock_code: str                   # 股票代號
    company_name: str                 # 公司名稱
    industry: str                     # 產業
    aliases: List[str]                # 別名列表
```

## 🔍 搜尋功能

### 1. 精確搜尋
```python
# 精確匹配公司名稱
results = await service.search_company_by_name("台積電", fuzzy=False)
```

### 2. 模糊搜尋
```python
# 模糊匹配，支援部分關鍵詞
results = await service.search_company_by_name("台積", fuzzy=True)
```

### 3. 智能搜尋
```typescript
// 前端智能搜尋，自動選擇最佳搜尋方式
const results = await companyInfoService.smartSearch("台積電");
```

### 4. 股票代號搜尋
```python
# 直接使用股票代號查詢
company = await service.get_company_by_code("2330")
```

## 🏭 產業查詢

```python
# 根據產業獲取公司列表
companies = await service.get_companies_by_industry("半導體業")

# 獲取統計資訊
stats = await service.get_statistics()
industry_dist = stats['industry_distribution']
```

## 💾 快取機制

### 自動快取
- 資料會自動快取到本地檔案
- 快取有效期：24小時
- 支援強制重新整理

```python
# 強制重新整理快取
companies = await service.get_company_basic_info(force_refresh=True)

# 重新整理所有快取
await service.refresh_cache()
```

### 快取檔案位置
```
./cache/
├── company_basic_info.json      # 公司基本資料快取
└── company_mapping.json         # 公司對應表快取
```

## 🧪 測試

### 運行測試腳本
```bash
python test_company_api.py
```

### 測試內容
- ✅ 公司基本資料獲取
- ✅ 公司名稱代號對應表建立
- ✅ 公司搜尋功能
- ✅ 股票代號查詢
- ✅ 產業分類查詢
- ✅ 統計資訊獲取
- ✅ API 端點測試

## 🔄 整合現有系統

### 更新硬編碼對照表

原本的硬編碼對照表：
```python
stock_names = {
    "2330": "台積電",
    "2454": "聯發科",
    # ...
}
```

現在使用動態 API：
```python
# 自動從 API 獲取，備用硬編碼
company = await service.get_company_by_code("2330")
if company:
    return company.company_name
else:
    return fallback_stock_names.get("2330", "股票2330")
```

### 前端整合

在 TriggerSelector 組件中：
```typescript
// 公司搜尋功能
const handleCompanySearch = async (searchValue: string) => {
  const results = await companyInfoService.smartSearch(searchValue);
  setCompanySearchResults(results);
};

// 公司選擇
const handleCompanySelect = (company: CompanySearchResult) => {
  // 添加到股票列表
  onChange({
    ...value,
    stock_codes: [...currentCodes, company.stock_code],
    stock_names: [...currentNames, company.company_name]
  });
};
```

## 📈 效能優化

### 1. 快取策略
- 本地檔案快取，減少 API 調用
- 24小時快取有效期
- 支援手動重新整理

### 2. 搜尋優化
- 延遲搜尋（300ms），避免過於頻繁的 API 調用
- 智能搜尋，自動選擇最佳搜尋方式
- 結果限制，避免過多結果

### 3. 錯誤處理
- 備用方案：API 失敗時使用硬編碼對照表
- 優雅降級：部分功能失敗不影響整體運作
- 詳細日誌：便於問題排查

## 🚨 注意事項

1. **API 金鑰**：需要有效的 FinLab API 金鑰
2. **網路連線**：首次使用需要網路連線獲取資料
3. **快取空間**：快取檔案約 2MB，確保有足夠空間
4. **更新頻率**：建議每日更新一次快取資料

## 🔧 故障排除

### 常見問題

1. **API 金鑰錯誤**
   ```
   錯誤: FinLab API 登入失敗
   解決: 檢查 FINLAB_API_KEY 環境變數
   ```

2. **快取檔案損壞**
   ```
   錯誤: 載入快取失敗
   解決: 刪除快取檔案，重新獲取資料
   ```

3. **搜尋無結果**
   ```
   問題: 搜尋不到公司
   解決: 嘗試使用股票代號或更通用的關鍵詞
   ```

### 日誌查看
```python
import logging
logging.basicConfig(level=logging.INFO)
# 查看詳細日誌
```

## 📞 支援

如有問題，請檢查：
1. 環境變數設定
2. 網路連線狀態
3. API 金鑰有效性
4. 快取檔案完整性

---

🎉 **恭喜！** 你現在可以使用完整的公司基本資料 API 了！
