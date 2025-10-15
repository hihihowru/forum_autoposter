#!/usr/bin/env python3
"""
強力修復所有硬編碼敏感信息
"""

import os
import re
import glob

def fix_all_hardcoded_secrets_force():
    """強力修復所有硬編碼的敏感信息"""
    
    # 要替換的敏感信息
    replacements = {
        # Google Sheets ID
        os.getenv('GOOGLE_SHEETS_ID'): "os.getenv('GOOGLE_SHEETS_ID')",
        
        # CMoney 密碼
        os.getenv('CMONEY_PASSWORD'): "os.getenv('CMONEY_PASSWORD')",
        os.getenv('CMONEY_PASSWORD_201'): "os.getenv('CMONEY_PASSWORD_201')",
        os.getenv('CMONEY_PASSWORD_202'): "os.getenv('CMONEY_PASSWORD_202')",
        os.getenv('CMONEY_PASSWORD_203'): "os.getenv('CMONEY_PASSWORD_203')",
        os.getenv('CMONEY_PASSWORD_204'): "os.getenv('CMONEY_PASSWORD_204')",
        os.getenv('CMONEY_PASSWORD_205'): "os.getenv('CMONEY_PASSWORD_205')",
        os.getenv('CMONEY_PASSWORD_206'): "os.getenv('CMONEY_PASSWORD_206')",
        os.getenv('CMONEY_PASSWORD_207'): "os.getenv('CMONEY_PASSWORD_207')",
        os.getenv('CMONEY_PASSWORD_208'): "os.getenv('CMONEY_PASSWORD_208')",
        os.getenv('CMONEY_PASSWORD_209'): "os.getenv('CMONEY_PASSWORD_209')",
        os.getenv('CMONEY_PASSWORD_210'): "os.getenv('CMONEY_PASSWORD_210')",
        
        # FinLab API Key
        os.getenv('FINLAB_API_KEY'): "os.getenv('FINLAB_API_KEY')",
    }
    
    # 查找所有 Python 文件
    python_files = glob.glob("**/*.py", recursive=True)
    
    # 排除一些不需要修改的文件
    exclude_patterns = [
        "__pycache__",
        "node_modules",
        ".git",
        "venv",
        "env",
        ".venv",
        "pre_commit_security_check.py",  # 排除檢查腳本本身
        "fix_all_hardcoded_secrets.py",
        "replace_hardcoded_sheets_id.py"
    ]
    
    filtered_files = []
    for file_path in python_files:
        if not any(pattern in file_path for pattern in exclude_patterns):
            filtered_files.append(file_path)
    
    print(f"找到 {len(filtered_files)} 個 Python 文件需要檢查")
    
    replaced_count = 0
    
    for file_path in filtered_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_updated = False
            
            # 檢查是否需要添加 import os
            needs_os_import = False
            
            for old_value, new_value in replacements.items():
                if old_value in content:
                    # 替換硬編碼的值
                    content = content.replace(f'"{old_value}"', f'{new_value}')
                    content = content.replace(f"'{old_value}'", f'{new_value}')
                    
                    # 檢查是否需要添加 import os
                    if 'os.getenv(' in content and 'import os' not in content:
                        needs_os_import = True
                    
                    file_updated = True
            
            # 如果需要添加 import os
            if needs_os_import:
                # 找到第一個 import 語句的位置
                import_match = re.search(r'^import\s+', content, re.MULTILINE)
                if import_match:
                    # 在第一個 import 前添加 import os
                    pos = import_match.start()
                    content = content[:pos] + "import os\n" + content[pos:]
                else:
                    # 如果沒有 import 語句，在文件開頭添加
                    content = "import os\n" + content
            
            if file_updated and content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ 已更新: {file_path}")
                replaced_count += 1
                
        except Exception as e:
            print(f"  ❌ 處理文件 {file_path} 時出錯: {e}")
    
    print(f"\n總共更新了 {replaced_count} 個文件")

if __name__ == "__main__":
    fix_all_hardcoded_secrets_force()



