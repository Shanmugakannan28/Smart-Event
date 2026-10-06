from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base, utcnow

# Status / type constants (stored as strings)
CATEGORIES = ["Music", "Tech", "Sports", "Business"]
PENDING, CONFIRMED, CANCELLED = "PENDING", "CONFIRMED", "CANCELLED"
PAY_PENDING, PAY_SUCCESS, PAY_FAILED, PAY_REFUNDED = "PENDING", "SUCCESS", "FAILED", "REFUNDED"
PAY_METHODS = ["CARD", "UPI", "NETBANKING", "WALLET"]
TICKET_VALID, TICKET_USED, TICKET_CANCELLED = "VALID", "USED", "CANCELLED"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utcnow)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(20), nullable=False, index=True)
    location = Column(String(200), nullable=False)
    event_date = Column(DateTime, nullable=False)
    ticket_price = Column(Numeric(10, 2), nullable=False)
    banner_image = Column(String(500))
    total_tickets = Column(Integer, nullable=False, default=100)
    available_tickets = Column(Integer, nullable=False, default=100)
    created_at = Column(DateTime, default=utcnow)


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    ticket_quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    booking_status = Column(String(15), nullable=False, default=PENDING)
    expires_at = Column(DateTime)            # payment hold deadline while PENDING
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    event = relationship("Event")
    payments = relationship("Payment", back_populates="booking", order_by="Payment.id")
    ticket = relationship("Ticket", back_populates="booking", uselist=False)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    method = Column(String(15), nullable=False)
    status = Column(String(15), nullable=False, default=PAY_PENDING)
    transaction_id = Column(String(64), unique=True, index=True)
    card_last4 = Column(String(4))           # only the last 4 digits are ever stored
    failure_reason = Column(String(200))
    refunded_at = Column(DateTime)
    created_at = Column(DateTime, default=utcnow)

    booking = relationship("Booking", back_populates="payments")


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    ticket_code = Column(String(32), unique=True, nullable=False, index=True)
    qr_code_url = Column(String(500))
    status = Column(String(10), nullable=False, default=TICKET_VALID)
    created_at = Column(DateTime, default=utcnow)

    booking = relationship("Booking", back_populates="ticket")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(10), nullable=False, default="SYSTEM")  # EVENT / BOOKING / SYSTEM
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
