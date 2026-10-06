from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Ticket, Booking, User, TICKET_VALID, TICKET_USED
from ..schemas import TicketOut, VerifyRequest
from ..services.qr import QR_DIR

router = APIRouter(prefix="/tickets", tags=["Tickets"])


def _user_tickets(db, user):
    return db.query(Ticket).join(Booking).filter(Booking.user_id == user.id)


@router.get("", response_model=list[TicketOut])
def my_tickets(booking_id: Optional[int] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = _user_tickets(db, user)
    if booking_id:
        q = q.filter(Ticket.booking_id == booking_id)
    return q.order_by(Ticket.id.desc()).all()


@router.post("/verify")
def verify_ticket(data: VerifyRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Entry-gate check. Marks a VALID ticket as USED so it can't be reused.
    (Any logged-in account can call this in the demo; restrict to a staff role in production.)"""
    t = db.query(Ticket).filter(Ticket.ticket_code == data.ticket_code.strip().upper()).first()
    if not t:
        return {"valid": False, "reason": "Ticket not found"}
    if t.status == TICKET_USED:
        return {"valid": False, "reason": "Ticket already used"}
    if t.status != TICKET_VALID:
        return {"valid": False, "reason": "Ticket was cancelled"}
    t.status = TICKET_USED
    db.commit()
    b = t.booking
    return {"valid": True, "event": b.event.title, "quantity": b.ticket_quantity, "ticket_code": t.ticket_code}


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    t = _user_tickets(db, user).filter(Ticket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")
    return t


@router.get("/{ticket_id}/download")
def download_ticket(ticket_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    t = _user_tickets(db, user).filter(Ticket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")
    path = QR_DIR / f"{t.ticket_code}.png"
    if not path.exists():
        raise HTTPException(404, "QR image missing")
    return FileResponse(path, media_type="image/png", filename=f"{t.ticket_code}.png")
