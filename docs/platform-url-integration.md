# 平台 URL 整合設計

## 概述
在 KOL 個人詳情頁面中，實現平台 URL 的點擊跳轉功能，讓用戶可以直接從儀表板跳轉到實際的文章頁面。

## 數據來源

### 貼文記錄表結構
根據現有的貼文記錄表，平台 URL 相關欄位包括：

| 欄位名稱 | 欄位位置 | 說明 | 範例 |
|---------|---------|------|------|
| 平台發文ID | 第16列 (P) | 平台上的文章ID | "173337593" |
| 平台發文URL | 第17列 (Q) | 完整的文章URL | "https://www.cmoney.tw/forum/articles/173337593" |

### URL 格式
- **CMoney 論壇**: `https://www.cmoney.tw/forum/articles/{article_id}`
- **其他平台**: 根據實際平台格式調整

## 功能設計

### 1. 發文歷史表格中的 URL 顯示

#### 1.1 表格欄位設計
```typescript
{
  title: '平台 URL',
  dataIndex: 'platform_post_url',
  key: 'platform_post_url',
  width: 100,
  render: (url: string, record: PostHistory) => {
    // 根據發文狀態和 URL 顯示不同內容
    if (record.status !== '已發布') {
      return <Tag color="orange">未發布</Tag>;
    }
    
    if (!url || url.trim() === '') {
      return <Tag color="red">無URL</Tag>;
    }
    
    return (
      <Button 
        type="link" 
        size="small"
        onClick={() => window.open(url, '_blank')}
        icon={<ExternalLinkOutlined />}
        style={{ padding: '4px 8px' }}
      >
        查看
      </Button>
    );
  }
}
```

#### 1.2 狀態處理邏輯
- **已發布 + 有URL**: 顯示「查看」按鈕，點擊跳轉
- **已發布 + 無URL**: 顯示「無URL」標籤
- **未發布**: 顯示「未發布」標籤
- **草稿**: 顯示「草稿」標籤

### 2. 貼文詳情彈窗中的 URL 顯示

#### 2.1 詳情彈窗設計
```typescript
const PostDetailModal: React.FC<PostDetailModalProps> = ({ post, visible, onClose }) => {
  return (
    <Modal
      title={`貼文詳情 - ${post.post_id}`}
      open={visible}
      onCancel={onClose}
      width={800}
      footer={[
        <Button key="close" onClick={onClose}>
          關閉
        </Button>,
        post.platform_post_url && post.status === '已發布' && (
          <Button 
            key="view" 
            type="primary"
            icon={<ExternalLinkOutlined />}
            onClick={() => window.open(post.platform_post_url, '_blank')}
          >
            查看原文
          </Button>
        )
      ]}
    >
      <Descriptions column={2} bordered>
        <Descriptions.Item label="貼文ID">{post.post_id}</Descriptions.Item>
        <Descriptions.Item label="話題標題">{post.topic_title}</Descriptions.Item>
        <Descriptions.Item label="發文狀態">
          <Tag color={post.status === '已發布' ? 'green' : 'orange'}>
            {post.status}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="發文時間">
          {post.post_time ? new Date(post.post_time).toLocaleString('zh-TW') : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="平台URL" span={2}>
          {post.platform_post_url ? (
            <a 
              href={post.platform_post_url} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ wordBreak: 'break-all' }}
            >
              {post.platform_post_url}
            </a>
          ) : (
            <span style={{ color: '#999' }}>無</span>
          )}
        </Descriptions.Item>
        <Descriptions.Item label="內容" span={2}>
          <div style={{ 
            maxHeight: '200px', 
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            backgroundColor: '#f5f5f5',
            padding: '12px',
            borderRadius: '4px'
          }}>
            {post.content}
          </div>
        </Descriptions.Item>
      </Descriptions>
    </Modal>
  );
};
```

### 3. 互動數據中的 URL 關聯

#### 3.1 互動數據表格
在互動分析頁面中，也可以顯示相關的平台 URL：

```typescript
{
  title: '文章連結',
  dataIndex: 'platform_post_url',
  key: 'platform_post_url',
  width: 100,
  render: (url: string, record: InteractionRecord) => {
    if (!url || url.trim() === '') {
      return <span style={{ color: '#999' }}>-</span>;
    }
    
    return (
      <Button 
        type="text" 
        size="small"
        onClick={() => window.open(url, '_blank')}
        icon={<LinkOutlined />}
      >
        連結
      </Button>
    );
  }
}
```

## 技術實現

### 1. 數據處理

#### 1.1 後端 API 處理
```python
def parse_post_record(row):
    """解析貼文記錄行數據"""
    if len(row) < 17:
        return None
    
    return {
        "post_id": row[0],
        "kol_serial": row[1],
        "kol_nickname": row[2],
        "kol_member_id": row[3],
        "persona": row[4],
        "content_type": row[5],
        "topic_index": row[6],
        "topic_id": row[7],
        "topic_title": row[8],
        "topic_keywords": row[9],
        "content": row[10],
        "status": row[11],
        "scheduled_time": row[12],
        "post_time": row[13],
        "error_message": row[14],
        "platform_post_id": row[15],
        "platform_post_url": row[16],
        "trending_topic_title": row[17] if len(row) > 17 else ""
    }

def validate_platform_url(url: str) -> bool:
    """驗證平台 URL 格式"""
    if not url or url.strip() == "":
        return False
    
    # 檢查是否為有效的 URL
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))
```

#### 1.2 前端數據驗證
```typescript
const validatePlatformUrl = (url: string): boolean => {
  if (!url || url.trim() === '') {
    return false;
  }
  
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

const formatPlatformUrl = (url: string): string => {
  if (!validatePlatformUrl(url)) {
    return '';
  }
  
  // 確保 URL 格式正確
  return url.trim();
};
```

### 2. 用戶體驗優化

#### 2.1 載入狀態處理
```typescript
const PlatformUrlButton: React.FC<{ url: string; status: string }> = ({ url, status }) => {
  const [loading, setLoading] = useState(false);
  
  const handleClick = async () => {
    if (!url || status !== '已發布') {
      return;
    }
    
    setLoading(true);
    try {
      // 在新視窗中打開連結
      window.open(url, '_blank', 'noopener,noreferrer');
    } catch (error) {
      message.error('無法打開連結');
    } finally {
      setLoading(false);
    }
  };
  
  if (status !== '已發布') {
    return <Tag color="orange">未發布</Tag>;
  }
  
  if (!url || url.trim() === '') {
    return <Tag color="red">無URL</Tag>;
  }
  
  return (
    <Button 
      type="link" 
      size="small"
      loading={loading}
      onClick={handleClick}
      icon={<ExternalLinkOutlined />}
    >
      查看
    </Button>
  );
};
```

#### 2.2 錯誤處理
```typescript
const handleUrlClick = (url: string) => {
  try {
    // 驗證 URL
    if (!validatePlatformUrl(url)) {
      message.error('無效的 URL');
      return;
    }
    
    // 打開新視窗
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
    
    // 檢查是否成功打開
    if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
      message.error('無法打開連結，請檢查瀏覽器設定');
    }
  } catch (error) {
    message.error('打開連結時發生錯誤');
    console.error('URL click error:', error);
  }
};
```

### 3. 安全性考慮

#### 3.1 URL 安全驗證
```typescript
const isSafeUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    
    // 只允許特定的域名
    const allowedDomains = [
      'www.cmoney.tw',
      'cmoney.tw',
      'forum.cmoney.tw'
    ];
    
    return allowedDomains.includes(urlObj.hostname);
  } catch {
    return false;
  }
};
```

#### 3.2 防止 XSS 攻擊
```typescript
const sanitizeUrl = (url: string): string => {
  // 移除可能的惡意腳本
  return url.replace(/javascript:/gi, '').replace(/data:/gi, '');
};
```

## 測試策略

### 1. 功能測試
- [ ] 測試有效 URL 的點擊跳轉
- [ ] 測試無效 URL 的錯誤處理
- [ ] 測試不同發文狀態的顯示
- [ ] 測試新視窗打開功能

### 2. 安全性測試
- [ ] 測試惡意 URL 的防護
- [ ] 測試 XSS 攻擊防護
- [ ] 測試域名白名單功能

### 3. 用戶體驗測試
- [ ] 測試載入狀態顯示
- [ ] 測試錯誤提示
- [ ] 測試響應式設計

## 部署注意事項

### 1. 環境配置
- 確保生產環境的 URL 格式正確
- 配置適當的 CORS 設定
- 設定安全策略

### 2. 監控
- 監控 URL 點擊率
- 監控錯誤率
- 監控用戶行為

### 3. 維護
- 定期檢查 URL 有效性
- 更新域名白名單
- 優化用戶體驗

## 總結

平台 URL 整合功能將為 KOL 個人詳情頁面提供：

1. **直接跳轉**: 用戶可以直接從儀表板跳轉到實際文章
2. **狀態管理**: 根據發文狀態顯示不同的 URL 狀態
3. **安全防護**: 防止惡意 URL 和 XSS 攻擊
4. **用戶體驗**: 提供直觀的按鈕和錯誤處理
5. **數據完整性**: 確保 URL 數據的準確性和有效性

這個功能將大大提升儀表板的實用性，讓用戶能夠快速訪問和驗證 KOL 的實際發文內容。
