#!/usr/bin/env python3
"""
統一日誌管理器
提供統一的日誌格式和配置管理
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(name: str, 
                level: str = "INFO",
                log_file: Optional[str] = None,
                max_file_size: int = 10 * 1024 * 1024,  # 10MB
                backup_count: int = 5) -> logging.Logger:
    """
    設置統一的日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        level: 日誌級別
        log_file: 日誌文件路徑
        max_file_size: 最大文件大小
        backup_count: 備份文件數量
        
    Returns:
        配置好的日誌記錄器
    """
    
    # 創建日誌記錄器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重複添加處理器
    if logger.handlers:
        return logger
    
    # 創建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件處理器（如果指定了日誌文件）
    if log_file:
        # 確保日誌目錄存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 創建輪轉文件處理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_workflow_logger(workflow_name: str) -> logging.Logger:
    """
    獲取工作流程專用的日誌記錄器
    
    Args:
        workflow_name: 工作流程名稱
        
    Returns:
        工作流程日誌記錄器
    """
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = f"logs/workflows/{workflow_name}_{timestamp}.log"
    
    return setup_logger(
        name=f"workflow.{workflow_name}",
        level="INFO",
        log_file=log_file
    )

def get_kol_logger(kol_serial: str) -> logging.Logger:
    """
    獲取 KOL 專用的日誌記錄器
    
    Args:
        kol_serial: KOL 序號
        
    Returns:
        KOL 日誌記錄器
    """
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = f"logs/kols/kol_{kol_serial}_{timestamp}.log"
    
    return setup_logger(
        name=f"kol.{kol_serial}",
        level="INFO",
        log_file=log_file
    )

def get_error_logger() -> logging.Logger:
    """
    獲取錯誤專用的日誌記錄器
    
    Returns:
        錯誤日誌記錄器
    """
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = f"logs/errors/errors_{timestamp}.log"
    
    return setup_logger(
        name="errors",
        level="ERROR",
        log_file=log_file
    )

def get_performance_logger() -> logging.Logger:
    """
    獲取性能監控專用的日誌記錄器
    
    Returns:
        性能日誌記錄器
    """
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = f"logs/performance/performance_{timestamp}.log"
    
    return setup_logger(
        name="performance",
        level="INFO",
        log_file=log_file
    )

class WorkflowLogger:
    """工作流程日誌管理器"""
    
    def __init__(self, workflow_name: str):
        """初始化工作流程日誌管理器"""
        self.workflow_name = workflow_name
        self.logger = get_workflow_logger(workflow_name)
        self.start_time = datetime.now()
        
        self.logger.info(f"🚀 工作流程開始: {workflow_name}")
        self.logger.info(f"⏰ 開始時間: {self.start_time}")
    
    def log_step(self, step_name: str, status: str = "開始", details: Optional[str] = None):
        """記錄步驟執行"""
        message = f"📋 步驟: {step_name} - {status}"
        if details:
            message += f" | {details}"
        
        if status == "開始":
            self.logger.info(message)
        elif status == "完成":
            self.logger.info(f"✅ {message}")
        elif status == "失敗":
            self.logger.error(f"❌ {message}")
        elif status == "警告":
            self.logger.warning(f"⚠️ {message}")
        else:
            self.logger.info(message)
    
    def log_error(self, error: Exception, context: Optional[str] = None):
        """記錄錯誤"""
        message = f"❌ 錯誤: {type(error).__name__}: {str(error)}"
        if context:
            message += f" | 上下文: {context}"
        
        self.logger.error(message)
        
        # 同時記錄到錯誤日誌
        error_logger = get_error_logger()
        error_logger.error(message, exc_info=True)
    
    def log_performance(self, operation: str, duration: float, details: Optional[str] = None):
        """記錄性能指標"""
        message = f"⚡ 性能: {operation} - {duration:.2f}秒"
        if details:
            message += f" | {details}"
        
        self.logger.info(message)
        
        # 同時記錄到性能日誌
        perf_logger = get_performance_logger()
        perf_logger.info(message)
    
    def log_kol_activity(self, kol_serial: str, action: str, details: Optional[str] = None):
        """記錄 KOL 活動"""
        message = f"👤 KOL {kol_serial}: {action}"
        if details:
            message += f" | {details}"
        
        self.logger.info(message)
    
    def log_content_generation(self, kol_serial: str, topic: str, success: bool, details: Optional[str] = None):
        """記錄內容生成"""
        status = "✅ 成功" if success else "❌ 失敗"
        message = f"📝 內容生成: KOL {kol_serial} - {topic} - {status}"
        if details:
            message += f" | {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_publishing(self, kol_serial: str, post_id: str, success: bool, details: Optional[str] = None):
        """記錄發布活動"""
        status = "✅ 成功" if success else "❌ 失敗"
        message = f"📤 發布: KOL {kol_serial} - {post_id} - {status}"
        if details:
            message += f" | {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def finish(self, success: bool = True, summary: Optional[str] = None):
        """完成工作流程並記錄總結"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        status = "✅ 成功完成" if success else "❌ 執行失敗"
        message = f"🏁 工作流程結束: {self.workflow_name} - {status}"
        message += f" | 總執行時間: {duration:.2f}秒"
        
        if summary:
            message += f" | 總結: {summary}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)

class KOLActivityLogger:
    """KOL 活動日誌管理器"""
    
    def __init__(self, kol_serial: str):
        """初始化 KOL 活動日誌管理器"""
        self.kol_serial = kol_serial
        self.logger = get_kol_logger(kol_serial)
        
        self.logger.info(f"👤 KOL {kol_serial} 活動開始記錄")
    
    def log_login(self, success: bool, details: Optional[str] = None):
        """記錄登入活動"""
        status = "✅ 成功" if success else "❌ 失敗"
        message = f"🔐 登入: {status}"
        if details:
            message += f" | {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_content_creation(self, topic: str, content_length: int, success: bool, details: Optional[str] = None):
        """記錄內容創建"""
        status = "✅ 成功" if success else "❌ 失敗"
        message = f"📝 內容創建: {topic} - {content_length}字 - {status}"
        if details:
            message += f" | {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_publishing(self, post_id: str, success: bool, details: Optional[str] = None):
        """記錄發布活動"""
        status = "✅ 成功" if success else "❌ 失敗"
        message = f"📤 發布: {post_id} - {status}"
        if details:
            message += f" | {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_interaction(self, post_id: str, interaction_type: str, count: int):
        """記錄互動數據"""
        message = f"💬 互動: {post_id} - {interaction_type}: {count}"
        self.logger.info(message)
    
    def log_error(self, error: Exception, context: Optional[str] = None):
        """記錄錯誤"""
        message = f"❌ 錯誤: {type(error).__name__}: {str(error)}"
        if context:
            message += f" | 上下文: {context}"
        
        self.logger.error(message)
        
        # 同時記錄到錯誤日誌
        error_logger = get_error_logger()
        error_logger.error(message, exc_info=True)

def log_system_startup():
    """記錄系統啟動"""
    logger = setup_logger("system.startup")
    logger.info("🚀 AI 發文系統啟動")
    logger.info(f"⏰ 啟動時間: {datetime.now()}")
    logger.info(f"🐍 Python 版本: {sys.version}")
    logger.info(f"📁 工作目錄: {os.getcwd()}")

def log_system_shutdown():
    """記錄系統關閉"""
    logger = setup_logger("system.shutdown")
    logger.info("🛑 AI 發文系統關閉")
    logger.info(f"⏰ 關閉時間: {datetime.now()}")

def log_configuration_validation(config_info: dict):
    """記錄配置驗證結果"""
    logger = setup_logger("system.config")
    logger.info("🔧 配置驗證開始")
    
    for key, value in config_info.items():
        if isinstance(value, dict):
            logger.info(f"📋 {key}:")
            for sub_key, sub_value in value.items():
                logger.info(f"  - {sub_key}: {sub_value}")
        else:
            logger.info(f"📋 {key}: {value}")
    
    logger.info("✅ 配置驗證完成")

def log_api_call(api_name: str, endpoint: str, success: bool, duration: float, details: Optional[str] = None):
    """記錄 API 調用"""
    logger = get_performance_logger()
    
    status = "✅ 成功" if success else "❌ 失敗"
    message = f"🌐 API 調用: {api_name} - {endpoint} - {status} - {duration:.2f}秒"
    if details:
        message += f" | {details}"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)




