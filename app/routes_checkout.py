import uuid
import stripe
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from .config import get_stripe_publishable_key, get_stripe_secret_key
from .db import get_session
from .models import Order
from .auth import get_setting, log_audit_event

router = APIRouter(prefix="/api/checkout", tags=["checkout"])

class CreateSessionRequest(BaseModel):
    amount: int = Field(..., ge=1, description="Amount in smallest currency unit (e.g., cents for USD)")
    currency: str = Field(..., description="Currency code (e.g., usd, eur, pln, gbp)")
    payment_method: str = Field(..., description="Selected payment method")

@router.post("/session")
async def create_checkout_session(body: CreateSessionRequest, request: Request):
    try:
        # Get Stripe API key from database and set it globally for this request
        stripe_key = get_stripe_secret_key()
        
        print(f"DEBUG: Using Stripe API key: {stripe_key[:20]}...")
        
        # Create Order
        with get_session() as db:
            order = Order(amount=body.amount, currency=body.currency.lower(), status="pending")
            db.add(order)
            db.commit()
            db.refresh(order)

        idem_key = request.headers.get("Idempotency-Key") or f"checkout-{order.id}-{uuid.uuid4()}"
        # Get payment methods from settings, fallback to default
        payment_methods_str = get_setting("PAYMENT_METHODS") or "card,blik,p24,bancontact,ideal,sofort"
        available_methods = [method.strip() for method in payment_methods_str.split(",")]
        
        # Validate selected payment method
        if body.payment_method not in available_methods:
            # Log failed payment attempt due to invalid payment method
            log_audit_event(
                username="customer",
                action="payment_attempt_failed",
                resource_type="order",
                resource_id=str(order.id),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                details=f"Invalid payment method: {body.payment_method}. Available methods: {', '.join(available_methods)}"
            )
            raise HTTPException(400, f"Invalid payment method: {body.payment_method}")
        
        # Use requests directly to call Stripe API
        import requests
        
        # Format data for Stripe API (form-encoded)
        stripe_data = {
            "mode": "payment",
            "payment_method_types[]": body.payment_method,
            "line_items[0][price_data][currency]": body.currency.lower(),
            "line_items[0][price_data][product_data][name]": f"Order #{order.id}",
            "line_items[0][price_data][unit_amount]": str(body.amount),
            "line_items[0][quantity]": "1",
            "client_reference_id": str(order.id),
            "success_url": f"http://localhost:8000/?success=1&order_id={order.id}&sid={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"http://localhost:8000/?canceled=1&order_id={order.id}",
        }
        
        response = requests.post(
            "https://api.stripe.com/v1/checkout/sessions",
            headers={
                "Authorization": f"Bearer {stripe_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Idempotency-Key": idem_key
            },
            data=stripe_data
        )
        
        if response.status_code != 200:
            print(f"DEBUG: Stripe API error: {response.status_code} - {response.text}")
            raise HTTPException(400, f"Stripe API error: {response.text}")
        
        session_data = response.json()

        with get_session() as db:
            obj = db.get(Order, order.id)
            if obj:
                obj.stripe_session_id = session_data["id"]
                db.add(obj)
                db.commit()

        # Log successful payment attempt
        log_audit_event(
            username="customer",
            action="payment_attempt_created",
            resource_type="order",
            resource_id=str(order.id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details=f"Payment session created for Order #{order.id}. Amount: {body.amount/100} {body.currency.upper()}, Method: {body.payment_method}, Session ID: {session_data['id']}"
        )

        return {"url": session_data["url"], "order_id": order.id}
    except Exception as e:
        # Log failed payment attempt due to system error
        if 'order' in locals():
            log_audit_event(
                username="customer",
                action="payment_attempt_failed",
                resource_type="order",
                resource_id=str(order.id),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                details=f"System error during payment creation: {str(e)}"
            )
        raise HTTPException(400, str(e))

@router.get("/payment-methods")
async def get_payment_methods():
    """Get available payment methods"""
    try:
        payment_methods_str = get_setting("PAYMENT_METHODS") or "card,blik,p24,bancontact,ideal,sofort"
        payment_methods = [method.strip() for method in payment_methods_str.split(",")]
        
        # Map payment method codes to display names
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
            "sepa_credit_transfer": "🇪🇺 SEPA Credit Transfer"
        }
        
        available_methods = []
        for method in payment_methods:
            if method in method_names:
                available_methods.append({
                    "code": method,
                    "name": method_names[method]
                })
        
        return {"payment_methods": available_methods}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/test-deployment")
async def test_deployment():
    """Test endpoint to verify deployment"""
    try:
        import requests
        return {"message": "Deployment test - updated code is running", "timestamp": "2024-01-19", "requests_available": True}
    except ImportError:
        return {"message": "Deployment test - updated code is running", "timestamp": "2024-01-19", "requests_available": False, "error": "requests not available"}

@router.get("/currencies")
async def get_currencies():
    """Get available currencies"""
    try:
        currencies_str = get_setting("SUPPORTED_CURRENCIES") or "pln,usd,eur,gbp"
        default_currency = get_setting("DEFAULT_CURRENCY") or "pln"
        currencies = [currency.strip() for currency in currencies_str.split(",")]
        
        # Map currency codes to display names and symbols
        currency_info = {
            "pln": {"name": "Polish Złoty", "symbol": "zł", "position": "after"},
            "usd": {"name": "US Dollar", "symbol": "$", "position": "before"},
            "eur": {"name": "Euro", "symbol": "€", "position": "before"},
            "gbp": {"name": "British Pound", "symbol": "£", "position": "before"},
            "cad": {"name": "Canadian Dollar", "symbol": "C$", "position": "before"},
            "aud": {"name": "Australian Dollar", "symbol": "A$", "position": "before"},
            "chf": {"name": "Swiss Franc", "symbol": "CHF", "position": "before"},
            "sek": {"name": "Swedish Krona", "symbol": "kr", "position": "after"},
            "nok": {"name": "Norwegian Krone", "symbol": "kr", "position": "after"},
            "dkk": {"name": "Danish Krone", "symbol": "kr", "position": "after"},
        }
        
        available_currencies = []
        for currency in currencies:
            if currency in currency_info:
                available_currencies.append({
                    "code": currency,
                    "name": currency_info[currency]["name"],
                    "symbol": currency_info[currency]["symbol"],
                    "position": currency_info[currency]["position"],
                    "is_default": currency == default_currency
                })
        
        return {"currencies": available_currencies, "default": default_currency}
    except Exception as e:
        raise HTTPException(400, str(e))
