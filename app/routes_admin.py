from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlmodel import select
from .db import get_session
from .models import AdminUser, AppSettings, AuditLog
from .auth import (
    verify_password, get_password_hash, create_access_token, 
    get_current_user, get_setting, set_setting, log_audit_event, ACCESS_TOKEN_EXPIRE_MINUTES
)
import logging
import stripe
from .config import get_stripe_secret_key

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger("app.admin")

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SettingUpdateRequest(BaseModel):
    value: str
    description: str = None

class SettingResponse(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: str
    updated_by: Optional[int] = None

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: str
    details: Optional[str] = None

class StripePaymentMethod(BaseModel):
    code: str
    name: str
    active: bool | None = None
    capability: Optional[str] = None
    status: Optional[str] = None

class StripePaymentMethodsResponse(BaseModel):
    currency: str
    amount: int
    payment_methods: list[StripePaymentMethod]
    account_id: Optional[str] = None
    country: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, client_request: Request):
    with get_session() as db:
        user = db.exec(select(AdminUser).where(AdminUser.username == request.username)).first()
        if not user or not verify_password(request.password, user.password_hash):
            # Log failed login attempt
            log_audit_event(
                username=request.username,
                action="login_failed",
                resource_type="user",
                resource_id=request.username,
                ip_address=client_request.client.host if client_request.client else None,
                user_agent=client_request.headers.get("user-agent"),
                details="Invalid credentials"
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_active:
            # Log failed login attempt for disabled user
            log_audit_event(
                username=request.username,
                action="login_failed",
                resource_type="user",
                resource_id=request.username,
                ip_address=client_request.client.host if client_request.client else None,
                user_agent=client_request.headers.get("user-agent"),
                details="User account is disabled"
            )
            raise HTTPException(status_code=401, detail="User account is disabled")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Log successful login
        log_audit_event(
            user_id=user.id,
            username=user.username,
            action="login_success",
            resource_type="user",
            resource_id=user.username,
            ip_address=client_request.client.host if client_request.client else None,
            user_agent=client_request.headers.get("user-agent")
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/settings", response_model=list[SettingResponse])
async def get_settings(current_user: AdminUser = Depends(get_current_user)):
    with get_session() as db:
        settings = db.exec(select(AppSettings)).all()
        return [
            SettingResponse(
                key=setting.key,
                value=setting.value,
                description=setting.description,
                updated_at=setting.updated_at.isoformat(),
                updated_by=setting.updated_by
            )
            for setting in settings
        ]

@router.put("/settings/{key}", response_model=SettingResponse)
async def update_setting(
    key: str, 
    request: SettingUpdateRequest,
    current_user: AdminUser = Depends(get_current_user),
    client_request: Request = None
):
    setting = set_setting(
        key=key,
        value=request.value,
        description=request.description,
        user_id=current_user.id
    )
    
    # Additional audit logging for setting updates
    if client_request:
        log_audit_event(
            user_id=current_user.id,
            username=current_user.username,
            action="setting_update",
            resource_type="setting",
            resource_id=key,
            new_value=request.value,
            ip_address=client_request.client.host if client_request.client else None,
            user_agent=client_request.headers.get("user-agent"),
            details=f"Updated via admin panel"
        )
    
    return SettingResponse(
        key=setting.key,
        value=setting.value,
        description=setting.description,
        updated_at=setting.updated_at.isoformat(),
        updated_by=setting.updated_by
    )

@router.get("/stripe/payment-methods", response_model=StripePaymentMethodsResponse)
async def admin_stripe_payment_methods(
    currency: str = "pln",
    amount: int = 2000,
    current_user: AdminUser = Depends(get_current_user),
):
    """
    Secure admin endpoint to fetch Stripe-active payment methods for a given
    currency/amount by probing a PaymentIntent. Augments results with account
    capability status when available.
    """
    try:
        # Probe with PI to get payment_method_types
        stripe.api_key = get_stripe_secret_key()
        pi = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency.lower(),
            automatic_payment_methods={"enabled": True},
        )
        pm_types = list(getattr(pi, "payment_method_types", []) or pi.get("payment_method_types", []))

        # Cleanup best-effort
        try:
            stripe.PaymentIntent.cancel(pi.id)
        except Exception:
            pass

        # Map display names
        method_names = {
            "card": "💳 Credit/Debit Cards",
            "blik": "📱 BLIK",
            "p24": "🏦 Przelewy24 (P24)",
            "bancontact": "🇪🇺 Bancontact (Belgium)",
            "ideal": "🇳🇱 iDEAL (Netherlands)",
            "sofort": "🇩🇪 SOFORT (Germany)",
            "giropay": "🇩🇪 Giropay (Germany)",
            "eps": "🇦🇹 EPS (Austria)",
            "sepa_debit": "🇪🇺 SEPA Direct Debit",
            "sepa_credit_transfer": "🇪🇺 SEPA Credit Transfer",
            "paypal": "🅿️ PayPal",
            "alipay": "🇨🇳 Alipay",
            "klarna": "🇪🇺 Klarna",
        }

        # Try to attach capabilities info
        acct = stripe.Account.retrieve()
        caps = getattr(acct, "capabilities", {}) or {}
        capability_map = {
            "card": "card_payments",
            "blik": "blik_payments",
            "p24": "p24_payments",
            "ideal": "ideal_payments",
            "bancontact": "bancontact_payments",
            "sofort": "sofort_payments",
            "giropay": "giropay_payments",
            "eps": "eps_payments",
            "sepa_debit": "sepa_debit_payments",
        }

        methods: list[StripePaymentMethod] = []
        for code in pm_types:
            cap_key = capability_map.get(code)
            status = caps.get(cap_key) if cap_key else None
            methods.append(StripePaymentMethod(
                code=code,
                name=method_names.get(code, code),
                active=(status == "active") if status is not None else None,
                capability=cap_key,
                status=status,
            ))

        logger.info("Admin fetched Stripe methods for %s %s: %s", amount, currency.upper(), ", ".join(pm_types) or "(none)")
        return StripePaymentMethodsResponse(
            currency=currency.lower(),
            amount=amount,
            payment_methods=methods,
            account_id=acct.get("id"),
            country=acct.get("country"),
        )
    except stripe.error.StripeError as e:  # type: ignore
        user_msg = getattr(e, "user_message", None) or str(e)
        logger.exception("Stripe error in admin methods: %s", user_msg)
        raise HTTPException(status_code=400, detail=user_msg)
    except Exception as e:
        logger.exception("Unexpected error in admin stripe methods")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/init")
async def initialize_admin():
    """Initialize admin user and default settings"""
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
        
        # Initialize default settings
        default_settings = [
            ("STRIPE_SECRET_KEY", "sk_test_your_stripe_secret_key_here", "Stripe Secret Key"),
            ("STRIPE_WEBHOOK_SECRET", "whsec_your_webhook_secret_here", "Stripe Webhook Secret"),
            ("STRIPE_PUBLISHABLE_KEY", "pk_test_your_publishable_key_here", "Stripe Publishable Key"),
            ("PAYMENT_METHODS", "card,blik,p24,bancontact,ideal,sofort", "Available Payment Methods (comma-separated list: card,blik,p24,bancontact,ideal,sofort,giropay,eps,sepa_debit,sepa_credit_transfer)"),
            ("SUPPORTED_CURRENCIES", "pln,usd,eur,gbp", "Supported Currencies (comma-separated list: pln,usd,eur,gbp,cad,aud,chf,sek,nok,dkk)"),
            ("DEFAULT_CURRENCY", "pln", "Default Currency (3-letter code: pln, usd, eur, gbp)"),
        ]
        
        for key, value, description in default_settings:
            setting = db.exec(select(AppSettings).where(AppSettings.key == key)).first()
            if not setting:
                setting = AppSettings(
                    key=key,
                    value=value,
                    description=description
                )
                db.add(setting)
        
        db.commit()
        
        # Log the initialization
        log_audit_event(
            username="system",
            action="admin_init",
            resource_type="system",
            resource_id="admin_panel",
            details="Admin user and settings initialized"
        )
        
        return {"message": "Admin user and settings initialized successfully"}

@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    current_user: AdminUser = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
    action: str = None,
    username: str = None,
    resource_type: str = None
):
    """Get audit logs with optional filtering"""
    with get_session() as db:
        query = select(AuditLog)
        
        # Apply filters
        if action:
            query = query.where(AuditLog.action == action)
        if username:
            query = query.where(AuditLog.username == username)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        
        # Order by most recent first
        query = query.order_by(AuditLog.created_at.desc())
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        logs = db.exec(query).all()
        
        return [
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                username=log.username,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                old_value=log.old_value,
                new_value=log.new_value,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                created_at=log.created_at.isoformat(),
                details=log.details
            )
            for log in logs
        ]

@router.get("/debug/stripe-keys")
async def debug_stripe_keys(current_user: AdminUser = Depends(get_current_user)):
    """Debug endpoint to check Stripe key configuration"""
    from .config import get_stripe_secret_key, get_stripe_publishable_key, get_stripe_webhook_secret
    from .auth import get_setting
    
    # Get values from database only
    db_secret = get_setting("STRIPE_SECRET_KEY")
    db_publishable = get_setting("STRIPE_PUBLISHABLE_KEY")
    db_webhook = get_setting("STRIPE_WEBHOOK_SECRET")
    
    config_secret = get_stripe_secret_key()
    config_publishable = get_stripe_publishable_key()
    config_webhook = get_stripe_webhook_secret()
    
    return {
        "database": {
            "secret": db_secret,
            "publishable": db_publishable,
            "webhook": db_webhook
        },
        "config_functions": {
            "secret": config_secret,
            "publishable": config_publishable,
            "webhook": config_webhook
        }
    }
