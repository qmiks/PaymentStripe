#!/usr/bin/env python3
"""
Sync Local Settings to Remote Application
Reads settings from local database and updates them in the remote application.
"""

import sys
import requests
import json
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.db import get_session
from app.auth import get_setting

# Configuration
BASE_URL = "https://paymentstripe-uee3a.ondigitalocean.app"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def get_local_settings():
    """Get all settings from local database"""
    print("📖 Reading local database settings...")
    
    try:
        with get_session() as db:
            from app.models import AppSettings
            from sqlmodel import select
            
            settings = db.exec(select(AppSettings)).all()
            
            settings_dict = {}
            for setting in settings:
                settings_dict[setting.key] = {
                    "value": setting.value,
                    "description": setting.description
                }
            
            print(f"✅ Found {len(settings_dict)} settings in local database")
            return settings_dict
            
    except Exception as e:
        print(f"❌ Error reading local settings: {e}")
        return None

def login_to_remote():
    """Login to remote admin panel"""
    print("\n🔐 Logging into remote admin panel...")
    
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
                print("✅ Remote login successful")
                return data["access_token"]
            else:
                print("❌ Login response missing access token")
                return None
        else:
            print(f"❌ Remote login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Remote login error: {e}")
        return None

def get_remote_settings(token):
    """Get current settings from remote application"""
    print("\n📡 Reading remote settings...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/api/admin/settings", headers=headers, timeout=10)
        
        if response.status_code == 200:
            settings = response.json()
            print(f"✅ Retrieved {len(settings)} settings from remote")
            return settings
        else:
            print(f"❌ Failed to get remote settings: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting remote settings: {e}")
        return None

def update_remote_setting(token, key, value, description):
    """Update a single setting in remote application"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "value": value,
            "description": description or ""
        }
        
        response = requests.put(
            f"{BASE_URL}/api/admin/settings/{key}",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Failed to update {key}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {key}: {e}")
        return False

def sync_settings():
    """Main function to sync local settings to remote"""
    print("🚀 Starting Settings Sync")
    print(f"📍 Local → {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Get local settings
    local_settings = get_local_settings()
    if not local_settings:
        print("❌ Cannot proceed without local settings")
        return False
    
    # Step 2: Login to remote
    token = login_to_remote()
    if not token:
        print("❌ Cannot proceed without remote authentication")
        return False
    
    # Step 3: Get remote settings
    remote_settings = get_remote_settings(token)
    if not remote_settings:
        print("❌ Cannot proceed without remote settings")
        return False
    
    # Step 4: Compare and update settings
    print("\n🔄 Comparing and updating settings...")
    
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    
    for key, local_data in local_settings.items():
        local_value = local_data["value"]
        local_description = local_data["description"]
        
        # Find corresponding remote setting
        remote_setting = None
        for rs in remote_settings:
            if rs["key"] == key:
                remote_setting = rs
                break
        
        if remote_setting:
            remote_value = remote_setting["value"]
            
            # Check if values are different
            if local_value != remote_value:
                print(f"📝 Updating {key}:")
                print(f"   Local:  {local_value[:30]}...")
                print(f"   Remote: {remote_value[:30]}...")
                
                if update_remote_setting(token, key, local_value, local_description):
                    print(f"   ✅ Updated successfully")
                    updated_count += 1
                else:
                    print(f"   ❌ Update failed")
                    failed_count += 1
            else:
                print(f"⏭️  Skipping {key} (values match)")
                skipped_count += 1
        else:
            print(f"⚠️  Setting {key} not found in remote, skipping")
            skipped_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SYNC SUMMARY")
    print("=" * 50)
    print(f"✅ Updated: {updated_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total: {len(local_settings)}")
    
    if failed_count == 0:
        print("\n🎉 Settings sync completed successfully!")
        return True
    else:
        print(f"\n⚠️  Settings sync completed with {failed_count} failures")
        return False

def verify_sync():
    """Verify that the sync was successful"""
    print("\n🔍 Verifying sync results...")
    
    # Get local settings again
    local_settings = get_local_settings()
    if not local_settings:
        return False
    
    # Login and get remote settings
    token = login_to_remote()
    if not token:
        return False
    
    remote_settings = get_remote_settings(token)
    if not remote_settings:
        return False
    
    # Compare key settings
    print("\n🔑 Verifying Stripe keys...")
    
    stripe_keys = ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY", "STRIPE_WEBHOOK_SECRET"]
    
    for key in stripe_keys:
        local_value = local_settings.get(key, {}).get("value", "")
        remote_value = ""
        
        for rs in remote_settings:
            if rs["key"] == key:
                remote_value = rs["value"]
                break
        
        if local_value == remote_value:
            print(f"✅ {key}: Synced correctly")
        else:
            print(f"❌ {key}: Mismatch detected")
            print(f"   Local:  {local_value[:30]}...")
            print(f"   Remote: {remote_value[:30]}...")
    
    return True

if __name__ == "__main__":
    print("🔄 Settings Sync Tool")
    print("This will sync your local database settings to the remote application.")
    print("Make sure your local settings are correct before proceeding.")
    
    # Run the sync
    success = sync_settings()
    
    if success:
        # Verify the sync
        verify_sync()
    
    exit(0 if success else 1)
