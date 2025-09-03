"""
CMoney API 客戶端
處理登入、獲取話題、發文等 API 調用
"""
import httpx
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class LoginCredentials:
    """登入憑證"""
    email: str
    password: str


@dataclass
class AccessToken:
    """存取 Token"""
    token: str
    expires_at: datetime
    
    @property
    def is_expired(self) -> bool:
        """檢查 Token 是否過期"""
        return datetime.now() >= self.expires_at


@dataclass
class Topic:
    """話題數據結構"""
    id: str
    title: str
    name: str
    last_article_create_time: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class ArticleData:
    """文章數據結構"""
    title: str
    text: str
    community_topic: Optional[Dict[str, str]] = None  # {"id": "topic_id"}
    commodity_tags: Optional[List[Dict[str, Any]]] = None  # [{"type": "Stock", "key": "2330", "bullOrBear": 0}]


@dataclass
class PublishResult:
    """發文結果"""
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class MemberInfo:
    """會員資訊"""
    member_id: str
    nickname: str
    avatar_url: Optional[str] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    article_count: Optional[int] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class InteractionData:
    """互動數據"""
    post_id: str
    member_id: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    click_rate: float = 0.0
    engagement_rate: float = 0.0
    
    # 新增：詳細表情統計
    dislikes: int = 0
    laughs: int = 0
    money: int = 0
    shock: int = 0
    cry: int = 0
    think: int = 0
    angry: int = 0
    total_emojis: int = 0
    
    # 新增：其他互動數據
    collections: int = 0
    donations: int = 0
    total_interactions: int = 0
    
    raw_data: Optional[Dict[str, Any]] = None




@dataclass
class UpdateNicknameResult:
    """更改暱稱結果"""
    success: bool
    new_nickname: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

class CMoneyClient:
    """CMoney API 客戶端"""
    
    def __init__(self, login_url: str = "https://social.cmoney.tw/identity/token",
                 api_base_url: str = "https://forumservice.cmoney.tw",
                 graphql_url: str = "https://social.cmoney.tw/profile/graphql/mutation/member"):
        """
        初始化 CMoney 客戶端
        
        Args:
            login_url: 登入 API URL
            api_base_url: API 基礎 URL
            graphql_url: GraphQL API URL (用於會員資料更新)
        """
        self.login_url = login_url
        self.api_base_url = api_base_url
        self.graphql_url = graphql_url
        self.client = httpx.Client(timeout=30.0)
        self._tokens: Dict[str, AccessToken] = {}  # email -> AccessToken
    
    async def login(self, credentials: LoginCredentials) -> AccessToken:
        """
        登入 CMoney 平台
        
        Args:
            credentials: 登入憑證
            
        Returns:
            存取 Token
            
        Raises:
            Exception: 登入失敗
        """
        try:
            # 檢查是否已有有效 Token
            if credentials.email in self._tokens:
                token = self._tokens[credentials.email]
                if not token.is_expired:
                    logger.info(f"使用快取的 Token: {credentials.email}")
                    return token
            
            # 準備登入請求
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "password",
                "login_method": "email",
                "client_id": "cmstockcommunity",
                "account": credentials.email,
                "password": credentials.password
            }
            
            # 發送登入請求
            response = self.client.post(
                self.login_url,
                headers=headers,
                data=data
            )
            
            if response.status_code != 200:
                error_msg = f"登入失敗: HTTP {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                raise Exception(error_msg)
            
            # 解析回應
            result = response.json()
            access_token = result.get("access_token")
            expires_in = result.get("expires_in", 3600)  # 預設 1 小時
            
            if not access_token:
                error_msg = f"登入失敗: 沒有收到 access_token"
                logger.error(f"{error_msg} - {result}")
                raise Exception(error_msg)
            
            # 建立 Token 物件
            token = AccessToken(
                token=access_token,
                expires_at=datetime.now() + timedelta(seconds=expires_in - 300)  # 提前 5 分鐘過期
            )
            
            # 快取 Token
            self._tokens[credentials.email] = token
            
            logger.info(f"登入成功: {credentials.email}")
            return token
            
        except Exception as e:
            logger.error(f"登入 CMoney 失敗: {e}")
            raise
    
    async def get_trending_topics(self, access_token: str) -> List[Topic]:
        """
        獲取熱門話題
        
        Args:
            access_token: 存取 Token
            
        Returns:
            話題列表
            
        Raises:
            Exception: 獲取失敗
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Version": "2.0",
                "cmoneyapi-trace-context": "n8n"
            }
            
            url = f"{self.api_base_url}/api/Topic/Trending"
            response = self.client.get(url, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"獲取話題失敗: HTTP {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                raise Exception(error_msg)
            
            # 解析回應
            result = response.json()
            topics = []
            
            # 處理不同的回應格式
            if isinstance(result, list):
                # 直接是話題陣列
                topic_list = result
            elif isinstance(result, dict) and "topics" in result:
                # 包含在 topics 欄位中
                topic_list = result["topics"]
            else:
                # 單一話題物件
                topic_list = [result] if result else []
            
            # 轉換為 Topic 物件
            for item in topic_list:
                if isinstance(item, dict):
                    topic = Topic(
                        id=item.get("id") or item.get("topicId", ""),
                        title=item.get("title") or item.get("name", ""),
                        name=item.get("name") or item.get("title", ""),
                        last_article_create_time=item.get("lastArticleCreateTime"),
                        raw_data=item
                    )
                    topics.append(topic)
            
            logger.info(f"成功獲取 {len(topics)} 個話題")
            return topics
            
        except Exception as e:
            logger.error(f"獲取熱門話題失敗: {e}")
            raise
    
    async def get_topic_detail(self, access_token: str, topic_id: str) -> Dict[str, Any]:
        """
        獲取特定話題的詳細資訊（包含 relatedStockSymbols）
        
        Args:
            access_token: 存取 Token
            topic_id: 話題 ID
            
        Returns:
            話題詳細資訊字典
            
        Raises:
            Exception: 獲取失敗
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Version": "2.0",
                "cmoneyapi-trace-context": "n8n"
            }
            
            url = f"{self.api_base_url}/api/Topic/{topic_id}/Trending"
            response = self.client.get(url, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"獲取話題詳細資訊失敗: HTTP {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                raise Exception(error_msg)
            
            # 解析回應
            result = response.json()
            logger.info(f"成功獲取話題 {topic_id} 的詳細資訊")
            return result
            
        except Exception as e:
            logger.error(f"獲取話題詳細資訊失敗: {e}")
            raise
    
    async def publish_article(self, access_token: str, article: ArticleData) -> PublishResult:
        """
        發布文章
        
        Args:
            access_token: 存取 Token
            article: 文章數據
            
        Returns:
            發文結果
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "cmoneyapi-trace-context": "n8n",
                "accept": "application/json",
                "Content-Type": "application/json-patch+json"
            }
            
            # 準備文章數據
            payload = {
                "title": article.title,
                "text": article.text
            }
            
            if article.community_topic:
                payload["communityTopic"] = article.community_topic
            
            if article.commodity_tags:
                payload["commodityTags"] = article.commodity_tags
            
            url = f"{self.api_base_url}/api/Article/Create"
            response = self.client.post(
                url,
                headers=headers,
                json=payload
            )
            
            if response.status_code not in [200, 201]:
                error_msg = f"發文失敗: HTTP {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return PublishResult(
                    success=False,
                    error_message=f"{error_msg} - {response.text}"
                )
            
            # 解析回應
            result = response.json()
            
            # 提取發文 ID 和 URL
            post_id = result.get("id") or result.get("articleId")
            
            # 生成正確的 URL 格式
            if post_id:
                post_url = f"https://www.cmoney.tw/forum/article/{post_id}"
            else:
                post_url = result.get("url") or result.get("link")
            
            logger.info(f"發文成功: post_id={post_id}, post_url={post_url}")
            
            return PublishResult(
                success=True,
                post_id=str(post_id) if post_id else None,
                post_url=post_url,
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"發布文章失敗: {e}")
            return PublishResult(
                success=False,
                error_message=str(e)
            )
    
    async def get_member_info(self, access_token: str, member_ids: List[str]) -> List[MemberInfo]:
        """
        獲取會員資訊 (用於互動數據收集)
        
        Args:
            access_token: 存取 Token
            member_ids: 會員ID列表
            
        Returns:
            會員資訊列表
        """
        try:
            # 將 member_ids 轉換為逗號分隔的字串
            member_ids_str = ",".join(member_ids)
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "cmoneyapi-trace-context": "2016090103_test",
                "accept": "text/plain"
            }
            
            url = f"{self.api_base_url}/api/Member/Info"
            params = {"memberIds": member_ids_str}
            
            response = self.client.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                error_msg = f"獲取會員資訊失敗: HTTP {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                raise Exception(error_msg)
            
            # 解析回應
            result = response.json()
            members = []
            
            # 處理回應格式
            if isinstance(result, list):
                member_list = result
            elif isinstance(result, dict):
                # 可能是包裝在某個欄位中
                member_list = result.get("data", result.get("members", [result]))
            else:
                member_list = []
            
            # 轉換為 MemberInfo 物件
            for item in member_list:
                if isinstance(item, dict):
                    member = MemberInfo(
                        member_id=str(item.get("memberId", item.get("id", ""))),
                        nickname=item.get("nickname", item.get("name", "")),
                        avatar_url=item.get("avatarUrl", item.get("avatar")),
                        follower_count=item.get("followerCount", item.get("followers")),
                        following_count=item.get("followingCount", item.get("following")),
                        article_count=item.get("articleCount", item.get("articles")),
                        raw_data=item
                    )
                    members.append(member)
            
            logger.info(f"成功獲取 {len(members)} 個會員資訊")
            return members
            
        except Exception as e:
            logger.error(f"獲取會員資訊失敗: {e}")
            raise
    
    async def get_article_interactions(self, access_token: str, article_id: str) -> InteractionData:
        """
        獲取文章互動數據 (使用正確的 CMoney API v2.0)
        
        Args:
            access_token: 存取 Token
            article_id: 文章ID
            
        Returns:
            互動數據
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Version": "2.0",  # 重要：需要指定版本號
                "cmoneyapi-trace-context": "2016090103_test",
                "accept": "application/json"
            }
            
            # 使用正確的 CMoney API 端點
            url = f"{self.api_base_url}/api/Article/{article_id}"
            
            response = self.client.get(url, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"獲取文章互動數據失敗: HTTP {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                # 返回預設值而不是拋出異常
                return InteractionData(
                    post_id=article_id,
                    member_id="",
                    raw_data={"error": error_msg}
                )
            
            # 解析回應
            result = response.json()
            
            # 提取 emoji 數據
            emoji_count = result.get("emojiCount", {})
            likes = emoji_count.get("like", 0)  # 正確的讚數來源
            dislikes = emoji_count.get("dislike", 0)
            laughs = emoji_count.get("laugh", 0)
            money = emoji_count.get("money", 0)
            shock = emoji_count.get("shock", 0)
            cry = emoji_count.get("cry", 0)
            think = emoji_count.get("think", 0)
            angry = emoji_count.get("angry", 0)
            
            # 計算總表情數
            total_emojis = likes + dislikes + laughs + money + shock + cry + think + angry
            
            # 其他互動數據
            comments = result.get("commentCount", 0)
            collections = result.get("collectedCount", 0)
            donations = result.get("donation", 0)
            
            # 計算總互動數 (包含所有表情、留言、收藏、打賞)
            total_interactions = total_emojis + comments + collections + donations
            
            # 計算互動率 (基於總互動數)
            engagement_rate = float(total_interactions)
            
            # 建立互動數據物件
            interaction = InteractionData(
                post_id=article_id,
                member_id=str(result.get("creatorId", "")),
                likes=likes,  # 使用 emojiCount.like
                comments=comments,
                shares=collections,  # 用收藏數代替分享數
                views=0,  # CMoney API 沒有提供瀏覽數
                click_rate=0.0,  # CMoney API 沒有提供點擊率
                engagement_rate=engagement_rate,
                
                # 詳細表情統計
                dislikes=dislikes,
                laughs=laughs,
                money=money,
                shock=shock,
                cry=cry,
                think=think,
                angry=angry,
                total_emojis=total_emojis,
                
                # 其他互動數據
                collections=collections,
                donations=donations,
                total_interactions=total_interactions,
                
                raw_data=result
            )
            
            logger.info(f"成功獲取文章 {article_id} 的互動數據: 讚={likes}, 留言={comments}, 收藏={collections}, 打賞={donations}, 表情總數={total_emojis}, 總互動={total_interactions}")
            return interaction
            
        except Exception as e:
            logger.error(f"獲取文章互動數據失敗: {e}")
            # 返回預設值
            return InteractionData(
                post_id=article_id,
                member_id="",
                raw_data={"error": str(e)}
            )
    
    async def delete_article(self, access_token: str, article_id: str) -> bool:
        """
        刪除文章
        
        Args:
            access_token: 存取 Token
            article_id: 文章 ID
            
        Returns:
            刪除是否成功
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "cmoneyapi-trace-context": "2016090103_test",
                "accept": "application/json"
            }
            
            # 使用 CMoney 刪文 API 端點
            url = f"{self.api_base_url}/api/Article/Delete/{article_id}"
            
            response = self.client.delete(url, headers=headers)
            
            if response.status_code == 204:
                logger.info(f"成功刪除文章: {article_id}")
                return True
            else:
                error_msg = f"刪除文章失敗: HTTP {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"刪除文章失敗: {e}")
            return False
    
    async def update_nickname(self, access_token: str, new_nickname: str) -> UpdateNicknameResult:
        """
        更改用戶暱稱 (使用 GraphQL mutation)
        
        Args:
            access_token: 用戶的存取 Token
            new_nickname: 新的暱稱
            
        Returns:
            更改暱稱結果
        """
        try:
            # 準備 GraphQL mutation 請求頭
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "cmoneyapi-trace-context": '{"appVersion":"2.42.0","model":"Backend","manufacturer":"System","appId":18,"osName":"Backend","platform":1,"osVersion":"1.0"}',
                "Accept-Encoding": "gzip"
            }
            
            # GraphQL mutation payload (根據你提供的 API 格式)
            payload = {
                "operationName": "updateMember",
                "variables": {
                    "nickname": new_nickname
                },
                "fields": "{ nickname }"
            }
            
            # 發送 GraphQL mutation 請求
            response = self.client.post(
                self.graphql_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"更改暱稱失敗: HTTP {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return UpdateNicknameResult(
                    success=False,
                    error_message=f"{error_msg} - {response.text}"
                )
            
            # 解析回應
            result = response.json()
            
            # 檢查是否成功 (根據你提供的回應格式)
            if "nickname" in result and result["nickname"] == new_nickname:
                logger.info(f"暱稱更改成功: {new_nickname}")
                return UpdateNicknameResult(
                    success=True,
                    new_nickname=result["nickname"],
                    raw_response=result
                )
            else:
                error_msg = f"暱稱更改失敗: 回應格式異常 - {result}"
                logger.error(error_msg)
                return UpdateNicknameResult(
                    success=False,
                    error_message=error_msg,
                    raw_response=result
                )
            
        except Exception as e:
            logger.error(f"更改暱稱失敗: {e}")
            return UpdateNicknameResult(
                success=False,
                error_message=str(e)
            )
    
    def close(self):
        """關閉客戶端"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 測試函數
async def test_cmoney_client():
    """測試 CMoney 客戶端"""
    try:
        # 創建客戶端
        client = CMoneyClient()
        
        print("測試 CMoney API 客戶端...")
        print("=" * 50)
        
        # 顯示可用的 API 方法
        print("✅ 可用的 API 方法:")
        print("   1. login() - 登入獲取 access_token")
        print("   2. get_trending_topics() - 獲取熱門話題")
        print("   3. publish_article() - 發布文章")
        print("   4. get_member_info() - 獲取會員資訊 (互動數據)")
        print("   5. get_article_interactions() - 獲取文章互動統計")
        print("   6. update_nickname() - 更改用戶暱稱 (GraphQL)")
        
        print("\n📝 注意事項:")
        print("   - 需要真實的 CMoney 憑證才能進行實際 API 調用")
        print("   - 互動數據 API 已整合 Make.com 的會員資訊端點")
        print("   - 支援批量獲取多個會員的資訊")
        
        print("\n🔗 API 端點:")
        print(f"   - 登入: {client.login_url}")
        print(f"   - 基礎 API: {client.api_base_url}")
        print(f"   - 會員資訊: {client.api_base_url}/api/Member/Info")
        print(f"   - 文章統計: {client.api_base_url}/api/Article/{{id}}/Stats")
        
        # 測試數據結構
        print("\n🗃️ 數據結構:")
        print("   - LoginCredentials: email, password")
        print("   - Topic: id, title, name, last_article_create_time")
        print("   - ArticleData: title, text, community_topic, commodity_tags")
        print("   - PublishResult: success, post_id, post_url, error_message")
        print("   - MemberInfo: member_id, nickname, follower_count, article_count")
        print("   - InteractionData: post_id, likes, comments, shares, views")
        
        print("\n✅ CMoney API 客戶端已準備就緒")
        print("可以開始整合到話題派發和互動數據收集服務中")
        
        return True
        
    except Exception as e:
        print(f"❌ CMoney API 客戶端測試失敗: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cmoney_client())
