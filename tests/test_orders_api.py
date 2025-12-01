import os
import sys
from copy import deepcopy
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TEST_DB_PATH = PROJECT_ROOT / "tests" / "test_toro.db"
TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
# Use an isolated SQLite database for tests before the app is imported.
os.environ.setdefault("TORO_DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")

from app import app  # noqa: E402  # pylint: disable=wrong-import-position
from database import db  # noqa: E402  # pylint: disable=wrong-import-position
from models import Order  # noqa: E402  # pylint: disable=wrong-import-position

app.config.update(TESTING=True)


@pytest.fixture(autouse=True)
def clean_database():
    """Reset the database before every test to ensure isolation."""

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()


@pytest.fixture()
def client():
    with app.test_client() as flask_client:
        yield flask_client


@pytest.fixture()
def sample_payload():
    return {
        "equipment_type": "Токарный станок",
        "equipment_id": "LAT-042",
        "issue_description": "Не работает автоматическая подача резца",
        "priority": "high",
        "requester_name": "Петров Петр",
        "department": "Цех №1",
        "contact_phone": "+7-900-123-45-67",
        "contact_email": "petrov@example.com",
    }


def create_order(client, payload):
    response = client.post("/api/v1/orders", json=payload)
    assert response.status_code == 201
    return response


def test_create_order_success(client, sample_payload):
    response = create_order(client, sample_payload)
    data = response.get_json()

    assert data["order_number"].startswith("TORO-")
    assert data["status"] == "created"
    assert data["priority"] == sample_payload["priority"]


def test_create_order_validation_error(client, sample_payload):
    invalid_payload = deepcopy(sample_payload)
    invalid_payload["contact_phone"] = "123"

    response = client.post("/api/v1/orders", json=invalid_payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "validation_error"
    assert "contact_phone" in data["details"]


def test_list_orders_can_be_filtered_by_status(client, sample_payload):
    create_order(client, sample_payload)

    second_payload = deepcopy(sample_payload)
    second_payload["equipment_id"] = "LAT-050"
    second_payload["requester_name"] = "Иванов Иван"
    create_order(client, second_payload)

    with app.app_context():
        order = Order.query.filter_by(equipment_id="LAT-050").first()
        order.status = "in_progress"
        db.session.commit()

    response = client.get("/api/v1/orders", query_string={"status": "in_progress"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["total"] == 1
    assert data["orders"][0]["equipment_id"] == "LAT-050"


def test_get_order_returns_404_for_missing_record(client):
    response = client.get("/api/v1/orders/999")

    assert response.status_code == 404
    assert response.get_json()["message"] == "Order not found"


def test_order_number_sequence_increments(client, sample_payload):
    first = create_order(client, sample_payload).get_json()["order_number"]

    second_payload = deepcopy(sample_payload)
    second_payload["equipment_id"] = "LAT-777"
    second = create_order(client, second_payload).get_json()["order_number"]

    assert first != second
    assert int(second.split("-")[-1]) == int(first.split("-")[-1]) + 1
