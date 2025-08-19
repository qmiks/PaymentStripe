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
