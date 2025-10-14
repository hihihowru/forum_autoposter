#!/usr/bin/env python3
"""
處理 TSV 數據並整合到互動分析系統
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# memberid 到 KOL Serial 的映射表
MEMBERID_TO_KOL_SERIAL = {
    9505537: 191,  # 雪山飛翔
    9505538: 192,  # 星夜
    9505539: 193,  # 紫羅蘭
    9505540: 194,  # 飛天魚
    9505541: 195,  # 霜雪
    9505542: 196,  # 花開
    9505543: 197,  # 雨天
    9505544: 198,  # 心悅
    9505545: 199,  # 青澀
    9505546: 200,  # 明月
    9505547: 201,  # 碧海
    9505548: 202,  # 雪落
    9505549: 203,  # 紅塵
    9505550: 204,  # 流風
    9505551: 205,  # 雲淡
    9505552: 206,  # 天空
    9505553: 207,  # 念慈
    9505554: 208,  # 綠葉
    9505555: 209,  # 童話
    9505556: 210,  # 露珠
}

# KOL Serial 到暱稱的映射
KOL_SERIAL_TO_NICKNAME = {
    191: "雪山飛翔",
    192: "星夜",
    193: "紫羅蘭",
    194: "飛天魚",
    195: "霜雪",
    196: "花開",
    197: "雨天",
    198: "心悅",
    199: "青澀",
    200: "明月",
    201: "碧海",
    202: "雪落",
    203: "紅塵",
    204: "流風",
    205: "雲淡",
    206: "天空",
    207: "念慈",
    208: "綠葉",
    209: "童話",
    210: "露珠",
}

def process_tsv_file(tsv_file_path: str) -> List[Dict[str, Any]]:
    """處理 TSV 文件並轉換為統一格式"""
    
    processed_posts = []
    
    with open(tsv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        
        for row in reader:
            try:
                # 解析數據
                article_id = row['articleid']
                member_id = int(row['memberid'])
                create_time = row['createtime']
                title = row['title']
                text = row['text']
                commodity_tags = row['commoditytags']
                
                # 映射到 KOL Serial
                kol_serial = MEMBERID_TO_KOL_SERIAL.get(member_id)
                if not kol_serial:
                    print(f"⚠️ 找不到 member_id {member_id} 對應的 KOL Serial")
                    continue
                
                # 獲取 KOL 暱稱
                kol_nickname = KOL_SERIAL_TO_NICKNAME.get(kol_serial, f"KOL-{kol_serial}")
                
                # 解析商品標籤
                try:
                    tags_data = json.loads(commodity_tags) if commodity_tags else []
                except json.JSONDecodeError:
                    tags_data = []
                
                # 生成 URL
                article_url = f"https://www.cmoney.tw/forum/article/{article_id}"
                
                # 創建統一的貼文記錄
                post_record = {
                    "post_id": f"external_{article_id}",  # 外部貼文 ID
                    "article_id": article_id,
                    "kol_serial": kol_serial,
                    "kol_nickname": kol_nickname,
                    "title": title,
                    "content": text,
                    "article_url": article_url,
                    "create_time": create_time,
                    "commodity_tags": tags_data,
                    "source": "external",  # 標記為外部數據
                    "status": "published",
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "bookmarks": 0,
                    "engagement_rate": 0.0
                }
                
                processed_posts.append(post_record)
                
            except Exception as e:
                print(f"❌ 處理行數據失敗: {e}")
                continue
    
    return processed_posts

def generate_interaction_analysis_data(processed_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成互動分析數據"""
    
    # 按 KOL 分組統計
    kol_stats = {}
    total_posts = len(processed_posts)
    
    for post in processed_posts:
        kol_serial = post['kol_serial']
        kol_nickname = post['kol_nickname']
        
        if kol_serial not in kol_stats:
            kol_stats[kol_serial] = {
                "kol_nickname": kol_nickname,
                "post_count": 0,
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_bookmarks": 0,
                "avg_engagement_rate": 0.0
            }
        
        kol_stats[kol_serial]["post_count"] += 1
        kol_stats[kol_serial]["total_views"] += post["views"]
        kol_stats[kol_serial]["total_likes"] += post["likes"]
        kol_stats[kol_serial]["total_comments"] += post["comments"]
        kol_stats[kol_serial]["total_shares"] += post["shares"]
        kol_stats[kol_serial]["total_bookmarks"] += post["bookmarks"]
    
    # 計算平均互動率
    for kol_serial in kol_stats:
        stats = kol_stats[kol_serial]
        total_interactions = stats["total_likes"] + stats["total_comments"] + stats["total_shares"]
        if stats["total_views"] > 0:
            stats["avg_engagement_rate"] = (total_interactions / stats["total_views"]) * 100
    
    return {
        "total_posts": total_posts,
        "kol_stats": kol_stats,
        "posts": processed_posts
    }

def main():
    """主函數"""
    tsv_file_path = "anya-forumteam-1758002569826-24188529182977924.tsv"
    
    if not os.path.exists(tsv_file_path):
        print(f"❌ TSV 文件不存在: {tsv_file_path}")
        return
    
    print("🔄 開始處理 TSV 數據...")
    
    # 處理 TSV 數據
    processed_posts = process_tsv_file(tsv_file_path)
    print(f"✅ 成功處理 {len(processed_posts)} 篇貼文")
    
    # 生成互動分析數據
    analysis_data = generate_interaction_analysis_data(processed_posts)
    
    # 輸出統計信息
    print("\n📊 處理結果統計:")
    print(f"總貼文數: {analysis_data['total_posts']}")
    print(f"KOL 數量: {len(analysis_data['kol_stats'])}")
    
    print("\n📋 KOL 發文統計:")
    for kol_serial, stats in analysis_data['kol_stats'].items():
        print(f"KOL {kol_serial} ({stats['kol_nickname']}): {stats['post_count']} 篇")
    
    # 保存處理後的數據
    output_file = "processed_external_posts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 處理後的數據已保存到: {output_file}")
    
    return analysis_data

if __name__ == "__main__":
    main()





















