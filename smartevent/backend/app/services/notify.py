from sqlalchemy.orm import Session
from ..models import Notification


def notify(db: Session, user_id: int, title: str, message: str, type_: str = "SYSTEM"):
    """Add a notification (caller commits)."""
    db.add(Notification(user_id=user_id, title=title, message=message, type=type_))
