// 簡單的 API proxy
export default async function handler(req, res) {
  console.log('Proxy API called:', req.method, req.url);
  
  // 設置 CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  try {
    const RAILWAY_URL = process.env.RAILWAY_API_URL || 'https://forumautoposter-production-ed0b.up.railway.app';
    const targetUrl = `${RAILWAY_URL}${req.url}`;
    
    console.log('Proxying to:', targetUrl);
    
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
    });
    
    const data = await response.text();
    
    res.status(response.status);
    res.setHeader('Content-Type', response.headers.get('content-type') || 'application/json');
    res.send(data);
    
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({
      error: 'Proxy failed',
      message: error.message
    });
  }
}
