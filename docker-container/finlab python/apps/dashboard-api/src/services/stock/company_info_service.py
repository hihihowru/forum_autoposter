"""
公司基本資料服務
負責獲取公司基本資訊、股票代號與公司名稱對應表
"""
import logging
import httpx
import asyncio
import pandas as pd
import finlab
import os
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

# 載入環境變數
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class CompanyInfo:
    """公司基本資訊"""
    stock_code: str
    company_short_name: str
    company_full_name: str
    industry_category: str
    market_type: Optional[str] = None
    listing_date: Optional[str] = None
    capital: Optional[float] = None
    ceo: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

@dataclass
class CompanyMapping:
    """公司名稱代號對應"""
    stock_code: str
    company_name: str
    industry: str
    aliases: List[str] = None  # 別名列表

class CompanyInfoService:
    """公司基本資料服務"""
    
    def __init__(self, 
                 finlab_api_key: Optional[str] = None,
                 cache_dir: str = "./cache"):
        """
        初始化公司基本資料服務
        
        Args:
            finlab_api_key: FinLab API 金鑰
            cache_dir: 快取目錄
        """
        self.finlab_api_key = finlab_api_key or os.getenv('FINLAB_API_KEY')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 快取檔案路徑
        self.company_info_cache_file = self.cache_dir / "company_basic_info.json"
        self.company_mapping_cache_file = self.cache_dir / "company_mapping.json"
        
        # 快取過期時間（24小時）
        self.cache_expiry_hours = 24
        
        # 初始化 FinLab
        self._finlab_logged_in = False
        if self.finlab_api_key:
            self._ensure_finlab_login()
        
        logger.info("公司基本資料服務初始化完成")
    
    def _ensure_finlab_login(self):
        """確保 FinLab API 已登入"""
        if not self._finlab_logged_in and self.finlab_api_key:
            try:
                finlab.login(self.finlab_api_key)
                self._finlab_logged_in = True
                logger.info("FinLab API 登入成功")
            except Exception as e:
                logger.warning(f"FinLab API 登入失敗: {e}")
                self._finlab_logged_in = False
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """檢查快取是否有效"""
        if not cache_file.exists():
            return False
        
        # 檢查檔案修改時間
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        expiry_time = datetime.now() - timedelta(hours=self.cache_expiry_hours)
        
        return file_time > expiry_time
    
    async def _load_from_cache(self, cache_file: Path) -> Optional[Dict[str, Any]]:
        """從快取載入資料"""
        try:
            if self._is_cache_valid(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"從快取載入資料: {cache_file.name}")
                return data
        except Exception as e:
            logger.warning(f"載入快取失敗: {e}")
        
        return None
    
    def _save_to_cache(self, data: Dict[str, Any], cache_file: Path):
        """儲存資料到快取"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"資料已儲存到快取: {cache_file.name}")
        except Exception as e:
            logger.error(f"儲存快取失敗: {e}")
    
    async def get_company_basic_info(self, force_refresh: bool = False) -> List[CompanyInfo]:
        """
        獲取公司基本資料
        
        Args:
            force_refresh: 強制重新整理，忽略快取
            
        Returns:
            公司基本資料列表
        """
        try:
            # 檢查快取
            if not force_refresh:
                cached_data = await self._load_from_cache(self.company_info_cache_file)
                if cached_data:
                    return [CompanyInfo(**item) for item in cached_data.get('companies', [])]
            
            logger.info("開始從 FinLab API 獲取公司基本資料")
            
            if not self._finlab_logged_in:
                raise Exception("FinLab API 未登入")
            
            # 從 FinLab 獲取 company_basic_info 資料
            company_data = finlab.data.get('company_basic_info')
            
            if company_data is None or company_data.empty:
                logger.warning("FinLab API 未返回公司資料")
                return []
            
            # 轉換為 CompanyInfo 物件
            companies = []
            for _, row in company_data.iterrows():
                try:
                    company = CompanyInfo(
                        stock_code=str(row.get('stock_id', '')),
                        company_short_name=str(row.get('company_short_name', '')),
                        company_full_name=str(row.get('company_full_name', '')),
                        industry_category=str(row.get('industry_category', '')),
                        market_type=str(row.get('market_type', '')) if pd.notna(row.get('market_type')) else None,
                        listing_date=str(row.get('listing_date', '')) if pd.notna(row.get('listing_date')) else None,
                        capital=float(row.get('capital', 0)) if pd.notna(row.get('capital')) else None,
                        ceo=str(row.get('ceo', '')) if pd.notna(row.get('ceo')) else None,
                        address=str(row.get('address', '')) if pd.notna(row.get('address')) else None,
                        phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                        website=str(row.get('website', '')) if pd.notna(row.get('website')) else None
                    )
                    companies.append(company)
                except Exception as e:
                    logger.warning(f"解析公司資料失敗: {e}")
                    continue
            
            # 儲存到快取
            cache_data = {
                'companies': [company.__dict__ for company in companies],
                'total_count': len(companies),
                'last_updated': datetime.now().isoformat()
            }
            self._save_to_cache(cache_data, self.company_info_cache_file)
            
            logger.info(f"成功獲取 {len(companies)} 家公司基本資料")
            return companies
            
        except Exception as e:
            logger.error(f"獲取公司基本資料失敗: {e}")
            return []
    
    async def get_company_mapping(self, force_refresh: bool = False) -> Dict[str, CompanyMapping]:
        """
        獲取公司名稱代號對應表
        
        Args:
            force_refresh: 強制重新整理，忽略快取
            
        Returns:
            公司名稱代號對應字典
        """
        try:
            # 檢查快取
            if not force_refresh:
                cached_data = await self._load_from_cache(self.company_mapping_cache_file)
                if cached_data:
                    return {
                        code: CompanyMapping(**data) 
                        for code, data in cached_data.get('mapping', {}).items()
                    }
            
            logger.info("開始建立公司名稱代號對應表")
            
            # 獲取公司基本資料
            companies = await self.get_company_basic_info(force_refresh)
            
            if not companies:
                logger.warning("無法獲取公司基本資料")
                return {}
            
            # 建立對應表
            mapping = {}
            for company in companies:
                # 主要對應
                mapping[company.stock_code] = CompanyMapping(
                    stock_code=company.stock_code,
                    company_name=company.company_short_name,
                    industry=company.industry_category,
                    aliases=[company.company_full_name]
                )
                
                # 建立反向對應（公司名稱 -> 股票代號）
                # 這裡可以添加更多別名邏輯
                aliases = [
                    company.company_short_name,
                    company.company_full_name
                ]
                
                # 添加常見別名
                if company.company_short_name in ['台積電', 'TSMC']:
                    aliases.extend(['台積', 'TSM'])
                elif company.company_short_name in ['聯發科', 'MediaTek']:
                    aliases.extend(['聯發', 'MTK'])
                elif company.company_short_name in ['鴻海', 'Foxconn']:
                    aliases.extend(['鴻海精密', '富士康'])
                
                mapping[company.stock_code].aliases = aliases
            
            # 儲存到快取
            cache_data = {
                'mapping': {code: mapping.__dict__ for code, mapping in mapping.items()},
                'total_count': len(mapping),
                'last_updated': datetime.now().isoformat()
            }
            self._save_to_cache(cache_data, self.company_mapping_cache_file)
            
            logger.info(f"成功建立 {len(mapping)} 個公司名稱代號對應")
            return mapping
            
        except Exception as e:
            logger.error(f"建立公司名稱代號對應表失敗: {e}")
            return {}
    
    async def search_company_by_name(self, company_name: str, fuzzy: bool = True) -> List[CompanyMapping]:
        """
        根據公司名稱搜尋股票代號
        
        Args:
            company_name: 公司名稱
            fuzzy: 是否使用模糊搜尋
            
        Returns:
            符合條件的公司對應列表
        """
        try:
            mapping = await self.get_company_mapping()
            
            if not mapping:
                return []
            
            results = []
            company_name_lower = company_name.lower()
            
            for code, company in mapping.items():
                # 精確匹配
                if company_name_lower in company.company_name.lower():
                    results.append(company)
                    continue
                
                # 模糊搜尋
                if fuzzy:
                    # 檢查別名
                    for alias in company.aliases or []:
                        if company_name_lower in alias.lower():
                            results.append(company)
                            break
                    
                    # 檢查部分匹配
                    if any(company_name_lower in alias.lower() for alias in company.aliases or []):
                        results.append(company)
            
            logger.info(f"搜尋 '{company_name}' 找到 {len(results)} 個結果")
            return results
            
        except Exception as e:
            logger.error(f"搜尋公司失敗: {e}")
            return []
    
    async def get_company_by_code(self, stock_code: str) -> Optional[CompanyMapping]:
        """
        根據股票代號獲取公司資訊
        
        Args:
            stock_code: 股票代號
            
        Returns:
            公司對應資訊
        """
        try:
            mapping = await self.get_company_mapping()
            return mapping.get(stock_code)
            
        except Exception as e:
            logger.error(f"根據股票代號獲取公司資訊失敗: {e}")
            return None
    
    async def get_companies_by_industry(self, industry: str) -> List[CompanyMapping]:
        """
        根據產業類別獲取公司列表
        
        Args:
            industry: 產業類別
            
        Returns:
            符合條件的公司列表
        """
        try:
            mapping = await self.get_company_mapping()
            
            if not mapping:
                return []
            
            results = []
            industry_lower = industry.lower()
            
            for company in mapping.values():
                if industry_lower in company.industry.lower():
                    results.append(company)
            
            logger.info(f"產業 '{industry}' 找到 {len(results)} 家公司")
            return results
            
        except Exception as e:
            logger.error(f"根據產業獲取公司列表失敗: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        獲取統計資訊
        
        Returns:
            統計資訊
        """
        try:
            companies = await self.get_company_basic_info()
            mapping = await self.get_company_mapping()
            
            # 統計各產業公司數量
            industry_stats = {}
            for company in companies:
                industry = company.industry_category
                industry_stats[industry] = industry_stats.get(industry, 0) + 1
            
            return {
                'total_companies': len(companies),
                'total_mappings': len(mapping),
                'industry_distribution': industry_stats,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"獲取統計資訊失敗: {e}")
            return {}

# 創建服務實例的工廠函數
def create_company_info_service(finlab_api_key: Optional[str] = None) -> CompanyInfoService:
    """創建公司基本資料服務實例"""
    return CompanyInfoService(finlab_api_key=finlab_api_key)

# 全域服務實例
_company_info_service: Optional[CompanyInfoService] = None

def get_company_info_service() -> CompanyInfoService:
    """獲取全域公司基本資料服務實例"""
    global _company_info_service
    if _company_info_service is None:
        _company_info_service = create_company_info_service()
    return _company_info_service
