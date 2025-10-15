# 專案清理整頓計劃

## 📊 現況分析

- **總計 Python 檔案**: 826 個
- **測試/版本/修復檔案**: 256 個 (31%)
- **已停用檔案**: 7 個
- **核心代碼目錄**: `src/` (結構良好)
- **問題**: 根目錄有大量零散腳本，結構混亂

## 🎯 清理目標

1. 保持 `src/` 目錄的核心代碼
2. 歸檔舊版本、測試、臨時檔案
3. 整理根目錄的腳本到適當位置
4. 刪除重複和無用的檔案
5. 建立清晰的專案結構

## 📁 建議的新專案結構

```
n8n-migration-project/
├── src/                          # 核心源代碼（保持不變）
│   ├── agents/
│   ├── api_integration/
│   ├── clients/
│   ├── components/
│   ├── config/
│   ├── content_generation/
│   ├── core/
│   ├── operations/
│   ├── services/
│   └── utils/
│
├── scripts/                      # 實用腳本（整理後）
│   ├── backup/                   # 備份相關
│   ├── data_migration/           # 數據遷移
│   ├── maintenance/              # 維護工具
│   └── analysis/                 # 數據分析
│
├── tools/                        # 開發工具
│   ├── limit_up_posts/           # 漲停股相關工具
│   ├── kol_management/           # KOL 管理工具
│   └── manual_posting/           # 手動發文工具
│
├── tests/                        # 所有測試
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── archive/                      # 歸檔舊檔案
│   ├── old_versions/             # 舊版本（v2, v3...）
│   ├── deprecated/               # 已棄用的代碼
│   └── experiments/              # 實驗性代碼
│
├── docs/                         # 文檔（保持）
├── docker-container/             # Docker 配置（保持）
├── backups/                      # 備份文件（保持）
├── credentials/                  # 憑證（保持）
├── config/                       # 配置文件（保持）
│
├── main.py                       # 主入口（保持）
├── docker-compose.yml            # Docker 配置（保持）
├── requirements.txt              # 依賴（保持）
├── .env.example                  # 環境變數範例（保持）
└── README.md                     # 說明文件（保持）
```

## 🗂️ 檔案分類計劃

### 1️⃣ 保留在根目錄（核心檔案）
- `main.py` - 主入口點
- `docker-compose*.yml` - Docker 配置
- `requirements*.txt` - 依賴管理
- `.env.example` - 環境變數範例
- `README.md` - 專案說明
- `.gitignore` - Git 配置
- `Dockerfile` - Docker 映像

### 2️⃣ 移動到 `tools/` 目錄（工具腳本）

#### tools/limit_up_posts/
- `limit_up_analysis.py`
- `quick_limit_up_posts.py`
- `manual_limit_up_posts.py`
- `generate_limit_up_posts.py`
- `scheduled_limit_up_publisher.py`

#### tools/manual_posting/
- `manual_posting_service.py`
- `manual_posting_api.py`
- `manual_posting_page.html`
- `start_manual_posting.sh`
- `start_manual_posting_integrated.sh`

#### tools/kol_management/
- `kol_config_manager.py`
- `analyze_kol_profiles.py`
- `update_kol_profiles.py`
- `sync_kol_data.py`
- `init_kol_data.py`

#### tools/data_analysis/
- `article_interaction_checker.py`
- `explore_member_articles_api.py`
- `monthly_revenue_api.py`

### 3️⃣ 移動到 `scripts/` 目錄（維護腳本）

#### scripts/backup/
- `backup_database.py`
- `comprehensive_backup.py`
- `quick_backup.py`
- `essential_backup.py`
- `restore_*.sh`

#### scripts/maintenance/
- `clear_and_rebuild.py`
- `rebuild_sheet.py`
- `restore_sheet_structure.py`
- `fix_google_sheets_credentials.py`

#### scripts/data_migration/
- `migrate_posts_to_database.py`
- `process_tsv_data.py`
- `add_columns_manually.py`

### 4️⃣ 移動到 `archive/` 目錄（舊版本和實驗代碼）

#### archive/old_versions/
- 所有 `*_v2.py`, `*_v3.py`, `*_v4.py` 等版本檔案
- 所有 `*_fix.py`, `*_fixed.py` 修復檔案
- 所有 `*_old.py`, `*_backup.py` 備份檔案

#### archive/deprecated/
- 所有 `*.DISABLED` 檔案
- 所有 `*_old.py` 檔案
- 過時的工作流程檔案

#### archive/experiments/
- `advanced_self_learning.py`
- `self_learning_prototype.py`
- `smart_*.py` 系列檔案

### 5️⃣ 移動到 `tests/` 目錄（所有測試）

所有 `test_*.py` 檔案分類到：
- `tests/unit/` - 單元測試
- `tests/integration/` - 整合測試
- `tests/e2e/` - 端對端測試

### 6️⃣ 可以刪除的檔案（重複/臨時）

- 所有空檔案（1 byte 的 .py 檔）
- 重複的 JSON 數據檔案（保留最新版本）
- 臨時生成的 .txt 檔案
- 舊的備份目錄（BACKUP_*, RESTORE_BACKUP_*）

## ✅ 執行步驟

### Phase 1: 準備工作
1. ✅ 創建清理計劃文件
2. ⬜ 建立新目錄結構
3. ⬜ 備份整個專案到安全位置

### Phase 2: 歸檔舊檔案
1. ⬜ 創建 `archive/` 目錄及子目錄
2. ⬜ 移動所有版本檔案到 `archive/old_versions/`
3. ⬜ 移動已停用檔案到 `archive/deprecated/`
4. ⬜ 移動實驗性代碼到 `archive/experiments/`

### Phase 3: 整理測試檔案
1. ⬜ 創建 `tests/` 目錄及子目錄
2. ⬜ 移動所有 test_*.py 到適當的測試目錄

### Phase 4: 整理工具腳本
1. ⬜ 創建 `tools/` 目錄及子目錄
2. ⬜ 移動工具腳本到對應目錄
3. ⬜ 移動維護腳本到 `scripts/` 目錄

### Phase 5: 清理和驗證
1. ⬜ 刪除空檔案和重複檔案
2. ⬜ 刪除舊的備份目錄
3. ⬜ 更新 README.md
4. ⬜ 測試主要功能是否正常

### Phase 6: 文檔更新
1. ⬜ 更新 README.md 說明新結構
2. ⬜ 創建 CONTRIBUTING.md
3. ⬜ 更新相關文檔

## 📝 注意事項

1. **備份優先**: 執行任何操作前先備份
2. **逐步進行**: 每個階段完成後測試
3. **保持追蹤**: 記錄所有移動和刪除操作
4. **測試驗證**: 確保核心功能不受影響
5. **更新引用**: 更新 import 路徑和腳本引用

## 🚀 預期成果

- **減少根目錄檔案**: 從 300+ 減少到 < 20
- **清晰的結構**: 所有檔案都在適當位置
- **易於維護**: 新開發者能快速理解專案
- **保留歷史**: 舊代碼歸檔而非刪除
- **提高效率**: 減少檔案搜尋時間

## ❓ 需要確認的問題

1. 是否有特定的腳本目前正在生產環境使用？
2. 是否需要保留所有的版本檔案（v2, v3...）還是可以直接刪除？
3. 測試檔案是否還需要運行？哪些是重要的？
4. 舊的備份目錄（BACKUP_*, RESTORE_BACKUP_*）可以刪除嗎？
5. 是否需要建立 Git 分支進行清理工作？

---

**準備好開始了嗎？我可以幫你逐步執行這個計劃！** 🎯
