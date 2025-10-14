"""
測試標籤增強功能
"""

import asyncio
import sys
import os

# 添加src目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.publish.tag_enhancer import TagEnhancer
from src.clients.cmoney.cmoney_client import ArticleData

def test_tag_enhancer():
    """測試標籤增強器"""
    
    print("🧪 測試標籤增強功能")
    print("=" * 50)
    
    # 創建標籤增強器
    enhancer = TagEnhancer()
    
    # 測試案例1：包含台積電的看多內容
    print("\n📝 測試案例1: 台積電看多內容")
    article1 = ArticleData(
        title="台積電技術面強勢，突破新高可期",
        text="台積電今日股價表現強勢，技術面呈現多頭排列，均線向上發散，量能放大，後市看好。",
        community_topic=None,
        commodity_tags=None
    )
    
    enhanced1 = enhancer.enhance_article_tags(
        article1, 
        topic_id="test-topic-1",
        topic_title="台積電技術分析",
        topic_content="台積電今日表現亮眼"
    )
    
    print(f"原始文章: {article1.title}")
    print(f"增強後標籤: {enhanced1.commodity_tags}")
    print(f"話題標籤: {enhanced1.community_topic}")
    
    # 測試案例2：包含多檔股票的內容
    print("\n📝 測試案例2: 多檔股票內容")
    article2 = ArticleData(
        title="金融股集體走強，國泰金、富邦金領漲",
        text="金融股今日集體走強，國泰金和富邦金表現亮眼，技術面強勢，後市看好。",
        community_topic=None,
        commodity_tags=None
    )
    
    enhanced2 = enhancer.enhance_article_tags(
        article2,
        topic_id="test-topic-2",
        topic_title="金融股分析",
        topic_content="金融股集體走強"
    )
    
    print(f"原始文章: {article2.title}")
    print(f"增強後標籤: {enhanced2.commodity_tags}")
    print(f"話題標籤: {enhanced2.community_topic}")
    
    # 測試案例3：看空內容
    print("\n📝 測試案例3: 看空內容")
    article3 = ArticleData(
        title="聯發科業績不如預期，股價承壓",
        text="聯發科最新財報不如市場預期，營收下滑，業績表現不佳，股價可能承壓。",
        community_topic=None,
        commodity_tags=None
    )
    
    enhanced3 = enhancer.enhance_article_tags(
        article3,
        topic_id="test-topic-3",
        topic_title="聯發科財報分析",
        topic_content="聯發科業績不如預期"
    )
    
    print(f"原始文章: {article3.title}")
    print(f"增強後標籤: {enhanced3.commodity_tags}")
    print(f"話題標籤: {enhanced3.community_topic}")
    
    # 測試案例4：指數相關內容
    print("\n📝 測試案例4: 指數相關內容")
    article4 = ArticleData(
        title="台股今日大漲，電子股領軍",
        text="台股今日大漲，電子股領軍上攻，加權指數突破新高，技術面強勢。",
        community_topic=None,
        commodity_tags=None
    )
    
    enhanced4 = enhancer.enhance_article_tags(
        article4,
        topic_id="test-topic-4",
        topic_title="台股大盤分析",
        topic_content="台股今日大漲"
    )
    
    print(f"原始文章: {article4.title}")
    print(f"增強後標籤: {enhanced4.commodity_tags}")
    print(f"話題標籤: {enhanced4.community_topic}")
    
    # 測試案例5：無股票內容
    print("\n📝 測試案例5: 無股票內容")
    article5 = ArticleData(
        title="市場情緒分析：投資人信心回升",
        text="根據最新調查，投資人信心指數回升，市場情緒轉為樂觀，後市可期。",
        community_topic=None,
        commodity_tags=None
    )
    
    enhanced5 = enhancer.enhance_article_tags(
        article5,
        topic_id="test-topic-5",
        topic_title="市場情緒分析",
        topic_content="投資人信心回升"
    )
    
    print(f"原始文章: {article5.title}")
    print(f"增強後標籤: {enhanced5.commodity_tags}")
    print(f"話題標籤: {enhanced5.community_topic}")
    
    print("\n" + "=" * 50)
    print("✅ 標籤增強測試完成")

if __name__ == "__main__":
    test_tag_enhancer()

























