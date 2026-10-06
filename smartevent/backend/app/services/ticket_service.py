from sqlalchemy.orm import Session
from ..models import Ticket
from .qr import new_ticket_code, generate_qr


def create_ticket(db: Session, booking_id: int) -> Ticket:
    """One unique QR ticket per confirmed booking (idempotent)."""
    existing = db.query(Ticket).filter(Ticket.booking_id == booking_id).first()
    if existing:
        return existing
    while True:
        code = new_ticket_code()
        if not db.query(Ticket).filter(Ticket.ticket_code == code).first():
            break
    _, url = generate_qr(code)
    ticket = Ticket(booking_id=booking_id, ticket_code=code, qr_code_url=url)
    db.add(ticket)
    db.flush()
    return ticket
