// 簡單的 API 測試
export default function handler(req, res) {
  console.log('API route called:', req.method, req.url);
  res.status(200).json({
    message: 'API is working!',
    method: req.method,
    url: req.url,
    timestamp: new Date().toISOString()
  });
}
