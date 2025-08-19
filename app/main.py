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
    # Set Stripe API key from database
    stripe.api_key = get_stripe_secret_key()

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
