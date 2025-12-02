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
  Alert
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
  ExportOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getApiBaseUrl } from '../config/api';
import dayjs from 'dayjs';


const API_BASE_URL = getApiBaseUrl();
const { Title, Text } = Typography;
const { Option } = Select;
const { Search } = Input;
const { RangePicker } = DatePicker;

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

interface KOLStats {
  kol_nickname: string;
  post_count: number;
  system_posts: number;
  external_posts: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  total_bookmarks: number;
  avg_engagement_rate: number;
}

interface OverallStats {
  total_posts: number;
  system_posts: number;
  external_posts: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  total_bookmarks: number;
  avg_engagement_rate: number;
}

const InteractionAnalysisPage: React.FC = () => {
  const [posts, setPosts] = useState<InteractionPost[]>([]);
  const [kolStats, setKolStats] = useState<Record<number, KOLStats>>({});
  const [overallStats, setOverallStats] = useState<OverallStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // 篩選條件
  const [selectedKOLs, setSelectedKOLs] = useState<number[]>([]); // 🔥 改為多選
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  const [includeExternal, setIncludeExternal] = useState(true);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [timeQuickFilter, setTimeQuickFilter] = useState<string>('all'); // 時間快速篩選
  const [selectedStock, setSelectedStock] = useState<string | undefined>(undefined); // 個股篩選
  const [selectedTrigger, setSelectedTrigger] = useState<string | undefined>(undefined); // 觸發器篩選
  
  // 排序條件
  const [sortField, setSortField] = useState<string>('total_interactions');
  const [sortOrder, setSortOrder] = useState<'ascend' | 'descend'>('descend');
  const [showTop30, setShowTop30] = useState(false);
  const [showFeatureAnalysis, setShowFeatureAnalysis] = useState(false);
  const [showSchedulingSuggestions, setShowSchedulingSuggestions] = useState(false);
  const [schedulingSuggestions, setSchedulingSuggestions] = useState<any[]>([]);

  // 計算總互動數
  const calculateTotalInteractions = (post: InteractionPost): number => {
    return (post.likes || 0) + (post.comments || 0) + (post.shares || 0) + (post.bookmarks || 0);
  };

  // 🔥 獲取所有唯一的股票標籤
  const uniqueStocks = useMemo(() => {
    const stockSet = new Set<string>();
    posts.forEach(post => {
      if (post.commodity_tags && Array.isArray(post.commodity_tags)) {
        post.commodity_tags.forEach(tag => {
          if (tag.key) stockSet.add(tag.key);
        });
      }
    });
    return Array.from(stockSet).sort();
  }, [posts]);

  // 🔥 獲取所有唯一的 KOL
  const uniqueKOLs = useMemo(() => {
    const kolMap = new Map<number, string>();
    posts.forEach(post => {
      if (post.kol_serial && !kolMap.has(post.kol_serial)) {
        kolMap.set(post.kol_serial, post.kol_nickname);
      }
    });
    return Array.from(kolMap.entries()).map(([serial, nickname]) => ({ serial, nickname }));
  }, [posts]);

  // 🔥 時間快速篩選處理
  const handleTimeQuickFilter = (value: string) => {
    setTimeQuickFilter(value);

    switch (value) {
      case 'today':
        setDateRange([dayjs().startOf('day'), dayjs().endOf('day')]);
        break;
      case 'yesterday':
        setDateRange([dayjs().subtract(1, 'day').startOf('day'), dayjs().subtract(1, 'day').endOf('day')]);
        break;
      case 'week':
        setDateRange([dayjs().subtract(7, 'day').startOf('day'), dayjs().endOf('day')]);
        break;
      case 'month':
        setDateRange([dayjs().subtract(30, 'day').startOf('day'), dayjs().endOf('day')]);
        break;
      case 'custom':
        // 使用者自選日期範圍
        return;
      case 'all':
      default:
        setDateRange(null);
        return;
    }
  };

  // 分析幽默程度
  const analyzeHumorLevel = (title: string, content: string): 'none' | 'light' | 'moderate' | 'strong' => {
    const fullText = title + ' ' + content;
    let humorScore = 0;

    // 輕度幽默關鍵字
    const lightHumorKeywords = ['有趣', '好玩', '不錯', '厲害', '👍', '👏'];
    lightHumorKeywords.forEach(keyword => {
      if (fullText.includes(keyword)) humorScore += 1;
    });

    // 中度幽默關鍵字
    const moderateHumorKeywords = ['哈哈', '笑死', '搞笑', '幽默', '😄', '😆', 'XD', 'LOL'];
    moderateHumorKeywords.forEach(keyword => {
      if (fullText.includes(keyword)) humorScore += 2;
    });

    // 強烈幽默關鍵字
    const strongHumorKeywords = ['笑到肚子痛', '笑到流淚', '笑到不行', '😂', '🤣', '笑死我了', '太搞笑了'];
    strongHumorKeywords.forEach(keyword => {
      if (fullText.includes(keyword)) humorScore += 3;
    });

    // Emoji幽默檢測
    const humorEmojis = ['😂', '🤣', '😄', '😆', '😅', '🤭', '😜', '😝', '🤪'];
    humorEmojis.forEach(emoji => {
      if (fullText.includes(emoji)) humorScore += 2;
    });

    // 根據分數判斷幽默程度
    if (humorScore === 0) return 'none';
    else if (humorScore <= 2) return 'light';
    else if (humorScore <= 5) return 'moderate';
    else return 'strong';
  };

  // 排序和篩選貼文
  const getSortedAndFilteredPosts = (): InteractionPost[] => {
    let filteredPosts = [...posts];

    // 🔥 應用 KOL 篩選（多選）
    if (selectedKOLs.length > 0) {
      filteredPosts = filteredPosts.filter(post => selectedKOLs.includes(post.kol_serial));
    }

    // 🔥 應用個股篩選
    if (selectedStock) {
      filteredPosts = filteredPosts.filter(post =>
        post.commodity_tags?.some(tag => tag.key === selectedStock)
      );
    }

    // 🔥 應用時間篩選（使用 dayjs）
    if (dateRange && dateRange[0] && dateRange[1]) {
      const startDate = dateRange[0].valueOf();
      const endDate = dateRange[1].valueOf();
      filteredPosts = filteredPosts.filter(post => {
        const postDate = new Date(post.create_time).getTime();
        return postDate >= startDate && postDate <= endDate;
      });
    }

    // 應用搜索篩選
    if (searchKeyword) {
      filteredPosts = filteredPosts.filter(post =>
        post.title.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        post.content.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        post.kol_nickname.toLowerCase().includes(searchKeyword.toLowerCase())
      );
    }

    // 添加總互動數
    const postsWithTotal = filteredPosts.map(post => ({
      ...post,
      total_interactions: calculateTotalInteractions(post)
    }));

    // 排序
    postsWithTotal.sort((a, b) => {
      let aValue: number, bValue: number;
      
      switch (sortField) {
        case 'total_interactions':
          aValue = a.total_interactions;
          bValue = b.total_interactions;
          break;
        case 'likes':
          aValue = a.likes || 0;
          bValue = b.likes || 0;
          break;
        case 'comments':
          aValue = a.comments || 0;
          bValue = b.comments || 0;
          break;
        case 'shares':
          aValue = a.shares || 0;
          bValue = b.shares || 0;
          break;
        case 'views':
          aValue = a.views || 0;
          bValue = b.views || 0;
          break;
        case 'engagement_rate':
          aValue = a.engagement_rate || 0;
          bValue = b.engagement_rate || 0;
          break;
        default:
          aValue = a.total_interactions;
          bValue = b.total_interactions;
      }

      if (sortOrder === 'ascend') {
        return aValue - bValue;
      } else {
        return bValue - aValue;
      }
    });

    // 如果選擇顯示前30名，則限制數量
    if (showTop30) {
      return postsWithTotal.slice(0, 30);
    }

    return postsWithTotal;
  };

  // 分析貼文特徵（通用函數）
  const analyzePostFeatures = (posts: InteractionPost[]) => {
    const features = {
      // 發文時間分析
      postingTime: {
        morning: 0,    // 6-12點
        afternoon: 0,   // 12-18點
        evening: 0,    // 18-24點
        night: 0       // 0-6點
      },
      // 股票標記
      hasStockTags: 0,
      stockTagCount: 0,
      // 熱門話題
      hasTrendingTopic: 0,
      // 內容長度
      avgContentLength: 0,
      shortContent: 0,    // < 200字
      mediumContent: 0,   // 200-500字
      longContent: 0,     // > 500字
      // 幽默模式檢測
      hasHumorMode: 0,
      // 新聞連結
      hasNewsLinks: 0,
      // KOL分析
      kolDistribution: {} as Record<string, number>,
      // 來源分析
      sourceDistribution: { system: 0, external: 0 },
      // 互動數據分析
      avgTotalInteractions: 0,
      avgLikes: 0,
      avgComments: 0,
      avgShares: 0,
      avgBookmarks: 0,
      avgViews: 0,
      avgEngagementRate: 0,
      // 標題分析
      avgTitleLength: 0,
      shortTitle: 0,      // < 20字
      mediumTitle: 0,     // 20-40字
      longTitle: 0,       // > 40字
      // 文章架構分析
      hasEmoji: 0,
      hasHashtag: 0,
      hasQuestion: 0,
      hasExclamation: 0,
      hasNumber: 0,
      hasStockCode: 0,
      // 幽默型內容分析
      humorType: {
        none: 0,          // 無幽默
        light: 0,         // 輕度幽默
        moderate: 0,      // 中度幽默
        strong: 0         // 強烈幽默
      },
      // 內容結構分析
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

      // 幽默型內容分析（更詳細的檢測）
      const humorScore = analyzeHumorLevel(post.title, post.content);
      features.humorType[humorScore]++;

      // 幽默模式檢測（簡單關鍵字檢測）
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

  // 分析高互動貼文特徵
  const analyzeHighInteractionFeatures = () => {
    const sortedPosts = getSortedAndFilteredPosts();
    const totalPosts = sortedPosts.length;
    const top10PercentCount = Math.max(1, Math.floor(totalPosts * 0.1));
    const top10PercentPosts = sortedPosts.slice(0, top10PercentCount);
    const allPosts = sortedPosts;

    // 分析前10%和所有貼文
    const top10Analysis = analyzePostFeatures(top10PercentPosts);
    const allAnalysis = analyzePostFeatures(allPosts);

    return {
      totalPosts,
      top10PercentCount,
      top10PercentPosts,
      top10Analysis,
      allAnalysis
    };
  };

  // 使用 useMemo 來優化分析數據計算，避免無限重新渲染
  const analysisData = useMemo(() => {
    if (!showFeatureAnalysis || posts.length === 0) {
      return null;
    }
    return analyzeHighInteractionFeatures();
  }, [showFeatureAnalysis, posts, selectedKOLs, dateRange, includeExternal, searchKeyword, sortField, sortOrder, showTop30]);

  // 🔥 計算選中 KOL 群體的統計數據
  const selectedKOLGroupStats = useMemo(() => {
    if (selectedKOLs.length === 0 || posts.length === 0) {
      return null;
    }

    const filteredPosts = posts.filter(post => selectedKOLs.includes(post.kol_serial));
    if (filteredPosts.length === 0) return null;

    const stats = {
      totalPosts: filteredPosts.length,
      totalLikes: 0,
      totalComments: 0,
      totalShares: 0,
      totalViews: 0,
      kolDetails: [] as Array<{
        serial: number;
        nickname: string;
        postCount: number;
        likes: number;
        comments: number;
        shares: number;
        views: number;
        avgInteractions: number;
      }>
    };

    // 計算每個 KOL 的統計
    const kolMap = new Map<number, typeof stats.kolDetails[0]>();

    filteredPosts.forEach(post => {
      stats.totalLikes += post.likes || 0;
      stats.totalComments += post.comments || 0;
      stats.totalShares += post.shares || 0;
      stats.totalViews += post.views || 0;

      if (!kolMap.has(post.kol_serial)) {
        kolMap.set(post.kol_serial, {
          serial: post.kol_serial,
          nickname: post.kol_nickname,
          postCount: 0,
          likes: 0,
          comments: 0,
          shares: 0,
          views: 0,
          avgInteractions: 0
        });
      }
      const kolStat = kolMap.get(post.kol_serial)!;
      kolStat.postCount++;
      kolStat.likes += post.likes || 0;
      kolStat.comments += post.comments || 0;
      kolStat.shares += post.shares || 0;
      kolStat.views += post.views || 0;
    });

    // 計算平均互動數
    kolMap.forEach(kolStat => {
      kolStat.avgInteractions = kolStat.postCount > 0
        ? (kolStat.likes + kolStat.comments + kolStat.shares) / kolStat.postCount
        : 0;
    });

    stats.kolDetails = Array.from(kolMap.values()).sort((a, b) => b.avgInteractions - a.avgInteractions);

    return stats;
  }, [selectedKOLs, posts]);

  // 生成排程建議
  const generateSchedulingSuggestions = () => {
    const suggestions = [
      {
        id: 1,
        name: "高互動時段發文策略",
        description: "基於前10%高互動貼文的發文時間分析",
        settings: {
          preferredTimeSlots: ["14:00-16:00", "19:00-21:00"],
          contentLength: "200-500字",
          humorLevel: "輕度幽默",
          stockTags: "包含2-3個股票標記",
          features: ["包含Emoji", "有問號互動", "系統發文"]
        },
        expectedEngagement: "預期互動率提升 25%",
        color: "#52c41a"
      },
      {
        id: 2,
        name: "內容結構優化策略", 
        description: "參考高互動貼文的內容特徵",
        settings: {
          preferredTimeSlots: ["09:00-11:00", "15:00-17:00"],
          contentLength: "300-600字",
          humorLevel: "中度幽默",
          stockTags: "包含1-2個熱門股票標記",
          features: ["有段落結構", "包含數字", "有驚嘆號"]
        },
        expectedEngagement: "預期互動率提升 18%",
        color: "#1890ff"
      },
      {
        id: 3,
        name: "KOL個性化發文策略",
        description: "針對特定KOL的高互動模式",
        settings: {
          preferredTimeSlots: ["12:00-14:00", "20:00-22:00"],
          contentLength: "150-400字",
          humorLevel: "強烈幽默",
          stockTags: "包含3-4個股票標記",
          features: ["有Hashtag", "包含引用", "有條列式內容"]
        },
        expectedEngagement: "預期互動率提升 32%",
        color: "#722ed1"
      }
    ];
    
    setSchedulingSuggestions(suggestions);
    setShowSchedulingSuggestions(true);
  };

  // 獲取互動分析數據
  const fetchInteractionAnalysis = async () => {
    console.log('🔄 開始獲取互動分析數據...');
    setLoading(true);
    try {
      // 使用現有的 posts API 獲取已發布的貼文數據
      console.log(`📡 發送 API 請求到: ${API_BASE_URL}/api/posts?limit=10000&status=published`);
      const response = await fetch(`${API_BASE_URL}/api/posts?limit=10000&status=published`);
      console.log('📥 API 回應狀態:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('📊 獲取到數據:', result.posts ? result.posts.length : 0, '篇貼文');
      console.log('📊 完整 API 回應:', result);
      
      // 檢查響應結構
      if (!result || !result.posts) {
        console.error('❌ API 響應格式錯誤:', result);
        message.error('API 響應格式錯誤');
        setPosts([]);
        setOverallStats(null);
        return;
      }

      if (result.posts && Array.isArray(result.posts)) {
        console.log('✅ 數據格式正確，開始轉換...');
        console.log('⚠️ 注意：CMoney API 憑證已失效，顯示的是數據庫中現有的互動數據');
        
        // 轉換貼文數據為互動分析格式
        const interactionPosts: InteractionPost[] = result.posts.map((post: any) => ({
          post_id: post.post_id,
          article_id: post.post_id, // 使用 post_id 作為 article_id
          kol_serial: post.kol_serial || 0,
          kol_nickname: post.kol_nickname || 'Unknown KOL',
          title: post.title || '無標題',
          content: post.content || '',
          article_url: post.cmoney_post_url || '',
          create_time: post.created_at || new Date().toISOString(),
          commodity_tags: post.commodity_tags || [],
          community_topic: post.topic_title || undefined,
          source: 'system' as const,
          status: post.status || 'draft',
          views: post.views || 0,
          likes: post.likes || 0,
          comments: post.comments || 0,
          shares: post.shares || 0,
          bookmarks: 0,
          donations: post.donations || 0,  // 🔥 使用 API 返回的打賞數據
          engagement_rate: post.views > 0 ? ((post.likes || 0) + (post.comments || 0) + (post.shares || 0)) / post.views : 0
        }));

        console.log('📝 設置貼文數據:', interactionPosts.length, '篇');
        console.log('📝 前 3 篇貼文數據:', interactionPosts.slice(0, 3));
        setPosts(interactionPosts);
        console.log('✅ setPosts 調用完成');

        // 計算 KOL 統計
        console.log('📊 開始計算 KOL 統計...');
        const kolStatsMap: Record<number, KOLStats> = {};
        const overallStats: OverallStats = {
          total_posts: interactionPosts.length,
          system_posts: interactionPosts.length,
          external_posts: 0,
          total_views: 0,
          total_likes: 0,
          total_comments: 0,
          total_shares: 0,
          total_bookmarks: 0,
          avg_engagement_rate: 0
        };

        interactionPosts.forEach(post => {
          // 更新總體統計
          overallStats.total_views += post.views;
          overallStats.total_likes += post.likes;
          overallStats.total_comments += post.comments;
          overallStats.total_shares += post.shares;
          overallStats.total_bookmarks += post.bookmarks;

          // 更新 KOL 統計
          if (!kolStatsMap[post.kol_serial]) {
            kolStatsMap[post.kol_serial] = {
              kol_nickname: post.kol_nickname,
              post_count: 0,
              system_posts: 0,
              external_posts: 0,
              total_views: 0,
              total_likes: 0,
              total_comments: 0,
              total_shares: 0,
              total_bookmarks: 0,
              avg_engagement_rate: 0
            };
          }

          const kolStats = kolStatsMap[post.kol_serial];
          kolStats.post_count++;
          kolStats.system_posts++;
          kolStats.total_views += post.views;
          kolStats.total_likes += post.likes;
          kolStats.total_comments += post.comments;
          kolStats.total_shares += post.shares;
          kolStats.total_bookmarks += post.bookmarks;
        });

        // 計算平均互動率
        overallStats.avg_engagement_rate = overallStats.total_posts > 0 ? 
          (overallStats.total_likes + overallStats.total_comments + overallStats.total_shares) / overallStats.total_posts : 0;

        Object.values(kolStatsMap).forEach(kolStats => {
          kolStats.avg_engagement_rate = kolStats.post_count > 0 ? 
            (kolStats.total_likes + kolStats.total_comments + kolStats.total_shares) / kolStats.post_count : 0;
        });

        console.log('✅ 設置統計數據完成');
        setKolStats(kolStatsMap);
        setOverallStats(overallStats);
        console.log('🎉 互動分析數據加載完成！');
      } else {
        console.error('❌ 數據格式錯誤:', result);
        message.error('獲取貼文數據失敗');
      }
    } catch (error) {
      console.error('獲取互動分析數據失敗:', error);
      message.error('獲取互動分析數據失敗');
    } finally {
      setLoading(false);
    }
  };

  // 批量刷新互動數據（從 CMoney API 抓取最新數據並更新到資料庫）
  const refreshAllInteractions = async () => {
    setRefreshing(true);

    // 獲取當前篩選後的貼文
    const filteredPosts = getSortedAndFilteredPosts();
    const hasFilters = filteredPosts.length > 0 && filteredPosts.length < posts.length;

    // 如果有篩選條件，只刷新篩選後的貼文；否則刷新全部
    const endpoint = hasFilters
      ? `${API_BASE_URL}/api/posts/refresh-filtered`
      : `${API_BASE_URL}/api/posts/refresh-all`;

    const filterInfo = hasFilters
      ? `篩選後的 ${filteredPosts.length} 篇`
      : '所有';

    message.loading({
      content: `正在從 CMoney API 刷新${filterInfo}貼文的互動數據...`,
      key: 'refresh-interactions',
      duration: 0
    });

    try {
      // 如果有篩選，發送篩選後的 post_ids
      const requestBody = hasFilters
        ? { post_ids: filteredPosts.map(p => p.post_id), limit: 200 }
        : {};

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const result = await response.json();

      if (result.success) {
        message.destroy('refresh-interactions');
        if (result.updated_count > 0) {
          message.success({
            content: `刷新成功！從 CMoney API 更新了 ${result.updated_count} 篇貼文的互動數據，失敗 ${result.failed_count} 篇`,
            duration: 5
          });
        } else if (result.total_posts === 0) {
          message.warning({
            content: '沒有找到符合條件的已發布貼文',
            duration: 3
          });
        } else {
          message.warning({
            content: `找到 ${result.total_posts} 篇貼文，但全部刷新失敗。請檢查 KOL 的登入憑證是否正確。`,
            duration: 5
          });
        }
        // 重新獲取數據以顯示更新後的結果
        await fetchInteractionAnalysis();
      } else {
        message.destroy('refresh-interactions');
        message.error({
          content: `刷新失敗: ${result.error || '未知錯誤'}`,
          duration: 5
        });
      }
    } catch (error) {
      message.destroy('refresh-interactions');
      console.error('批量刷新失敗:', error);
      message.error({
        content: '批量刷新失敗: ' + (error as Error).message,
        duration: 5
      });
    } finally {
      setRefreshing(false);
    }
  };

  // 刷新篩選後的貼文互動數據
  const refreshFilteredInteractions = async () => {
    if (selectedKOLs.length === 0) {
      message.info('請先選擇要刷新的 KOL');
      return;
    }
    await refreshAllInteractions();
  };

  // 去重功能（現已整合到刷新功能中）
  const deduplicatePosts = async () => {
    message.info('去重功能已整合至批量刷新功能中');
    await refreshAllInteractions();
  };

  // 打開外部連結
  const openExternalLink = (url: string) => {
    if (url) {
      window.open(url, '_blank');
    }
  };

  // 複製到剪貼板
  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text).then(() => {
      message.success(`${label}已複製到剪貼板`);
    }).catch(() => {
      message.error('複製失敗');
    });
  };

  // 下載 CSV
  const downloadCSV = () => {
    const filteredPosts = getSortedAndFilteredPosts();
    if (filteredPosts.length === 0) {
      message.warning('沒有數據可下載');
      return;
    }

    // CSV 標題行
    const headers = [
      'KOL Serial',
      'KOL 暱稱',
      '標題',
      '讚數',
      '留言數',
      '分享數',
      '總互動',
      '發文時間',
      'Article ID',
      '貼文連結'
    ];

    // 轉換數據為 CSV 行
    const rows = filteredPosts.map(post => [
      post.kol_serial,
      `"${(post.kol_nickname || '').replace(/"/g, '""')}"`,
      `"${(post.title || '').replace(/"/g, '""')}"`,
      post.likes || 0,
      post.comments || 0,
      post.shares || 0,
      (post.likes || 0) + (post.comments || 0) + (post.shares || 0),
      post.create_time || '',
      post.article_id || '',
      post.article_url || ''
    ]);

    // 組合 CSV 內容
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    // 建立下載連結
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `互動分析_${dayjs().format('YYYYMMDD_HHmmss')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    message.success(`已下載 ${filteredPosts.length} 筆數據`);
  };

  // 表格列定義
  const columns: ColumnsType<InteractionPost> = [
    {
      title: '發文者',
      dataIndex: 'kol_nickname',
      key: 'kol_nickname',
      width: 120,
      render: (text: string, record: InteractionPost) => (
        <Space direction="vertical" size="small">
          <Tag icon={<UserOutlined />} color="blue">
            {text}
          </Tag>
          <Text code style={{ fontSize: '10px' }}>
            {record.kol_serial}
          </Text>
        </Space>
      ),
    },
    {
      title: 'Article ID',
      dataIndex: 'article_id',
      key: 'article_id',
      width: 100,
      render: (text: string) => (
        <Text 
          code 
          style={{ cursor: 'pointer', fontSize: '11px' }}
          onClick={() => copyToClipboard(text, '文章ID')}
        >
          {text}
        </Text>
      ),
    },
    {
      title: '標題',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      render: (text: string, record: InteractionPost) => (
        <div>
          <Text strong ellipsis={{ tooltip: text }}>
            {text}
          </Text>
          <div style={{ marginTop: 4 }}>
            <Space size="small">
              {record.source === 'system' ? (
                <Tag color="green" size="small">系統</Tag>
              ) : (
                <Tag color="orange" size="small">外部</Tag>
              )}
              {record.community_topic && (
                <Tag color="purple" size="small">熱門話題</Tag>
              )}
            </Space>
          </div>
        </div>
      ),
    },
    {
      title: '商品標籤',
      dataIndex: 'commodity_tags',
      key: 'commodity_tags',
      width: 120,
      render: (tags: Array<{key: string, type: string, bullOrBear: string}>) => (
        <Space wrap>
          {tags.map((tag, index) => (
            <Tag 
              key={index} 
              color={tag.bullOrBear === '0' ? 'green' : 'red'}
              size="small"
            >
              {tag.key}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '發文時間',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 120,
      render: (text: string) => (
        <Space>
          <CalendarOutlined />
          <Text style={{ fontSize: '11px' }}>
            {new Date(text).toLocaleDateString()}
          </Text>
        </Space>
      ),
    },
    {
      title: '讚數',
      dataIndex: 'likes',
      key: 'likes',
      width: 80,
      sorter: (a: InteractionPost, b: InteractionPost) => a.likes - b.likes,
      render: (likes: number) => (
        <Space>
          <LikeOutlined style={{ color: '#52c41a' }} />
          <Text strong>{likes}</Text>
        </Space>
      ),
    },
    {
      title: '留言數',
      dataIndex: 'comments',
      key: 'comments',
      width: 80,
      sorter: (a: InteractionPost, b: InteractionPost) => a.comments - b.comments,
      render: (comments: number) => (
        <Space>
          <MessageOutlined style={{ color: '#722ed1' }} />
          <Text strong>{comments}</Text>
        </Space>
      ),
    },
    {
      title: '分享數',
      dataIndex: 'shares',
      key: 'shares',
      width: 80,
      sorter: (a: InteractionPost, b: InteractionPost) => a.shares - b.shares,
      render: (shares: number) => (
        <Space>
          <ShareAltOutlined style={{ color: '#fa8c16' }} />
          <Text strong>{shares}</Text>
        </Space>
      ),
    },
    {
      title: '收藏數',
      dataIndex: 'bookmarks',
      key: 'bookmarks',
      width: 80,
      sorter: (a: InteractionPost, b: InteractionPost) => a.bookmarks - b.bookmarks,
      render: (bookmarks: number) => (
        <Space>
          <Text strong>{bookmarks}</Text>
        </Space>
      ),
    },
    {
      title: '總互動數',
      dataIndex: 'total_interactions',
      key: 'total_interactions',
      width: 100,
      sorter: (a: InteractionPost, b: InteractionPost) => {
        const aTotal = (a.likes || 0) + (a.comments || 0) + (a.shares || 0) + (a.bookmarks || 0);
        const bTotal = (b.likes || 0) + (b.comments || 0) + (b.shares || 0) + (b.bookmarks || 0);
        return aTotal - bTotal;
      },
      render: (_, record: InteractionPost) => {
        const total = (record.likes || 0) + (record.comments || 0) + (record.shares || 0) + (record.bookmarks || 0);
        return (
          <Space>
            <BarChartOutlined style={{ color: '#722ed1' }} />
            <Text strong style={{ color: '#722ed1' }}>{total}</Text>
          </Space>
        );
      },
    },
    {
      title: '打賞數',
      dataIndex: 'donations',
      key: 'donations',
      width: 80,
      sorter: (a: InteractionPost, b: InteractionPost) => (a.donations || 0) - (b.donations || 0),
      render: (donations: number) => (
        <Space>
          <Text strong>{donations || 0}</Text>
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 80,
      render: (_, record: InteractionPost) => (
        <Space>
          <Tooltip title="查看原文">
            <Button
              type="link"
              icon={<LinkOutlined />}
              onClick={() => openExternalLink(record.article_url)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 初始數據加載 - 顯示數據庫中現有的數據
  useEffect(() => {
    console.log('📊 互動分析頁面載入完成，開始載入數據庫中現有的互動數據');
    console.log('🔍 準備調用 fetchInteractionAnalysis...');
    
    const loadData = async () => {
      try {
        console.log('🚀 開始執行 fetchInteractionAnalysis...');
        await fetchInteractionAnalysis();
        console.log('✅ fetchInteractionAnalysis 執行完成');
      } catch (error) {
        console.error('❌ fetchInteractionAnalysis 執行失敗:', error);
        // 顯示錯誤信息給用戶
        message.error('載入互動數據失敗，請檢查後端服務是否運行');
        // 設置空數據以避免頁面顯示異常
        setPosts([]);
        setOverallStats(null);
      }
    };
    
    loadData();
  }, []); // 只在組件掛載時執行一次

  // 監控 posts 狀態變化
  useEffect(() => {
    console.log('📊 posts 狀態更新:', posts.length, '篇貼文');
    if (posts.length > 0) {
      console.log('📊 前 3 篇貼文:', posts.slice(0, 3).map(p => ({ id: p.post_id, title: p.title, likes: p.likes })));
    }
  }, [posts]);

  // 篩選條件變化時重新加載數據
  useEffect(() => {
    if (selectedKOLs.length > 0 || dateRange !== null || includeExternal !== true) {
      fetchInteractionAnalysis();
    }
  }, [selectedKOLs, dateRange, includeExternal]);

  return (
    <div style={{ padding: '24px' }}>
      {/* 頁面標題 */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <BarChartOutlined style={{ marginRight: 8 }} />
          互動分析總覽
        </Title>
        <Text type="secondary">整合系統發文和外部數據的完整互動分析</Text>
      </div>


      {/* 總體統計 */}
      {overallStats && (
        <Card size="small" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="總貼文數"
                value={overallStats.total_posts}
                prefix={<BarChartOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="系統發文"
                value={overallStats.system_posts}
                valueStyle={{ color: '#52c41a' }}
                prefix={<UserOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="外部發文"
                value={overallStats.external_posts}
                valueStyle={{ color: '#fa8c16' }}
                prefix={<LinkOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="總互動數"
                value={overallStats.total_likes + overallStats.total_comments + overallStats.total_shares}
                prefix={<LikeOutlined />}
              />
            </Col>
          </Row>
          <Divider style={{ margin: '12px 0' }} />
          <Row gutter={16}>
            <Col span={8}>
              <Statistic
                title="總讚數"
                value={overallStats.total_likes}
                prefix={<LikeOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="總留言"
                value={overallStats.total_comments}
                prefix={<MessageOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="總分享"
                value={overallStats.total_shares}
                prefix={<ShareAltOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* 🔥 篩選區域 - 重新設計 */}
      <Card
        size="small"
        style={{ marginBottom: 24 }}
        title={
          <Space>
            <FilterOutlined />
            <span>篩選條件</span>
            <Tag color="blue">{getSortedAndFilteredPosts().length} 筆符合</Tag>
          </Space>
        }
        extra={
          <Space size="small">
            <Button
              icon={<ReloadOutlined spin={loading} />}
              onClick={fetchInteractionAnalysis}
              loading={loading}
              size="small"
            >
              刷新
            </Button>
          </Space>
        }
      >
        {/* 第一行：時間篩選 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={24}>
            <Space size="middle">
              <Text strong><CalendarOutlined /> 時間篩選：</Text>
              <Button
                type={timeQuickFilter === 'all' ? 'primary' : 'default'}
                size="small"
                onClick={() => handleTimeQuickFilter('all')}
              >
                全部
              </Button>
              <Button
                type={timeQuickFilter === 'today' ? 'primary' : 'default'}
                size="small"
                onClick={() => handleTimeQuickFilter('today')}
              >
                今日
              </Button>
              <Button
                type={timeQuickFilter === 'yesterday' ? 'primary' : 'default'}
                size="small"
                onClick={() => handleTimeQuickFilter('yesterday')}
              >
                昨日
              </Button>
              <Button
                type={timeQuickFilter === 'week' ? 'primary' : 'default'}
                size="small"
                onClick={() => handleTimeQuickFilter('week')}
              >
                近7天
              </Button>
              <Button
                type={timeQuickFilter === 'month' ? 'primary' : 'default'}
                size="small"
                onClick={() => handleTimeQuickFilter('month')}
              >
                近30天
              </Button>
              <Divider type="vertical" />
              <RangePicker
                placeholder={['開始日期', '結束日期']}
                value={dateRange ? [dateRange[0], dateRange[1]] : undefined}
                onChange={(dates, dateStrings) => {
                  // 使用 dateStrings 來重建 dayjs 物件，避免類型問題
                  if (dateStrings && dateStrings[0] && dateStrings[1]) {
                    setDateRange([dayjs(dateStrings[0]), dayjs(dateStrings[1])]);
                    setTimeQuickFilter('custom');
                  } else {
                    setDateRange(null);
                    setTimeQuickFilter('all');
                  }
                }}
                size="small"
                style={{ width: 240 }}
                allowClear
              />
            </Space>
          </Col>
        </Row>

        {/* 第二行：角色池 + 個股篩選 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text type="secondary"><UserOutlined /> 角色池篩選</Text>
              <Select
                mode="multiple"
                placeholder="選擇 KOL（可多選）"
                value={selectedKOLs}
                onChange={setSelectedKOLs}
                style={{ width: '100%' }}
                allowClear
                showSearch
                optionFilterProp="label"
                optionLabelProp="label"
                maxTagCount={2}
                maxTagPlaceholder={(omittedValues) => `+${omittedValues.length} 位`}
                options={uniqueKOLs.map(kol => ({
                  value: kol.serial,
                  label: kol.nickname
                }))}
              />
            </Space>
          </Col>
          <Col span={6}>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text type="secondary">📈 個股篩選</Text>
              <Select
                placeholder="選擇股票"
                value={selectedStock}
                onChange={setSelectedStock}
                style={{ width: '100%' }}
                allowClear
                showSearch
              >
                {uniqueStocks.map(stock => (
                  <Option key={stock} value={stock}>
                    {stock}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>
          <Col span={6}>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text type="secondary">🔍 關鍵字搜尋</Text>
              <Search
                placeholder="標題、內容、KOL"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                allowClear
                size="middle"
              />
            </Space>
          </Col>
          <Col span={6}>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text type="secondary">📊 排序方式</Text>
              <Space.Compact style={{ width: '100%' }}>
                <Select
                  value={sortField}
                  onChange={setSortField}
                  style={{ width: '60%' }}
                >
                  <Option value="total_interactions">總互動</Option>
                  <Option value="likes">讚數</Option>
                  <Option value="comments">留言</Option>
                  <Option value="shares">分享</Option>
                </Select>
                <Select
                  value={sortOrder}
                  onChange={setSortOrder}
                  style={{ width: '40%' }}
                >
                  <Option value="descend">↓降</Option>
                  <Option value="ascend">↑升</Option>
                </Select>
              </Space.Compact>
            </Space>
          </Col>
        </Row>

        {/* 第三行：快速操作按鈕 */}
        <Row>
          <Col span={24}>
            <Space wrap>
              <Button
                type={showTop30 ? "primary" : "default"}
                onClick={() => setShowTop30(!showTop30)}
                icon={<BarChartOutlined />}
                size="small"
              >
                {showTop30 ? "顯示全部" : "僅前30名"}
              </Button>
              <Button
                type={showFeatureAnalysis ? "primary" : "default"}
                onClick={() => setShowFeatureAnalysis(!showFeatureAnalysis)}
                icon={<BarChartOutlined />}
                size="small"
              >
                {showFeatureAnalysis ? "隱藏分析" : "特徵分析"}
              </Button>
              <Divider type="vertical" />
              <Button
                size="small"
                onClick={() => {
                  setSelectedKOLs([]);
                  setSelectedStock(undefined);
                  setDateRange(null);
                  setTimeQuickFilter('all');
                  setSearchKeyword('');
                }}
              >
                清除篩選
              </Button>
              <Button
                type="primary"
                icon={<ReloadOutlined spin={refreshing} />}
                onClick={refreshAllInteractions}
                loading={refreshing}
                size="small"
                style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
              >
                {selectedKOLs.length > 0
                  ? `刷新 ${selectedKOLs.length} 位 KOL`
                  : '刷新互動數據'}
              </Button>
              <Button
                icon={<ExportOutlined />}
                onClick={downloadCSV}
                size="small"
              >
                下載 CSV
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 🔥 選中 KOL 群體統計 */}
      {selectedKOLGroupStats && selectedKOLs.length > 0 && (
        <Card
          size="small"
          style={{ marginBottom: 24 }}
          title={
            <Space>
              <UserOutlined />
              <span>已選擇 {selectedKOLs.length} 位 KOL 群體統計</span>
              <Tag color="purple">{selectedKOLGroupStats.totalPosts} 篇貼文</Tag>
            </Space>
          }
        >
          {/* 群體總計 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={4}>
              <Statistic
                title="群體總貼文"
                value={selectedKOLGroupStats.totalPosts}
                prefix={<BarChartOutlined />}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="群體總讚數"
                value={selectedKOLGroupStats.totalLikes}
                prefix={<LikeOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="群體總留言"
                value={selectedKOLGroupStats.totalComments}
                prefix={<MessageOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="群體總分享"
                value={selectedKOLGroupStats.totalShares}
                prefix={<ShareAltOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="群體總互動"
                value={selectedKOLGroupStats.totalLikes + selectedKOLGroupStats.totalComments + selectedKOLGroupStats.totalShares}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="平均互動/篇"
                value={((selectedKOLGroupStats.totalLikes + selectedKOLGroupStats.totalComments + selectedKOLGroupStats.totalShares) / selectedKOLGroupStats.totalPosts).toFixed(1)}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#eb2f96' }}
              />
            </Col>
          </Row>

          {/* 各 KOL 詳細數據 */}
          <Divider style={{ margin: '12px 0' }} />
          <Text strong style={{ marginBottom: 8, display: 'block' }}>各 KOL 表現對比：</Text>
          <Row gutter={[12, 12]}>
            {selectedKOLGroupStats.kolDetails.map((kol, index) => (
              <Col span={selectedKOLs.length <= 3 ? 8 : selectedKOLs.length <= 4 ? 6 : 4} key={kol.serial}>
                <Card
                  size="small"
                  style={{
                    borderLeft: `3px solid ${index === 0 ? '#52c41a' : index === 1 ? '#1890ff' : '#d9d9d9'}`
                  }}
                >
                  <div style={{ marginBottom: 8 }}>
                    <Tag color={index === 0 ? 'gold' : index === 1 ? 'silver' : 'default'}>
                      #{index + 1}
                    </Tag>
                    <Text strong>{kol.nickname}</Text>
                  </div>
                  <Row gutter={4}>
                    <Col span={12}>
                      <Text type="secondary" style={{ fontSize: '11px' }}>貼文數</Text>
                      <div style={{ fontWeight: 'bold' }}>{kol.postCount}</div>
                    </Col>
                    <Col span={12}>
                      <Text type="secondary" style={{ fontSize: '11px' }}>平均互動</Text>
                      <div style={{ fontWeight: 'bold', color: '#1890ff' }}>{kol.avgInteractions.toFixed(1)}</div>
                    </Col>
                  </Row>
                  <Row gutter={4} style={{ marginTop: 4 }}>
                    <Col span={8}>
                      <Text type="secondary" style={{ fontSize: '10px' }}>讚</Text>
                      <div style={{ fontSize: '12px' }}>{kol.likes}</div>
                    </Col>
                    <Col span={8}>
                      <Text type="secondary" style={{ fontSize: '10px' }}>留言</Text>
                      <div style={{ fontSize: '12px' }}>{kol.comments}</div>
                    </Col>
                    <Col span={8}>
                      <Text type="secondary" style={{ fontSize: '10px' }}>分享</Text>
                      <div style={{ fontSize: '12px' }}>{kol.shares}</div>
                    </Col>
                  </Row>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 特徵分析區域 */}
      {showFeatureAnalysis && analysisData && (
        <Card 
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>📊 貼文特徵對比分析</span>
              <Button 
                type="primary" 
                icon={<BarChartOutlined />}
                onClick={generateSchedulingSuggestions}
                style={{ marginLeft: 16 }}
              >
                提取高互動特徵
              </Button>
            </div>
          } 
          style={{ marginBottom: 24 }}
        >
          <div>
                <Row gutter={[16, 16]}>
                  {/* 基本統計對比 */}
                  <Col span={24}>
                    <Card size="small" title="📈 基本統計對比">
                      <Row gutter={16}>
                        <Col span={6}>
                          <Statistic
                            title="總貼文數"
                            value={analysisData.totalPosts}
                            prefix={<BarChartOutlined />}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="前10%貼文數"
                            value={analysisData.top10PercentCount}
                            prefix={<BarChartOutlined />}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="前10%平均內容長度"
                            value={analysisData.top10Analysis.features.avgContentLength}
                            suffix="字"
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="所有貼文平均內容長度"
                            value={analysisData.allAnalysis.features.avgContentLength}
                            suffix="字"
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                          />
                        </Col>
                      </Row>
                      <Row gutter={16} style={{ marginTop: 16 }}>
                        <Col span={6}>
                          <Statistic
                            title="前10%平均股票標記數"
                            value={analysisData.top10Analysis.features.avgStockTagsPerPost.toFixed(1)}
                            suffix="個"
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="所有貼文平均股票標記數"
                            value={analysisData.allAnalysis.features.avgStockTagsPerPost.toFixed(1)}
                            suffix="個"
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="前10%系統發文比例"
                            value={analysisData.top10Analysis.features.sourceDistribution.system}
                            suffix="%"
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="所有貼文系統發文比例"
                            value={analysisData.allAnalysis.features.sourceDistribution.system}
                            suffix="%"
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                          />
                        </Col>
                      </Row>
                      <Row gutter={16} style={{ marginTop: 16 }}>
                        <Col span={6}>
                          <Statistic
                            title="前10%平均總互動數"
                            value={analysisData.top10Analysis.features.avgTotalInteractions.toFixed(0)}
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="所有貼文平均總互動數"
                            value={analysisData.allAnalysis.features.avgTotalInteractions.toFixed(0)}
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="前10%平均讚數"
                            value={analysisData.top10Analysis.features.avgLikes.toFixed(0)}
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="所有貼文平均讚數"
                            value={analysisData.allAnalysis.features.avgLikes.toFixed(0)}
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                          />
                        </Col>
                      </Row>
                      <Row gutter={16} style={{ marginTop: 16 }}>
                        <Col span={6}>
                          <Statistic
                            title="前10%平均留言數"
                            value={analysisData.top10Analysis.features.avgComments.toFixed(0)}
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="所有貼文平均留言數"
                            value={analysisData.allAnalysis.features.avgComments.toFixed(0)}
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="前10%平均分享數"
                            value={analysisData.top10Analysis.features.avgShares.toFixed(0)}
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                          />
                        </Col>
                        <Col span={6}>
                          <Statistic
                            title="所有貼文平均分享數"
                            value={analysisData.allAnalysis.features.avgShares.toFixed(0)}
                            prefix={<BarChartOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                          />
                        </Col>
                      </Row>
                    </Card>
                  </Col>

                  {/* 發文時間分析對比 */}
                  <Col span={12}>
                    <Card size="small" title="🕐 發文時間分布對比">
                      <Row gutter={8}>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.postingTime.morning}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 上午</div>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.postingTime.morning}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 上午</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.postingTime.afternoon}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 下午</div>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.postingTime.afternoon}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 下午</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.postingTime.evening}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 晚上</div>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.postingTime.evening}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 晚上</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.postingTime.night}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 深夜</div>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.postingTime.night}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 深夜</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </Col>

                  {/* 內容特徵分析對比 */}
                  <Col span={12}>
                    <Card size="small" title="📝 內容特徵分析對比">
                      <Row gutter={8}>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasStockTags}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 有股票標記</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasStockTags}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 有股票標記</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasTrendingTopic}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 熱門話題</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasTrendingTopic}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 熱門話題</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasHumorMode}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 幽默模式</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasHumorMode}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 幽默模式</div>
                          </div>
                        </Col>
                      </Row>
                      <Row gutter={8} style={{ marginTop: 16 }}>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasNewsLinks}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 有新聞連結</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasNewsLinks}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 有新聞連結</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.sourceDistribution.system}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 系統發文</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.sourceDistribution.system}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 系統發文</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.sourceDistribution.external}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 外部發文</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.sourceDistribution.external}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 外部發文</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </Col>

                  {/* 內容長度分析對比 */}
                  <Col span={12}>
                    <Card size="small" title="📏 內容長度分布對比">
                      <Row gutter={8}>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.shortContent}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 短內容</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.shortContent}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 短內容</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.mediumContent}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 中內容</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.mediumContent}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 中內容</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.longContent}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 長內容</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.longContent}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 長內容</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </Col>

                  {/* KOL分布對比 */}
                  <Col span={12}>
                    <Card size="small" title="👥 KOL分布對比">
                      <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                        {Object.entries(analysisData.top10Analysis.features.kolDistribution)
                          .sort(([,a], [,b]) => b - a)
                          .slice(0, 10)
                          .map(([kolName, count]) => {
                            const allCount = analysisData.allAnalysis.features.kolDistribution[kolName] || 0;
                            return (
                              <div key={kolName} style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between', 
                                padding: '4px 0',
                                borderBottom: '1px solid #f0f0f0'
                              }}>
                                <span style={{ fontSize: '12px' }}>{kolName}</span>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                  <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#1890ff' }}>
                                    前10%: {count}
                                  </span>
                                  <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#52c41a' }}>
                                    全部: {allCount}
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                      </div>
                    </Card>
                  </Col>
                </Row>

                {/* 詳細內容分析區域 */}
                <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
                  {/* 標題分析對比 */}
                  <Col span={12}>
                    <Card size="small" title="📝 標題分析對比">
                      <Row gutter={8}>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.avgTitleLength}
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 平均標題長度</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.avgTitleLength}
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 平均標題長度</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.shortTitle}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 短標題(&lt;20字)</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.shortTitle}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 短標題(&lt;20字)</div>
                          </div>
                        </Col>
                        <Col span={8}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.longTitle}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>前10% 長標題(&gt;40字)</div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.longTitle}%
                            </div>
                            <div style={{ fontSize: '10px', color: '#666' }}>全部 長標題(&gt;40字)</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </Col>

                  {/* 文章架構分析對比 */}
                  <Col span={12}>
                    <Card size="small" title="🏗️ 文章架構分析對比">
                      <Row gutter={8}>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasEmoji}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 有Emoji</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasEmoji}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 有Emoji</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasHashtag}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 有Hashtag</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasHashtag}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 有Hashtag</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasQuestion}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 有問號</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasQuestion}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 有問號</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasExclamation}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 有驚嘆號</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasExclamation}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 有驚嘆號</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </Col>

                  {/* 幽默型內容分析對比 */}
                  <Col span={12}>
                    <Card size="small" title="😄 幽默型內容分析對比">
                      <Row gutter={8}>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.humorType.none}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 無幽默</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.humorType.none}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 無幽默</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.humorType.light}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 輕度幽默</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.humorType.light}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 輕度幽默</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.humorType.moderate}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 中度幽默</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.humorType.moderate}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 中度幽默</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.humorType.strong}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 強烈幽默</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.humorType.strong}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 強烈幽默</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </Col>

                  {/* 內容結構分析對比 */}
                  <Col span={12}>
                    <Card size="small" title="📋 內容結構分析對比">
                      <Row gutter={8}>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasParagraphs}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 有段落</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasParagraphs}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 有段落</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasLineBreaks}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 有換行</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasLineBreaks}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 有換行</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasBulletPoints}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 有條列</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasBulletPoints}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 有條列</div>
                          </div>
                        </Col>
                        <Col span={6}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}>
                              {analysisData.top10Analysis.features.hasQuotes}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>前10% 有引用</div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#52c41a' }}>
                              {analysisData.allAnalysis.features.hasQuotes}%
                            </div>
                            <div style={{ fontSize: '9px', color: '#666' }}>全部 有引用</div>
                          </div>
                        </Col>
                      </Row>
                    </Card>
                  </Col>
                </Row>
          </div>
        </Card>
      )}

      {/* 排程建議區域 */}
      {showSchedulingSuggestions && (
        <Card title="🎯 高互動特徵排程建議" style={{ marginBottom: 24 }}>
          <Row gutter={[16, 16]}>
            {schedulingSuggestions.map((suggestion) => (
              <Col span={8} key={suggestion.id}>
                <Card 
                  size="small" 
                  style={{ 
                    border: `2px solid ${suggestion.color}`,
                    borderRadius: '8px'
                  }}
                >
                  <div style={{ marginBottom: 12 }}>
                    <Title level={4} style={{ color: suggestion.color, margin: 0 }}>
                      {suggestion.name}
                    </Title>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {suggestion.description}
                    </Text>
                  </div>
                  
                  <div style={{ marginBottom: 12 }}>
                    <Text strong style={{ fontSize: '13px' }}>建議設定：</Text>
                    <div style={{ marginTop: 8 }}>
                      <div style={{ marginBottom: 4 }}>
                        <Text style={{ fontSize: '12px' }}>
                          <CalendarOutlined style={{ marginRight: 4 }} />
                          發文時段: {suggestion.settings.preferredTimeSlots.join(', ')}
                        </Text>
                      </div>
                      <div style={{ marginBottom: 4 }}>
                        <Text style={{ fontSize: '12px' }}>
                          <BarChartOutlined style={{ marginRight: 4 }} />
                          內容長度: {suggestion.settings.contentLength}
                        </Text>
                      </div>
                      <div style={{ marginBottom: 4 }}>
                        <Text style={{ fontSize: '12px' }}>
                          <MessageOutlined style={{ marginRight: 4 }} />
                          幽默程度: {suggestion.settings.humorLevel}
                        </Text>
                      </div>
                      <div style={{ marginBottom: 4 }}>
                        <Text style={{ fontSize: '12px' }}>
                          <Tag style={{ marginRight: 4 }} />
                          股票標記: {suggestion.settings.stockTags}
                        </Text>
                      </div>
                      <div>
                        <Text style={{ fontSize: '12px' }}>
                          <FilterOutlined style={{ marginRight: 4 }} />
                          特徵: {suggestion.settings.features.join(', ')}
                        </Text>
                      </div>
                    </div>
                  </div>
                  
                  <div style={{ 
                    padding: '8px', 
                    backgroundColor: `${suggestion.color}15`, 
                    borderRadius: '4px',
                    textAlign: 'center'
                  }}>
                    <Text strong style={{ color: suggestion.color, fontSize: '13px' }}>
                      {suggestion.expectedEngagement}
                    </Text>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
          
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Button 
              type="default" 
              onClick={() => setShowSchedulingSuggestions(false)}
              style={{ marginRight: 8 }}
            >
              關閉建議
            </Button>
            <Button 
              type="primary" 
              onClick={generateSchedulingSuggestions}
              icon={<ReloadOutlined />}
            >
              重新生成建議
            </Button>
          </div>
        </Card>
      )}

      {/* 貼文列表 */}
      <Card title={`📋 貼文列表 (${getSortedAndFilteredPosts().length} 篇)`}>
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={getSortedAndFilteredPosts()}
            rowKey="post_id"
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `第 ${range[0]}-${range[1]} 條，共 ${total} 條`,
            }}
            scroll={{ x: 1200 }}
            size="small"
          />
        </Spin>
      </Card>
    </div>
  );
};

export default InteractionAnalysisPage;

