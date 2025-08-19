import os, stripe
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import settings
from . import routes_checkout, routes_webhooks, routes_orders
from .db import init_db

stripe.api_key = settings.STRIPE_SECRET_KEY

app = FastAPI(title="FastAPI + Stripe BLIK Demo (with DB)")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(routes_checkout.router)
app.include_router(routes_webhooks.router)
app.include_router(routes_orders.router)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(static_dir, "index.html"))
