#!/usr/bin/env python3
"""
Database initialization script for deployment environments.
Run this script to set up the database with admin user and default settings.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.db import init_db, get_session
from app.models import AdminUser, AppSettings
from app.auth import get_password_hash, log_audit_event
from sqlmodel import select

def initialize_database():
    """Initialize database with tables, admin user, and default settings"""
    print("🔧 Initializing database...")
    
    # Create database and tables
    init_db()
    print("✅ Database tables created")
    
    with get_session() as db:
        # Check if admin user exists
        admin_user = db.exec(select(AdminUser).where(AdminUser.username == "admin")).first()
        if not admin_user:
            admin_user = AdminUser(
                username="admin",
                password_hash=get_password_hash("admin123"),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("✅ Admin user created (username: admin, password: admin123)")
        else:
            print("ℹ️  Admin user already exists")
        
        # Initialize default settings
        default_settings = [
            ("STRIPE_SECRET_KEY", "sk_test_your_stripe_secret_key_here", "Stripe Secret Key"),
            ("STRIPE_WEBHOOK_SECRET", "whsec_your_webhook_secret_here", "Stripe Webhook Secret"),
            ("STRIPE_PUBLISHABLE_KEY", "pk_test_your_publishable_key_here", "Stripe Publishable Key"),
            ("PAYMENT_METHODS", "card,blik,p24,bancontact,ideal,sofort", "Available Payment Methods (comma-separated list: card,blik,p24,bancontact,ideal,sofort,giropay,eps,sepa_debit,sepa_credit_transfer)"),
            ("SUPPORTED_CURRENCIES", "pln,usd,eur,gbp", "Supported Currencies (comma-separated list: pln,usd,eur,gbp,cad,aud,chf,sek,nok,dkk)"),
            ("DEFAULT_CURRENCY", "pln", "Default Currency (3-letter code: pln, usd, eur, gbp)"),
        ]
        
        settings_created = 0
        for key, value, description in default_settings:
            setting = db.exec(select(AppSettings).where(AppSettings.key == key)).first()
            if not setting:
                setting = AppSettings(
                    key=key,
                    value=value,
                    description=description
                )
                db.add(setting)
                settings_created += 1
        
        db.commit()
        print(f"✅ {settings_created} default settings created")
        
        # Log the initialization
        log_audit_event(
            username="system",
            action="admin_init",
            resource_type="system",
            resource_id="deployment_init",
            details="Database initialized via deployment script"
        )
        
        print("✅ Database initialization completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update Stripe keys in admin panel")
        print("2. Configure payment methods and currencies")
        print("3. Change default admin password")

if __name__ == "__main__":
    initialize_database()
