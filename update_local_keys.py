#!/usr/bin/env python3
"""
Update Local Database with Real Stripe Keys
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.db import get_session
from app.models import AppSettings
from app.auth import set_setting
from sqlmodel import select

def update_local_keys():
    """Update local database with real Stripe keys"""
    print("🔑 Updating local database with real Stripe keys...")
    
    # These are the real keys we know work (you need to get the full keys)
    # From your previous successful tests, we know they start with:
    # sk_test_51Rur96HpiHJ... and whsec_WKO8zQaMhvwKr6...
    
    print("📝 Please enter your real Stripe keys:")
    print("(You can find these in your Stripe dashboard or from previous successful tests)")
    print()
    
    secret_key = input("Enter STRIPE_SECRET_KEY (starts with sk_test_): ").strip()
    publishable_key = input("Enter STRIPE_PUBLISHABLE_KEY (starts with pk_test_): ").strip()
    webhook_secret = input("Enter STRIPE_WEBHOOK_SECRET (starts with whsec_): ").strip()
    
    if not all([secret_key, publishable_key, webhook_secret]):
        print("❌ All keys are required!")
        return False
    
    real_keys = {
        "STRIPE_SECRET_KEY": secret_key,
        "STRIPE_PUBLISHABLE_KEY": publishable_key,
        "STRIPE_WEBHOOK_SECRET": webhook_secret
    }
    
    try:
        with get_session() as db:
            updated_count = 0
            
            for key, value in real_keys.items():
                # Check if setting exists
                setting = db.exec(select(AppSettings).where(AppSettings.key == key)).first()
                if setting:
                    old_value = setting.value
                    setting.value = value
                    db.add(setting)
                    print(f"✅ Updated {key}")
                    print(f"   Old: {old_value[:30]}...")
                    print(f"   New: {value[:30]}...")
                    updated_count += 1
                else:
                    print(f"❌ Setting {key} not found")
            
            db.commit()
            print(f"\n🎉 Updated {updated_count} settings successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error updating keys: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Local Keys Update Tool")
    print("This will update your local database with real Stripe keys for testing.")
    print()
    
    success = update_local_keys()
    exit(0 if success else 1)
