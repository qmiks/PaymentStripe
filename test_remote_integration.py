#!/usr/bin/env python3
"""
Remote Stripe Integration Test Script
Tests the deployed application's Stripe integration via HTTP requests.
"""

import requests
import json
import time

# Configuration
BASE_URL = "https://paymentstripe-uee3a.ondigitalocean.app"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def test_application_availability():
    """Test if the application is accessible"""
    print("🌐 Testing application availability...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Application is accessible")
            return True
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Application not accessible: {e}")
        return False

def test_admin_panel_access():
    """Test admin panel accessibility"""
    print("\n👤 Testing admin panel access...")
    try:
        response = requests.get(f"{BASE_URL}/admin", timeout=10)
        if response.status_code == 200:
            print("✅ Admin panel is accessible")
            return True
        else:
            print(f"❌ Admin panel returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin panel not accessible: {e}")
        return False

def test_admin_login():
    """Test admin login functionality"""
    print("\n🔐 Testing admin login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json=ADMIN_CREDENTIALS,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Admin login successful")
                return data["access_token"]
            else:
                print("❌ Login response missing access token")
                return None
        else:
            print(f"❌ Admin login failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return None

def test_settings_retrieval(token):
    """Test settings retrieval with authentication"""
    print("\n⚙️ Testing settings retrieval...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/api/admin/settings", headers=headers, timeout=10)
        
        if response.status_code == 200:
            settings = response.json()
            print(f"✅ Settings retrieved successfully ({len(settings)} settings)")
            
            # Check for Stripe keys
            stripe_keys = {}
            for setting in settings:
                if setting["key"] in ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY", "STRIPE_WEBHOOK_SECRET"]:
                    stripe_keys[setting["key"]] = setting["value"]
            
            print("🔑 Stripe Keys Status:")
            for key, value in stripe_keys.items():
                if value and "your_" not in value and "placeholder" not in value:
                    print(f"   ✅ {key}: {value[:20]}...")
                else:
                    print(f"   ❌ {key}: Placeholder value detected")
            
            return stripe_keys
        else:
            print(f"❌ Settings retrieval failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Settings retrieval error: {e}")
        return None

def test_payment_methods_api():
    """Test payment methods API"""
    print("\n💳 Testing payment methods API...")
    try:
        response = requests.get(f"{BASE_URL}/api/checkout/payment-methods", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            methods = data.get("payment_methods", [])
            print(f"✅ Payment methods retrieved: {len(methods)} methods")
            for method in methods:
                print(f"   - {method['name']} ({method['code']})")
            return True
        else:
            print(f"❌ Payment methods API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Payment methods API error: {e}")
        return False

def test_currencies_api():
    """Test currencies API"""
    print("\n💰 Testing currencies API...")
    try:
        response = requests.get(f"{BASE_URL}/api/checkout/currencies", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            currencies = data.get("currencies", [])
            print(f"✅ Currencies retrieved: {len(currencies)} currencies")
            for currency in currencies:
                print(f"   - {currency['name']} ({currency['code']})")
            return True
        else:
            print(f"❌ Currencies API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Currencies API error: {e}")
        return False

def test_checkout_session_creation():
    """Test checkout session creation"""
    print("\n🛒 Testing checkout session creation...")
    try:
        payload = {
            "amount": 2000,
            "currency": "pln",
            "payment_method": "card"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/checkout/session",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "url" in data:
                print("✅ Checkout session created successfully")
                print(f"   Session URL: {data['url'][:50]}...")
                return True
            else:
                print("❌ Checkout session missing URL")
                return False
        else:
            print(f"❌ Checkout session creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Checkout session creation error: {e}")
        return False

def test_audit_logs_api(token):
    """Test audit logs API"""
    print("\n📝 Testing audit logs API...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/api/admin/audit-logs", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            print(f"✅ Audit logs retrieved: {len(logs)} logs")
            
            if logs:
                latest_log = logs[0]  # Assuming newest first
                print(f"   Latest action: {latest_log.get('action')}")
                print(f"   Latest user: {latest_log.get('username')}")
                print(f"   Latest timestamp: {latest_log.get('created_at')}")
            
            return True
        else:
            print(f"❌ Audit logs API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Audit logs API error: {e}")
        return False

def test_orders_api():
    """Test orders API"""
    print("\n📋 Testing orders API...")
    try:
        response = requests.get(f"{BASE_URL}/api/orders", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get("orders", [])
            print(f"✅ Orders API working: {len(orders)} orders found")
            return True
        else:
            print(f"❌ Orders API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Orders API error: {e}")
        return False

def run_remote_tests():
    """Run all remote integration tests"""
    print("🚀 Starting Remote Stripe Integration Tests")
    print(f"📍 Testing application at: {BASE_URL}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Application availability
    result = test_application_availability()
    results.append(("Application Availability", result))
    
    # Test 2: Admin panel access
    result = test_admin_panel_access()
    results.append(("Admin Panel Access", result))
    
    # Test 3: Admin login
    token = test_admin_login()
    results.append(("Admin Login", bool(token)))
    
    # Test 4: Settings retrieval (requires token)
    if token:
        stripe_keys = test_settings_retrieval(token)
        results.append(("Settings Retrieval", bool(stripe_keys)))
        
        # Test 5: Audit logs (requires token)
        result = test_audit_logs_api(token)
        results.append(("Audit Logs API", result))
    else:
        results.append(("Settings Retrieval", False))
        results.append(("Audit Logs API", False))
    
    # Test 6: Payment methods API
    result = test_payment_methods_api()
    results.append(("Payment Methods API", result))
    
    # Test 7: Currencies API
    result = test_currencies_api()
    results.append(("Currencies API", result))
    
    # Test 8: Orders API
    result = test_orders_api()
    results.append(("Orders API", result))
    
    # Test 9: Checkout session creation
    result = test_checkout_session_creation()
    results.append(("Checkout Session Creation", result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 REMOTE TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All remote tests passed! Deployed application is working correctly.")
    else:
        print("⚠️  Some remote tests failed. Check the deployment configuration.")
        
    return passed == total

if __name__ == "__main__":
    success = run_remote_tests()
    exit(0 if success else 1)
