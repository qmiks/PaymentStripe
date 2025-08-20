from fastapi import APIRouter
from sqlmodel import select
from typing import List
from .models import Order
from .db import get_session

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.get("/", response_model=List[Order])
def list_orders():
    with get_session() as session:
        return session.exec(select(Order).order_by(Order.id.desc()).limit(50)).all()

@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int):
    with get_session() as session:
        order = session.get(Order, order_id)
        if not order:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Order not found")
        return order
