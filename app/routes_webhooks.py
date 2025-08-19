import stripe
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from .config import settings, get_stripe_webhook_secret
from .db import get_session
from .models import Order
from datetime import datetime

router = APIRouter(tags=["webhooks"])

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
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
                    order.status = "paid"
                    order.payment_intent_id = payment_intent_id
                    order.updated_at = datetime.utcnow()
                    db.add(order)
                    db.commit()
        print("[webhook] checkout.session.completed for order", order_id)

    elif event["type"] == "payment_intent.payment_failed":
        pi = event["data"]["object"]
        print("[webhook] payment failed:", pi.get("id"))

    return JSONResponse({"received": True})
