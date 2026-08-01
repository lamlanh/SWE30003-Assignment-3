from datetime import datetime


class Order:
    def __init__(
        self,
        order_id,
        customer_id,
        cargo_description,
        cargo_weight_kg,
        pickup_address,
        delivery_address,
        preferred_date,
        status="PENDING",
        vehicle_id=None,
        driver_id=None,
        created_date=None,
    ):
        self.order_id = order_id
        self.customer_id = customer_id
        self.cargo_description = cargo_description
        self.cargo_weight_kg = cargo_weight_kg
        self.pickup_address = pickup_address
        self.delivery_address = delivery_address
        self.preferred_date = preferred_date
        self.status = status
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.created_date = created_date or datetime.now().isoformat()

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "cargo_description": self.cargo_description,
            "cargo_weight_kg": self.cargo_weight_kg,
            "pickup_address": self.pickup_address,
            "delivery_address": self.delivery_address,
            "preferred_date": self.preferred_date,
            "status": self.status,
            "vehicle_id": self.vehicle_id,
            "driver_id": self.driver_id,
            "created_date": self.created_date,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            order_id=data.get("order_id"),
            customer_id=data.get("customer_id"),
            cargo_description=data.get("cargo_description"),
            cargo_weight_kg=data.get("cargo_weight_kg"),
            pickup_address=data.get("pickup_address"),
            delivery_address=data.get("delivery_address"),
            preferred_date=data.get("preferred_date"),
            status=data.get("status", "PENDING"),
            vehicle_id=data.get("vehicle_id"),
            driver_id=data.get("driver_id"),
            created_date=data.get("created_date"),
        )
