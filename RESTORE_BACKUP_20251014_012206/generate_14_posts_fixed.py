#!/usr/bin/env python3
"""
重新生成 14 個貼文並更新到新的 Google Sheets
使用修復後的 FinLab API 數據調度層
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostGenerator:
    """貼文生成器 - 使用修復後的 FinLab API"""
    
    def __init__(self):
        self.api_key = os.getenv('FINLAB_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.serper_key = os.getenv('SERPER_API_KEY')
        
        if not all([self.api_key, self.openai_key, self.serper_key]):
            raise ValueError("缺少必要的 API 金鑰")
        
        # 新的 Google Sheets ID
        self.new_sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        
        logger.info("貼文生成器初始化完成")
    
    async def get_finlab_revenue_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取 FinLab 營收數據 - 使用正確的數據表名稱"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取營收相關數據
            revenue_data = data.get('monthly_revenue:當月營收')
            mom_growth_data = data.get('monthly_revenue:上月比較增減(%)')
            yoy_growth_data = data.get('monthly_revenue:去年同月增減(%)')
            
            if stock_id not in revenue_data.columns:
                logger.warning(f"⚠️ 股票 {stock_id} 不在營收數據表中")
                return None
            
            # 獲取最新數據
            stock_revenue = revenue_data[stock_id].dropna()
            if len(stock_revenue) == 0:
                logger.warning(f"⚠️ 股票 {stock_id} 無營收數據")
                return None
            
            latest_date = stock_revenue.index[-1]
            latest_revenue = stock_revenue.iloc[-1]
            
            # 獲取增長率數據
            mom_growth = 0.0
            yoy_growth = 0.0
            
            if mom_growth_data is not None and stock_id in mom_growth_data.columns:
                stock_mom = mom_growth_data[stock_id].dropna()
                if len(stock_mom) > 0:
                    mom_growth = float(stock_mom.iloc[-1])
            
            if yoy_growth_data is not None and stock_id in yoy_growth_data.columns:
                stock_yoy = yoy_growth_data[stock_id].dropna()
                if len(stock_yoy) > 0:
                    yoy_growth = float(stock_yoy.iloc[-1])
            
            logger.info(f"✅ 獲取到 {stock_name} 營收數據")
            
            return {
                'revenue': float(latest_revenue),
                'yoy_growth': yoy_growth,
                'mom_growth': mom_growth,
                'period': latest_date.strftime('%Y-%m'),
                'date': latest_date.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} 營收數據失敗: {e}")
            return None
    
    async def get_finlab_earnings_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取 FinLab 財報數據 - 使用正確的財報數據表"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取財報相關數據
            eps_data = data.get('fundamental_features:每股稅後淨利')
            revenue_growth_data = data.get('fundamental_features:營收成長率')
            profit_growth_data = data.get('fundamental_features:稅後淨利成長率')
            operating_profit_data = data.get('fundamental_features:營業利益')
            net_profit_data = data.get('fundamental_features:歸屬母公司淨利')
            gross_margin_data = data.get('fundamental_features:營業毛利率')
            net_margin_data = data.get('fundamental_features:稅後淨利率')
            
            if stock_id not in eps_data.columns:
                logger.warning(f"⚠️ 股票 {stock_id} 不在財報數據表中")
                return None
            
            # 獲取最新數據
            stock_eps = eps_data[stock_id].dropna()
            if len(stock_eps) == 0:
                logger.warning(f"⚠️ 股票 {stock_id} 無財報數據")
                return None
            
            latest_date = stock_eps.index[-1]
            latest_eps = stock_eps.iloc[-1]
            
            # 獲取其他財報數據
            earnings_data = {
                'eps': float(latest_eps),
                'period': str(latest_date),
                'date': str(latest_date)  # 財報數據的日期格式是字符串
            }
            
            # 獲取增長率數據
            if revenue_growth_data is not None and stock_id in revenue_growth_data.columns:
                stock_revenue_growth = revenue_growth_data[stock_id].dropna()
                if len(stock_revenue_growth) > 0:
                    earnings_data['revenue_growth'] = float(stock_revenue_growth.iloc[-1])
            
            if profit_growth_data is not None and stock_id in profit_growth_data.columns:
                stock_profit_growth = profit_growth_data[stock_id].dropna()
                if len(stock_profit_growth) > 0:
                    earnings_data['profit_growth'] = float(stock_profit_growth.iloc[-1])
            
            # 獲取利潤數據
            if operating_profit_data is not None and stock_id in operating_profit_data.columns:
                stock_operating_profit = operating_profit_data[stock_id].dropna()
                if len(stock_operating_profit) > 0:
                    earnings_data['operating_profit'] = float(stock_operating_profit.iloc[-1])
            
            if net_profit_data is not None and stock_id in net_profit_data.columns:
                stock_net_profit = net_profit_data[stock_id].dropna()
                if len(stock_net_profit) > 0:
                    earnings_data['net_profit'] = float(stock_net_profit.iloc[-1])
            
            # 獲取利潤率數據
            if gross_margin_data is not None and stock_id in gross_margin_data.columns:
                stock_gross_margin = gross_margin_data[stock_id].dropna()
                if len(stock_gross_margin) > 0:
                    earnings_data['gross_margin'] = float(stock_gross_margin.iloc[-1])
            
            if net_margin_data is not None and stock_id in net_margin_data.columns:
                stock_net_margin = net_margin_data[stock_id].dropna()
                if len(stock_net_margin) > 0:
                    earnings_data['net_margin'] = float(stock_net_margin.iloc[-1])
            
            logger.info(f"✅ 獲取到 {stock_name} 財報數據")
            
            return earnings_data
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} 財報數據失敗: {e}")
            return None
    
    async def get_finlab_stock_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取 FinLab 股票數據"""
        try:
            import finlab
            from finlab import data
            
            # 登入
            finlab.login(self.api_key)
            
            # 獲取價格數據
            open_data = data.get('price:開盤價')
            high_data = data.get('price:最高價')
            low_data = data.get('price:最低價')
            close_data = data.get('price:收盤價')
            volume_data = data.get('price:成交股數')
            
            if stock_id not in close_data.columns:
                logger.warning(f"⚠️ 股票 {stock_id} 不在價格數據表中")
                return None
            
            # 獲取最新數據
            stock_close = close_data[stock_id].dropna()
            if len(stock_close) == 0:
                logger.warning(f"⚠️ 股票 {stock_id} 無價格數據")
                return None
            
            latest_date = stock_close.index[-1]
            
            # 組合 OHLC 數據
            stock_data = {
                'date': latest_date.strftime('%Y-%m-%d'),
                'open': float(open_data[stock_id][latest_date]),
                'high': float(high_data[stock_id][latest_date]),
                'low': float(low_data[stock_id][latest_date]),
                'close': float(close_data[stock_id][latest_date]),
                'volume': int(volume_data[stock_id][latest_date]),
                'daily_change': float(close_data[stock_id][latest_date] - open_data[stock_id][latest_date]),
                'daily_change_pct': float((close_data[stock_id][latest_date] - open_data[stock_id][latest_date]) / open_data[stock_id][latest_date] * 100)
            }
            
            logger.info(f"✅ 獲取到 {stock_name} 股票數據")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"獲取 {stock_name} 股票數據失敗: {e}")
            return None
    
    async def get_serper_news_data(self, stock_id: str, stock_name: str) -> Optional[Dict[str, Any]]:
        """獲取 Serper 新聞數據"""
        try:
            import httpx
            
            # 構建搜尋查詢
            query = f"{stock_name} {stock_id} 股票 新聞"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": self.serper_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "q": query,
                        "num": 5
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    news_results = data.get('organic', [])
                    
                    if news_results:
                        # 提取新聞標題和摘要
                        news_summaries = []
                        for result in news_results[:3]:  # 只取前3個
                            title = result.get('title', '')
                            snippet = result.get('snippet', '')
                            news_summaries.append(f"{title}: {snippet}")
                        
                        return {
                            'news_count': len(news_results),
                            'news_summaries': news_summaries,
                            'query': query
                        }
                
                logger.warning(f"⚠️ 無法獲取 {stock_name} 新聞數據")
                return None
                
        except Exception as e:
            logger.error(f"獲取 {stock_name} 新聞數據失敗: {e}")
            return None
    
    async def generate_openai_content(self, stock_id: str, stock_name: str, kol_nickname: str, 
                                     finlab_data: Optional[Dict[str, Any]], 
                                     serper_data: Optional[Dict[str, Any]], 
                                     analysis_type: str) -> Optional[Dict[str, Any]]:
        """使用 OpenAI 生成內容"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_key)
            
            # 構建提示詞
            prompt = f"""
請為 {kol_nickname} 生成一篇關於 {stock_name}({stock_id}) 的投資分析貼文。

分析類型: {analysis_type}

股票數據:
"""
            
            if finlab_data:
                if 'revenue' in finlab_data:
                    prompt += f"- 當月營收: {finlab_data['revenue']:,.0f}\n"
                    prompt += f"- 年增率: {finlab_data['yoy_growth']:.2f}%\n"
                    prompt += f"- 月增率: {finlab_data['mom_growth']:.2f}%\n"
                
                if 'eps' in finlab_data:
                    prompt += f"- EPS: {finlab_data['eps']:.2f}\n"
                    if 'revenue_growth' in finlab_data:
                        prompt += f"- 營收成長率: {finlab_data['revenue_growth']:.2f}%\n"
                    if 'profit_growth' in finlab_data:
                        prompt += f"- 淨利成長率: {finlab_data['profit_growth']:.2f}%\n"
                
                if 'close' in finlab_data:
                    prompt += f"- 收盤價: {finlab_data['close']:.2f}\n"
                    prompt += f"- 漲跌幅: {finlab_data['daily_change_pct']:.2f}%\n"
            
            if serper_data and serper_data.get('news_summaries'):
                prompt += "\n相關新聞:\n"
                for news in serper_data['news_summaries'][:2]:
                    prompt += f"- {news}\n"
            
            prompt += f"""

請以 {kol_nickname} 的風格撰寫一篇 300-500 字的投資分析貼文，包含：
1. 吸引人的標題
2. 簡潔的內容摘要
3. 投資建議
4. 風險提醒

請確保內容真實、客觀，符合投資分析標準。
"""
            
            # 調用 OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一位專業的投資分析師，擅長撰寫股票分析貼文。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # 提取標題和內容
            lines = content.split('\n')
            title = ""
            body = ""
            
            for line in lines:
                if line.strip() and not title:
                    title = line.strip()
                elif line.strip():
                    body += line.strip() + "\n"
            
            return {
                'title': title,
                'content': body.strip(),
                'tokens_used': response.usage.total_tokens,
                'model': 'gpt-3.5-turbo'
            }
            
        except Exception as e:
            logger.error(f"生成 {stock_name} 內容失敗: {e}")
            return None
    
    async def record_to_sheets(self, post_data: Dict[str, Any]):
        """記錄到 Google Sheets"""
        try:
            from src.clients.google.sheets_client import GoogleSheetsClient
            
            # 創建 Google Sheets 客戶端
            sheets_client = GoogleSheetsClient(
                credentials_file="./credentials/google-service-account.json",
                spreadsheet_id=self.new_sheets_id
            )
            
            # 構建記錄數據
            record_data = {
                'post_id': post_data['post_id'],
                'generation_time': post_data['generation_time'],
                'workflow_type': 'after_hours_limit_up',
                'trigger_type': 'limit_up_stock',
                'status': 'ready_to_post',
                'priority_level': 'high',
                'batch_id': post_data['batch_id'],
                'kol_serial': post_data['kol_serial'],
                'kol_nickname': post_data['kol_nickname'],
                'stock_id': post_data['stock_id'],
                'stock_name': post_data['stock_name'],
                'analysis_type': post_data['analysis_type'],
                'title': post_data['title'],
                'content': post_data['content'],
                'content_length': len(post_data['content']),
                'openai_model': post_data['model'],
                'openai_tokens_used': post_data['tokens_used'],
                'finlab_api_called': post_data['finlab_api_called'],
                'serper_api_called': post_data['serper_api_called'],
                'data_sources_used': post_data['data_sources_used']
            }
            
            # 轉換為列表格式
            headers = [
                'post_id', 'generation_time', 'workflow_type', 'trigger_type', 'status',
                'priority_level', 'batch_id', 'kol_serial', 'kol_nickname', 'stock_id',
                'stock_name', 'analysis_type', 'title', 'content', 'content_length',
                'openai_model', 'openai_tokens_used', 'finlab_api_called', 'serper_api_called',
                'data_sources_used'
            ]
            
            row_data = []
            for header in headers:
                row_data.append(str(record_data.get(header, '')))
            
            # 寫入到 Google Sheets
            result = sheets_client.append_sheet('貼文紀錄表', [row_data])
            
            logger.info(f"✅ 記錄到 Google Sheets: {post_data['post_id']}")
            
        except Exception as e:
            logger.error(f"記錄到 Google Sheets 失敗: {e}")
    
    async def generate_posts(self):
        """生成 14 個貼文"""
        print("🚀 開始生成 14 個貼文...")
        print("=" * 60)
        
        # 測試股票列表
        test_stocks = [
            ('2330', '台積電'),
            ('2317', '鴻海'),
            ('2454', '聯發科'),
            ('3008', '大立光'),
            ('2412', '中華電'),
            ('2881', '富邦金'),
            ('1301', '台塑'),
            ('2002', '中鋼'),
            ('1216', '統一'),
            ('2207', '和泰車'),
            ('2882', '國泰金'),
            ('1303', '南亞'),
            ('2308', '台達電'),
            ('2884', '玉山金')
        ]
        
        # KOL 設定
        kol_settings = [
            {'nickname': '投資達人', 'style': '專業分析'},
            {'nickname': '股市老手', 'style': '經驗分享'},
            {'nickname': '財經專家', 'style': '深度解析'},
            {'nickname': '技術分析師', 'style': '技術指標'},
            {'nickname': '價值投資者', 'style': '基本面分析'},
            {'nickname': '短線高手', 'style': '快速反應'},
            {'nickname': '長線投資者', 'style': '穩健策略'}
        ]
        
        # 分析類型
        analysis_types = ['revenue', 'earnings', 'stock_analysis']
        
        generated_posts = []
        
        for i, (stock_id, stock_name) in enumerate(test_stocks):
            print(f"\n📊 處理股票 {i+1}/14: {stock_name}({stock_id})")
            print("-" * 40)
            
            # 選擇 KOL 和分析類型
            kol = kol_settings[i % len(kol_settings)]
            analysis_type = analysis_types[i % len(analysis_types)]
            
            # 獲取數據
            finlab_data = None
            serper_data = None
            
            if analysis_type == 'revenue':
                finlab_data = await self.get_finlab_revenue_data(stock_id, stock_name)
            elif analysis_type == 'earnings':
                finlab_data = await self.get_finlab_earnings_data(stock_id, stock_name)
            elif analysis_type == 'stock_analysis':
                finlab_data = await self.get_finlab_stock_data(stock_id, stock_name)
            
            # 獲取新聞數據
            serper_data = await self.get_serper_news_data(stock_id, stock_name)
            
            # 生成內容
            content_data = await self.generate_openai_content(
                stock_id, stock_name, kol['nickname'], 
                finlab_data, serper_data, analysis_type
            )
            
            if content_data:
                # 構建貼文數據
                post_data = {
                    'post_id': f"{stock_id}_{i+1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'generation_time': datetime.now().isoformat(),
                    'batch_id': f"batch_{datetime.now().strftime('%Y%m%d')}",
                    'kol_serial': str(i+1),
                    'kol_nickname': kol['nickname'],
                    'stock_id': stock_id,
                    'stock_name': stock_name,
                    'analysis_type': analysis_type,
                    'title': content_data['title'],
                    'content': content_data['content'],
                    'model': content_data['model'],
                    'tokens_used': content_data['tokens_used'],
                    'finlab_api_called': finlab_data is not None,
                    'serper_api_called': serper_data is not None,
                    'data_sources_used': 'finlab_api,serper_api'
                }
                
                # 記錄到 Google Sheets
                await self.record_to_sheets(post_data)
                
                generated_posts.append(post_data)
                
                print(f"✅ 生成成功: {content_data['title'][:50]}...")
                print(f"📝 內容長度: {len(content_data['content'])} 字")
                print(f"🤖 使用模型: {content_data['model']}")
                print(f"🔢 使用 Token: {content_data['tokens_used']}")
            else:
                print(f"❌ 生成失敗: {stock_name}")
        
        print(f"\n🎉 貼文生成完成！")
        print(f"📊 總計生成: {len(generated_posts)} 個貼文")
        print(f"📋 已更新到 Google Sheets: {self.new_sheets_id}")
        print("=" * 60)

async def main():
    """主函數"""
    try:
        generator = PostGenerator()
        await generator.generate_posts()
    except Exception as e:
        logger.error(f"貼文生成過程中發生錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
