import sys
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("models", "utils"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

from models.shipment    import Shipment
from utils.json_helper  import JsonHelper
from utils.id_generator import IdGenerator


# ---------------------------------------------------------------------------
# Shipment status constants
# ---------------------------------------------------------------------------
STATUS_ASSIGNED   = "ASSIGNED"
STATUS_IN_TRANSIT = "IN_TRANSIT"
STATUS_DELIVERED  = "DELIVERED"


class ShipmentManager:
    """
    Manages shipment records and tracking updates in SmartFM.

    Responsibilities (CRC Card 2):
        - Create a shipment record when an order is confirmed
        - Update shipment status at each milestone
        - Record tracking events for the shipment history
        - Mark shipment as delivered and trigger payment finalisation
        - Provide shipment data to ReportGenerator

    Collaborators:
        - Shipment   (data-holder)
        - FleetManager
        - OrderManager
        - JsonHelper
        - IdGenerator
    """

    def __init__(self):
        """Initialise ShipmentManager and load shipment records from JSON."""
        self._helper    = JsonHelper()
        self._id_gen    = IdGenerator()
        self._shipments = {}   # { shipment_id: Shipment }
        self._load()

    # -----------------------------------------------------------------------
    # Load / Save
    # -----------------------------------------------------------------------
    def _load(self) -> None:
        """Load all shipment records from JSON into memory."""
        raw = self._helper.load("shipments")
        self._shipments = {
            sid: Shipment.from_dict(data)
            for sid, data in raw.items()
        }

    def save(self) -> None:
        """Save all shipment records from memory to JSON."""
        self._helper.save("shipments", {
            sid: s.to_dict() for sid, s in self._shipments.items()
        })

    # -----------------------------------------------------------------------
    # Create shipment
    # -----------------------------------------------------------------------
    def create_shipment(
        self,
        order_id   : str,
        vehicle_id : str,
        driver_id  : str
    ) -> tuple:
        """
        Create a new shipment record when an order is confirmed.

        Called by OrderManager after a vehicle and driver are assigned.
        Records the initial tracking event automatically.

        Args:
            order_id   (str): The confirmed order ID.
            vehicle_id (str): The assigned vehicle ID.
            driver_id  (str): The assigned driver ID.

        Returns:
            tuple: (success: bool, message: str, shipment: Shipment or None)
        """
        # Check no shipment already exists for this order
        existing = self.get_shipment_by_order(order_id)
        if existing:
            return (
                False,
                f"A shipment already exists for Order {order_id}: "
                f"{existing.shipment_id}.",
                None
            )

        shipment_id = self._id_gen.next_shipment_id(self._shipments)
        shipment = Shipment(
            shipment_id = shipment_id,
            order_id    = order_id,
            vehicle_id  = vehicle_id,
            driver_id   = driver_id,
            status      = STATUS_ASSIGNED
        )

        # Record initial tracking event
        shipment.add_tracking_event(
            milestone = "Order Confirmed — Vehicle and Driver Assigned",
            notes     = f"Vehicle: {vehicle_id} | Driver: {driver_id}"
        )

        self._shipments[shipment_id] = shipment
        self.save()

        return True, f"Shipment {shipment_id} created for Order {order_id}.", shipment

    # -----------------------------------------------------------------------
    # Status updates
    # -----------------------------------------------------------------------
    def mark_in_transit(self, shipment_id: str, notes: str = "") -> tuple:
        """
        Update shipment status to IN_TRANSIT.

        Called when the driver has picked up the cargo and departed.

        Args:
            shipment_id (str): The shipment to update.
            notes       (str): Optional notes about the pickup.

        Returns:
            tuple: (success: bool, message: str)
        """
        shipment = self._shipments.get(shipment_id)
        if not shipment:
            return False, f"Shipment {shipment_id} not found."

        if shipment.status != STATUS_ASSIGNED:
            return False, (
                f"Shipment {shipment_id} cannot be set to IN_TRANSIT "
                f"— current status is {shipment.status}."
            )

        shipment.status = STATUS_IN_TRANSIT
        shipment.add_tracking_event(
            milestone = "Cargo Picked Up — In Transit",
            notes     = notes or "Driver has collected the cargo and departed."
        )
        self.save()
        return True, f"Shipment {shipment_id} is now IN_TRANSIT."

    def mark_delivered(self, shipment_id: str, notes: str = "") -> tuple:
        """
        Update shipment status to DELIVERED.

        Called when the driver has completed the delivery.
        Records the delivery date and final tracking event.

        Args:
            shipment_id (str): The shipment to update.
            notes       (str): Optional delivery notes.

        Returns:
            tuple: (success: bool, message: str)
        """
        shipment = self._shipments.get(shipment_id)
        if not shipment:
            return False, f"Shipment {shipment_id} not found."

        if shipment.status not in (STATUS_ASSIGNED, STATUS_IN_TRANSIT):
            return False, (
                f"Shipment {shipment_id} cannot be marked as DELIVERED "
                f"— current status is {shipment.status}."
            )

        shipment.status         = STATUS_DELIVERED
        shipment.delivered_date = datetime.now().strftime("%Y-%m-%d")
        shipment.add_tracking_event(
            milestone = "Delivered Successfully",
            notes     = notes or "Cargo delivered to destination."
        )
        self.save()
        return True, f"Shipment {shipment_id} marked as DELIVERED."

    def add_tracking_event(
        self,
        shipment_id : str,
        milestone   : str,
        notes       : str = ""
    ) -> tuple:
        """
        Add a custom tracking event to a shipment.

        Args:
            shipment_id (str): The shipment to update.
            milestone   (str): Description of the event/milestone.
            notes       (str): Additional notes.

        Returns:
            tuple: (success: bool, message: str)
        """
        shipment = self._shipments.get(shipment_id)
        if not shipment:
            return False, f"Shipment {shipment_id} not found."

        shipment.add_tracking_event(milestone=milestone, notes=notes)
        self.save()
        return True, f"Tracking event added to Shipment {shipment_id}."

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------
    def get_shipment(self, shipment_id: str):
        """Return a Shipment by ID or None."""
        return self._shipments.get(shipment_id)

    def get_shipment_by_order(self, order_id: str):
        """
        Find the shipment linked to a specific order.

        Args:
            order_id (str): The order ID to search for.

        Returns:
            Shipment or None.
        """
        for shipment in self._shipments.values():
            if shipment.order_id == order_id:
                return shipment
        return None

    def get_all_shipments(self) -> list:
        """Return all shipments sorted by shipment ID."""
        return sorted(
            self._shipments.values(),
            key=lambda s: s.shipment_id
        )

    def get_active_shipments(self) -> list:
        """Return shipments that are currently ASSIGNED or IN_TRANSIT."""
        return [
            s for s in self._shipments.values()
            if s.status in (STATUS_ASSIGNED, STATUS_IN_TRANSIT)
        ]

    def get_shipment_count(self) -> int:
        """Return the total number of shipments."""
        return len(self._shipments)

    def __repr__(self) -> str:
        return f"ShipmentManager(shipments={len(self._shipments)})"