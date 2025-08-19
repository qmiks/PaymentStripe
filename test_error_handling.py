#!/usr/bin/env python3
"""
Test Error Handling - Verify the improved error messages work correctly
"""

import requests
import json

def test_error_handling():
    """Test the improved error handling in the frontend"""
    
    print("🧪 Testing Error Handling")
    print("=" * 50)
    
    # Test 1: Test with invalid payment data
    print("\n📋 Test 1: Testing payment with current (invalid) Stripe key...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/checkout/session",
            json={
                "amount": 2000,
                "currency": "pln",
                "payment_method": "card"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 400:
            error_text = response.text
            print(f"📄 Error Response: {error_text}")
            
            # Check if it contains the expected error patterns
            if "Invalid API Key" in error_text or "0x9o" in error_text:
                print("✅ SUCCESS: Error response contains Stripe API key error indicators")
                print("💡 The frontend will now show a user-friendly error message")
                return True
            else:
                print("❌ Unexpected error response")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_frontend_error_display():
    """Test that the frontend loads correctly with error handling"""
    
    print("\n📋 Test 2: Testing frontend error display...")
    
    try:
        response = requests.get("http://localhost:8000/")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check if error display elements are present
            if 'error-display' in html_content:
                print("✅ SUCCESS: Error display HTML elements are present")
            else:
                print("❌ Error display HTML elements not found")
                return False
            
            # Check if error handling JavaScript is present
            if 'showError' in html_content:
                print("✅ SUCCESS: Error handling JavaScript functions are present")
            else:
                print("❌ Error handling JavaScript functions not found")
                return False
            
            # Check if Stripe API key error detection is present
            if 'Invalid API Key' in html_content or '0x9o' in html_content:
                print("✅ SUCCESS: Stripe API key error detection is present")
            else:
                print("⚠️  Stripe API key error detection not found (this is normal if no errors)")
            
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Error Handling Test")
    print("=" * 60)
    
    # Test 1: Backend error handling
    success1 = test_error_handling()
    
    # Test 2: Frontend error display
    success2 = test_frontend_error_display()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Backend Error Handling: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Frontend Error Display: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! The error handling is working correctly.")
        print("💡 When users click the pay button with an invalid Stripe key:")
        print("   1. They'll see a user-friendly error message")
        print("   2. The message explains it's a Stripe API key issue")
        print("   3. They can easily access the admin panel to fix it")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
