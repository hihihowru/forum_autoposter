// Vercel API Proxy - 解決 CORS 問題
// 將前端請求代理到 Railway 後端

const RAILWAY_BASE_URL = 'https://forumautoposter-production.up.railway.app';

export default async function handler(req, res) {
  // 設置 CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // 處理 OPTIONS 請求
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    // 構建目標 URL
    const { query } = req;
    const queryString = new URLSearchParams(query).toString();
    const targetUrl = `${RAILWAY_BASE_URL}${req.url}${queryString ? `?${queryString}` : ''}`;

    console.log(`🔄 [Proxy] ${req.method} ${req.url} -> ${targetUrl}`);

    // 準備請求選項
    const requestOptions = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Vercel-Proxy/1.0',
      },
    };

    // 如果有 body，添加到請求中
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      requestOptions.body = JSON.stringify(req.body);
    }

    // 發送請求到 Railway
    const response = await fetch(targetUrl, requestOptions);
    
    // 獲取響應數據
    const data = await response.text();
    
    console.log(`📡 [Proxy] 響應狀態: ${response.status}`);
    console.log(`📊 [Proxy] 響應數據: ${data.substring(0, 200)}...`);

    // 設置響應 headers
    res.status(response.status);
    
    // 複製重要的 headers
    const headersToForward = ['content-type', 'content-length', 'cache-control'];
    headersToForward.forEach(header => {
      const value = response.headers.get(header);
      if (value) {
        res.setHeader(header, value);
      }
    });

    // 發送響應
    res.send(data);

  } catch (error) {
    console.error('❌ [Proxy] 代理請求失敗:', error);
    
    res.status(500).json({
      success: false,
      message: '代理請求失敗',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
