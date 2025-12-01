"""Flask application exposing the TORO maintenance orders API."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Mapping

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError

from database import db, init_db
from models import Order
from schemas import OrderCreateSchema, OrderFiltersSchema, OrderStatusUpdateSchema

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("toro.api")
SPEC_VERSION = "Opus 4.5"
SERVER_STARTED_AT = datetime.utcnow()

ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "created": {"in_progress"},
    "in_progress": {"completed"},
    "completed": set(),
}

# Keep the app/module level singleton so `flask run` and WSGI servers reuse
# the same initialized extensions.
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app)  # Allow all origins for easier integration during development.
init_db(app)  # Creates tables on first import to guarantee the API is usable.


class RequestValidationError(ValueError):
    """Raised when incoming payloads do not satisfy requirements."""

    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid payload")
        self.errors = errors


def _format_pydantic_errors(error: PydanticValidationError) -> dict[str, str]:
    """Flatten pydantic errors into a field -> message mapping."""

    formatted: dict[str, str] = {}
    for err in error.errors():
        location = ".".join(str(part) for part in err.get("loc", ()))
        formatted[location or "body"] = err.get("msg", "Invalid value")
    return formatted


def validate_order_payload(payload: Any) -> dict[str, Any]:
    """Run pydantic validation for incoming order creation requests."""

    if not isinstance(payload, dict):
        raise RequestValidationError({"body": "JSON body must be an object"})

    try:
        validated = OrderCreateSchema.model_validate(payload)
    except PydanticValidationError as exc:
        raise RequestValidationError(_format_pydantic_errors(exc)) from exc

    return validated.model_dump()


def validate_filters(args: Mapping[str, str]) -> dict[str, str]:
    """Validate query parameters for list endpoint via pydantic."""

    try:
        filters = OrderFiltersSchema.model_validate(dict(args))
    except PydanticValidationError as exc:
        raise RequestValidationError(_format_pydantic_errors(exc)) from exc

    return filters.model_dump(exclude_none=True)


def generate_order_number() -> str:
    """Generate the next order number in the TORO-YYYY-NNN format."""

    current_year = datetime.utcnow().year
    prefix = f"TORO-{current_year}-"

    latest_order = (
        Order.query.filter(Order.order_number.like(f"{prefix}%"))
        .order_by(Order.order_number.desc())
        .first()
    )

    # Default to 001 when there are no orders for the current year yet.
    next_sequence = 1
    if latest_order:
        try:
            next_sequence = int(latest_order.order_number.split("-")[-1]) + 1
        except (AttributeError, ValueError):
            # Fallback to the DB id to avoid collisions if someone tampered
            # with the order number manually.
            next_sequence = latest_order.id + 1

    return f"{prefix}{next_sequence:03d}"


def ensure_valid_status_transition(order: Order, next_status: str) -> None:
    """Ensure status changes follow Opus 4.5 sequential flow."""

    if order.status == next_status:
        raise RequestValidationError({"status": "Order already in requested status"})

    allowed = ALLOWED_STATUS_TRANSITIONS.get(order.status, set())
    if next_status not in allowed:
        abort(
            409,
            description=(
                f"Transition {order.status!r} -> {next_status!r} is not allowed "
                f"(Opus 4.5 linear workflow)"
            ),
        )


@app.route("/api/v1/orders", methods=["POST"])
def create_order() -> Any:
    """Create a new order."""

    payload = request.get_json(silent=True)
    if payload is None:
        raise RequestValidationError({"body": "JSON body is required"})

    data = validate_order_payload(payload)

    # `status` and `order_number` are controlled server-side to prevent
    # clients from spoofing state transitions.
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


@app.route("/api/v1/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id: int) -> Any:
    """Update order status with Opus 4.5 transition checks."""

    payload = request.get_json(silent=True)
    if payload is None:
        raise RequestValidationError({"body": "JSON body is required"})

    data = OrderStatusUpdateSchema.model_validate(payload).model_dump()

    order = db.session.get(Order, order_id)
    if order is None:
        abort(404, description="Order not found")

    ensure_valid_status_transition(order, data["status"])
    order.status = data["status"]

    try:
        db.session.commit()
    except SQLAlchemyError as exc:  # pragma: no cover - DB failure path
        db.session.rollback()
        logger.exception("Failed to update status for %s: %s", order_id, exc)
        abort(500, description="Unable to update status at this time")

    logger.info(
        "Order %s transitioned to %s under %s",
        order.order_number,
        order.status,
        SPEC_VERSION,
    )

    return jsonify(order.to_dict()), 200


@app.route("/health", methods=["GET"])
def healthcheck() -> Any:
    """Lightweight readiness probe for Opus services."""

    uptime_seconds = int((datetime.utcnow() - SERVER_STARTED_AT).total_seconds())
    return (
        jsonify(
            {
                "status": "ok",
                "spec_version": SPEC_VERSION,
                "uptime_seconds": uptime_seconds,
            }
        ),
        200,
    )


@app.route("/", methods=["GET"])
def root() -> Any:
    """Tiny landing endpoint pointing operators to docs."""

    return jsonify(
        {
            "message": "TORO Maintenance Orders API",
            "docs": "USER_GUIDE.md",
            "spec_version": SPEC_VERSION,
        }
    ), 200


@app.errorhandler(RequestValidationError)
def handle_validation_error(error: RequestValidationError):
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


@app.after_request
def attach_spec_version(response):
    """Expose Opus spec version for observability."""

    response.headers.setdefault("X-Opus-Version", SPEC_VERSION)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
