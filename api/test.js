// 測試 API route
export default async function handler(req, res) {
  res.status(200).json({
    message: 'API route is working!',
    method: req.method,
    url: req.url,
    timestamp: new Date().toISOString()
  });
}
