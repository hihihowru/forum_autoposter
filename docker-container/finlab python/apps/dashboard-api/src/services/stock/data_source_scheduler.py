"""
數據源調度器
負責管理和調度不同類型的個股數據源
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """數據源類型"""
    TECHNICAL = "technical"      # 技術分析相關
    FUNDAMENTAL = "fundamental"  # 基本面分析相關
    REVENUE = "revenue"         # 營收相關
    FINANCIAL = "financial"     # 財報相關
    MARKET = "market"           # 市場數據相關

@dataclass
class DataSource:
    """數據源定義"""
    name: str
    type: DataSourceType
    priority: int  # 優先級，數字越小優先級越高
    description: str
    api_endpoint: Optional[str] = None
    finlab_key: Optional[str] = None
    enabled: bool = True

class DataSourceScheduler:
    """數據源調度器"""
    
    def __init__(self):
        """初始化數據源調度器"""
        self.data_sources = self._initialize_data_sources()
        logger.info("數據源調度器初始化完成")
    
    def _initialize_data_sources(self) -> Dict[DataSourceType, List[DataSource]]:
        """初始化數據源配置"""
        data_sources = {
            DataSourceType.TECHNICAL: [
                DataSource(
                    name="OHLC數據",
                    type=DataSourceType.TECHNICAL,
                    priority=1,
                    description="股價開高低收成交量數據",
                    api_endpoint="http://localhost:8001/get_ohlc",
                    enabled=True
                ),
                DataSource(
                    name="技術指標分析",
                    type=DataSourceType.TECHNICAL,
                    priority=2,
                    description="RSI、MACD、移動平均線等技術指標",
                    api_endpoint="http://localhost:8002/analyze",
                    enabled=True
                )
            ],
            DataSourceType.REVENUE: [
                DataSource(
                    name="月營收數據",
                    type=DataSourceType.REVENUE,
                    priority=1,
                    description="當月營收、上月營收、年增率等",
                    finlab_key="monthly_revenue:當月營收",
                    enabled=True
                ),
                DataSource(
                    name="營收成長分析",
                    type=DataSourceType.REVENUE,
                    priority=2,
                    description="營收年增率、月增率分析",
                    finlab_key="monthly_revenue:去年同月增減(%)",
                    enabled=True
                )
            ],
            DataSourceType.FINANCIAL: [
                DataSource(
                    name="財報數據",
                    type=DataSourceType.FINANCIAL,
                    priority=1,
                    description="資產負債表、損益表、現金流量表",
                    finlab_key="financial_statement:營業收入淨額",
                    enabled=True
                ),
                DataSource(
                    name="財務比率分析",
                    type=DataSourceType.FINANCIAL,
                    priority=2,
                    description="本益比、股價淨值比、ROE等",
                    finlab_key="financial_statement:每股盈餘",
                    enabled=True
                )
            ],
            DataSourceType.FUNDAMENTAL: [
                DataSource(
                    name="基本面分析",
                    type=DataSourceType.FUNDAMENTAL,
                    priority=1,
                    description="公司基本面數據分析",
                    enabled=True
                )
            ],
            DataSourceType.MARKET: [
                DataSource(
                    name="市場數據",
                    type=DataSourceType.MARKET,
                    priority=1,
                    description="市場整體數據",
                    enabled=True
                )
            ]
        }
        
        return data_sources
    
    def get_data_sources_by_type(self, data_type: DataSourceType) -> List[DataSource]:
        """根據類型獲取數據源"""
        return self.data_sources.get(data_type, [])
    
    def get_enabled_data_sources(self, data_type: DataSourceType) -> List[DataSource]:
        """獲取啟用的數據源"""
        sources = self.get_data_sources_by_type(data_type)
        return [source for source in sources if source.enabled]
    
    def get_priority_sorted_sources(self, data_type: DataSourceType) -> List[DataSource]:
        """獲取按優先級排序的數據源"""
        sources = self.get_enabled_data_sources(data_type)
        return sorted(sources, key=lambda x: x.priority)
    
    def get_all_data_types(self) -> List[DataSourceType]:
        """獲取所有數據類型"""
        return list(self.data_sources.keys())
    
    def get_data_source_info(self) -> Dict[str, Any]:
        """獲取數據源資訊"""
        info = {}
        for data_type, sources in self.data_sources.items():
            info[data_type.value] = {
                "count": len(sources),
                "enabled": len([s for s in sources if s.enabled]),
                "sources": [
                    {
                        "name": source.name,
                        "priority": source.priority,
                        "description": source.description,
                        "enabled": source.enabled
                    }
                    for source in sources
                ]
            }
        return info
    
    def enable_data_source(self, data_type: DataSourceType, source_name: str):
        """啟用數據源"""
        sources = self.get_data_sources_by_type(data_type)
        for source in sources:
            if source.name == source_name:
                source.enabled = True
                logger.info(f"啟用數據源: {data_type.value} - {source_name}")
                return
        logger.warning(f"未找到數據源: {data_type.value} - {source_name}")
    
    def disable_data_source(self, data_type: DataSourceType, source_name: str):
        """停用數據源"""
        sources = self.get_data_sources_by_type(data_type)
        for source in sources:
            if source.name == source_name:
                source.enabled = False
                logger.info(f"停用數據源: {data_type.value} - {source_name}")
                return
        logger.warning(f"未找到數據源: {data_type.value} - {source_name}")

# 創建全域調度器實例
data_source_scheduler = DataSourceScheduler()

def get_data_source_scheduler() -> DataSourceScheduler:
    """獲取數據源調度器實例"""
    return data_source_scheduler

# 測試函數
def test_data_source_scheduler():
    """測試數據源調度器"""
    try:
        scheduler = get_data_source_scheduler()
        
        print("🔍 測試數據源調度器")
        print("=" * 50)
        
        # 測試獲取不同類型的數據源
        for data_type in DataSourceType:
            sources = scheduler.get_priority_sorted_sources(data_type)
            print(f"\n{data_type.value.upper()} 數據源:")
            for source in sources:
                print(f"  - {source.name} (優先級: {source.priority})")
                print(f"    描述: {source.description}")
                print(f"    狀態: {'啟用' if source.enabled else '停用'}")
        
        # 測試數據源資訊
        print(f"\n📊 數據源統計:")
        info = scheduler.get_data_source_info()
        for data_type, data_info in info.items():
            print(f"  {data_type}: {data_info['enabled']}/{data_info['count']} 啟用")
        
        print("\n✅ 數據源調度器測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    test_data_source_scheduler()

