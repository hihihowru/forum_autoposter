import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  Table,
  Tag,
  Statistic,
  Select,
  Space,
  Button,
  Input,
  DatePicker,
  Row,
  Col,
  Divider,
  Tooltip,
  Badge,
  Spin,
  message,
  Modal,
  Typography,
  Progress,
  Alert,
  List,
  Avatar,
  Switch,
  Timeline,
  Steps
} from 'antd';
import {
  LikeOutlined,
  MessageOutlined,
  ShareAltOutlined,
  EyeOutlined,
  UserOutlined,
  CalendarOutlined,
  ReloadOutlined,
  LinkOutlined,
  BarChartOutlined,
  FilterOutlined,
  ExportOutlined,
  ExperimentOutlined,
  ThunderboltOutlined,
  CrownOutlined,
  RocketOutlined,
  BulbOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ClockCircleOutlined,
  QuestionCircleOutlined,
  SmileOutlined,
  PlusOutlined,
  FileTextOutlined,
  FileOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import BatchScheduleModal from '../components/PostingManagement/BatchHistory/BatchScheduleModal';
import { getApiBaseUrl } from '../config/api';


const API_BASE_URL = getApiBaseUrl();
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Search } = Input;
const { RangePicker } = DatePicker;
const { Step } = Steps;

interface InteractionPost {
  post_id: string;
  article_id: string;
  kol_serial: number;
  kol_nickname: string;
  title: string;
  content: string;
  article_url: string;
  create_time: string;
  commodity_tags: Array<{key: string, type: string, bullOrBear: string}>;
  community_topic?: string;
  source: 'system' | 'external';
  status: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  bookmarks: number;
  donations?: number;
  engagement_rate: number;
}

interface FeatureRanking {
  feature: string;
  score: number;
  impact: 'high' | 'medium' | 'low';
  description: string;
  top20PercentValue: number;
  allPostsValue: number;
  improvement: number;
}

interface HighPerformanceFeature {
  feature_id: string;
  feature_name: string;
  feature_type: string;
  description: string;
  frequency_in_top_posts: number;
  frequency_in_all_posts: number;
  improvement_potential: number;
  setting_key: string;
  is_modifiable: boolean;
  modification_method: string;
  examples: string[];
}

interface ContentCategory {
  category_id: string;
  category_name: string;
  description: string;
  top_posts: any[];
  avg_performance_score: number;
  key_characteristics: string[];
  success_rate: number;
}

interface PostingSetting {
  setting_id: string;
  setting_name: string;
  description: string;
  trigger_type: string;
  content_length: string;
  has_news_link: boolean;
  has_question_interaction: boolean;
  has_emoji: boolean;
  has_hashtag: boolean;
  humor_level: string;
  kol_style: string;
  posting_time_preference: string[];
  stock_tags_count: number;
  content_structure: string;
  interaction_elements: string[];
  expected_performance: number;
  confidence_level: number;
  based_on_features: string[];
}

interface ExperimentConfig {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'paused';
  startDate: string;
  endDate: string;
  settings: {
    preferredTimeSlots: string[];
    contentLength: string;
    humorLevel: string;
    stockTags: string;
    features: string[];
    kolSelection: string[];
  };
  expectedEngagement: string;
  actualEngagement?: number;
  progress: number;
  color: string;
}

interface SelfLearningInsight {
  id: string;
  type: 'pattern' | 'recommendation' | 'warning' | 'success';
  title: string;
  description: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  action: string;
  timestamp: string;
}

const SelfLearningPage: React.FC = () => {
  const [posts, setPosts] = useState<InteractionPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // 篩選條件
  const [selectedKOL, setSelectedKOL] = useState<number | undefined>(undefined);
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [includeExternal, setIncludeExternal] = useState(true);
  
  // 自我學習狀態
  const [featureRankings, setFeatureRankings] = useState<FeatureRanking[]>([]);
  const [highPerformanceFeatures, setHighPerformanceFeatures] = useState<HighPerformanceFeature[]>([]);
  const [calculationResults, setCalculationResults] = useState<any>(null);
  const [contentCategories, setContentCategories] = useState<ContentCategory[]>([]);
  const [generatedSettings, setGeneratedSettings] = useState<PostingSetting[]>([]);
  const [experiments, setExperiments] = useState<ExperimentConfig[]>([]);
  const [insights, setInsights] = useState<SelfLearningInsight[]>([]);
  const [showFeatureAnalysis, setShowFeatureAnalysis] = useState(false);
  const [showCalculationResults, setShowCalculationResults] = useState(false);
  const [selectedFeaturesForExperiment, setSelectedFeaturesForExperiment] = useState<string[]>([]);
  const [autoLearningEnabled, setAutoLearningEnabled] = useState(true);
  
  // 排程 modal 狀態
  const [scheduleModalVisible, setScheduleModalVisible] = useState(false);
  const [selectedFeatureForSchedule, setSelectedFeatureForSchedule] = useState<HighPerformanceFeature | null>(null);
  
  // 智能實驗管理狀態
  const [showSmartExperiments, setShowSmartExperiments] = useState(false);
  const [smartExperiments, setSmartExperiments] = useState<any[]>([]);
  
  // 數據抓取狀態
  const [fetchingData, setFetchingData] = useState(false);

  // 計算總互動數
  const calculateTotalInteractions = (post: InteractionPost): number => {
    return (post.likes || 0) + (post.comments || 0) + (post.shares || 0) + (post.bookmarks || 0);
  };

  // 分析貼文特徵（重用互動分析頁面的邏輯）
  const analyzePostFeatures = (posts: InteractionPost[]) => {
    const features = {
      postingTime: { morning: 0, afternoon: 0, evening: 0, night: 0 },
      hasStockTags: 0,
      stockTagCount: 0,
      hasTrendingTopic: 0,
      avgContentLength: 0,
      shortContent: 0,
      mediumContent: 0,
      longContent: 0,
      hasHumorMode: 0,
      hasNewsLinks: 0,
      kolDistribution: {} as Record<string, number>,
      sourceDistribution: { system: 0, external: 0 },
      avgTotalInteractions: 0,
      avgLikes: 0,
      avgComments: 0,
      avgShares: 0,
      avgBookmarks: 0,
      avgViews: 0,
      avgEngagementRate: 0,
      avgTitleLength: 0,
      shortTitle: 0,
      mediumTitle: 0,
      longTitle: 0,
      hasEmoji: 0,
      hasHashtag: 0,
      hasQuestion: 0,
      hasExclamation: 0,
      hasNumber: 0,
      hasStockCode: 0,
      humorType: { none: 0, light: 0, moderate: 0, strong: 0 },
      hasParagraphs: 0,
      hasLineBreaks: 0,
      hasBulletPoints: 0,
      hasQuotes: 0
    };

    let totalContentLength = 0;
    let totalTitleLength = 0;
    let totalInteractions = 0;
    let totalLikes = 0;
    let totalComments = 0;
    let totalShares = 0;
    let totalBookmarks = 0;
    let totalViews = 0;
    let totalEngagementRate = 0;

    posts.forEach(post => {
      // 發文時間分析
      const postTime = new Date(post.create_time);
      const hour = postTime.getHours();
      if (hour >= 6 && hour < 12) features.postingTime.morning++;
      else if (hour >= 12 && hour < 18) features.postingTime.afternoon++;
      else if (hour >= 18 && hour < 24) features.postingTime.evening++;
      else features.postingTime.night++;

      // 股票標記分析
      if (post.commodity_tags && post.commodity_tags.length > 0) {
        features.hasStockTags++;
        features.stockTagCount += post.commodity_tags.length;
      }

      // 熱門話題分析
      if (post.community_topic) {
        features.hasTrendingTopic++;
      }

      // 內容長度分析
      const contentLength = post.content.length;
      totalContentLength += contentLength;
      if (contentLength < 200) features.shortContent++;
      else if (contentLength <= 500) features.mediumContent++;
      else features.longContent++;

      // 標題分析
      const titleLength = post.title.length;
      totalTitleLength += titleLength;
      if (titleLength < 20) features.shortTitle++;
      else if (titleLength <= 40) features.mediumTitle++;
      else features.longTitle++;

      // 文章架構分析
      const fullText = post.title + ' ' + post.content;
      
      // Emoji檢測
      const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u;
      if (emojiRegex.test(fullText)) features.hasEmoji++;

      // Hashtag檢測
      if (fullText.includes('#')) features.hasHashtag++;

      // 問號檢測
      if (fullText.includes('？') || fullText.includes('?')) features.hasQuestion++;

      // 驚嘆號檢測
      if (fullText.includes('！') || fullText.includes('!')) features.hasExclamation++;

      // 數字檢測
      if (/\d/.test(fullText)) features.hasNumber++;

      // 股票代碼檢測
      if (/\d{4}/.test(fullText)) features.hasStockCode++;

      // 內容結構分析
      if (post.content.includes('\n\n')) features.hasParagraphs++;
      if (post.content.includes('\n')) features.hasLineBreaks++;
      if (post.content.includes('•') || post.content.includes('-') || post.content.includes('*')) features.hasBulletPoints++;
      if (post.content.includes('"') || post.content.includes('「') || post.content.includes('『')) features.hasQuotes++;

      // 幽默型內容分析
      const humorKeywords = ['哈哈', '笑死', '搞笑', '幽默', '有趣', '😂', '😄', '😆', 'XD', 'LOL'];
      const hasHumor = humorKeywords.some(keyword => 
        post.content.includes(keyword) || post.title.includes(keyword)
      );
      if (hasHumor) features.hasHumorMode++;

      // 新聞連結檢測
      if (post.content.includes('http') || post.content.includes('www.') || post.content.includes('新聞')) {
        features.hasNewsLinks++;
      }

      // KOL分布
      const kolName = post.kol_nickname;
      features.kolDistribution[kolName] = (features.kolDistribution[kolName] || 0) + 1;

      // 來源分布
      if (post.source === 'system') features.sourceDistribution.system++;
      else features.sourceDistribution.external++;

      // 互動數據統計
      const postTotalInteractions = calculateTotalInteractions(post);
      totalInteractions += postTotalInteractions;
      totalLikes += post.likes || 0;
      totalComments += post.comments || 0;
      totalShares += post.shares || 0;
      totalBookmarks += post.bookmarks || 0;
      totalViews += post.views || 0;
      totalEngagementRate += post.engagement_rate || 0;
    });

    // 計算平均值
    features.avgContentLength = Math.round(totalContentLength / posts.length);
    features.avgTitleLength = Math.round(totalTitleLength / posts.length);
    features.avgTotalInteractions = totalInteractions / posts.length;
    features.avgLikes = totalLikes / posts.length;
    features.avgComments = totalComments / posts.length;
    features.avgShares = totalShares / posts.length;
    features.avgBookmarks = totalBookmarks / posts.length;
    features.avgViews = totalViews / posts.length;
    features.avgEngagementRate = totalEngagementRate / posts.length;

    // 轉換為百分比
    const convertToPercentage = (count: number) => 
      Math.round((count / posts.length) * 100);

    return {
      totalPosts: posts.length,
      features: {
        ...features,
        postingTime: {
          morning: convertToPercentage(features.postingTime.morning),
          afternoon: convertToPercentage(features.postingTime.afternoon),
          evening: convertToPercentage(features.postingTime.evening),
          night: convertToPercentage(features.postingTime.night)
        },
        hasStockTags: convertToPercentage(features.hasStockTags),
        hasTrendingTopic: convertToPercentage(features.hasTrendingTopic),
        shortContent: convertToPercentage(features.shortContent),
        mediumContent: convertToPercentage(features.mediumContent),
        longContent: convertToPercentage(features.longContent),
        hasHumorMode: convertToPercentage(features.hasHumorMode),
        hasNewsLinks: convertToPercentage(features.hasNewsLinks),
        avgStockTagsPerPost: features.stockTagCount / posts.length,
        sourceDistribution: {
          system: convertToPercentage(features.sourceDistribution.system),
          external: convertToPercentage(features.sourceDistribution.external)
        }
      }
    };
  };

  // 基於真實貼文數據分析高成效特徵 - 完整版
  const analyzeHighPerformanceFeaturesFromPosts = (posts: any[]) => {
    if (!posts || posts.length === 0) return [];
    
    // 計算每篇貼文的成效分數
    const scoredPosts = posts.map(post => {
      const totalInteractions = (post.likes || 0) + (post.comments || 0) + (post.shares || 0) + (post.views || 0) + (post.donations || 0);
      return { ...post, performanceScore: totalInteractions };
    });
    
    // 按分數排序
    scoredPosts.sort((a, b) => b.performanceScore - a.performanceScore);
    
    // 取前20%進行分析
    const top20Count = Math.max(1, Math.floor(scoredPosts.length * 0.2));
    const top20Posts = scoredPosts.slice(0, top20Count);
    const allPosts = scoredPosts;
    
    console.log(`🎯 前20%貼文數量: ${top20Count}, 總貼文數: ${allPosts.length}`);
    
    // 分析所有特徵
    const features = [];
    
    // ==================== 內容特徵 ====================
    
    // 1. 問句互動特徵
    const top20Questions = top20Posts.filter(post => 
      (post.title && (post.title.includes('？') || post.title.includes('?'))) ||
      (post.content && (post.content.includes('？') || post.content.includes('?')))
    ).length;
    const allQuestions = allPosts.filter(post => 
      (post.title && (post.title.includes('？') || post.title.includes('?'))) ||
      (post.content && (post.content.includes('？') || post.content.includes('?')))
    ).length;
    
    const questionFrequency = top20Questions / top20Posts.length;
    const allQuestionFrequency = allQuestions / allPosts.length;
    const questionImprovement = questionFrequency - allQuestionFrequency;
    
    if (questionImprovement > 0) {
      features.push({
        feature_id: 'has_question',
        feature_name: '問句互動',
        feature_type: 'interaction',
        description: '包含問句的貼文互動率較高',
        frequency_in_top_posts: questionFrequency,
        frequency_in_all_posts: allQuestionFrequency,
        improvement_potential: questionImprovement,
        setting_key: 'include_questions',
        is_modifiable: true,
        modification_method: '在內容生成中加入問句',
        examples: top20Posts
          .filter(post => (post.title && (post.title.includes('？') || post.title.includes('?'))) || (post.content && (post.content.includes('？') || post.content.includes('?'))))
          .slice(0, 3)
          .map(post => post.title)
      });
    }
    
    // 2. 表情符號特徵
    const emojiPattern = /[😂😄😆👍👏🔥💰📈📊💡🎯]/;
    const top20Emojis = top20Posts.filter(post => 
      (post.title && emojiPattern.test(post.title)) ||
      (post.content && emojiPattern.test(post.content))
    ).length;
    const allEmojis = allPosts.filter(post => 
      (post.title && emojiPattern.test(post.title)) ||
      (post.content && emojiPattern.test(post.content))
    ).length;
    
    const emojiFrequency = top20Emojis / top20Posts.length;
    const allEmojiFrequency = allEmojis / allPosts.length;
    const emojiImprovement = emojiFrequency - allEmojiFrequency;
    
    if (emojiImprovement > 0) {
      features.push({
        feature_id: 'has_emoji',
        feature_name: '表情符號',
        feature_type: 'interaction',
        description: '使用表情符號的貼文更受歡迎',
        frequency_in_top_posts: emojiFrequency,
        frequency_in_all_posts: allEmojiFrequency,
        improvement_potential: emojiImprovement,
        setting_key: 'include_emoji',
        is_modifiable: true,
        modification_method: '在內容生成中加入表情符號',
        examples: ['😂', '😄', '👍', '👏', '📈', '📊']
      });
    }
    
    // 3. 標籤使用特徵
    const top20Hashtags = top20Posts.filter(post => 
      (post.title && post.title.includes('#')) ||
      (post.content && post.content.includes('#'))
    ).length;
    const allHashtags = allPosts.filter(post => 
      (post.title && post.title.includes('#')) ||
      (post.content && post.content.includes('#'))
    ).length;
    
    const hashtagFrequency = top20Hashtags / top20Posts.length;
    const allHashtagFrequency = allHashtags / allPosts.length;
    const hashtagImprovement = hashtagFrequency - allHashtagFrequency;
    
    if (hashtagImprovement > 0) {
      features.push({
        feature_id: 'has_hashtag',
        feature_name: '標籤使用',
        feature_type: 'interaction',
        description: '使用標籤的貼文互動率較高',
        frequency_in_top_posts: hashtagFrequency,
        frequency_in_all_posts: allHashtagFrequency,
        improvement_potential: hashtagImprovement,
        setting_key: 'include_hashtag',
        is_modifiable: true,
        modification_method: '在內容生成中加入標籤',
        examples: ['#鄉民觀點', '#PTT', '#股市討論', '#技術分析']
      });
    }
    
    // 4. 內容長度特徵 - 短內容
    const top20Short = top20Posts.filter(post => {
      const contentLength = (post.content || '').length;
      return contentLength < 200;
    }).length;
    const allShort = allPosts.filter(post => {
      const contentLength = (post.content || '').length;
      return contentLength < 200;
    }).length;
    
    const shortFrequency = top20Short / top20Posts.length;
    const allShortFrequency = allShort / allPosts.length;
    const shortImprovement = shortFrequency - allShortFrequency;
    
    if (shortImprovement > 0) {
      features.push({
        feature_id: 'content_length_short',
        feature_name: '短內容',
        feature_type: 'content',
        description: '200字以下的短內容效果較好',
        frequency_in_top_posts: shortFrequency,
        frequency_in_all_posts: allShortFrequency,
        improvement_potential: shortImprovement,
        setting_key: 'content_length',
        is_modifiable: true,
        modification_method: '調整內容生成為短內容',
        examples: ['簡潔明瞭的觀點', '重點摘要']
      });
    }
    
    // 5. 內容長度特徵 - 中等內容
    const top20Medium = top20Posts.filter(post => {
      const contentLength = (post.content || '').length;
      return contentLength >= 200 && contentLength <= 500;
    }).length;
    const allMedium = allPosts.filter(post => {
      const contentLength = (post.content || '').length;
      return contentLength >= 200 && contentLength <= 500;
    }).length;
    
    const mediumFrequency = top20Medium / top20Posts.length;
    const allMediumFrequency = allMedium / allPosts.length;
    const mediumImprovement = mediumFrequency - allMediumFrequency;
    
    if (mediumImprovement > 0) {
      features.push({
        feature_id: 'content_length_medium',
        feature_name: '中等長度內容',
        feature_type: 'content',
        description: '200-500字的內容效果最佳',
        frequency_in_top_posts: mediumFrequency,
        frequency_in_all_posts: allMediumFrequency,
        improvement_potential: mediumImprovement,
        setting_key: 'content_length',
        is_modifiable: true,
        modification_method: '調整內容生成長度設定',
        examples: ['適中的分析內容', '詳細但不冗長']
      });
    }
    
    // 6. 技術分析關鍵詞
    const techKeywords = ['技術', '分析', '指標', '支撐', '阻力', 'MACD', 'RSI', 'KD', 'MA', '趨勢'];
    const top20Tech = top20Posts.filter(post => {
      const text = `${post.title || ''} ${post.content || ''}`;
      return techKeywords.some(keyword => text.includes(keyword));
    }).length;
    const allTech = allPosts.filter(post => {
      const text = `${post.title || ''} ${post.content || ''}`;
      return techKeywords.some(keyword => text.includes(keyword));
    }).length;
    
    const techFrequency = top20Tech / top20Posts.length;
    const allTechFrequency = allTech / allPosts.length;
    const techImprovement = techFrequency - allTechFrequency;
    
    if (techImprovement > 0) {
      features.push({
        feature_id: 'has_technical_analysis',
        feature_name: '技術分析',
        feature_type: 'content',
        description: '包含技術分析關鍵詞的貼文更受歡迎',
        frequency_in_top_posts: techFrequency,
        frequency_in_all_posts: allTechFrequency,
        improvement_potential: techImprovement,
        setting_key: 'include_technical_analysis',
        is_modifiable: true,
        modification_method: '在內容中加入技術分析元素',
        examples: ['技術指標分析', '支撐阻力位', '趨勢判斷']
      });
    }
    
    // ==================== 時間特徵 ====================
    
    // 7. 上午發文
    const top20Morning = top20Posts.filter(post => {
      if (!post.create_time) return false;
      const hour = new Date(post.create_time).getHours();
      return hour >= 6 && hour < 12;
    }).length;
    const allMorning = allPosts.filter(post => {
      if (!post.create_time) return false;
      const hour = new Date(post.create_time).getHours();
      return hour >= 6 && hour < 12;
    }).length;
    
    const morningFrequency = top20Morning / top20Posts.length;
    const allMorningFrequency = allMorning / allPosts.length;
    const morningImprovement = morningFrequency - allMorningFrequency;
    
    if (morningImprovement > 0) {
      features.push({
        feature_id: 'morning_posting',
        feature_name: '上午發文',
        feature_type: 'timing',
        description: '上午時段發文的互動率較高',
        frequency_in_top_posts: morningFrequency,
        frequency_in_all_posts: allMorningFrequency,
        improvement_potential: morningImprovement,
        setting_key: 'preferred_time',
        is_modifiable: true,
        modification_method: '調整發文時間為上午時段',
        examples: ['09:00-11:00', '開盤時段']
      });
    }
    
    // 8. 下午發文
    const top20Afternoon = top20Posts.filter(post => {
      if (!post.create_time) return false;
      const hour = new Date(post.create_time).getHours();
      return hour >= 12 && hour < 18;
    }).length;
    const allAfternoon = allPosts.filter(post => {
      if (!post.create_time) return false;
      const hour = new Date(post.create_time).getHours();
      return hour >= 12 && hour < 18;
    }).length;
    
    const afternoonFrequency = top20Afternoon / top20Posts.length;
    const allAfternoonFrequency = allAfternoon / allPosts.length;
    const afternoonImprovement = afternoonFrequency - allAfternoonFrequency;
    
    if (afternoonImprovement > 0) {
      features.push({
        feature_id: 'afternoon_posting',
        feature_name: '下午發文',
        feature_type: 'timing',
        description: '下午時段發文的互動率較高',
        frequency_in_top_posts: afternoonFrequency,
        frequency_in_all_posts: allAfternoonFrequency,
        improvement_potential: afternoonImprovement,
        setting_key: 'preferred_time',
        is_modifiable: true,
        modification_method: '調整發文時間為下午時段',
        examples: ['14:00-16:00', '收盤時段']
      });
    }
    
    // ==================== 來源特徵 ====================
    
    // 9. 系統貼文
    const top20System = top20Posts.filter(post => post.source === 'system').length;
    const allSystem = allPosts.filter(post => post.source === 'system').length;
    
    const systemFrequency = top20System / top20Posts.length;
    const allSystemFrequency = allSystem / allPosts.length;
    const systemImprovement = systemFrequency - allSystemFrequency;
    
    if (systemImprovement > 0) {
      features.push({
        feature_id: 'system_source',
        feature_name: '系統貼文',
        feature_type: 'source',
        description: '系統生成的貼文互動率較高',
        frequency_in_top_posts: systemFrequency,
        frequency_in_all_posts: allSystemFrequency,
        improvement_potential: systemImprovement,
        setting_key: 'content_source',
        is_modifiable: false,
        modification_method: '使用系統生成內容',
        examples: ['AI生成內容', '自動化發文']
      });
    }
    
    // ==================== 結構特徵 ====================
    
    // 10. 多標籤使用
    const top20MultiTags = top20Posts.filter(post => 
      post.commodity_tags && post.commodity_tags.length > 1
    ).length;
    const allMultiTags = allPosts.filter(post => 
      post.commodity_tags && post.commodity_tags.length > 1
    ).length;
    
    const multiTagFrequency = top20MultiTags / top20Posts.length;
    const allMultiTagFrequency = allMultiTags / allPosts.length;
    const multiTagImprovement = multiTagFrequency - allMultiTagFrequency;
    
    if (multiTagImprovement > 0) {
      features.push({
        feature_id: 'multi_tags',
        feature_name: '多標籤使用',
        feature_type: 'structure',
        description: '使用多個標籤的貼文互動率較高',
        frequency_in_top_posts: multiTagFrequency,
        frequency_in_all_posts: allMultiTagFrequency,
        improvement_potential: multiTagImprovement,
        setting_key: 'tag_count',
        is_modifiable: true,
        modification_method: '增加標籤數量',
        examples: ['股票標籤 + 市場標籤', '多維度標籤']
      });
    }
    
    // 按改善潛力排序
    features.sort((a, b) => b.improvement_potential - a.improvement_potential);
    
    console.log(`✅ 分析出 ${features.length} 個高成效特徵:`);
    features.forEach(f => {
      console.log(`  - ${f.feature_name}: ${f.improvement_potential.toFixed(3)} (前20%: ${f.frequency_in_top_posts.toFixed(3)}, 全部: ${f.frequency_in_all_posts.toFixed(3)})`);
    });
    
    // 生成詳細的計算結果表格數據
    const calculationResults = generateCalculationResults(top20Posts, allPosts, features);
    
    return { features, calculationResults };
  };
  
  // 生成詳細的計算結果表格數據
  const generateCalculationResults = (top20Posts: any[], allPosts: any[], features: any[]) => {
    const results = {
      summary: {
        totalPosts: allPosts.length,
        top20Count: top20Posts.length,
        top20Percentage: Math.round((top20Posts.length / allPosts.length) * 100),
        analysisDate: new Date().toLocaleString('zh-TW')
      },
      topPosts: top20Posts.slice(0, 10).map((post, index) => ({
        rank: index + 1,
        title: post.title,
        totalInteractions: (post.likes || 0) + (post.comments || 0) + (post.shares || 0) + (post.views || 0) + (post.donations || 0),
        likes: post.likes || 0,
        comments: post.comments || 0,
        shares: post.shares || 0,
        views: post.views || 0,
        donations: post.donations || 0
      })),
      featureCalculations: features.map(feature => {
        // 重新計算每個特徵的詳細數據
        let top20Count = 0;
        let allCount = 0;
        
        // 根據特徵類型重新計算
        if (feature.feature_id === 'has_question') {
          top20Count = top20Posts.filter(post => 
            (post.title && (post.title.includes('？') || post.title.includes('?'))) ||
            (post.content && (post.content.includes('？') || post.content.includes('?')))
          ).length;
          allCount = allPosts.filter(post => 
            (post.title && (post.title.includes('？') || post.title.includes('?'))) ||
            (post.content && (post.content.includes('？') || post.content.includes('?')))
          ).length;
        } else if (feature.feature_id === 'has_emoji') {
          const emojiPattern = /[😂😄😆👍👏🔥💰📈📊💡🎯]/;
          top20Count = top20Posts.filter(post => 
            (post.title && emojiPattern.test(post.title)) ||
            (post.content && emojiPattern.test(post.content))
          ).length;
          allCount = allPosts.filter(post => 
            (post.title && emojiPattern.test(post.title)) ||
            (post.content && emojiPattern.test(post.content))
          ).length;
        } else if (feature.feature_id === 'multi_tags') {
          top20Count = top20Posts.filter(post => 
            post.commodity_tags && post.commodity_tags.length > 1
          ).length;
          allCount = allPosts.filter(post => 
            post.commodity_tags && post.commodity_tags.length > 1
          ).length;
        } else if (feature.feature_id === 'has_technical_analysis') {
          const techKeywords = ['技術', '分析', '指標', '支撐', '阻力', 'MACD', 'RSI', 'KD', 'MA', '趨勢'];
          top20Count = top20Posts.filter(post => {
            const text = `${post.title || ''} ${post.content || ''}`;
            return techKeywords.some(keyword => text.includes(keyword));
          }).length;
          allCount = allPosts.filter(post => {
            const text = `${post.title || ''} ${post.content || ''}`;
            return techKeywords.some(keyword => text.includes(keyword));
          }).length;
        } else if (feature.feature_id === 'content_length_medium') {
          top20Count = top20Posts.filter(post => {
            const contentLength = (post.content || '').length;
            return contentLength >= 200 && contentLength <= 500;
          }).length;
          allCount = allPosts.filter(post => {
            const contentLength = (post.content || '').length;
            return contentLength >= 200 && contentLength <= 500;
          }).length;
        } else if (feature.feature_id === 'afternoon_posting') {
          top20Count = top20Posts.filter(post => {
            if (!post.create_time) return false;
            const hour = new Date(post.create_time).getHours();
            return hour >= 12 && hour < 18;
          }).length;
          allCount = allPosts.filter(post => {
            if (!post.create_time) return false;
            const hour = new Date(post.create_time).getHours();
            return hour >= 12 && hour < 18;
          }).length;
        }
        
        const top20Frequency = top20Count / top20Posts.length;
        const allFrequency = allCount / allPosts.length;
        const improvement = top20Frequency - allFrequency;
        
        return {
          key: feature.feature_id, // 添加唯一的 key
          featureName: feature.feature_name,
          featureType: feature.feature_type,
          top20Count,
          allCount,
          top20Frequency: (top20Frequency * 100).toFixed(1),
          allFrequency: (allFrequency * 100).toFixed(1),
          improvement: (improvement * 100).toFixed(1),
          isModifiable: feature.is_modifiable,
          modificationMethod: feature.modification_method,
          examples: feature.examples
        };
      })
    };
    
    return results;
  };
  
  // 基於選中特徵生成實驗
  const generateExperimentsFromSelectedFeatures = () => {
    if (selectedFeaturesForExperiment.length === 0) {
      message.warning('請先選擇要生成實驗的特徵');
      return;
    }
    
    if (!calculationResults) {
      message.error('沒有計算結果數據');
      return;
    }
    
    // 根據選中的特徵生成實驗
    const selectedFeatureData = calculationResults.featureCalculations.filter(
      feature => selectedFeaturesForExperiment.includes(feature.key)
    );
    
    const experiments = selectedFeatureData.map((feature, index) => {
      // 根據特徵類型生成對應的實驗設定
      let postingType = 'analysis';
      let triggerType = 'limit_up_after_hours';
      let maxStocks = 5;
      let contentLength = 'medium';
      let maxWords = 500;
      let contentStyle = 'technical';
      let executionTime = '14:00';
      
      // 根據特徵調整設定
      if (feature.key === 'has_question') {
        postingType = 'interaction';
        triggerType = 'limit_up_after_hours';
        maxStocks = 3;
        contentLength = 'short';
        maxWords = 200;
        contentStyle = 'casual';
      } else if (feature.key === 'has_emoji') {
        postingType = 'analysis';
        triggerType = 'volume_surge';
        maxStocks = 4;
        contentLength = 'medium';
        maxWords = 400;
        contentStyle = 'humorous';
      } else if (feature.key === 'multi_tags') {
        postingType = 'analysis';
        triggerType = 'limit_up_after_hours';
        maxStocks = 5;
        contentLength = 'medium';
        maxWords = 400;
        contentStyle = 'technical';
      } else if (feature.key === 'has_technical_analysis') {
        postingType = 'analysis';
        triggerType = 'volume_surge';
        maxStocks = 3;
        contentLength = 'long';
        maxWords = 600;
        contentStyle = 'technical';
      } else if (feature.key === 'afternoon_posting') {
        postingType = 'analysis';
        triggerType = 'limit_up_after_hours';
        maxStocks = 5;
        contentLength = 'medium';
        maxWords = 400;
        contentStyle = 'technical';
        executionTime = '15:00';
      } else if (feature.key === 'morning_posting') {
        postingType = 'analysis';
        triggerType = 'volume_surge';
        maxStocks = 5;
        contentLength = 'medium';
        maxWords = 400;
        contentStyle = 'technical';
        executionTime = '10:00';
      }
      
      return {
        id: `custom_${feature.key}_${Date.now()}`,
        experiment_id: `custom_${feature.key}_${Date.now()}`,
        name: `${feature.featureName} 優化實驗`,
        description: `基於 ${feature.featureName} 特徵的智能實驗設定`,
        color: ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#eb2f96'][index % 6],
        based_on_feature: feature.featureName,
        based_on_features: [feature.featureName], // 添加複數形式以兼容現有代碼
        settings: {
          posting_type: postingType,
          trigger_type: triggerType,
          max_stocks: maxStocks,
          content_length: contentLength,
          content_length_hint: contentLength, // 添加缺失的屬性
          max_words: maxWords,
          content_style: contentStyle,
          execution_time: executionTime,
          improvement_potential: parseFloat(feature.improvement),
          is_modifiable: feature.isModifiable || true,
          modification_method: feature.modificationMethod || '自動調整',
          interaction_style_hint: postingType === 'interaction' ? 'question_based' : 'standard', // 添加缺失的屬性
          min_volume: 1000000 // 添加缺失的屬性
        },
        expected_performance: Math.round(50 + parseFloat(feature.improvement) * 10), // 基於改善潛力計算預期成效
        confidence_level: Math.min(0.9, 0.5 + parseFloat(feature.improvement) * 2) // 基於改善潛力計算信心度
      };
    });
    
    setSmartExperiments(experiments);
    setShowSmartExperiments(true);
    
    message.success(`基於 ${selectedFeaturesForExperiment.length} 個選中特徵生成了 ${experiments.length} 個實驗！`);
  };
  
  // 基於真實貼文數據分析內容分類
  const analyzeContentCategoriesFromPosts = (posts: any[]) => {
    if (!posts || posts.length === 0) return [];
    
    // 計算每篇貼文的成效分數
    const scoredPosts = posts.map(post => {
      const totalInteractions = (post.likes || 0) + (post.comments || 0) + (post.shares || 0) + (post.views || 0) + (post.donations || 0);
      return { ...post, performanceScore: totalInteractions };
    });
    
    // 分析型內容
    const analysisPosts = scoredPosts.filter(post => {
      const text = `${post.title || ''} ${post.content || ''}`;
      return text.includes('分析') || text.includes('技術') || text.includes('指標') || text.includes('趨勢');
    });
    
    const analysisTopPosts = analysisPosts
      .sort((a, b) => b.performanceScore - a.performanceScore)
      .slice(0, 5)
      .map(post => ({
        title: post.title,
        performance_score: post.performanceScore
      }));
    
    const analysisAvgScore = analysisPosts.length > 0 
      ? analysisPosts.reduce((sum, post) => sum + post.performanceScore, 0) / analysisPosts.length 
      : 0;
    
    // 互動型內容
    const interactivePosts = scoredPosts.filter(post => {
      const text = `${post.title || ''} ${post.content || ''}`;
      return text.includes('？') || text.includes('?') || /[😂😄😆👍👏]/.test(text);
    });
    
    const interactiveTopPosts = interactivePosts
      .sort((a, b) => b.performanceScore - a.performanceScore)
      .slice(0, 5)
      .map(post => ({
        title: post.title,
        performance_score: post.performanceScore
      }));
    
    const interactiveAvgScore = interactivePosts.length > 0 
      ? interactivePosts.reduce((sum, post) => sum + post.performanceScore, 0) / interactivePosts.length 
      : 0;
    
    const categories = [];
    
    if (analysisPosts.length > 0) {
      categories.push({
        category_id: 'analysis_type',
        category_name: '分析型內容',
        description: '技術分析和市場解讀類內容',
        top_posts: analysisTopPosts,
        avg_performance_score: analysisAvgScore,
        key_characteristics: ['專業', '數據驅動', '技術指標'],
        success_rate: analysisPosts.length / posts.length
      });
    }
    
    if (interactivePosts.length > 0) {
      categories.push({
        category_id: 'interactive_type',
        category_name: '互動型內容',
        description: '包含問句和互動元素的內容',
        top_posts: interactiveTopPosts,
        avg_performance_score: interactiveAvgScore,
        key_characteristics: ['問句', '互動', '親切'],
        success_rate: interactivePosts.length / posts.length
      });
    }
    
    console.log(`📊 內容分類: 分析型(${analysisPosts.length}篇), 互動型(${interactivePosts.length}篇)`);
    
    return categories;
  };
  
  // 基於特徵生成發文設定
  const generateSettingsFromFeatures = (features: any[]) => {
    const settings = [];
    
    // 基於問句互動特徵生成設定
    const questionFeature = features.find(f => f.feature_id === 'has_question');
    const emojiFeature = features.find(f => f.feature_id === 'has_emoji');
    
    if (questionFeature && emojiFeature) {
      settings.push({
        setting_id: 'high_interaction_1',
        setting_name: '高互動設定',
        description: '基於問句互動特徵的發文設定',
        trigger_type: 'limit_up',
        content_length: 'medium',
        has_news_link: true,
        has_question_interaction: true,
        has_emoji: true,
        has_hashtag: true,
        humor_level: 'light',
        kol_style: 'casual',
        posting_time_preference: ['14:00-16:00', '19:00-21:00'],
        stock_tags_count: 2,
        content_structure: 'mixed',
        interaction_elements: ['question', 'emoji'],
        expected_performance: 85.0,
        confidence_level: 0.8,
        based_on_features: ['問句互動', '表情符號']
      });
    }
    
    // 基於中等長度內容特徵生成設定
    const mediumFeature = features.find(f => f.feature_id === 'content_length_medium');
    if (mediumFeature) {
      settings.push({
        setting_id: 'professional_1',
        setting_name: '專業分析設定',
        description: '基於分析型內容的發文設定',
        trigger_type: 'volume_surge',
        content_length: 'long',
        has_news_link: true,
        has_question_interaction: false,
        has_emoji: false,
        has_hashtag: true,
        humor_level: 'none',
        kol_style: 'professional',
        posting_time_preference: ['09:00-11:00', '15:00-17:00'],
        stock_tags_count: 3,
        content_structure: 'narrative',
        interaction_elements: ['hashtag'],
        expected_performance: 80.0,
        confidence_level: 0.75,
        based_on_features: ['中等長度內容', '專業分析']
      });
    }
    
    console.log(`⚙️ 生成 ${settings.length} 個發文設定`);
    
    return settings;
  };

  // 智能特徵排名分析
  const analyzeFeatureRankings = () => {
    const sortedPosts = posts.sort((a, b) => calculateTotalInteractions(b) - calculateTotalInteractions(a));
    const totalPosts = sortedPosts.length;
    const top20PercentCount = Math.max(1, Math.floor(totalPosts * 0.2)); // 改為前20%
    const top20PercentPosts = sortedPosts.slice(0, top20PercentCount);
    const allPosts = sortedPosts;

    const top20Analysis = analyzePostFeatures(top20PercentPosts);
    const allAnalysis = analyzePostFeatures(allPosts);

    // 計算特徵重要性排名
    const rankings: FeatureRanking[] = [
      {
        feature: '發文時段-下午',
        score: Math.abs(top20Analysis.features.postingTime.afternoon - allAnalysis.features.postingTime.afternoon),
        impact: Math.abs(top20Analysis.features.postingTime.afternoon - allAnalysis.features.postingTime.afternoon) > 15 ? 'high' : Math.abs(top20Analysis.features.postingTime.afternoon - allAnalysis.features.postingTime.afternoon) > 8 ? 'medium' : 'low',
        description: '下午時段發文的互動效果',
        top20PercentValue: top20Analysis.features.postingTime.afternoon,
        allPostsValue: allAnalysis.features.postingTime.afternoon,
        improvement: top20Analysis.features.postingTime.afternoon - allAnalysis.features.postingTime.afternoon
      },
      {
        feature: '發文時段-晚上',
        score: Math.abs(top20Analysis.features.postingTime.evening - allAnalysis.features.postingTime.evening),
        impact: Math.abs(top20Analysis.features.postingTime.evening - allAnalysis.features.postingTime.evening) > 15 ? 'high' : Math.abs(top20Analysis.features.postingTime.evening - allAnalysis.features.postingTime.evening) > 8 ? 'medium' : 'low',
        description: '晚上時段發文的互動效果',
        top20PercentValue: top20Analysis.features.postingTime.evening,
        allPostsValue: allAnalysis.features.postingTime.evening,
        improvement: top20Analysis.features.postingTime.evening - allAnalysis.features.postingTime.evening
      },
      {
        feature: '內容長度-中等',
        score: Math.abs(top20Analysis.features.mediumContent - allAnalysis.features.mediumContent),
        impact: Math.abs(top20Analysis.features.mediumContent - allAnalysis.features.mediumContent) > 15 ? 'high' : Math.abs(top20Analysis.features.mediumContent - allAnalysis.features.mediumContent) > 8 ? 'medium' : 'low',
        description: '200-500字中等長度內容的互動效果',
        top20PercentValue: top20Analysis.features.mediumContent,
        allPostsValue: allAnalysis.features.mediumContent,
        improvement: top20Analysis.features.mediumContent - allAnalysis.features.mediumContent
      },
      {
        feature: '股票標記',
        score: Math.abs(top20Analysis.features.hasStockTags - allAnalysis.features.hasStockTags),
        impact: Math.abs(top20Analysis.features.hasStockTags - allAnalysis.features.hasStockTags) > 15 ? 'high' : Math.abs(top20Analysis.features.hasStockTags - allAnalysis.features.hasStockTags) > 8 ? 'medium' : 'low',
        description: '包含股票標記的互動效果',
        top20PercentValue: top20Analysis.features.hasStockTags,
        allPostsValue: allAnalysis.features.hasStockTags,
        improvement: top20Analysis.features.hasStockTags - allAnalysis.features.hasStockTags
      },
      {
        feature: '幽默模式',
        score: Math.abs(top20Analysis.features.hasHumorMode - allAnalysis.features.hasHumorMode),
        impact: Math.abs(top20Analysis.features.hasHumorMode - allAnalysis.features.hasHumorMode) > 15 ? 'high' : Math.abs(top20Analysis.features.hasHumorMode - allAnalysis.features.hasHumorMode) > 8 ? 'medium' : 'low',
        description: '包含幽默元素的互動效果',
        top20PercentValue: top20Analysis.features.hasHumorMode,
        allPostsValue: allAnalysis.features.hasHumorMode,
        improvement: top20Analysis.features.hasHumorMode - allAnalysis.features.hasHumorMode
      },
      {
        feature: 'Emoji使用',
        score: Math.abs(top20Analysis.features.hasEmoji - allAnalysis.features.hasEmoji),
        impact: Math.abs(top20Analysis.features.hasEmoji - allAnalysis.features.hasEmoji) > 15 ? 'high' : Math.abs(top20Analysis.features.hasEmoji - allAnalysis.features.hasEmoji) > 8 ? 'medium' : 'low',
        description: '使用Emoji的互動效果',
        top20PercentValue: top20Analysis.features.hasEmoji,
        allPostsValue: allAnalysis.features.hasEmoji,
        improvement: top20Analysis.features.hasEmoji - allAnalysis.features.hasEmoji
      },
      {
        feature: '問號互動',
        score: Math.abs(top20Analysis.features.hasQuestion - allAnalysis.features.hasQuestion),
        impact: Math.abs(top20Analysis.features.hasQuestion - allAnalysis.features.hasQuestion) > 15 ? 'high' : Math.abs(top20Analysis.features.hasQuestion - allAnalysis.features.hasQuestion) > 8 ? 'medium' : 'low',
        description: '包含問號引導互動的效果',
        top20PercentValue: top20Analysis.features.hasQuestion,
        allPostsValue: allAnalysis.features.hasQuestion,
        improvement: top20Analysis.features.hasQuestion - allAnalysis.features.hasQuestion
      },
      {
        feature: '系統發文',
        score: Math.abs(top20Analysis.features.sourceDistribution.system - allAnalysis.features.sourceDistribution.system),
        impact: Math.abs(top20Analysis.features.sourceDistribution.system - allAnalysis.features.sourceDistribution.system) > 15 ? 'high' : Math.abs(top20Analysis.features.sourceDistribution.system - allAnalysis.features.sourceDistribution.system) > 8 ? 'medium' : 'low',
        description: '系統發文vs外部發文的互動效果',
        top20PercentValue: top20Analysis.features.sourceDistribution.system,
        allPostsValue: allAnalysis.features.sourceDistribution.system,
        improvement: top20Analysis.features.sourceDistribution.system - allAnalysis.features.sourceDistribution.system
      }
    ];

    // 按分數排序
    rankings.sort((a, b) => b.score - a.score);
    
    return {
      totalPosts,
      top20PercentCount,
      top20PercentPosts,
      rankings,
      top20Analysis,
      allAnalysis
    };
  };


  // 生成自我學習洞察
  const generateSelfLearningInsights = () => {
    const analysis = analyzeFeatureRankings();
    const insights: SelfLearningInsight[] = [
      {
        id: 'insight_1',
        type: 'pattern',
        title: '發現高互動時段模式',
        description: `前20%高互動貼文中，${analysis.rankings[0].feature}的表現比全部貼文高出${Math.abs(analysis.rankings[0].improvement)}%`,
        confidence: 85,
        impact: 'high',
        action: '建議在該時段增加發文頻率',
        timestamp: new Date().toISOString()
      },
      {
        id: 'insight_2',
        type: 'recommendation',
        title: '內容長度優化建議',
        description: '中等長度內容(200-500字)在前20%高互動貼文中表現最佳',
        confidence: 78,
        impact: 'medium',
        action: '調整內容生成策略，優先生成中等長度內容',
        timestamp: new Date().toISOString()
      },
      {
        id: 'insight_3',
        type: 'success',
        title: '幽默元素效果顯著',
        description: '包含幽默元素的貼文互動率平均提升15%',
        confidence: 92,
        impact: 'high',
        action: '增加幽默元素在內容生成中的權重',
        timestamp: new Date().toISOString()
      },
      {
        id: 'insight_4',
        type: 'warning',
        title: 'KOL表現差異明顯',
        description: '不同KOL的互動表現存在顯著差異，需要個性化策略',
        confidence: 88,
        impact: 'high',
        action: '為每個KOL制定專屬的發文策略',
        timestamp: new Date().toISOString()
      }
    ];

    setInsights(insights);
    setShowInsights(true);
  };

  // 獲取增強版自我學習分析數據
  const fetchEnhancedSelfLearningAnalysis = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedKOL) params.append('kol_serial', selectedKOL.toString());
      if (dateRange && dateRange[0] && dateRange[1]) {
        params.append('start_date', dateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', dateRange[1].format('YYYY-MM-DD'));
      }
      params.append('include_external', includeExternal.toString());

      // 使用與 InteractionAnalysisPage 相同的 API 端點
      const response = await fetch(`${API_BASE_URL}/posts?limit=10000&status=published`);
      const result = await response.json();

      if (result.posts) {
        // 從 posts API 獲取貼文數據
        const posts = result.posts || [];
        
        console.log(`📊 獲取到 ${posts.length} 篇貼文數據`);
        
        // 設置貼文數據
        setPosts(posts);
        
        // 基於真實數據進行特徵分析
        const analysisResult = analyzeHighPerformanceFeaturesFromPosts(posts);
        setHighPerformanceFeatures(analysisResult.features);
        
        // 設置計算結果數據
        setCalculationResults(analysisResult.calculationResults);
        
        // 基於真實數據進行內容分類
        const categories = analyzeContentCategoriesFromPosts(posts);
        setContentCategories(categories);
        
        // 生成發文設定
        const settings = generateSettingsFromFeatures(analysisResult.features);
        setGeneratedSettings(settings);
        
        // 自動顯示分析結果
        setShowHighPerformanceFeatures(true);
        setShowContentCategories(true);
        setShowGeneratedSettings(true);
        
        message.success(`自我學習分析完成！分析了 ${posts.length} 篇貼文`);
      } else {
        message.error('獲取互動分析數據失敗');
      }
    } catch (error) {
      console.error('獲取增強版自我學習分析數據失敗:', error);
      message.error('獲取增強版自我學習分析數據失敗');
    } finally {
      setLoading(false);
    }
  };

  // 重新載入貼文數據 - 從現有數據庫讀取
  const reloadPostData = async () => {
    setFetchingData(true);
    try {
      message.info('正在重新載入貼文數據...');
      // 重新獲取分析數據
      await fetchEnhancedSelfLearningAnalysis();
      message.success('貼文數據載入成功！');
    } catch (error) {
      console.error('載入貼文數據失敗:', error);
      message.error('載入貼文數據失敗');
    } finally {
      setFetchingData(false);
    }
  };

  // 分析高成效特徵 - 基於現有數據進行統計分析
  const analyzeHighPerformanceFeatures = async () => {
    setFetchingData(true);
    try {
      message.info('正在分析高成效特徵...');
      // 重新獲取分析數據
      await fetchEnhancedSelfLearningAnalysis();
      message.success('高成效特徵分析完成！');
    } catch (error) {
      console.error('分析高成效特徵失敗:', error);
      message.error('分析高成效特徵失敗');
    } finally {
      setFetchingData(false);
    }
  };

  // 生成智能實驗 - 基於高成效特徵生成實驗設定
  const generateSmartExperimentsFromFeatures = async () => {
    setFetchingData(true);
    try {
      message.info('正在生成智能實驗...');
      // 重新獲取分析數據
      await fetchEnhancedSelfLearningAnalysis();
      // 生成實驗設定
      generateSmartExperiments();
      message.success('智能實驗生成完成！');
    } catch (error) {
      console.error('生成智能實驗失敗:', error);
      message.error('生成智能實驗失敗');
    } finally {
      setFetchingData(false);
    }
  };

  // 處理加入排程
  const handleAddToSchedule = (feature: HighPerformanceFeature) => {
    // 設置選中的特徵並打開排程 modal
    setSelectedFeatureForSchedule(feature);
    setScheduleModalVisible(true);
  };

  // 生成智能實驗設定
  const generateSmartExperiments = () => {
    if (highPerformanceFeatures.length === 0) {
      message.warning('請先分析高成效特徵');
      return;
    }

    // 基於實際的高成效特徵生成實驗設定
    const topFeatures = highPerformanceFeatures
      .sort((a, b) => b.improvement_potential - a.improvement_potential)
      .slice(0, 6); // 取前6個最高成效特徵

    console.log('基於以下高成效特徵生成實驗:', topFeatures.map(f => f.feature_name));

    const experiments = [];

    // 實驗1: 基於最高成效特徵
    if (topFeatures.length > 0) {
      const topFeature = topFeatures[0];
      experiments.push({
        id: 'experiment_1',
        name: `${topFeature.feature_name}實驗`,
        description: `基於「${topFeature.feature_name}」特徵的實驗設定，改善潛力 ${(topFeature.improvement_potential * 100).toFixed(1)}%`,
        color: '#52c41a',
        settings: {
          // 發文生成設定層級 - 完整填寫所有相關設定
          posting_type: topFeature.feature_id === 'has_question' ? 'interaction' : 'analysis',
          trigger_type: 'limit_up_after_hours',
          include_news_links: true,
          max_stocks: 5,
          min_volume: 1000,
          stock_sorting: 'five_day_change_desc',
          posting_time_preference: ['14:00-16:00', '19:00-21:00'],
          
          // 內容生成設定
          content_length: topFeature.feature_id === 'content_length_short' ? 'short' : 
                         topFeature.feature_id === 'content_length_long' ? 'long' : 'medium',
          max_words: topFeature.feature_id === 'content_length_short' ? 200 : 
                    topFeature.feature_id === 'content_length_long' ? 800 : 500,
          content_style: topFeature.feature_id === 'has_question' ? 'casual' : 
                       topFeature.feature_id === 'has_emoji' ? 'humorous' : 'technical',
          
          // 新聞連結設定
          enable_news_links: true,
          news_max_links: 5,
          
          // KOL 分配設定
          kol_assignment: 'random',
          
          // 其他設定
          generation_mode: 'high_quality',
          include_risk_warning: true,
          include_charts: false,
          
          // 實驗標記，用於追蹤效果
          experiment_id: 'experiment_1',
          based_on_feature: topFeature.feature_id,
          feature_name: topFeature.feature_name,
          improvement_potential: topFeature.improvement_potential
        },
        expected_performance: 60 + (topFeature.improvement_potential * 40), // 基於改善潛力計算
        confidence_level: 0.8,
        based_on_features: [topFeature.feature_name],
        improvement_potential: topFeature.improvement_potential,
        feature_details: topFeature
      });
    }

    // 實驗2: 基於第二高成效特徵
    if (topFeatures.length > 1) {
      const secondFeature = topFeatures[1];
      experiments.push({
        id: 'experiment_2',
        name: `${secondFeature.feature_name}實驗`,
        description: `基於「${secondFeature.feature_name}」特徵的實驗設定，改善潛力 ${(secondFeature.improvement_potential * 100).toFixed(1)}%`,
        color: '#1890ff',
        settings: {
          // 發文生成設定層級 - 完整填寫所有相關設定
          posting_type: secondFeature.feature_id === 'has_question' ? 'interaction' : 'analysis',
          trigger_type: 'volume_surge',
          include_news_links: true,
          max_stocks: 3,
          min_volume: 2000,
          stock_sorting: 'volume_desc',
          posting_time_preference: ['09:00-11:00', '15:00-17:00'],
          
          // 內容生成設定
          content_length: secondFeature.feature_id === 'content_length_short' ? 'short' : 
                         secondFeature.feature_id === 'content_length_long' ? 'long' : 'medium',
          max_words: secondFeature.feature_id === 'content_length_short' ? 200 : 
                    secondFeature.feature_id === 'content_length_long' ? 800 : 500,
          content_style: secondFeature.feature_id === 'has_question' ? 'casual' : 
                       secondFeature.feature_id === 'has_emoji' ? 'humorous' : 'technical',
          
          // 新聞連結設定
          enable_news_links: true,
          news_max_links: 5,
          
          // KOL 分配設定
          kol_assignment: 'random',
          
          // 其他設定
          generation_mode: 'high_quality',
          include_risk_warning: true,
          include_charts: false,
          
          // 實驗標記
          experiment_id: 'experiment_2',
          based_on_feature: secondFeature.feature_id,
          feature_name: secondFeature.feature_name,
          improvement_potential: secondFeature.improvement_potential
        },
        expected_performance: 60 + (secondFeature.improvement_potential * 40),
        confidence_level: 0.75,
        based_on_features: [secondFeature.feature_name],
        improvement_potential: secondFeature.improvement_potential,
        feature_details: secondFeature
      });
    }

    // 實驗3: 結合多個高成效特徵的綜合實驗
    if (topFeatures.length > 2) {
      const combinedFeatures = topFeatures.slice(0, 3);
      experiments.push({
        id: 'experiment_3',
        name: '綜合高成效實驗',
        description: `結合「${combinedFeatures.map(f => f.feature_name).join('」、「')}」等多個高成效特徵的綜合實驗`,
        color: '#722ed1',
        settings: {
          // 發文生成設定層級 - 完整填寫所有相關設定
          posting_type: combinedFeatures.some(f => f.feature_id === 'has_question') ? 'interaction' : 'analysis',
          trigger_type: 'limit_up_after_hours',
          include_news_links: true,
          max_stocks: 4,
          min_volume: 1500,
          stock_sorting: 'five_day_change_desc',
          posting_time_preference: ['13:00-15:00', '18:00-20:00'],
          
          // 內容生成設定 - 綜合多個特徵
          content_length: combinedFeatures.some(f => f.feature_id === 'content_length_short') ? 'short' : 
                         combinedFeatures.some(f => f.feature_id === 'content_length_long') ? 'long' : 'medium',
          max_words: combinedFeatures.some(f => f.feature_id === 'content_length_short') ? 200 : 
                    combinedFeatures.some(f => f.feature_id === 'content_length_long') ? 800 : 500,
          content_style: combinedFeatures.some(f => f.feature_id === 'has_question') ? 'casual' : 
                       combinedFeatures.some(f => f.feature_id === 'has_emoji') ? 'humorous' : 'technical',
          
          // 新聞連結設定
          enable_news_links: true,
          news_max_links: 5,
          
          // KOL 分配設定
          kol_assignment: 'random',
          
          // 其他設定
          generation_mode: 'high_quality',
          include_risk_warning: true,
          include_charts: false,
          
          // 實驗標記
          experiment_id: 'experiment_3',
          based_on_feature: 'combined',
          combined_features: combinedFeatures.map(f => f.feature_id),
          feature_name: '綜合高成效實驗',
          improvement_potential: combinedFeatures.reduce((sum, f) => sum + f.improvement_potential, 0) / combinedFeatures.length
        },
        expected_performance: 60 + (combinedFeatures.reduce((sum, f) => sum + f.improvement_potential, 0) / combinedFeatures.length * 40),
        confidence_level: 0.7,
        based_on_features: combinedFeatures.map(f => f.feature_name),
        improvement_potential: combinedFeatures.reduce((sum, f) => sum + f.improvement_potential, 0) / combinedFeatures.length,
        feature_details: combinedFeatures
      });
    }

    setSmartExperiments(experiments);
    setShowSmartExperiments(true);
    message.success(`已基於 ${topFeatures.length} 個高成效特徵生成 ${experiments.length} 種智能實驗設定`);
  };

  // 處理智能實驗加入排程
  const handleAddExperimentToSchedule = (experiment: any) => {
    // 設置選中的實驗並打開排程 modal
    setSelectedFeatureForSchedule({
      feature_id: experiment.id,
      feature_name: experiment.name,
      feature_type: 'experiment',
      description: experiment.description,
      frequency_in_top_posts: experiment.expected_performance / 100,
      frequency_in_all_posts: 0.3,
      improvement_potential: experiment.settings?.improvement_potential || 0.5,
      setting_key: 'experiment_config',
      is_modifiable: true,
      modification_method: '實驗設定調整',
      examples: experiment.based_on_features || [experiment.based_on_feature] || []
    });
    setScheduleModalVisible(true);
  };

  // 處理排程確認
  const handleConfirmSchedule = async (scheduleConfig: any) => {
    try {
      setLoading(true);
      
      // 根據選中的特徵自動填上預設排程設定
      if (selectedFeatureForSchedule) {
        const feature = selectedFeatureForSchedule;
        
        // 根據特徵類型決定發文類型和相關設定
        let postingType = 'analysis'; // 預設為發表分析
        let triggerType = 'limit_up_after_hours';
        let maxStocks = 5;
        let stockSorting = 'five_day_change_desc';
        
        // 根據特徵自動調整設定
        if (feature.feature_id === 'has_question') {
          postingType = 'interaction'; // 互動發問
          triggerType = 'limit_up_after_hours';
          maxStocks = 3; // 互動發問用較少股票
        } else if (feature.feature_id === 'has_emoji') {
          postingType = 'analysis';
          triggerType = 'volume_surge';
          maxStocks = 4;
        } else if (feature.feature_id === 'content_length_medium') {
          postingType = 'analysis';
          triggerType = 'limit_up_after_hours';
          maxStocks = 5;
        } else if (feature.feature_id === 'multi_tags') {
          postingType = 'analysis';
          triggerType = 'limit_up_after_hours';
          maxStocks = 5;
        } else if (feature.feature_id === 'has_technical_analysis') {
          postingType = 'analysis';
          triggerType = 'volume_surge';
          maxStocks = 3; // 技術分析用較少股票，更專注
        } else if (feature.feature_id === 'system_source') {
          postingType = 'analysis';
          triggerType = 'limit_up_after_hours';
          maxStocks = 5;
        } else if (feature.feature_id === 'afternoon_posting') {
          postingType = 'analysis';
          triggerType = 'limit_up_after_hours';
          maxStocks = 5;
        } else if (feature.feature_id === 'morning_posting') {
          postingType = 'analysis';
          triggerType = 'volume_surge';
          maxStocks = 5;
        } else if (feature.feature_id === 'content_length_short') {
          postingType = 'interaction'; // 短內容適合互動
          triggerType = 'limit_up_after_hours';
          maxStocks = 3;
        } else if (feature.feature_id === 'has_hashtag') {
          postingType = 'analysis';
          triggerType = 'volume_surge';
          maxStocks = 4;
        }
        
        // 🔥 根據特徵設定詳細的生成配置（只包含 BatchScheduleModal 中實際存在的欄位）
        const featureBasedConfig = {
          // 基礎設定
          posting_type: postingType,
          trigger_type: triggerType,
          max_stocks: maxStocks,
          stock_sorting: stockSorting,
          enable_news_links: true,
          news_max_links: 5,
          
          // 根據特徵設定具體參數
          ...(feature.feature_id === 'has_question' && {
            content_length: 'short',
            max_words: 200,
            content_style: 'casual' // 互動發問用輕鬆風格
          }),
          
          ...(feature.feature_id === 'has_emoji' && {
            content_length: 'medium',
            max_words: 400,
            content_style: 'humorous' // 表情符號用幽默風格
          }),
          
          ...(feature.feature_id === 'content_length_medium' && {
            content_length: 'medium',
            max_words: 500,
            content_style: 'technical' // 中等長度用技術風格
          }),
          
          ...(feature.feature_id === 'content_length_short' && {
            content_length: 'short',
            max_words: 150,
            content_style: 'casual' // 短內容用輕鬆風格
          }),
          
          ...(feature.feature_id === 'multi_tags' && {
            content_length: 'medium',
            max_words: 400,
            content_style: 'technical' // 多標籤用技術風格
          }),
          
          ...(feature.feature_id === 'has_technical_analysis' && {
            content_length: 'long',
            max_words: 600,
            content_style: 'technical' // 技術分析用專業風格
          }),
          
          ...(feature.feature_id === 'has_hashtag' && {
            content_length: 'medium',
            max_words: 400,
            content_style: 'casual' // 標籤用輕鬆風格
          }),
          
          ...(feature.feature_id === 'afternoon_posting' && {
            content_length: 'medium',
            max_words: 400,
            content_style: 'technical' // 下午發文用技術風格
          }),
          
          ...(feature.feature_id === 'morning_posting' && {
            content_length: 'medium',
            max_words: 400,
            content_style: 'technical' // 上午發文用技術風格
          }),
          
          ...(feature.feature_id === 'system_source' && {
            content_length: 'medium',
            max_words: 400,
            content_style: 'technical' // 系統貼文用技術風格
          })
        };
        
        // 根據時間特徵設定發文時間
        let executionTime = '14:00'; // 預設下午2點
        if (feature.feature_id === 'afternoon_posting') {
          executionTime = '15:00'; // 下午3點
        } else if (feature.feature_id === 'morning_posting') {
          executionTime = '10:00'; // 上午10點
        }
        
        // 自動填上預設排程設定
        scheduleConfig = {
          ...scheduleConfig,
          // 排程基本設定
          session_id: Date.now(), // 生成一個唯一的 session_id
          schedule_name: `基於${feature.feature_name}的排程`,
          schedule_description: `基於「${feature.feature_name}」特徵創建的排程，改善潛力：${(feature.improvement_potential * 100).toFixed(1)}%`,
          schedule_type: 'weekday_daily',
          daily_execution_time: executionTime,
          enabled: true,
          max_posts_per_hour: 2,
          timezone: 'Asia/Taipei',
          
          // 來源追蹤
          source_type: feature.feature_type === 'experiment' ? 'self_learning' : 'self_learning',
          source_experiment_id: feature.feature_type === 'experiment' ? feature.feature_id : null,
          source_feature_name: feature.feature_name,
          created_by: 'user',
          
          // 生成配置 - 只包含 BatchScheduleModal 中實際存在的欄位
          generation_config: {
            // 基礎發文設定
            posting_type: featureBasedConfig.posting_type,
            trigger_type: featureBasedConfig.trigger_type,
            max_stocks: featureBasedConfig.max_stocks,
            stock_sorting: featureBasedConfig.stock_sorting,
            
            // 內容生成設定
            content_length: featureBasedConfig.content_length || 'medium',
            max_words: featureBasedConfig.max_words || 500,
            content_style: featureBasedConfig.content_style || 'technical',
            
            // 新聞連結設定
            enable_news_links: featureBasedConfig.enable_news_links,
            news_max_links: featureBasedConfig.news_max_links,
            
            // KOL 分配設定
            kol_assignment: 'random',
            
            // 其他設定
            generation_mode: 'high_quality',
            include_risk_warning: true,
            include_charts: false,
            
            // 特徵相關設定（用於追蹤）
            feature_based: true,
            feature_name: feature.feature_name,
            improvement_potential: feature.improvement_potential
          }
        };
        
        console.log('🎯 自動填上的排程設定:', scheduleConfig);
      }
      
      // 創建排程 - 直接調用 posting-service 的 API
      const response = await fetch(`${API_BASE_URL}/api/schedule/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: scheduleConfig.session_id,
          post_ids: [], // 空陣列，因為這是新排程
          schedule_type: scheduleConfig.schedule_type,
          interval_seconds: 30,
          batch_duration_hours: null,
          // 來源追蹤參數
          source_type: scheduleConfig.source_type,
          source_batch_id: scheduleConfig.source_batch_id,
          source_experiment_id: scheduleConfig.source_experiment_id,
          source_feature_name: scheduleConfig.source_feature_name,
          created_by: scheduleConfig.created_by
        })
      });

      const result = await response.json();

      if (result.success) {
        message.success('排程創建成功！任務 ID: ' + result.task_id);
        setScheduleModalVisible(false);
        setSelectedFeatureForSchedule(null);
      } else {
        message.error('創建排程失敗: ' + result.message);
      }
    } catch (error) {
      console.error('創建排程失敗:', error);
      message.error('創建排程失敗');
    } finally {
      setLoading(false);
    }
  };

  // 啟動實驗
  const startExperiment = (experimentId: string) => {
    setExperiments(prev => prev.map(exp => 
      exp.id === experimentId 
        ? { ...exp, status: 'running' as const, progress: 10 }
        : exp
    ));
    message.success('實驗已啟動');
  };

  // 暫停實驗
  const pauseExperiment = (experimentId: string) => {
    setExperiments(prev => prev.map(exp => 
      exp.id === experimentId 
        ? { ...exp, status: 'paused' as const }
        : exp
    ));
    message.info('實驗已暫停');
  };

  // 完成實驗
  const completeExperiment = (experimentId: string) => {
    setExperiments(prev => prev.map(exp => 
      exp.id === experimentId 
        ? { ...exp, status: 'completed' as const, progress: 100 }
        : exp
    ));
    message.success('實驗已完成');
  };

  // 特徵排名表格列定義
  const featureRankingColumns: ColumnsType<FeatureRanking> = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 60,
      render: (_, __, index) => (
        <Badge 
          count={index + 1} 
          style={{ backgroundColor: index < 3 ? '#52c41a' : '#1890ff' }}
        />
      ),
    },
    {
      title: '特徵',
      dataIndex: 'feature',
      key: 'feature',
      width: 150,
      render: (text: string) => (
        <Text strong style={{ fontSize: '13px' }}>{text}</Text>
      ),
    },
    {
      title: '重要性',
      dataIndex: 'impact',
      key: 'impact',
      width: 100,
      render: (impact: string) => {
        const colors = { high: '#ff4d4f', medium: '#fa8c16', low: '#52c41a' };
        return (
          <Tag color={colors[impact as keyof typeof colors]}>
            {impact === 'high' ? '高' : impact === 'medium' ? '中' : '低'}
          </Tag>
        );
      },
    },
    {
      title: '前20%表現',
      dataIndex: 'top20PercentValue',
      key: 'top20PercentValue',
      width: 100,
      render: (value: number) => (
        <Text strong style={{ color: '#1890ff' }}>{value}%</Text>
      ),
    },
    {
      title: '全部表現',
      dataIndex: 'allPostsValue',
      key: 'allPostsValue',
      width: 100,
      render: (value: number) => (
        <Text style={{ color: '#52c41a' }}>{value}%</Text>
      ),
    },
    {
      title: '改善幅度',
      dataIndex: 'improvement',
      key: 'improvement',
      width: 100,
      render: (improvement: number) => (
        <Text 
          strong 
          style={{ color: improvement > 0 ? '#52c41a' : '#ff4d4f' }}
        >
          {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}%
        </Text>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => (
        <Text type="secondary" style={{ fontSize: '12px' }}>{text}</Text>
      ),
    },
  ];

  // 實驗表格列定義
  const experimentColumns: ColumnsType<ExperimentConfig> = [
    {
      title: '實驗名稱',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text: string, record: ExperimentConfig) => (
        <Space>
          <ExperimentOutlined style={{ color: record.color }} />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: '狀態',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusConfig = {
          pending: { color: 'default', icon: <ClockCircleOutlined />, text: '待啟動' },
          running: { color: 'processing', icon: <PlayCircleOutlined />, text: '進行中' },
          completed: { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
          paused: { color: 'warning', icon: <PauseCircleOutlined />, text: '已暫停' }
        };
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      },
    },
    {
      title: '進度',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress: number) => (
        <Progress percent={progress} size="small" />
      ),
    },
    {
      title: '預期效果',
      dataIndex: 'expectedEngagement',
      key: 'expectedEngagement',
      width: 150,
      render: (text: string) => (
        <Text type="secondary" style={{ fontSize: '12px' }}>{text}</Text>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record: ExperimentConfig) => (
        <Space>
          {record.status === 'pending' && (
            <Button 
              type="primary" 
              size="small" 
              icon={<PlayCircleOutlined />}
              onClick={() => startExperiment(record.id)}
            >
              啟動
            </Button>
          )}
          {record.status === 'running' && (
            <>
              <Button 
                type="default" 
                size="small" 
                icon={<PauseCircleOutlined />}
                onClick={() => pauseExperiment(record.id)}
              >
                暫停
              </Button>
              <Button 
                type="primary" 
                size="small" 
                icon={<CheckCircleOutlined />}
                onClick={() => completeExperiment(record.id)}
              >
                完成
              </Button>
            </>
          )}
          {record.status === 'paused' && (
            <Button 
              type="primary" 
              size="small" 
              icon={<PlayCircleOutlined />}
              onClick={() => startExperiment(record.id)}
            >
              繼續
            </Button>
          )}
        </Space>
      ),
    },
  ];

  useEffect(() => {
    fetchEnhancedSelfLearningAnalysis();
  }, [selectedKOL, dateRange, includeExternal]);

  return (
    <div style={{ padding: '24px' }}>
      {/* 頁面標題 */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <ThunderboltOutlined style={{ marginRight: 8 }} />
          AI自我學習系統
        </Title>
        <Text type="secondary">基於互動數據的智能學習與優化系統</Text>
      </div>

      {/* 系統狀態 */}
      <Card size="small" style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Space>
              <Switch 
                checked={autoLearningEnabled} 
                onChange={setAutoLearningEnabled}
                checkedChildren="開啟" 
                unCheckedChildren="關閉"
              />
              <Text strong>自動學習模式</Text>
            </Space>
          </Col>
          <Col span={6}>
            <Statistic
              title="總貼文數"
              value={posts.length}
              prefix={<BarChartOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="進行中實驗"
              value={experiments.filter(exp => exp.status === 'running').length}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="學習洞察"
              value={insights.length}
              prefix={<BulbOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
        </Row>
      </Card>

      {/* 篩選條件 */}
      <Card size="small" style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={4}>
            <Select
              placeholder="選擇KOL"
              value={selectedKOL}
              onChange={setSelectedKOL}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value={1}>龜狗一日散戶</Option>
              <Option value={2}>板橋大who</Option>
            </Select>
          </Col>
          <Col span={6}>
            <RangePicker
              placeholder={['開始日期', '結束日期']}
              value={dateRange}
              onChange={setDateRange}
              style={{ width: '100%' }}
            />
          </Col>
          <Col span={4}>
            <Select
              value={includeExternal}
              onChange={setIncludeExternal}
              style={{ width: '100%' }}
            >
              <Option value={true}>包含外部數據</Option>
              <Option value={false}>僅系統數據</Option>
            </Select>
          </Col>
          <Col span={10}>
            <Space wrap>
              <Button 
                type="primary" 
                icon={<ReloadOutlined />}
                onClick={fetchEnhancedSelfLearningAnalysis}
                loading={loading}
              >
                分析數據
              </Button>
              <Button 
                type="default"
                icon={<RocketOutlined />}
                onClick={generateSelfLearningInsights}
                loading={fetchingData}
              >
                生成洞察
              </Button>
              <Button 
                type="default"
                icon={<ExperimentOutlined />}
                onClick={generateSmartExperimentsFromFeatures}
                loading={fetchingData}
              >
                智能實驗
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 高成效特徵分析 */}
      {highPerformanceFeatures.length > 0 && (
        <Card 
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>🏆 智能特徵排名分析</span>
              <Button 
                type="primary" 
                icon={<RocketOutlined />}
                onClick={generateSmartExperiments}
                style={{ marginLeft: 16 }}
              >
                生成智能實驗
              </Button>
            </div>
          } 
          style={{ marginBottom: 24 }}
        >
          <Alert
            message="基於前20%高成效貼文的特徵分析"
            description="系統自動分析高成效貼文的特徵，識別可修改的設定項目，為發文策略優化提供數據支持"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <Table
            columns={[
              {
                title: '特徵名稱',
                dataIndex: 'feature_name',
                key: 'feature_name',
                width: 150,
                render: (text: string) => (
                  <Text strong style={{ fontSize: '13px' }}>{text}</Text>
                ),
              },
              {
                title: '特徵類型',
                dataIndex: 'feature_type',
                key: 'feature_type',
                width: 100,
                render: (type: string) => {
                  const colors = { content: 'blue', timing: 'green', structure: 'orange', interaction: 'purple', kol: 'red' };
                  return (
                    <Tag color={colors[type as keyof typeof colors]}>
                      {type === 'content' ? '內容' : type === 'timing' ? '時機' : type === 'structure' ? '結構' : type === 'interaction' ? '互動' : 'KOL'}
                    </Tag>
                  );
                },
              },
              {
                title: '改善潛力',
                dataIndex: 'improvement_potential',
                key: 'improvement_potential',
                width: 120,
                sorter: (a: HighPerformanceFeature, b: HighPerformanceFeature) => a.improvement_potential - b.improvement_potential,
                render: (potential: number) => (
                  <Progress 
                    type="circle" 
                    size={40} 
                    percent={potential * 100} 
                    format={() => `${(potential * 100).toFixed(1)}%`}
                    strokeColor={potential > 0.3 ? '#52c41a' : potential > 0.1 ? '#fa8c16' : '#ff4d4f'}
                  />
                ),
              },
              {
                title: '可修改',
                dataIndex: 'is_modifiable',
                key: 'is_modifiable',
                width: 100,
                render: (modifiable: boolean) => (
                  <Tag color={modifiable ? 'green' : 'red'}>
                    {modifiable ? '可修改' : '不可修改'}
                  </Tag>
                ),
              },
              {
                title: '修改方法',
                dataIndex: 'modification_method',
                key: 'modification_method',
                width: 200,
                render: (method: string) => (
                  <Text type="secondary" style={{ fontSize: '12px' }}>{method}</Text>
                ),
              },
              {
                title: '設定鍵名',
                dataIndex: 'setting_key',
                key: 'setting_key',
                width: 120,
                render: (key: string) => (
                  <Text code style={{ fontSize: '11px' }}>{key}</Text>
                ),
              },
              {
                title: '範例',
                dataIndex: 'examples',
                key: 'examples',
                render: (examples: string[]) => (
                  <Space wrap>
                    {examples.slice(0, 2).map((example, index) => (
                      <Tag key={index} size="small" color="blue">
                        {example}
                      </Tag>
                    ))}
                    {examples.length > 2 && (
                      <Tag size="small" color="default">
                        +{examples.length - 2}
                      </Tag>
                    )}
                  </Space>
                ),
              },
              {
                title: '操作',
                key: 'action',
                width: 120,
                render: (_, record: HighPerformanceFeature) => (
                  <Space>
                    {record.is_modifiable && (
                      <Button
                        type="primary"
                        size="small"
                        icon={<PlayCircleOutlined />}
                        onClick={() => handleAddToSchedule(record)}
                        style={{ fontSize: '11px' }}
                      >
                        加入排程
                      </Button>
                    )}
                  </Space>
                ),
              },
            ]}
            dataSource={highPerformanceFeatures}
            rowKey="feature_id"
            pagination={{ pageSize: 10 }}
            size="small"
          />
        </Card>
      )}

      {/* 智能實驗管理 */}
      {showSmartExperiments && smartExperiments.length > 0 && (
        <Card 
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>🧪 智能實驗管理</span>
              <Space>
                <Button 
                  type="default" 
                  icon={<ReloadOutlined />}
                  onClick={generateSmartExperiments}
                >
                  重新生成
                </Button>
                <Button 
                  type="default" 
                  onClick={() => setShowSmartExperiments(false)}
                >
                  關閉
                </Button>
              </Space>
            </div>
          } 
          style={{ marginBottom: 24 }}
        >
          <Alert
            message="基於成效特徵自動生成的實驗設定"
            description="系統根據高成效特徵分析，自動生成三種不同的實驗設定參數，可直接加入排程進行測試"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <Row gutter={[16, 16]}>
            {smartExperiments.map((experiment) => (
              <Col span={8} key={experiment.id}>
                <Card 
                  size="small" 
                  style={{ 
                    border: `2px solid ${experiment.color}`,
                    borderRadius: '8px'
                  }}
                >
                  <div style={{ marginBottom: 12 }}>
                    <Title level={4} style={{ color: experiment.color, margin: 0 }}>
                      {experiment.name}
                    </Title>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {experiment.description}
                    </Text>
                  </div>
                  
                  <div style={{ marginBottom: 12 }}>
                    <div style={{ marginBottom: 8 }}>
                      <Text strong style={{ fontSize: '12px', color: experiment.color }}>
                        基於特徵: {experiment.based_on_feature || experiment.based_on_features?.join('、') || '未知特徵'}
                      </Text>
                    </div>
                    <div style={{ marginBottom: 4 }}>
                      <Text style={{ fontSize: '12px' }}>
                        <ClockCircleOutlined style={{ marginRight: 4 }} />
                        發文類型: {experiment.settings?.posting_type === 'interaction' ? '互動發問' : '發表分析'}
                      </Text>
                    </div>
                    <div style={{ marginBottom: 4 }}>
                      <Text style={{ fontSize: '12px' }}>
                        <FilterOutlined style={{ marginRight: 4 }} />
                        觸發器: {experiment.settings?.trigger_type === 'limit_up_after_hours' ? '盤後漲停' : 
                                 experiment.settings?.trigger_type === 'volume_surge' ? '成交量激增' : '盤中觸發'}
                      </Text>
                    </div>
                    <div style={{ marginBottom: 4 }}>
                      <Text style={{ fontSize: '12px' }}>
                        <FileOutlined style={{ marginRight: 4 }} />
                        內容長度提示: {experiment.settings?.content_length_hint === 'short' ? '簡短' : 
                                     experiment.settings?.content_length_hint === 'long' ? '長篇' : '中等'}
                      </Text>
                    </div>
                    <div style={{ marginBottom: 4 }}>
                      <Text style={{ fontSize: '12px' }}>
                        <QuestionCircleOutlined style={{ marginRight: 4 }} />
                        互動風格: {experiment.settings?.interaction_style_hint === 'question_based' ? '問句導向' : 
                                 experiment.settings?.interaction_style_hint === 'emoji_rich' ? '表情豐富' : '標準'}
                      </Text>
                    </div>
                    <div style={{ marginBottom: 4 }}>
                      <Text style={{ fontSize: '12px' }}>
                        <Tag style={{ marginRight: 4 }} />
                        股票數量: {experiment.settings?.max_stocks || 5} 支
                      </Text>
                    </div>
                    <div>
                      <Text style={{ fontSize: '12px' }}>
                        <BarChartOutlined style={{ marginRight: 4 }} />
                        最小成交量: {experiment.settings?.min_volume?.toLocaleString() || '1,000,000'}
                      </Text>
                    </div>
                  </div>
                  
                  <div style={{ 
                    padding: '8px', 
                    backgroundColor: `${experiment.color}15`, 
                    borderRadius: '4px',
                    textAlign: 'center',
                    marginBottom: 12
                  }}>
                    <Text strong style={{ color: experiment.color, fontSize: '13px' }}>
                      預期成效: {experiment.expected_performance?.toFixed(1) || '0.0'}%
                    </Text>
                  </div>
                  
                  <div style={{ textAlign: 'center' }}>
                    <Button 
                      type="primary" 
                      size="small"
                      icon={<PlusOutlined />}
                      onClick={() => handleAddExperimentToSchedule(experiment)}
                      style={{ 
                        backgroundColor: experiment.color,
                        borderColor: experiment.color,
                        width: '100%'
                      }}
                    >
                      加入排程
                    </Button>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 計算結果詳細表格 */}
      {calculationResults && (
        <Card 
          title="📊 特徵分析計算結果詳表" 
          extra={
            <Button 
              type="link" 
              onClick={() => setShowCalculationResults(!showCalculationResults)}
            >
              {showCalculationResults ? '隱藏詳表' : '顯示詳表'}
            </Button>
          }
          style={{ marginBottom: 24 }}
        >
          {showCalculationResults && (
            <div>
              {/* 分析摘要 */}
              <div style={{ marginBottom: 24, padding: 16, backgroundColor: '#f5f5f5', borderRadius: 8 }}>
                <Title level={4}>📈 分析摘要</Title>
                <Row gutter={16}>
                  <Col span={6}>
                    <Statistic title="總貼文數" value={calculationResults.summary.totalPosts} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="前20%貼文數" value={calculationResults.summary.top20Count} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="前20%比例" value={`${calculationResults.summary.top20Percentage}%`} />
                  </Col>
                  <Col span={6}>
                    <Text>分析時間: {calculationResults.summary.analysisDate}</Text>
                  </Col>
                </Row>
              </div>

              {/* 前10名高成效貼文 */}
              <div style={{ marginBottom: 24 }}>
                <Title level={4}>🏆 前10名高成效貼文</Title>
                <Table
                  dataSource={calculationResults.topPosts}
                  columns={[
                    { title: '排名', dataIndex: 'rank', key: 'rank', width: 80 },
                    { title: '標題', dataIndex: 'title', key: 'title', ellipsis: true },
                    { title: '總互動', dataIndex: 'totalInteractions', key: 'totalInteractions', width: 100 },
                    { title: '讚', dataIndex: 'likes', key: 'likes', width: 80 },
                    { title: '留言', dataIndex: 'comments', key: 'comments', width: 80 },
                    { title: '分享', dataIndex: 'shares', key: 'shares', width: 80 },
                    { title: '瀏覽', dataIndex: 'views', key: 'views', width: 80 },
                    { title: '打賞', dataIndex: 'donations', key: 'donations', width: 80 }
                  ]}
                  pagination={false}
                  size="small"
                />
              </div>

              {/* 特徵計算詳表 */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                  <Title level={4} style={{ margin: 0 }}>🔍 特徵計算詳表</Title>
                  <div>
                    <Text style={{ marginRight: 16 }}>
                      已選擇 {selectedFeaturesForExperiment.length} 個特徵
                    </Text>
                    <Button 
                      type="primary" 
                      onClick={generateExperimentsFromSelectedFeatures}
                      disabled={selectedFeaturesForExperiment.length === 0}
                    >
                      基於選中特徵生成實驗
                    </Button>
                  </div>
                </div>
                <Table
                  dataSource={calculationResults.featureCalculations}
                  rowSelection={{
                    selectedRowKeys: selectedFeaturesForExperiment,
                    onChange: (selectedRowKeys) => {
                      setSelectedFeaturesForExperiment(selectedRowKeys as string[]);
                    },
                    getCheckboxProps: (record) => ({
                      name: record.featureName,
                    }),
                  }}
                  columns={[
                    { title: '特徵名稱', dataIndex: 'featureName', key: 'featureName', width: 120 },
                    { title: '特徵類型', dataIndex: 'featureType', key: 'featureType', width: 100 },
                    { title: '前20%數量', dataIndex: 'top20Count', key: 'top20Count', width: 100 },
                    { title: '全部數量', dataIndex: 'allCount', key: 'allCount', width: 100 },
                    { 
                      title: '前20%頻率', 
                      dataIndex: 'top20Frequency', 
                      key: 'top20Frequency', 
                      width: 100,
                      render: (value: string) => `${value}%`
                    },
                    { 
                      title: '全部頻率', 
                      dataIndex: 'allFrequency', 
                      key: 'allFrequency', 
                      width: 100,
                      render: (value: string) => `${value}%`
                    },
                    { 
                      title: '改善潛力', 
                      dataIndex: 'improvement', 
                      key: 'improvement', 
                      width: 100,
                      render: (value: string) => (
                        <span style={{ 
                          color: parseFloat(value) > 0 ? '#52c41a' : '#ff4d4f',
                          fontWeight: 'bold'
                        }}>
                          {parseFloat(value) > 0 ? '+' : ''}{value}%
                        </span>
                      )
                    },
                    { 
                      title: '可修改', 
                      dataIndex: 'isModifiable', 
                      key: 'isModifiable', 
                      width: 80,
                      render: (value: boolean) => (
                        <Tag color={value ? 'green' : 'red'}>
                          {value ? '可修改' : '不可修改'}
                        </Tag>
                      )
                    },
                    { title: '修改方法', dataIndex: 'modificationMethod', key: 'modificationMethod', ellipsis: true },
                    { 
                      title: '範例', 
                      dataIndex: 'examples', 
                      key: 'examples', 
                      width: 200,
                      render: (examples: string[]) => (
                        <div>
                          {examples.slice(0, 2).map((example, index) => (
                            <Tag key={index} style={{ marginBottom: 4 }}>{example}</Tag>
                          ))}
                          {examples.length > 2 && <Tag>+{examples.length - 2}</Tag>}
                        </div>
                      )
                    }
                  ]}
                  pagination={false}
                  size="small"
                  scroll={{ x: 1200 }}
                />
              </div>
            </div>
          )}
        </Card>
      )}

      {/* 內容分類分析 */}
      {contentCategories.length > 0 && (
        <Card 
          title="📊 LLM內容分類分析" 
          style={{ marginBottom: 24 }}
        >
          <Alert
            message="基於LLM的內容智能分類"
            description="使用不同指標對貼文進行分類，識別各類別的前5名高成效貼文"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <Row gutter={[16, 16]}>
            {contentCategories.map((category) => (
              <Col span={8} key={category.category_id}>
                <Card size="small" title={category.category_name}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {category.description}
                      </Text>
                    </div>
                    <div>
                      <Text strong>平均成效分數: </Text>
                      <Text style={{ color: '#1890ff' }}>
                        {category.avg_performance_score.toFixed(1)}
                      </Text>
                    </div>
                    <div>
                      <Text strong>成功率: </Text>
                      <Text style={{ color: '#52c41a' }}>
                        {(category.success_rate * 100).toFixed(1)}%
                      </Text>
                    </div>
                    <div>
                      <Text strong>關鍵特徵: </Text>
                      <Space wrap>
                        {category.key_characteristics.slice(0, 3).map((char, index) => (
                          <Tag key={index} size="small" color="blue">
                            {char}
                          </Tag>
                        ))}
                      </Space>
                    </div>
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 自動生成發文設定 */}
      {generatedSettings.length > 0 && (
        <Card 
          title="⚙️ 自動生成發文設定" 
          style={{ marginBottom: 24 }}
        >
          <Alert
            message="基於高成效特徵自動生成的發文設定"
            description="系統根據分析結果自動生成多種不同的發文設定，包含不同觸發器、內容長度、互動元素等"
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <Row gutter={[16, 16]}>
            {generatedSettings.map((setting) => (
              <Col span={8} key={setting.setting_id}>
                <Card 
                  size="small" 
                  title={setting.setting_name}
                  extra={
                    <Space>
                      <Tag color="blue">{setting.trigger_type}</Tag>
                      <Text style={{ fontSize: '12px' }}>
                        預期成效: {setting.expected_performance.toFixed(1)}
                      </Text>
                    </Space>
                  }
                >
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {setting.description}
                      </Text>
                    </div>
                    
                    <Divider style={{ margin: '8px 0' }} />
                    
                    <div>
                      <Text strong style={{ fontSize: '12px' }}>設定參數:</Text>
                      <div style={{ marginTop: 4 }}>
                        <Space wrap>
                          <Tag size="small" color="green">
                            內容長度: {setting.content_length}
                          </Tag>
                          <Tag size="small" color="blue">
                            幽默程度: {setting.humor_level}
                          </Tag>
                          <Tag size="small" color="orange">
                            KOL風格: {setting.kol_style}
                          </Tag>
                        </Space>
                      </div>
                    </div>
                    
                    <div>
                      <Text strong style={{ fontSize: '12px' }}>互動元素:</Text>
                      <div style={{ marginTop: 4 }}>
                        <Space wrap>
                          {setting.has_question_interaction && (
                            <Tag size="small" color="purple">問句互動</Tag>
                          )}
                          {setting.has_emoji && (
                            <Tag size="small" color="purple">表情符號</Tag>
                          )}
                          {setting.has_hashtag && (
                            <Tag size="small" color="purple">標籤</Tag>
                          )}
                          {setting.has_news_link && (
                            <Tag size="small" color="purple">新聞連結</Tag>
                          )}
                        </Space>
                      </div>
                    </div>
                    
                    <div>
                      <Text strong style={{ fontSize: '12px' }}>發文時段:</Text>
                      <div style={{ marginTop: 4 }}>
                        <Text style={{ fontSize: '11px' }}>
                          {setting.posting_time_preference.join(', ')}
                        </Text>
                      </div>
                    </div>
                    
                    <div>
                      <Text strong style={{ fontSize: '12px' }}>基於特徵:</Text>
                      <div style={{ marginTop: 4 }}>
                        <Space wrap>
                          {setting.based_on_features.slice(0, 2).map((feature, index) => (
                            <Tag key={index} size="small" color="cyan">
                              {feature}
                            </Tag>
                          ))}
                        </Space>
                      </div>
                    </div>
                    
                    <div style={{ textAlign: 'center', marginTop: 8 }}>
                      <Button 
                        type="primary" 
                        size="small"
                        onClick={() => message.info('設定應用功能開發中')}
                      >
                        應用設定
                      </Button>
                    </div>
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 智能實驗管理 */}
      {experiments.length > 0 && (
        <Card 
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>🧪 智能實驗管理</span>
              <Button 
                type="primary" 
                icon={<ExperimentOutlined />}
                onClick={generateSmartExperiments}
                style={{ marginLeft: 16 }}
              >
                生成新實驗
              </Button>
            </div>
          } 
          style={{ marginBottom: 24 }}
        >
          {experiments.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <ExperimentOutlined style={{ fontSize: '48px', color: '#d9d9d9', marginBottom: 16 }} />
              <Text type="secondary">暫無實驗，點擊上方按鈕生成智能實驗</Text>
            </div>
          ) : (
            <Table
              columns={experimentColumns}
              dataSource={experiments}
              rowKey="id"
              pagination={false}
              size="small"
            />
          )}
        </Card>
      )}

      {/* 學習洞察 */}
      {insights.length > 0 && (
        <Card 
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>💡 自我學習洞察</span>
              <Button 
                type="primary" 
                icon={<BulbOutlined />}
                onClick={generateSelfLearningInsights}
                style={{ marginLeft: 16 }}
              >
                生成新洞察
              </Button>
            </div>
          } 
          style={{ marginBottom: 24 }}
        >
          {insights.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <BulbOutlined style={{ fontSize: '48px', color: '#d9d9d9', marginBottom: 16 }} />
              <Text type="secondary">暫無洞察，點擊上方按鈕生成學習洞察</Text>
            </div>
          ) : (
            <List
              dataSource={insights}
              renderItem={(insight) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Avatar 
                        style={{ 
                          backgroundColor: insight.type === 'success' ? '#52c41a' : 
                                          insight.type === 'warning' ? '#fa8c16' : 
                                          insight.type === 'pattern' ? '#1890ff' : '#722ed1'
                        }}
                        icon={
                          insight.type === 'success' ? <CheckCircleOutlined /> :
                          insight.type === 'warning' ? <WarningOutlined /> :
                          insight.type === 'pattern' ? <BarChartOutlined /> : <InfoCircleOutlined />
                        }
                      />
                    }
                    title={
                      <Space>
                        <Text strong>{insight.title}</Text>
                        <Tag color={insight.impact === 'high' ? 'red' : insight.impact === 'medium' ? 'orange' : 'green'}>
                          {insight.impact === 'high' ? '高影響' : insight.impact === 'medium' ? '中影響' : '低影響'}
                        </Tag>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          信心度: {insight.confidence}%
                        </Text>
                      </Space>
                    }
                    description={
                      <div>
                        <Paragraph style={{ marginBottom: 8 }}>{insight.description}</Paragraph>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          建議行動: {insight.action}
                        </Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      )}

      {/* 學習流程 */}
      <Card title="🔄 自我學習流程" style={{ marginBottom: 24 }}>
        <Steps current={2} size="small">
          <Step title="數據收集" description="收集互動數據" icon={<BarChartOutlined />} />
          <Step title="特徵分析" description="分析高互動特徵" icon={<FilterOutlined />} />
          <Step title="智能排名" description="特徵重要性排名" icon={<CrownOutlined />} />
          <Step title="實驗生成" description="生成智能實驗" icon={<ExperimentOutlined />} />
          <Step title="效果驗證" description="驗證實驗效果" icon={<CheckCircleOutlined />} />
          <Step title="策略優化" description="優化發文策略" icon={<SettingOutlined />} />
        </Steps>
      </Card>

      {/* 排程設定 Modal */}
      <BatchScheduleModal
        visible={scheduleModalVisible}
        onCancel={() => {
          setScheduleModalVisible(false);
          setSelectedFeatureForSchedule(null);
        }}
        onConfirm={handleConfirmSchedule}
        batchData={selectedFeatureForSchedule ? (() => {
          // 根據選中的特徵生成對應的排程設定
          const feature = selectedFeatureForSchedule;
          
          // 檢查是否來自實驗設定
          if (feature.feature_type === 'experiment') {
            // 如果是實驗，使用實驗的設定
            const experiment = smartExperiments.find(exp => exp.id === feature.feature_id);
            if (experiment && experiment.settings) {
              return {
                session_id: `experiment_${feature.feature_id}`,
                total_posts: 1,
                published_posts: 0,
                success_rate: Math.round(experiment.expected_performance || 50),
                trigger_type: experiment.settings.trigger_type || 'limit_up_after_hours',
                kol_assignment: 'random',
                created_at: new Date().toISOString(),
                status: 'completed',
                stock_codes: ['2330', '2317', '2454'],
                kol_names: ['龜狗一日散戶', '板橋大who'],
                posts: [{
                  post_id: `experiment_post_${feature.feature_id}`,
                  title: `基於${feature.feature_name}的實驗貼文`,
                  content: '這是一個基於高成效特徵生成的實驗貼文...',
                  kol_nickname: '實驗KOL',
                  status: 'pending',
                  generation_config: {
                    posting_type: experiment.settings.posting_type || 'analysis', // 🔥 關鍵修復：使用實驗的 posting_type
                    trigger_type: experiment.settings.trigger_type || 'limit_up_after_hours',
                    max_stocks: experiment.settings.max_stocks || 5,
                    content_length: experiment.settings.content_length || 'medium',
                    max_words: experiment.settings.max_words || 500,
                    content_style: experiment.settings.content_style || 'technical',
                    enable_news_links: true,
                    news_max_links: 5,
                    kol_assignment: 'random',
                    generation_mode: 'high_quality',
                    include_risk_warning: true,
                    include_charts: false
                  }
                }]
              };
            }
          }
          
          // 根據特徵自動調整設定
          let postingType = 'analysis'; // 預設為發表分析
          let triggerType = 'limit_up_after_hours';
          let maxStocks = 5;
          let contentLength = 'medium';
          let maxWords = 500;
          let contentStyle = 'technical';
          let executionTime = '14:00';
          
          // 根據特徵自動調整設定
          if (feature.feature_id === 'has_question') {
            postingType = 'interaction'; // 互動發問
            triggerType = 'limit_up_after_hours';
            maxStocks = 3;
            contentLength = 'short';
            maxWords = 200;
            contentStyle = 'casual';
          } else if (feature.feature_id === 'has_emoji') {
            postingType = 'analysis';
            triggerType = 'volume_surge';
            maxStocks = 4;
            contentLength = 'medium';
            maxWords = 400;
            contentStyle = 'humorous';
          } else if (feature.feature_id === 'content_length_medium') {
            postingType = 'analysis';
            triggerType = 'limit_up_after_hours';
            maxStocks = 5;
            contentLength = 'medium';
            maxWords = 500;
            contentStyle = 'technical';
          } else if (feature.feature_id === 'multi_tags') {
            postingType = 'analysis';
            triggerType = 'limit_up_after_hours';
            maxStocks = 5;
            contentLength = 'medium';
            maxWords = 400;
            contentStyle = 'technical';
          } else if (feature.feature_id === 'has_technical_analysis') {
            postingType = 'analysis';
            triggerType = 'volume_surge';
            maxStocks = 3;
            contentLength = 'long';
            maxWords = 600;
            contentStyle = 'technical';
          } else if (feature.feature_id === 'system_source') {
            postingType = 'analysis';
            triggerType = 'limit_up_after_hours';
            maxStocks = 5;
            contentLength = 'medium';
            maxWords = 400;
            contentStyle = 'technical';
          } else if (feature.feature_id === 'afternoon_posting') {
            postingType = 'analysis';
            triggerType = 'limit_up_after_hours';
            maxStocks = 5;
            contentLength = 'medium';
            maxWords = 400;
            contentStyle = 'technical';
            executionTime = '15:00';
          } else if (feature.feature_id === 'morning_posting') {
            postingType = 'analysis';
            triggerType = 'volume_surge';
            maxStocks = 5;
            contentLength = 'medium';
            maxWords = 400;
            contentStyle = 'technical';
            executionTime = '10:00';
          } else if (feature.feature_id === 'content_length_short') {
            postingType = 'interaction';
            triggerType = 'limit_up_after_hours';
            maxStocks = 3;
            contentLength = 'short';
            maxWords = 150;
            contentStyle = 'casual';
          } else if (feature.feature_id === 'has_hashtag') {
            postingType = 'analysis';
            triggerType = 'volume_surge';
            maxStocks = 4;
            contentLength = 'medium';
            maxWords = 400;
            contentStyle = 'casual';
          }
          
          return {
            session_id: `feature_${feature.feature_id}`,
            total_posts: 1,
            published_posts: 0,
            success_rate: Math.round(feature.improvement_potential * 100),
            trigger_type: triggerType,
            kol_assignment: 'random',
            created_at: new Date().toISOString(),
            status: 'completed',
            stock_codes: ['2330', '2317', '2454'],
            kol_names: ['龜狗一日散戶', '板橋大who'],
            posts: [{
              post_id: `feature_post_${feature.feature_id}`,
              title: `基於${feature.feature_name}的實驗貼文`,
              content: '這是一個基於高成效特徵生成的實驗貼文...',
              kol_nickname: '實驗KOL',
              status: 'pending',
              generation_config: {
                posting_type: postingType,
                trigger_type: triggerType,
                max_stocks: maxStocks,
                content_length: contentLength,
                max_words: maxWords,
                content_style: contentStyle,
                enable_news_links: true,
                news_max_links: 5,
                kol_assignment: 'random',
                generation_mode: 'high_quality',
                include_risk_warning: true,
                include_charts: false
              }
            }]
          };
        })() : null}
      />
    </div>
  );
};

export default SelfLearningPage;
