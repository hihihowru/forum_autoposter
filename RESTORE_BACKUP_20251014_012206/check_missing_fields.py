#!/usr/bin/env python3
"""
檢查 record_data 中缺少的欄位
"""

def check_missing_fields():
    """檢查 record_data 中缺少的欄位"""
    
    # 定義完整的 109 個欄位
    all_fields = [
        'test_post_id', 'test_time', 'test_status', 'trigger_type', 'status',
        'priority_level', 'batch_id', 'kol_serial', 'kol_nickname', 'kol_id',
        'persona', 'writing_style', 'tone', 'key_phrases', 'avoid_topics',
        'preferred_data_sources', 'kol_assignment_method', 'kol_weight', 'kol_version',
        'kol_learning_score', 'stock_id', 'stock_name', 'topic_category', 'analysis_type',
        'analysis_type_detail', 'topic_priority', 'topic_heat_score', 'topic_id',
        'topic_title', 'topic_keywords', 'is_stock_trigger', 'stock_trigger_type',
        'title', 'content', 'content_length', 'content_style', 'target_length',
        'weight', 'random_seed', 'content_quality_score', 'content_type',
        'article_length_type', 'content_length_vector', 'tone_vector', 'temperature_setting',
        'openai_model', 'openai_tokens_used', 'prompt_template', 'sentiment_score',
        'ai_detection_risk_score', 'personalization_level', 'creativity_score',
        'coherence_score', 'data_sources_used', 'serper_api_called', 'serper_api_results',
        'serper_api_summary_count', 'finlab_api_called', 'finlab_api_results',
        'cmoney_api_called', 'cmoney_api_results', 'data_quality_score', 'data_freshness',
        'data_manager_dispatch', 'trending_topics_summarized', 'data_interpretability_score',
        'news_count', 'news_summaries', 'news_sentiment', 'news_sources',
        'news_relevance_score', 'news_freshness_score', 'revenue_yoy_growth',
        'revenue_mom_growth', 'eps_value', 'eps_growth', 'gross_margin', 'net_margin',
        'financial_analysis_score', 'price_change_percent', 'volume_ratio', 'rsi_value',
        'macd_signal', 'ma_trend', 'technical_analysis_score', 'technical_confidence',
        'publish_time', 'publish_platform', 'publish_status', 'interaction_count',
        'engagement_rate', 'platform_post_id', 'platform_post_url', 'articleid',
        'learning_insights', 'strategy_adjustments', 'performance_improvement',
        'risk_alerts', 'next_optimization_targets', 'learning_cycle_count',
        'adaptive_score', 'quality_check_rounds', 'quality_issues_record',
        'regeneration_count', 'quality_improvement_record', 'body_parameter',
        'commodity_tags', 'post_id', 'agent_decision_record'
    ]
    
    # 從代碼中提取的 record_data 欄位（根據實際代碼）
    defined_fields = [
        'test_post_id', 'test_time', 'test_status', 'trigger_type', 'status',
        'priority_level', 'batch_id', 'kol_serial', 'kol_nickname', 'kol_id',
        'persona', 'writing_style', 'tone', 'key_phrases', 'avoid_topics',
        'preferred_data_sources', 'kol_assignment_method', 'kol_weight', 'kol_version',
        'kol_learning_score', 'stock_id', 'stock_name', 'topic_category', 'analysis_type',
        'analysis_type_detail', 'topic_priority', 'topic_heat_score', 'topic_id',
        'topic_title', 'topic_keywords', 'is_stock_trigger', 'stock_trigger_type',
        'title', 'content', 'content_length', 'content_style', 'target_length',
        'weight', 'random_seed', 'content_quality_score', 'content_type',
        'article_length_type', 'content_length_vector', 'tone_vector', 'temperature_setting',
        'openai_model', 'openai_tokens_used', 'prompt_template', 'sentiment_score',
        'ai_detection_risk_score', 'personalization_level', 'creativity_score',
        'coherence_score', 'data_sources_used', 'serper_api_called', 'serper_api_results',
        'serper_api_summary_count', 'finlab_api_called', 'finlab_api_results',
        'cmoney_api_called', 'cmoney_api_results', 'data_quality_score', 'data_freshness',
        'data_manager_dispatch', 'trending_topics_summarized', 'data_interpretability_score',
        'news_count', 'news_summaries', 'news_sentiment', 'news_sources',
        'news_relevance_score', 'news_freshness_score', 'revenue_yoy_growth',
        'revenue_mom_growth', 'eps_value', 'eps_growth', 'gross_margin', 'net_margin',
        'financial_analysis_score', 'price_change_percent', 'volume_ratio', 'rsi_value',
        'macd_signal', 'ma_trend', 'technical_analysis_score', 'technical_confidence',
        'publish_time', 'publish_platform', 'publish_status', 'interaction_count',
        'engagement_rate', 'platform_post_id', 'platform_post_url', 'articleid',
        'learning_insights', 'strategy_adjustments', 'performance_improvement',
        'risk_alerts', 'next_optimization_targets', 'learning_cycle_count',
        'adaptive_score', 'quality_check_rounds', 'quality_issues_record',
        'regeneration_count', 'quality_improvement_record', 'body_parameter',
        'commodity_tags', 'post_id', 'agent_decision_record'
    ]
    
    print(f"完整欄位數量: {len(all_fields)}")
    print(f"已定義欄位數量: {len(defined_fields)}")
    
    # 檢查是否有缺少的欄位
    missing_fields = []
    for field in all_fields:
        if field not in defined_fields:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n缺少的欄位 ({len(missing_fields)} 個):")
        for field in missing_fields:
            print(f"  - {field}")
    else:
        print("\n✅ 所有欄位都已定義")
    
    # 檢查是否有多餘的欄位
    extra_fields = []
    for field in defined_fields:
        if field not in all_fields:
            extra_fields.append(field)
    
    if extra_fields:
        print(f"\n多餘的欄位 ({len(extra_fields)} 個):")
        for field in extra_fields:
            print(f"  - {field}")
    else:
        print("\n✅ 沒有多餘的欄位")

if __name__ == "__main__":
    check_missing_fields()












