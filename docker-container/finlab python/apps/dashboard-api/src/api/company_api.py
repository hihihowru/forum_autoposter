"""
公司基本資料 API 端點
提供公司基本資訊、股票代號與公司名稱對應表的 HTTP API
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
import logging
from ..stock.company_info_service import (
    CompanyInfoService, 
    CompanyInfo, 
    CompanyMapping,
    get_company_info_service
)

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/company", tags=["company"])

@router.get("/basic-info", response_model=List[Dict[str, Any]])
async def get_company_basic_info(
    force_refresh: bool = Query(False, description="強制重新整理，忽略快取"),
    service: CompanyInfoService = Depends(get_company_info_service)
):
    """
    獲取公司基本資料
    
    Args:
        force_refresh: 強制重新整理，忽略快取
        
    Returns:
        公司基本資料列表
    """
    try:
        companies = await service.get_company_basic_info(force_refresh=force_refresh)
        
        return [
            {
                "stock_code": company.stock_code,
                "company_short_name": company.company_short_name,
                "company_full_name": company.company_full_name,
                "industry_category": company.industry_category,
                "market_type": company.market_type,
                "listing_date": company.listing_date,
                "capital": company.capital,
                "ceo": company.ceo,
                "address": company.address,
                "phone": company.phone,
                "website": company.website
            }
            for company in companies
        ]
        
    except Exception as e:
        logger.error(f"獲取公司基本資料失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取公司基本資料失敗: {str(e)}")

@router.get("/mapping", response_model=Dict[str, Dict[str, Any]])
async def get_company_mapping(
    force_refresh: bool = Query(False, description="強制重新整理，忽略快取"),
    service: CompanyInfoService = Depends(get_company_info_service)
):
    """
    獲取公司名稱代號對應表
    
    Args:
        force_refresh: 強制重新整理，忽略快取
        
    Returns:
        公司名稱代號對應字典
    """
    try:
        mapping = await service.get_company_mapping(force_refresh=force_refresh)
        
        return {
            code: {
                "stock_code": company.stock_code,
                "company_name": company.company_name,
                "industry": company.industry,
                "aliases": company.aliases or []
            }
            for code, company in mapping.items()
        }
        
    except Exception as e:
        logger.error(f"獲取公司名稱代號對應表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取公司名稱代號對應表失敗: {str(e)}")

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_company_by_name(
    name: str = Query(..., description="公司名稱"),
    fuzzy: bool = Query(True, description="是否使用模糊搜尋"),
    service: CompanyInfoService = Depends(get_company_info_service)
):
    """
    根據公司名稱搜尋股票代號
    
    Args:
        name: 公司名稱
        fuzzy: 是否使用模糊搜尋
        
    Returns:
        符合條件的公司對應列表
    """
    try:
        results = await service.search_company_by_name(name, fuzzy=fuzzy)
        
        return [
            {
                "stock_code": company.stock_code,
                "company_name": company.company_name,
                "industry": company.industry,
                "aliases": company.aliases or []
            }
            for company in results
        ]
        
    except Exception as e:
        logger.error(f"搜尋公司失敗: {e}")
        raise HTTPException(status_code=500, detail=f"搜尋公司失敗: {str(e)}")

@router.get("/code/{stock_code}", response_model=Dict[str, Any])
async def get_company_by_code(
    stock_code: str,
    service: CompanyInfoService = Depends(get_company_info_service)
):
    """
    根據股票代號獲取公司資訊
    
    Args:
        stock_code: 股票代號
        
    Returns:
        公司對應資訊
    """
    try:
        company = await service.get_company_by_code(stock_code)
        
        if not company:
            raise HTTPException(status_code=404, detail=f"找不到股票代號 {stock_code} 的公司資訊")
        
        return {
            "stock_code": company.stock_code,
            "company_name": company.company_name,
            "industry": company.industry,
            "aliases": company.aliases or []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"根據股票代號獲取公司資訊失敗: {e}")
        raise HTTPException(status_code=500, detail=f"根據股票代號獲取公司資訊失敗: {str(e)}")

@router.get("/industry/{industry}", response_model=List[Dict[str, Any]])
async def get_companies_by_industry(
    industry: str,
    service: CompanyInfoService = Depends(get_company_info_service)
):
    """
    根據產業類別獲取公司列表
    
    Args:
        industry: 產業類別
        
    Returns:
        符合條件的公司列表
    """
    try:
        companies = await service.get_companies_by_industry(industry)
        
        return [
            {
                "stock_code": company.stock_code,
                "company_name": company.company_name,
                "industry": company.industry,
                "aliases": company.aliases or []
            }
            for company in companies
        ]
        
    except Exception as e:
        logger.error(f"根據產業獲取公司列表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"根據產業獲取公司列表失敗: {str(e)}")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(
    service: CompanyInfoService = Depends(get_company_info_service)
):
    """
    獲取統計資訊
    
    Returns:
        統計資訊
    """
    try:
        stats = await service.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"獲取統計資訊失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取統計資訊失敗: {str(e)}")

@router.post("/refresh")
async def refresh_cache(
    service: CompanyInfoService = Depends(get_company_info_service)
):
    """
    重新整理快取
    
    Returns:
        重新整理結果
    """
    try:
        # 重新整理公司基本資料
        companies = await service.get_company_basic_info(force_refresh=True)
        
        # 重新整理對應表
        mapping = await service.get_company_mapping(force_refresh=True)
        
        return {
            "success": True,
            "message": "快取重新整理成功",
            "companies_count": len(companies),
            "mapping_count": len(mapping)
        }
        
    except Exception as e:
        logger.error(f"重新整理快取失敗: {e}")
        raise HTTPException(status_code=500, detail=f"重新整理快取失敗: {str(e)}")
