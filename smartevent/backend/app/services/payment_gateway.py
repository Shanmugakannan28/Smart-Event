"""Payment gateway abstraction.

`MockGateway` simulates a real provider so the whole flow works offline.
To use Stripe / Razorpay, implement `PaymentGateway` and return it from `get_gateway()`.
Sensitive card data (number, CVV) is passed to the gateway only and is never stored.
"""
import uuid
from dataclasses import dataclass
from typing import Protocol
from ..config import PAYMENT_PROVIDER


@dataclass
class GatewayResult:
    success: bool
    transaction_id: str
    message: str


class PaymentGateway(Protocol):
    def charge(self, amount: float, currency: str, method: str, details: dict) -> GatewayResult: ...
    def refund(self, transaction_id: str, amount: float) -> GatewayResult: ...


class MockGateway:
    """Test rules:
    - Card ending 0002            -> declined
    - Card ending 9995            -> insufficient funds
    - UPI id starting with 'fail' -> declined
    - Bank named 'FailBank'       -> declined
    - everything else             -> success
    """

    def charge(self, amount, currency, method, details):
        txn = "TXN" + uuid.uuid4().hex[:14].upper()
        if method == "CARD":
            num = details.get("card_number", "")
            if num.endswith("0002"):
                return GatewayResult(False, txn, "Card was declined by the bank")
            if num.endswith("9995"):
                return GatewayResult(False, txn, "Insufficient funds")
        if method == "UPI" and details.get("upi_id", "").lower().startswith("fail"):
            return GatewayResult(False, txn, "UPI payment was declined")
        if method == "NETBANKING" and details.get("bank", "").lower() == "failbank":
            return GatewayResult(False, txn, "Net banking authorization failed")
        return GatewayResult(True, txn, "Payment successful")

    def refund(self, transaction_id, amount):
        return GatewayResult(True, "RFD" + uuid.uuid4().hex[:14].upper(), "Refund processed")


def get_gateway() -> PaymentGateway:
    if PAYMENT_PROVIDER == "mock":
        return MockGateway()
    raise RuntimeError(f"Unsupported PAYMENT_PROVIDER '{PAYMENT_PROVIDER}'. Implement it in payment_gateway.py")
