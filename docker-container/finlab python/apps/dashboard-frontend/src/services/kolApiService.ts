import axios from 'axios';

// KOL API 服務 - 使用 PostgreSQL 數據庫
class KOLApiService {
  private baseURL = `${import.meta.env.VITE_API_BASE_URL || 'https://forumautoposter-production.up.railway.app'}/api/kol`;
  
  /**
   * 根據 member_id 獲取 KOL 詳情
   */
  async getKOLByMemberId(memberId: string) {
    try {
      // 首先獲取 KOL 列表，找到對應的 serial
      const listResponse = await axios.get(`${this.baseURL}/list`);
      const kols = listResponse.data.data || [];
      
      // 根據 member_id 找到對應的 KOL
      const kol = kols.find((k: any) => k.member_id === memberId);
      if (!kol) {
        throw new Error(`找不到 member_id 為 ${memberId} 的 KOL`);
      }
      
      // 獲取完整的 KOL 詳情
      const detailResponse = await axios.get(`${this.baseURL}/${kol.serial}`);
      return detailResponse.data;
    } catch (error) {
      console.error('獲取 KOL 詳情失敗:', error);
      throw error;
    }
  }
  
  /**
   * 根據 serial 獲取 KOL 詳情
   */
  async getKOLBySerial(serial: string) {
    try {
      const response = await axios.get(`${this.baseURL}/${serial}`);
      return response.data;
    } catch (error) {
      console.error('獲取 KOL 詳情失敗:', error);
      throw error;
    }
  }
  
  /**
   * 獲取所有 KOL 列表
   */
  async getKOLList() {
    try {
      const response = await axios.get(`${this.baseURL}/list`);
      return response.data.data || [];
    } catch (error) {
      console.error('獲取 KOL 列表失敗:', error);
      throw error;
    }
  }
  
  /**
   * 更新 KOL 設定
   */
  async updateKOL(serial: string, data: any) {
    try {
      const response = await axios.put(`${this.baseURL}/${serial}`, data);
      return response.data;
    } catch (error) {
      console.error('更新 KOL 設定失敗:', error);
      throw error;
    }
  }
}

export const kolApiService = new KOLApiService();
export default kolApiService;
