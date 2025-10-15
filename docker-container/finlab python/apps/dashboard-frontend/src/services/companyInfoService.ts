/**
 * 公司基本資料服務
 * 提供公司名稱搜尋、股票代號查詢等功能
 */
import api from './api';

export interface CompanyInfo {
  stock_code: string;
  company_short_name: string;
  company_full_name: string;
  industry_category: string;
  market_type?: string;
  listing_date?: string;
  capital?: number;
  ceo?: string;
  address?: string;
  phone?: string;
  website?: string;
}

export interface CompanyMapping {
  stock_code: string;
  company_name: string;
  industry: string;
  aliases: string[];
}

export interface CompanySearchResult {
  stock_code: string;
  company_name: string;
  industry: string;
  aliases: string[];
}

export interface CompanyStatistics {
  total_companies: number;
  total_mappings: number;
  industry_distribution: Record<string, number>;
  last_updated: string;
}

class CompanyInfoService {
  private baseUrl = '/api/company';

  /**
   * 獲取公司基本資料
   */
  async getCompanyBasicInfo(forceRefresh: boolean = false): Promise<CompanyInfo[]> {
    try {
      const response = await api.get(`${this.baseUrl}/basic-info`, {
        params: { force_refresh: forceRefresh }
      });
      
      if (response.data) {
        return response.data;
      }
      
      return [];
    } catch (error) {
      console.error('獲取公司基本資料失敗:', error);
      throw error;
    }
  }

  /**
   * 獲取公司名稱代號對應表
   */
  async getCompanyMapping(forceRefresh: boolean = false): Promise<Record<string, CompanyMapping>> {
    try {
      const response = await api.get(`${this.baseUrl}/mapping`, {
        params: { force_refresh: forceRefresh }
      });
      
      if (response.data) {
        return response.data;
      }
      
      return {};
    } catch (error) {
      console.error('獲取公司名稱代號對應表失敗:', error);
      throw error;
    }
  }

  /**
   * 根據公司名稱搜尋股票代號
   */
  async searchCompanyByName(name: string, fuzzy: boolean = true): Promise<CompanySearchResult[]> {
    try {
      const response = await api.get(`${this.baseUrl}/search`, {
        params: { 
          name: name,
          fuzzy: fuzzy
        }
      });
      
      if (response.data) {
        return response.data;
      }
      
      return [];
    } catch (error) {
      console.error('搜尋公司失敗:', error);
      throw error;
    }
  }

  /**
   * 根據股票代號獲取公司資訊
   */
  async getCompanyByCode(stockCode: string): Promise<CompanyMapping | null> {
    try {
      const response = await api.get(`${this.baseUrl}/code/${stockCode}`);
      
      if (response.data) {
        return response.data;
      }
      
      return null;
    } catch (error) {
      console.error('根據股票代號獲取公司資訊失敗:', error);
      return null;
    }
  }

  /**
   * 根據產業類別獲取公司列表
   */
  async getCompaniesByIndustry(industry: string): Promise<CompanySearchResult[]> {
    try {
      const response = await api.get(`${this.baseUrl}/industry/${industry}`);
      
      if (response.data) {
        return response.data;
      }
      
      return [];
    } catch (error) {
      console.error('根據產業獲取公司列表失敗:', error);
      throw error;
    }
  }

  /**
   * 獲取統計資訊
   */
  async getStatistics(): Promise<CompanyStatistics> {
    try {
      const response = await api.get(`${this.baseUrl}/statistics`);
      
      if (response.data) {
        return response.data;
      }
      
      return {
        total_companies: 0,
        total_mappings: 0,
        industry_distribution: {},
        last_updated: new Date().toISOString()
      };
    } catch (error) {
      console.error('獲取統計資訊失敗:', error);
      throw error;
    }
  }

  /**
   * 重新整理快取
   */
  async refreshCache(): Promise<{ success: boolean; message: string; companies_count: number; mapping_count: number }> {
    try {
      const response = await api.post(`${this.baseUrl}/refresh`);
      
      if (response.data) {
        return response.data;
      }
      
      throw new Error('重新整理快取失敗');
    } catch (error) {
      console.error('重新整理快取失敗:', error);
      throw error;
    }
  }

  /**
   * 智能搜尋公司（支援多種搜尋方式）
   */
  async smartSearch(query: string): Promise<CompanySearchResult[]> {
    try {
      // 先嘗試精確搜尋
      let results = await this.searchCompanyByName(query, false);
      
      // 如果精確搜尋沒有結果，嘗試模糊搜尋
      if (results.length === 0) {
        results = await this.searchCompanyByName(query, true);
      }
      
      // 如果還是沒有結果，嘗試搜尋股票代號
      if (results.length === 0 && /^\d{4,5}$/.test(query)) {
        const company = await this.getCompanyByCode(query);
        if (company) {
          results = [{
            stock_code: company.stock_code,
            company_name: company.company_name,
            industry: company.industry,
            aliases: company.aliases
          }];
        }
      }
      
      return results;
    } catch (error) {
      console.error('智能搜尋失敗:', error);
      return [];
    }
  }

  /**
   * 獲取熱門公司列表（基於搜尋頻率）
   */
  async getPopularCompanies(limit: number = 20): Promise<CompanySearchResult[]> {
    try {
      // 這裡可以實作基於搜尋頻率的熱門公司邏輯
      // 暫時返回一些常見的公司
      const popularStockCodes = [
        '2330', '2454', '2317', '2881', '2882', '1101', '1102', '1216', 
        '1303', '1326', '2002', '2308', '2377', '2382', '2408', '2474', 
        '2498', '3008', '3034', '3231'
      ];
      
      const results: CompanySearchResult[] = [];
      
      for (const code of popularStockCodes.slice(0, limit)) {
        const company = await this.getCompanyByCode(code);
        if (company) {
          results.push({
            stock_code: company.stock_code,
            company_name: company.company_name,
            industry: company.industry,
            aliases: company.aliases
          });
        }
      }
      
      return results;
    } catch (error) {
      console.error('獲取熱門公司列表失敗:', error);
      return [];
    }
  }
}

// 創建服務實例
const companyInfoService = new CompanyInfoService();

export default companyInfoService;
