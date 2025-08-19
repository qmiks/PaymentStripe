#!/usr/bin/env python3
"""
Update Deployed Stripe Key - Update the Stripe API key in the deployed DigitalOcean app
"""

import requests
import json

def update_deployed_stripe_key(new_key, admin_username="admin", admin_password="admin123"):
    """Update the Stripe secret key in the deployed app"""
    
    DEPLOYED_URL = "https://paymentstripe-uee3a.ondigitalocean.app"
    
    print("🔄 Updating Stripe Secret Key in Deployed App")
    print("=" * 60)
    print(f"📍 Deployed URL: {DEPLOYED_URL}")
    
    if not new_key.startswith("sk_test_") and not new_key.startswith("sk_live_"):
        print("❌ Invalid key format! Key must start with 'sk_test_' or 'sk_live_'")
        return False
    
    try:
        # Step 1: Login to admin panel
        print("\n🔐 Step 1: Logging in to admin panel...")
        login_data = {
            "username": admin_username,
            "password": admin_password
        }
        
        login_response = requests.post(
            f"{DEPLOYED_URL}/api/admin/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
        
        login_result = login_response.json()
        access_token = login_result.get("access_token")
        
        if not access_token:
            print("❌ No access token received")
            return False
        
        print("✅ Login successful")
        
        # Step 2: Update the Stripe secret key
        print("\n🔧 Step 2: Updating Stripe secret key...")
        
        update_data = {
            "key": "STRIPE_SECRET_KEY",
            "value": new_key,
            "description": "Stripe Secret Key"
        }
        
        update_response = requests.put(
            f"{DEPLOYED_URL}/api/admin/settings",
            json=update_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        if update_response.status_code != 200:
            print(f"❌ Update failed: {update_response.status_code} - {update_response.text}")
            return False
        
        print("✅ Stripe secret key updated successfully!")
        
        # Step 3: Verify the update
        print("\n🔍 Step 3: Verifying the update...")
        
        verify_response = requests.get(
            f"{DEPLOYED_URL}/api/admin/settings",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if verify_response.status_code == 200:
            settings = verify_response.json()
            for setting in settings:
                if setting.get("key") == "STRIPE_SECRET_KEY":
                    current_value = setting.get("value", "")
                    if current_value == new_key:
                        print("✅ Verification successful! Key matches.")
                        return True
                    else:
                        print(f"❌ Verification failed! Expected: {new_key[:20]}..., Got: {current_value[:20]}...")
                        return False
        
        print("❌ Could not verify the update")
        return False
        
    except Exception as e:
        print(f"💥 Error updating key: {e}")
        return False

def test_deployed_payment():
    """Test if the payment works after updating the key"""
    
    DEPLOYED_URL = "https://paymentstripe-uee3a.ondigitalocean.app"
    
    print("\n🧪 Testing deployed payment...")
    
    try:
        # Test payment session creation
        test_data = {
            "amount": 2000,  # 20 PLN in cents
            "currency": "pln",
            "payment_method": "card"
        }
        
        response = requests.post(
            f"{DEPLOYED_URL}/api/checkout/session",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment test successful!")
            print(f"📋 Order ID: {result.get('order_id')}")
            print(f"🔗 Checkout URL: {result.get('url')}")
            return True
        else:
            print(f"❌ Payment test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error testing payment: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Deployed App Stripe Key Update Tool")
    print("=" * 60)
    
    print("\n📋 Instructions:")
    print("1. Go to https://dashboard.stripe.com/")
    print("2. Navigate to Developers → API keys")
    print("3. Copy your secret key (starts with 'sk_test_' or 'sk_live_')")
    print("4. Run this script with the new key as an argument")
    print("5. Example: python update_deployed_key.py sk_test_your_new_key_here")
    
    import sys
    if len(sys.argv) > 1:
        new_key = sys.argv[1]
        
        # Update the key
        success = update_deployed_stripe_key(new_key)
        
        if success:
            print("\n🎉 Key updated successfully!")
            print("💡 Now test the payment button on the deployed app.")
            
            # Optionally test the payment
            test_choice = input("\n🧪 Would you like to test the payment now? (y/n): ")
            if test_choice.lower() == 'y':
                test_deployed_payment()
        else:
            print("\n❌ Failed to update the key. Check the error messages above.")
    else:
        print("\n💡 To update the key, run:")
        print("   python update_deployed_key.py YOUR_NEW_STRIPE_KEY")
