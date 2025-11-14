// 貼文相關的類型定義

export interface Post {
  id: string;
  post_id: string;
  session_id: number;
  kol_serial: number;
  kol_nickname: string;
  kol_persona: string;
  stock_code: string;
  stock_name: string;
  title: string;
  content: string;
  content_md: string;
  status: string;
  quality_score?: number;
  ai_detection_score?: number;
  risk_level?: string;
  reviewer_notes?: string;
  approved_by?: string;
  approved_at?: string;
  scheduled_at?: string;
  published_at?: string;
  cmoney_post_id?: string;
  cmoney_post_url?: string;
  publish_error?: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  topic_id?: string;
  topic_title?: string;
  has_trending_topic?: boolean;
  topic_content?: string;
  created_at: string;
  updated_at: string;
  commodity_tags?: any[];
  stock_codes?: string[];
  stock_names?: string[];
}

export interface PostReviewPageProps {
  sessionId?: number;
  onBack?: () => void;
}

export interface PostEditFormData {
  edited_title: string;
  edited_content: string;
  reviewer_notes?: string;
  approved_by?: string;
}
