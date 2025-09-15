/**
 * 發文管理API服務
 */

import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8001';
const POSTING_SERVICE_URL = 'http://localhost:8001'; // posting-service

// 創建axios實例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在這裡添加認證token
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 響應攔截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// ==================== 類型定義 ====================

export interface PostingTemplate {
  id: number;
  name: string;
  description?: string;
  trigger_type: string;
  data_sources: any;
  explainability_config: any;
  news_config: any;
  kol_config: any;
  generation_settings: any;
  tag_settings: any;
  batch_mode_config: any;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PostingSession {
  id: number;
  session_name: string;
  trigger_type: string;
  trigger_data: any;
  template_id?: number;
  config: any;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Post {
  id: string;
  session_id: number;
  title: string;
  content: string;
  status: string;
  kol_serial: number;
  kol_nickname: string;
  kol_persona?: string;
  stock_codes: string[];
  stock_names: string[];
  stock_data: any;
  generation_config: any;
  commodity_tags?: any[];
  prompt_template?: string;
  technical_indicators: string[];
  quality_score?: number;
  ai_detection_score?: number;
  risk_level?: string;
  reviewer_notes?: string;
  approved_by?: string;
  approved_at?: string;
  published_at?: string;
  cmoney_post_id?: string;
  cmoney_post_url?: string;
  publish_error?: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  created_at: string;
  updated_at: string;
}

export interface PromptTemplate {
  id: number;
  name: string;
  description?: string;
  data_source: string;
  template: string;
  variables: string[];
  technical_indicators: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface KOLProfile {
  id: number;
  serial: number;
  nickname: string;
  name?: string;
  persona?: string;
  style_preference?: string;
  expertise_areas?: string[];
  activity_level?: string;
  question_ratio?: number;
  content_length?: string;
  interaction_starters?: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface GeneratePostsRequest {
  session_id: number;
  max_posts?: number;
  force_regenerate?: boolean;
}

export interface GeneratePostsResponse {
  success: boolean;
  generated_count: number;
  failed_count: number;
  posts: Post[];
  errors: string[];
}

// ==================== API服務類 ====================

export class PostingManagementAPI {
  
  // ==================== 模板管理 ====================
  
  static async createTemplate(template: Partial<PostingTemplate>): Promise<PostingTemplate> {
    const response = await apiClient.post('/api/posting-management/templates', template);
    return response.data;
  }
  
  static async getTemplates(skip = 0, limit = 100): Promise<PostingTemplate[]> {
    const response = await apiClient.get('/api/posting-management/templates', {
      params: { skip, limit }
    });
    return response.data;
  }
  
  static async getTemplate(templateId: number): Promise<PostingTemplate> {
    const response = await apiClient.get(`/api/posting-management/templates/${templateId}`);
    return response.data;
  }
  
  static async updateTemplate(templateId: number, template: Partial<PostingTemplate>): Promise<PostingTemplate> {
    const response = await apiClient.put(`/api/posting-management/templates/${templateId}`, template);
    return response.data;
  }
  
  static async deleteTemplate(templateId: number): Promise<void> {
    await apiClient.delete(`/api/posting-management/templates/${templateId}`);
  }
  
  // ==================== 發文會話管理 ====================
  
  static async createSession(session: Partial<PostingSession>): Promise<PostingSession> {
    // 簡化實現：直接返回一個模擬的會話對象
    return {
      id: Date.now(),
      session_name: session.session_name || `批量發文_${new Date().toLocaleString()}`,
      trigger_type: session.trigger_type || 'custom_stocks',
      trigger_data: session.trigger_data || {},
      template_id: session.template_id,
      config: session.config || {},
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  }
  
  static async getSessions(skip = 0, limit = 100, status?: string): Promise<PostingSession[]> {
    const response = await apiClient.get('/api/posting-management/sessions', {
      params: { skip, limit, status }
    });
    return response.data;
  }
  
  static async getSession(sessionId: number): Promise<PostingSession> {
    const response = await apiClient.get(`/api/posting-management/sessions/${sessionId}`);
    return response.data;
  }
  
  // ==================== 發文生成 ====================
  
  static async generateBatchPosts(batchConfig: {
    session_id: number;
    posts: Array<{
      stock_code: string;
      stock_name: string;
      kol_serial: string;
      session_id: number;
    }>;
    batch_config: any;
    data_sources?: any;
    explainability_config?: any;
    news_config?: any;
    tags_config?: any;  // 新增：標籤配置
  }): Promise<GeneratePostsResponse> {
    try {
      console.log('🚀 開始批量生成貼文:', {
        session_id: batchConfig.session_id,
        posts_count: batchConfig.posts.length,
        batch_config: batchConfig.batch_config,
        data_sources: batchConfig.data_sources
      });
      
      const startTime = Date.now();
      const { session_id, posts, batch_config, data_sources, tags_config } = batchConfig;
      
      // 逐個生成貼文（而不是並行生成）
      const successful = [];
      const failed = [];
      
      for (let i = 0; i < posts.length; i++) {
        const post = posts[i];
        try {
          console.log(`🚀 開始生成貼文 ${i + 1}/${posts.length} ${post.stock_code}-${post.kol_serial}:`, {
            url: `${POSTING_SERVICE_URL}/post/manual`,
            payload: {
              stock_code: post.stock_code,
              stock_name: post.stock_name,
              kol_serial: String(post.kol_serial),
              kol_persona: batch_config.kol_persona || 'technical',
              content_style: batch_config.content_style || 'chart_analysis',
              target_audience: batch_config.target_audience || 'active_traders',
              auto_post: batch_config.batch_type === 'auto_publish',
              post_to_thread: null,
              batch_mode: true,
              session_id: session_id,
              content_length: batchConfig.settings?.content_length || 'medium',
              max_words: batchConfig.settings?.max_words || 1000,
              data_sources: data_sources || {},
              explainability_config: batchConfig.explainability_config || {},
              news_config: batchConfig.news_config || {}
            }
          });
          
          // 添加調試信息
          console.log('🔍 前端 API 調試 - 傳遞的參數:');
          console.log('  - tags_config:', tags_config);
          console.log('  - topic_tags:', tags_config?.topic_tags);
          console.log('  - mixed_mode:', tags_config?.topic_tags?.mixed_mode);
          console.log('  - topic_id:', post.topic_id || batch_config.topic_id);
          console.log('  - topic_title:', post.topic_title || batch_config.topic_title);
          
          const startTime = Date.now();
          // 調用單個貼文生成 API
          const response = await axios.post(`${POSTING_SERVICE_URL}/post/manual`, {
            stock_code: post.stock_code,
            stock_name: post.stock_name,
            kol_serial: String(post.kol_serial),
            kol_persona: batch_config.kol_persona || 'technical',
            content_style: batch_config.content_style || 'chart_analysis',
            target_audience: batch_config.target_audience || 'active_traders',
            auto_post: batch_config.batch_type === 'auto_publish',
            post_to_thread: null,
            batch_mode: true,
            session_id: session_id,
            content_length: batchConfig.settings?.content_length || 'medium',
            max_words: batchConfig.settings?.max_words || 200,
            data_sources: data_sources || {},
            explainability_config: batchConfig.explainability_config || {},
            news_config: batchConfig.news_config || {},
            tags_config: tags_config || {},  // 新增：標籤配置
            topic_id: post.topic_id || batch_config.topic_id || null,  // 優先使用貼文級別的 topic_id
            topic_title: post.topic_title || batch_config.topic_title || null  // 優先使用貼文級別的 topic_title
          });
          
          const endTime = Date.now();
          console.log(`✅ 貼文生成完成 ${i + 1}/${posts.length} ${post.stock_code}-${post.kol_serial}:`, {
            duration: `${endTime - startTime}ms`,
            success: response.data.success,
            post_id: response.data.post_id
          });

          const postData = {
            id: Date.now() + i,
            session_id: session_id,
            title: response.data.content?.title || `${post.stock_name}(${post.stock_code}) 分析`,
            content: response.data.content?.content_md || response.data.content?.content || '內容生成中...',
            status: batch_config.batch_type === 'test_mode' ? 'test_mode' : 
                   batch_config.batch_type === 'review_mode' ? 'pending_review' : 'published',
            kol_serial: parseInt(post.kol_serial),
            kol_nickname: `KOL-${post.kol_serial}`,
            kol_persona: batch_config.kol_persona || 'technical',
            stock_codes: [post.stock_code],
            stock_names: [post.stock_name],
            stock_data: { [post.stock_code]: { name: post.stock_name } },
            generation_config: batch_config,
            technical_indicators: [],
            quality_score: 0.8,
            ai_detection_score: 0.1,
            risk_level: 'low',
            reviewer_notes: '',
            approved_by: undefined,
            views: 0,
            likes: 0,
            comments: 0,
            shares: 0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };
          
          successful.push(postData);
          
          // 每生成一篇貼文就通知一次（用於實時更新）
          console.log(`📝 貼文 ${i + 1}/${posts.length} 已生成，審核頁面將自動刷新`);
          
        } catch (error: any) {
          console.error(`❌ 生成貼文失敗 ${i + 1}/${posts.length} ${post.stock_code}-${post.kol_serial}:`, {
            error: error.message,
            response: error.response?.data
          });
          failed.push(`貼文 ${i + 1} 生成失敗: ${error.response?.data?.detail || error.message}`);
        }
      }
      
      console.log('📊 批量生成結果:', {
        total: posts.length,
        successful: successful.length,
        failed: failed.length,
        errors: failed,
        duration: `${Date.now() - startTime}ms`
      });
      
      return {
        success: true,
        generated_count: successful.length,
        failed_count: failed.length,
        posts: successful,
        errors: failed
      };
      
    } catch (error: any) {
      console.error('❌ 批量生成失敗:', error);
      return {
        success: false,
        generated_count: 0,
        failed_count: batchConfig.posts.length,
        posts: [],
        errors: [error.response?.data?.detail || error.message]
      };
    }
  }
  
  /**
   * 批量生成貼文 - 使用Server-Sent Events一則一則接收
   */
  static async generateBatchPostsStream(
    request: any,
    onProgress: (data: any) => void,
    onPostGenerated: (post: Post) => void,
    onComplete: (result: any) => void,
    onError: (error: any) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${POSTING_SERVICE_URL}/post/batch-generate-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 保留最後一行（可能不完整）

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'batch_start':
                  onProgress({ type: 'start', total: data.total, session_id: data.session_id });
                  break;
                  
                case 'progress':
                  onProgress({ 
                    type: 'progress', 
                    current: data.current, 
                    total: data.total, 
                    percentage: data.percentage,
                    successful: data.successful,
                    failed: data.failed
                  });
                  break;
                  
                case 'post_generated':
                  if (data.success && data.content) {
                    const post: Post = {
                      id: Date.now() + Math.random(),
                      session_id: request.session_id,
                      title: data.content.title || `${data.content.stock_name}分析`,
                      content: data.content.content_md || data.content.content || '內容生成中...',
                      status: 'pending_review',
                      kol_serial: parseInt(data.content.kol_serial),
                      kol_nickname: `KOL-${data.content.kol_serial}`,
                      kol_persona: data.content.kol_persona || 'technical',
                      stock_codes: [data.content.stock_code],
                      stock_names: [data.content.stock_name],
                      stock_data: { [data.content.stock_code]: { name: data.content.stock_name } },
                      generation_config: request.batch_config,
                      technical_indicators: [],
                      quality_score: 0.8,
                      ai_detection_score: 0.1,
                      risk_level: 'low',
                      reviewer_notes: '',
                      approved_by: undefined,
                      views: 0,
                      likes: 0,
                      comments: 0,
                      shares: 0,
                      created_at: new Date().toISOString(),
                      updated_at: new Date().toISOString()
                    };
                    onPostGenerated(post);
                  }
                  break;
                  
                case 'post_error':
                  console.error('貼文生成錯誤:', data.error);
                  break;
                  
                case 'batch_complete':
                  onComplete({
                    total: data.total,
                    successful: data.successful,
                    failed: data.failed,
                    session_id: data.session_id
                  });
                  break;
              }
            } catch (parseError) {
              console.error('解析SSE數據失敗:', parseError, '原始數據:', line);
            }
          }
        }
      }
    } catch (error) {
      console.error('SSE連接失敗:', error);
      onError(error);
    }
  }
  
  static async generatePosts(sessionId: number, config?: any): Promise<GeneratePostsResponse> {
    try {
      // 使用現有的手動發文API
      const response = await axios.post(`${POSTING_SERVICE_URL}/post/manual`, {
        kol_persona: config?.kol?.persona || 'technical',
        content_style: config?.settings?.content_style || 'chart_analysis',
        target_audience: config?.settings?.target_audience || 'active_traders',
        auto_post: false, // 不自動發文，先審核
        post_to_thread: null,
        content_length: config?.settings?.content_length || 'medium',
        max_words: config?.settings?.max_words || 1000
      });

      // 轉換為前端期望的格式
      const kolContent = response.data;
      return {
        success: true,
        generated_count: 1,
        failed_count: 0,
        posts: [{
          id: Date.now(),
          session_id: sessionId,
          title: kolContent.title,
          content: kolContent.content_md,
          status: 'pending_review',
          kol_serial: kolContent.kol_id,
          kol_nickname: kolContent.kol_name,
          kol_persona: config?.kol?.persona || 'technical',
          stock_codes: [kolContent.stock_id],
          stock_names: [kolContent.stock_id],
          stock_data: {},
          generation_config: config,
          technical_indicators: [],
          quality_score: kolContent.engagement_prediction || 0.8,
          ai_detection_score: 0.1,
          risk_level: 'low',
          views: 0,
          likes: 0,
          comments: 0,
          shares: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }],
        errors: []
      };
    } catch (error) {
      console.error('生成發文失敗:', error);
      throw error;
    }
  }
  
  static async getSessionPosts(
    sessionId: number, 
    skip = 0, 
    limit = 100, 
    status?: string
  ): Promise<{ success: boolean; posts: Post[]; count: number; session_id: number; timestamp: string }> {
    // 使用新的posting-service API
    const response = await axios.get(`${POSTING_SERVICE_URL}/posts/session/${sessionId}`, {
      params: { status }
    });
    
    // 轉換後端數據格式為前端期望的格式
    console.log('🔍 後端響應數據:', response.data);
    const posts = (response.data.posts || []).map((post: any) => ({
      id: post.post_id, // 直接使用UUID作為ID
      session_id: post.session_id,
      title: post.title,
      content: post.content,
      status: post.status,
      kol_serial: post.kol_serial,
      kol_nickname: post.kol_nickname,
      kol_persona: post.kol_persona,
      stock_codes: [post.stock_code], // 轉換為數組
      stock_names: [post.stock_name], // 轉換為數組
      stock_data: null,
      generation_config: post.generation_params,
      commodity_tags: post.commodity_tags || [],
      prompt_template: undefined,
      technical_indicators: post.generation_params?.technical_indicators || [],
      quality_score: post.quality_score,
      ai_detection_score: post.ai_detection_score,
      risk_level: post.risk_level,
      reviewer_notes: post.reviewer_notes,
      approved_by: post.approved_by,
      approved_at: post.approved_at,
      published_at: post.published_at,
      cmoney_post_id: post.cmoney_post_id,
      cmoney_post_url: post.cmoney_post_url,
      publish_error: post.publish_error,
      views: post.views || 0,
      likes: post.likes || 0,
      comments: post.comments || 0,
      shares: post.shares || 0,
      created_at: post.created_at,
      updated_at: post.updated_at
    }));
    
    return {
      success: response.data.success,
      posts,
      count: response.data.count,
      session_id: response.data.session_id,
      timestamp: response.data.timestamp
    };
  }
  
  // ==================== 發文管理 ====================
  
  static async getPosts(
    skip = 0, 
    limit = 100, 
    status?: string
  ): Promise<{posts: Post[], total: number, skip: number, limit: number}> {
    try {
      // 從 posting-service 獲取所有貼文（不限制於pending-review）
      const response = await axios.get(`${POSTING_SERVICE_URL}/posts`, {
        params: { skip, limit, status }
      });
      
      console.log('✅ 從posting-service獲取貼文:', response.data);
      
      // 轉換後端數據格式為前端期望的格式
      const posts = (response.data.posts || []).map((post: any) => ({
        id: post.post_id, // 使用 post_id 作為 id
        session_id: post.session_id,
        title: post.title,
        content: post.content,
        status: post.status,
        kol_serial: post.kol_serial,
        kol_nickname: post.kol_nickname,
        kol_persona: post.kol_persona,
        stock_codes: [post.stock_code], // 轉換為數組
        stock_names: [post.stock_name], // 轉換為數組
        stock_data: null,
        generation_config: post.generation_params,
        commodity_tags: post.commodity_tags || [],
        prompt_template: undefined,
        technical_indicators: post.generation_params?.technical_indicators || [],
        quality_score: post.quality_score,
        ai_detection_score: post.ai_detection_score,
        risk_level: post.risk_level,
        reviewer_notes: post.reviewer_notes,
        approved_by: post.approved_by,
        approved_at: post.approved_at,
        published_at: post.published_at,
        cmoney_post_id: post.cmoney_post_id,
        cmoney_post_url: post.cmoney_post_url,
        publish_error: post.publish_error,
        views: post.views || 0,
        likes: post.likes || 0,
        comments: post.comments || 0,
        shares: post.shares || 0,
        created_at: post.created_at,
        updated_at: post.updated_at
      }));
      
      return {
        posts,
        total: response.data.count || 0,
        skip,
        limit
      };
    } catch (error) {
      console.error('從 posting-service 獲取數據失敗:', error);
      
      // 備用方案：從 dashboard-api 獲取數據
      try {
        const dashboardResponse = await axios.get(`${API_BASE_URL}/api/dashboard/content-management`);
        const postList = dashboardResponse.data.post_list || [];
        
        // 轉換為 Post 格式
        const posts: Post[] = postList.map((item: any, index: number) => ({
          id: index + 1,
          session_id: Date.now(),
          title: item.topic_title || `貼文 ${index + 1}`,
          content: item.content || '內容載入中...',
          status: item.status === '已發布' ? 'published' : 
                 item.status === '待發布' ? 'pending_review' : 'draft',
          kol_serial: parseInt(item.kol_serial) || 0,
          kol_nickname: item.kol_nickname || '未知KOL',
          kol_persona: item.persona || 'technical',
          stock_codes: item.topic_id ? [item.topic_id] : [],
          stock_names: item.topic_title ? [item.topic_title] : [],
          stock_data: {},
          generation_config: {},
          technical_indicators: [],
          quality_score: 0.8,
          ai_detection_score: 0.1,
          risk_level: 'low',
          views: 0,
          likes: 0,
          comments: 0,
          shares: 0,
          created_at: item.post_time || new Date().toISOString(),
          updated_at: item.post_time || new Date().toISOString()
        }));
        
        return {
          posts: posts,
          total: posts.length,
          skip,
          limit
        };
      } catch (dashboardError) {
        console.error('從 dashboard-api 獲取數據也失敗:', dashboardError);
        throw new Error('無法獲取貼文數據');
      }
    }
  }
  
  /**
   * 獲取發文審核 sidebar 數據
   */
  static async getReviewSidebarData(): Promise<{
    success: boolean;
    stats: {
      total_pending: number;
      sessions_count: number;
      latest_session: number | null;
      oldest_pending: string | null;
    };
    sidebar_data: {
      sessions: Array<{
        session_id: number;
        posts_count: number;
        latest_post: string;
        kol_personas: string[];
        stock_codes: string[];
        posts: Post[];
      }>;
    };
    timestamp: string;
  }> {
    try {
      const response = await axios.get(`${POSTING_SERVICE_URL}/posts/review-sidebar`);
      return response.data;
    } catch (error) {
      console.error('獲取審核 sidebar 數據失敗:', error);
      throw error;
    }
  }
  
  /**
   * 獲取貼文的自我學習數據
   */
  static async getPostSelfLearningData(postId: string): Promise<{
    success: boolean;
    self_learning_data: any;
    reconstruction_ready: boolean;
    timestamp: string;
  }> {
    try {
      const response = await axios.get(`${POSTING_SERVICE_URL}/posts/${postId}/self-learning-data`);
      return response.data;
    } catch (error) {
      console.error('獲取自我學習數據失敗:', error);
      throw error;
    }
  }
  
  /**
   * 獲取歷史生成資料統計
   */
  static async getHistoryStats(): Promise<{
    success: boolean;
    total_posts: number;
    status_stats: Record<string, number>;
    session_stats: Record<string, any>;
    kol_stats: Record<string, any>;
    stock_stats: Record<string, any>;
    learning_data_stats: {
      total_posts: number;
      with_generation_params: number;
      with_technical_analysis: number;
      with_serper_data: number;
      with_quality_scores: number;
      reconstruction_ready: number;
    };
    timestamp: string;
  }> {
    try {
      const response = await axios.get(`${POSTING_SERVICE_URL}/posts/history-stats`);
      return response.data;
    } catch (error) {
      console.error('獲取歷史統計失敗:', error);
      throw error;
    }
  }
  
  static async getPost(postId: string): Promise<Post> {
    const response = await axios.get(`${POSTING_SERVICE_URL}/posts/${postId}`);
    return response.data.post;
  }
  
  static async updatePost(postId: string, post: Partial<Post>): Promise<Post> {
    // 暫時使用現有API，後續可以擴展
    const response = await apiClient.put(`/api/posting-management/posts/${postId}`, post);
    return response.data;
  }
  
  static async approvePost(postId: string, reviewerNotes?: string, approvedBy = 'system', editedTitle?: string, editedContent?: string): Promise<void> {
    await axios.post(`${POSTING_SERVICE_URL}/posts/${postId}/approve`, {
      reviewer_notes: reviewerNotes,
      approved_by: approvedBy,
      edited_title: editedTitle,
      edited_content: editedContent
    });
  }
  
  static async rejectPost(postId: string, reviewerNotes: string): Promise<void> {
    await axios.post(`${POSTING_SERVICE_URL}/posts/${postId}/reject`, {
      reviewer_notes: reviewerNotes
    });
  }
  
  static async publishPost(postId: string): Promise<any> {
    // 使用正確的 posting-service API 端點
    const response = await axios.post(`${POSTING_SERVICE_URL}/posts/${postId}/publish`);
    return response.data;
  }

  /**
   * 發布貼文到CMoney
   */
  static async publishToCMoney(postId: string, cmoneyConfig?: any): Promise<{success: boolean, article_id?: string, article_url?: string, error?: string}> {
    try {
      const response = await axios.post(`${POSTING_SERVICE_URL}/posts/${postId}/publish`, cmoneyConfig);
      return response.data;
    } catch (error: any) {
      console.error('發布到CMoney失敗:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || '發布失敗'
      };
    }
  }

  static async deleteFromCMoney(postId: string): Promise<{success: boolean, error?: string}> {
    try {
      const response = await axios.delete(`${POSTING_SERVICE_URL}/posts/${postId}/delete`);
      return response.data;
    } catch (error: any) {
      console.error('從CMoney刪除失敗:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || '刪除失敗'
      };
    }
  }

  /**
   * 刪除貼文（軟刪除或硬刪除）
   */
  static async deletePost(postId: string): Promise<{success: boolean, error?: string}> {
    try {
      const response = await axios.delete(`${POSTING_SERVICE_URL}/posts/${postId}`);
      return response.data;
    } catch (error: any) {
      console.error('刪除貼文失敗:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || '刪除失敗'
      };
    }
  }

  /**
   * 還原已刪除的貼文
   */
  static async restorePost(postId: string): Promise<{success: boolean, error?: string}> {
    try {
      const response = await axios.post(`${POSTING_SERVICE_URL}/posts/${postId}/restore`);
      return response.data;
    } catch (error: any) {
      console.error('還原貼文失敗:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || '還原失敗'
      };
    }
  }
  
  // ==================== Prompt模板管理 ====================
  
  static async createPromptTemplate(template: Partial<PromptTemplate>): Promise<PromptTemplate> {
    const response = await apiClient.post('/api/posting-management/prompt-templates', template);
    return response.data;
  }
  
  static async getPromptTemplates(dataSource?: string): Promise<PromptTemplate[]> {
    const response = await apiClient.get('/api/posting-management/prompt-templates', {
      params: { data_source: dataSource }
    });
    return response.data;
  }
  
  // ==================== KOL管理 ====================
  
  static async getKOLs(): Promise<KOLProfile[]> {
    const response = await apiClient.get('/api/posting-management/kols');
    return response.data;
  }
  
  // ==================== 觸發器數據 ====================
  
  static async getAfterHoursLimitUpStocks(triggerConfig: any): Promise<any> {
    try {
      // 準備查詢參數 - 移除限制，使用篩選機制
      const params: any = {
        limit: triggerConfig.threshold || 1000  // 設為大數值以獲取所有符合條件的股票
      };
      
      // 如果有漲跌幅設定，添加到參數中
      if (triggerConfig.changeThreshold) {
        params.changeThreshold = triggerConfig.changeThreshold.percentage || 9.5;
      }
      
      // 如果有產業類別設定，添加到參數中
      if (triggerConfig.selectedIndustries && triggerConfig.selectedIndustries.length > 0) {
        params.industries = triggerConfig.selectedIndustries.join(',');
      }
      
      // 調用 ohlc-api 獲取盤後漲停股票數據
      const response = await axios.get('http://localhost:8005/after_hours_limit_up', {
        params,
        timeout: 30000,  // 添加超時設置
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (response.data && response.data.success) {
        // 如果 API 成功，直接返回結果（不管有沒有股票）
        return {
          success: true,
          total_count: response.data.total_count,
          stocks: response.data.stocks || [],
          timestamp: response.data.timestamp,
          source: 'ohlc-api',
          date: response.data.date,
          changeThreshold: response.data.changeThreshold,
          note: response.data.total_count === 0 ? `沒有找到漲幅超過 ${response.data.changeThreshold || 9.5}% 的股票` : undefined
        };
      } else {
        throw new Error('API 返回數據格式不正確');
      }
    } catch (error) {
      console.error('API 調用失敗，使用備用數據:', error);
      
      // 備用模擬數據
      const mockStocks = [
        { stock_code: "2330", stock_name: "台積電", change_percent: 10.0, volume: 45000000, close_price: 550.0 },
        { stock_code: "2454", stock_name: "聯發科", change_percent: 10.0, volume: 32000000, close_price: 880.0 },
        { stock_code: "2317", stock_name: "鴻海", change_percent: 10.0, volume: 28000000, close_price: 110.0 },
        { stock_code: "2881", stock_name: "富邦金", change_percent: 10.0, volume: 15000000, close_price: 66.0 },
        { stock_code: "2886", stock_name: "兆豐金", change_percent: 10.0, volume: 12000000, close_price: 33.0 }
      ];
      
      return {
        success: true,
        total_count: mockStocks.length,
        stocks: mockStocks,
        timestamp: new Date().toISOString(),
        source: 'fallback'
      };
    }
  }

  // 輔助函數：根據股票代號獲取股票名稱
  private static getStockName(stockCode: string): string {
    const stockNames: Record<string, string> = {
      "2330": "台積電",
      "2454": "聯發科",
      "2317": "鴻海",
      "2881": "富邦金",
      "2882": "國泰金",
      "1101": "台泥",
      "1102": "亞泥",
      "1216": "統一",
      "1303": "南亞",
      "1326": "台化",
      "2002": "中鋼",
      "2308": "台達電",
      "2377": "微星",
      "2382": "廣達",
      "2408": "南亞科",
      "2474": "可成",
      "2498": "宏達電",
      "3008": "大立光",
      "3034": "聯詠",
      "3231": "緯創",
      "3711": "日月光投控",
      "4938": "和碩",
      "6505": "台塑化",
      "8046": "南電",
      "9910": "豐泰",
      "2412": "中華電",
      "1301": "台塑",
      "2603": "長榮"
    };
    return stockNames[stockCode] || `股票${stockCode}`;
  }
  
  // ==================== 分析數據 ====================
  
  static async getPostAnalytics(postId: number, days = 7): Promise<any[]> {
    const response = await apiClient.get(`/api/posting-management/analytics/posts/${postId}`, {
      params: { days }
    });
    return response.data;
  }
  
  static async getAnalyticsSummary(days = 30): Promise<any> {
    const response = await apiClient.get('/api/posting-management/analytics/summary', {
      params: { days }
    });
    return response.data;
  }
}

// ==================== 工具函數 ====================

export const PostingAPIUtils = {
  
  // 格式化日期
  formatDate: (dateString: string): string => {
    return new Date(dateString).toLocaleString('zh-TW');
  },
  
  // 獲取狀態顏色
  getStatusColor: (status: string): string => {
    const statusColors: Record<string, string> = {
      draft: 'default',
      pending_review: 'warning',
      approved: 'success',
      published: 'blue',
      rejected: 'error',
      failed: 'error',
      deleted: 'red'
    };
    return statusColors[status] || 'default';
  },
  
  // 獲取狀態文字
  getStatusText: (status: string): string => {
    const statusTexts: Record<string, string> = {
      draft: '草稿',
      pending_review: '待審核',
      approved: '已審核',
      published: '已發布',
      rejected: '已拒絕',
      failed: '發布失敗',
      deleted: '已刪除'
    };
    return statusTexts[status] || status;
  },
  
  // 計算互動率
  calculateEngagementRate: (views: number, likes: number, comments: number, shares: number): number => {
    if (views === 0) return 0;
    return ((likes + comments + shares) / views) * 100;
  },
  
  // 格式化數字
  formatNumber: (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  },

  // 獲取所有產業類別
  async getAllIndustries(): Promise<any> {
    try {
      const response = await axios.get('http://localhost:8005/industries', {
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error('獲取產業類別失敗:', error);
      throw error;
    }
  },

  // 根據產業類別獲取股票列表
  async getStocksByIndustry(industries: string[], limit: number = 1000): Promise<any> {
    try {
      const params: any = {
        limit
      };
      
      if (industries && industries.length > 0) {
        params.industries = industries.join(',');
      }
      
      const response = await axios.get('http://localhost:8005/stocks_by_industry', {
        params,
        timeout: 30000
      });
      return response.data;
    } catch (error) {
      console.error('根據產業獲取股票失敗:', error);
      throw error;
    }
  }
};

export default PostingManagementAPI;
