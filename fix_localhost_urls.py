#!/usr/bin/env python3
"""
Script to fix hardcoded localhost:8001 URLs in frontend files.
Replaces http://localhost:8001 with proper template string ${getApiBaseUrl()}
and adds necessary imports.
"""

import re
import os

FILES_TO_FIX = [
    "docker-container/finlab python/apps/dashboard-frontend/src/components/Dashboard/InteractionAnalysis.tsx",
    "docker-container/finlab python/apps/dashboard-frontend/src/components/Dashboard/InteractionAnalysisPage.tsx",
    "docker-container/finlab python/apps/dashboard-frontend/src/components/KOL/KOLManagementPage.tsx",
    "docker-container/finlab python/apps/dashboard-frontend/src/components/PostingManagement/BatchHistory/BatchHistoryPage.tsx",
    "docker-container/finlab python/apps/dashboard-frontend/src/components/PostingManagement/PostingGenerator/TrendingTopicsDisplay.tsx",
    "docker-container/finlab python/apps/dashboard-frontend/src/pages/InteractionAnalysisPage.tsx",
    "docker-container/finlab python/apps/dashboard-frontend/src/pages/PerformanceAnalysisPage.tsx",
    "docker-container/finlab python/apps/dashboard-frontend/src/pages/SelfLearningPage.tsx",
]

def fix_file(filepath):
    """Fix localhost URLs in a single file."""
    print(f"Processing: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file needs fixing
    if 'localhost:8001' not in content:
        print(f"  ✅ No localhost URLs found, skipping")
        return False

    original_content = content

    # Add import if not present
    if 'getApiBaseUrl' not in content:
        # Find the last import statement
        import_pattern = r"(import [^;]+;)"
        imports = list(re.finditer(import_pattern, content, re.MULTILINE))
        if imports:
            last_import = imports[-1]
            insert_pos = last_import.end()
            import_statement = "\nimport { getApiBaseUrl } from '../../../config/api';"

            # Adjust path based on file location
            if '/pages/' in filepath:
                import_statement = "\nimport { getApiBaseUrl } from '../config/api';"
            elif '/components/Dashboard/' in filepath:
                import_statement = "\nimport { getApiBaseUrl } from '../../config/api';"
            elif '/components/KOL/' in filepath:
                import_statement = "\nimport { getApiBaseUrl } from '../../config/api';"
            elif '/components/PostingManagement/BatchHistory/' in filepath:
                import_statement = "\nimport { getApiBaseUrl } from '../../../config/api';"
            elif '/components/PostingManagement/PostingGenerator/' in filepath:
                import_statement = "\nimport { getApiBaseUrl } from '../../../config/api';"

            content = content[:insert_pos] + import_statement + content[insert_pos:]
            print(f"  ✅ Added import statement")

    # Add API_BASE_URL constant after imports
    if 'const API_BASE_URL' not in content:
        # Find where to insert (after imports, before first function/const)
        pattern = r"(import [^;]+;\s*\n+)"
        matches = list(re.finditer(pattern, content))
        if matches:
            last_match = matches[-1]
            insert_pos = last_match.end()
            constant_def = "\nconst API_BASE_URL = getApiBaseUrl();\n"
            content = content[:insert_pos] + constant_def + content[insert_pos:]
            print(f"  ✅ Added API_BASE_URL constant")

    # Replace all localhost URLs
    # Pattern 1: 'http://localhost:8001...' -> `${API_BASE_URL}...`
    content = re.sub(
        r"'http://localhost:8001([^']*)'",
        r"`${API_BASE_URL}\1`",
        content
    )

    # Pattern 2: "http://localhost:8001..." -> `${API_BASE_URL}...`
    content = re.sub(
        r'"http://localhost:8001([^"]*)"',
        r'`${API_BASE_URL}\1`',
        content
    )

    # Pattern 3: `http://localhost:8001...` -> `${API_BASE_URL}...`
    content = re.sub(
        r'`http://localhost:8001([^`]*)`',
        r'`${API_BASE_URL}\1`',
        content
    )

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Fixed and saved")
        return True
    else:
        print(f"  ⚠️  No changes made")
        return False

def main():
    fixed_count = 0
    for filepath in FILES_TO_FIX:
        if os.path.exists(filepath):
            if fix_file(filepath):
                fixed_count += 1
        else:
            print(f"❌ File not found: {filepath}")

    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
