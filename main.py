#!/usr/bin/env python3
"""
AI 發文系統主入口點
統一的系統啟動和管理介面
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from typing import Optional

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.main_workflow_engine import MainWorkflowEngine, WorkflowType, WorkflowConfig
from src.utils.config_manager import ConfigManager
from src.utils.logger import log_system_startup, log_system_shutdown, log_configuration_validation

class AIWorkflowCLI:
    """AI 工作流程命令行介面"""
    
    def __init__(self):
        """初始化 CLI"""
        self.engine = None
        self.config_manager = None
        
    async def initialize(self):
        """初始化系統"""
        try:
            # 記錄系統啟動
            log_system_startup()
            
            # 初始化配置管理器
            self.config_manager = ConfigManager()
            config_info = self.config_manager.get_environment_info()
            log_configuration_validation(config_info)
            
            # 初始化主工作流程引擎
            self.engine = MainWorkflowEngine()
            
            print("✅ 系統初始化完成")
            
        except Exception as e:
            print(f"❌ 系統初始化失敗: {e}")
            sys.exit(1)
    
    async def run_workflow(self, workflow_type: str, **kwargs):
        """執行指定的工作流程"""
        try:
            # 映射工作流程類型
            workflow_map = {
                'trending': WorkflowType.TRENDING_TOPICS,
                'limit_up': WorkflowType.LIMIT_UP_STOCKS,
                'hot_stocks': WorkflowType.HOT_STOCKS,
                'industry': WorkflowType.INDUSTRY_ANALYSIS,
                'revenue': WorkflowType.MONTHLY_REVENUE,
                'volume': WorkflowType.HIGH_VOLUME,
                'news': WorkflowType.NEWS_SUMMARY,
                'after_hours_limit_up': WorkflowType.AFTER_HOURS_LIMIT_UP
            }
            
            if workflow_type not in workflow_map:
                print(f"❌ 不支援的工作流程類型: {workflow_type}")
                print(f"支援的類型: {', '.join(workflow_map.keys())}")
                return
            
            # 創建工作流程配置
            config = WorkflowConfig(
                workflow_type=workflow_map[workflow_type],
                max_posts_per_topic=kwargs.get('max_posts', 3),
                enable_content_generation=kwargs.get('generate', True),
                enable_publishing=kwargs.get('publish', False),
                enable_learning=kwargs.get('learning', True),
                enable_quality_check=kwargs.get('quality_check', True),
                enable_sheets_recording=kwargs.get('record', True)
            )
            
            print(f"🚀 開始執行工作流程: {workflow_type}")
            print(f"📋 配置: 最大貼文數={config.max_posts_per_topic}, 生成內容={config.enable_content_generation}, 發布={config.enable_publishing}")
            
            # 執行工作流程
            result = await self.engine.execute_workflow(workflow_map[workflow_type], config)
            
            # 顯示結果
            self._display_result(result)
            
        except Exception as e:
            print(f"❌ 工作流程執行失敗: {e}")
    
    def _display_result(self, result):
        """顯示工作流程結果"""
        print("\n" + "="*50)
        print("📊 工作流程執行結果")
        print("="*50)
        
        print(f"✅ 狀態: {'成功' if result.success else '失敗'}")
        print(f"🔄 工作流程: {result.workflow_type.value}")
        print(f"📝 生成貼文: {result.total_posts_generated}")
        print(f"📤 發布貼文: {result.total_posts_published}")
        print(f"⏱️  執行時間: {result.execution_time:.2f}秒")
        
        if result.errors:
            print(f"\n❌ 錯誤 ({len(result.errors)}個):")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print(f"\n⚠️  警告 ({len(result.warnings)}個):")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        print("="*50)
    
    async def show_status(self):
        """顯示系統狀態"""
        if not self.engine:
            print("❌ 系統未初始化")
            return
        
        try:
            status = await self.engine.get_workflow_status()
            
            print("\n" + "="*50)
            print("📊 系統狀態")
            print("="*50)
            
            print(f"🔄 運行狀態: {'運行中' if status['is_running'] else '閒置'}")
            print(f"📋 當前工作流程: {status['current_workflow'] or '無'}")
            
            if status['start_time']:
                print(f"⏰ 開始時間: {status['start_time']}")
                print(f"⏱️  運行時間: {status['uptime']:.2f}秒")
            
            print("="*50)
            
        except Exception as e:
            print(f"❌ 獲取狀態失敗: {e}")
    
    async def stop_workflow(self):
        """停止當前工作流程"""
        if not self.engine:
            print("❌ 系統未初始化")
            return
        
        try:
            await self.engine.stop_workflow()
            print("✅ 工作流程已停止")
            
        except Exception as e:
            print(f"❌ 停止工作流程失敗: {e}")
    
    async def show_config(self):
        """顯示系統配置"""
        if not self.config_manager:
            print("❌ 配置管理器未初始化")
            return
        
        try:
            config = self.config_manager.get_config()
            env_info = self.config_manager.get_environment_info()
            
            print("\n" + "="*50)
            print("🔧 系統配置")
            print("="*50)
            
            print("📋 環境變數:")
            for key, value in env_info['environment_vars'].items():
                print(f"  - {key}: {value}")
            
            print(f"\n📁 配置路徑: {env_info['config_path']}")
            print(f"📄 配置文件存在: {env_info['config_exists']}")
            print(f"🐍 Python 版本: {env_info['python_version']}")
            
            print("\n📋 KOL 配置:")
            kol_settings = self.config_manager.get_kol_personalization_settings()
            for kol_id, settings in kol_settings.items():
                print(f"  - KOL {kol_id}: {settings['persona']} ({settings['writing_style']})")
            
            print("="*50)
            
        except Exception as e:
            print(f"❌ 顯示配置失敗: {e}")
    
    async def cleanup(self):
        """清理資源"""
        try:
            if self.engine:
                await self.engine.stop_workflow()
            
            log_system_shutdown()
            print("✅ 系統清理完成")
            
        except Exception as e:
            print(f"❌ 系統清理失敗: {e}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='AI 發文系統主入口點')
    parser.add_argument('command', choices=['run', 'status', 'stop', 'config', 'help'], 
                       help='執行的命令')
    parser.add_argument('--workflow', '-w', choices=['trending', 'limit_up', 'hot_stocks', 'industry', 'revenue', 'volume', 'news', 'after_hours_limit_up'],
                       help='工作流程類型')
    parser.add_argument('--max-posts', '-m', type=int, default=3,
                       help='每個話題的最大貼文數')
    parser.add_argument('--generate', '-g', action='store_true', default=True,
                       help='啟用內容生成')
    parser.add_argument('--publish', '-p', action='store_true', default=False,
                       help='啟用自動發布')
    parser.add_argument('--learning', '-l', action='store_true', default=True,
                       help='啟用學習機制')
    parser.add_argument('--quality-check', '-q', action='store_true', default=True,
                       help='啟用品質檢查')
    parser.add_argument('--record', '-r', action='store_true', default=True,
                       help='啟用 Google Sheets 記錄')
    
    args = parser.parse_args()
    
    # 創建 CLI 實例
    cli = AIWorkflowCLI()
    
    async def run_cli():
        """運行 CLI"""
        try:
            # 初始化系統
            await cli.initialize()
            
            # 執行命令
            if args.command == 'run':
                if not args.workflow:
                    print("❌ 請指定工作流程類型 (--workflow)")
                    return
                
                await cli.run_workflow(
                    args.workflow,
                    max_posts=args.max_posts,
                    generate=args.generate,
                    publish=args.publish,
                    learning=args.learning,
                    quality_check=args.quality_check,
                    record=args.record
                )
                
            elif args.command == 'status':
                await cli.show_status()
                
            elif args.command == 'stop':
                await cli.stop_workflow()
                
            elif args.command == 'config':
                await cli.show_config()
                
            elif args.command == 'help':
                print("""
🤖 AI 發文系統使用說明

📋 支援的命令:
  run      - 執行工作流程
  status   - 顯示系統狀態
  stop     - 停止當前工作流程
  config   - 顯示系統配置
  help     - 顯示此說明

📋 支援的工作流程:
  trending    - 熱門話題觸發器
  limit_up    - 漲停股觸發器
  hot_stocks  - 熱門股觸發器
  industry    - 產業分析觸發器
  revenue     - 月營收觸發器
  volume      - 高成交量觸發器
  news        - 新聞總結觸發器
  after_hours_limit_up - 盤後漲停股分析

📋 常用參數:
  --workflow, -w     - 指定工作流程類型
  --max-posts, -m    - 每個話題的最大貼文數 (預設: 3)
  --generate, -g     - 啟用內容生成 (預設: 是)
  --publish, -p      - 啟用自動發布 (預設: 否)
  --learning, -l     - 啟用學習機制 (預設: 是)
  --quality-check, -q - 啟用品質檢查 (預設: 是)
  --record, -r       - 啟用 Google Sheets 記錄 (預設: 是)

📋 使用範例:
  # 執行熱門話題工作流程
  python main.py run --workflow trending --max-posts 5

  # 執行漲停股工作流程並自動發布
  python main.py run --workflow limit_up --publish

  # 查看系統狀態
  python main.py status

  # 查看系統配置
  python main.py config

  # 停止當前工作流程
  python main.py stop
                """)
            
        except KeyboardInterrupt:
            print("\n⚠️ 收到中斷信號，正在停止...")
        except Exception as e:
            print(f"❌ 執行失敗: {e}")
        finally:
            # 清理資源
            await cli.cleanup()
    
    # 運行 CLI
    asyncio.run(run_cli())

if __name__ == "__main__":
    main()
