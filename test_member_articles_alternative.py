"""
測試其他方式獲取Member文章列表
包括GraphQL、不同的API端點等
"""

import asyncio
import sys
import os
import httpx
import json
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

class MemberArticlesAlternativeExplorer:
    """Member文章替代方案探索器"""
    
    def __init__(self):
        self.cmoney_client = CMoneyClient()
        self.access_token = None
    
    async def login(self):
        """登入獲取token"""
        try:
            credentials = LoginCredentials(
                email='forum_200@cmoney.com.tw',
                password='N9t1kY3x'
            )
            
            login_result = await self.cmoney_client.login(credentials)
            if login_result and not login_result.is_expired:
                self.access_token = login_result.token
                print(f"✅ 登入成功，Token: {self.access_token[:20]}...")
                return True
            else:
                print("❌ 登入失敗")
                return False
        except Exception as e:
            print(f"❌ 登入失敗: {e}")
            return False
    
    async def test_graphql_endpoints(self, member_id: str):
        """測試GraphQL端點"""
        if not self.access_token:
            print("❌ 請先登入")
            return
        
        print(f"\n🔍 測試GraphQL端點")
        print(f"Member ID: {member_id}")
        print("-" * 50)
        
        # GraphQL查詢
        graphql_queries = [
            {
                "name": "獲取用戶文章",
                "query": """
                query GetUserArticles($memberId: String!) {
                    user(id: $memberId) {
                        articles {
                            id
                            title
                            content
                            createdAt
                        }
                    }
                }
                """,
                "variables": {"memberId": member_id}
            },
            {
                "name": "獲取會員文章",
                "query": """
                query GetMemberArticles($memberId: String!) {
                    member(id: $memberId) {
                        posts {
                            id
                            title
                            text
                            createTime
                        }
                    }
                }
                """,
                "variables": {"memberId": member_id}
            },
            {
                "name": "獲取作者內容",
                "query": """
                query GetAuthorContent($authorId: String!) {
                    author(id: $authorId) {
                        content {
                            id
                            title
                            body
                            publishedAt
                        }
                    }
                }
                """,
                "variables": {"authorId": member_id}
            }
        ]
        
        # 可能的GraphQL端點
        graphql_endpoints = [
            "https://social.cmoney.tw/profile/graphql",
            "https://forumservice.cmoney.tw/graphql",
            "https://api.cmoney.tw/graphql",
            "https://social.cmoney.tw/graphql",
            "https://forumservice.cmoney.tw/api/graphql",
            "https://api.cmoney.tw/api/graphql",
            "https://social.cmoney.tw/api/graphql",
        ]
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in graphql_endpoints:
                print(f"\n📝 測試GraphQL端點: {endpoint}")
                
                for query_info in graphql_queries:
                    print(f"  - 查詢: {query_info['name']}")
                    
                    payload = {
                        "query": query_info["query"],
                        "variables": query_info["variables"]
                    }
                    
                    try:
                        response = await client.post(endpoint, headers=headers, json=payload)
                        print(f"    狀態碼: {response.status_code}")
                        
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                if "data" in data and data["data"]:
                                    print("    ✅ 成功！有數據返回")
                                    print(f"    數據: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                                elif "errors" in data:
                                    print(f"    ⚠️ GraphQL錯誤: {data['errors']}")
                                else:
                                    print("    ℹ️ 無數據返回")
                            except:
                                print("    響應不是JSON格式")
                        else:
                            print(f"    ❌ 錯誤: {response.status_code}")
                            
                    except Exception as e:
                        print(f"    ❌ 請求失敗: {e}")
                    
                    await asyncio.sleep(0.5)
    
    async def test_alternative_endpoints(self, member_id: str):
        """測試其他可能的端點"""
        if not self.access_token:
            print("❌ 請先登入")
            return
        
        print(f"\n🔍 測試其他可能的端點")
        print(f"Member ID: {member_id}")
        print("-" * 50)
        
        # 其他可能的端點
        alternative_endpoints = [
            f"/api/Article/Recent?memberId={member_id}",
            f"/api/Article/Recent?author={member_id}",
            f"/api/Article/Recent?userId={member_id}",
            f"/api/Article/Recent?member={member_id}",
            f"/api/Article/Latest?memberId={member_id}",
            f"/api/Article/Latest?author={member_id}",
            f"/api/Article/Latest?userId={member_id}",
            f"/api/Article/Latest?member={member_id}",
            f"/api/Article/History?memberId={member_id}",
            f"/api/Article/History?author={member_id}",
            f"/api/Article/History?userId={member_id}",
            f"/api/Article/History?member={member_id}",
            f"/api/Article/Feed?memberId={member_id}",
            f"/api/Article/Feed?author={member_id}",
            f"/api/Article/Feed?userId={member_id}",
            f"/api/Article/Feed?member={member_id}",
            f"/api/Article/Timeline?memberId={member_id}",
            f"/api/Article/Timeline?author={member_id}",
            f"/api/Article/Timeline?userId={member_id}",
            f"/api/Article/Timeline?member={member_id}",
            f"/api/Article/Archive?memberId={member_id}",
            f"/api/Article/Archive?author={member_id}",
            f"/api/Article/Archive?userId={member_id}",
            f"/api/Article/Archive?member={member_id}",
            f"/api/Article/Collection?memberId={member_id}",
            f"/api/Article/Collection?author={member_id}",
            f"/api/Article/Collection?userId={member_id}",
            f"/api/Article/Collection?member={member_id}",
            f"/api/Article/Portfolio?memberId={member_id}",
            f"/api/Article/Portfolio?author={member_id}",
            f"/api/Article/Portfolio?userId={member_id}",
            f"/api/Article/Portfolio?member={member_id}",
        ]
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Version": "2.0",
            "cmoneyapi-trace-context": "member-articles-alternative",
            "accept": "application/json"
        }
        
        successful_endpoints = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for i, endpoint in enumerate(alternative_endpoints, 1):
                url = f"{self.cmoney_client.api_base_url}{endpoint}"
                print(f"\n{i:2d}. 測試: {endpoint}")
                print(f"    URL: {url}")
                
                try:
                    response = await client.get(url, headers=headers)
                    print(f"    狀態碼: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("    ✅ 成功！")
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                keys = list(data.keys())[:10]
                                print(f"    響應欄位: {keys}{'...' if len(data) > 10 else ''}")
                                
                                # 檢查是否包含文章數據
                                if any(key in data for key in ['articles', 'posts', 'content', 'data', 'items', 'results']):
                                    print("    🎯 可能包含文章數據！")
                                    successful_endpoints.append({
                                        'endpoint': endpoint,
                                        'url': url,
                                        'status_code': response.status_code,
                                        'data': data
                                    })
                            elif isinstance(data, list):
                                print(f"    響應類型: 陣列，長度: {len(data)}")
                                if len(data) > 0:
                                    print("    🎯 可能包含文章數據！")
                                    successful_endpoints.append({
                                        'endpoint': endpoint,
                                        'url': url,
                                        'status_code': response.status_code,
                                        'data': data
                                    })
                        except:
                            print("    響應不是JSON格式")
                    elif response.status_code == 404:
                        print("    ❌ 404 - 端點不存在")
                    elif response.status_code == 400:
                        print("    ❌ 400 - 請求參數錯誤")
                    else:
                        print(f"    ❌ 其他錯誤: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ 請求失敗: {e}")
                
                # 添加延遲避免API限制
                await asyncio.sleep(0.2)
        
        return successful_endpoints
    
    async def test_member_info_with_articles(self, member_id: str):
        """測試Member Info API是否包含文章信息"""
        if not self.access_token:
            print("❌ 請先登入")
            return
        
        print(f"\n🔍 詳細分析Member Info API")
        print(f"Member ID: {member_id}")
        print("-" * 50)
        
        try:
            # 使用現有的get_member_info方法
            members = await self.cmoney_client.get_member_info(self.access_token, [member_id])
            
            if members:
                member = members[0]
                print(f"✅ 會員資訊:")
                print(f"  - Member ID: {member.member_id}")
                print(f"  - 暱稱: {member.nickname}")
                print(f"  - 文章數: {member.article_count}")
                
                if member.raw_data:
                    print(f"\n📊 原始數據詳細分析:")
                    for key, value in member.raw_data.items():
                        print(f"  - {key}: {value}")
                    
                    # 檢查是否有文章相關的詳細信息
                    if 'totalCountArticle' in member.raw_data:
                        article_count = member.raw_data['totalCountArticle']
                        print(f"\n📝 文章統計:")
                        print(f"  - 總文章數: {article_count}")
                        
                        if article_count > 0:
                            print(f"  - 該會員有 {article_count} 篇文章")
                            print(f"  - 但API沒有提供文章列表")
                            print(f"  - 需要其他方式獲取文章列表")
            else:
                print("❌ 未找到會員資訊")
                
        except Exception as e:
            print(f"❌ 獲取會員資訊失敗: {e}")

async def main():
    """主函數"""
    print("🧪 Member文章替代方案探索工具")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    explorer = MemberArticlesAlternativeExplorer()
    
    # 登入
    if not await explorer.login():
        return
    
    # 測試的Member ID
    test_member_id = "961964"
    
    print(f"\n{'='*60}")
    print(f"🎯 測試Member ID: {test_member_id}")
    print(f"{'='*60}")
    
    # 1. 詳細分析Member Info API
    await explorer.test_member_info_with_articles(test_member_id)
    
    # 2. 測試GraphQL端點
    await explorer.test_graphql_endpoints(test_member_id)
    
    # 3. 測試其他可能的端點
    successful_endpoints = await explorer.test_alternative_endpoints(test_member_id)
    
    # 顯示結果
    print(f"\n📊 探索結果摘要:")
    if successful_endpoints:
        print(f"✅ 找到 {len(successful_endpoints)} 個可能的端點:")
        for endpoint_info in successful_endpoints:
            print(f"  - {endpoint_info['endpoint']}")
    else:
        print("❌ 未找到可用的文章列表API端點")
        print("\n💡 建議:")
        print("1. CMoney API可能沒有提供member文章列表的端點")
        print("2. 可能需要通過其他方式獲取，如:")
        print("   - 爬蟲抓取")
        print("   - 第三方API")
        print("   - 數據庫直接查詢")
        print("3. 或者需要聯繫CMoney技術支援確認是否有此功能")
    
    print(f"\n✅ 探索完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

























