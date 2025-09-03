# N8N Migration Project

## 專案概述
將 n8n 工作流程遷移到後端服務，實現高效能的話題派發、內容生成和發文系統。

## 專案結構
```
n8n-migration-project/
├── src/                    # 源代碼
│   ├── services/           # 核心服務
│   │   ├── assign/         # 派發服務
│   │   ├── content/        # 內容生成服務
│   │   ├── publish/        # 發文服務
│   │   └── sync/           # Google Sheets 同步服務
│   ├── clients/            # API 客戶端
│   │   ├── cmoney/         # CMoney API
│   │   ├── google/         # Google Sheets API
│   │   └── openai/         # OpenAI API
│   ├── models/             # 數據模型
│   ├── utils/              # 工具函數
│   └── config/             # 配置文件
├── docker-container/       # 現有後端代碼
├── docker/                 # Docker 配置
├── tests/                  # 測試
├── scripts/                # 腳本
└── docs/                   # 文檔
```

## 核心功能
1. **話題派發**: 自動將熱門話題派發給適合的 KOL
2. **內容生成**: 使用 AI 生成個性化貼文內容
3. **自動發文**: 排程發文到 CMoney 平台
4. **狀態同步**: 與 Google Sheets 雙向同步
5. **互動學習**: 收集互動數據並優化派發策略

## 技術棧
- **後端**: FastAPI, Python 3.9+
- **數據庫**: PostgreSQL, Redis
- **任務隊列**: Celery
- **API 整合**: Google Sheets, CMoney, OpenAI
- **部署**: Docker, Railway

## 開發環境設置
```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動本地開發環境
docker-compose up -d

# 運行測試
pytest tests/
```

## 部署
```bash
# 部署到 Railway
railway deploy
```
