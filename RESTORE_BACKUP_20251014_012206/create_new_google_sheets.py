#!/usr/bin/env python3
"""
創建新的 Google Sheets 並更新配置
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any

def print_instructions():
    """打印創建 Google Sheets 的說明"""
    print("=" * 60)
    print("📋 創建新的 Google Sheets 步驟")
    print("=" * 60)
    print()
    print("1️⃣ 創建新的 Google Sheets:")
    print("   • 前往 https://sheets.google.com")
    print("   • 點擊「+ 新增」創建新的試算表")
    print("   • 將第一個分頁重命名為「新貼文紀錄表」")
    print()
    print("2️⃣ 設置標題行（109個欄位）:")
    print("   在 A1:DD1 添加以下標題：")
    
    # 109個欄位的標題
    headers = [
        "post_id", "generation_time", "workflow_type", "trigger_type", "status", "priority_level", "batch_id",
        "kol_serial", "kol_nickname", "kol_id", "persona", "writing_style", "tone", "key_phrases", "avoid_topics",
        "preferred_data_sources", "kol_assignment_method", "kol_weight", "kol_version", "kol_learning_score",
        "stock_id", "stock_name", "topic_category", "analysis_type", "analysis_type_detail", "topic_priority",
        "topic_heat_score", "topic_id", "topic_title", "topic_keywords", "is_stock_trigger", "stock_trigger_type",
        "title", "content", "content_length", "content_style", "target_length", "weight", "random_seed",
        "content_quality_score", "content_type", "article_length_type", "content_length_vector", "tone_vector",
        "temperature_setting", "openai_model", "openai_tokens_used", "prompt_template", "sentiment_score",
        "ai_detection_risk_score", "personalization_level", "creativity_score", "coherence_score", "data_sources_used",
        "serper_api_called", "serper_api_results", "serper_api_summary_count", "finlab_api_called", "finlab_api_results",
        "cmoney_api_called", "cmoney_api_results", "data_quality_score", "data_freshness", "data_manager_dispatch",
        "trending_topics_summarized", "data_interpretability_score", "news_count", "news_summaries", "news_sentiment",
        "news_sources", "news_relevance_score", "news_freshness_score", "revenue_yoy_growth", "revenue_mom_growth",
        "eps_value", "eps_growth", "gross_margin", "net_margin", "financial_analysis_score", "price_change_percent",
        "volume_ratio", "rsi_value", "macd_signal", "ma_trend", "technical_analysis_score", "technical_confidence",
        "publish_time", "publish_platform", "publish_status", "interaction_count", "engagement_rate", "platform_post_id",
        "platform_post_url", "articleid", "learning_insights", "strategy_adjustments", "performance_improvement",
        "risk_alerts", "next_optimization_targets", "learning_cycle_count", "adaptive_score", "quality_check_rounds",
        "quality_issues_record", "regeneration_count", "quality_improvement_record", "body_parameter", "commodity_tags",
        "community_topic", "agent_decision_record"
    ]
    
    # 每行顯示10個欄位
    for i in range(0, len(headers), 10):
        row_headers = headers[i:i+10]
        print(f"   {chr(65+i//10)}1-{chr(65+min((i+9)//10, 25))}1: {', '.join(row_headers)}")
    
    print()
    print("3️⃣ 獲取新的 Google Sheets ID:")
    print("   • 從 URL 中複製 ID 部分")
    print("   • 格式: https://docs.google.com/spreadsheets/d/[ID]/edit")
    print()
    print("4️⃣ 設置權限:")
    print("   • 點擊「共用」按鈕")
    print("   • 添加服務帳號郵箱（從 credentials 文件獲取）")
    print("   • 設置為「編輯者」權限")
    print()

def get_service_account_email():
    """獲取服務帳號郵箱"""
    try:
        credentials_file = "credentials/google-service-account.json"
        if os.path.exists(credentials_file):
            with open(credentials_file, 'r') as f:
                data = json.load(f)
                return data.get('client_email', '未找到服務帳號郵箱')
        else:
            return "credentials 文件不存在"
    except Exception as e:
        return f"讀取失敗: {e}"

def update_configuration(new_sheets_id: str):
    """更新配置文件"""
    print(f"🔄 更新配置文件...")
    
    # 1. 更新 .env 文件
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # 替換 Google Sheets ID
        content = content.replace(
            'GOOGLE_SHEETS_ID=your_google_sheets_id_here',
            f'GOOGLE_SHEETS_ID={new_sheets_id}'
        )
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("✅ .env 文件已更新")
    except Exception as e:
        print(f"❌ 更新 .env 文件失敗: {e}")
    
    # 2. 更新主工作流程引擎
    try:
        workflow_file = "src/core/main_workflow_engine.py"
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        content = content.replace(
            'new_sheets_id = "your_google_sheets_id_here"',
            f'new_sheets_id = "{new_sheets_id}"'
        )
        
        with open(workflow_file, 'w') as f:
            f.write(content)
        
        print("✅ 主工作流程引擎已更新")
    except Exception as e:
        print(f"❌ 更新主工作流程引擎失敗: {e}")
    
    # 3. 更新其他相關文件
    files_to_update = [
        "src/operations/post_processing_manager.py",
        "upload_backup_to_sheets.py"
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                content = content.replace(
                    'your_google_sheets_id_here',
                    new_sheets_id
                )
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ {file_path} 已更新")
            except Exception as e:
                print(f"❌ 更新 {file_path} 失敗: {e}")

def test_new_sheets_connection(new_sheets_id: str):
    """測試新的 Google Sheets 連接"""
    print(f"🧪 測試新的 Google Sheets 連接...")
    
    try:
        from src.clients.google.sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient(
            credentials_file="credentials/google-service-account.json",
            spreadsheet_id=new_sheets_id
        )
        
        # 測試讀取
        result = client.read_sheet('新貼文紀錄表', 'A1:DD1')
        print("✅ 成功連接到新的 Google Sheets")
        print(f"📊 標題行包含 {len(result[0]) if result else 0} 個欄位")
        
        return True
    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 Google Sheets 配置更新工具")
    print("=" * 60)
    
    # 顯示服務帳號郵箱
    service_email = get_service_account_email()
    print(f"📧 服務帳號郵箱: {service_email}")
    print()
    
    # 顯示說明
    print_instructions()
    
    # 獲取新的 Google Sheets ID
    new_sheets_id = input("請輸入新的 Google Sheets ID: ").strip()
    
    if not new_sheets_id:
        print("❌ 未輸入 Google Sheets ID")
        return
    
    # 驗證 ID 格式
    if len(new_sheets_id) < 20:
        print("❌ Google Sheets ID 格式不正確")
        return
    
    print(f"📋 新的 Google Sheets ID: {new_sheets_id}")
    print()
    
    # 確認更新
    confirm = input("確認要更新所有配置文件嗎？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消更新")
        return
    
    # 更新配置
    update_configuration(new_sheets_id)
    print()
    
    # 測試連接
    test_new_sheets_connection(new_sheets_id)
    print()
    
    print("🎉 配置更新完成！")
    print("📝 請確保：")
    print("   1. 新的 Google Sheets 已設置正確的標題行")
    print("   2. 服務帳號有編輯權限")
    print("   3. 分頁名稱為「新貼文紀錄表」")
    print()
    print("🔗 新的 Google Sheets 連結:")
    print(f"   https://docs.google.com/spreadsheets/d/{new_sheets_id}/edit")

if __name__ == "__main__":
    main()
