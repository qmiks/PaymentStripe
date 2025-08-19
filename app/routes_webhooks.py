import stripe
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from .config import settings, get_stripe_webhook_secret
from .db import get_session
from .models import Order
from .auth import log_audit_event
from datetime import datetime

router = APIRouter(tags=["webhooks"])

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    # Set Stripe API key dynamically from database
    stripe.api_key = get_stripe_secret_key()
    
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, get_stripe_webhook_secret())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {e}")

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        order_id = session_obj.get("client_reference_id")
        payment_intent_id = session_obj.get("payment_intent")
        if order_id:
            with get_session() as db:
                order = db.get(Order, int(order_id))
                if order:
                    old_status = order.status
                    order.status = "paid"
                    order.payment_intent_id = payment_intent_id
                    order.updated_at = datetime.utcnow()
                    db.add(order)
                    db.commit()
                    
                    # Log successful payment
                    log_audit_event(
                        username="stripe_webhook",
                        action="payment_completed",
                        resource_type="order",
                        resource_id=str(order_id),
                        old_value=old_status,
                        new_value="paid",
                        details=f"Payment completed via Stripe webhook. Payment Intent: {payment_intent_id}, Session: {session_obj.get('id')}"
                    )
        print("[webhook] checkout.session.completed for order", order_id)

    elif event["type"] == "payment_intent.payment_failed":
        pi = event["data"]["object"]
        order_id = pi.get("metadata", {}).get("order_id") or pi.get("client_reference_id")
        if order_id:
            with get_session() as db:
                order = db.get(Order, int(order_id))
                if order:
                    old_status = order.status
                    order.status = "failed"
                    order.updated_at = datetime.utcnow()
                    db.add(order)
                    db.commit()
                    
                    # Log failed payment
                    log_audit_event(
                        username="stripe_webhook",
                        action="payment_failed",
                        resource_type="order",
                        resource_id=str(order_id),
                        old_value=old_status,
                        new_value="failed",
                        details=f"Payment failed via Stripe webhook. Payment Intent: {pi.get('id')}, Failure reason: {pi.get('last_payment_error', {}).get('message', 'Unknown')}"
                    )
        print("[webhook] payment failed:", pi.get("id"))

    elif event["type"] == "checkout.session.expired":
        session_obj = event["data"]["object"]
        order_id = session_obj.get("client_reference_id")
        if order_id:
            with get_session() as db:
                order = db.get(Order, int(order_id))
                if order:
                    old_status = order.status
                    order.status = "expired"
                    order.updated_at = datetime.utcnow()
                    db.add(order)
                    db.commit()
                    
                    # Log expired payment session
                    log_audit_event(
                        username="stripe_webhook",
                        action="payment_session_expired",
                        resource_type="order",
                        resource_id=str(order_id),
                        old_value=old_status,
                        new_value="expired",
                        details=f"Payment session expired via Stripe webhook. Session: {session_obj.get('id')}"
                    )
        print("[webhook] checkout.session.expired for order", order_id)

    return JSONResponse({"received": True})
