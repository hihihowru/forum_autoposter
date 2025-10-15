"""
KOL角色管理API
處理KOL人設、Prompt設定和批量更新
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from clients.google.sheets_client import GoogleSheetsClient, get_sheets_client

logger = logging.getLogger(__name__)

router = APIRouter()

# 數據模型
class KOLUpdateRequest(BaseModel):
    """KOL更新請求"""
    serial: Optional[str] = None
    nickname: Optional[str] = None
    persona: Optional[str] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    interaction_threshold: Optional[float] = None
    common_terms: Optional[str] = None
    colloquial_terms: Optional[str] = None
    tone_style: Optional[str] = None
    prompt_persona: Optional[str] = None
    prompt_style: Optional[str] = None
    prompt_guardrails: Optional[str] = None
    prompt_skeleton: Optional[str] = None
    prompt_cta: Optional[str] = None
    prompt_hashtags: Optional[str] = None
    signature: Optional[str] = None
    emoji_pack: Optional[str] = None
    model_id: Optional[str] = None
    model_temp: Optional[float] = None
    max_tokens: Optional[int] = None

class BatchUpdateRequest(BaseModel):
    """批量更新請求"""
    selected_kols: List[str]  # member_id列表
    update_fields: Dict[str, Any]  # 要更新的欄位

class KOLUpdateResponse(BaseModel):
    """KOL更新響應"""
    success: bool
    message: str
    updated_count: int = 0
    failed_count: int = 0
    errors: List[str] = []

class KOLRoleManager:
    """KOL角色管理器"""
    
    def __init__(self, sheets_client: GoogleSheetsClient):
        self.sheets_client = sheets_client
        self.sheet_name = '同學會帳號管理'
        
        # 欄位映射
        self.field_mapping = {
            'serial': 0,
            'nickname': 1,
            'owner': 2,
            'persona': 3,
            'member_id': 4,
            'email': 6,
            'password': 7,
            'whitelist': 8,
            'notes': 9,
            'content_types': 10,
            'post_times': 11,
            'target_audience': 12,
            'interaction_threshold': 13,
            'common_terms': 14,
            'colloquial_terms': 15,
            'tone_style': 16,
            'typing_habit': 17,
            'backstory': 18,
            'expertise': 19,
            'data_source': 20,
            'prompt_persona': 21,
            'prompt_style': 22,
            'prompt_guardrails': 23,
            'prompt_skeleton': 24,
            'prompt_cta': 25,
            'prompt_hashtags': 26,
            'signature': 27,
            'emoji_pack': 28,
            'model_id': 29,
            'model_temp': 30,
            'max_tokens': 31
        }
    
    def get_kol_by_member_id(self, member_id: str) -> Optional[Dict[str, Any]]:
        """根據member_id獲取KOL資訊"""
        try:
            data = self.sheets_client.read_sheet(self.sheet_name, 'A:AZ')
            if len(data) < 2:
                return None
            
            headers = data[0]
            for row in data[1:]:
                if len(row) > 4 and row[4] == member_id:
                    return self._row_to_dict(row, headers)
            return None
        except Exception as e:
            logger.error(f"獲取KOL資訊失敗: {e}")
            return None
    
    def update_kol(self, member_id: str, update_data: KOLUpdateRequest) -> bool:
        """更新單個KOL"""
        try:
            # 獲取當前數據
            data = self.sheets_client.read_sheet(self.sheet_name, 'A:AZ')
            if len(data) < 2:
                return False
            
            headers = data[0]
            updated = False
            
            # 找到對應的行並更新
            for i, row in enumerate(data[1:], start=2):  # 從第2行開始（第1行是標題）
                if len(row) > 4 and row[4] == member_id:
                    # 更新欄位
                    for field, value in update_data.dict(exclude_unset=True).items():
                        if field in self.field_mapping:
                            col_index = self.field_mapping[field]
                            # 確保行有足夠的列
                            while len(row) <= col_index:
                                row.append('')
                            row[col_index] = str(value) if value is not None else ''
                    
                    # 寫回Google Sheets
                    range_name = f'{self.sheet_name}!A{i}:AZ{i}'
                    self.sheets_client.write_sheet(self.sheet_name, [row], range_name)
                    updated = True
                    break
            
            return updated
        except Exception as e:
            logger.error(f"更新KOL失敗: {e}")
            return False
    
    def batch_update_kols(self, member_ids: List[str], update_fields: Dict[str, Any]) -> KOLUpdateResponse:
        """批量更新KOL"""
        success_count = 0
        failed_count = 0
        errors = []
        
        for member_id in member_ids:
            try:
                # 創建更新請求
                update_request = KOLUpdateRequest(**update_fields)
                
                # 執行更新
                if self.update_kol(member_id, update_request):
                    success_count += 1
                    logger.info(f"KOL {member_id} 更新成功")
                else:
                    failed_count += 1
                    errors.append(f"KOL {member_id} 更新失敗")
                    
            except Exception as e:
                failed_count += 1
                error_msg = f"KOL {member_id} 更新異常: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return KOLUpdateResponse(
            success=failed_count == 0,
            message=f"批量更新完成: 成功 {success_count} 個，失敗 {failed_count} 個",
            updated_count=success_count,
            failed_count=failed_count,
            errors=errors
        )
    
    def copy_kol_settings(self, source_member_id: str, target_member_id: str, 
                         fields_to_copy: List[str]) -> bool:
        """複製KOL設定"""
        try:
            # 獲取源KOL設定
            source_kol = self.get_kol_by_member_id(source_member_id)
            if not source_kol:
                return False
            
            # 準備複製的欄位
            copy_data = {}
            for field in fields_to_copy:
                if field in source_kol:
                    copy_data[field] = source_kol[field]
            
            # 更新目標KOL
            update_request = KOLUpdateRequest(**copy_data)
            return self.update_kol(target_member_id, update_request)
            
        except Exception as e:
            logger.error(f"複製KOL設定失敗: {e}")
            return False
    
    def _row_to_dict(self, row: List[str], headers: List[str]) -> Dict[str, Any]:
        """將行數據轉換為字典"""
        result = {}
        for i, header in enumerate(headers):
            if i < len(row):
                result[header] = row[i]
            else:
                result[header] = ''
        return result

# API端點
@router.put("/api/dashboard/kols/{member_id}")
async def update_kol(
    member_id: str,
    update_request: KOLUpdateRequest,
    sheets_client: GoogleSheetsClient = Depends(get_sheets_client)
):
    """更新單個KOL設定"""
    try:
        manager = KOLRoleManager(sheets_client)
        
        # 檢查KOL是否存在
        kol_info = manager.get_kol_by_member_id(member_id)
        if not kol_info:
            raise HTTPException(status_code=404, detail="KOL不存在")
        
        # 執行更新
        success = manager.update_kol(member_id, update_request)
        
        if success:
            return {
                "success": True,
                "message": "KOL設定已更新",
                "member_id": member_id,
                "updated_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="更新失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新KOL失敗: {e}")
        raise HTTPException(status_code=500, detail=f"更新失敗: {str(e)}")

@router.post("/api/dashboard/kols/batch-update")
async def batch_update_kols(
    request: BatchUpdateRequest,
    sheets_client: GoogleSheetsClient = Depends(get_sheets_client)
):
    """批量更新KOL設定"""
    try:
        manager = KOLRoleManager(sheets_client)
        
        # 執行批量更新
        result = manager.batch_update_kols(
            request.selected_kols,
            request.update_fields
        )
        
        return result
        
    except Exception as e:
        logger.error(f"批量更新失敗: {e}")
        raise HTTPException(status_code=500, detail=f"批量更新失敗: {str(e)}")

@router.post("/api/dashboard/kols/copy-settings")
async def copy_kol_settings(
    source_member_id: str,
    target_member_id: str,
    fields_to_copy: List[str],
    sheets_client: GoogleSheetsClient = Depends(get_sheets_client)
):
    """複製KOL設定"""
    try:
        manager = KOLRoleManager(sheets_client)
        
        # 執行複製
        success = manager.copy_kol_settings(
            source_member_id,
            target_member_id,
            fields_to_copy
        )
        
        if success:
            return {
                "success": True,
                "message": "KOL設定複製成功",
                "source_member_id": source_member_id,
                "target_member_id": target_member_id,
                "copied_fields": fields_to_copy
            }
        else:
            raise HTTPException(status_code=500, detail="複製失敗")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"複製KOL設定失敗: {e}")
        raise HTTPException(status_code=500, detail=f"複製失敗: {str(e)}")

@router.get("/api/dashboard/kols/{member_id}/settings")
async def get_kol_settings(
    member_id: str,
    sheets_client: GoogleSheetsClient = Depends(get_sheets_client)
):
    """獲取KOL完整設定"""
    try:
        manager = KOLRoleManager(sheets_client)
        
        kol_info = manager.get_kol_by_member_id(member_id)
        if not kol_info:
            raise HTTPException(status_code=404, detail="KOL不存在")
        
        return {
            "success": True,
            "data": kol_info,
            "member_id": member_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取KOL設定失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取設定失敗: {str(e)}")

@router.get("/api/dashboard/kols/export")
async def export_kol_settings(
    sheets_client: GoogleSheetsClient = Depends(get_sheets_client)
):
    """匯出所有KOL設定"""
    try:
        manager = KOLRoleManager(sheets_client)
        
        # 獲取所有KOL數據
        data = sheets_client.read_sheet(manager.sheet_name, 'A:AZ')
        
        if len(data) < 2:
            return {
                "success": True,
                "data": [],
                "message": "沒有KOL數據"
            }
        
        headers = data[0]
        kols = []
        
        for row in data[1:]:
            kol_data = manager._row_to_dict(row, headers)
            kols.append(kol_data)
        
        return {
            "success": True,
            "data": kols,
            "total_count": len(kols),
            "exported_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"匯出KOL設定失敗: {e}")
        raise HTTPException(status_code=500, detail=f"匯出失敗: {str(e)}")
