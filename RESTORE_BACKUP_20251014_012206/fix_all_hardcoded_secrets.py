#!/usr/bin/env python3
"""
全面修復所有遺漏的硬編碼敏感信息
"""

import os
import re
import glob

def fix_all_hardcoded_secrets():
    """修復所有硬編碼的敏感信息"""
    
    # 要替換的敏感信息 - 使用環境變數
    replacements = {
        # Google Sheets ID
        "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s": "os.getenv('GOOGLE_SHEETS_ID')",
        
        # CMoney 密碼 - 使用環境變數
        "N9t1kY3x": "os.getenv('CMONEY_PASSWORD')",
        "m7C1lR4t": "os.getenv('CMONEY_PASSWORD_201')",
        "x2U9nW5p": "os.getenv('CMONEY_PASSWORD_202')",
        "k8D2mN5v": "os.getenv('CMONEY_PASSWORD_203')",
        "p9E3nO6w": "os.getenv('CMONEY_PASSWORD_204')",
        "q0F4oP7x": "os.getenv('CMONEY_PASSWORD_205')",
        "r1G5pQ8y": "os.getenv('CMONEY_PASSWORD_206')",
        "s2H6qR9z": "os.getenv('CMONEY_PASSWORD_207')",
        "t3I7rS0a": "os.getenv('CMONEY_PASSWORD_208')",
        "u4J8sT1b": "os.getenv('CMONEY_PASSWORD_209')",
        "v5K9tU2c": "os.getenv('CMONEY_PASSWORD_210')",
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
        "replace_hardcoded_sheets_id.py",  # 排除腳本本身
        "fix_all_hardcoded_secrets.py"      # 排除腳本本身
    ]
    
    filtered_files = []
    for file_path in python_files:
        if not any(pattern in file_path for pattern in exclude_patterns):
            filtered_files.append(file_path)
    
    print(f"找到 {len(filtered_files)} 個 Python 文件需要檢查")
    
    total_replaced = 0
    
    for file_path in filtered_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_modified = False
            
            # 檢查是否包含任何硬編碼的敏感信息
            for old_value, new_value in replacements.items():
                if old_value in content:
                    print(f"處理文件: {file_path}")
                    
                    # 替換硬編碼的值
                    if old_value == "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s":
                        # 特殊處理 Google Sheets ID
                        content = content.replace(
                            f'spreadsheet_id="{old_value}"',
                            f'spreadsheet_id={new_value}'
                        )
                        content = content.replace(
                            f"spreadsheet_id='{old_value}'",
                            f"spreadsheet_id={new_value}"
                        )
                        content = content.replace(
                            f'self.spreadsheet_id = "{old_value}"',
                            f'self.spreadsheet_id = {new_value}'
                        )
                        content = content.replace(
                            f"self.spreadsheet_id = '{old_value}'",
                            f"self.spreadsheet_id = {new_value}"
                        )
                        content = content.replace(
                            f'env["GOOGLE_SHEETS_ID"] = "{old_value}"',
                            f'env["GOOGLE_SHEETS_ID"] = {new_value}'
                        )
                        content = content.replace(
                            f"env['GOOGLE_SHEETS_ID'] = '{old_value}'",
                            f"env['GOOGLE_SHEETS_ID'] = {new_value}"
                        )
                    else:
                        # 處理密碼
                        content = content.replace(
                            f"password='{old_value}'",
                            f"password={new_value}"
                        )
                        content = content.replace(
                            f'password="{old_value}"',
                            f'password={new_value}'
                        )
                        content = content.replace(
                            f'"password": "{old_value}"',
                            f'"password": {new_value}'
                        )
                        content = content.replace(
                            f"'password': '{old_value}'",
                            f"'password': {new_value}"
                        )
                    
                    file_modified = True
            
            # 如果內容有變化，寫回文件
            if file_modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                total_replaced += 1
                print(f"  ✅ 已更新: {file_path}")
                
        except Exception as e:
            print(f"  ❌ 處理文件 {file_path} 時出錯: {e}")
    
    print(f"\n總共更新了 {total_replaced} 個文件")

if __name__ == "__main__":
    fix_all_hardcoded_secrets()



