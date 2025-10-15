#!/usr/bin/env python3
"""
智能API調配系統
為15篇漲停股分析文章均衡分配各種API資源
"""

import random
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class APIResource:
    """API資源配置"""
    name: str
    description: str
    priority: str
    max_usage: int
    current_usage: int = 0

@dataclass
class StockAnalysis:
    """股票分析配置"""
    stock_id: str
    stock_name: str
    volume_rank: int
    change_percent: float
    volume_amount: float
    rank_type: str
    assigned_apis: List[str] = None

class SmartAPIAllocator:
    """智能API調配器"""
    
    def __init__(self):
        """初始化API資源"""
        self.api_resources = {
            'serper': APIResource(
                name='Serper API',
                description='搜尋最新新聞/資訊',
                priority='🔴 最高',
                max_usage=15  # 每篇文都必須使用
            ),
            'finlab_financial': APIResource(
                name='Finlab 財報API',
                description='營收、EPS、毛利等財報數據',
                priority='🟡 高',
                max_usage=8
            ),
            'monthly_revenue': APIResource(
                name='月營收API',
                description='最新月營收數據、成長率分析',
                priority='🟡 高',
                max_usage=6
            ),
            'technical_analysis': APIResource(
                name='股價技術面API',
                description='技術分析、Summary分析',
                priority='🟡 高',
                max_usage=7
            ),
            'volume_analysis': APIResource(
                name='成交量分析',
                description='內文提及成交量資訊',
                priority='🟢 中',
                max_usage=15  # 內嵌在所有文章中
            )
        }
        
        self.analysis_templates = {
            'high_volume': {
                'name': '有量漲停分析',
                'focus': '市場熱點、資金流向',
                'apis': ['serper', 'volume_analysis'],
                'optional_apis': ['finlab_financial', 'monthly_revenue', 'technical_analysis']
            },
            'low_volume': {
                'name': '無量漲停分析',
                'focus': '籌碼集中、續漲潛力',
                'apis': ['serper', 'volume_analysis'],
                'optional_apis': ['technical_analysis', 'monthly_revenue', 'finlab_financial']
            }
        }
    
    def allocate_apis_for_stocks(self, stocks: List[StockAnalysis]) -> List[StockAnalysis]:
        """
        為股票列表智能分配API資源
        
        Args:
            stocks: 股票分析列表
            
        Returns:
            分配了API的股票分析列表
        """
        print("🎯 開始智能API調配...")
        print(f"📊 總股票數: {len(stocks)}")
        print()
        
        # 重置API使用計數
        for api in self.api_resources.values():
            api.current_usage = 0
        
        allocated_stocks = []
        
        for i, stock in enumerate(stocks):
            print(f"📈 處理第 {i+1} 檔股票: {stock.stock_name}({stock.stock_id})")
            print(f"    排名: {stock.rank_type} 第{stock.volume_rank}名")
            print(f"    漲幅: {stock.change_percent:.2f}%")
            print(f"    成交金額: {stock.volume_amount:.4f} 億元")
            
            # 確定分析類型
            analysis_type = 'high_volume' if '有量' in stock.rank_type else 'low_volume'
            template = self.analysis_templates[analysis_type]
            
            # 分配必備API
            assigned_apis = template['apis'].copy()
            
            # 智能分配可選API
            optional_apis = self._allocate_optional_apis(template['optional_apis'])
            assigned_apis.extend(optional_apis)
            
            # 更新股票配置
            stock.assigned_apis = assigned_apis
            
            # 更新API使用計數
            for api_name in assigned_apis:
                if api_name in self.api_resources:
                    self.api_resources[api_name].current_usage += 1
            
            print(f"    📋 分配API: {', '.join(assigned_apis)}")
            print()
            
            allocated_stocks.append(stock)
        
        # 顯示分配結果
        self._show_allocation_summary()
        
        return allocated_stocks
    
    def _allocate_optional_apis(self, optional_apis: List[str]) -> List[str]:
        """
        智能分配可選API
        
        Args:
            optional_apis: 可選API列表
            
        Returns:
            分配的API列表
        """
        allocated = []
        
        for api_name in optional_apis:
            if api_name not in self.api_resources:
                continue
                
            api = self.api_resources[api_name]
            
            # 檢查是否還有配額
            if api.current_usage < api.max_usage:
                # 根據優先級和剩餘配額決定是否分配
                allocation_chance = self._calculate_allocation_chance(api)
                
                if random.random() < allocation_chance:
                    allocated.append(api_name)
        
        return allocated
    
    def _calculate_allocation_chance(self, api: APIResource) -> float:
        """
        計算API分配機率
        
        Args:
            api: API資源
            
        Returns:
            分配機率 (0-1)
        """
        remaining_quota = api.max_usage - api.current_usage
        total_quota = api.max_usage
        
        # 基礎機率
        base_chance = remaining_quota / total_quota
        
        # 根據優先級調整
        priority_multiplier = {
            '🔴 最高': 1.0,
            '🟡 高': 0.8,
            '🟢 中': 0.6
        }
        
        multiplier = priority_multiplier.get(api.priority, 0.7)
        
        return base_chance * multiplier
    
    def _show_allocation_summary(self):
        """顯示分配摘要"""
        print("📊 API調配結果摘要")
        print("=" * 50)
        
        for api_name, api in self.api_resources.items():
            usage_rate = (api.current_usage / api.max_usage) * 100
            print(f"{api.name}:")
            print(f"  使用量: {api.current_usage}/{api.max_usage} ({usage_rate:.1f}%)")
            print(f"  優先級: {api.priority}")
            print(f"  功能: {api.description}")
            print()
    
    def generate_content_outline(self, stock: StockAnalysis) -> Dict[str, Any]:
        """
        為股票生成內容大綱
        
        Args:
            stock: 股票分析配置
            
        Returns:
            內容大綱
        """
        outline = {
            'stock_info': {
                'id': stock.stock_id,
                'name': stock.stock_name,
                'rank': stock.volume_rank,
                'rank_type': stock.rank_type,
                'change_percent': stock.change_percent,
                'volume_amount': stock.volume_amount
            },
            'apis_to_use': stock.assigned_apis,
            'content_sections': []
        }
        
        # 根據分配的API生成內容大綱
        for api_name in stock.assigned_apis:
            section = self._generate_section_outline(api_name, stock)
            outline['content_sections'].append(section)
        
        return outline
    
    def _generate_section_outline(self, api_name: str, stock: StockAnalysis) -> Dict[str, Any]:
        """
        生成API對應的內容大綱
        
        Args:
            api_name: API名稱
            stock: 股票資訊
            
        Returns:
            內容大綱
        """
        section_templates = {
            'serper': {
                'title': '最新市場動態',
                'content': f'使用Serper API搜尋{stock.stock_name}最新新聞、市場傳聞、產業動態',
                'keywords': ['最新消息', '市場傳聞', '產業動態', '投資人關注']
            },
            'finlab_financial': {
                'title': '財報基本面分析',
                'content': f'分析{stock.stock_name}的營收、EPS、毛利率等財務指標',
                'keywords': ['營收成長', 'EPS表現', '毛利率', '財務體質']
            },
            'monthly_revenue': {
                'title': '月營收分析',
                'content': f'分析{stock.stock_name}最新月營收數據、成長率、營收趨勢',
                'keywords': ['月營收', '營收成長率', '營收趨勢', '業績表現']
            },
            'technical_analysis': {
                'title': '技術面分析',
                'content': f'分析{stock.stock_id}的技術指標、支撐壓力位、趨勢研判',
                'keywords': ['技術指標', '支撐壓力', '趨勢研判', '買賣點位']
            },
            'volume_analysis': {
                'title': '成交量分析',
                'content': f'分析{stock.stock_name}的成交量排名第{stock.volume_rank}名，成交金額{self._format_volume_amount(stock.volume_amount)}',
                'keywords': ['成交量', '資金流向', '籌碼分析', '市場熱度']
            }
        }
        
        return section_templates.get(api_name, {
            'title': '其他分析',
            'content': f'對{stock.stock_name}進行綜合分析',
            'keywords': ['綜合分析']
        })
    
    def _format_volume_amount(self, amount_billion: float) -> str:
        """
        格式化成交金額顯示
        
        Args:
            amount_billion: 成交金額（億元）
            
        Returns:
            格式化後的成交金額字符串
        """
        if amount_billion >= 1.0:
            return f"{amount_billion:.4f}億元"
        else:
            # 轉換為百萬元
            amount_million = amount_billion * 100
            return f"{amount_million:.2f}百萬元"

def main():
    """主函數 - 測試智能調配系統"""
    
    # 創建調配器
    allocator = SmartAPIAllocator()
    
    # 模擬股票數據（今日的漲停股票）
    sample_stocks = [
        StockAnalysis("3665", "股票3665", 1, 9.62, 86.3432, "成交金額排名"),
        StockAnalysis("3653", "股票3653", 2, 9.93, 59.4404, "成交金額排名"),
        StockAnalysis("5314", "股票5314", 3, 9.91, 31.8937, "成交金額排名"),
        StockAnalysis("6753", "股票6753", 4, 9.78, 31.4252, "成交金額排名"),
        StockAnalysis("8039", "股票8039", 5, 10.00, 20.2122, "成交金額排名"),
        StockAnalysis("3707", "股票3707", 6, 9.83, 15.3369, "成交金額排名"),
        StockAnalysis("3704", "股票3704", 7, 9.98, 14.4642, "成交金額排名"),
        StockAnalysis("4303", "股票4303", 8, 9.99, 11.6107, "成交金額排名"),
        StockAnalysis("1605", "股票1605", 9, 9.89, 10.3519, "成交金額排名"),
        StockAnalysis("2353", "股票2353", 10, 10.00, 9.5462, "成交金額排名"),
        StockAnalysis("5345", "股票5345", 1, 9.95, 0.0164, "成交金額排名（無量）"),
        StockAnalysis("2724", "股票2724", 2, 9.95, 0.0306, "成交金額排名（無量）"),
        StockAnalysis("6264", "股票6264", 3, 10.00, 0.0326, "成交金額排名（無量）"),
        StockAnalysis("8906", "股票8906", 4, 10.00, 0.0380, "成交金額排名（無量）"),
        StockAnalysis("2380", "股票2380", 5, 9.97, 0.0406, "成交金額排名（無量）")
    ]
    
    # 執行智能調配
    allocated_stocks = allocator.allocate_apis_for_stocks(sample_stocks)
    
    # 生成內容大綱示例
    print("\n📝 內容大綱示例（前3篇）:")
    print("=" * 60)
    
    for i, stock in enumerate(allocated_stocks[:3]):
        outline = allocator.generate_content_outline(stock)
        print(f"\n📄 第{i+1}篇: {stock.stock_name}({stock.stock_id})")
        print(f"   排名: {stock.rank_type} 第{stock.volume_rank}名")
        print(f"   使用API: {', '.join(outline['apis_to_use'])}")
        print("   內容大綱:")
        
        for section in outline['content_sections']:
            print(f"   - {section['title']}: {section['content']}")
        
        print()
    
    # 特別檢查無量股票的成交量格式化
    print("\n🔍 無量股票成交量格式化檢查:")
    print("=" * 40)
    for stock in allocated_stocks:
        if stock.volume_amount < 1.0:
            formatted_amount = allocator._format_volume_amount(stock.volume_amount)
            print(f"{stock.stock_name}({stock.stock_id}): {stock.volume_amount:.4f}億元 -> {formatted_amount}")

if __name__ == "__main__":
    main()
