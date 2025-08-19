import os, stripe
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import settings, get_stripe_secret_key
from . import routes_checkout, routes_webhooks, routes_orders, routes_admin
from .db import init_db

app = FastAPI(title="FastAPI + Stripe BLIK Demo (with DB + Admin)")

@app.on_event("startup")
def on_startup():
    init_db()
    
    # Auto-initialize admin user and settings if they don't exist
    from .db import get_session
    from .models import AdminUser, AppSettings
    from .auth import get_password_hash
    from sqlmodel import select
    
    with get_session() as db:
        # Check if admin user exists, create if not
        admin_user = db.exec(select(AdminUser).where(AdminUser.username == "admin")).first()
        if not admin_user:
            admin_user = AdminUser(
                username="admin",
                password_hash=get_password_hash("admin123"),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
        
        # Check if settings exist, create with placeholder values if not
        settings_count = len(db.exec(select(AppSettings)).all())
        if settings_count == 0:
            # Initialize with placeholder values only
            default_settings = [
                ("STRIPE_SECRET_KEY", "sk_test_your_stripe_secret_key_here", "Stripe Secret Key"),
                ("STRIPE_WEBHOOK_SECRET", "whsec_your_webhook_secret_here", "Stripe Webhook Secret"),
                ("STRIPE_PUBLISHABLE_KEY", "pk_test_your_publishable_key_here", "Stripe Publishable Key"),
                ("PAYMENT_METHODS", "card,blik,p24,bancontact,ideal,sofort", "Available Payment Methods"),
                ("SUPPORTED_CURRENCIES", "pln,usd,eur,gbp", "Supported Currencies"),
                ("DEFAULT_CURRENCY", "pln", "Default Currency"),
            ]
            
            for key, value, description in default_settings:
                setting = AppSettings(
                    key=key,
                    value=value,
                    description=description,
                    updated_by=admin_user.id
                )
                db.add(setting)
            db.commit()
    
    # Note: Stripe API key is now loaded dynamically per request

app.include_router(routes_checkout.router)
app.include_router(routes_webhooks.router)
app.include_router(routes_orders.router)
app.include_router(routes_admin.router)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/admin")
async def admin():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(static_dir, "admin.html"))
