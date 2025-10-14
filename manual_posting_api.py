"""
手動發文 API
提供手動發文功能的 FastAPI 端點
"""

import logging
from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from manual_posting_service import (
    ManualPostingService, 
    ManualPostingRequest, 
    ManualPostingResponse,
    KOLInfo,
    StockInfo,
    TopicInfo
)

logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(title="手動發文 API", version="1.0.0")

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依賴注入
def get_manual_posting_service():
    return ManualPostingService()

# API 端點
@app.get("/api/manual-posting/kols", response_model=List[KOLInfo])
async def get_kols(service: ManualPostingService = Depends(get_manual_posting_service)):
    """獲取所有 KOL 列表"""
    try:
        kols = service.get_kols()
        logger.info(f"獲取 {len(kols)} 個 KOL")
        return kols
    except Exception as e:
        logger.error(f"獲取 KOL 列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/manual-posting/stocks", response_model=List[StockInfo])
async def get_stocks(service: ManualPostingService = Depends(get_manual_posting_service)):
    """獲取所有股票列表"""
    try:
        stocks = service.get_stocks()
        logger.info(f"獲取 {len(stocks)} 個股票")
        return stocks
    except Exception as e:
        logger.error(f"獲取股票列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/manual-posting/stocks/search", response_model=List[StockInfo])
async def search_stocks(
    q: str = "",
    service: ManualPostingService = Depends(get_manual_posting_service)
):
    """搜尋股票"""
    try:
        stocks = service.search_stocks(q)
        logger.info(f"搜尋股票 '{q}' 找到 {len(stocks)} 個結果")
        return stocks
    except Exception as e:
        logger.error(f"搜尋股票失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/manual-posting/trending-topics", response_model=List[TopicInfo])
async def get_trending_topics():
    """獲取熱門話題"""
    try:
        # 調用現有的 trending-api 服務
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8004/trending?limit=10")
            if response.status_code == 200:
                data = response.json()
                topics = []
                for topic in data.get("topics", []):
                    topics.append(TopicInfo(
                        id=topic.get("id", ""),
                        title=topic.get("title", ""),
                        name=topic.get("title", "")  # trending-api 沒有 name 欄位，使用 title
                    ))
                logger.info(f"從 trending-api 獲取 {len(topics)} 個熱門話題")
                return topics
            else:
                logger.warning(f"trending-api 調用失敗: {response.status_code}")
                # 降級到模擬資料
                mock_topics = [
                    TopicInfo(id="1", title="台股開紅盤", name="台股開紅盤"),
                    TopicInfo(id="2", title="科技股大漲", name="科技股大漲"),
                    TopicInfo(id="3", title="半導體強勢", name="半導體強勢"),
                    TopicInfo(id="4", title="金融股反彈", name="金融股反彈"),
                    TopicInfo(id="5", title="航運股回溫", name="航運股回溫"),
                ]
                logger.info(f"使用模擬資料: {len(mock_topics)} 個熱門話題")
                return mock_topics
    except Exception as e:
        logger.error(f"獲取熱門話題失敗: {e}")
        # 降級到模擬資料
        mock_topics = [
            TopicInfo(id="1", title="台股開紅盤", name="台股開紅盤"),
            TopicInfo(id="2", title="科技股大漲", name="科技股大漲"),
            TopicInfo(id="3", title="半導體強勢", name="半導體強勢"),
            TopicInfo(id="4", title="金融股反彈", name="金融股反彈"),
            TopicInfo(id="5", title="航運股回溫", name="航運股回溫"),
        ]
        logger.info(f"使用模擬資料: {len(mock_topics)} 個熱門話題")
        return mock_topics

@app.post("/api/manual-posting/submit", response_model=ManualPostingResponse)
async def submit_manual_post(
    request: ManualPostingRequest,
    service: ManualPostingService = Depends(get_manual_posting_service)
):
    """提交手動發文"""
    try:
        logger.info(f"收到手動發文請求: KOL-{request.kol_serial}")
        
        # 驗證輸入
        if not request.title.strip():
            raise HTTPException(status_code=400, detail="標題不能為空")
        
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="內容不能為空")
        
        # 提交發文
        result = service.submit_manual_post(request)
        
        if result.success:
            logger.info(f"手動發文成功: {result.post_id}")
        else:
            logger.error(f"手動發文失敗: {result.message}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交手動發文失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/manual-posting/recent-posts")
async def get_recent_posts(
    limit: int = 10,
    service: ManualPostingService = Depends(get_manual_posting_service)
):
    """獲取最近的發文記錄"""
    try:
        posts = service.get_recent_posts(limit)
        logger.info(f"獲取 {len(posts)} 個最近發文")
        return {"posts": posts}
    except Exception as e:
        logger.error(f"獲取發文記錄失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/manual-posting/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy", "service": "manual-posting-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
