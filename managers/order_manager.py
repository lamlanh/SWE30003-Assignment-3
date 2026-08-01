import os
import json

from models.order import Order
from utils.id_generator import generate_new_id
from utils.json_helper import load_data, save_data
from utils.validator import validate_order_details


class OrderManager:
    def __init__(self, storage_path=None):
        self.storage_path = storage_path
        self.orders = self._load_orders()

    def _load_orders(self):
        if self.storage_path:
            file_path = self.storage_path
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                return [Order.from_dict(item) for item in data]
            return []

        data = load_data("orders.json")
        return [Order.from_dict(item) for item in data]

    def _save_orders(self):
        if self.storage_path:
            file_path = self.storage_path
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as handle:
                json.dump([order.to_dict() for order in self.orders], handle, indent=4)
            return

        save_data("orders.json", [order.to_dict() for order in self.orders])

    def create_order(self, customer_id, cargo_description, cargo_weight_kg, pickup_address, delivery_address, preferred_date):
        validated = validate_order_details(
            customer_id=customer_id,
            cargo_description=cargo_description,
            cargo_weight_kg=cargo_weight_kg,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
            preferred_date=preferred_date,
        )

        order_id = generate_new_id([order.to_dict() for order in self.orders], "order_id", "ORD")
        order = Order(
            order_id=order_id,
            customer_id=validated["customer_id"],
            cargo_description=validated["cargo_description"],
            cargo_weight_kg=validated["cargo_weight_kg"],
            pickup_address=validated["pickup_address"],
            delivery_address=validated["delivery_address"],
            preferred_date=validated["preferred_date"],
            status="PENDING",
        )
        self.orders.append(order)
        self._save_orders()
        return order

    def get_order_by_id(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def list_orders(self):
        return list(self.orders)

    def list_orders_for_customer(self, customer_id):
        return [order for order in self.orders if order.customer_id == customer_id]

    def update_order_status(self, order_id, status):
        order = self.get_order_by_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        if status not in {"PENDING", "CONFIRMED", "DELIVERED", "CANCELLED"}:
            raise ValueError("Invalid order status")
        order.status = status
        self._save_orders()
        return order

    def cancel_order(self, order_id):
        return self.update_order_status(order_id, "CANCELLED")
