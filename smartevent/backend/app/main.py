from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import CORS_ORIGINS
from .database import Base, engine, SessionLocal
from .routers import auth, events, bookings, payments, tickets, notifications
from .seed import seed_events
from .services.qr import QR_DIR
from .services.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_events(db)
    finally:
        db.close()
    scheduler = start_scheduler()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="SmartEvent API", version="1.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=QR_DIR.parent), name="static")  # qrcodes/ and banners/

for r in (auth, events, bookings, payments, tickets, notifications):
    app.include_router(r.router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "SmartEvent API"}
