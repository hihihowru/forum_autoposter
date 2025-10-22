# API Testing Best Practices for Forum AutoPoster

## 🎯 Current API Status Summary

Based on the comprehensive API test results:

### ✅ **Working APIs (30/35)**
- **Core Health**: `/`, `/health` 
- **After Hours Triggers**: All 6 working! ✅
  - `/after_hours_limit_up` - 盤後漲
  - `/after_hours_limit_down` - 盤後跌  
  - `/after_hours_volume_amount_high` - 成交金額高 ✅ **NEW**
  - `/after_hours_volume_amount_low` - 成交金額低 ✅ **NEW**
  - `/after_hours_volume_change_rate_high` - 成交金額變化率高 ✅ **NEW**
  - `/after_hours_volume_change_rate_low` - 成交金額變化率低 ✅ **NEW**
- **Stock Data**: `/stock_mapping.json`, `/industries`, `/stocks_by_industry`, `/get_ohlc`
- **Posting Services**: `/api/posting`, `/api/manual-posting`
- **Dashboard**: `/dashboard/system-monitoring`, `/dashboard/content-management`, `/dashboard/interaction-analysis`
- **Content Management**: `/posts`, `/trending`, `/extract-keywords`, `/search-stocks-by-keywords`, `/analyze-topic`, `/generate-content`
- **KOL Management**: `/api/kol/list` ✅ **FIXED!**
- **Schedule Management**: `/api/schedule/tasks`, `/api/schedule/daily-stats`, `/api/schedule/scheduler/status`

### ⚠️ **Conditional APIs (1/35)**
- **Intraday Trigger**: `/intraday-trigger/execute` (works but may fail due to CMoney API issues)

### ⚠️ **Admin APIs (7/35)**
- All admin endpoints return 200 but may need authentication

### 🐌 **Slow APIs**
- `/get_ohlc`: 11.7s (FinLab API dependency)

---

## 🔧 API Testing Best Practices

### 1. **Automated Testing Strategy**

#### **Health Checks**
```python
# Basic health check
def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

#### **Response Time Monitoring**
```python
# Performance testing
def test_response_times():
    endpoints = ["/health", "/api/kol/list", "/posts"]
    for endpoint in endpoints:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}")
        response_time = time.time() - start_time
        
        assert response_time < 2.0, f"{endpoint} too slow: {response_time:.2f}s"
```

#### **Data Validation**
```python
# Schema validation
def test_kol_list_structure():
    response = requests.get(f"{BASE_URL}/api/kol/list")
    data = response.json()
    
    assert "success" in data
    assert "data" in data  # Fixed: was "kols"
    assert isinstance(data["data"], list)
    
    if data["data"]:
        kol = data["data"][0]
        required_fields = ["serial", "nickname", "persona", "prompt_persona"]
        for field in required_fields:
            assert field in kol, f"Missing field: {field}"
```

### 2. **Error Handling Patterns**

#### **Graceful Degradation**
```python
def test_error_responses():
    # Test 404 handling
    response = requests.get(f"{BASE_URL}/nonexistent")
    assert response.status_code == 404
    
    # Test 500 handling
    response = requests.post(f"{BASE_URL}/intraday-trigger/execute", json={})
    if response.status_code == 500:
        error_data = response.json()
        assert "error" in error_data
```

#### **Retry Logic**
```python
def test_with_retry(endpoint, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 3. **Monitoring & Alerting**

#### **Continuous Monitoring**
```python
# Set up monitoring for critical endpoints
CRITICAL_ENDPOINTS = [
    "/health",
    "/api/kol/list", 
    "/api/schedule/tasks",
    "/after_hours_limit_up",
    "/after_hours_limit_down"
]

def monitor_critical_endpoints():
    for endpoint in CRITICAL_ENDPOINTS:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code != 200:
                send_alert(f"Endpoint {endpoint} returned {response.status_code}")
        except Exception as e:
            send_alert(f"Endpoint {endpoint} failed: {str(e)}")
```

#### **Performance Baselines**
```python
PERFORMANCE_BASELINES = {
    "/health": 0.1,  # 100ms
    "/api/kol/list": 0.2,  # 200ms
    "/posts": 0.5,  # 500ms
    "/get_ohlc": 15.0,  # 15s (FinLab dependency)
}

def check_performance():
    for endpoint, max_time in PERFORMANCE_BASELINES.items():
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}")
        response_time = time.time() - start_time
        
        if response_time > max_time:
            send_alert(f"Performance degradation: {endpoint} took {response_time:.2f}s")
```

### 4. **Testing Environments**

#### **Environment-Specific Testing**
```python
ENVIRONMENTS = {
    "production": "https://forumautoposter-production.up.railway.app",
    "staging": "https://forumautoposter-staging.up.railway.app",
    "local": "http://localhost:8001"
}

def test_all_environments():
    for env_name, base_url in ENVIRONMENTS.items():
        print(f"Testing {env_name} environment...")
        tester = APITester(base_url)
        results = tester.test_all_endpoints()
        # Generate environment-specific reports
```

### 5. **API Documentation & Validation**

#### **OpenAPI/Swagger Integration**
```python
def validate_api_docs():
    # Test that all documented endpoints exist
    swagger_url = f"{BASE_URL}/docs"
    response = requests.get(swagger_url)
    assert response.status_code == 200
    
    # Validate response schemas match documentation
    # This would require parsing OpenAPI spec
```

#### **Contract Testing**
```python
def test_api_contracts():
    # Test that API responses match expected contracts
    contracts = {
        "/api/kol/list": {
            "required_fields": ["success", "data", "count"],
            "data_type": "array",
            "item_fields": ["serial", "nickname", "persona"]
        }
    }
    
    for endpoint, contract in contracts.items():
        response = requests.get(f"{BASE_URL}{endpoint}")
        data = response.json()
        
        for field in contract["required_fields"]:
            assert field in data, f"Missing required field: {field}"
```

---

## 🚨 **Critical Issues to Address**

### 1. **Intraday Trigger 500 Error**
```python
# Debug the intraday trigger
def debug_intraday_trigger():
    response = requests.post(f"{BASE_URL}/intraday-trigger/execute", 
                           json={"stock_id": "2330"})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    # Check logs for specific error
```

### 2. **After Hours Triggers Status**
✅ **Good News**: Both after_hours triggers are working!
- `/after_hours_limit_up` ✅
- `/after_hours_limit_down` ✅

You mentioned "only 2 out of 6 work" - but I only found 2 after_hours endpoints. The other 4 might be:
- Volume-based triggers
- Sector-based triggers  
- Earnings-based triggers
- News-based triggers

### 3. **Performance Optimization**
- `/get_ohlc` is slow (11.7s) due to FinLab API dependency
- Consider caching or async processing

---

## 🛠️ **Recommended Testing Workflow**

### **Daily Health Checks**
```bash
# Run basic health check
python3 api_test_script.py

# Check specific endpoints
python3 api_test_script.py https://forumautoposter-production.up.railway.app
```

### **Weekly Comprehensive Testing**
```bash
# Full test suite with detailed reporting
python3 api_test_script.py > weekly_report.txt
```

### **Before Deployment**
```bash
# Test staging environment
python3 api_test_script.py https://forumautoposter-staging.up.railway.app

# Test production after deployment
python3 api_test_script.py https://forumautoposter-production.up.railway.app
```

---

## 📊 **API Metrics Dashboard**

Track these key metrics:
- **Uptime**: % of time APIs are responding
- **Response Time**: Average response time per endpoint
- **Error Rate**: % of failed requests
- **Data Quality**: Schema validation results
- **Coverage**: % of endpoints tested

---

## 🔍 **Next Steps**

1. **Fix Intraday Trigger**: Debug the 500 error
2. **Identify Missing Triggers**: Find the other 4 after_hours triggers
3. **Performance Optimization**: Cache slow endpoints
4. **Monitoring Setup**: Implement continuous monitoring
5. **Documentation**: Update API docs with current status

The API testing script is now ready for regular use! 🚀
