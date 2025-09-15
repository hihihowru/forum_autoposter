#!/usr/bin/env python3
"""
緊急安全修復腳本
"""

import os
import subprocess
import shutil

def emergency_security_fix():
    """緊急安全修復"""
    print("🚨 緊急安全修復開始...")
    print()
    
    # 1. 移除敏感文件
    sensitive_files = [
        "credentials/google-service-account.json",
        "docker-container/finlab python/python-service/.env"
    ]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            print(f"🗑️  移除敏感文件: {file_path}")
            os.remove(file_path)
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    print()
    
    # 2. 修復硬編碼的 API Keys
    files_with_hardcoded_keys = [
        "smart_limit_up_generator.py",
        "generate_kangpei_posts_v4.py", 
        "generate_kangpei_posts_v3.py",
        "generate_kangpei_posts.py",
        "generate_kangpei_posts_v6.py",
        "generate_kangpei_posts_v2.py"
    ]
    
    serper_key = os.getenv('SERPER_API_KEY')
    if not serper_key:
        raise ValueError("請設定 SERPER_API_KEY 環境變數")
    
    for file_path in files_with_hardcoded_keys:
        if os.path.exists(file_path):
            print(f"🔧 修復硬編碼 API Key: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替換硬編碼的 API Key
                content = content.replace(
                    f'SerperNewsClient("{serper_key}")',
                    'SerperNewsClient(os.getenv("SERPER_API_KEY"))'
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ 已修復: {file_path}")
            except Exception as e:
                print(f"❌ 修復失敗: {file_path} - {e}")
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    print()
    print("📋 需要手動處理的項目：")
    print("1. 撤銷 Google Service Account 憑證")
    print("2. 重新生成 FinLab API Key")
    print("3. 重新生成 Serper API Key")
    print("4. 從 Git 歷史中移除敏感文件")
    print("5. 更新所有相關的環境變數")
    print()
    print("🔗 Google Cloud Console: https://console.cloud.google.com/iam-admin/serviceaccounts")
    print("🔗 FinLab API: 請聯繫 FinLab 支援")
    print("🔗 Serper API: 請聯繫 Serper 支援")

if __name__ == "__main__":
    emergency_security_fix()
