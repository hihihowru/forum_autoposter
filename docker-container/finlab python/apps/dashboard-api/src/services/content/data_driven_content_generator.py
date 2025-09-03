"""
數據驅動的內容生成器
先調度資料 → 再生成內容
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import finlab
import finlab.data as fdata

from .enhanced_prompt_generator import EnhancedPromptGenerator, create_enhanced_prompt_generator
from .technical_explanation_generator import technical_explanation_generator

logger = logging.getLogger(__name__)

@dataclass
class StockMarketData:
    """股票市場數據"""
    stock_id: str
    stock_name: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    daily_change: float
    daily_change_pct: float
    technical_summary: str

@dataclass
class MarketContext:
    """市場整體環境"""
    market_sentiment: str      # 市場情緒
    sector_performance: str    # 板塊表現  
    macro_factors: str         # 總經因素
    news_highlights: str       # 新聞亮點

class DataDrivenContentGenerator:
    """數據驅動的內容生成器"""
    
    def __init__(self, finlab_api_key: Optional[str] = None):
        self.finlab_api_key = finlab_api_key or os.getenv('FINLAB_API_KEY')
        self.prompt_generator = create_enhanced_prompt_generator()
        self._finlab_logged_in = False
        
        # 確保 Finlab 登入
        self._ensure_finlab_login()
        
        logger.info("數據驅動內容生成器初始化完成")
    
    def _ensure_finlab_login(self):
        """確保 Finlab API 已登入"""
        if not self._finlab_logged_in and self.finlab_api_key:
            try:
                finlab.login(self.finlab_api_key)
                self._finlab_logged_in = True
                logger.info("Finlab API 登入成功")
            except Exception as e:
                logger.error(f"Finlab API 登入失敗: {e}")
                self._finlab_logged_in = False
    
    async def fetch_stock_data(self, stock_id: str, stock_name: str = "") -> Optional[StockMarketData]:
        """獲取單檔股票的市場數據"""
        
        try:
            if not self._finlab_logged_in:
                logger.error("Finlab API 未登入")
                return None
                
            print(f"📊 獲取 {stock_name}({stock_id}) 的市場數據...")
            
            # 獲取 OHLC 數據
            open_price = fdata.get('price:開盤價')
            high_price = fdata.get('price:最高價')
            low_price = fdata.get('price:最低價')
            close_price = fdata.get('price:收盤價')
            volume = fdata.get('price:成交股數')
            
            if not all([open_price is not None, high_price is not None, 
                       low_price is not None, close_price is not None]):
                logger.error(f"無法獲取 {stock_id} 的完整 OHLC 數據")
                return None
            
            # 檢查是否有該股票的數據
            if stock_id not in close_price.columns:
                logger.error(f"未找到股票 {stock_id} 的數據")
                return None
            
            # 獲取最新數據
            stock_close = close_price[stock_id].dropna()
            if len(stock_close) == 0:
                logger.error(f"股票 {stock_id} 無收盤價數據")
                return None
                
            latest_date = stock_close.index[-1]
            
            # 組合 OHLC 數據
            ohlc_data = {
                'date': latest_date.strftime('%Y-%m-%d'),
                'open': float(open_price[stock_id][latest_date]),
                'high': float(high_price[stock_id][latest_date]),
                'low': float(low_price[stock_id][latest_date]),
                'close': float(close_price[stock_id][latest_date]),
                'volume': int(volume[stock_id][latest_date]) if volume is not None and stock_id in volume.columns else 0
            }
            
            # 計算漲跌
            daily_change = ohlc_data['close'] - ohlc_data['open']
            daily_change_pct = (daily_change / ohlc_data['open']) * 100
            
            # 生成技術分析摘要
            technical_summary = self._generate_technical_summary(ohlc_data, daily_change_pct)
            
            stock_data = StockMarketData(
                stock_id=stock_id,
                stock_name=stock_name or stock_id,
                date=ohlc_data['date'],
                open=ohlc_data['open'],
                high=ohlc_data['high'],
                low=ohlc_data['low'],
                close=ohlc_data['close'],
                volume=ohlc_data['volume'],
                daily_change=daily_change,
                daily_change_pct=daily_change_pct,
                technical_summary=technical_summary
            )
            
            print(f"✅ 成功獲取 {stock_name}({stock_id}) 數據: ${ohlc_data['close']:.2f} ({daily_change_pct:+.2f}%)")
            
            return stock_data
            
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 數據失敗: {e}")
            return None
    
    def _generate_technical_summary(self, ohlc_data: Dict[str, Any], change_pct: float) -> str:
        """生成技術分析摘要"""
        
        high_low_range = ohlc_data['high'] - ohlc_data['low']
        body_size = abs(ohlc_data['close'] - ohlc_data['open'])
        volume_level = "高量" if ohlc_data['volume'] > 10000000 else "平量" if ohlc_data['volume'] > 5000000 else "低量"
        
        # 判斷K棒型態
        if ohlc_data['close'] > ohlc_data['open']:
            candle_type = "紅K"
            if body_size / high_low_range > 0.7:
                pattern = "長紅"
            else:
                pattern = "小紅"
        else:
            candle_type = "黑K"
            if body_size / high_low_range > 0.7:
                pattern = "長黑"
            else:
                pattern = "小黑"
        
        # 生成技術摘要
        if abs(change_pct) > 3:
            momentum = "強勢" if change_pct > 0 else "弱勢"
        elif abs(change_pct) > 1:
            momentum = "溫和" if change_pct > 0 else "回檔"
        else:
            momentum = "盤整"
        
        return f"{pattern}K棒，{volume_level}，{momentum}格局"
    
    async def fetch_multiple_stocks_data(self, stock_assignments: List[Dict[str, Any]]) -> Dict[str, StockMarketData]:
        """獲取多檔股票數據"""
        
        print(f"\n📊 開始獲取多檔股票數據...")
        
        stock_data_map = {}
        unique_stocks = set()
        
        # 收集所有需要的股票
        for assignment in stock_assignments:
            assigned_stocks = assignment.get('assigned_stocks', [])
            for stock in assigned_stocks:
                unique_stocks.add((stock['stock_id'], stock['stock_name']))
        
        print(f"🎯 需要獲取 {len(unique_stocks)} 檔股票的數據")
        
        # 獲取每檔股票的數據
        for stock_id, stock_name in unique_stocks:
            stock_data = await self.fetch_stock_data(stock_id, stock_name)
            if stock_data:
                stock_data_map[stock_id] = stock_data
                
            # 避免 API 限制
            await asyncio.sleep(0.5)
        
        print(f"✅ 成功獲取 {len(stock_data_map)} 檔股票數據")
        
        return stock_data_map
    
    def generate_market_context(self, stock_data_map: Dict[str, StockMarketData]) -> MarketContext:
        """生成市場整體環境分析"""
        
        if not stock_data_map:
            return MarketContext(
                market_sentiment="中性",
                sector_performance="無明確趨勢",
                macro_factors="待觀察",
                news_highlights="無特殊消息"
            )
        
        # 分析整體漲跌情況
        total_stocks = len(stock_data_map)
        up_stocks = sum(1 for data in stock_data_map.values() if data.daily_change_pct > 0)
        down_stocks = total_stocks - up_stocks
        
        # 計算平均漲跌幅
        avg_change = sum(data.daily_change_pct for data in stock_data_map.values()) / total_stocks
        
        # 判斷市場情緒
        if up_stocks > down_stocks * 1.5:
            sentiment = "偏多樂觀"
        elif down_stocks > up_stocks * 1.5:
            sentiment = "偏空謹慎"
        else:
            sentiment = "中性觀望"
        
        # 生成板塊表現描述
        if avg_change > 1:
            sector_perf = "科技股表現強勁"
        elif avg_change < -1:
            sector_perf = "科技股承壓整理"
        else:
            sector_perf = "科技股漲跌互見"
        
        # 生成總經因素（基於當前市場狀況的通用分析）
        macro_factors = "聯準會政策、中美關係、AI發展趨勢"
        
        # 生成新聞亮點
        news_highlights = f"今日科技股{sentiment}，{sector_perf}"
        
        return MarketContext(
            market_sentiment=sentiment,
            sector_performance=sector_perf,
            macro_factors=macro_factors,
            news_highlights=news_highlights
        )
    
    async def generate_data_driven_content(self, 
                                         kol_profile: Dict[str, Any],
                                         topic_data: Dict[str, Any], 
                                         stock_assignments: List[Dict[str, Any]],
                                         stock_data_map: Dict[str, StockMarketData],
                                         market_context: MarketContext) -> Optional[Dict[str, Any]]:
        """生成數據驅動的內容"""
        
        try:
            kol_serial = kol_profile['serial']
            kol_nickname = kol_profile['nickname']
            persona = kol_profile['persona']
            
            print(f"\n🎭 為 {kol_nickname} ({persona}) 生成數據驅動內容...")
            
            # 找到該 KOL 的股票分配
            kol_assignment = None
            for assignment in stock_assignments:
                if assignment['kol_profile']['serial'] == kol_serial:
                    kol_assignment = assignment
                    break
            
            if not kol_assignment:
                logger.error(f"未找到 KOL {kol_nickname} 的股票分配")
                return None
            
            assigned_stocks = kol_assignment.get('assigned_stocks', [])
            
            # 準備股票數據摘要
            stock_summary_data = self._prepare_stock_summary_for_kol(
                assigned_stocks, stock_data_map, persona
            )
            
            print(f"📊 分析股票: {', '.join([s['stock_name'] for s in assigned_stocks])}")
            print(f"🎯 分析角度: {kol_assignment.get('analysis_angle', '一般分析')}")
            
            # 生成增強版個人化 Prompt
            enhanced_prompt = self.prompt_generator.generate_enhanced_prompt(
                kol_serial=kol_serial,
                kol_nickname=kol_nickname,
                persona=persona,
                topic_title=topic_data['title'],
                stock_data=stock_summary_data,
                market_context=market_context.news_highlights,
                stock_names=[s['stock_name'] for s in assigned_stocks]
            )
            
            print(f"🎭 個性變體: {enhanced_prompt.get('personality_variant', {}).mood_modifier if enhanced_prompt.get('personality_variant') else '標準'}")
            print(f"🎲 隨機種子: {enhanced_prompt.get('randomization_seed', 'N/A')}")
            
            # 使用 OpenAI 生成內容
            content_result = await self._call_openai_api(enhanced_prompt)
            
            if content_result:
                # 添加數據來源和分析資訊
                content_result['data_sources'] = [f"finlab_{stock['stock_id']}" for stock in assigned_stocks]
                content_result['analysis_angle'] = kol_assignment.get('analysis_angle', '')
                content_result['market_data_summary'] = stock_summary_data
                content_result['generation_metadata'] = {
                    'personality_variant': enhanced_prompt.get('personality_variant'),
                    'randomization_seed': enhanced_prompt.get('randomization_seed'),
                    'generation_params': enhanced_prompt.get('generation_params')
                }
                
                print(f"✅ 內容生成成功")
                return content_result
            else:
                print(f"❌ 內容生成失敗")
                return None
                
        except Exception as e:
            logger.error(f"生成數據驅動內容失敗: {e}")
            return None
    
    def _prepare_stock_summary_for_kol(self, 
                                     assigned_stocks: List[Dict[str, Any]], 
                                     stock_data_map: Dict[str, StockMarketData],
                                     persona: str) -> Dict[str, Any]:
        """為 KOL 準備股票數據摘要，包含技術指標評分解釋"""
        
        if not assigned_stocks:
            return {'has_stock_data': False}
        
        stock_summaries = []
        technical_summaries = []
        technical_explanations = []  # 新增：技術指標解釋
        
        for stock in assigned_stocks:
            stock_id = stock['stock_id']
            stock_name = stock['stock_name']
            
            if stock_id in stock_data_map:
                data = stock_data_map[stock_id]
                
                # 個股摘要
                summary = f"{stock_name}({stock_id}): ${data.close:.2f} ({data.daily_change_pct:+.2f}%)"
                stock_summaries.append(summary)
                
                # 技術摘要
                technical_summaries.append(f"{stock_name}: {data.technical_summary}")
                
                # 新增：技術指標詳細解釋
                tech_explanation = self._build_technical_explanation(stock_name, stock_id, data)
                if tech_explanation:
                    technical_explanations.append(tech_explanation)
        
        # 根據 persona 調整重點
        if persona == "技術派":
            main_summary = f"技術分析重點：{'; '.join(technical_summaries)}"
            secondary_summary = f"價格表現：{'; '.join(stock_summaries)}"
            # 技術派提供詳細的指標解釋
            explanation_summary = f"技術指標評分解釋：{chr(10).join(technical_explanations)}" if technical_explanations else ""
        elif persona == "新聞派":
            main_summary = f"市場表現：{'; '.join(stock_summaries)}"
            secondary_summary = f"技術狀況：{'; '.join(technical_summaries)}"
            # 新聞派提供簡化的技術參考
            explanation_summary = f"技術參考：{chr(10).join(technical_explanations)}" if technical_explanations else ""
        else:  # 總經派
            main_summary = f"基本表現：{'; '.join(stock_summaries)}"
            secondary_summary = f"技術面：{'; '.join(technical_summaries)}"
            # 總經派提供基本的技術背景
            explanation_summary = f"技術背景：{chr(10).join(technical_explanations)}" if technical_explanations else ""
        
        return {
            'has_stock_data': True,
            'stock_summary': main_summary,
            'technical_summary': secondary_summary,
            'technical_explanation': explanation_summary,  # 新增
            'assigned_stocks_count': len(assigned_stocks),
            'detailed_data': [stock_data_map.get(s['stock_id']) for s in assigned_stocks if s['stock_id'] in stock_data_map]
        }
    
    def _build_technical_explanation(self, stock_name: str, stock_id: str, data: StockMarketData) -> str:
        """建構技術指標評分的詳細解釋"""
        
        # 從 technical_summary 中提取評分資訊
        technical_score = 5.0  # 預設值
        confidence_score = 50.0  # 預設值
        
        # 嘗試從 technical_summary 中提取評分
        if hasattr(data, 'technical_summary') and data.technical_summary:
            # 解析 technical_summary 中的評分資訊
            import re
            score_match = re.search(r'評分:\s*([\d.]+)/10', data.technical_summary)
            confidence_match = re.search(r'信心度:\s*([\d.]+)%', data.technical_summary)
            
            if score_match:
                technical_score = float(score_match.group(1))
            if confidence_match:
                confidence_score = float(confidence_match.group(1))
        
        # 使用技術解釋生成器生成詳細解釋
        return technical_explanation_generator.generate_technical_explanation(
            stock_name=stock_name,
            technical_score=technical_score,
            confidence_score=confidence_score,
            persona="技術派"  # 這裡應該根據實際的 KOL persona 調整
        )
    
    async def _call_openai_api(self, enhanced_prompt: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """調用 OpenAI API 生成內容"""
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # 分離 model 參數避免重複
            generation_params = enhanced_prompt['generation_params'].copy()
            model = generation_params.pop('model', 'gpt-4o-mini')
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": enhanced_prompt['system_prompt']},
                    {"role": "user", "content": enhanced_prompt['user_prompt']}
                ],
                **generation_params
            )
            
            content = response.choices[0].message.content
            
            # 解析標題和內容
            lines = content.strip().split('\n')
            title = ""
            main_content = ""
            
            for line in lines:
                if line.startswith('標題：'):
                    title = line.replace('標題：', '').strip()
                elif line.startswith('內容：'):
                    main_content = line.replace('內容：', '').strip()
                elif not title and '：' not in line and line.strip():
                    title = line.strip()
                elif title and line.strip():
                    if main_content:
                        main_content += '\n' + line.strip()
                    else:
                        main_content = line.strip()
            
            if not title:
                title = main_content.split('\n')[0][:30] + "..."
            
            return {
                'title': title,
                'content': main_content,
                'raw_response': content
            }
            
        except Exception as e:
            logger.error(f"OpenAI API 調用失敗: {e}")
            return None

# 創建服務實例的工廠函數
def create_data_driven_content_generator(finlab_api_key: Optional[str] = None) -> DataDrivenContentGenerator:
    """創建數據驅動內容生成器實例"""
    return DataDrivenContentGenerator(finlab_api_key)
