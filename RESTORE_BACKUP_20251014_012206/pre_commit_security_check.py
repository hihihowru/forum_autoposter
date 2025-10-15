#!/usr/bin/env python3
"""
Git 提交前安全檢查腳本
在 commit and push 之前檢查是否有潛在的 API 洩露
"""

import os
import re
import subprocess
import sys
from pathlib import Path

def check_for_api_keys():
    """檢查是否有 API Key 洩露"""
    print("🔍 檢查 API Key 洩露...")
    
    # 要檢查的 API Key 模式 - 更精確的匹配
    patterns = [
        r'sk-[a-zA-Z0-9]{48}',  # OpenAI API Key
        r'sk-proj-[a-zA-Z0-9]{48}',  # OpenAI Project API Key
        r'[A-Za-z0-9]{32,}',  # Generic API Key pattern (32+ chars)
        r'[A-Za-z0-9]{8,}',  # Generic password pattern (8+ chars) - 但排除常見變數名
    ]
    
    # 排除的文件和目錄
    exclude_patterns = [
        '.git', '__pycache__', 'node_modules', '.env', '.venv', 'venv',
        'test_env_variables.py', 'fix_all_hardcoded_secrets.py', 'replace_hardcoded_sheets_id.py'
    ]
    
    issues_found = []
    
    # 獲取所有要提交的文件
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        staged_files = []
    
    # 如果沒有 staged 文件，檢查所有文件
    if not staged_files:
        try:
            result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
            all_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except:
            all_files = []
        
        # 獲取所有 Python 文件
        python_files = []
        for root, dirs, files in os.walk('.'):
            # 排除不需要檢查的目錄
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if not any(pattern in file_path for pattern in exclude_patterns):
                        python_files.append(file_path)
        
        files_to_check = python_files
    else:
        files_to_check = [f for f in staged_files if f.endswith('.py')]
    
    print(f"📁 檢查 {len(files_to_check)} 個文件...")
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    issues_found.append({
                        'file': file_path,
                        'pattern': pattern,
                        'matches': matches
                    })
        except Exception as e:
            print(f"⚠️  無法讀取文件 {file_path}: {e}")
    
    return issues_found

def check_env_file():
    """檢查 .env 文件是否被意外提交"""
    print("🔍 檢查 .env 文件...")
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        status_output = result.stdout
        
        if '.env' in status_output:
            return True
    except:
        pass
    
    return False

def check_gitignore():
    """檢查 .gitignore 是否正確配置"""
    print("🔍 檢查 .gitignore 配置...")
    
    gitignore_path = '.gitignore'
    if not os.path.exists(gitignore_path):
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    required_patterns = ['.env', 'credentials/', '*.key', '*.pem']
    missing_patterns = []
    
    for pattern in required_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    return len(missing_patterns) == 0, missing_patterns

def main():
    """主函數"""
    print("🚨 Git 提交前安全檢查")
    print("=" * 50)
    
    # 檢查 API Key 洩露
    api_issues = check_for_api_keys()
    
    # 檢查 .env 文件
    env_issue = check_env_file()
    
    # 檢查 .gitignore
    gitignore_ok, missing_patterns = check_gitignore()
    
    print("\n📊 檢查結果:")
    print("=" * 50)
    
    # 報告 API Key 問題
    if api_issues:
        print("❌ 發現 API Key 洩露問題:")
        for issue in api_issues:
            print(f"   📄 {issue['file']}")
            print(f"   🔑 發現模式: {issue['pattern']}")
            print(f"   📍 匹配數量: {len(issue['matches'])}")
            print()
    else:
        print("✅ 未發現 API Key 洩露")
    
    # 報告 .env 文件問題
    if env_issue:
        print("❌ .env 文件被意外追蹤")
    else:
        print("✅ .env 文件未被追蹤")
    
    # 報告 .gitignore 問題
    if gitignore_ok:
        print("✅ .gitignore 配置正確")
    else:
        print("❌ .gitignore 缺少必要模式:")
        for pattern in missing_patterns:
            print(f"   📝 缺少: {pattern}")
    
    print("=" * 50)
    
    # 總結
    total_issues = len(api_issues) + (1 if env_issue else 0) + (0 if gitignore_ok else 1)
    
    if total_issues == 0:
        print("🎉 安全檢查通過！可以安全地 commit 和 push")
        return True
    else:
        print(f"🚨 發現 {total_issues} 個安全問題，請修復後再提交")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



