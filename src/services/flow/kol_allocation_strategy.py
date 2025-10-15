#!/usr/bin/env python3
"""
KOL 分配策略系統
區分「固定KOL池」和「配對池」兩種分配策略
"""

import os
import random
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from src.services.assign.assignment_service import AssignmentService, TopicData, TaskAssignment
from src.services.kol.kol_settings_loader import KOLSettingsLoader

logger = logging.getLogger(__name__)

class AllocationStrategy(Enum):
    """KOL分配策略類型"""
    FIXED_POOL = "fixed_pool"      # 固定KOL池
    MATCHING_POOL = "matching_pool" # 配對池

@dataclass
class TriggerConfig:
    """觸發器配置"""
    trigger_type: str
    allocation_strategy: AllocationStrategy
    fixed_kol_pool: Optional[List[int]] = None
    max_assignments_per_topic: int = 3
    enable_content_generation: bool = True
    enable_publishing: bool = False

class KOLAllocationStrategy:
    """KOL分配策略管理器"""
    
    def __init__(self, sheets_client):
        self.sheets_client = sheets_client
        self.assignment_service = AssignmentService(sheets_client)
        self.kol_settings_loader = KOLSettingsLoader(sheets_client)
        
        # 載入KOL配置
        self.kol_profiles = self._load_kol_profiles()
        
        # 固定KOL池配置
        self.fixed_pools = self._initialize_fixed_pools()
        
        logger.info(f"KOL分配策略初始化完成，載入 {len(self.kol_profiles)} 個KOL")
    
    def _load_kol_profiles(self) -> List[Dict[str, Any]]:
        """載入所有KOL配置"""
        try:
            # 從Google Sheets載入KOL設定
            rows = self.kol_settings_loader._read_all_rows('同學會帳號管理')
            if not rows:
                logger.warning("無法載入KOL設定，使用預設配置")
                return self._get_default_kol_profiles()
            
            headers = rows[0]
            kol_profiles = []
            
            for row in rows[1:]:
                if len(row) < len(headers):
                    row.extend([''] * (len(headers) - len(row)))
                
                kol_data = dict(zip(headers, row))
                if kol_data.get('序號') and kol_data.get('暱稱'):
                    kol_profiles.append(kol_data)
            
            logger.info(f"成功載入 {len(kol_profiles)} 個KOL配置")
            return kol_profiles
            
        except Exception as e:
            logger.error(f"載入KOL配置失敗: {e}")
            return self._get_default_kol_profiles()
    
    def _get_default_kol_profiles(self) -> List[Dict[str, Any]]:
        """預設KOL配置"""
        return [
            {"序號": "200", "暱稱": "川川哥", "人設": "技術派", "狀態": "啟用"},
            {"序號": "201", "暱稱": "韭割哥", "人設": "籌碼派", "狀態": "啟用"},
            {"序號": "202", "暱稱": "梅川褲子", "人設": "基本面派", "狀態": "啟用"},
            {"序號": "203", "暱稱": "信號宅神", "人設": "技術派", "狀態": "啟用"},
            {"序號": "204", "暱稱": "八卦護城河", "人設": "消息面派", "狀態": "啟用"},
            {"序號": "205", "暱稱": "長線韭韭", "人設": "價值投資派", "狀態": "啟用"},
            {"序號": "206", "暱稱": "報爆哥", "人設": "消息面派", "狀態": "啟用"},
            {"序號": "207", "暱稱": "板橋大who", "人設": "技術派", "狀態": "啟用"},
            {"序號": "208", "暱稱": "韭割哥2", "人設": "籌碼派", "狀態": "啟用"},
            {"序號": "209", "暱稱": "小道爆料王", "人設": "消息面派", "狀態": "啟用"},
            {"序號": "210", "暱稱": "技術分析師", "人設": "技術派", "狀態": "啟用"}
        ]
    
    def _initialize_fixed_pools(self) -> Dict[str, List[int]]:
        """初始化固定KOL池"""
        return {
            "after_hours_limit_up": {
                "high_volume": [201, 202, 203, 204, 205],  # 高量股票專用KOL
                "low_volume": [206, 207, 208, 209, 210]    # 低量股票專用KOL
            },
            "intraday_surge": {
                "all": [201, 202, 203, 204, 205, 206, 207, 208, 209, 210]  # 盤中急漲股可用所有KOL
            },
            "trending_topics": {
                "matching": []  # 使用配對池，不預設固定KOL
            }
        }
    
    def allocate_kols(self, config: TriggerConfig, topics: List[TopicData]) -> List[TaskAssignment]:
        """
        根據策略分配KOL
        
        Args:
            config: 觸發器配置
            topics: 話題列表
            
        Returns:
            任務分配結果
        """
        logger.info(f"開始KOL分配，策略: {config.allocation_strategy.value}")
        
        if config.allocation_strategy == AllocationStrategy.FIXED_POOL:
            return self._allocate_fixed_pool(config, topics)
        elif config.allocation_strategy == AllocationStrategy.MATCHING_POOL:
            return self._allocate_matching_pool(config, topics)
        else:
            raise ValueError(f"不支援的分配策略: {config.allocation_strategy}")
    
    def _allocate_fixed_pool(self, config: TriggerConfig, topics: List[TopicData]) -> List[TaskAssignment]:
        """固定KOL池分配"""
        logger.info(f"使用固定KOL池分配，觸發器: {config.trigger_type}")
        
        assignments = []
        
        # 獲取固定KOL池
        fixed_pool = self._get_fixed_pool(config.trigger_type)
        if not fixed_pool:
            logger.warning(f"找不到觸發器 {config.trigger_type} 的固定KOL池，使用預設")
            fixed_pool = [201, 202, 203, 204, 205]
        
        logger.info(f"固定KOL池: {fixed_pool}")
        
        for i, topic in enumerate(topics):
            # 輪流分配KOL
            kol_serial = fixed_pool[i % len(fixed_pool)]
            
            # 獲取KOL資訊
            kol_info = self._get_kol_info(kol_serial)
            if not kol_info:
                logger.warning(f"找不到KOL {kol_serial} 的配置")
                continue
            
            # 創建任務分配
            assignment = TaskAssignment(
                task_id=f"{topic.topic_id}::{kol_serial}",
                topic_id=topic.topic_id,
                kol_serial=kol_serial,
                topic_title=topic.title,
                topic_keywords=topic.persona_tags + topic.industry_tags + topic.event_tags,
                match_score=999.0,  # 固定分配給最高分
                status="queued"
            )
            
            assignments.append(assignment)
            logger.info(f"固定分配: {topic.title} -> KOL {kol_serial} ({kol_info.get('暱稱', 'Unknown')})")
        
        logger.info(f"固定KOL池分配完成，共 {len(assignments)} 個任務")
        return assignments
    
    def _allocate_matching_pool(self, config: TriggerConfig, topics: List[TopicData]) -> List[TaskAssignment]:
        """配對池分配"""
        logger.info(f"使用配對池分配，觸發器: {config.trigger_type}")
        
        # 使用現有的AssignmentService進行智能匹配
        assignments = self.assignment_service.assign_topics(
            topics, 
            max_assignments_per_topic=config.max_assignments_per_topic
        )
        
        logger.info(f"配對池分配完成，共 {len(assignments)} 個任務")
        return assignments
    
    def _get_fixed_pool(self, trigger_type: str) -> List[int]:
        """獲取指定觸發器的固定KOL池"""
        if trigger_type == "after_hours_limit_up":
            # 盤後機器人：合併高量和低量KOL池
            high_volume_kols = self.fixed_pools["after_hours_limit_up"]["high_volume"]
            low_volume_kols = self.fixed_pools["after_hours_limit_up"]["low_volume"]
            return high_volume_kols + low_volume_kols  # 15個KOL
        
        elif trigger_type == "intraday_surge":
            return self.fixed_pools["intraday_surge"]["all"]
        
        else:
            logger.warning(f"未定義觸發器 {trigger_type} 的固定KOL池")
            return []
    
    def _get_kol_info(self, kol_serial: int) -> Optional[Dict[str, Any]]:
        """獲取KOL資訊"""
        for kol in self.kol_profiles:
            if str(kol.get('序號', '')) == str(kol_serial):
                return kol
        return None
    
    def update_fixed_pool(self, trigger_type: str, pool_name: str, kol_list: List[int]):
        """更新固定KOL池"""
        if trigger_type not in self.fixed_pools:
            self.fixed_pools[trigger_type] = {}
        
        self.fixed_pools[trigger_type][pool_name] = kol_list
        logger.info(f"更新固定KOL池: {trigger_type}.{pool_name} = {kol_list}")
    
    def get_allocation_summary(self) -> Dict[str, Any]:
        """獲取分配策略摘要"""
        return {
            "total_kols": len(self.kol_profiles),
            "fixed_pools": self.fixed_pools,
            "available_strategies": [strategy.value for strategy in AllocationStrategy]
        }

# 預設觸發器配置
DEFAULT_TRIGGER_CONFIGS = {
    "after_hours_limit_up": TriggerConfig(
        trigger_type="after_hours_limit_up",
        allocation_strategy=AllocationStrategy.FIXED_POOL,
        max_assignments_per_topic=1,  # 每檔股票分配1個KOL
        enable_content_generation=True,
        enable_publishing=False
    ),
    "intraday_surge": TriggerConfig(
        trigger_type="intraday_surge", 
        allocation_strategy=AllocationStrategy.FIXED_POOL,
        max_assignments_per_topic=1,
        enable_content_generation=True,
        enable_publishing=False
    ),
    "trending_topics": TriggerConfig(
        trigger_type="trending_topics",
        allocation_strategy=AllocationStrategy.MATCHING_POOL,
        max_assignments_per_topic=3,  # 每個話題最多3個KOL
        enable_content_generation=True,
        enable_publishing=False
    ),
    "limit_up_stocks": TriggerConfig(
        trigger_type="limit_up_stocks",
        allocation_strategy=AllocationStrategy.MATCHING_POOL,
        max_assignments_per_topic=2,
        enable_content_generation=True,
        enable_publishing=False
    ),
    "hot_stocks": TriggerConfig(
        trigger_type="hot_stocks",
        allocation_strategy=AllocationStrategy.MATCHING_POOL,
        max_assignments_per_topic=2,
        enable_content_generation=True,
        enable_publishing=False
    )
}

def create_allocation_strategy(sheets_client) -> KOLAllocationStrategy:
    """創建KOL分配策略實例"""
    return KOLAllocationStrategy(sheets_client)








