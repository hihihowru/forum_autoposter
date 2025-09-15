# 歷史貼文數據收集方案

## 🎯 目標
收集 10 個 KOL 過去發過的所有貼文數據，包括互動數據。

## 🔧 技術方案

### **1. CMoney API 查詢 KOL 歷史貼文**

#### **方法 A: 使用 KOL 會員 ID 查詢**
```python
async def get_kol_historical_posts(kol_member_id: str, access_token: str):
    """
    通過 KOL 會員 ID 獲取歷史貼文列表
    
    API 端點: GET /api/Member/{member_id}/Articles
    參數: 
    - member_id: KOL 的會員 ID
    - page: 頁碼
    - pageSize: 每頁數量
    """
    url = f"{api_base_url}/api/Member/{kol_member_id}/Articles"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Version": "2.0"
    }
    
    # 分頁獲取所有貼文
    all_posts = []
    page = 1
    while True:
        response = client.get(f"{url}?page={page}&pageSize=50", headers=headers)
        if response.status_code != 200:
            break
            
        data = response.json()
        posts = data.get('data', [])
        if not posts:
            break
            
        all_posts.extend(posts)
        page += 1
    
    return all_posts
```

#### **方法 B: 使用時間範圍查詢**
```python
async def get_posts_by_date_range(start_date: str, end_date: str, access_token: str):
    """
    通過時間範圍獲取貼文
    
    API 端點: GET /api/Article/Search
    參數:
    - startDate: 開始日期
    - endDate: 結束日期
    - page: 頁碼
    """
    url = f"{api_base_url}/api/Article/Search"
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "page": 1,
        "pageSize": 100
    }
    
    # 實現分頁邏輯
    # 篩選出屬於我們 KOL 的貼文
```

### **2. KOL 憑證管理**

#### **KOL 憑證列表**
```python
KOL_CREDENTIALS = {
    "川川哥": {
        "email": "forum_200@cmoney.com.tw",
        "password": "N9t1kY3x",
        "member_id": "9505548"  # 需要查詢獲取
    },
    "KOL_2": {
        "email": "kol2@cmoney.com.tw",
        "password": "password2",
        "member_id": "待查詢"
    },
    # ... 其他 8 個 KOL
}
```

#### **獲取 KOL 會員 ID**
```python
async def get_kol_member_id(email: str, password: str):
    """獲取 KOL 的會員 ID"""
    credentials = LoginCredentials(email=email, password=password)
    login_result = await client.login(credentials)
    
    if login_result:
        # 從登入回應中獲取會員 ID
        member_info = await client.get_member_info(login_result.token, [login_result.member_id])
        return member_info[0].member_id if member_info else None
    
    return None
```

### **3. 數據收集流程**

#### **步驟 1: 收集 KOL 列表**
```python
async def collect_kol_list():
    """收集所有 KOL 的基本資訊"""
    kol_list = []
    
    for kol_name, credentials in KOL_CREDENTIALS.items():
        member_id = await get_kol_member_id(
            credentials["email"], 
            credentials["password"]
        )
        
        if member_id:
            kol_list.append({
                "name": kol_name,
                "email": credentials["email"],
                "member_id": member_id
            })
    
    return kol_list
```

#### **步驟 2: 收集歷史貼文**
```python
async def collect_historical_posts(kol_list: List[Dict]):
    """收集所有 KOL 的歷史貼文"""
    all_posts = []
    
    for kol in kol_list:
        print(f"正在收集 {kol['name']} 的歷史貼文...")
        
        # 登入獲取 token
        credentials = LoginCredentials(
            email=kol["email"], 
            password=KOL_CREDENTIALS[kol["name"]]["password"]
        )
        login_result = await client.login(credentials)
        
        if login_result:
            # 獲取歷史貼文
            posts = await get_kol_historical_posts(
                kol["member_id"], 
                login_result.token
            )
            
            # 為每個貼文添加 KOL 資訊
            for post in posts:
                post["kol_name"] = kol["name"]
                post["kol_member_id"] = kol["member_id"]
            
            all_posts.extend(posts)
            print(f"✅ {kol['name']}: 收集到 {len(posts)} 篇貼文")
        
        # 避免 API 限制
        await asyncio.sleep(1)
    
    return all_posts
```

#### **步驟 3: 獲取互動數據**
```python
async def collect_interaction_data(posts: List[Dict]):
    """為所有貼文收集互動數據"""
    posts_with_interactions = []
    
    for post in posts:
        article_id = post.get("articleId")
        if article_id:
            # 獲取互動數據
            interaction_data = await client.get_article_interactions(
                access_token, 
                article_id
            )
            
            if interaction_data:
                post["interaction_data"] = {
                    "views": interaction_data.views,
                    "likes": interaction_data.likes,
                    "comments": interaction_data.comments,
                    "shares": interaction_data.shares,
                    "engagement_rate": interaction_data.engagement_rate,
                    "emoji_count": interaction_data.raw_data.get("emojiCount", {})
                }
            
            posts_with_interactions.append(post)
        
        # 避免 API 限制
        await asyncio.sleep(0.5)
    
    return posts_with_interactions
```

### **4. 數據存儲**

#### **存儲到 PostgreSQL**
```python
async def save_historical_posts_to_db(posts: List[Dict]):
    """將歷史貼文數據存儲到數據庫"""
    from docker_container.finlab_python.apps.posting_service.postgresql_service import PostgreSQLPostRecordService
    
    service = PostgreSQLPostRecordService()
    
    for post in posts:
        # 創建歷史貼文記錄
        historical_post = {
            "post_id": str(uuid.uuid4()),  # 生成新的 UUID
            "title": post.get("title", ""),
            "content": post.get("content", ""),
            "kol_name": post.get("kol_name"),
            "kol_serial": get_kol_serial(post.get("kol_name")),
            "cmoney_post_id": post.get("articleId"),
            "cmoney_post_url": f"https://forum.cmoney.tw/article/{post.get('articleId')}",
            "publish_date": post.get("publishDate"),
            "status": "published",
            
            # 互動數據
            "views": post.get("interaction_data", {}).get("views", 0),
            "likes": post.get("interaction_data", {}).get("likes", 0),
            "comments": post.get("interaction_data", {}).get("comments", 0),
            "shares": post.get("interaction_data", {}).get("shares", 0),
            "engagement_rate": post.get("interaction_data", {}).get("engagement_rate", 0),
            "emoji_count": post.get("interaction_data", {}).get("emoji_count", {}),
            
            # 標記為歷史數據
            "is_historical": True,
            "created_at": datetime.now()
        }
        
        await service.create_post_record(historical_post)
```

## 🚀 實施計劃

### **階段 1: 準備工作 (1小時)**
1. 收集所有 KOL 的憑證
2. 獲取每個 KOL 的會員 ID
3. 測試 API 查詢功能

### **階段 2: 數據收集 (2小時)**
1. 實現歷史貼文收集腳本
2. 批量收集所有 KOL 的貼文
3. 獲取每篇貼文的互動數據

### **階段 3: 數據存儲 (1小時)**
1. 設計歷史數據存儲結構
2. 將數據存儲到 PostgreSQL
3. 創建數據驗證和清理腳本

## 📋 需要的資訊

### **KOL 憑證清單**
請提供 10 個 KOL 的：
- Email 地址
- 密碼
- 會員 ID (如果知道的話)

### **時間範圍**
- 需要收集多長時間的歷史數據？
- 從什麼時候開始？

## ⚠️ 注意事項

1. **API 限制**: CMoney API 可能有請求頻率限制
2. **數據量**: 10 個 KOL 的歷史數據可能很大
3. **數據品質**: 需要驗證和清理收集到的數據
4. **隱私**: 確保 KOL 憑證的安全性

## 🎯 下一步行動

1. 確認 KOL 憑證清單
2. 開始實施數據收集腳本
3. 測試小規模數據收集
4. 批量收集所有歷史數據
