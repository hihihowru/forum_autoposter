# Add this endpoint to the unified API main.py file

@app.post("/admin/import-1788-posts")
async def import_1788_posts():
    """導入 1788 筆 post_records 數據（管理員功能）"""
    try:
        if not db_connection:
            return {"error": "數據庫連接不存在"}
        
        # 讀取 JSON 數據文件
        json_file_path = '/app/post_records_1788.json'
        if not os.path.exists(json_file_path):
            return {"error": "post_records_1788.json 文件不存在"}
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        logger.info(f"📊 從 JSON 文件加載 {len(records)} 筆記錄")
        
        with db_connection.cursor() as cursor:
            # 清空現有數據
            cursor.execute("DELETE FROM post_records")
            logger.info("🗑️ 清空現有數據")
            
            # 批量插入數據
            insert_sql = """
                INSERT INTO post_records (
                    post_id, created_at, updated_at, session_id, kol_serial, kol_nickname, 
                    kol_persona, stock_code, stock_name, title, content, content_md, 
                    status, reviewer_notes, approved_by, approved_at, scheduled_at, 
                    published_at, cmoney_post_id, cmoney_post_url, publish_error, 
                    views, likes, comments, shares, topic_id, topic_title, 
                    technical_analysis, serper_data, quality_score, ai_detection_score, 
                    risk_level, generation_params, commodity_tags, alternative_versions
                ) VALUES (
                    %(post_id)s, %(created_at)s, %(updated_at)s, %(session_id)s, 
                    %(kol_serial)s, %(kol_nickname)s, %(kol_persona)s, %(stock_code)s, 
                    %(stock_name)s, %(title)s, %(content)s, %(content_md)s, %(status)s, 
                    %(reviewer_notes)s, %(approved_by)s, %(approved_at)s, %(scheduled_at)s, 
                    %(published_at)s, %(cmoney_post_id)s, %(cmoney_post_url)s, 
                    %(publish_error)s, %(views)s, %(likes)s, %(comments)s, %(shares)s, 
                    %(topic_id)s, %(topic_title)s, %(technical_analysis)s, %(serper_data)s, 
                    %(quality_score)s, %(ai_detection_score)s, %(risk_level)s, 
                    %(generation_params)s, %(commodity_tags)s, %(alternative_versions)s
                )
            """
            
            # 轉換記錄格式
            records_dict = []
            for record in records:
                record_dict = dict(record)
                
                # 處理 datetime 字符串
                for datetime_field in ['created_at', 'updated_at', 'approved_at', 'scheduled_at', 'published_at']:
                    if record_dict.get(datetime_field):
                        if isinstance(record_dict[datetime_field], str):
                            try:
                                record_dict[datetime_field] = datetime.fromisoformat(record_dict[datetime_field].replace('Z', '+00:00'))
                            except:
                                record_dict[datetime_field] = None
                        elif not isinstance(record_dict[datetime_field], datetime):
                            record_dict[datetime_field] = None
                    else:
                        record_dict[datetime_field] = None
                
                # 處理 JSON 字段 - 確保是字符串格式
                for json_field in ['technical_analysis', 'serper_data', 'generation_params', 'commodity_tags', 'alternative_versions']:
                    if record_dict.get(json_field):
                        if isinstance(record_dict[json_field], (dict, list)):
                            # 如果是字典或列表，轉換為 JSON 字符串
                            try:
                                record_dict[json_field] = json.dumps(record_dict[json_field], ensure_ascii=False)
                            except:
                                record_dict[json_field] = None
                        elif isinstance(record_dict[json_field], str):
                            # 如果已經是字符串，保持不變
                            pass
                        else:
                            record_dict[json_field] = None
                    else:
                        record_dict[json_field] = None
                
                records_dict.append(record_dict)
            
            # 批量插入
            logger.info(f"📥 開始插入 {len(records_dict)} 筆記錄...")
            cursor.executemany(insert_sql, records_dict)
            db_connection.commit()
            
            logger.info(f"✅ 成功導入 {len(records_dict)} 筆記錄")
            
            # 驗證導入結果
            cursor.execute("SELECT COUNT(*) FROM post_records")
            count = cursor.fetchone()[0]
            
            # 顯示狀態統計
            cursor.execute("SELECT status, COUNT(*) FROM post_records GROUP BY status")
            status_stats = cursor.fetchall()
            
            return {
                "success": True,
                "message": f"成功導入 {len(records_dict)} 筆記錄",
                "total_count": count,
                "status_stats": {status: count for status, count in status_stats},
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ 導入 1788 筆記錄失敗: {e}")
        return {"error": str(e)}
