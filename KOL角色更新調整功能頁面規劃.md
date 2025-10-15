# 🎯 KOL角色更新調整功能頁面規劃

## 📊 功能概述

KOL角色更新調整功能頁面是一個專門用於管理KOL人設、Prompt設定和批量調整的綜合管理系統。

## 🎨 頁面設計

### **主要功能區域**

#### 1. **頁面標題區域**
- KOL角色管理標題
- 功能說明文字
- 操作按鈕組（刷新、批量更新、匯出、匯入）

#### 2. **KOL列表表格**
- 序號、暱稱、人設、狀態顯示
- 目標受眾、互動閾值、發文統計
- 操作按鈕（編輯、複製、查看詳情）
- 多選功能支援批量操作

#### 3. **編輯Modal**
- **人設設定Tab**：人設類型、目標受眾、常用詞彙、口語化用詞、語氣風格
- **Prompt設定Tab**：Prompt人設、風格、守則、骨架、行動呼籲

#### 4. **批量更新Modal**
- 選擇的KOL數量顯示
- 批量更新欄位選擇
- 更新結果回饋

## 🔧 技術實現

### **前端組件**

#### **KOLRoleUpdatePage.tsx**
```typescript
// 主要功能
- KOL列表載入和顯示
- 單個KOL編輯
- 批量KOL更新
- 設定複製功能
- 匯出/匯入功能
```

#### **核心功能**
1. **KOL列表管理**
   - 從API載入KOL數據
   - 表格顯示KOL資訊
   - 多選支援批量操作

2. **單個KOL編輯**
   - Modal彈窗編輯
   - 人設設定表單
   - Prompt設定表單
   - 即時保存

3. **批量更新**
   - 選擇多個KOL
   - 統一更新欄位
   - 批量操作結果回饋

### **後端API**

#### **主要端點**
```python
# 單個KOL更新
PUT /api/dashboard/kols/{member_id}

# 批量更新KOL
POST /api/dashboard/kols/batch-update

# 獲取KOL完整設定
GET /api/dashboard/kols/{member_id}/settings
```

#### **數據模型**
```python
class KOLUpdateRequest(BaseModel):
    serial: Optional[str] = None
    nickname: Optional[str] = None
    persona: Optional[str] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    interaction_threshold: Optional[float] = None
    common_terms: Optional[str] = None
    colloquial_terms: Optional[str] = None
    tone_style: Optional[str] = None
    prompt_persona: Optional[str] = None
    prompt_style: Optional[str] = None
    prompt_guardrails: Optional[str] = None
    prompt_skeleton: Optional[str] = None
    prompt_cta: Optional[str] = None
    prompt_hashtags: Optional[str] = None
    signature: Optional[str] = None
    emoji_pack: Optional[str] = None
    model_id: Optional[str] = None
    model_temp: Optional[float] = None
    max_tokens: Optional[int] = None
```

## 🚀 使用流程

### **單個KOL編輯**
1. 在KOL列表中點擊"編輯"按鈕
2. 在Modal中選擇"人設設定"或"Prompt設定"Tab
3. 修改相關欄位
4. 點擊"保存"按鈕
5. 系統更新KOL設定並顯示成功訊息

### **批量更新KOL**
1. 在KOL列表中選擇多個KOL（勾選checkbox）
2. 點擊"批量更新"按鈕
3. 在Modal中選擇要更新的欄位
4. 點擊"批量更新"按鈕
5. 系統顯示更新結果（成功/失敗數量）

### **複製KOL設定**
1. 點擊KOL的"複製"按鈕
2. 選擇目標KOL
3. 選擇要複製的欄位
4. 確認複製操作
5. 系統複製設定到目標KOL

## 📈 功能特色

### **1. 直觀的UI設計**
- 清晰的表格佈局
- 顏色標籤區分不同人設
- 狀態指示器顯示KOL狀態
- 響應式設計適配不同螢幕

### **2. 靈活的編輯方式**
- 單個KOL精細調整
- 批量KOL統一更新
- 設定複製快速配置
- 即時預覽和驗證

### **3. 完整的數據管理**
- 支援所有KOL設定欄位
- 人設和Prompt分離管理
- 數據匯出/匯入功能
- 操作歷史記錄

### **4. 錯誤處理和回饋**
- 詳細的錯誤訊息
- 操作結果統計
- 失敗原因說明
- 成功確認提示

## 🔒 安全考量

### **權限控制**
- 只有管理員可以修改KOL設定
- 操作日誌記錄
- 敏感資訊保護

### **數據驗證**
- 前端表單驗證
- 後端數據檢查
- 欄位格式驗證
- 業務邏輯檢查

### **備份機制**
- 修改前自動備份
- 操作回滾功能
- 數據恢復機制

## 📊 監控和統計

### **操作統計**
- KOL更新次數統計
- 批量操作成功率
- 最常修改的欄位
- 操作時間分析

### **KOL狀態監控**
- 人設分佈統計
- 狀態變更追蹤
- 設定完整性檢查
- 異常狀態警報

## 🎯 優勢

1. **效率提升**：批量操作大幅提升管理效率
2. **靈活性**：支援單個和批量兩種調整方式
3. **直觀性**：清晰的UI設計降低使用門檻
4. **完整性**：涵蓋所有KOL設定需求
5. **可靠性**：完善的錯誤處理和數據驗證
6. **擴展性**：易於添加新的設定欄位和功能

## 🔮 未來擴展

### **計劃功能**
- KOL設定模板系統
- 自動化設定建議
- 設定變更審批流程
- 設定版本控制
- 批量匯入Excel功能
- 設定差異對比工具

這個KOL角色更新調整功能頁面為KOL管理提供了完整、高效、易用的解決方案！🎯
