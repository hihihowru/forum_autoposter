"""
測試Article ID互動數據抓取功能
確認指定的article ID是否可以成功獲取互動數據
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient

class ArticleInteractionTester:
    """Article ID互動數據測試器"""
    
    def __init__(self):
        self.cmoney_client = CMoneyClient()
        self.sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
    
    async def test_article_interaction(self, article_id: str, kol_credentials: Optional[LoginCredentials] = None) -> Dict[str, Any]:
        """
        測試指定Article ID的互動數據抓取
        
        Args:
            article_id: 文章ID
            kol_credentials: KOL登入憑證，如果為None則使用預設憑證
            
        Returns:
            測試結果字典
        """
        result = {
            "article_id": article_id,
            "test_time": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "interaction_data": None,
            "api_endpoint": f"{self.cmoney_client.api_base_url}/api/Article/{article_id}",
            "raw_response": None
        }
        
        try:
            print(f"🔍 測試Article ID: {article_id}")
            print(f"🔗 API端點: {result['api_endpoint']}")
            
            # 使用預設憑證或提供的憑證
            if kol_credentials is None:
                # 使用川川哥的憑證作為預設
                kol_credentials = LoginCredentials(
                    email='forum_200@cmoney.com.tw',
                    password='N9t1kY3x'
                )
                print(f"🔐 使用預設憑證: {kol_credentials.email}")
            else:
                print(f"🔐 使用提供憑證: {kol_credentials.email}")
            
            # 1. 登入獲取token
            print("📝 步驟1: 登入CMoney...")
            login_result = await self.cmoney_client.login(kol_credentials)
            
            if not login_result or login_result.is_expired:
                result["error"] = f"登入失敗或Token已過期"
                print(f"❌ {result['error']}")
                return result
            
            print(f"✅ 登入成功，Token: {login_result.token[:20]}...")
            
            # 2. 獲取互動數據
            print("📝 步驟2: 獲取互動數據...")
            interaction_data = await self.cmoney_client.get_article_interactions(
                login_result.token, 
                article_id
            )
            
            # 3. 分析結果
            if interaction_data:
                result["success"] = True
                result["interaction_data"] = {
                    "post_id": interaction_data.post_id,
                    "member_id": interaction_data.member_id,
                    "likes": interaction_data.likes,
                    "comments": interaction_data.comments,
                    "shares": interaction_data.shares,
                    "views": interaction_data.views,
                    "engagement_rate": interaction_data.engagement_rate,
                    "raw_data_keys": list(interaction_data.raw_data.keys()) if interaction_data.raw_data else []
                }
                
                # 保存原始響應
                result["raw_response"] = interaction_data.raw_data
                
                print("✅ 成功獲取互動數據:")
                print(f"  - 文章ID: {interaction_data.post_id}")
                print(f"  - 會員ID: {interaction_data.member_id}")
                print(f"  - 讚數: {interaction_data.likes}")
                print(f"  - 留言數: {interaction_data.comments}")
                print(f"  - 分享數: {interaction_data.shares}")
                print(f"  - 瀏覽數: {interaction_data.views}")
                print(f"  - 互動率: {interaction_data.engagement_rate}")
                
                # 顯示原始數據中的關鍵欄位
                if interaction_data.raw_data:
                    key_fields = ["commentCount", "interestedCount", "collectedCount", "emojiCount", "viewCount"]
                    print("📊 原始數據關鍵欄位:")
                    for field in key_fields:
                        if field in interaction_data.raw_data:
                            print(f"  - {field}: {interaction_data.raw_data[field]}")
            else:
                result["error"] = "獲取互動數據失敗，返回None"
                print(f"❌ {result['error']}")
                
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 測試失敗: {e}")
        
        return result
    
    async def test_multiple_articles(self, article_ids: List[str], kol_credentials: Optional[LoginCredentials] = None) -> List[Dict[str, Any]]:
        """
        測試多個Article ID的互動數據抓取
        
        Args:
            article_ids: 文章ID列表
            kol_credentials: KOL登入憑證
            
        Returns:
            測試結果列表
        """
        results = []
        
        print(f"🚀 開始測試 {len(article_ids)} 個Article ID")
        print("=" * 60)
        
        for i, article_id in enumerate(article_ids, 1):
            print(f"\n📝 測試 {i}/{len(article_ids)}: {article_id}")
            print("-" * 40)
            
            result = await self.test_article_interaction(article_id, kol_credentials)
            results.append(result)
            
            # 添加延遲避免API限制
            if i < len(article_ids):
                await asyncio.sleep(1)
        
        return results
    
    async def get_kol_credentials_from_sheets(self, kol_serial: str) -> Optional[LoginCredentials]:
        """
        從Google Sheets獲取指定KOL的登入憑證
        
        Args:
            kol_serial: KOL序號
            
        Returns:
            KOL登入憑證或None
        """
        try:
            print(f"📖 從Google Sheets獲取KOL {kol_serial}的憑證...")
            
            # 讀取KOL配置
            kol_data = self.sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            
            if len(kol_data) < 2:
                print("❌ 沒有找到KOL數據")
                return None
            
            headers = kol_data[0]
            rows = kol_data[1:]
            
            # 找到Email和密碼欄位索引
            email_idx = None
            password_idx = None
            
            for i, header in enumerate(headers):
                if 'Email' in header or '帳號' in header:
                    email_idx = i
                elif '密碼' in header:
                    password_idx = i
            
            if email_idx is None or password_idx is None:
                print("❌ 找不到Email或密碼欄位")
                return None
            
            # 查找指定序號的KOL
            for row in rows:
                if len(row) > 0 and row[0] == kol_serial:
                    email = row[email_idx] if len(row) > email_idx else None
                    password = row[password_idx] if len(row) > password_idx else None
                    
                    if email and password:
                        print(f"✅ 找到KOL憑證: {email}")
                        return LoginCredentials(email=email, password=password)
            
            print(f"❌ 找不到序號為 {kol_serial} 的KOL")
            return None
            
        except Exception as e:
            print(f"❌ 獲取KOL憑證失敗: {e}")
            return None
    
    def analyze_test_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析測試結果
        
        Args:
            results: 測試結果列表
            
        Returns:
            分析結果
        """
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        failed_tests = total_tests - successful_tests
        
        analysis = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "successful_article_ids": [r["article_id"] for r in results if r["success"]],
            "failed_article_ids": [r["article_id"] for r in results if not r["success"]],
            "common_errors": {}
        }
        
        # 統計常見錯誤
        for result in results:
            if not result["success"] and result["error"]:
                error = result["error"]
                analysis["common_errors"][error] = analysis["common_errors"].get(error, 0) + 1
        
        return analysis

async def main():
    """主函數 - 測試Article ID互動數據抓取"""
    print("🧪 Article ID互動數據抓取測試工具")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = ArticleInteractionTester()
    
    # 測試用的Article ID列表
    test_article_ids = [
        "173337593",  # 您提供的ID
        "173337594",  # 相近的ID
        "173337595",  # 相近的ID
    ]
    
    print(f"\n📝 測試Article ID列表:")
    for i, article_id in enumerate(test_article_ids, 1):
        print(f"  {i}. {article_id}")
    
    # 選項1: 使用預設憑證測試
    print(f"\n🔧 選項1: 使用預設憑證測試")
    print("-" * 40)
    results = await tester.test_multiple_articles(test_article_ids)
    
    # 分析結果
    analysis = tester.analyze_test_results(results)
    
    print(f"\n📊 測試結果分析:")
    print(f"  - 總測試數: {analysis['total_tests']}")
    print(f"  - 成功數: {analysis['successful_tests']}")
    print(f"  - 失敗數: {analysis['failed_tests']}")
    print(f"  - 成功率: {analysis['success_rate']:.2%}")
    
    if analysis['successful_article_ids']:
        print(f"  - 成功的Article ID: {analysis['successful_article_ids']}")
    
    if analysis['failed_article_ids']:
        print(f"  - 失敗的Article ID: {analysis['failed_article_ids']}")
    
    if analysis['common_errors']:
        print(f"  - 常見錯誤:")
        for error, count in analysis['common_errors'].items():
            print(f"    * {error}: {count}次")
    
    # 選項2: 使用特定KOL憑證測試
    print(f"\n🔧 選項2: 使用特定KOL憑證測試")
    print("-" * 40)
    
    # 獲取川川哥的憑證
    kol_credentials = await tester.get_kol_credentials_from_sheets("200")
    
    if kol_credentials:
        print(f"使用KOL憑證測試單個Article ID...")
        single_result = await tester.test_article_interaction(test_article_ids[0], kol_credentials)
        
        if single_result["success"]:
            print("✅ 使用KOL憑證測試成功！")
        else:
            print(f"❌ 使用KOL憑證測試失敗: {single_result['error']}")
    else:
        print("❌ 無法獲取KOL憑證")
    
    print(f"\n✅ 測試完成！")
    print("=" * 60)
    
    # 提供使用建議
    print("💡 使用建議:")
    print("1. 如果測試成功，表示Article ID可以正常抓取互動數據")
    print("2. 如果測試失敗，請檢查:")
    print("   - Article ID是否有效")
    print("   - KOL憑證是否正確")
    print("   - CMoney API是否正常")
    print("   - 網路連接是否正常")
    print("3. 可以將此函數整合到您的系統中使用")

if __name__ == "__main__":
    asyncio.run(main())
