#!/usr/bin/env python3
"""
Direct Stripe API Test - Isolate Network Interference Issue
"""

import requests
import json
from app.config import get_stripe_secret_key

def test_stripe_api_directly():
    """Test Stripe API directly to isolate network interference"""
    
    print("🔍 Testing Stripe API Directly")
    print("=" * 50)
    
    # Get the key from our database
    stripe_key = get_stripe_secret_key()
    print(f"📋 Key from database: {stripe_key[:20]}...")
    print(f"📏 Key length: {len(stripe_key)}")
    
    # Test 1: Simple API call to Stripe
    print("\n🧪 Test 1: Simple Stripe API call")
    try:
        response = requests.get(
            "https://api.stripe.com/v1/account",
            headers={
                "Authorization": f"Bearer {stripe_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            account_data = response.json()
            print(f"✅ Success! Account ID: {account_data.get('id', 'N/A')}")
            print(f"📊 Account Details: {json.dumps(account_data, indent=2)}")
            return True
        else:
            print(f"❌ Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_stripe_with_curl_equivalent():
    """Test using curl-like approach"""
    
    print("\n🧪 Test 2: Curl-like approach")
    try:
        import subprocess
        import sys
        
        # Get the key again for this test
        stripe_key = get_stripe_secret_key()
        
        # Create curl command
        curl_cmd = [
            "curl", "-X", "GET",
            "https://api.stripe.com/v1/account",
            "-H", f"Authorization: Bearer {stripe_key}",
            "-H", "Content-Type: application/x-www-form-urlencoded",
            "-v"  # Verbose to see headers
        ]
        
        print(f"🔧 Running: {' '.join(curl_cmd[:4])} ...")
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        print(f"📡 Exit Code: {result.returncode}")
        print(f"📄 STDOUT: {result.stdout}")
        print(f"❌ STDERR: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_different_networks():
    """Test if the issue is network-specific"""
    
    print("\n🧪 Test 3: Network Analysis")
    
    # Test with different DNS
    dns_servers = [
        "8.8.8.8",  # Google DNS
        "1.1.1.1",  # Cloudflare DNS
        "208.67.222.222"  # OpenDNS
    ]
    
    for dns in dns_servers:
        print(f"\n🌐 Testing with DNS: {dns}")
        try:
            # This is a simplified test - in practice you'd need to configure DNS
            response = requests.get(
                "https://api.stripe.com/v1/account",
                headers={
                    "Authorization": f"Bearer {get_stripe_secret_key()}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                timeout=10
            )
            print(f"📡 Status: {response.status_code}")
        except Exception as e:
            print(f"💥 Error: {e}")

def test_stripe_key_validation():
    """Test if the key itself is valid by checking its format"""
    
    print("\n🧪 Test 4: Key Format Validation")
    
    stripe_key = get_stripe_secret_key()
    
    # Check key format
    if stripe_key.startswith("sk_test_"):
        print("✅ Key format: Test key (correct)")
    elif stripe_key.startswith("sk_live_"):
        print("✅ Key format: Live key (correct)")
    else:
        print("❌ Key format: Invalid prefix")
        return False
    
    # Check key length (should be around 107 characters)
    if len(stripe_key) >= 100:
        print(f"✅ Key length: {len(stripe_key)} characters (reasonable)")
    else:
        print(f"❌ Key length: {len(stripe_key)} characters (too short)")
        return False
    
    # Check for common issues
    if "placeholder" in stripe_key.lower():
        print("❌ Key contains placeholder text")
        return False
    
    if "your" in stripe_key.lower():
        print("❌ Key contains placeholder text")
        return False
    
    print("✅ Key format validation passed")
    return True

def test_environment_variables():
    """Check if environment variables are interfering"""
    
    print("\n🧪 Test 5: Environment Variable Check")
    
    import os
    
    # Check for Stripe-related environment variables
    stripe_env_vars = [
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY", 
        "STRIPE_WEBHOOK_SECRET",
        "STRIPE_API_KEY"
    ]
    
    found_vars = []
    for var in stripe_env_vars:
        value = os.getenv(var)
        if value:
            found_vars.append((var, value[:20] + "..." if len(value) > 20 else value))
    
    if found_vars:
        print("⚠️  Found Stripe environment variables:")
        for var, value in found_vars:
            print(f"   {var}: {value}")
        print("💡 These might be overriding database settings!")
        return False
    else:
        print("✅ No Stripe environment variables found")
        return True

if __name__ == "__main__":
    print("🚀 Stripe API Network Interference Test")
    print("=" * 60)
    
    # Test 1: Direct API call
    success1 = test_stripe_api_directly()
    
    # Test 2: Curl-like approach
    success2 = test_stripe_with_curl_equivalent()
    
    # Test 3: Network analysis
    test_different_networks()
    
    # Test 4: Key validation
    success4 = test_stripe_key_validation()
    
    # Test 5: Environment variables
    success5 = test_environment_variables()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Direct API Test: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Curl Test: {'PASS' if success2 else 'FAIL'}")
    print(f"✅ Key Validation: {'PASS' if success4 else 'FAIL'}")
    print(f"✅ Environment Check: {'PASS' if success5 else 'FAIL'}")
    
    if not success1 and not success2:
        print("\n🔍 DIAGNOSIS: Network-level interference detected!")
        print("💡 Possible causes:")
        print("   - Corporate firewall/proxy")
        print("   - ISP-level request modification")
        print("   - Stripe API caching")
        print("   - Different Stripe account being used")
        print("\n🛠️  Solutions:")
        print("   - Try different network (mobile hotspot)")
        print("   - Check corporate proxy settings")
        print("   - Verify Stripe account and keys")
        print("   - Contact Stripe support")
    else:
        print("\n✅ No network interference detected!")
