# 智能學習機制使用範例

## 🚀 快速開始

### 1. 基本使用流程

```python
from src.services.learning.learning_orchestrator import LearningOrchestrator

# 初始化學習協調器
orchestrator = LearningOrchestrator()

# 1. 開始學習會話
session_id = await orchestrator.start_learning_session("kol_001", "content_123")

# 2. 準備互動數據
interaction_data = {
    "content_id": "content_123",
    "kol_id": "kol_001",
    "content_type": "technical",
    "topic_category": "stock_analysis",
    "generated_content": "台積電技術面分析：目前處於上升趨勢...",
    "posting_time": "2024-01-15T10:00:00Z",
    "likes_count": 150,
    "comments_count": 25,
    "shares_count": 10,
    "saves_count": 5,
    "views_count": 1000,
    "comments": [
        {
            "id": "comment_1",
            "content": "分析得很詳細，感謝分享！",
            "is_reply": False
        },
        {
            "id": "comment_2", 
            "content": "看起來像AI寫的...",
            "is_reply": False
        }
    ]
}

# 3. 處理互動數據
results = await orchestrator.process_interaction_data(session_id, interaction_data)

# 4. 查看結果
print("AI偵測結果:", results['ai_detection'])
print("互動指標:", results['engagement_metrics'])
print("學習洞察:", results['insights'])
```

### 2. 生成學習報告

```python
# 生成7天學習報告
report = await orchestrator.generate_learning_report("kol_001", days=7)

print(f"報告期間: {report.period_start} - {report.period_end}")
print(f"總發文數: {report.total_posts}")
print(f"平均互動率: {report.avg_engagement_score:.3f}")
print(f"平均AI偵測分數: {report.avg_ai_detection_score:.3f}")

# 查看洞察和建議
for insight in report.insights:
    print(f"洞察類型: {insight.insight_type}")
    print(f"描述: {insight.description}")
    print(f"建議: {insight.recommended_action}")
    print(f"預期改善: {insight.expected_improvement:.2f}")
    print("---")
```

## 🔍 AI偵測使用範例

### 1. 單一內容AI偵測

```python
from src.services.learning.ai_detection_service import AIDetectionService

detector = AIDetectionService()

# 偵測AI生成內容
content = """
根據技術分析，台積電目前處於上升趨勢。
基於MA5和MA20的黃金交叉，我們可以預期股價將持續上漲。
綜合分析來看，建議投資者可以考慮買入。
"""

result = await detector.detect_ai_content(content, "content_001")

print(f"AI偵測分數: {result.detection_score:.3f}")
print(f"風險等級: {result.risk_level}")
print(f"偵測信號: {result.detection_signals}")
print(f"改進建議: {result.recommendations}")
```

### 2. 批量分析留言

```python
comments = [
    {"id": "1", "content": "分析得很棒！"},
    {"id": "2", "content": "看起來像AI寫的，太正式了"},
    {"id": "3", "content": "我覺得這個分析有道理"},
    {"id": "4", "content": "根據數據顯示，這個結論是正確的"}
]

analyses = await detector.analyze_comments(comments)

for analysis in analyses:
    print(f"留言ID: {analysis.comment_id}")
    print(f"AI偵測分數: {analysis.ai_detection_score:.3f}")
    print(f"情感分數: {analysis.sentiment_score:.3f}")
    print(f"品質分數: {analysis.quality_score:.3f}")
    print(f"可疑模式: {analysis.suspicious_patterns}")
    print("---")
```

## 📊 互動成效分析範例

### 1. 分析互動數據

```python
from src.services.learning.engagement_analyzer import EngagementAnalyzer

analyzer = EngagementAnalyzer()

# 準備互動數據
interaction_data = [
    {
        "content_id": "content_001",
        "kol_id": "kol_001",
        "content_type": "technical",
        "topic_category": "stock_analysis",
        "posting_time": "2024-01-15T10:00:00Z",
        "likes_count": 150,
        "comments_count": 25,
        "shares_count": 10,
        "saves_count": 5,
        "views_count": 1000,
        "comments": [
            {"content": "很好的分析", "is_reply": False},
            {"content": "感謝分享", "is_reply": False}
        ]
    },
    {
        "content_id": "content_002",
        "kol_id": "kol_001", 
        "content_type": "news",
        "topic_category": "market_news",
        "posting_time": "2024-01-15T14:00:00Z",
        "likes_count": 80,
        "comments_count": 15,
        "shares_count": 5,
        "saves_count": 2,
        "views_count": 800,
        "comments": [
            {"content": "新聞很及時", "is_reply": False}
        ]
    }
]

# 分析互動成效
metrics = await analyzer.analyze_engagement_data(interaction_data)

for metric in metrics:
    print(f"內容ID: {metric.content_id}")
    print(f"互動率: {metric.engagement_rate:.3f}")
    print(f"留言率: {metric.comment_rate:.3f}")
    print(f"分享率: {metric.share_rate:.3f}")
    print(f"平均留言長度: {metric.avg_comment_length:.1f}")
    print(f"正面情感比例: {metric.positive_sentiment_ratio:.3f}")
    print("---")
```

### 2. 生成互動洞察

```python
# 生成互動洞察
insights = await analyzer.generate_engagement_insights(metrics)

for insight in insights:
    print(f"洞察類型: {insight.insight_type}")
    print(f"描述: {insight.description}")
    print(f"信心度: {insight.confidence:.2f}")
    print(f"建議: {insight.recommendation}")
    print(f"預期影響: {insight.expected_impact:.2f}")
    print("---")
```

### 3. 計算表現基準

```python
# 計算表現基準
benchmarks = analyzer.calculate_benchmarks(metrics)

for benchmark_name, benchmark in benchmarks.items():
    print(f"基準名稱: {benchmark_name}")
    print(f"當前值: {benchmark.current_value:.3f}")
    print(f"基準值: {benchmark.benchmark_value:.3f}")
    print(f"百分位數: {benchmark.percentile:.1f}%")
    print(f"趨勢: {benchmark.trend}")
    print("---")
```

## 🧠 學習引擎使用範例

### 1. 分析學習指標

```python
from src.services.learning.learning_engine import LearningEngine

engine = LearningEngine()

# 準備學習數據
learning_data = [
    {
        "kol_id": "kol_001",
        "content_type": "technical",
        "topic_category": "stock_analysis",
        "engagement_score": 0.15,
        "ai_detection_score": 0.3,
        "sentiment_score": 0.7,
        "interaction_count": 190,
        "comment_quality_score": 0.8
    }
]

# 分析學習指標
metrics = await engine.analyze_interaction_effectiveness(learning_data)

for metric in metrics:
    print(f"KOL ID: {metric.kol_id}")
    print(f"互動分數: {metric.engagement_score:.3f}")
    print(f"AI偵測分數: {metric.ai_detection_score:.3f}")
    print(f"情感分數: {metric.sentiment_score:.3f}")
    print(f"留言品質分數: {metric.comment_quality_score:.3f}")
    print("---")
```

### 2. 生成學習洞察

```python
# 生成學習洞察
insights = await engine.generate_learning_insights(metrics)

for insight in insights:
    print(f"洞察類型: {insight.insight_type}")
    print(f"KOL ID: {insight.kol_id}")
    print(f"描述: {insight.description}")
    print(f"信心度: {insight.confidence:.2f}")
    print(f"建議: {insight.recommended_action}")
    print(f"預期改善: {insight.expected_improvement:.2f}")
    print("---")
```

### 3. 更新KOL策略

```python
# 更新KOL策略
strategy_updates = await engine.update_kol_strategies(insights)

for kol_id, strategy in strategy_updates.items():
    print(f"KOL ID: {kol_id}")
    print(f"內容類型權重: {strategy.content_type_weights}")
    print(f"人格調整: {strategy.persona_adjustments}")
    print(f"時機偏好: {strategy.timing_preferences}")
    print(f"最後更新: {strategy.last_updated}")
    print("---")
```

### 4. 預測功能

```python
# 預測互動潛力
content_features = {
    "content_length": 500,
    "has_images": 1,
    "has_hashtags": 1,
    "posting_hour": 10,
    "topic_heat": 0.8,
    "kol_experience": 0.7
}

engagement_prediction = await engine.predict_engagement(content_features)
ai_detection_prediction = await engine.predict_ai_detection(content_features)

print(f"預測互動潛力: {engagement_prediction:.3f}")
print(f"預測AI偵測風險: {ai_detection_prediction:.3f}")
```

## 🌐 API使用範例

### 1. 使用FastAPI客戶端

```python
import requests
import json

# API基礎URL
BASE_URL = "http://localhost:8004"

# 1. 開始學習會話
session_response = requests.post(f"{BASE_URL}/learning/session/start", json={
    "kol_id": "kol_001",
    "content_id": "content_123"
})
session_id = session_response.json()["session_id"]

# 2. 處理互動數據
interaction_data = {
    "content_id": "content_123",
    "kol_id": "kol_001",
    "content_type": "technical",
    "topic_category": "stock_analysis",
    "generated_content": "台積電技術面分析...",
    "posting_time": "2024-01-15T10:00:00Z",
    "likes_count": 150,
    "comments_count": 25,
    "shares_count": 10,
    "saves_count": 5,
    "views_count": 1000,
    "comments": []
}

process_response = requests.post(
    f"{BASE_URL}/learning/session/{session_id}/process",
    json=interaction_data
)
results = process_response.json()["results"]

# 3. 生成學習報告
report_response = requests.get(f"{BASE_URL}/learning/report/kol_001?days=7")
report = report_response.json()["report"]

print(f"總發文數: {report['total_posts']}")
print(f"平均互動率: {report['avg_engagement_score']:.3f}")
print(f"平均AI偵測分數: {report['avg_ai_detection_score']:.3f}")

# 4. 獲取學習儀表板
dashboard_response = requests.get(f"{BASE_URL}/learning/dashboard")
dashboard = dashboard_response.json()["dashboard"]

print(f"活躍會話數: {dashboard['active_sessions']}")
print(f"總會話數: {dashboard['total_sessions']}")
```

### 2. 使用curl命令

```bash
# 開始學習會話
curl -X POST "http://localhost:8004/learning/session/start" \
  -H "Content-Type: application/json" \
  -d '{
    "kol_id": "kol_001",
    "content_id": "content_123"
  }'

# 處理互動數據
curl -X POST "http://localhost:8004/learning/session/session_123/process" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "content_123",
    "kol_id": "kol_001",
    "content_type": "technical",
    "topic_category": "stock_analysis",
    "generated_content": "台積電技術面分析...",
    "posting_time": "2024-01-15T10:00:00Z",
    "likes_count": 150,
    "comments_count": 25,
    "shares_count": 10,
    "saves_count": 5,
    "views_count": 1000,
    "comments": []
  }'

# 生成學習報告
curl -X GET "http://localhost:8004/learning/report/kol_001?days=7"

# 獲取學習儀表板
curl -X GET "http://localhost:8004/learning/dashboard"

# 健康檢查
curl -X GET "http://localhost:8004/learning/health"
```

## 🔧 批量處理範例

### 1. 批量處理歷史數據

```python
# 準備歷史數據
historical_data = [
    {
        "content_id": "content_001",
        "kol_id": "kol_001",
        "content_type": "technical",
        "generated_content": "台積電分析...",
        "posting_time": "2024-01-01T10:00:00Z",
        "likes_count": 100,
        "comments_count": 20,
        "shares_count": 5,
        "saves_count": 3,
        "views_count": 800
    },
    {
        "content_id": "content_002",
        "kol_id": "kol_001",
        "content_type": "news",
        "generated_content": "市場新聞...",
        "posting_time": "2024-01-02T14:00:00Z",
        "likes_count": 80,
        "comments_count": 15,
        "shares_count": 3,
        "saves_count": 2,
        "views_count": 600
    }
]

# 批量處理
results = await orchestrator.batch_process_historical_data(historical_data)

for kol_id, result in results.items():
    print(f"KOL ID: {kol_id}")
    print(f"總發文數: {result['total_posts']}")
    print(f"AI偵測摘要: {result['ai_detection_summary']}")
    print(f"互動摘要: {result['engagement_summary']}")
    print(f"洞察數量: {result['insights_count']}")
    print(f"策略已更新: {result['strategy_updated']}")
    print("---")
```

### 2. 訓練模型

```python
# 準備訓練數據
training_data = [
    {
        "content_length": 500,
        "has_images": 1,
        "has_hashtags": 1,
        "posting_hour": 10,
        "topic_heat": 0.8,
        "kol_experience": 0.7,
        "engagement_score": 0.15,
        "ai_detection_score": 0.3
    },
    {
        "content_length": 300,
        "has_images": 0,
        "has_hashtags": 0,
        "posting_hour": 14,
        "topic_heat": 0.6,
        "kol_experience": 0.5,
        "engagement_score": 0.08,
        "ai_detection_score": 0.5
    }
]

# 訓練模型
training_result = await orchestrator.train_models(training_data)

print(f"訓練狀態: {training_result['status']}")
print(f"訓練樣本數: {training_result['training_samples']}")
print(f"已訓練模型: {training_result['models_trained']}")
```

## 📈 監控和調試

### 1. 獲取學習狀態

```python
# 獲取KOL學習狀態
status = orchestrator.get_kol_learning_status("kol_001")

print(f"KOL ID: {status['kol_id']}")
print(f"總會話數: {status['total_sessions']}")
print(f"最後學習時間: {status['last_learning']}")
print(f"狀態: {status['status']}")

if status['strategy']:
    print(f"策略: {status['strategy']}")
```

### 2. 獲取學習儀表板

```python
# 獲取學習儀表板
dashboard = orchestrator.get_learning_dashboard()

print(f"活躍會話數: {dashboard['active_sessions']}")
print(f"總會話數: {dashboard['total_sessions']}")
print(f"學習引擎摘要: {dashboard['learning_engine_summary']}")

print("最近洞察:")
for insight in dashboard['recent_insights']:
    print(f"  KOL: {insight['kol_id']}")
    print(f"  內容: {insight['content_id']}")
    print(f"  洞察數: {insight['insights_count']}")
    print(f"  時間: {insight['timestamp']}")
    print("  ---")
```

## 🎯 最佳實踐

### 1. 定期學習

```python
import asyncio
from datetime import datetime, timedelta

async def daily_learning_routine():
    """每日學習例程"""
    orchestrator = LearningOrchestrator()
    
    # 獲取所有KOL
    kol_ids = ["kol_001", "kol_002", "kol_003"]
    
    for kol_id in kol_ids:
        try:
            # 生成每日學習報告
            report = await orchestrator.generate_learning_report(kol_id, days=1)
            
            # 檢查是否需要調整策略
            if report.avg_ai_detection_score > 0.4:
                print(f"警告: KOL {kol_id} AI偵測風險過高")
            
            if report.avg_engagement_score < 0.03:
                print(f"警告: KOL {kol_id} 互動率過低")
            
            # 記錄學習結果
            print(f"KOL {kol_id} 學習完成:")
            print(f"  發文數: {report.total_posts}")
            print(f"  互動率: {report.avg_engagement_score:.3f}")
            print(f"  AI偵測分數: {report.avg_ai_detection_score:.3f}")
            print(f"  洞察數: {len(report.insights)}")
            
        except Exception as e:
            print(f"KOL {kol_id} 學習失敗: {e}")

# 每日執行
asyncio.run(daily_learning_routine())
```

### 2. 錯誤處理

```python
async def safe_learning_process(session_id: str, interaction_data: dict):
    """安全的學習處理"""
    try:
        results = await orchestrator.process_interaction_data(session_id, interaction_data)
        return {"status": "success", "results": results}
    
    except ValueError as e:
        print(f"參數錯誤: {e}")
        return {"status": "error", "error": "invalid_parameters"}
    
    except Exception as e:
        print(f"處理失敗: {e}")
        return {"status": "error", "error": "processing_failed"}
```

### 3. 性能優化

```python
async def batch_learning_process(interaction_batch: list):
    """批量學習處理"""
    # 按KOL分組
    kol_groups = {}
    for data in interaction_batch:
        kol_id = data['kol_id']
        if kol_id not in kol_groups:
            kol_groups[kol_id] = []
        kol_groups[kol_id].append(data)
    
    # 並行處理每個KOL
    tasks = []
    for kol_id, kol_data in kol_groups.items():
        task = asyncio.create_task(
            process_kol_data(kol_id, kol_data)
        )
        tasks.append(task)
    
    # 等待所有任務完成
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

async def process_kol_data(kol_id: str, kol_data: list):
    """處理單個KOL的數據"""
    orchestrator = LearningOrchestrator()
    
    # 批量處理
    results = await orchestrator.batch_process_historical_data(kol_data)
    
    return {kol_id: results}
```

這些範例展示了如何使用智能學習機制的各個組件，從基本的單一內容分析到複雜的批量處理和模型訓練。通過這些範例，您可以快速上手並根據自己的需求進行定制。

