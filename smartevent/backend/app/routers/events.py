from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Event, CATEGORIES
from ..schemas import EventOut

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=list[EventOut])
def list_events(
    category: Optional[str] = None,
    search: Optional[str] = Query(None, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Event)
    if category and category.lower() != "all":
        match = next((c for c in CATEGORIES if c.lower() == category.lower()), None)
        if not match:
            raise HTTPException(400, f"Category must be one of {CATEGORIES}")
        q = q.filter(Event.category == match)
    if search:
        q = q.filter(Event.title.ilike(f"%{search}%"))
    return q.order_by(Event.event_date).offset(skip).limit(limit).all()


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    return event
