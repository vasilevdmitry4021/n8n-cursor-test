"""Database models for the TORO Maintenance Orders API."""

from __future__ import annotations

from datetime import datetime

from database import db


class Order(db.Model):
    """Represents a maintenance or repair order."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    equipment_type = db.Column(db.String(120), nullable=False)
    equipment_id = db.Column(db.String(120), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), nullable=False, default="medium")
    status = db.Column(db.String(20), nullable=False, default="created")
    requester_name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Order id={self.id} number={self.order_number}>"

    def to_dict(self) -> dict[str, str | int]:
        """Return a serializable representation of the order."""

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
            "contact_email": self.contact_email,
            "created_at": self._format_dt(self.created_at),
            "updated_at": self._format_dt(self.updated_at),
        }

    @staticmethod
    def _format_dt(value: datetime | None) -> str | None:
        if value is None:
            return None
        # ISO 8601 with UTC "Z" suffix for compatibility.
        return value.replace(microsecond=0).isoformat() + "Z"


__all__: list[str] = ["Order"]
