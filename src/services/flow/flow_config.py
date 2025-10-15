from dataclasses import dataclass
from typing import Optional

@dataclass
class FlowConfig:
    """流程配置類"""
    enable_content_generation: bool = True
    enable_sheets_recording: bool = True
    max_posts_per_kol: int = 3
    max_assignments_per_topic: int = 3  # 每個話題最多分配給幾個 KOL
    content_style: str = "analysis"
    enable_serper_api: bool = True
    enable_finlab_api: bool = True
