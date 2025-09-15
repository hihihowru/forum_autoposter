#!/usr/bin/env python3
"""
批量替換硬編碼的 Google Sheets ID 為環境變數
"""

import os
import re
import glob

def replace_hardcoded_sheets_id():
    """替換所有硬編碼的 Google Sheets ID"""
    
    # 要替換的 Google Sheets ID
    old_sheets_id = "your_old_sheets_id_here"
    
    # 查找所有 Python 文件
    python_files = glob.glob("**/*.py", recursive=True)
    
    # 排除一些不需要修改的文件
    exclude_patterns = [
        "__pycache__",
        "node_modules",
        ".git",
        "venv",
        "env",
        ".venv"
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
            
            # 檢查是否包含硬編碼的 Google Sheets ID
            if old_sheets_id in content:
                print(f"處理文件: {file_path}")
                
                # 替換硬編碼的 Google Sheets ID
                new_content = content.replace(
                    f'spreadsheet_id="{old_sheets_id}"',
                    'spreadsheet_id=os.getenv("GOOGLE_SHEETS_ID")'
                )
                new_content = new_content.replace(
                    f"spreadsheet_id='{old_sheets_id}'",
                    "spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')"
                )
                new_content = new_content.replace(
                    f'self.spreadsheet_id = "{old_sheets_id}"',
                    'self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")'
                )
                new_content = new_content.replace(
                    f"self.spreadsheet_id = '{old_sheets_id}'",
                    "self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')"
                )
                new_content = new_content.replace(
                    f'env["GOOGLE_SHEETS_ID"] = "{old_sheets_id}"',
                    'env["GOOGLE_SHEETS_ID"] = os.getenv("GOOGLE_SHEETS_ID")'
                )
                new_content = new_content.replace(
                    f"env['GOOGLE_SHEETS_ID'] = '{old_sheets_id}'",
                    "env['GOOGLE_SHEETS_ID'] = os.getenv('GOOGLE_SHEETS_ID')"
                )
                
                # 處理其他格式的硬編碼
                new_content = re.sub(
                    rf'os\.getenv\([\'"](GOOGLE_SHEETS_ID)[\'"],\s*[\'"]{old_sheets_id}[\'"]\)',
                    r'os.getenv("\1")',
                    new_content
                )
                
                # 如果內容有變化，寫回文件
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    replaced_count += 1
                    print(f"  ✅ 已更新: {file_path}")
                
        except Exception as e:
            print(f"  ❌ 處理文件 {file_path} 時出錯: {e}")
    
    print(f"\n總共更新了 {replaced_count} 個文件")

if __name__ == "__main__":
    replace_hardcoded_sheets_id()



