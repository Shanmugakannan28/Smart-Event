import re
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, model_validator

Category = Literal["Music", "Tech", "Sports", "Business"]
Method = Literal["CARD", "UPI", "NETBANKING", "WALLET"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORM):
    id: int
    username: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Events ----------
class EventOut(ORM):
    id: int
    title: str
    description: str
    category: str
    location: str
    event_date: datetime
    ticket_price: float
    banner_image: Optional[str]
    total_tickets: int
    available_tickets: int
    created_at: datetime


# ---------- Bookings ----------
class BookingCreate(BaseModel):
    event_id: int
    ticket_quantity: int = Field(ge=1, le=10)


class BookingOut(ORM):
    id: int
    user_id: int
    event_id: int
    ticket_quantity: int
    total_price: float
    booking_status: str
    expires_at: Optional[datetime]
    created_at: datetime
    event: EventOut


# ---------- Payments ----------
def _luhn(number: str) -> bool:
    total, alt = 0, False
    for ch in reversed(number):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


class PaymentRequest(BaseModel):
    booking_id: int
    method: Method
    # CARD
    card_name: Optional[str] = Field(default=None, max_length=80)
    card_number: Optional[str] = None
    card_expiry: Optional[str] = None  # MM/YY
    card_cvv: Optional[str] = None
    # UPI
    upi_id: Optional[str] = None
    # NETBANKING
    bank: Optional[str] = Field(default=None, max_length=60)

    @field_validator("card_number")
    @classmethod
    def clean_card(cls, v):
        return re.sub(r"[\s-]", "", v) if v else v

    @model_validator(mode="after")
    def check_method_fields(self):
        if self.method == "CARD":
            if not (self.card_name and self.card_number and self.card_expiry and self.card_cvv):
                raise ValueError("Card name, number, expiry and CVV are required")
            if not (self.card_number.isdigit() and 13 <= len(self.card_number) <= 19 and _luhn(self.card_number)):
                raise ValueError("Invalid card number")
            m = re.fullmatch(r"(0[1-9]|1[0-2])/(\d{2})", self.card_expiry)
            if not m:
                raise ValueError("Expiry must be MM/YY")
            today = date.today()
            if (2000 + int(m.group(2)), int(m.group(1))) < (today.year, today.month):
                raise ValueError("Card has expired")
            if not re.fullmatch(r"\d{3,4}", self.card_cvv):
                raise ValueError("Invalid CVV")
        elif self.method == "UPI":
            if not (self.upi_id and re.fullmatch(r"[\w.\-]{2,}@[A-Za-z]{2,}", self.upi_id)):
                raise ValueError("Enter a valid UPI ID, e.g. name@bank")
        elif self.method == "NETBANKING":
            if not self.bank:
                raise ValueError("Select a bank")
        return self


class PaymentOut(ORM):
    id: int
    booking_id: int
    amount: float
    currency: str
    method: str
    status: str
    transaction_id: Optional[str]
    card_last4: Optional[str]
    failure_reason: Optional[str]
    refunded_at: Optional[datetime]
    created_at: datetime


class PaymentResult(BaseModel):
    payment: PaymentOut
    booking: BookingOut
    message: str


# ---------- Tickets ----------
class TicketOut(ORM):
    id: int
    booking_id: int
    ticket_code: str
    qr_code_url: Optional[str]
    status: str
    created_at: datetime
    booking: BookingOut


class VerifyRequest(BaseModel):
    ticket_code: str = Field(min_length=4, max_length=32)


# ---------- Notifications ----------
class NotificationOut(ORM):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
