"""Flask application exposing the TORO maintenance orders API."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Mapping

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from database import db, init_db
from models import Order

PRIORITY_CHOICES = {"low", "medium", "high"}
STATUS_CHOICES = {"created", "in_progress", "completed"}
REQUIRED_FIELDS = {
    "equipment_type",
    "equipment_id",
    "issue_description",
    "requester_name",
    "department",
    "contact_phone",
}
PHONE_PATTERN = re.compile(r"^\+7-\d{3}-\d{3}-\d{2}-\d{2}$")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("toro.api")

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app)
init_db(app)


class ValidationError(ValueError):
    """Raised when incoming payloads do not satisfy requirements."""

    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid payload")
        self.errors = errors


def normalize_string(value: Any) -> str | None:
    """Trim incoming strings; return None for empty/invalid values."""

    if isinstance(value, str):
        trimmed = value.strip()
        return trimmed or None
    return None


def validate_order_payload(payload: dict[str, Any]) -> dict[str, str]:
    """Validate and sanitize payload for order creation."""

    if not isinstance(payload, dict):
        raise ValidationError({"body": "JSON body must be an object"})

    errors: dict[str, str] = {}
    result: dict[str, str] = {}

    for field in REQUIRED_FIELDS:
        value = normalize_string(payload.get(field))
        if not value:
            errors[field] = "Field is required"
        else:
            result[field] = value

    priority = normalize_string(payload.get("priority")) or "medium"
    if priority not in PRIORITY_CHOICES:
        errors["priority"] = f"Priority must be one of {sorted(PRIORITY_CHOICES)}"
    else:
        result["priority"] = priority

    contact_phone = result.get("contact_phone")
    if contact_phone and not PHONE_PATTERN.match(contact_phone):
        errors["contact_phone"] = "Phone must match +7-XXX-XXX-XX-XX"

    if errors:
        raise ValidationError(errors)

    return result


def validate_filters(args: Mapping[str, str]) -> dict[str, str]:
    """Validate query parameters for list endpoint."""

    errors: dict[str, str] = {}
    filters: dict[str, str] = {}

    priority = args.get("priority")
    if priority:
        if priority not in PRIORITY_CHOICES:
            errors["priority"] = f"Priority must be one of {sorted(PRIORITY_CHOICES)}"
        else:
            filters["priority"] = priority

    status = args.get("status")
    if status:
        if status not in STATUS_CHOICES:
            errors["status"] = f"Status must be one of {sorted(STATUS_CHOICES)}"
        else:
            filters["status"] = status

    department = normalize_string(args.get("department"))
    if department:
        filters["department"] = department

    if errors:
        raise ValidationError(errors)

    return filters


def generate_order_number() -> str:
    """Generate the next order number in the TORO-YYYY-NNN format."""

    current_year = datetime.utcnow().year
    prefix = f"TORO-{current_year}-"

    latest_order = (
        Order.query.filter(Order.order_number.like(f"{prefix}%"))
        .order_by(Order.order_number.desc())
        .first()
    )

    next_sequence = 1
    if latest_order:
        try:
            next_sequence = int(latest_order.order_number.split("-")[-1]) + 1
        except (AttributeError, ValueError):
            next_sequence = latest_order.id + 1

    return f"{prefix}{next_sequence:03d}"


@app.route("/api/v1/orders", methods=["POST"])
def create_order() -> Any:
    """Create a new order."""

    payload = request.get_json(silent=True)
    if payload is None:
        raise ValidationError({"body": "JSON body is required"})

    data = validate_order_payload(payload)

    order = Order(
        order_number=generate_order_number(),
        status="created",
        **data,
    )

    try:
        db.session.add(order)
        db.session.commit()
    except SQLAlchemyError as exc:  # pragma: no cover - DB failure path
        db.session.rollback()
        logger.exception("Failed to create order: %s", exc)
        abort(500, description="Unable to create order at this time")

    logger.info(
        "Created order %s (%s) for equipment %s by %s",
        order.order_number,
        order.priority,
        order.equipment_id,
        order.requester_name,
    )

    return jsonify(order.to_dict()), 201


@app.route("/api/v1/orders", methods=["GET"])
def list_orders() -> Any:
    """Return a list of orders with optional filtering."""

    filters = validate_filters(request.args)

    query = Order.query
    if "priority" in filters:
        query = query.filter_by(priority=filters["priority"])
    if "status" in filters:
        query = query.filter_by(status=filters["status"])
    if "department" in filters:
        query = query.filter_by(department=filters["department"])

    orders = query.order_by(Order.created_at.desc()).all()

    return (
        jsonify({"orders": [order.to_dict() for order in orders], "total": len(orders)}),
        200,
    )


@app.route("/api/v1/orders/<int:order_id>", methods=["GET"])
def get_order(order_id: int) -> Any:
    """Return a single order by its identifier."""

    order = db.session.get(Order, order_id)
    if order is None:
        abort(404, description="Order not found")

    return jsonify(order.to_dict()), 200


@app.errorhandler(ValidationError)
def handle_validation_error(error: ValidationError):
    logger.warning("Validation error: %s", error.errors)
    return jsonify({"error": "validation_error", "details": error.errors}), 400


@app.errorhandler(HTTPException)
def handle_http_exception(error: HTTPException):
    response = {
        "error": error.name.replace(" ", "_").lower(),
        "message": error.description,
    }
    return jsonify(response), error.code


@app.errorhandler(Exception)
def handle_exception(error: Exception):  # pragma: no cover - fallback path
    logger.exception("Unhandled error: %s", error)
    return (
        jsonify({"error": "internal_server_error", "message": "Unexpected server error"}),
        500,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
