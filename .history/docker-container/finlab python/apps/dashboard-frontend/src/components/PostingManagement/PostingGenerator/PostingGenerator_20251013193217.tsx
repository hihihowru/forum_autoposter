import React, { useState } from 'react';
import { Card, Row, Col, Steps, Button, Space, message, Spin } from 'antd';
import { 
  ArrowLeftOutlined, 
  ArrowRightOutlined, 
  EyeOutlined, 
  SaveOutlined, 
  FileTextOutlined,
  RocketOutlined
} from '@ant-design/icons';
import PostingManagementAPI from '../../../services/postingManagementAPI';
import PostReviewPage from '../PostReview/PostReviewPage';
// import { usePostingStore, GeneratedPost } from '../../../stores/postingStore';

// 導入步驟組件
import TriggerSelector from './TriggerSelector';
import DataSourceSelector from './DataSourceSelector';
import ExplainabilityConfig from './ExplainabilityConfig';
import NewsConfig from './NewsConfig';
import KOLSelector from './KOLSelector';
import GenerationSettings from './GenerationSettings';
import TagSettings from './TagSettings';
import BatchModeSettings from './BatchModeSettings';
import AfterHoursLimitUpDisplay from './AfterHoursLimitUpDisplay';
import TrendingTopicsDisplay from './TrendingTopicsDisplay';
import KOLPromptTuner from './KOLPromptTuner';

interface GenerationConfig {
  triggers: any;
  dataSources: any;
  explainability: any;
  news: any;
  kol: any;
  settings: any;
  tags: any;
  batchMode: any;
}

interface PostingGeneratorProps {
  onGenerate?: (config: GenerationConfig) => Promise<void>;
  onSaveTemplate?: (template: any) => void;
  onLoadTemplate?: (templateId: string) => void;
  loading?: boolean;
}

const PostingGenerator: React.FC<PostingGeneratorProps> = ({
  onGenerate,
  onSaveTemplate,
  onLoadTemplate,
  loading = false
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [showReviewPage, setShowReviewPage] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  // const { addGeneratedPosts } = usePostingStore();
  const [generationConfig, setGenerationConfig] = useState<GenerationConfig>({
    triggers: {
      triggerConfig: undefined,
      threshold: 1000,
      changeThreshold: undefined,
      sectorSelection: undefined,
      industrySelection: undefined,
      filters: undefined,
      stock_codes: [],
      stock_names: [],
      stockCountLimit: 10,
      stockFilterCriteria: []
    },
    dataSources: {},
    explainability: {
      summarizer_enabled: true,
      data_extractor_enabled: true,
      prompt_templates: [],
      selected_template: 'stock_price_basic',
      technical_indicators: ['MACD', 'RSI'],
      custom_prompt: '',
      explainability_level: 'detailed'
    },
    news: {
      max_links: 5,
      search_keywords: [
        {
          id: '1',
          keyword: '{stock_name}',
          type: 'stock_name',
          description: '股票名稱'
        },
        {
          id: '2',
          keyword: '漲停',
          type: 'trigger_keyword',
          description: '觸發關鍵字'
        }
      ],
      use_realtime_news_api: true,
      search_templates: []
    },
    kol: {
      assignment_mode: 'fixed',
      selected_kols: [],
      dynamic_criteria: {
        style_preference: 'balanced',
        expertise_match: 'high',
        activity_level: 'active'
      },
      max_kols_per_post: 1
    },
    kolPrompts: [],
    settings: {
      post_mode: 'one_to_one',
      content_length: 'medium',
      max_stocks_per_post: 1,
      content_style: 'professional',
      include_analysis_depth: true,
      max_words: 1000,
      include_charts: false,
      include_risk_warning: true
    },
    tags: {
      tag_mode: 'stock_tags',
      stock_tags: {
        auto_generate: true,
        include_stock_code: true,
        include_stock_name: true,
        custom_tags: [],
        batch_shared_tags: false  // 預設關閉，用戶可手動開啟
      },
      topic_tags: {
        auto_generate: false,
        trending_topics: [],
        custom_tags: []
      },
      max_tags_per_post: 5
    },
    batchMode: {
      batch_type: 'test_mode',
      max_posts_per_batch: 10,
      generation_strategy: 'one_kol_one_stock', // 1個KOL為每檔股票生成獨立貼文
      review_required: true,
      auto_approve_threshold: 0.8,
      publish_delay_minutes: 5,
      quality_check_enabled: true,
      ai_detection_enabled: true,
      shared_commodity_tags: true  // 啟用同 batch 共享股票標籤
    }
  });

  const steps = [
    { title: '觸發器選擇', description: '選擇內容觸發器' },
    { title: '數據源配置', description: '配置數據來源' },
    { title: '解釋層設定', description: '設定可解釋性' },
    { title: '新聞搜尋', description: '配置新聞搜尋' },
    { title: 'KOL 選擇', description: '選擇 KOL' },
    { title: 'KOL Prompt 微調', description: '微調 KOL Prompt' },
    { title: '生成設定', description: '配置生成參數' },
    { title: '標籤設定', description: '設定標籤' },
    { title: '批量模式', description: '配置批量生成' }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleConfigChange = (stepKey: string, config: any) => {
    try {
      console.log(`更新配置 ${stepKey}:`, config);
      setGenerationConfig(prev => ({
        ...prev,
        [stepKey]: config
      }));
    } catch (error) {
      console.error(`配置更新錯誤 ${stepKey}:`, error);
      message.error(`配置更新失敗: ${stepKey}`);
    }
  };

  const handleGenerate = async () => {
    try {
      message.loading('正在生成內容...', 0);
      
      // 調試信息
      console.log('生成配置:', generationConfig);
      console.log('觸發器配置:', generationConfig.triggers);
      console.log('股票代號:', generationConfig.triggers?.stock_codes);
      console.log('KOL配置:', generationConfig.kol);
      
      // 驗證必要配置
      // 檢查是否為熱門話題觸發器
      const isTrendingTopicTrigger = generationConfig.triggers?.triggerConfig?.triggerKey === 'trending_topics';
      
      // 只有在非熱門話題模式下才強制要求選擇股票
      if (!isTrendingTopicTrigger && (!generationConfig.triggers?.stock_codes || generationConfig.triggers.stock_codes.length === 0)) {
        message.destroy();
        message.error('請先選擇股票');
        console.error('股票驗證失敗:', {
          stock_codes: generationConfig.triggers?.stock_codes,
          triggers: generationConfig.triggers
        });
        return;
      }
      
      // 熱門話題模式下的特殊驗證
      if (isTrendingTopicTrigger) {
        const selectedTopics = generationConfig.triggers?.selectedTopics || [];
        if (selectedTopics.length === 0) {
          message.destroy();
          message.error('請先選擇要生成的熱門話題');
          console.error('熱門話題驗證失敗:', {
            selectedTopics,
            triggers: generationConfig.triggers
          });
          return;
        }
        console.log('✅ 熱門話題模式驗證通過:', {
          selectedTopics: selectedTopics.length,
          topics: selectedTopics.map(t => ({ id: t.id, title: t.title }))
        });
      }
      
      if (!generationConfig.kol?.selected_kols || generationConfig.kol.selected_kols.length === 0) {
        message.destroy();
        message.error('請先選擇 KOL');
        console.error('KOL驗證失敗:', generationConfig.kol);
        return;
      }
      
      // 根據批量模式設定決定生成策略
      const batchMode = generationConfig.batchMode;
      const stockCodes = generationConfig.triggers.stock_codes;
      const stockNames = generationConfig.triggers.stock_names || [];
      const selectedKOLs = generationConfig.kol.selected_kols;
      
      console.log('批量生成配置:', {
        batchMode,
        stockCodes,
        stockNames,
        selectedKOLs,
        generationStrategy: batchMode.generation_strategy,
        fullTriggersConfig: generationConfig.triggers
      });
      
      // 創建發文會話
      const session = await PostingManagementAPI.createSession({
        session_name: `批量發文_${new Date().toLocaleString()}`,
        trigger_type: generationConfig.triggers?.triggerConfig?.triggerType || 'custom_stocks',
        trigger_data: generationConfig.triggers,
        config: generationConfig
      });
      
      // 檢查 session 是否有效
      if (!session || !session.id) {
        throw new Error('創建會話失敗：無效的會話ID');
      }
      
      console.log('✅ 會話創建成功:', session);
      
      // 根據觸發器類型創建貼文任務
      let postsToGenerate = [];
      
      // 確保 selectedKOLs 是數字數組
      const kolSerials = selectedKOLs.map(kol => 
        typeof kol === 'object' ? kol.serial || kol.kol_serial : kol
      ).filter(serial => serial != null);
      
      console.log('處理後的KOL序號:', kolSerials);
      
      if (isTrendingTopicTrigger) {
        // 熱門話題觸發器：為每個選中的話題生成貼文
        console.log('🔥 熱門話題觸發器模式');
        
        // 獲取選中的話題（從 TrendingTopicsDisplay 傳遞）
        const selectedTopics = generationConfig.triggers?.selectedTopics || [];
        
        if (selectedTopics.length === 0) {
          message.destroy();
          message.error('請先選擇要生成的熱門話題');
          return;
        }
        
        // 為每個選中的話題生成貼文
        for (const topic of selectedTopics) {
          if (topic.stock_ids && topic.stock_ids.length > 0) {
            // 有股票的話題：為每個股票生成一篇貼文
            for (const stockId of topic.stock_ids) {
              const stockName = stockId === 'TWA00' ? '台指期' : `股票${stockId}`;
              const postData = {
                stock_code: stockId,
                stock_name: stockName,
                kol_serial: kolSerials[0] || '201', // 使用第一個KOL或默認KOL
                session_id: session.id,
                topic_id: topic.id,
                topic_title: topic.title
              };
              console.log('➕ 添加話題貼文:', postData);
              postsToGenerate.push(postData);
            }
          } else {
            // 純話題：生成一篇貼文
            const postData = {
              stock_code: `TOPIC_${topic.id}`,
              stock_name: topic.title,
              kol_serial: kolSerials[0] || '201',
              session_id: session.id,
              topic_id: topic.id,
              topic_title: topic.title
            };
            console.log('➕ 添加純話題貼文:', postData);
            postsToGenerate.push(postData);
          }
        }
      } else if (batchMode.generation_strategy === 'one_kol_one_stock') {
        // 1:1 對應：每支股票對應一個 KOL
        console.log('🔄 使用one_kol_one_stock策略:', {
          stockCodes,
          kolSerials,
          stockNames
        });
        
        // 如果只有一個KOL，為每個股票生成一篇貼文，都使用同一個KOL
        if (kolSerials.length === 1) {
          console.log('📝 單KOL多股票模式');
          for (const stockCode of stockCodes) {
            const postData = {
              stock_code: stockCode,
              stock_name: stockNames[stockCodes.indexOf(stockCode)] || `股票${stockCode}`,
              kol_serial: kolSerials[0], // 使用唯一的KOL
              session_id: session.id
            };
            console.log('➕ 添加貼文:', postData);
            postsToGenerate.push(postData);
          }
        } else {
          // 多KOL模式：為每個股票分配一個KOL
          console.log('📝 多KOL多股票模式');
          const minLength = Math.min(stockCodes.length, kolSerials.length);
          for (let i = 0; i < minLength; i++) {
            const postData = {
              stock_code: stockCodes[i],
              stock_name: stockNames[i] || `股票${stockCodes[i]}`,
              kol_serial: kolSerials[i],
              session_id: session.id
            };
            console.log('➕ 添加貼文:', postData);
            postsToGenerate.push(postData);
          }
        }
      } else if (batchMode.generation_strategy === 'one_kol_all_stocks') {
        // 1個KOL對應所有股票
        console.log('🔄 使用one_kol_all_stocks策略:', {
          stockCodes,
          kolSerials,
          stockNames
        });
        
        // 如果只有一個股票但多個KOL，為每個KOL生成一篇貼文
        if (stockCodes.length === 1 && kolSerials.length > 1) {
          console.log('📝 單股票多KOL模式');
          for (const kolSerial of kolSerials) {
            postsToGenerate.push({
              stock_code: stockCodes[0],
              stock_name: stockNames[0] || `股票${stockCodes[0]}`,
              kol_serial: kolSerial,
              session_id: session.id
            });
          }
        } else {
          // 正常模式：為每個股票生成一篇貼文，都使用同一個KOL
          console.log('📝 多股票單KOL模式');
          for (const stockCode of stockCodes) {
            const postData = {
              stock_code: stockCode,
              stock_name: stockNames[stockCodes.indexOf(stockCode)] || `股票${stockCode}`,
              kol_serial: kolSerials[0], // 使用第一個KOL
              session_id: session.id
            };
            console.log('➕ 添加貼文:', postData);
            postsToGenerate.push(postData);
          }
        }
      } else {
        // 混合模式：循環分配KOL
        // 如果只有一個股票但多個KOL，為每個KOL生成一篇貼文
        if (stockCodes.length === 1 && kolSerials.length > 1) {
          for (const kolSerial of kolSerials) {
            postsToGenerate.push({
              stock_code: stockCodes[0],
              stock_name: stockNames[0] || `股票${stockCodes[0]}`,
              kol_serial: kolSerial,
              session_id: session.id
            });
          }
        } else {
          // 正常混合模式：為每個股票分配KOL
          for (let i = 0; i < stockCodes.length; i++) {
            const kolIndex = i % kolSerials.length;
            postsToGenerate.push({
              stock_code: stockCodes[i],
              stock_name: stockNames[i] || `股票${stockCodes[i]}`,
              kol_serial: kolSerials[kolIndex],
              session_id: session.id
            });
          }
        }
      }
      
      console.log('準備生成的貼文:', postsToGenerate);
      
      // 立即跳轉到審核頁面（不等待所有貼文生成完成）
      if (batchMode.batch_type === 'test_mode' || batchMode.batch_type === 'review_mode') {
        console.log('🚀 立即跳轉到審核頁面，貼文將異步生成');
        setCurrentSessionId(session.id);
        setShowReviewPage(true);
        message.info('正在生成貼文，請稍候...');
      }
      
      // 異步批量生成貼文（不阻塞UI）
      // 添加調試信息
      console.log('🔍 前端調試 - 批量生成貼文參數:');
      console.log('  - session_id:', session.id);
      console.log('  - posts:', postsToGenerate);
      console.log('  - batch_config:', batchMode);
      console.log('  - tags_config:', generationConfig.tags);
      console.log('  - topic_tags:', generationConfig.tags?.topic_tags);
      console.log('  - mixed_mode:', generationConfig.tags?.topic_tags?.mixed_mode);
      console.log('  - trigger_type:', generationConfig.triggers?.triggerConfig?.triggerType);
      console.log('  - trigger_key:', generationConfig.triggers?.triggerConfig?.triggerKey);
      console.log('  - full_triggers_config:', generationConfig.triggers);
      
      // 根據觸發器類型設置 topic_id
      const batchConfigWithTopic = {
        ...batchMode,
        topic_id: generationConfig.triggers?.triggerConfig?.triggerKey === 'trending_topics' ? 'auto_fetch' : null,
        topic_title: generationConfig.triggers?.triggerConfig?.triggerKey === 'trending_topics' ? '自動獲取熱門話題' : null
      };
      
      console.log('🔍 批量生成配置（包含 topic_id）:', batchConfigWithTopic);
      
      PostingManagementAPI.generateBatchPosts({
        session_id: session.id,
        posts: postsToGenerate,
        batch_config: batchConfigWithTopic,
        data_sources: generationConfig.dataSources,
        explainability_config: generationConfig.explainability,
        news_config: generationConfig.news,
        tags_config: generationConfig.tags  // 新增：傳送標籤配置
      }).then(result => {
        message.destroy();
        
        if (result.success) {
          message.success(`批量生成完成！成功生成 ${result.generated_count} 篇貼文`);
          
          if (result.errors && result.errors.length > 0) {
            message.warning(`有 ${result.failed_count || 0} 篇貼文生成失敗`);
          }
        } else {
          message.error('批量生成失敗');
        }
      }).catch(error => {
        message.destroy();
        message.error(`批量生成失敗: ${error.message}`);
      });
      
      return; // 提前返回，不執行後續的同步邏輯
      
    } catch (error) {
      message.destroy();
      console.error('批量生成失敗:', error);
      message.error('批量生成失敗，請重試');
    }
  };

  // 根據KOL人設生成標題後綴
  const getTitleSuffix = (persona: string): string => {
    const suffixes = {
      '技術派': '技術面強勢突破',
      '總經派': '基本面分析看好',
      '消息派': '內線消息曝光',
      '散戶派': '散戶心聲分享',
      '地方派': '在地人觀點',
      '八卦派': '八卦內幕爆料',
      '爆料派': '獨家消息曝光',
      '新聞派': '新聞分析報導',
      '數據派': '數據統計分析',
      '短線派': '短線操作機會',
      '價值派': '價值投資機會'
    };
    return suffixes[persona] || '市場分析';
  };

  // 根據KOL人設生成內容
  const generateContent = (kol: any, stockName: string, stockCode: string): string => {
    const baseContent = `${stockName}(${stockCode}) `;
    
    const contentTemplates = {
      '技術派': `${baseContent}從技術面來看，MACD出現黃金交叉，均線呈現多頭排列，成交量放大，技術指標顯示強勢突破信號。`,
      '總經派': `${baseContent}從基本面分析來看，營收成長超預期，財務指標穩健，長期投資價值顯現。`,
      '消息派': `${baseContent}聽說有內線消息...這個消息如果屬實，股價應該會有不錯的表現。`,
      '散戶派': `${baseContent}今天又看到這檔股票，散戶的悲哀就是總是在追高殺低...`,
      '地方派': `${baseContent}在地人告訴你，這家公司在新北地區的布局很積極，值得關注。`,
      '八卦派': `${baseContent}八卦一下，聽說這家公司最近有一些內幕消息...`,
      '爆料派': `${baseContent}獨家爆料！這家公司的最新動向，內幕消息曝光。`,
      '新聞派': `${baseContent}新聞報導指出，該公司最新發展動向值得關注。`,
      '數據派': `${baseContent}數據顯示，該公司各項指標表現優異，統計分析結果看好。`,
      '短線派': `${baseContent}短線操作機會來了，隔日沖的好標的。`,
      '價值派': `${baseContent}長線價值投資的好機會，基本面穩健。`
    };
    
    return contentTemplates[kol.persona] || `${baseContent}市場分析顯示投資機會。`;
  };

  const handleSaveTemplate = () => {
    if (onSaveTemplate) {
      onSaveTemplate(generationConfig);
      message.success('模板已儲存');
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div>
            <TriggerSelector
              value={generationConfig.triggers}
              onChange={(config) => handleConfigChange('triggers', config)}
            />
            
            {/* 盤後漲停股票顯示 */}
            {(generationConfig.triggers.limit_up_after_hours_high_volume || 
              generationConfig.triggers.limit_up_after_hours_low_volume) && (
              <div style={{ marginTop: '24px' }}>
                <AfterHoursLimitUpDisplay
                  triggerConfig={generationConfig.triggers}
                  onStockSelect={(stocks) => {
                    const stockCodes = stocks.map(s => s.stock_code);
                    const stockNames = stocks.map(s => s.stock_name);
                    handleConfigChange('triggers', {
                      ...generationConfig.triggers,
                      stock_codes: stockCodes,
                      stock_names: stockNames
                    });
                  }}
                />
              </div>
            )}
            
            {/* 熱門話題顯示 */}
            {generationConfig.triggers.triggerConfig?.triggerKey === 'trending_topics' && (
              <div style={{ marginTop: '24px' }}>
                <TrendingTopicsDisplay
                  triggerConfig={generationConfig.triggers}
                  onStockSelect={(stocks) => {
                    const stockCodes = stocks.map(s => s.code);
                    const stockNames = stocks.map(s => s.name);
                    handleConfigChange('triggers', {
                      ...generationConfig.triggers,
                      stock_codes: stockCodes,
                      stock_names: stockNames
                    });
                  }}
                  onSelectedTopicsChange={(topics) => {
                    handleConfigChange('triggers', {
                      ...generationConfig.triggers,
                      selectedTopics: topics
                    });
                  }}
                  onTopicSelect={(topic) => {
                    // 處理話題選擇，為該話題生成專屬貼文
                    console.log('選擇的話題:', topic);
                    
                    // 創建該話題的貼文配置
                    const topicPosts = [];
                    
                    if (topic.stock_ids && topic.stock_ids.length > 0) {
                      // 為話題的每個股票生成貼文
                      topic.stock_ids.forEach((stockId, index) => {
                        const stockName = stockId === 'TWA00' ? '台指期' : `股票${stockId}`;
                        topicPosts.push({
                          stock_code: stockId,
                          stock_name: stockName,
                          kol_serial: '201', // 使用默認 KOL
                          session_id: Date.now() + index // 確保每個貼文有不同的 session_id
                        });
                      });
                    } else {
                      // 純話題，沒有關聯股票
                      topicPosts.push({
                        stock_code: `TOPIC_${topic.id}`,
                        stock_name: topic.title,
                        kol_serial: '201',
                        session_id: Date.now()
                      });
                    }
                    
                    // 使用批量生成 API 來生成該話題的貼文
                    PostingManagementAPI.generateBatchPosts({
                      session_id: Date.now(),
                      posts: topicPosts,
                      batch_config: {
                        batch_type: 'trending_topic',
                        kol_persona: 'technical',
                        content_style: 'trending_analysis',
                        target_audience: 'active_traders',
                        topic_id: topic.id,
                        topic_title: topic.title
                      },
                      data_sources: generationConfig.dataSources,
                      explainability_config: generationConfig.explainability,
                      news_config: generationConfig.news,
                      tags_config: generationConfig.tags
                    })
                      .then(result => {
                        if (result.success) {
                          message.success(`話題「${topic.title}」的 ${topicPosts.length} 篇貼文生成成功！`);
                          console.log('生成的貼文:', result);
                        } else {
                          message.error('話題貼文生成失敗');
                        }
                      })
                      .catch(error => {
                        console.error('話題貼文生成失敗:', error);
                        message.error(`話題貼文生成失敗: ${error.message}`);
                      });
                  }}
                />
              </div>
            )}
          </div>
        );
      case 1:
        return (
          <DataSourceSelector
            value={generationConfig.dataSources}
            onChange={(config) => handleConfigChange('dataSources', config)}
          />
        );
      case 2:
        return (
          <ExplainabilityConfig
            value={generationConfig.explainability}
            onChange={(config) => handleConfigChange('explainability', config)}
          />
        );
      case 3:
        return (
          <NewsConfig
            value={generationConfig.news}
            onChange={(config) => handleConfigChange('news', config)}
            // 移除手動選擇的熱門話題，改為自動標記
          />
        );
      case 4:
        return (
          <KOLSelector
            value={generationConfig.kol}
            onChange={(config) => handleConfigChange('kol', config)}
          />
        );
      case 5:
        return (
          <KOLPromptTuner
            value={generationConfig.kolPrompts}
            onChange={(config) => handleConfigChange('kolPrompts', config)}
            selectedKOLs={generationConfig.kol?.selected_kols || []}
          />
        );
      case 6:
        return (
          <GenerationSettings
            value={generationConfig.settings}
            onChange={(config) => handleConfigChange('settings', config)}
          />
        );
      case 7:
        return (
          <TagSettings
            value={generationConfig.tags}
            onChange={(config) => handleConfigChange('tags', config)}
            triggerData={{
              stock_codes: generationConfig.triggers?.stock_codes,
              stock_names: generationConfig.triggers?.stock_names
            }}
            kolData={{
              kol_serials: generationConfig.kol?.selected_kols?.map((k: any) => k.serial),
              kol_names: generationConfig.kol?.selected_kols?.map((k: any) => k.nickname)
            }}
          />
        );
      case 8:
        return (
          <BatchModeSettings
            value={generationConfig.batchMode}
            onChange={(config) => handleConfigChange('batchMode', config)}
            onStartBatchGeneration={handleGenerate}
            loading={loading}
          />
        );
      default:
        return null;
    }
  };

  // 如果顯示審核頁面，則渲染審核頁面
  if (showReviewPage) {
    return (
      <PostReviewPage 
        sessionId={currentSessionId || undefined}
        onBack={() => {
          setShowReviewPage(false);
          setCurrentSessionId(null);
        }}
      />
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
          <Col>
            <Space>
              <RocketOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <div>
                <h2 style={{ margin: 0 }}>智能發文生成器</h2>
                <p style={{ margin: 0, color: '#666' }}>
                  配置發文參數，生成高品質內容
                </p>
              </div>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<FileTextOutlined />} onClick={handleSaveTemplate}>
                儲存模板
              </Button>
              <Button icon={<EyeOutlined />}>
                預覽設定
              </Button>
            </Space>
          </Col>
        </Row>

        {/* 步驟指示器 */}
        <Card size="small" style={{ marginBottom: '24px' }}>
          <Steps current={currentStep} items={steps} />
        </Card>

        {/* 當前步驟內容 */}
        <Card title={`步驟 ${currentStep + 1}: ${steps[currentStep].title}`}>
          <Spin spinning={loading}>
            {renderStepContent()}
          </Spin>
        </Card>

        {/* 操作按鈕 */}
        <Card size="small" style={{ marginTop: '24px' }}>
          <Row justify="space-between">
            <Col>
              <Button 
                icon={<ArrowLeftOutlined />} 
                onClick={handlePrev}
                disabled={currentStep === 0}
              >
                上一步
              </Button>
            </Col>
            <Col>
              <Space>
                {currentStep < steps.length - 1 ? (
                  <Button 
                    type="primary" 
                    icon={<ArrowRightOutlined />} 
                    onClick={handleNext}
                  >
                    下一步
                  </Button>
                ) : (
                  <Button 
                    type="primary" 
                    icon={<RocketOutlined />} 
                    onClick={handleGenerate}
                    loading={loading}
                    size="large"
                  >
                    開始生成
                  </Button>
                )}
              </Space>
            </Col>
          </Row>
        </Card>
      </Card>
    </div>
  );
};

export default PostingGenerator;
