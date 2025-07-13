#!/usr/bin/env python3
"""
Test script for the Flask API endpoints
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, expected_status=200):
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"{method} {endpoint} -> Status: {response.status_code}")
        
        if response.status_code == expected_status:
            try:
                data = response.json()
                print(f"✅ Response: {data.get('message', 'No message')}")
                return True
            except json.JSONDecodeError:
                print(f"✅ Response received (non-JSON)")
                return True
        else:
            print(f"❌ Expected {expected_status}, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - Is the API running on {BASE_URL}?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Test all API endpoints."""
    print("🧪 Testing Resume Extractor Flask API")
    print("=" * 50)
    
    # Test basic endpoints
    tests = [
        ("GET", "/", 200),
        ("GET", "/health", 200),
        ("GET", "/status", 200),
        ("GET", "/config", 200),
        ("POST", "/start", 200),  # Start the bot
        ("GET", "/status", 200),  # Check status after start
        ("POST", "/stop", 200),   # Stop the bot
        ("GET", "/status", 200),  # Check status after stop
        ("GET", "/nonexistent", 404),  # Test 404 handler
    ]
    
    passed = 0
    total = len(tests)
    
    for method, endpoint, expected_status in tests:
        print(f"\n🔍 Testing {method} {endpoint}")
        if test_endpoint(method, endpoint, expected_status):
            passed += 1
        
        # Small delay between tests
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
