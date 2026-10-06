from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..database import utcnow
from ..models import (Booking, Payment, PENDING, CONFIRMED, CANCELLED, PAY_SUCCESS, PAY_FAILED)
from ..schemas import PaymentRequest
from .booking_service import expire_stale_bookings
from .notify import notify
from .payment_gateway import get_gateway
from .ticket_service import create_ticket

CURRENCY = "INR"


def process_payment(db: Session, user_id: int, req: PaymentRequest):
    expire_stale_bookings(db)
    booking = db.get(Booking, req.booking_id)
    # Ownership validation (404 so booking ids can't be probed)
    if not booking or booking.user_id != user_id:
        raise HTTPException(404, "Booking not found")
    if booking.booking_status == CONFIRMED:
        raise HTTPException(409, "This booking is already paid")
    if booking.booking_status == CANCELLED:
        raise HTTPException(400, "This booking was cancelled or expired. Please book again")

    details = req.model_dump()
    result = get_gateway().charge(float(booking.total_price), CURRENCY, req.method, details)
    payment = Payment(
        booking_id=booking.id, user_id=user_id, amount=booking.total_price, currency=CURRENCY,
        method=req.method, transaction_id=result.transaction_id,
        card_last4=req.card_number[-4:] if req.method == "CARD" else None,
    )
    if result.success:
        payment.status = PAY_SUCCESS
        booking.booking_status = CONFIRMED
        booking.expires_at = None
        db.add(payment)
        db.flush()
        create_ticket(db, booking.id)
        notify(db, user_id, "Payment received",
               f"We received {booking.total_price} {CURRENCY} (ref {result.transaction_id}).", "BOOKING")
        notify(db, user_id, "Booking confirmed",
               f"Your {booking.ticket_quantity} ticket(s) for {booking.event.title} are ready. Open Tickets to see your QR code.", "BOOKING")
    else:
        payment.status = PAY_FAILED
        payment.failure_reason = result.message
        db.add(payment)
        notify(db, user_id, "Payment failed",
               f"{result.message}. Booking #{booking.id} is still held until it expires, so you can try again.", "BOOKING")
    db.commit()
    db.refresh(payment)
    db.refresh(booking)
    return payment, booking, result.message
