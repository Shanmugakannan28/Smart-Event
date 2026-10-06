import uuid
from pathlib import Path
import qrcode
from ..config import BASE_URL

QR_DIR = Path(__file__).resolve().parents[2] / "static" / "qrcodes"
QR_DIR.mkdir(parents=True, exist_ok=True)


def new_ticket_code() -> str:
    return "SE-" + uuid.uuid4().hex[:12].upper()


def generate_qr(ticket_code: str):
    """Create a QR PNG that encodes the ticket code. Returns (file_path, public_url)."""
    path = QR_DIR / f"{ticket_code}.png"
    img = qrcode.make(ticket_code, box_size=10, border=2)
    img.save(path)
    return path, f"{BASE_URL}/static/qrcodes/{ticket_code}.png"
