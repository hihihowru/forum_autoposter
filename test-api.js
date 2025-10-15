// 測試 API 連接
const testApi = async () => {
  const baseUrl = 'https://forumautoposter-production.up.railway.app';
  
  console.log('🔍 測試 API 連接...');
  console.log(`Base URL: ${baseUrl}`);
  
  try {
    // 測試健康檢查
    console.log('\n1. 測試健康檢查...');
    const healthResponse = await fetch(`${baseUrl}/health`);
    console.log(`健康檢查狀態: ${healthResponse.status}`);
    console.log(`健康檢查響應: ${await healthResponse.text()}`);
    
    // 測試根路徑
    console.log('\n2. 測試根路徑...');
    const rootResponse = await fetch(`${baseUrl}/`);
    console.log(`根路徑狀態: ${rootResponse.status}`);
    console.log(`根路徑響應: ${await rootResponse.text()}`);
    
    // 測試 OHLC API
    console.log('\n3. 測試 OHLC API...');
    const ohlcResponse = await fetch(`${baseUrl}/after_hours_limit_up?limit=10`);
    console.log(`OHLC API 狀態: ${ohlcResponse.status}`);
    console.log(`OHLC API 響應: ${await ohlcResponse.text()}`);
    
  } catch (error) {
    console.error('❌ API 測試失敗:', error);
  }
};

testApi();
