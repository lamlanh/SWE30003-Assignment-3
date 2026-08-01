import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from managers.order_manager import OrderManager
from managers.payment_processor import PaymentProcessor
from utils.validator import validate_cargo_weight, validate_date


def test_create_order_sets_pending_status_and_persists(tmp_path):
    manager = OrderManager(storage_path=str(tmp_path / "orders.json"))
    order = manager.create_order(
        customer_id="CUST-001",
        cargo_description="Electronics",
        cargo_weight_kg="12.5",
        pickup_address="A",
        delivery_address="B",
        preferred_date="2026-08-10",
    )

    assert order.status == "PENDING"
    assert manager.get_order_by_id(order.order_id) is not None


def test_payment_processor_creates_invoice_and_receipt(tmp_path):
    order_manager = OrderManager(storage_path=str(tmp_path / "orders.json"))
    payment_processor = PaymentProcessor(
        order_manager=order_manager,
        storage_dir=str(tmp_path),
    )

    order = order_manager.create_order(
        customer_id="CUST-001",
        cargo_description="Books",
        cargo_weight_kg="5",
        pickup_address="X",
        delivery_address="Y",
        preferred_date="2026-08-11",
    )

    invoice = payment_processor.create_invoice(order, amount_vnd=250000)
    assert invoice.status == "UNPAID"

    receipt = payment_processor.process_payment(invoice.invoice_id, payment_method="card")

    assert receipt is not None
    assert invoice.status == "PAID"
    assert order_manager.get_order_by_id(order.order_id).status == "CONFIRMED"


def test_validator_rejects_invalid_weight_and_date():
    with pytest.raises(ValueError):
        validate_cargo_weight(-1)

    with pytest.raises(ValueError):
        validate_date("not-a-date")
