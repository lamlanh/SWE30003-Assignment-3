from datetime import datetime


# ---------------------------------------------------------------------------
# Shipment status constants
# ---------------------------------------------------------------------------
STATUS_ASSIGNED   = "ASSIGNED"
STATUS_IN_TRANSIT = "IN_TRANSIT"
STATUS_DELIVERED  = "DELIVERED"


class Shipment:
    """
    Data-holder class representing a physical shipment.

    Attributes:
        shipment_id      (str)  : Unique system-generated identifier.
        order_id         (str)  : Reference to the associated Order.
        vehicle_id       (str)  : ID of the assigned vehicle.
        driver_id        (str)  : ID of the assigned driver.
        status           (str)  : Current shipment status.
        assigned_date    (str)  : Date vehicle and driver were assigned.
        delivered_date   (str)  : Date delivery was completed (or None).
        tracking_events  (list) : List of tracking milestone dicts.
    """

    def __init__(
        self,
        shipment_id: str,
        order_id: str,
        vehicle_id: str,
        driver_id: str,
        status: str = STATUS_ASSIGNED,
        assigned_date: str = None,
        delivered_date: str = None,
        tracking_events: list = None
    ):
        self.shipment_id     = shipment_id
        self.order_id        = order_id
        self.vehicle_id      = vehicle_id
        self.driver_id       = driver_id
        self.status          = status
        self.assigned_date   = assigned_date or datetime.now().strftime("%Y-%m-%d")
        self.delivered_date  = delivered_date
        self.tracking_events = tracking_events or []

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def add_tracking_event(self, milestone: str, notes: str = "") -> None:
        """
        Add a tracking milestone event to the shipment history.

        Args:
            milestone (str): Type of event e.g. 'Picked Up', 'In Transit'.
            notes     (str): Optional additional notes for the event.
        """
        event = {
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M"),
            "milestone" : milestone,
            "notes"     : notes
        }
        self.tracking_events.append(event)

    def is_delivered(self) -> bool:
        """Return True if the shipment has been delivered."""
        return self.status == STATUS_DELIVERED

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert the Shipment object to a dictionary for JSON storage."""
        return {
            "shipment_id"     : self.shipment_id,
            "order_id"        : self.order_id,
            "vehicle_id"      : self.vehicle_id,
            "driver_id"       : self.driver_id,
            "status"          : self.status,
            "assigned_date"   : self.assigned_date,
            "delivered_date"  : self.delivered_date,
            "tracking_events" : self.tracking_events
        }

    @staticmethod
    def from_dict(data: dict) -> "Shipment":
        """Create a Shipment object from a dictionary loaded from JSON."""
        return Shipment(
            shipment_id     = data["shipment_id"],
            order_id        = data["order_id"],
            vehicle_id      = data["vehicle_id"],
            driver_id       = data["driver_id"],
            status          = data.get("status", STATUS_ASSIGNED),
            assigned_date   = data.get("assigned_date"),
            delivered_date  = data.get("delivered_date"),
            tracking_events = data.get("tracking_events", [])
        )

    def __repr__(self) -> str:
        return (
            f"Shipment(id={self.shipment_id}, "
            f"order={self.order_id}, "
            f"status={self.status})"
        )