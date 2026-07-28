from datetime import datetime


# ---------------------------------------------------------------------------
# Order status constants
# ---------------------------------------------------------------------------
STATUS_PENDING    = "PENDING"
STATUS_CONFIRMED  = "CONFIRMED"
STATUS_IN_TRANSIT = "IN_TRANSIT"
STATUS_DELIVERED  = "DELIVERED"
STATUS_CANCELLED  = "CANCELLED"


class Order:
    """
    Data-holder class representing a customer shipment order.

    Attributes:
        order_id         (str)  : Unique system-generated identifier.
        customer_id      (str)  : Reference to the Customer who placed it.
        cargo_description(str)  : Description of the goods being shipped.
        cargo_weight_kg  (float): Weight of the cargo in kilograms.
        pickup_address   (str)  : Address where cargo will be collected.
        delivery_address (str)  : Address where cargo will be delivered.
        preferred_date   (str)  : Customer's preferred pickup date (YYYY-MM-DD).
        status           (str)  : Current status of the order.
        vehicle_id       (str)  : Assigned vehicle ID (None if not yet assigned).
        driver_id        (str)  : Assigned driver ID (None if not yet assigned).
        invoice_id       (str)  : Linked invoice ID (None if not yet generated).
        created_date     (str)  : ISO format date when order was created.
        notes            (str)  : Any special handling notes.
    """

    def __init__(
        self,
        order_id: str,
        customer_id: str,
        cargo_description: str,
        cargo_weight_kg: float,
        pickup_address: str,
        delivery_address: str,
        preferred_date: str,
        status: str = STATUS_PENDING,
        vehicle_id: str = None,
        driver_id: str = None,
        invoice_id: str = None,
        created_date: str = None,
        notes: str = ""
    ):
        self.order_id          = order_id
        self.customer_id       = customer_id
        self.cargo_description = cargo_description
        self.cargo_weight_kg   = cargo_weight_kg
        self.pickup_address    = pickup_address
        self.delivery_address  = delivery_address
        self.preferred_date    = preferred_date
        self.status            = status
        self.vehicle_id        = vehicle_id
        self.driver_id         = driver_id
        self.invoice_id        = invoice_id
        self.created_date      = created_date or datetime.now().strftime("%Y-%m-%d")
        self.notes             = notes

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert the Order object to a dictionary for JSON storage."""
        return {
            "order_id"          : self.order_id,
            "customer_id"       : self.customer_id,
            "cargo_description" : self.cargo_description,
            "cargo_weight_kg"   : self.cargo_weight_kg,
            "pickup_address"    : self.pickup_address,
            "delivery_address"  : self.delivery_address,
            "preferred_date"    : self.preferred_date,
            "status"            : self.status,
            "vehicle_id"        : self.vehicle_id,
            "driver_id"         : self.driver_id,
            "invoice_id"        : self.invoice_id,
            "created_date"      : self.created_date,
            "notes"             : self.notes
        }

    @staticmethod
    def from_dict(data: dict) -> "Order":
        """Create an Order object from a dictionary loaded from JSON."""
        return Order(
            order_id          = data["order_id"],
            customer_id       = data["customer_id"],
            cargo_description = data["cargo_description"],
            cargo_weight_kg   = data["cargo_weight_kg"],
            pickup_address    = data["pickup_address"],
            delivery_address  = data["delivery_address"],
            preferred_date    = data["preferred_date"],
            status            = data.get("status", STATUS_PENDING),
            vehicle_id        = data.get("vehicle_id"),
            driver_id         = data.get("driver_id"),
            invoice_id        = data.get("invoice_id"),
            created_date      = data.get("created_date"),
            notes             = data.get("notes", "")
        )

    def __repr__(self) -> str:
        return (
            f"Order(id={self.order_id}, "
            f"customer={self.customer_id}, "
            f"status={self.status})"
        )