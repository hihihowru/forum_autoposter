// KOL 詳情頁面相關類型定義

export interface KOLInfo {
  serial: string;
  nickname: string;
  member_id: string;
  persona: string;
  status: string;
  owner: string;
  email: string;
  password: string;
  whitelist: boolean;
  notes: string;
  post_times: string;
  target_audience: string;
  interaction_threshold: number;
  content_types: string[];
  common_terms: string;
  colloquial_terms: string;
  tone_style: string;
  typing_habit: string;
  backstory: string;
  expertise: string;
  data_source: string;
  created_time: string;
  last_updated: string;
  prompt_persona: string;
  prompt_style: string;
  prompt_guardrails: string;
  prompt_skeleton: string;
  prompt_cta: string;
  prompt_hashtags: string;
  signature: string;
  emoji_pack: string;
  model_id: string;
  template_variant: string;
  model_temp: number;
  max_tokens: number;
  title_openers: string[];
  title_signature_patterns: string[];
  title_tail_word: string;
  title_banned_words: string[];
  title_style_examples: string[];
  title_retry_max: number;
  tone_formal: number;
  tone_emotion: number;
  tone_confidence: number;
  tone_urgency: number;
  tone_interaction: number;
  question_ratio: number;
  content_length: string;
  interaction_starters: string[];
  require_finlab_api: boolean;
  allow_hashtags: boolean;
  total_posts: number;
  published_posts: number;
  avg_interaction_rate: number;
  best_performing_post: string;
}

export interface KOLStatistics {
  total_posts: number;
  published_posts: number;
  draft_posts: number;
  avg_interaction_rate: number;
  best_performing_post: string;
  total_interactions: number;
  avg_likes_per_post: number;
  avg_comments_per_post: number;
  // 新增歷史趨勢數據
  trend_data: InteractionTrend[];
  monthly_stats: MonthlyStats[];
  weekly_stats: WeeklyStats[];
  daily_stats: DailyStats[];
}

export interface MonthlyStats {
  month: string;
  posts_count: number;
  total_interactions: number;
  avg_likes_per_post: number;
  avg_comments_per_post: number;
  engagement_rate: number;
}

export interface WeeklyStats {
  week: string;
  posts_count: number;
  total_interactions: number;
  avg_likes_per_post: number;
  avg_comments_per_post: number;
  engagement_rate: number;
}

export interface DailyStats {
  date: string;
  posts_count: number;
  total_interactions: number;
  avg_likes_per_post: number;
  avg_comments_per_post: number;
  engagement_rate: number;
}

export interface PostHistory {
  post_id: string;
  kol_serial: string;
  kol_nickname: string;
  kol_member_id: string;
  persona: string;
  content_type: string;
  topic_index: number;
  topic_id: string;
  topic_title: string;
  topic_keywords: string;
  content: string;
  status: string;
  scheduled_time: string;
  post_time: string;
  error_message: string;
  platform_post_id: string;
  platform_post_url: string;
  trending_topic_title: string;
  interactions: {
    '1hr': InteractionData;
    '1day': InteractionData;
    '7days': InteractionData;
  };
}

export interface InteractionData {
  likes_count: number;
  comments_count: number;
  total_interactions: number;
  engagement_rate: number;
  growth_rate: number;
}

export interface InteractionTrend {
  date: string;
  post_count: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  avg_likes: number;
  avg_comments: number;
  avg_shares: number;
}

export interface TopicPerformance {
  topic_id: string;
  topic_title: string;
  posts_count: number;
  avg_interaction_rate: number;
  total_interactions: number;
}

export interface KOLDetailResponse {
  timestamp: string;
  success: boolean;
  data: {
    kol_info: KOLInfo;
    statistics: KOLStatistics;
  };
}

export interface KOLPostsResponse {
  timestamp: string;
  success: boolean;
  data: {
    posts: PostHistory[];
    pagination: {
      current_page: number;
      page_size: number;
      total_pages: number;
      total_items: number;
    };
  };
}

export interface KOLInteractionsResponse {
  timestamp: string;
  success: boolean;
  data: {
    interaction_summary: KOLStatistics;
    interaction_trend: InteractionTrend[];
    performance_by_topic: TopicPerformance[];
  };
}

// 組件 Props 類型
export interface KOLDetailProps {
  memberId: string;
}

export interface KOLBasicInfoProps {
  kolInfo: KOLInfo;
  statistics: KOLStatistics;
  loading: boolean;
  error: string | null;
  isEditMode?: boolean;
  onKolInfoChange?: (field: keyof KOLInfo, value: any) => void;
}

export interface KOLSettingsProps {
  kolInfo: KOLInfo;
  loading: boolean;
  error: string | null;
  isEditMode?: boolean;
  onKolInfoChange?: (field: keyof KOLInfo, value: any) => void;
}

export interface PostHistoryProps {
  posts: PostHistory[];
  loading: boolean;
  error: string | null;
  pagination: {
    current_page: number;
    page_size: number;
    total_pages: number;
    total_items: number;
  };
  onPageChange: (page: number, pageSize: number) => void;
  onViewDetail: (postId: string) => void;
}

export interface InteractionChartProps {
  memberId: string;
  loading: boolean;
  error: string | null;
}
