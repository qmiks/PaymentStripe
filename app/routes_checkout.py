import uuid
import stripe
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from .config import settings
from .db import get_session
from .models import Order

router = APIRouter(prefix="/api/checkout", tags=["checkout"])

class CreateSessionRequest(BaseModel):
    amount_pln: int = Field(..., ge=1, description="Kwota w PLN (całkowita liczba)")

@router.post("/session")
async def create_checkout_session(body: CreateSessionRequest, request: Request):
    amount_grosze = body.amount_pln * 100
    try:
        # Create Order
        with get_session() as db:
            order = Order(amount_pln=body.amount_pln, currency="pln", status="pending")
            db.add(order)
            db.commit()
            db.refresh(order)

        idem_key = request.headers.get("Idempotency-Key") or f"checkout-{order.id}-{uuid.uuid4()}"
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card", "blik"],
            line_items=[{
                "price_data": {
                    "currency": "pln",
                    "product_data": {"name": f"Order #{order.id}"},
                    "unit_amount": amount_grosze,
                },
                "quantity": 1,
            }],
            client_reference_id=str(order.id),
            success_url=f"{settings.APP_BASE_URL}/?success=1&order_id={order.id}&sid={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.APP_BASE_URL}/?canceled=1&order_id={order.id}",
            idempotency_key=idem_key
        )

        with get_session() as db:
            obj = db.get(Order, order.id)
            if obj:
                obj.stripe_session_id = session.id
                db.add(obj)
                db.commit()

        return {"url": session.url, "order_id": order.id}
    except Exception as e:
        raise HTTPException(400, str(e))
