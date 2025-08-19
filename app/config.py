from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from .auth import get_setting

class Settings(BaseSettings):
    STRIPE_SECRET_KEY: str = "sk_test_placeholder"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_placeholder"
    APP_BASE_URL: AnyUrl = "http://localhost:8000"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "dev"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

def get_stripe_secret_key() -> str:
    """Get Stripe secret key from database only"""
    return get_setting("STRIPE_SECRET_KEY")

def get_stripe_webhook_secret() -> str:
    """Get Stripe webhook secret from database only"""
    return get_setting("STRIPE_WEBHOOK_SECRET")

def get_stripe_publishable_key() -> str:
    """Get Stripe publishable key from database only"""
    return get_setting("STRIPE_PUBLISHABLE_KEY")
