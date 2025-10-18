export default async function handler(req, res) {
  const { path } = req.query;
  const apiUrl = process.env.RAILWAY_API_URL || 'https://forumautoposter-production.up.railway.app';
  
  // Construct the full API URL
  const fullUrl = `${apiUrl}/api/${path.join('/')}`;
  
  console.log(`Proxying ${req.method} ${fullUrl}`);
  
  try {
    const response = await fetch(fullUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...req.headers
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined
    });
    
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      res.status(response.status).json(data);
    } else {
      const text = await response.text();
      res.status(response.status).send(text);
    }
  } catch (error) {
    console.error('API proxy error:', error);
    res.status(500).json({ error: 'API proxy error', message: error.message });
  }
}