import React, { useState, useEffect } from 'react';
import { Card, Button, Spin, Alert, Table, Tag, Space, Typography, message, InputNumber } from 'antd';
import { ThunderboltOutlined, ReloadOutlined, CheckOutlined } from '@ant-design/icons';
import IntradayTriggerAPI, { IntradayTriggerConfig } from '../../../services/intradayTriggerAPI';
import { PostingManagementAPI } from '../../../services/postingManagementAPI';

const { Title, Text } = Typography;

interface IntradayTriggerDisplayProps {
  triggerConfig: IntradayTriggerConfig;
  onStockSelect: (stocks: string[], stockNames?: string[]) => void;
  selectedStocks?: string[];
}

const IntradayTriggerDisplay: React.FC<IntradayTriggerDisplayProps> = ({
  triggerConfig,
  onStockSelect,
  selectedStocks = []
}) => {
  const [loading, setLoading] = useState(false);
  const [stocks, setStocks] = useState<string[]>([]);
  const [stockNames, setStockNames] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [stockLimit, setStockLimit] = useState<number>(20);

  const executeTrigger = async () => {
    setLoading(true);
    setError(null);

    try {
      // 確保傳遞正確的觸發器配置格式
      if (!triggerConfig || !triggerConfig.endpoint || !triggerConfig.processing) {
        throw new Error('缺少必要的觸發器配置 (endpoint 或 processing)');
      }

      console.log('🚀 [前端] 執行盤中觸發器，triggerConfig:', triggerConfig);
      const result = await IntradayTriggerAPI.executeTrigger(triggerConfig);

      if (result.success) {
        // 檢查 stocks 格式：新格式（對象數組）還是舊格式（字符串數組）
        const isNewFormat = result.stocks.length > 0 && typeof result.stocks[0] === 'object';

        let stockCodes: string[];
        let stockNamesArray: string[];

        if (isNewFormat) {
          // 新格式：後端已經返回完整的股票信息
          const stockInfoArray = result.stocks as Array<{stock_code: string; stock_name: string; industry: string}>;
          const limitedStockInfo = stockInfoArray.slice(0, stockLimit);

          stockCodes = limitedStockInfo.map(s => s.stock_code);
          stockNamesArray = limitedStockInfo.map(s => s.stock_name || `股票${s.stock_code}`);

          console.log('✅ [前端] 使用後端返回的股票名稱:', stockNamesArray);
        } else {
          // 舊格式：只有股票代碼，需要額外查詢名稱
          const limitedStocks = (result.stocks as string[]).slice(0, stockLimit);
          stockCodes = limitedStocks;

          // 獲取股票名稱
          const stockNamePromises = limitedStocks.map(async (stockCode: string) => {
            try {
              const stockName = await PostingManagementAPI.getStockName(stockCode);
              return typeof stockName === 'string' ? stockName : `股票${stockCode}`;
            } catch (error) {
              console.warn(`獲取股票 ${stockCode} 名稱失敗:`, error);
              return `股票${stockCode}`;
            }
          });

          stockNamesArray = await Promise.all(stockNamePromises);
        }

        setStocks(stockCodes);
        setStockNames(stockNamesArray);

        message.success(`成功獲取 ${stockCodes.length} 支股票（限制 ${stockLimit} 檔），請手動選擇需要的股票`);
      } else {
        setError(result.error || '執行失敗');
        message.error('觸發器執行失敗');
      }
    } catch (err) {
      console.error('❌ [前端] 盤中觸發器執行失敗:', err);
      const errorMessage = err instanceof Error ? err.message : '未知錯誤';
      setError(errorMessage);
      message.error(`執行失敗: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  // 自動執行觸發器
  useEffect(() => {
    executeTrigger();
  }, [triggerConfig]);

  const columns = [
    {
      title: '股票代碼',
      dataIndex: 'code',
      key: 'code',
      render: (code: string, record: any) => (
        <div>
          <Tag color="blue" style={{ fontSize: '14px', padding: '4px 8px' }}>
            {code}
          </Tag>
          <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
            {record.name || `股票${code}`}
          </div>
        </div>
      )
    },
    {
      title: '狀態',
      key: 'status',
      render: (_, record: any) => (
        selectedStocks.includes(record.code) ? (
          <Tag color="green" icon={<CheckOutlined />}>已選擇</Tag>
        ) : (
          <Tag color="default">未選擇</Tag>
        )
      )
    }
  ];

  return (
    <Card 
      title={
        <Space>
          <ThunderboltOutlined style={{ color: '#fa8c16' }} />
          <span>盤中觸發器結果</span>
        </Space>
      }
      extra={
        <Space>
          <Space>
            <Text type="secondary" style={{ fontSize: '12px' }}>篩選檔數:</Text>
            <InputNumber
              min={1}
              max={100}
              value={stockLimit}
              onChange={(value) => setStockLimit(value || 20)}
              size="small"
              style={{ width: '60px' }}
            />
          </Space>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={executeTrigger}
            loading={loading}
            size="small"
          >
            重新獲取
          </Button>
        </Space>
      }
      size="small"
    >
      {error && (
        <Alert
          message="執行錯誤"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      <Spin spinning={loading}>
        {stocks.length > 0 ? (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">
                共找到 <Text strong>{stocks.length}</Text> 支股票，請勾選需要的股票添加到篩選列表
              </Text>
            </div>
            
            <Table
              dataSource={stocks.map((code, index) => ({ 
                code, 
                name: (typeof stockNames[index] === 'string' ? stockNames[index] : `股票${code}`) || `股票${code}`,
                key: code 
              }))}
              columns={columns}
              pagination={false}
              size="small"
              rowSelection={{
                selectedRowKeys: selectedStocks,
                       onChange: (selectedKeys) => {
                         // 只傳遞用戶實際選取的股票，允許取消選取
                         const selectedStockNames = (selectedKeys as string[]).map(code => {
                           const index = stocks.indexOf(code);
                           const stockName = index >= 0 ? stockNames[index] : `股票${code}`;
                           return typeof stockName === 'string' ? stockName : `股票${code}`;
                         });
                         onStockSelect(selectedKeys as string[], selectedStockNames);
                       },
                onSelectAll: (selected, selectedRows, changeRows) => {
                  // 處理全選/取消全選
                  const allStockCodes = stocks;
                         if (selected) {
                           // 全選：合併現有選取和所有股票
                           const newSelection = [...new Set([...selectedStocks, ...allStockCodes])];
                           const newSelectionNames = newSelection.map(code => {
                             const index = stocks.indexOf(code);
                             const stockName = index >= 0 ? stockNames[index] : `股票${code}`;
                             return typeof stockName === 'string' ? stockName : `股票${code}`;
                           });
                           onStockSelect(newSelection, newSelectionNames);
                         } else {
                           // 取消全選：移除所有股票
                           const newSelection = selectedStocks.filter(code => !allStockCodes.includes(code));
                           const newSelectionNames = newSelection.map(code => {
                             const index = stocks.indexOf(code);
                             const stockName = index >= 0 ? stockNames[index] : `股票${code}`;
                             return typeof stockName === 'string' ? stockName : `股票${code}`;
                           });
                           onStockSelect(newSelection, newSelectionNames);
                         }
                }
              }}
            />
          </div>
        ) : (
          !loading && (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Text type="secondary">暫無數據，請點擊重新獲取</Text>
            </div>
          )
        )}
      </Spin>
    </Card>
  );
};

export default IntradayTriggerDisplay;




