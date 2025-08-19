from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    APP_BASE_URL: AnyUrl = "http://localhost:8000"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "dev"
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
