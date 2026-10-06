from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Payment, User
from ..schemas import PaymentRequest, PaymentResult, PaymentOut, BookingOut
from ..services.payment_service import process_payment

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/pay", response_model=PaymentResult)
def pay(req: PaymentRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Charge a PENDING booking. On success the booking is CONFIRMED and a QR ticket is issued.
    On failure the payment is recorded as FAILED (HTTP 200) and the user can retry."""
    payment, booking, message = process_payment(db, user.id, req)
    return PaymentResult(payment=PaymentOut.model_validate(payment), booking=BookingOut.model_validate(booking), message=message)


@router.get("", response_model=list[PaymentOut])
def payment_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Payment).filter(Payment.user_id == user.id).order_by(Payment.id.desc()).all()


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = db.get(Payment, payment_id)
    if not p or p.user_id != user.id:
        raise HTTPException(404, "Payment not found")
    return p
