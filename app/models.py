from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount_pln: int
    currency: str = "pln"
    status: str = "pending"  # pending | paid | failed
    stripe_session_id: Optional[str] = None
    payment_intent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
