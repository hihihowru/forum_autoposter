#!/usr/bin/env python3
"""
Fix after-hours volume trigger endpoints to include all required fields
"""

import re

file_path = "docker-container/finlab python/apps/unified-api/main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match the volume_amount_stocks.append block
old_pattern = r"""                # 計算成交金額
                volume_amount = 0
                if latest_volume is not None and stock_id in latest_volume.index:
                    vol = latest_volume\[stock_id\]
                    if not pd\.isna\(vol\):
                        volume_amount = int\(vol\) \* float\(today_price\)

                volume_amount_stocks\.append\(\{
                    'stock_id': stock_id,
                    'stock_name': get_stock_name\(stock_id\),
                    'price': float\(today_price\),
                    'change_amount': float\(today_price - yesterday_price\),
                    'change_percent': float\(change_percent\),
                    'volume_amount': volume_amount,
                    'date': latest_date\.strftime\('%Y-%m-%d'\),
                    'previous_date': previous_date\.strftime\('%Y-%m-%d'\)
                \}\)"""

new_replacement = """                # 計算成交金額和成交量
                volume_amount = 0
                volume = 0
                if latest_volume is not None and stock_id in latest_volume.index:
                    vol = latest_volume[stock_id]
                    if not pd.isna(vol):
                        volume = int(vol)
                        volume_amount = volume * float(today_price)

                # 計算五日統計
                stats = calculate_trading_stats(stock_id, latest_date, close_df)

                volume_amount_stocks.append({
                    'stock_id': stock_id,
                    'stock_name': get_stock_name(stock_id),
                    'industry': get_stock_industry(stock_id),
                    'price': float(today_price),
                    'change_amount': float(today_price - yesterday_price),
                    'change_percent': float(change_percent),
                    'volume': volume,
                    'volume_amount': volume_amount,
                    'up_days_5': stats['up_days'],
                    'five_day_change': stats['five_day_change'],
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'previous_date': previous_date.strftime('%Y-%m-%d')
                })"""

content = re.sub(old_pattern, new_replacement, content)

# Now fix the volume_change_stocks.append blocks (2 instances)
old_change_pattern = r"""                volume_change_stocks\.append\(\{
                    'stock_id': stock_id,
                    'stock_name': get_stock_name\(stock_id\),
                    'price': float\(today_price\),
                    'change_amount': float\(today_price - yesterday_price\),
                    'change_percent': float\(change_percent\),
                    'volume_amount': volume_amount,
                    'volume_change_rate': volume_change_rate,
                    'date': latest_date\.strftime\('%Y-%m-%d'\),
                    'previous_date': previous_date\.strftime\('%Y-%m-%d'\)
                \}\)"""

new_change_replacement = """                # 計算五日統計
                stats = calculate_trading_stats(stock_id, latest_date, close_df)

                volume_change_stocks.append({
                    'stock_id': stock_id,
                    'stock_name': get_stock_name(stock_id),
                    'industry': get_stock_industry(stock_id),
                    'price': float(today_price),
                    'change_amount': float(today_price - yesterday_price),
                    'change_percent': float(change_percent),
                    'volume': int(latest_volume[stock_id]) if latest_volume is not None and stock_id in latest_volume.index and not pd.isna(latest_volume[stock_id]) else 0,
                    'volume_amount': volume_amount,
                    'volume_change_rate': volume_change_rate,
                    'up_days_5': stats['up_days'],
                    'five_day_change': stats['five_day_change'],
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'previous_date': previous_date.strftime('%Y-%m-%d')
                })"""

content = re.sub(old_change_pattern, new_change_replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all 4 volume endpoints!")
