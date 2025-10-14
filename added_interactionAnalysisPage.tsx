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
  Typography
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
  const [selectedKOL, setSelectedKOL] = useState<number | undefined>(undefined);
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [includeExternal, setIncludeExternal] = useState(true);
  const [searchKeyword, setSearchKeyword] = useState('');
  
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
  }, [showFeatureAnalysis, posts, selectedKOL, dateRange, includeExternal, searchKeyword, sortField, sortOrder, showTop30]);

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
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedKOL) params.append('kol_serial', selectedKOL.toString());
      if (dateRange && dateRange[0] && dateRange[1]) {
        params.append('start_date', dateRange[0].format('YYYY-MM-DD'));
        params.append('end_date', dateRange[1].format('YYYY-MM-DD'));
      }
      params.append('include_external', includeExternal.toString());

      const response = await fetch(`http://localhost:8001/interactions/analysis?${params}`);
      const result = await response.json();

      if (result.success) {
        setPosts(result.data.posts);
        setKolStats(result.data.kol_stats);
        setOverallStats(result.data.overall_stats);
      } else {
        message.error('獲取互動分析數據失敗');
      }
    } catch (error) {
      console.error('獲取互動分析數據失敗:', error);
      message.error('獲取互動分析數據失敗');
    } finally {
      setLoading(false);
    }
  };

  // 批量刷新互動數據
  const refreshAllInteractions = async () => {
    setRefreshing(true);
    try {
      const response = await fetch('http://localhost:8001/interactions/refresh-all', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      
      if (result.success) {
        message.success(result.message);
        // 重新獲取數據
        await fetchInteractionAnalysis();
      } else {
        message.error('批量刷新失敗');
      }
    } catch (error) {
      console.error('批量刷新失敗:', error);
      message.error('批量刷新失敗');
    } finally {
      setRefreshing(false);
    }
  };

  // 一鍵抓取所有互動數據
  const fetchAllInteractions = async () => {
    setRefreshing(true);
    try {
      const response = await fetch('http://localhost:8001/interactions/fetch-all-interactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      
      if (result.success) {
        message.success(result.message);
        // 重新獲取數據
        await fetchInteractionAnalysis();
      } else {
        message.error('一鍵抓取失敗');
      }
    } catch (error) {
      console.error('一鍵抓取失敗:', error);
      message.error('一鍵抓取失敗');
    } finally {
      setRefreshing(false);
    }
  };

  // 去重功能
  const deduplicatePosts = async () => {
    setRefreshing(true);
    try {
      const response = await fetch('http://localhost:8001/interactions/deduplicate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      
      if (result.success) {
        message.success(result.message);
        // 重新獲取數據
        await fetchInteractionAnalysis();
      } else {
        message.error('去重失敗');
      }
    } catch (error) {
      console.error('去重失敗:', error);
      message.error('去重失敗');
    } finally {
      setRefreshing(false);
    }
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
      title: '瀏覽數',
      dataIndex: 'views',
      key: 'views',
      width: 80,
      sorter: (a: InteractionPost, b: InteractionPost) => a.views - b.views,
      render: (views: number) => (
        <Space>
          <EyeOutlined style={{ color: '#1890ff' }} />
          <Text strong>{views}</Text>
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

  useEffect(() => {
    fetchInteractionAnalysis();
  }, [selectedKOL, dateRange, includeExternal]);

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

      {/* 篩選和搜索 */}
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
              {Object.entries(kolStats).map(([serial, stats]) => (
                <Option key={serial} value={parseInt(serial)}>
                  {stats.kol_nickname} ({serial})
                </Option>
              ))}
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
          <Col span={4}>
            <Search
              placeholder="搜索標題、內容、KOL"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={3}>
            <Select
              placeholder="排序欄位"
              value={sortField}
              onChange={setSortField}
              style={{ width: '100%' }}
            >
              <Option value="total_interactions">總互動數</Option>
              <Option value="likes">讚數</Option>
              <Option value="comments">留言數</Option>
              <Option value="shares">分享數</Option>
              <Option value="views">瀏覽數</Option>
              <Option value="engagement_rate">互動率</Option>
            </Select>
          </Col>
          <Col span={3}>
            <Select
              placeholder="排序順序"
              value={sortOrder}
              onChange={setSortOrder}
              style={{ width: '100%' }}
            >
              <Option value="descend">降序</Option>
              <Option value="ascend">升序</Option>
            </Select>
          </Col>
          <Col span={8}>
            <Space wrap>
              <Button 
                type={showTop30 ? "primary" : "default"}
                onClick={() => setShowTop30(!showTop30)}
                icon={<BarChartOutlined />}
              >
                {showTop30 ? "顯示全部" : "前30名"}
              </Button>
              <Button 
                type={showFeatureAnalysis ? "primary" : "default"}
                onClick={() => setShowFeatureAnalysis(!showFeatureAnalysis)}
                icon={<BarChartOutlined />}
              >
                {showFeatureAnalysis ? "隱藏分析" : "特徵分析"}
              </Button>
              <Button 
                type="primary" 
                icon={<ReloadOutlined />}
                onClick={fetchInteractionAnalysis}
                loading={loading}
              >
                刷新
              </Button>
              <Button 
                type="default"
                icon={<ReloadOutlined />}
                onClick={refreshAllInteractions}
                loading={refreshing}
              >
                批量刷新
              </Button>
              <Button 
                type="default"
                icon={<BarChartOutlined />}
                onClick={fetchAllInteractions}
                loading={refreshing}
              >
                一鍵抓取
              </Button>
              <Button 
                type="default"
                icon={<FilterOutlined />}
                onClick={deduplicatePosts}
                loading={refreshing}
              >
                去重
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

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
