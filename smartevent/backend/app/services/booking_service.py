from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..config import BOOKING_HOLD_MINUTES
from ..database import utcnow
from ..models import (Booking, Event, Payment, PENDING, CONFIRMED, CANCELLED, PAY_SUCCESS,
                      PAY_REFUNDED, TICKET_CANCELLED)
from .notify import notify
from .payment_gateway import get_gateway


def create_booking(db: Session, user_id: int, event_id: int, qty: int) -> Booking:
    expire_stale_bookings(db)
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    if event.event_date <= utcnow():
        raise HTTPException(400, "This event has already started or ended")
    if event.available_tickets <= 0:
        raise HTTPException(409, "Sold out")
    # Atomic reservation: only succeeds if enough tickets remain.
    updated = (
        db.query(Event)
        .filter(Event.id == event_id, Event.available_tickets >= qty)
        .update({Event.available_tickets: Event.available_tickets - qty}, synchronize_session=False)
    )
    if not updated:
        raise HTTPException(409, f"Only {event.available_tickets} ticket(s) left")
    booking = Booking(
        user_id=user_id, event_id=event_id, ticket_quantity=qty,
        total_price=event.ticket_price * qty,           # auto-calculated, never trusted from client
        booking_status=PENDING, expires_at=utcnow() + timedelta(minutes=BOOKING_HOLD_MINUTES),
    )
    db.add(booking)
    notify(db, user_id, "Booking created",
           f"Complete payment within {BOOKING_HOLD_MINUTES} minutes to confirm {qty} ticket(s) for {event.title}.", "BOOKING")
    db.commit()
    db.refresh(booking)
    return booking


def release_tickets(db: Session, booking: Booking):
    db.query(Event).filter(Event.id == booking.event_id).update(
        {Event.available_tickets: Event.available_tickets + booking.ticket_quantity}, synchronize_session=False)


def expire_stale_bookings(db: Session):
    """Cancel unpaid bookings whose hold has run out and return their tickets to stock."""
    stale = db.query(Booking).filter(Booking.booking_status == PENDING, Booking.expires_at < utcnow()).all()
    for b in stale:
        b.booking_status = CANCELLED
        release_tickets(db, b)
        notify(db, b.user_id, "Booking expired",
               f"Your unpaid booking #{b.id} expired and the tickets were released.", "BOOKING")
    if stale:
        db.commit()


def cancel_booking(db: Session, booking: Booking) -> Booking:
    if booking.booking_status == CANCELLED:
        raise HTTPException(400, "Booking is already cancelled")
    if booking.event.event_date <= utcnow():
        raise HTTPException(400, "Cannot cancel after the event has started")
    refunded_amount = None
    if booking.booking_status == CONFIRMED:
        payment = next((p for p in reversed(booking.payments) if p.status == PAY_SUCCESS), None)
        if payment:
            res = get_gateway().refund(payment.transaction_id, float(payment.amount))
            if not res.success:
                raise HTTPException(502, "Refund failed, please try again")
            payment.status = PAY_REFUNDED
            payment.refunded_at = utcnow()
            refunded_amount = payment.amount
        if booking.ticket:
            booking.ticket.status = TICKET_CANCELLED
    booking.booking_status = CANCELLED
    release_tickets(db, booking)
    msg = f"Booking #{booking.id} for {booking.event.title} was cancelled."
    if refunded_amount is not None:
        msg += f" A refund of {refunded_amount} has been issued."
    notify(db, booking.user_id, "Booking cancelled", msg, "BOOKING")
    db.commit()
    db.refresh(booking)
    return booking
