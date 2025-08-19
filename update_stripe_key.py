#!/usr/bin/env python3
"""
Update Stripe Key - Helper script to update the Stripe API key
"""

from app.db import get_session
from app.models import AppSettings
from sqlmodel import select

def update_stripe_key(new_key):
    """Update the Stripe secret key in the database"""
    
    print("🔄 Updating Stripe Secret Key")
    print("=" * 50)
    
    if not new_key.startswith("sk_test_") and not new_key.startswith("sk_live_"):
        print("❌ Invalid key format! Key must start with 'sk_test_' or 'sk_live_'")
        return False
    
    try:
        with get_session() as db:
            # Find the existing setting
            setting = db.exec(select(AppSettings).where(AppSettings.key == "STRIPE_SECRET_KEY")).first()
            
            if setting:
                old_key = setting.value
                setting.value = new_key
                db.add(setting)
                db.commit()
                
                print(f"✅ Key updated successfully!")
                print(f"📋 Old key: {old_key[:20]}...")
                print(f"📋 New key: {new_key[:20]}...")
                return True
            else:
                print("❌ STRIPE_SECRET_KEY setting not found in database")
                return False
                
    except Exception as e:
        print(f"💥 Error updating key: {e}")
        return False

def show_current_key():
    """Show the current Stripe key"""
    
    print("📋 Current Stripe Key")
    print("=" * 30)
    
    try:
        with get_session() as db:
            setting = db.exec(select(AppSettings).where(AppSettings.key == "STRIPE_SECRET_KEY")).first()
            
            if setting:
                print(f"Current key: {setting.value[:20]}...")
                print(f"Key length: {len(setting.value)} characters")
                return setting.value
            else:
                print("❌ No Stripe key found in database")
                return None
                
    except Exception as e:
        print(f"💥 Error reading key: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Stripe Key Update Tool")
    print("=" * 50)
    
    # Show current key
    current_key = show_current_key()
    
    print("\n📋 Instructions:")
    print("1. Go to https://dashboard.stripe.com/")
    print("2. Navigate to Developers → API keys")
    print("3. Copy your secret key (starts with 'sk_test_' or 'sk_live_')")
    print("4. Run this script with the new key as an argument")
    print("5. Example: python update_stripe_key.py sk_test_your_new_key_here")
    
    import sys
    if len(sys.argv) > 1:
        new_key = sys.argv[1]
        update_stripe_key(new_key)
    else:
        print("\n💡 To update the key, run:")
        print("   python update_stripe_key.py YOUR_NEW_STRIPE_KEY")
