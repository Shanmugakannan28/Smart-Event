from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Booking, User
from ..schemas import BookingCreate, BookingOut
from ..services import booking_service

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def _owned(db: Session, booking_id: int, user: User) -> Booking:
    b = db.get(Booking, booking_id)
    if not b or b.user_id != user.id:
        raise HTTPException(404, "Booking not found")
    return b


@router.post("", response_model=BookingOut, status_code=201)
def book(data: BookingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Reserves tickets (status PENDING). Pay via POST /payments/pay to confirm."""
    return booking_service.create_booking(db, user.id, data.event_id, data.ticket_quantity)


@router.get("", response_model=list[BookingOut])
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking_service.expire_stale_bookings(db)
    return db.query(Booking).filter(Booking.user_id == user.id).order_by(Booking.id.desc()).all()


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking_service.expire_stale_bookings(db)
    return _owned(db, booking_id, user)


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Cancels a booking; confirmed+paid bookings are refunded automatically."""
    return booking_service.cancel_booking(db, _owned(db, booking_id, user))
