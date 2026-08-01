import re
from datetime import datetime


def validate_required(value, field_name="Value"):
    if value is None:
        raise ValueError(f"{field_name} is required")
    if isinstance(value, str) and not value.strip():
        raise ValueError(f"{field_name} is required")
    return str(value).strip()


def validate_email(email):
    value = validate_required(email, "Email")
    if "@" not in value or "." not in value:
        raise ValueError("Email must be a valid email address")
    return value


def validate_phone(phone):
    value = validate_required(phone, "Phone")
    if not re.fullmatch(r"[\d\s+()-]{7,15}", value):
        raise ValueError("Phone must be a valid phone number")
    return value


def validate_date(date_value):
    value = validate_required(date_value, "Date")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Date must be in YYYY-MM-DD format") from exc
    return parsed.strftime("%Y-%m-%d")


def validate_cargo_weight(weight):
    value = validate_required(weight, "Cargo weight")
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError("Cargo weight must be a valid number") from exc
    if parsed <= 0:
        raise ValueError("Cargo weight must be greater than zero")
    return parsed


def validate_amount(amount_vnd):
    value = validate_required(amount_vnd, "Amount")
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError("Amount must be a valid number") from exc
    if parsed <= 0:
        raise ValueError("Amount must be greater than zero")
    return parsed


def validate_payment_method(payment_method):
    value = validate_required(payment_method, "Payment method")
    return value


def validate_order_details(customer_id, cargo_description, cargo_weight_kg, pickup_address, delivery_address, preferred_date):
    customer_id = validate_required(customer_id, "Customer ID")
    cargo_description = validate_required(cargo_description, "Cargo description")
    pickup_address = validate_required(pickup_address, "Pickup address")
    delivery_address = validate_required(delivery_address, "Delivery address")
    preferred_date = validate_date(preferred_date)
    cargo_weight_kg = validate_cargo_weight(cargo_weight_kg)
    return {
        "customer_id": customer_id,
        "cargo_description": cargo_description,
        "cargo_weight_kg": cargo_weight_kg,
        "pickup_address": pickup_address,
        "delivery_address": delivery_address,
        "preferred_date": preferred_date,
    }


def validate_payment_details(amount_vnd, payment_method):
    amount = validate_amount(amount_vnd)
    payment_method = validate_payment_method(payment_method)
    return {"amount_vnd": amount, "payment_method": payment_method}
