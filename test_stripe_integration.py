#!/usr/bin/env python3
"""
Stripe Integration Test Script
Tests the complete Stripe integration with database-stored keys.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.db import get_session
from app.auth import get_setting
from app.config import get_stripe_secret_key, get_stripe_publishable_key
import stripe

def test_database_connection():
    """Test database connection and key retrieval"""
    print("🔍 Testing database connection...")
    try:
        with get_session() as db:
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_stripe_keys_retrieval():
    """Test retrieval of Stripe keys from database"""
    print("\n🔑 Testing Stripe keys retrieval from database...")
    
    try:
        # Test direct setting retrieval
        secret_key = get_setting("STRIPE_SECRET_KEY")
        publishable_key = get_setting("STRIPE_PUBLISHABLE_KEY")
        webhook_secret = get_setting("STRIPE_WEBHOOK_SECRET")
        
        print(f"Secret Key: {secret_key[:20]}..." if secret_key else "❌ No secret key found")
        print(f"Publishable Key: {publishable_key[:20]}..." if publishable_key else "❌ No publishable key found")
        print(f"Webhook Secret: {webhook_secret[:20]}..." if webhook_secret else "❌ No webhook secret found")
        
        # Test config functions
        config_secret = get_stripe_secret_key()
        config_publishable = get_stripe_publishable_key()
        
        print(f"Config Secret Key: {config_secret[:20]}..." if config_secret else "❌ No config secret key")
        print(f"Config Publishable Key: {config_publishable[:20]}..." if config_publishable else "❌ No config publishable key")
        
        # Check if keys are placeholder values
        if secret_key and "your_stripe_secret_key_here" in secret_key:
            print("⚠️  WARNING: Secret key appears to be placeholder value")
            return False
        
        if publishable_key and "your_publishable_key_here" in publishable_key:
            print("⚠️  WARNING: Publishable key appears to be placeholder value")
            return False
            
        return bool(secret_key and publishable_key)
        
    except Exception as e:
        print(f"❌ Key retrieval failed: {e}")
        return False

def test_stripe_api_connection():
    """Test Stripe API connection with retrieved keys"""
    print("\n🌐 Testing Stripe API connection...")
    
    try:
        secret_key = get_stripe_secret_key()
        if not secret_key:
            print("❌ No secret key available for API test")
            return False
            
        # Configure Stripe with the key
        stripe.api_key = secret_key
        
        # Test API connection by retrieving account info
        account = stripe.Account.retrieve()
        print(f"✅ Stripe API connection successful")
        print(f"   Account ID: {account.id}")
        print(f"   Account Type: {account.type}")
        print(f"   Charges Enabled: {account.charges_enabled}")
        print(f"   Payouts Enabled: {account.payouts_enabled}")
        
        return True
        
    except stripe.error.AuthenticationError:
        print("❌ Stripe authentication failed - invalid API key")
        return False
    except stripe.error.APIError as e:
        print(f"❌ Stripe API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Stripe connection failed: {e}")
        return False

def test_payment_methods_configuration():
    """Test payment methods configuration"""
    print("\n💳 Testing payment methods configuration...")
    
    try:
        payment_methods = get_setting("PAYMENT_METHODS")
        if not payment_methods:
            print("❌ No payment methods configured")
            return False
            
        methods = [method.strip() for method in payment_methods.split(",")]
        print(f"✅ Payment methods configured: {', '.join(methods)}")
        
        # Test with Stripe API
        secret_key = get_stripe_secret_key()
        if secret_key:
            stripe.api_key = secret_key
            
            # Get supported payment methods from Stripe
            payment_intent_data = stripe.PaymentIntent.create(
                amount=1000,
                currency='pln',
                payment_method_types=['card'],
                confirm=False
            )
            print("✅ Payment intent creation test successful")
            
        return True
        
    except Exception as e:
        print(f"❌ Payment methods test failed: {e}")
        return False

def test_webhook_configuration():
    """Test webhook configuration"""
    print("\n🔔 Testing webhook configuration...")
    
    try:
        webhook_secret = get_setting("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            print("❌ No webhook secret configured")
            return False
            
        if "your_webhook_secret_here" in webhook_secret:
            print("⚠️  WARNING: Webhook secret appears to be placeholder value")
            return False
            
        print(f"✅ Webhook secret configured: {webhook_secret[:20]}...")
        return True
        
    except Exception as e:
        print(f"❌ Webhook configuration test failed: {e}")
        return False

def test_currency_configuration():
    """Test currency configuration"""
    print("\n💰 Testing currency configuration...")
    
    try:
        supported_currencies = get_setting("SUPPORTED_CURRENCIES")
        default_currency = get_setting("DEFAULT_CURRENCY")
        
        if not supported_currencies:
            print("❌ No supported currencies configured")
            return False
            
        currencies = [curr.strip() for curr in supported_currencies.split(",")]
        print(f"✅ Supported currencies: {', '.join(currencies)}")
        print(f"✅ Default currency: {default_currency}")
        
        return True
        
    except Exception as e:
        print(f"❌ Currency configuration test failed: {e}")
        return False

def test_admin_authentication():
    """Test admin authentication"""
    print("\n👤 Testing admin authentication...")
    
    try:
        with get_session() as db:
            from app.models import AdminUser
            from sqlmodel import select
            
            admin_user = db.exec(select(AdminUser).where(AdminUser.username == "admin")).first()
            if admin_user:
                print(f"✅ Admin user exists: {admin_user.username}")
                print(f"   Active: {admin_user.is_active}")
                return True
            else:
                print("❌ Admin user not found")
                return False
                
    except Exception as e:
        print(f"❌ Admin authentication test failed: {e}")
        return False

def test_audit_logging():
    """Test audit logging functionality"""
    print("\n📝 Testing audit logging...")
    
    try:
        with get_session() as db:
            from app.models import AuditLog
            from sqlmodel import select
            
            # Count audit logs
            audit_count = db.exec(select(AuditLog)).all()
            print(f"✅ Audit logs found: {len(audit_count)}")
            
            if audit_count:
                latest_log = audit_count[-1]
                print(f"   Latest action: {latest_log.action}")
                print(f"   Latest user: {latest_log.username}")
                print(f"   Latest timestamp: {latest_log.created_at}")
            
            return True
            
    except Exception as e:
        print(f"❌ Audit logging test failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Stripe Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Stripe Keys Retrieval", test_stripe_keys_retrieval),
        ("Stripe API Connection", test_stripe_api_connection),
        ("Payment Methods", test_payment_methods_configuration),
        ("Webhook Configuration", test_webhook_configuration),
        ("Currency Configuration", test_currency_configuration),
        ("Admin Authentication", test_admin_authentication),
        ("Audit Logging", test_audit_logging),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Stripe integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
