"""
安全檢查腳本 - 檢查是否有硬編碼的 API keys 和密碼
"""
import os
import re
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityChecker:
    """安全檢查器"""
    
    def __init__(self):
        self.suspicious_patterns = [
            # API Keys
            r'sk-proj-[a-zA-Z0-9\-_]{48,}',  # OpenAI API key
            r'[a-f0-9]{32,}',  # Generic API key (hex)
            r'[A-Za-z0-9]{20,}',  # Generic API key (alphanumeric)
            
            # Passwords
            r'password\s*=\s*[\'"][^\'"]{3,}[\'"]',  # password = "xxx" (3+ chars)
            r'password\s*:\s*[\'"][^\'"]{3,}[\'"]',  # password: "xxx" (3+ chars)
            
            # Email with password
            r'email\s*=\s*[\'"]\w+@\w+\.\w+[\'"]\s*,\s*password\s*=\s*[\'"][^\'"]+[\'"]',
            
            # Database credentials
            r'postgres://[^@]+@[^/]+/[^\s\'"]+',  # PostgreSQL URL
            r'mysql://[^@]+@[^/]+/[^\s\'"]+',     # MySQL URL
            
            # Hardcoded credentials
            r'LoginCredentials\([^)]*password\s*=\s*[\'"][^\'"]+[\'"]',
        ]
        
        self.safe_patterns = [
            r'os\.getenv\(',  # Environment variable usage
            r'os\.environ\[',  # Environment variable usage
            r'\.env',  # .env file reference
            r'password\s*=\s*[\'"]password[\'"]',  # Default placeholder
            r'password\s*=\s*[\'"]your-.*-here[\'"]',  # Template placeholder
        ]
    
    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """檢查單個文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # 跳過註釋行
                    if line.strip().startswith('#'):
                        continue
                    
                    # 檢查是否包含可疑模式
                    for pattern in self.suspicious_patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            # 檢查是否為安全模式
                            is_safe = any(re.search(safe_pattern, line, re.IGNORECASE) 
                                        for safe_pattern in self.safe_patterns)
                            
                            if not is_safe:
                                issues.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'content': line.strip(),
                                    'pattern': pattern,
                                    'match': match.group(),
                                    'severity': self._get_severity(pattern)
                                })
        
        except Exception as e:
            logger.error(f"檢查文件 {file_path} 時出錯: {e}")
        
        return issues
    
    def _get_severity(self, pattern: str) -> str:
        """獲取問題嚴重程度"""
        if 'sk-proj-' in pattern:
            return 'CRITICAL'
        elif 'password' in pattern:
            return 'HIGH'
        elif 'api' in pattern.lower():
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def check_directory(self, directory: str) -> List[Dict[str, Any]]:
        """檢查目錄中的所有 Python 文件"""
        all_issues = []
        
        for root, dirs, files in os.walk(directory):
            # 跳過某些目錄
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    issues = self.check_file(file_path)
                    all_issues.extend(issues)
        
        return all_issues
    
    def generate_report(self, issues: List[Dict[str, Any]]) -> str:
        """生成安全檢查報告"""
        if not issues:
            return "✅ 安全檢查通過！沒有發現硬編碼的 API keys 或密碼。"
        
        report = []
        report.append("🔍 安全檢查報告")
        report.append("=" * 50)
        
        # 按嚴重程度分組
        critical_issues = [i for i in issues if i['severity'] == 'CRITICAL']
        high_issues = [i for i in issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in issues if i['severity'] == 'MEDIUM']
        low_issues = [i for i in issues if i['severity'] == 'LOW']
        
        if critical_issues:
            report.append(f"\n🚨 CRITICAL 問題 ({len(critical_issues)} 個):")
            for issue in critical_issues:
                report.append(f"  📁 {issue['file']}:{issue['line']}")
                report.append(f"     🔍 匹配: {issue['match']}")
                report.append(f"     📝 內容: {issue['content']}")
                report.append("")
        
        if high_issues:
            report.append(f"\n⚠️ HIGH 問題 ({len(high_issues)} 個):")
            for issue in high_issues:
                report.append(f"  📁 {issue['file']}:{issue['line']}")
                report.append(f"     🔍 匹配: {issue['match']}")
                report.append(f"     📝 內容: {issue['content']}")
                report.append("")
        
        if medium_issues:
            report.append(f"\n📋 MEDIUM 問題 ({len(medium_issues)} 個):")
            for issue in medium_issues:
                report.append(f"  📁 {issue['file']}:{issue['line']}")
                report.append(f"     🔍 匹配: {issue['match']}")
                report.append(f"     📝 內容: {issue['content']}")
                report.append("")
        
        if low_issues:
            report.append(f"\n📝 LOW 問題 ({len(low_issues)} 個):")
            for issue in low_issues:
                report.append(f"  📁 {issue['file']}:{issue['line']}")
                report.append(f"     🔍 匹配: {issue['match']}")
                report.append(f"     📝 內容: {issue['content']}")
                report.append("")
        
        # 總結
        report.append("=" * 50)
        report.append(f"📊 總結:")
        report.append(f"   🚨 CRITICAL: {len(critical_issues)} 個")
        report.append(f"   ⚠️ HIGH: {len(high_issues)} 個")
        report.append(f"   📋 MEDIUM: {len(medium_issues)} 個")
        report.append(f"   📝 LOW: {len(low_issues)} 個")
        report.append(f"   📈 總計: {len(issues)} 個問題")
        
        if critical_issues or high_issues:
            report.append("\n🚨 建議立即修復 CRITICAL 和 HIGH 級別的問題！")
            report.append("💡 請將所有 API keys 和密碼移到 .env 文件中。")
        
        return "\n".join(report)

def main():
    """主函數"""
    checker = SecurityChecker()
    
    # 檢查當前目錄
    current_dir = os.getcwd()
    logger.info(f"🔍 開始檢查目錄: {current_dir}")
    
    issues = checker.check_directory(current_dir)
    report = checker.generate_report(issues)
    
    print(report)
    
    # 如果有嚴重問題，返回非零退出碼
    critical_issues = [i for i in issues if i['severity'] == 'CRITICAL']
    high_issues = [i for i in issues if i['severity'] == 'HIGH']
    
    if critical_issues or high_issues:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    main()
