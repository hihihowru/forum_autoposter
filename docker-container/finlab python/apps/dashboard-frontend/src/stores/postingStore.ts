import { create } from 'zustand';

export interface GeneratedPost {
  id: number;
  title: string;
  content: string;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'published';
  kol_nickname: string;
  kol_serial: number;
  stock_codes: string[];
  stock_names: string[];
  created_at: string;
  updated_at: string;
  session_id: string;
  trigger_type: string;
  content_length: string;
  tags: string[];
  interactions: number;
}

interface PostingStore {
  // 生成的貼文列表
  generatedPosts: GeneratedPost[];
  
  // 添加新生成的貼文
  addGeneratedPosts: (posts: GeneratedPost[]) => void;
  
  // 更新貼文狀態
  updatePostStatus: (postId: number, status: GeneratedPost['status']) => void;
  
  // 更新貼文內容
  updatePostContent: (postId: number, title: string, content: string) => void;
  
  // 清空貼文列表
  clearPosts: () => void;
  
  // 獲取等待審核的貼文
  getPendingPosts: () => GeneratedPost[];
  
  // 獲取所有貼文
  getAllPosts: () => GeneratedPost[];
}

export const usePostingStore = create<PostingStore>((set, get) => ({
  generatedPosts: [],
  
  addGeneratedPosts: (posts: GeneratedPost[]) => {
    set((state) => ({
      generatedPosts: [...state.generatedPosts, ...posts]
    }));
  },
  
  updatePostStatus: (postId: number, status: GeneratedPost['status']) => {
    set((state) => ({
      generatedPosts: state.generatedPosts.map(post => 
        post.id === postId ? { ...post, status, updated_at: new Date().toLocaleString() } : post
      )
    }));
  },
  
  updatePostContent: (postId: number, title: string, content: string) => {
    set((state) => ({
      generatedPosts: state.generatedPosts.map(post => 
        post.id === postId ? { ...post, title, content, updated_at: new Date().toLocaleString() } : post
      )
    }));
  },
  
  clearPosts: () => {
    set({ generatedPosts: [] });
  },
  
  getPendingPosts: () => {
    return get().generatedPosts.filter(post => 
      post.status === 'draft' || post.status === 'pending'
    );
  },
  
  getAllPosts: () => {
    return get().generatedPosts;
  }
}));
