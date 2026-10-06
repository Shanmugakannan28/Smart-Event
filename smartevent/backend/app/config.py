import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartevent.db")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "mock")
BOOKING_HOLD_MINUTES = int(os.getenv("BOOKING_HOLD_MINUTES", "15"))
REMINDER_HOURS_BEFORE = int(os.getenv("REMINDER_HOURS_BEFORE", "24"))
