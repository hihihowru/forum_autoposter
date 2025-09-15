// 測試 finlab API 的 company basic info
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';

async function testCompanyBasicInfo() {
  try {
    console.log('開始測試 finlab API company basic info...');
    
    // 測試獲取公司基本資料
    const response = await axios.get(`${API_BASE_URL}/api/company/basic-info`);
    const basicInfo = response.data;
    
    console.log('獲取到的公司基本資料數量:', basicInfo.length);
    
    if (basicInfo.length > 0) {
      console.log('前5筆資料範例:');
      basicInfo.slice(0, 5).forEach((company, index) => {
        console.log(`${index + 1}. 股票代號: ${company.stock_code}`);
        console.log(`   公司簡稱: ${company.company_short_name}`);
        console.log(`   公司全名: ${company.company_full_name}`);
        console.log(`   產業類別: ${company.industry_category}`);
        console.log('---');
      });
    }
    
    // 測試搜尋特定公司
    console.log('\n測試搜尋台積電...');
    const searchResponse = await axios.get(`${API_BASE_URL}/api/company/search`, {
      params: { name: '台積電', fuzzy: true }
    });
    console.log('搜尋結果:', searchResponse.data);
    
    // 測試根據股票代號獲取資訊
    console.log('\n測試根據股票代號 2330 獲取資訊...');
    const codeResponse = await axios.get(`${API_BASE_URL}/api/company/code/2330`);
    console.log('2330 公司資訊:', codeResponse.data);
    
  } catch (error) {
    console.error('測試失敗:', error);
    if (error.response) {
      console.error('API 回應狀態:', error.response.status);
      console.error('API 回應資料:', error.response.data);
    }
  }
}

// 執行測試
testCompanyBasicInfo();


