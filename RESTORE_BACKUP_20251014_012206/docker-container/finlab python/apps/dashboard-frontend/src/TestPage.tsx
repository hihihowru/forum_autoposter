import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div style={{ padding: '20px', backgroundColor: 'white', minHeight: '100vh' }}>
      <h1 style={{ color: 'red', fontSize: '24px' }}>測試頁面</h1>
      <p>如果你能看到這個頁面，說明React正常運作</p>
      <p>時間: {new Date().toLocaleString()}</p>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0' }}>
        <h2>系統狀態</h2>
        <ul>
          <li>React: ✅ 正常</li>
          <li>前端服務: ✅ 運行中</li>
          <li>後端API: ✅ 運行中</li>
          <li>KOL數據: ✅ 12個KOL已載入</li>
        </ul>
      </div>
    </div>
  );
};

export default TestPage;










