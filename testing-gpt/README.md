# GPT 模型測試工具

這個工具用來測試不同的 OpenAI 模型 ID 是否可以使用，特別是用來驗證 GPT-4.1 和 GPT-5 等新模型。

## 🚀 使用方法

### 1. 安裝依賴
```bash
cd testing-gpt
pip install -r requirements.txt
```

### 2. 設置環境變數
確保你的 `.env` 文件中有 `OPENAI_API_KEY`：
```bash
OPENAI_API_KEY=your-api-key-here
```

### 3. 運行測試
```bash
python test_models.py
```

## 📊 測試的模型

### GPT-4 系列
- `gpt-4`
- `gpt-4-0613`
- `gpt-4-32k`
- `gpt-4-32k-0613`
- `gpt-4-turbo`
- `gpt-4-turbo-2024-04-09`
- `gpt-4o`
- `gpt-4o-2024-05-13`
- `gpt-4o-mini`
- `gpt-4o-mini-2024-07-18`

### GPT-3.5 系列
- `gpt-3.5-turbo`
- `gpt-3.5-turbo-0613`
- `gpt-3.5-turbo-16k`
- `gpt-3.5-turbo-16k-0613`

### 新模型（測試中）
- `gpt-4.1` ⭐
- `gpt-5` ⭐
- `gpt-5-turbo`
- `gpt-4.5`
- `gpt-4.5-turbo`

### 其他模型
- `gpt-4-turbo-preview`
- `gpt-4-vision-preview`
- `gpt-4-1106-preview`
- `gpt-4-0125-preview`

## 📋 輸出結果

測試完成後會生成：
1. **控制台輸出** - 即時顯示測試進度和結果
2. **Markdown 報告** - 詳細的測試報告文件
3. **JSON 數據** - 每個模型的詳細測試結果

## 🔍 測試內容

每個模型會測試：
- ✅ **可用性** - 模型是否存在且可調用
- ⏱️ **響應時間** - API 調用的速度
- 📝 **內容生成** - 模型是否能正確生成繁體中文內容
- 🔢 **Token 使用** - 每次調用的 Token 消耗

## 📄 報告格式

生成的報告包含：
- 測試摘要統計
- 可用模型列表（含響應時間）
- 不可用模型列表（含錯誤信息）
- 每個模型的詳細測試結果

## 🎯 使用場景

1. **模型驗證** - 確認新模型是否可用
2. **性能比較** - 比較不同模型的響應時間
3. **成本評估** - 查看不同模型的 Token 使用量
4. **系統配置** - 為生產環境選擇最佳模型

## ⚠️ 注意事項

- 每次測試間隔 1 秒，避免觸發 API 限制
- 測試會消耗 OpenAI API 額度
- 建議在非生產環境中進行測試
- 某些模型可能需要特殊權限才能使用

