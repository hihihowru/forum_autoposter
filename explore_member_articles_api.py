"""
探索Member ID發文狀況的API端點
測試可能的API端點來獲取member的文章列表
"""

import asyncio
import sys
import os
import httpx
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

class MemberArticlesExplorer:
    """Member文章API探索器"""
    
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
    
    async def test_api_endpoints(self, member_id: str):
        """測試可能的API端點"""
        if not self.access_token:
            print("❌ 請先登入")
            return
        
        # 可能的API端點
        possible_endpoints = [
            f"/api/Member/{member_id}/Articles",
            f"/api/Member/{member_id}/Posts", 
            f"/api/Member/{member_id}/Content",
            f"/api/Article/Member/{member_id}",
            f"/api/Article/ByMember/{member_id}",
            f"/api/Article/List?memberId={member_id}",
            f"/api/Article/List?member={member_id}",
            f"/api/Article/Search?memberId={member_id}",
            f"/api/Article/Search?author={member_id}",
            f"/api/Article/Author/{member_id}",
            f"/api/Article/User/{member_id}",
            f"/api/Article/Profile/{member_id}",
            f"/api/Profile/{member_id}/Articles",
            f"/api/Profile/{member_id}/Posts",
            f"/api/User/{member_id}/Articles",
            f"/api/User/{member_id}/Posts",
            f"/api/Author/{member_id}/Articles",
            f"/api/Author/{member_id}/Posts",
            f"/api/Posts/Member/{member_id}",
            f"/api/Posts/Author/{member_id}",
            f"/api/Posts/User/{member_id}",
            f"/api/Content/Member/{member_id}",
            f"/api/Content/Author/{member_id}",
            f"/api/Content/User/{member_id}",
            f"/api/v1/Member/{member_id}/Articles",
            f"/api/v2/Member/{member_id}/Articles",
            f"/api/v1/Article/Member/{member_id}",
            f"/api/v2/Article/Member/{member_id}",
            f"/api/v1/Article/List?memberId={member_id}",
            f"/api/v2/Article/List?memberId={member_id}",
        ]
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Version": "2.0",
            "cmoneyapi-trace-context": "member-articles-explorer",
            "accept": "application/json"
        }
        
        print(f"🔍 測試Member ID: {member_id}")
        print(f"📝 測試 {len(possible_endpoints)} 個可能的API端點")
        print("=" * 80)
        
        successful_endpoints = []
        failed_endpoints = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for i, endpoint in enumerate(possible_endpoints, 1):
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
                        failed_endpoints.append({'endpoint': endpoint, 'status_code': 404})
                    elif response.status_code == 401:
                        print("    ❌ 401 - 需要認證")
                        failed_endpoints.append({'endpoint': endpoint, 'status_code': 401})
                    elif response.status_code == 403:
                        print("    ❌ 403 - 權限不足")
                        failed_endpoints.append({'endpoint': endpoint, 'status_code': 403})
                    else:
                        print(f"    ❌ 其他錯誤: {response.status_code}")
                        failed_endpoints.append({'endpoint': endpoint, 'status_code': response.status_code})
                        
                except Exception as e:
                    print(f"    ❌ 請求失敗: {e}")
                    failed_endpoints.append({'endpoint': endpoint, 'error': str(e)})
                
                # 添加延遲避免API限制
                await asyncio.sleep(0.2)
        
        # 顯示結果摘要
        print(f"\n📊 測試結果摘要:")
        print(f"  - 總測試數: {len(possible_endpoints)}")
        print(f"  - 成功數: {len(successful_endpoints)}")
        print(f"  - 失敗數: {len(failed_endpoints)}")
        
        if successful_endpoints:
            print(f"\n✅ 成功的端點:")
            for endpoint_info in successful_endpoints:
                print(f"  - {endpoint_info['endpoint']} (狀態碼: {endpoint_info['status_code']})")
        
        return successful_endpoints, failed_endpoints
    
    async def test_member_info_api(self, member_id: str):
        """測試現有的Member Info API"""
        if not self.access_token:
            print("❌ 請先登入")
            return
        
        print(f"\n🔍 測試現有的Member Info API")
        print(f"Member ID: {member_id}")
        print("-" * 50)
        
        try:
            # 使用現有的get_member_info方法
            members = await self.cmoney_client.get_member_info(self.access_token, [member_id])
            
            if members:
                member = members[0]
                print(f"✅ 成功獲取會員資訊:")
                print(f"  - Member ID: {member.member_id}")
                print(f"  - 暱稱: {member.nickname}")
                print(f"  - 頭像URL: {member.avatar_url}")
                print(f"  - 粉絲數: {member.follower_count}")
                print(f"  - 關注數: {member.following_count}")
                print(f"  - 文章數: {member.article_count}")
                
                if member.raw_data:
                    print(f"  - 原始數據欄位: {list(member.raw_data.keys())}")
                    
                    # 檢查是否有文章相關的欄位
                    article_related_fields = [k for k in member.raw_data.keys() if 'article' in k.lower() or 'post' in k.lower()]
                    if article_related_fields:
                        print(f"  - 文章相關欄位: {article_related_fields}")
            else:
                print("❌ 未找到會員資訊")
                
        except Exception as e:
            print(f"❌ 獲取會員資訊失敗: {e}")

async def main():
    """主函數"""
    print("🧪 Member文章API探索工具")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    explorer = MemberArticlesExplorer()
    
    # 登入
    if not await explorer.login():
        return
    
    # 測試的Member ID (使用之前測試中發現的member ID)
    test_member_ids = ["961964", "16223867"]
    
    for member_id in test_member_ids:
        print(f"\n{'='*60}")
        print(f"🎯 測試Member ID: {member_id}")
        print(f"{'='*60}")
        
        # 1. 測試現有的Member Info API
        await explorer.test_member_info_api(member_id)
        
        # 2. 探索可能的文章API端點
        successful_endpoints, failed_endpoints = await explorer.test_api_endpoints(member_id)
        
        if successful_endpoints:
            print(f"\n🎉 找到 {len(successful_endpoints)} 個可能的文章API端點！")
            for endpoint_info in successful_endpoints:
                print(f"  ✅ {endpoint_info['endpoint']}")
        else:
            print(f"\n😞 未找到可用的文章API端點")
    
    print(f"\n✅ 探索完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

























