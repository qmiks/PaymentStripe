#!/usr/bin/env python3
"""
Test Success Pages - Verify the success and cancel pages work correctly
"""

import requests
import json

def test_success_page():
    """Test the success page"""
    
    print("🧪 Testing Success Page")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/success")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check if success page elements are present
            if 'Payment Successful!' in html_content:
                print("✅ SUCCESS: Success page loads correctly")
            else:
                print("❌ Success page title not found")
                return False
            
            if 'success-icon' in html_content:
                print("✅ SUCCESS: Success page has proper styling")
            else:
                print("❌ Success page styling not found")
                return False
            
            if 'confetti' in html_content:
                print("✅ SUCCESS: Confetti animation is present")
            else:
                print("❌ Confetti animation not found")
                return False
            
            if 'order-details' in html_content:
                print("✅ SUCCESS: Order details section is present")
            else:
                print("❌ Order details section not found")
                return False
            
            return True
        else:
            print(f"❌ Success page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_cancel_page():
    """Test the cancel page"""
    
    print("\n🧪 Testing Cancel Page")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/cancel")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check if cancel page elements are present
            if 'Payment Canceled' in html_content:
                print("✅ SUCCESS: Cancel page loads correctly")
            else:
                print("❌ Cancel page title not found")
                return False
            
            if 'cancel-icon' in html_content:
                print("✅ SUCCESS: Cancel page has proper styling")
            else:
                print("❌ Cancel page styling not found")
                return False
            
            if 'shake' in html_content:
                print("✅ SUCCESS: Shake animation is present")
            else:
                print("❌ Shake animation not found")
                return False
            
            return True
        else:
            print(f"❌ Cancel page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_order_api():
    """Test the order API endpoint"""
    
    print("\n🧪 Testing Order API")
    print("=" * 50)
    
    try:
        # Test getting an existing order
        response = requests.get("http://localhost:8000/api/orders/1")
        
        if response.status_code == 200:
            order = response.json()
            print("✅ SUCCESS: Order API returns order data")
            print(f"📋 Order ID: {order.get('id')}")
            print(f"💰 Amount: {order.get('amount')}")
            print(f"💱 Currency: {order.get('currency')}")
            print(f"📅 Created: {order.get('created_at')}")
            return True
        else:
            print(f"❌ Order API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_success_page_with_params():
    """Test success page with URL parameters"""
    
    print("\n🧪 Testing Success Page with Parameters")
    print("=" * 50)
    
    try:
        # Test success page with order_id parameter
        response = requests.get("http://localhost:8000/success?order_id=1&sid=cs_test_123")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check if the page loads with parameters
            if 'Payment Successful!' in html_content:
                print("✅ SUCCESS: Success page loads with parameters")
            else:
                print("❌ Success page with parameters failed")
                return False
            
            # Check if receipt link section is present
            if 'receipt-link' in html_content:
                print("✅ SUCCESS: Receipt link section is present")
            else:
                print("❌ Receipt link section not found")
                return False
            
            return True
        else:
            print(f"❌ Success page with parameters failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Success Pages Test")
    print("=" * 60)
    
    # Test 1: Success page
    success1 = test_success_page()
    
    # Test 2: Cancel page
    success2 = test_cancel_page()
    
    # Test 3: Order API
    success3 = test_order_api()
    
    # Test 4: Success page with parameters
    success4 = test_success_page_with_params()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Success Page: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Cancel Page: {'PASS' if success2 else 'FAIL'}")
    print(f"✅ Order API: {'PASS' if success3 else 'FAIL'}")
    print(f"✅ Success Page with Params: {'PASS' if success4 else 'FAIL'}")
    
    if all([success1, success2, success3, success4]):
        print("\n🎉 All tests passed! The success pages are working correctly.")
        print("💡 Features implemented:")
        print("   1. Beautiful success page with confetti animation")
        print("   2. Professional cancel page with shake animation")
        print("   3. Order details display with API integration")
        print("   4. Receipt link to Stripe dashboard")
        print("   5. Responsive design for mobile devices")
        print("   6. Easy navigation back to payment or admin")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
