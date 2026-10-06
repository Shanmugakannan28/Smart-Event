from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from ..config import REMINDER_HOURS_BEFORE
from ..database import SessionLocal, utcnow
from ..models import Booking, Event, CONFIRMED
from .booking_service import expire_stale_bookings
from .notify import notify


def run_jobs():
    db = SessionLocal()
    try:
        expire_stale_bookings(db)
        now = utcnow()
        due = (db.query(Booking).join(Event)
               .filter(Booking.booking_status == CONFIRMED, Booking.reminder_sent == False,  # noqa: E712
                       Event.event_date > now, Event.event_date <= now + timedelta(hours=REMINDER_HOURS_BEFORE))
               .all())
        for b in due:
            notify(db, b.user_id, f"Reminder: {b.event.title}",
                   f"Starts {b.event.event_date:%d %b %Y, %I:%M %p} at {b.event.location}. Have your QR ticket ready.", "EVENT")
            b.reminder_sent = True
        db.commit()
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    s = BackgroundScheduler()
    s.add_job(run_jobs, "interval", minutes=1, id="maintenance", max_instances=1)
    s.start()
    return s
