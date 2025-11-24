"""Main Flask application exposing the TORO REST API."""
from __future__ import annotations

import logging
import re
from http import HTTPStatus

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

from database import db, init_db
from models import Order, PRIORITY_CHOICES, STATUS_CHOICES

PHONE_REGEX = re.compile(r"^\+7-\d{3}-\d{3}-\d{2}-\d{2}$")
REQUIRED_FIELDS = (
    "equipment_type",
    "equipment_id",
    "issue_description",
    "requester_name",
    "department",
    "contact_phone",
)


def create_app() -> Flask:
    """Application factory used for running and testing the API."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///toro.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)  # Development-friendly CORS settings
    init_db(app)
    _configure_logging(app)
    _register_error_handlers(app)
    _register_routes(app)

    return app


def _configure_logging(app: Flask) -> None:
    """Configure logging for the service."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    app.logger.setLevel(logging.INFO)


def _register_error_handlers(app: Flask) -> None:
    """Ensure all errors are rendered as JSON responses."""

    @app.errorhandler(404)
    def handle_not_found(error):  # type: ignore[unused-argument]
        return jsonify({"error": "Resource not found"}), HTTPStatus.NOT_FOUND

    @app.errorhandler(400)
    def handle_bad_request(error):  # type: ignore[unused-argument]
        return (
            jsonify({"error": "Bad request"}),
            HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(500)
    def handle_internal_error(error):  # type: ignore[unused-argument]
        app.logger.exception("Unhandled server error")
        return (
            jsonify({"error": "Internal server error"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


def _register_routes(app: Flask) -> None:
    """Register all API routes for the service."""

    @app.route("/api/v1/orders", methods=["POST"])
    def create_order():
        payload = request.get_json(silent=True) or {}
        errors = _validate_order_payload(payload)

        if errors:
            app.logger.warning("Validation failed for new order: %s", errors)
            return jsonify({"errors": errors}), HTTPStatus.BAD_REQUEST

        try:
            order = Order(
                order_number=Order.generate_order_number(),
                equipment_type=payload["equipment_type"],
                equipment_id=payload["equipment_id"],
                issue_description=payload["issue_description"],
                priority=payload.get("priority", "medium"),
                status="created",
                requester_name=payload["requester_name"],
                department=payload["department"],
                contact_phone=payload["contact_phone"],
            )

            db.session.add(order)
            db.session.commit()
            app.logger.info("Created order %s", order.order_number)
            return jsonify(order.to_dict()), HTTPStatus.CREATED
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.exception("Database error while creating order")
            return (
                jsonify({"error": "Failed to create order"}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    @app.route("/api/v1/orders", methods=["GET"])
    def list_orders():
        priority = request.args.get("priority")
        status = request.args.get("status")
        department = request.args.get("department")

        validation_error = _validate_filters(priority, status)
        if validation_error:
            return jsonify({"error": validation_error}), HTTPStatus.BAD_REQUEST

        query = Order.query
        if priority:
            query = query.filter_by(priority=priority)
        if status:
            query = query.filter_by(status=status)
        if department:
            query = query.filter_by(department=department)

        orders = query.order_by(Order.created_at.desc()).all()
        return jsonify({"orders": [order.to_dict() for order in orders], "total": len(orders)})

    @app.route("/api/v1/orders/<int:order_id>", methods=["GET"])
    def get_order(order_id: int):
        order = Order.query.get(order_id)
        if not order:
            return (
                jsonify({"error": f"Order with id {order_id} not found"}),
                HTTPStatus.NOT_FOUND,
            )

        return jsonify(order.to_dict())


def _validate_order_payload(payload: dict) -> dict:
    """Validate incoming order payloads."""
    errors = {}

    for field in REQUIRED_FIELDS:
        if not payload.get(field):
            errors[field] = "Field is required"

    priority = payload.get("priority", "medium")
    if priority not in PRIORITY_CHOICES:
        errors["priority"] = f"Priority must be one of: {', '.join(PRIORITY_CHOICES)}"

    status = payload.get("status")
    if status and status not in STATUS_CHOICES:
        errors["status"] = f"Status must be one of: {', '.join(STATUS_CHOICES)}"

    phone = payload.get("contact_phone")
    if phone and not PHONE_REGEX.match(phone):
        errors["contact_phone"] = "Phone must match +7-XXX-XXX-XX-XX format"

    return errors


def _validate_filters(priority: str | None, status: str | None) -> str | None:
    """Validate query parameters for list endpoint."""
    if priority and priority not in PRIORITY_CHOICES:
        return f"priority must be one of: {', '.join(PRIORITY_CHOICES)}"
    if status and status not in STATUS_CHOICES:
        return f"status must be one of: {', '.join(STATUS_CHOICES)}"
    return None


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
