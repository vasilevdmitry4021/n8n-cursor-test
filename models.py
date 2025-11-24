"""SQLAlchemy models for the TORO API."""
from datetime import datetime

from database import db

# Enumerations used for validation and storage
PRIORITY_CHOICES = ("low", "medium", "high")
STATUS_CHOICES = ("created", "in_progress", "completed")


class Order(db.Model):
    """Represents a maintenance or repair order."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    equipment_type = db.Column(db.String(120), nullable=False)
    equipment_id = db.Column(db.String(120), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), nullable=False, default="medium")
    status = db.Column(db.String(20), nullable=False, default="created")
    requester_name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def to_dict(self) -> dict:
        """Serialize model instance into a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "equipment_type": self.equipment_type,
            "equipment_id": self.equipment_id,
            "issue_description": self.issue_description,
            "priority": self.priority,
            "status": self.status,
            "requester_name": self.requester_name,
            "department": self.department,
            "contact_phone": self.contact_phone,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
        }

    @classmethod
    def generate_order_number(cls) -> str:
        """Generate a unique order number in the TORO-YYYY-NNN format."""
        current_year = datetime.utcnow().year
        prefix = f"TORO-{current_year}"
        pattern = f"{prefix}-%"

        latest = (
            db.session.query(cls.order_number)
            .filter(cls.order_number.like(pattern))
            .order_by(cls.order_number.desc())
            .first()
        )

        last_sequence = 0
        if latest and latest[0]:
            try:
                last_sequence = int(latest[0].split("-")[-1])
            except ValueError:
                last_sequence = 0

        next_sequence = last_sequence + 1
        return f"{prefix}-{next_sequence:03d}"
