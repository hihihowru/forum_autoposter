#!/usr/bin/env python3
"""
儀表板啟動腳本
啟動 Dashboard API 和前端服務
"""

import subprocess
import time
import os
import sys
import logging
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """檢查依賴"""
    try:
        # 檢查 Node.js
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ Node.js 未安裝或不在 PATH 中")
            return False
        logger.info(f"✅ Node.js 版本: {result.stdout.strip()}")
        
        # 檢查 npm
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ npm 未安裝或不在 PATH 中")
            return False
        logger.info(f"✅ npm 版本: {result.stdout.strip()}")
        
        # 檢查 Python
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ Python3 未安裝或不在 PATH 中")
            return False
        logger.info(f"✅ Python 版本: {result.stdout.strip()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 檢查依賴時發生錯誤: {e}")
        return False

def install_frontend_dependencies():
    """安裝前端依賴"""
    try:
        frontend_dir = Path("docker-container/finlab python/apps/dashboard-frontend")
        if not frontend_dir.exists():
            logger.error(f"❌ 前端目錄不存在: {frontend_dir}")
            return False
        
        logger.info("📦 安裝前端依賴...")
        result = subprocess.run(
            ['npm', 'install'],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ 安裝前端依賴失敗: {result.stderr}")
            return False
        
        logger.info("✅ 前端依賴安裝完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 安裝前端依賴時發生錯誤: {e}")
        return False

def install_backend_dependencies():
    """安裝後端依賴"""
    try:
        backend_dir = Path("docker-container/finlab python/apps/dashboard-api")
        if not backend_dir.exists():
            logger.error(f"❌ 後端目錄不存在: {backend_dir}")
            return False
        
        logger.info("📦 安裝後端依賴...")
        result = subprocess.run(
            ['pip3', 'install', '-r', 'requirements.txt'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ 安裝後端依賴失敗: {result.stderr}")
            return False
        
        logger.info("✅ 後端依賴安裝完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 安裝後端依賴時發生錯誤: {e}")
        return False

def start_backend():
    """啟動後端 API 服務"""
    try:
        backend_dir = Path("docker-container/finlab python/apps/dashboard-api")
        
        # 設定環境變數
        env = os.environ.copy()
        env['GOOGLE_CREDENTIALS_FILE'] = str(Path.cwd() / 'credentials' / 'google-service-account.json')
        env['GOOGLE_SHEETS_ID'] = os.getenv('GOOGLE_SHEETS_ID')
        env['PYTHONPATH'] = f"{Path.cwd()}/src:{Path.cwd()}/docker-container/finlab python/apps/dashboard-api/src"
        
        logger.info("🚀 啟動 Dashboard API 服務...")
        logger.info(f"   端口: 8007")
        logger.info(f"   目錄: {backend_dir}")
        
        process = subprocess.Popen(
            ['python3', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8007', '--reload'],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服務啟動
        time.sleep(3)
        
        if process.poll() is None:
            logger.info("✅ Dashboard API 服務啟動成功")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Dashboard API 服務啟動失敗: {stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ 啟動後端服務時發生錯誤: {e}")
        return None

def start_frontend():
    """啟動前端服務"""
    try:
        frontend_dir = Path("docker-container/finlab python/apps/dashboard-frontend")
        
        # 設定環境變數
        env = os.environ.copy()
        env['VITE_API_BASE_URL'] = 'http://localhost:8007'
        
        logger.info("🚀 啟動 Dashboard 前端服務...")
        logger.info(f"   端口: 3000")
        logger.info(f"   目錄: {frontend_dir}")
        
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=frontend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服務啟動
        time.sleep(5)
        
        if process.poll() is None:
            logger.info("✅ Dashboard 前端服務啟動成功")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Dashboard 前端服務啟動失敗: {stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ 啟動前端服務時發生錯誤: {e}")
        return None

def check_services():
    """檢查服務狀態"""
    import requests
    
    try:
        # 檢查後端 API
        response = requests.get('http://localhost:8007/health', timeout=5)
        if response.status_code == 200:
            logger.info("✅ Dashboard API 服務正常運行")
        else:
            logger.warning(f"⚠️ Dashboard API 服務狀態異常: {response.status_code}")
            
    except Exception as e:
        logger.warning(f"⚠️ 無法連接到 Dashboard API: {e}")
    
    try:
        # 檢查前端
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            logger.info("✅ Dashboard 前端服務正常運行")
        else:
            logger.warning(f"⚠️ Dashboard 前端服務狀態異常: {response.status_code}")
            
    except Exception as e:
        logger.warning(f"⚠️ 無法連接到 Dashboard 前端: {e}")

def main():
    """主函數"""
    logger.info("🎯 開始啟動虛擬 KOL 系統儀表板")
    
    # 檢查依賴
    if not check_dependencies():
        logger.error("❌ 依賴檢查失敗，請安裝必要的依賴")
        return
    
    # 安裝依賴
    if not install_frontend_dependencies():
        logger.error("❌ 前端依賴安裝失敗")
        return
    
    if not install_backend_dependencies():
        logger.error("❌ 後端依賴安裝失敗")
        return
    
    # 啟動後端
    backend_process = start_backend()
    if not backend_process:
        logger.error("❌ 後端服務啟動失敗")
        return
    
    # 啟動前端
    frontend_process = start_frontend()
    if not frontend_process:
        logger.error("❌ 前端服務啟動失敗")
        backend_process.terminate()
        return
    
    # 檢查服務狀態
    time.sleep(2)
    check_services()
    
    logger.info("🎉 儀表板啟動完成！")
    logger.info("📊 Dashboard 前端: http://localhost:3000")
    logger.info("🔧 Dashboard API: http://localhost:8007")
    logger.info("📚 API 文檔: http://localhost:8007/docs")
    
    try:
        # 保持服務運行
        while True:
            time.sleep(10)
            # 檢查進程是否還在運行
            if backend_process.poll() is not None:
                logger.error("❌ 後端服務意外停止")
                break
            if frontend_process.poll() is not None:
                logger.error("❌ 前端服務意外停止")
                break
                
    except KeyboardInterrupt:
        logger.info("🛑 收到停止信號，正在關閉服務...")
        
        # 關閉服務
        if backend_process:
            backend_process.terminate()
            logger.info("✅ 後端服務已關閉")
        
        if frontend_process:
            frontend_process.terminate()
            logger.info("✅ 前端服務已關閉")
        
        logger.info("👋 儀表板已關閉")

if __name__ == "__main__":
    main()



