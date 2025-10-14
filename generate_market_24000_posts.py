"""
為大盤重返兩萬四熱門話題生成貼文記錄
分配KOL並標記為ready_to_post狀態
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# 添加src目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.assign.assignment_service import AssignmentService
from src.services.content.content_generator import ContentGenerator
from src.services.classification.topic_classifier import TopicClassifier
from src.services.publish.tag_enhancer import TagEnhancer
from src.clients.google.sheets_client import GoogleSheetsClient
from src.clients.ohlc.ohlc_client import OHLCClient
from src.models.assignment import TopicData, Assignment
from src.models.content import ContentRequest

class Market24000PostGenerator:
    """大盤重返兩萬四貼文生成器"""
    
    def __init__(self):
        """初始化"""
        self.sheets_client = GoogleSheetsClient()
        self.ohlc_client = OHLCClient()
        self.assignment_service = AssignmentService(self.sheets_client)
        self.content_generator = ContentGenerator()
        self.topic_classifier = TopicClassifier()
        self.tag_enhancer = TagEnhancer()
        
        # 大盤重返兩萬四的話題信息
        self.topic_info = {
            "id": "market-24000-breakthrough",
            "title": "大盤重返兩萬四，台股再創新高",
            "content": "台股今日大漲，加權指數突破兩萬四千點關卡，創下歷史新高。主要受惠於AI概念股強勢、外資買超、以及市場對下半年景氣的樂觀預期。",
            "stock_ids": ["2330", "2454", "2317", "2412", "2881"],  # 五檔主要股票
            "stock_names": ["台積電", "聯發科", "鴻海", "中華電", "富邦金"]
        }
        
        print("🚀 大盤重返兩萬四貼文生成器初始化完成")
    
    async def generate_posts(self):
        """生成所有貼文記錄"""
        try:
            print(f"\n📊 開始處理話題: {self.topic_info['title']}")
            print("=" * 60)
            
            # 步驟1: 話題分類
            print("\n🔍 步驟1: 話題分類...")
            classification = self.topic_classifier.classify_topic(
                self.topic_info["id"],
                self.topic_info["title"],
                self.topic_info["content"]
            )
            print(f"✅ 分類結果:")
            print(f"   - 人設標籤: {classification.persona_tags}")
            print(f"   - 產業標籤: {classification.industry_tags}")
            print(f"   - 事件標籤: {classification.event_tags}")
            print(f"   - 股票標籤: {classification.stock_tags}")
            
            # 步驟2: 載入KOL配置
            print("\n👥 步驟2: 載入KOL配置...")
            self.assignment_service.load_kol_profiles()
            print(f"✅ 載入 {len(self.assignment_service._kol_profiles)} 個KOL配置")
            
            # 步驟3: 為每檔股票分配KOL
            print("\n📈 步驟3: 為每檔股票分配KOL...")
            stock_assignments = await self._assign_stocks_to_kols()
            
            # 步驟4: 生成貼文記錄
            print("\n✍️ 步驟4: 生成貼文記錄...")
            post_records = await self._generate_post_records(stock_assignments)
            
            # 步驟5: 寫入Google Sheets
            print("\n💾 步驟5: 寫入Google Sheets...")
            await self._write_to_sheets(post_records)
            
            print("\n" + "=" * 60)
            print("🎉 所有貼文記錄生成完成！")
            print(f"📝 共生成 {len(post_records)} 篇貼文")
            print("⏳ 狀態: ready_to_post (等待審核)")
            print("💡 請在Google Sheets中審核後，將狀態改為 'approved' 即可發文")
            
        except Exception as e:
            print(f"❌ 生成貼文記錄失敗: {e}")
            import traceback
            traceback.print_exc()
    
    async def _assign_stocks_to_kols(self) -> List[Dict[str, Any]]:
        """為每檔股票分配KOL"""
        stock_assignments = []
        
        # 可用的KOL序號（根據您的需求調整）
        available_kols = [200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210]
        
        # 為每檔股票分配一個KOL
        for i, (stock_id, stock_name) in enumerate(zip(self.topic_info["stock_ids"], self.topic_info["stock_names"])):
            # 選擇KOL（輪流分配）
            kol_serial = available_kols[i % len(available_kols)]
            
            # 獲取KOL信息
            kol_info = next((k for k in self.assignment_service._kol_profiles if k.serial == kol_serial), None)
            
            if kol_info:
                assignment = {
                    "stock_id": stock_id,
                    "stock_name": stock_name,
                    "kol_serial": kol_serial,
                    "kol_nickname": kol_info.nickname,
                    "kol_persona": kol_info.persona,
                    "topic_id": self.topic_info["id"],
                    "topic_title": self.topic_info["title"]
                }
                stock_assignments.append(assignment)
                
                print(f"   📊 {stock_name}({stock_id}) → {kol_info.nickname} ({kol_info.persona})")
            else:
                print(f"   ⚠️ 找不到KOL {kol_serial} 的配置")
        
        return stock_assignments
    
    async def _generate_post_records(self, stock_assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成貼文記錄"""
        post_records = []
        
        for assignment in stock_assignments:
            try:
                print(f"\n   🎯 為 {assignment['stock_name']} 生成內容...")
                
                # 獲取股票OHLC數據
                ohlc_data = await self._fetch_stock_ohlc(assignment['stock_id'])
                
                # 生成內容
                content_request = ContentRequest(
                    topic_title=f"{assignment['stock_name']} - {assignment['topic_title']}",
                    topic_keywords=f"{assignment['stock_name']}, 台股, 大盤, 兩萬四, 突破",
                    kol_persona=assignment['kol_persona'],
                    kol_nickname=assignment['kol_nickname'],
                    content_type="stock_analysis",
                    target_audience="active_traders",
                    market_data=ohlc_data
                )
                
                generated = self.content_generator.generate_complete_content(content_request)
                
                if generated.success:
                    # 生成標籤
                    article_data = {
                        "title": generated.title,
                        "text": generated.content,
                        "community_topic": None,
                        "commodity_tags": None
                    }
                    
                    enhanced_article = self.tag_enhancer.enhance_article_tags(
                        article_data,
                        topic_id=assignment['topic_id'],
                        topic_title=assignment['topic_title'],
                        topic_content=assignment['topic_title']
                    )
                    
                    # 創建貼文記錄
                    post_record = {
                        "post_id": f"market24000_{assignment['stock_id']}_{assignment['kol_serial']}",
                        "kol_serial": assignment['kol_serial'],
                        "kol_nickname": assignment['kol_nickname'],
                        "kol_member_id": f"forum_{assignment['kol_serial']}@cmoney.com.tw",
                        "persona": assignment['kol_persona'],
                        "content_type": "stock_analysis",
                        "topic_index": 0,
                        "topic_id": assignment['topic_id'],
                        "topic_title": assignment['topic_title'],
                        "topic_keywords": f"{assignment['stock_name']}, 台股, 大盤, 兩萬四",
                        "content": generated.content,
                        "status": "ready_to_post",  # 標記為等待審核
                        "scheduled_time": "",
                        "post_time": "",
                        "error_message": "",
                        "platform_post_id": "",
                        "platform_post_url": "",
                        "trending_topic_title": assignment['topic_title']
                    }
                    
                    post_records.append(post_record)
                    print(f"      ✅ 內容生成成功: {generated.title[:30]}...")
                else:
                    print(f"      ❌ 內容生成失敗: {generated.error_message}")
                
            except Exception as e:
                print(f"      ❌ 處理 {assignment['stock_name']} 時發生錯誤: {e}")
                continue
        
        return post_records
    
    async def _fetch_stock_ohlc(self, stock_id: str) -> Dict[str, Any]:
        """獲取股票OHLC數據"""
        try:
            # 這裡應該調用實際的OHLC API
            # 暫時返回模擬數據
            return {
                "stock_id": stock_id,
                "current_price": 100.0,
                "change": 2.5,
                "change_percent": 2.56,
                "volume": 1000000,
                "ma5": 98.5,
                "ma10": 97.2,
                "ma20": 95.8,
                "rsi": 65.0,
                "macd": 0.5
            }
        except Exception as e:
            print(f"      ⚠️ 獲取 {stock_id} OHLC數據失敗: {e}")
            return {}
    
    async def _write_to_sheets(self, post_records: List[Dict[str, Any]]):
        """寫入Google Sheets"""
        try:
            # 讀取現有的貼文記錄表
            existing_data = self.sheets_client.read_sheet('貼文記錄表', 'A:R')
            headers = existing_data[0] if existing_data else []
            
            # 準備新數據
            new_rows = []
            for record in post_records:
                row = [
                    record.get("post_id", ""),
                    record.get("kol_serial", ""),
                    record.get("kol_nickname", ""),
                    record.get("kol_member_id", ""),
                    record.get("persona", ""),
                    record.get("content_type", ""),
                    record.get("topic_index", ""),
                    record.get("topic_id", ""),
                    record.get("topic_title", ""),
                    record.get("topic_keywords", ""),
                    record.get("content", ""),
                    record.get("status", ""),
                    record.get("scheduled_time", ""),
                    record.get("post_time", ""),
                    record.get("error_message", ""),
                    record.get("platform_post_id", ""),
                    record.get("platform_post_url", ""),
                    record.get("trending_topic_title", "")
                ]
                new_rows.append(row)
            
            # 寫入新數據
            if new_rows:
                # 在現有數據後添加新行
                start_row = len(existing_data) + 1
                self.sheets_client.write_sheet('貼文記錄表', f'A{start_row}', new_rows)
                print(f"      ✅ 成功寫入 {len(new_rows)} 行數據到貼文記錄表")
            
        except Exception as e:
            print(f"      ❌ 寫入Google Sheets失敗: {e}")
            raise

async def main():
    """主函數"""
    generator = Market24000PostGenerator()
    await generator.generate_posts()

if __name__ == "__main__":
    asyncio.run(main())

























