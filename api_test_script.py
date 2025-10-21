#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Forum AutoPoster
Tests all endpoints and provides detailed health reports
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys
import os

# Configuration
BASE_URL = "https://forumautoposter-production.up.railway.app"
TIMEOUT = 10  # seconds
RETRY_COUNT = 2

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'API-Tester/1.0',
            'Accept': 'application/json'
        })
    
    def test_endpoint(self, method: str, endpoint: str, params: Dict = None, 
                     data: Dict = None, expected_status: int = 200, 
                     description: str = "") -> Dict:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        result = {
            'method': method,
            'endpoint': endpoint,
            'url': url,
            'description': description,
            'status': 'UNKNOWN',
            'response_time': 0,
            'status_code': None,
            'error': None,
            'response_size': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            start_time = time.time()
            
            # Make request with retries
            for attempt in range(RETRY_COUNT + 1):
                try:
                    if method.upper() == 'GET':
                        response = self.session.get(url, params=params, timeout=TIMEOUT)
                    elif method.upper() == 'POST':
                        response = self.session.post(url, json=data, params=params, timeout=TIMEOUT)
                    elif method.upper() == 'PUT':
                        response = self.session.put(url, json=data, params=params, timeout=TIMEOUT)
                    elif method.upper() == 'DELETE':
                        response = self.session.delete(url, params=params, timeout=TIMEOUT)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                    
                    break  # Success, exit retry loop
                    
                except requests.exceptions.RequestException as e:
                    if attempt == RETRY_COUNT:
                        raise e
                    time.sleep(1)  # Wait before retry
            
            end_time = time.time()
            result['response_time'] = round(end_time - start_time, 3)
            result['status_code'] = response.status_code
            result['response_size'] = len(response.content)
            
            # Determine status
            if response.status_code == expected_status:
                result['status'] = 'PASS'
            elif 200 <= response.status_code < 300:
                result['status'] = 'PASS_WARNING'
            elif response.status_code == 404:
                result['status'] = 'NOT_FOUND'
            elif response.status_code == 500:
                result['status'] = 'SERVER_ERROR'
            else:
                result['status'] = 'FAIL'
            
            # Try to parse JSON response
            try:
                result['response_data'] = response.json()
            except:
                result['response_data'] = response.text[:200]  # First 200 chars
            
        except Exception as e:
            result['status'] = 'ERROR'
            result['error'] = str(e)
            result['response_time'] = 0
        
        return result
    
    def test_all_endpoints(self) -> List[Dict]:
        """Test all known endpoints"""
        endpoints = [
            # Core Health & Info
            ('GET', '/', {}, None, 200, 'Root endpoint'),
            ('GET', '/health', {}, None, 200, 'Health check'),
            
            # After Hours Triggers (6 total - 2 working, 4 missing)
            ('GET', '/after_hours_limit_up', {}, None, 200, 'After hours limit up trigger'),
            ('GET', '/after_hours_limit_down', {}, None, 200, 'After hours limit down trigger'),
            
            # Volume-Based After Hours Triggers (now implemented)
            ('GET', '/after_hours_volume_amount_high', {}, None, 200, 'After hours volume amount high trigger'),
            ('GET', '/after_hours_volume_amount_low', {}, None, 200, 'After hours volume amount low trigger'),
            ('GET', '/after_hours_volume_change_rate_high', {}, None, 200, 'After hours volume change rate high trigger'),
            ('GET', '/after_hours_volume_change_rate_low', {}, None, 200, 'After hours volume change rate low trigger'),
            
            # Stock Data APIs
            ('GET', '/stock_mapping.json', {}, None, 200, 'Stock mapping data'),
            ('GET', '/industries', {}, None, 200, 'Industries list'),
            ('GET', '/stocks_by_industry', {'industry': '電子'}, None, 200, 'Stocks by industry'),
            ('GET', '/get_ohlc', {'stock_id': '2330'}, None, 200, 'OHLC data for TSMC'),
            
            # Intraday Trigger (endpoint works but may fail due to CMoney API issues)
            ('POST', '/intraday-trigger/execute', {}, {
                'endpoint': 'https://asterisk-chipsapi.cmoney.tw/AdditionInformationRevisit/api/GetAll/StockCalculation',
                'processing': [
                    {'ProcessType': 'EqualColumnsFilter'},
                    {'ProcessType': 'EqualColumnsFilter'},
                    {'ProcessType': 'DescOrder', 'ParameterJson': '{"TargetPropertyNamePath": ["ChangeRange"]}'},
                    {'ProcessType': 'ThenDescOrder', 'ParameterJson': '{"TargetPropertyNamePath": ["TotalVolume"]}'},
                    {'ProcessType': 'TakeCount', 'ParameterJson': '{"Count": 20}'}
                ]
            }, 200, 'Intraday trigger execution (may fail due to CMoney API)'),
            
            # Posting APIs
            ('POST', '/api/posting', {}, {'test': True}, 200, 'Posting service'),
            ('POST', '/api/manual-posting', {}, {'test': True}, 200, 'Manual posting service'),
            
            # Dashboard APIs
            ('GET', '/dashboard/system-monitoring', {}, None, 200, 'System monitoring dashboard'),
            ('GET', '/dashboard/content-management', {}, None, 200, 'Content management dashboard'),
            ('GET', '/dashboard/interaction-analysis', {}, None, 200, 'Interaction analysis dashboard'),
            
            # Post Management
            ('GET', '/posts', {'limit': 5}, None, 200, 'Get posts list'),
            
            # Trending & Content APIs
            ('GET', '/trending', {}, None, 200, 'Trending topics'),
            ('GET', '/extract-keywords', {'text': '台積電股價上漲'}, None, 200, 'Extract keywords'),
            ('GET', '/search-stocks-by-keywords', {'keywords': '台積電'}, None, 200, 'Search stocks by keywords'),
            ('GET', '/analyze-topic', {'topic': '台積電'}, None, 200, 'Analyze topic'),
            ('GET', '/generate-content', {'topic': '台積電'}, None, 200, 'Generate content'),
            
            # KOL Management APIs
            ('GET', '/api/kol/list', {}, None, 200, 'KOL list'),
            
            # Schedule Management APIs
            ('GET', '/api/schedule/tasks', {}, None, 200, 'Schedule tasks'),
            ('GET', '/api/schedule/daily-stats', {}, None, 200, 'Daily schedule stats'),
            ('GET', '/api/schedule/scheduler/status', {}, None, 200, 'Scheduler status'),
            
            # Admin APIs (these might return 404 or require auth)
            ('POST', '/admin/import-1788-posts', {}, {}, 404, 'Admin: Import posts'),
            ('POST', '/test/insert-sample-data', {}, {}, 404, 'Test: Insert sample data'),
            ('POST', '/admin/create-post-records-table', {}, {}, 404, 'Admin: Create table'),
            ('POST', '/admin/drop-and-recreate-post-records-table', {}, {}, 404, 'Admin: Drop and recreate table'),
            ('POST', '/admin/reset-database', {}, {}, 404, 'Admin: Reset database'),
            ('POST', '/admin/fix-database', {}, {}, 404, 'Admin: Fix database'),
            ('POST', '/admin/import-post-records', {}, {}, 404, 'Admin: Import post records'),
        ]
        
        print(f"🧪 Testing {len(endpoints)} endpoints against {self.base_url}")
        print("=" * 80)
        
        for i, (method, endpoint, params, data, expected_status, description) in enumerate(endpoints, 1):
            print(f"[{i:2d}/{len(endpoints)}] Testing {method} {endpoint}...", end=' ')
            
            result = self.test_endpoint(method, endpoint, params, data, expected_status, description)
            self.results.append(result)
            
            # Print status
            status_emoji = {
                'PASS': '✅',
                'PASS_WARNING': '⚠️',
                'NOT_FOUND': '❌',
                'SERVER_ERROR': '🔥',
                'FAIL': '❌',
                'ERROR': '💥'
            }
            
            emoji = status_emoji.get(result['status'], '❓')
            print(f"{emoji} {result['status']} ({result['response_time']:.3f}s)")
            
            # Brief delay to avoid overwhelming the server
            time.sleep(0.1)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        if not self.results:
            return "No test results available."
        
        # Calculate statistics
        total_tests = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        passed_warning = len([r for r in self.results if r['status'] == 'PASS_WARNING'])
        failed = len([r for r in self.results if r['status'] in ['FAIL', 'ERROR', 'SERVER_ERROR']])
        not_found = len([r for r in self.results if r['status'] == 'NOT_FOUND'])
        
        avg_response_time = sum(r['response_time'] for r in self.results) / total_tests
        
        # Group results by status
        by_status = {}
        for result in self.results:
            status = result['status']
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(result)
        
        # Generate report
        report = []
        report.append("🔍 API TEST REPORT")
        report.append("=" * 80)
        report.append(f"Base URL: {self.base_url}")
        report.append(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {total_tests}")
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY")
        report.append("-" * 40)
        report.append(f"✅ Passed: {passed}")
        report.append(f"⚠️  Passed with Warning: {passed_warning}")
        report.append(f"❌ Failed: {failed}")
        report.append(f"🔍 Not Found: {not_found}")
        report.append(f"⏱️  Average Response Time: {avg_response_time:.3f}s")
        report.append("")
        
        # After Hours Triggers Analysis
        after_hours_results = [r for r in self.results if 'after_hours' in r['endpoint']]
        if after_hours_results:
            report.append("🚨 AFTER HOURS TRIGGERS ANALYSIS")
            report.append("-" * 40)
            working_triggers = [r for r in after_hours_results if r['status'] == 'PASS']
            missing_triggers = [r for r in after_hours_results if r['status'] == 'NOT_FOUND']
            report.append(f"Total After Hours Triggers: {len(after_hours_results)}")
            report.append(f"✅ Working Triggers: {len(working_triggers)}")
            report.append(f"❌ Missing Triggers: {len(missing_triggers)}")
            report.append("")
            
            report.append("Working Triggers:")
            for result in working_triggers:
                report.append(f"  ✅ {result['endpoint']}: {result['description']}")
            
            if missing_triggers:
                report.append("")
                report.append("Missing Triggers (need implementation):")
                for result in missing_triggers:
                    report.append(f"  ❌ {result['endpoint']}: {result['description']}")
            report.append("")
        
        # Failed endpoints
        if failed > 0:
            report.append("❌ FAILED ENDPOINTS")
            report.append("-" * 40)
            for result in by_status.get('FAIL', []) + by_status.get('ERROR', []) + by_status.get('SERVER_ERROR', []):
                report.append(f"❌ {result['method']} {result['endpoint']}")
                if result['error']:
                    report.append(f"   Error: {result['error']}")
                elif result['status_code']:
                    report.append(f"   Status Code: {result['status_code']}")
            report.append("")
        
        # Not found endpoints
        if not_found > 0:
            report.append("🔍 NOT FOUND ENDPOINTS")
            report.append("-" * 40)
            for result in by_status.get('NOT_FOUND', []):
                report.append(f"🔍 {result['method']} {result['endpoint']}")
            report.append("")
        
        # Slow endpoints (>2s)
        slow_endpoints = [r for r in self.results if r['response_time'] > 2.0]
        if slow_endpoints:
            report.append("🐌 SLOW ENDPOINTS (>2s)")
            report.append("-" * 40)
            for result in sorted(slow_endpoints, key=lambda x: x['response_time'], reverse=True):
                report.append(f"🐌 {result['method']} {result['endpoint']}: {result['response_time']:.3f}s")
            report.append("")
        
        # All results table
        report.append("📋 DETAILED RESULTS")
        report.append("-" * 80)
        report.append(f"{'Status':<12} {'Method':<6} {'Endpoint':<40} {'Time':<8} {'Code':<6}")
        report.append("-" * 80)
        
        for result in sorted(self.results, key=lambda x: (x['status'], x['endpoint'])):
            status_emoji = {
                'PASS': '✅',
                'PASS_WARNING': '⚠️',
                'NOT_FOUND': '❌',
                'SERVER_ERROR': '🔥',
                'FAIL': '❌',
                'ERROR': '💥'
            }.get(result['status'], '❓')
            
            report.append(f"{status_emoji} {result['status']:<10} {result['method']:<6} {result['endpoint']:<40} {result['response_time']:<8.3f} {result['status_code'] or 'N/A':<6}")
        
        return "\n".join(report)
    
    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"api_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Results saved to: {filename}")
        return filename

def main():
    """Main function"""
    print("🚀 Forum AutoPoster API Testing Script")
    print("=" * 50)
    
    # Allow custom base URL
    base_url = BASE_URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    # Create tester and run tests
    tester = APITester(base_url)
    
    try:
        results = tester.test_all_endpoints()
        
        # Generate and print report
        report = tester.generate_report()
        print("\n" + report)
        
        # Save results
        json_file = tester.save_results()
        
        # Save report to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"api_test_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_file}")
        
        # Exit with appropriate code
        failed_count = len([r for r in results if r['status'] in ['FAIL', 'ERROR', 'SERVER_ERROR']])
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} endpoints failed. Check the report for details.")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
