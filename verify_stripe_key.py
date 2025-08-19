#!/usr/bin/env python3
"""
Verify Stripe Key - Check if the key is valid and belongs to the correct account
"""

import requests
import json
from app.config import get_stripe_secret_key

def verify_stripe_key():
    """Verify if the Stripe key is valid"""
    
    print("🔍 Verifying Stripe API Key")
    print("=" * 50)
    
    # Get the key from our database
    stripe_key = get_stripe_secret_key()
    print(f"📋 Key from database: {stripe_key[:20]}...")
    print(f"📏 Key length: {len(stripe_key)}")
    
    # Test the key with a simple API call
    print("\n🧪 Testing key validity...")
    
    try:
        response = requests.get(
            "https://api.stripe.com/v1/account",
            headers={
                "Authorization": f"Bearer {stripe_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            account_data = response.json()
            print("✅ SUCCESS! Key is valid!")
            print(f"📊 Account ID: {account_data.get('id', 'N/A')}")
            print(f"📊 Account Name: {account_data.get('business_profile', {}).get('name', 'N/A')}")
            print(f"📊 Account Type: {account_data.get('type', 'N/A')}")
            print(f"📊 Country: {account_data.get('country', 'N/A')}")
            print(f"📊 Default Currency: {account_data.get('default_currency', 'N/A')}")
            return True
        else:
            error_data = response.json()
            print(f"❌ Key validation failed!")
            print(f"📄 Error: {json.dumps(error_data, indent=2)}")
            
            # Check if it's the same interference issue
            if "0x9o" in str(error_data):
                print("\n🔍 ANALYSIS: This appears to be the same network interference issue!")
                print("💡 The key is being modified somewhere between our request and Stripe's servers.")
                print("🛠️  Possible solutions:")
                print("   1. Check if you're using the correct Stripe account")
                print("   2. Verify the key in your Stripe dashboard")
                print("   3. Try generating a new API key")
                print("   4. Check if there are any proxy/firewall settings")
            else:
                print("\n🔍 ANALYSIS: Different error - key might be invalid or revoked")
                print("💡 Try generating a new API key from your Stripe dashboard")
            
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_with_different_key_format():
    """Test if the issue is with the key format"""
    
    print("\n🧪 Testing with different key format...")
    
    stripe_key = get_stripe_secret_key()
    
    # Try without the "Bearer " prefix
    try:
        response = requests.get(
            "https://api.stripe.com/v1/account",
            headers={
                "Authorization": stripe_key,  # No "Bearer " prefix
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        
        print(f"📡 Response without 'Bearer' prefix: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS! The issue was with the 'Bearer ' prefix!")
            return True
            
    except Exception as e:
        print(f"💥 Exception: {e}")
    
    return False

def check_stripe_dashboard():
    """Provide instructions for checking the Stripe dashboard"""
    
    print("\n📋 Stripe Dashboard Verification Steps:")
    print("=" * 50)
    print("1. Go to https://dashboard.stripe.com/")
    print("2. Log in to your Stripe account")
    print("3. Go to Developers → API keys")
    print("4. Check if the secret key matches:")
    print(f"   Expected: {get_stripe_secret_key()[:20]}...")
    print("5. If different, copy the correct key and update it in the admin panel")
    print("6. Make sure you're using the correct Stripe account (test vs live)")

if __name__ == "__main__":
    print("🚀 Stripe Key Verification Tool")
    print("=" * 60)
    
    # Test 1: Verify key validity
    success1 = verify_stripe_key()
    
    # Test 2: Try different format
    if not success1:
        success2 = test_with_different_key_format()
    
    # Provide dashboard instructions
    check_stripe_dashboard()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Key Validation: {'PASS' if success1 else 'FAIL'}")
    
    if not success1:
        print("\n🛠️  NEXT STEPS:")
        print("1. Check your Stripe dashboard for the correct API key")
        print("2. Make sure you're using the right Stripe account")
        print("3. Try generating a new API key")
        print("4. Update the key in the admin panel")
        print("5. Test again")
    else:
        print("\n✅ Key is valid! The issue might be elsewhere.")
