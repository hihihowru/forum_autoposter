import axios from 'axios';

// 使用環境變數或默認 Railway URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://forumautoposter-production.up.railway.app';
const POSTING_SERVICE_URL = `${API_BASE_URL}/api`;
const DASHBOARD_API_URL = `${API_BASE_URL}/api/dashboard`;

export interface KOLProfile {
  serial: number;
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
}

class KOLService {
  /**
   * 從後端API獲取KOL列表
   */
  async getKOLs(): Promise<KOLProfile[]> {
    try {
      console.log('KOLService.getKOLs() 被調用');
      
      // 嘗試從 posting-service 獲取 KOL 數據
      const response = await axios.get(`${POSTING_SERVICE_URL}/kol/list`);
      
      if (response.data && Array.isArray(response.data)) {
        console.log('從後端API獲取到KOL數據:', response.data.length, '個KOL');
        
        // 轉換為前端期望的格式
        const kols = response.data.map((kol: any) => ({
          serial: kol.serial,
          nickname: kol.nickname || `KOL-${kol.serial}`,
          member_id: kol.serial.toString(),
          persona: kol.persona || "綜合派",
          status: kol.status || "active",
          owner: kol.owner || "",
          email: kol.email || "",
          password: "",
          whitelist: true,
          notes: kol.notes || "",
          post_times: "9:00-17:00",
          target_audience: "active_traders",
          interaction_threshold: 0.5,
          content_types: ["analysis"],
          common_terms: "",
          colloquial_terms: "",
          tone_style: "professional"
        }));
        
        console.log('轉換後的KOL列表:', kols.length, '個KOL');
        return kols;
      } else {
        console.warn('後端API返回的數據格式不正確:', response.data);
        return this.getFallbackKOLs();
      }
    } catch (error) {
      console.error('調用後端KOL API失敗:', error);
      console.log('使用備用KOL數據');
      return this.getFallbackKOLs();
    }
  }

  /**
   * 獲取備用KOL數據 - 包含所有 KOL (150, 186-198, 200-210)
   */
  private getFallbackKOLs(): KOLProfile[] {
    const knownKOLs = [
      // 150 KOL
      { serial: 150, member_id: "150", nickname: "隔日沖獵人", persona: "短線派" },
      
      // 186-198 KOL
      { serial: 186, member_id: "186", nickname: "KOL-186", persona: "技術派" },
      { serial: 187, member_id: "187", nickname: "KOL-187", persona: "總經派" },
      { serial: 188, member_id: "188", nickname: "KOL-188", persona: "消息派" },
      { serial: 189, member_id: "189", nickname: "KOL-189", persona: "散戶派" },
      { serial: 190, member_id: "190", nickname: "KOL-190", persona: "地方派" },
      { serial: 191, member_id: "191", nickname: "KOL-191", persona: "八卦派" },
      { serial: 192, member_id: "192", nickname: "KOL-192", persona: "爆料派" },
      { serial: 193, member_id: "193", nickname: "KOL-193", persona: "技術派" },
      { serial: 194, member_id: "194", nickname: "KOL-194", persona: "價值派" },
      { serial: 195, member_id: "195", nickname: "KOL-195", persona: "新聞派" },
      { serial: 196, member_id: "196", nickname: "KOL-196", persona: "數據派" },
      { serial: 197, member_id: "197", nickname: "KOL-197", persona: "短線派" },
      { serial: 198, member_id: "198", nickname: "KOL-198", persona: "綜合派" },
      
      // 200-210 KOL
      { serial: 200, member_id: "200", nickname: "川川哥", persona: "技術派" },
      { serial: 201, member_id: "201", nickname: "韭割哥", persona: "總經派" },
      { serial: 202, member_id: "202", nickname: "梅川褲子", persona: "消息派" },
      { serial: 203, member_id: "203", nickname: "龜狗一日散戶", persona: "散戶派" },
      { serial: 204, member_id: "204", nickname: "板橋大who", persona: "地方派" },
      { serial: 205, member_id: "205", nickname: "八卦護城河", persona: "八卦派" },
      { serial: 206, member_id: "206", nickname: "小道爆料王", persona: "爆料派" },
      { serial: 207, member_id: "207", nickname: "信號宅神", persona: "技術派" },
      { serial: 208, member_id: "208", nickname: "長線韭韭", persona: "價值派" },
      { serial: 209, member_id: "209", nickname: "報爆哥_209", persona: "新聞派" },
      { serial: 210, member_id: "210", nickname: "數據獵人", persona: "數據派" }
    ];

    console.log('使用備用KOL列表:', knownKOLs.length, '個KOL');

    // 轉換為KOLProfile格式
    return knownKOLs.map(kol => ({
      serial: kol.serial,
      nickname: kol.nickname,
      member_id: kol.member_id,
      persona: kol.persona,
      status: "active",
      owner: "",
      email: "",
      password: "",
      whitelist: true,
      notes: "",
      post_times: "9:00-17:00",
      target_audience: "active_traders",
      interaction_threshold: 0.5,
      content_types: ["analysis"],
      common_terms: "",
      colloquial_terms: "",
      tone_style: "professional"
    }));
  }

  /**
   * 根據序號獲取特定KOL
   */
  async getKOLBySerial(serial: number): Promise<KOLProfile | null> {
    try {
      const response = await axios.get(`${DASHBOARD_API_URL}/kols/${serial}`);
      return response.data;
    } catch (error) {
      console.error(`獲取KOL ${serial} 失敗:`, error);
      return null;
    }
  }

  /**
   * 獲取活躍的KOL列表 (別名方法)
   */
  async getActiveKOLs(): Promise<KOLProfile[]> {
    return this.getKOLs();
  }

  /**
   * 根據人設獲取KOL列表
   */
  async getKOLsByPersona(persona: string): Promise<KOLProfile[]> {
    try {
      const response = await axios.get(`${DASHBOARD_API_URL}/kols?persona=${persona}`);
      return response.data;
    } catch (error) {
      console.error(`獲取人設 ${persona} 的KOL失敗:`, error);
      return [];
    }
  }
}

export default new KOLService();
