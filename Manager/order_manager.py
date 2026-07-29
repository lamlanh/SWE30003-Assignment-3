import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("models", "storage", "services", "managers"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

from models.order import (
    Order,
    STATUS_PENDING, STATUS_CONFIRMED,
    STATUS_IN_TRANSIT, STATUS_DELIVERED, STATUS_CANCELLED
)
from models.shipment import Shipment
from models.invoice import Invoice, STATUS_UNPAID
from storage.file_storage import FileStorage
from managers.fleet_manager import FleetManager
from services.notification_service import NotificationService


class OrderManager:
    """
    Manages the full order lifecycle in SmartFM.

    Responsibilities (from CRC Card 1):
        - Create a new order from customer request
        - Validate order details (cargo weight, availability)
        - Update order status throughout the lifecycle
        - Cancel or modify an existing order
        - Notify relevant parties when order status changes
        - Provide order list to ReportGenerator

    Collaborators:
        - Customer         (data-holder)
        - Order            (data-holder)
        - Invoice          (data-holder)
        - Shipment         (data-holder)
        - FleetManager
        - NotificationService
        - FileStorage
    """

    def __init__(
        self,
        fleet_manager: FleetManager,
        notification_service: NotificationService
    ):
        """
        Initialise OrderManager.

        Args:
            fleet_manager        (FleetManager)       : For vehicle/driver checks.
            notification_service (NotificationService): For sending notifications.
        """
        self._fleet        = fleet_manager
        self._notifier     = notification_service
        self._storage      = FileStorage()

        # In-memory dictionaries
        self._orders    = {}    # { order_id: Order }
        self._shipments = {}    # { shipment_id: Shipment }
        self._invoices  = {}    # { invoice_id: Invoice }

        # ID counters
        self._order_counter    = 1
        self._shipment_counter = 1
        self._invoice_counter  = 1

        self._load()

    # -----------------------------------------------------------------------
    # Load / Save
    # -----------------------------------------------------------------------
    def _load(self) -> None:
        """Load all order, shipment, and invoice records from JSON."""
        raw_orders = self._storage.load_orders()
        self._orders = {
            oid: Order.from_dict(data)
            for oid, data in raw_orders.items()
        }

        raw_shipments = self._storage.load_shipments()
        self._shipments = {
            sid: Shipment.from_dict(data)
            for sid, data in raw_shipments.items()
        }

        raw_invoices = self._storage.load_invoices()
        self._invoices = {
            iid: Invoice.from_dict(data)
            for iid, data in raw_invoices.items()
        }

        self._order_counter    = len(self._orders)    + 1
        self._shipment_counter = len(self._shipments) + 1
        self._invoice_counter  = len(self._invoices)  + 1

    def save(self) -> None:
        """Save all order, shipment, and invoice records to JSON."""
        self._storage.save_orders({
            oid: o.to_dict() for oid, o in self._orders.items()
        })
        self._storage.save_shipments({
            sid: s.to_dict() for sid, s in self._shipments.items()
        })
        self._storage.save_invoices({
            iid: i.to_dict() for iid, i in self._invoices.items()
        })

    # -----------------------------------------------------------------------
    # ID generators
    # -----------------------------------------------------------------------
    def _generate_order_id(self) -> str:
        oid = f"ORD-{self._order_counter:03d}"
        self._order_counter += 1
        return oid

    def _generate_shipment_id(self) -> str:
        sid = f"SHIP-{self._shipment_counter:03d}"
        self._shipment_counter += 1
        return sid

    def _generate_invoice_id(self) -> str:
        iid = f"INV-{self._invoice_counter:03d}"
        self._invoice_counter += 1
        return iid

    # -----------------------------------------------------------------------
    # Place order
    # -----------------------------------------------------------------------
    def place_order(
        self,
        customer_id: str,
        customer_name: str,
        cargo_description: str,
        cargo_weight_kg: float,
        pickup_address: str,
        delivery_address: str,
        preferred_date: str,
        notes: str = ""
    ) -> tuple:
        """
        Create a new shipment order for a customer.

        Validates all fields, checks vehicle availability, creates
        the Order and Invoice, and notifies staff.

        Args:
            customer_id       (str)  : ID of the customer placing the order.
            customer_name     (str)  : Customer's name for notifications.
            cargo_description (str)  : Description of goods to ship.
            cargo_weight_kg   (float): Weight of the cargo in kg.
            pickup_address    (str)  : Where to collect the cargo.
            delivery_address  (str)  : Where to deliver the cargo.
            preferred_date    (str)  : Preferred pickup date (YYYY-MM-DD).
            notes             (str)  : Special handling notes (optional).

        Returns:
            tuple: (success: bool, message: str, order: Order or None)
        """
        # Validate inputs
        if not cargo_description.strip():
            return False, "Cargo description cannot be empty.", None
        if cargo_weight_kg <= 0:
            return False, "Cargo weight must be greater than 0 kg.", None
        if not pickup_address.strip():
            return False, "Pickup address cannot be empty.", None
        if not delivery_address.strip():
            return False, "Delivery address cannot be empty.", None
        if not preferred_date.strip():
            return False, "Preferred date cannot be empty.", None

        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(preferred_date, "%Y-%m-%d")
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format.", None

        # Check at least one vehicle can handle the cargo weight
        available_vehicles = self._fleet.get_available_vehicles(cargo_weight_kg)
        if not available_vehicles:
            return False, (
                f"No available vehicles can carry {cargo_weight_kg} kg. "
                "Please try a different date or reduce cargo weight."
            ), None

        # Check at least one driver is available
        available_drivers = self._fleet.get_available_drivers()
        if not available_drivers:
            return False, (
                "No drivers are currently available. "
                "Please try again later."
            ), None

        # Calculate invoice amount (simple rate: 10,000 VND per kg)
        amount_vnd = cargo_weight_kg * 10_000

        # Create Order
        order_id = self._generate_order_id()
        order = Order(
            order_id          = order_id,
            customer_id       = customer_id,
            cargo_description = cargo_description.strip(),
            cargo_weight_kg   = cargo_weight_kg,
            pickup_address    = pickup_address.strip(),
            delivery_address  = delivery_address.strip(),
            preferred_date    = preferred_date,
            notes             = notes.strip()
        )

        # Create Invoice
        invoice_id = self._generate_invoice_id()
        invoice = Invoice(
            invoice_id  = invoice_id,
            order_id    = order_id,
            customer_id = customer_id,
            amount_vnd  = amount_vnd
        )
        order.invoice_id = invoice_id

        # Store in memory
        self._orders[order_id]     = order
        self._invoices[invoice_id] = invoice
        self.save()

        # Notify staff of new order
        self._notifier.notify_staff_new_order(order_id, customer_name)

        # Notify customer of order confirmation
        self._notifier.notify_order_confirmed(customer_name, order_id)

        return True, (
            f"Order {order_id} placed successfully! "
            f"Invoice: {invoice_id} | Amount: {amount_vnd:,.0f} VND"
        ), order

    # -----------------------------------------------------------------------
    # Assign vehicle and driver
    # -----------------------------------------------------------------------
    def assign_vehicle_and_driver(
        self,
        order_id: str,
        vehicle_id: str,
        driver_id: str,
        customer_name: str
    ) -> tuple:
        """
        Assign a vehicle and driver to a confirmed order.

        Creates a Shipment record and updates order status to CONFIRMED.
        Notifies both the customer and the driver.

        Args:
            order_id      (str): The order to assign to.
            vehicle_id    (str): The vehicle to assign.
            driver_id     (str): The driver to assign.
            customer_name (str): Customer name for notification.

        Returns:
            tuple: (success: bool, message: str)
        """
        order = self._orders.get(order_id)
        if not order:
            return False, f"Order {order_id} not found."

        if order.status == STATUS_CANCELLED:
            return False, f"Order {order_id} has been cancelled."

        if order.status == STATUS_CONFIRMED:
            return False, f"Order {order_id} already has a vehicle assigned."

        # Assign vehicle via FleetManager
        v_success, v_msg = self._fleet.assign_vehicle(vehicle_id)
        if not v_success:
            return False, v_msg

        # Assign driver via FleetManager
        d_success, d_msg = self._fleet.assign_driver(driver_id)
        if not d_success:
            # Roll back vehicle assignment
            self._fleet.release_vehicle(vehicle_id)
            return False, d_msg

        # Update order
        order.vehicle_id = vehicle_id
        order.driver_id  = driver_id
        order.status     = STATUS_CONFIRMED

        # Create shipment record
        shipment_id = self._generate_shipment_id()
        shipment = Shipment(
            shipment_id = shipment_id,
            order_id    = order_id,
            vehicle_id  = vehicle_id,
            driver_id   = driver_id
        )
        shipment.add_tracking_event("Order Confirmed — Vehicle and Driver Assigned")
        self._shipments[shipment_id] = shipment

        self.save()

        # Get vehicle and driver details for notification
        vehicle = self._fleet.get_vehicle(vehicle_id)
        driver  = self._fleet.get_driver(driver_id)

        # Notify customer
        self._notifier.notify_vehicle_assigned(
            customer_name = customer_name,
            order_id      = order_id,
            vehicle_reg   = vehicle.registration if vehicle else vehicle_id,
            driver_name   = driver.full_name if driver else driver_id
        )

        # Notify driver
        self._notifier.notify_driver_assigned(
            driver_name      = driver.full_name if driver else driver_id,
            order_id         = order_id,
            pickup_address   = order.pickup_address,
            delivery_address = order.delivery_address,
            preferred_date   = order.preferred_date
        )

        return True, (
            f"Vehicle {vehicle_id} and Driver {driver_id} "
            f"assigned to Order {order_id}. "
            f"Shipment {shipment_id} created."
        )

    # -----------------------------------------------------------------------
    # Cancel order
    # -----------------------------------------------------------------------
    def cancel_order(
        self,
        order_id: str,
        customer_name: str
    ) -> tuple:
        """
        Cancel an existing order.

        Releases any assigned vehicle and driver back to available.
        Only orders that are PENDING or CONFIRMED can be cancelled.

        Args:
            order_id      (str): The order to cancel.
            customer_name (str): Customer name for notification.

        Returns:
            tuple: (success: bool, message: str)
        """
        order = self._orders.get(order_id)
        if not order:
            return False, f"Order {order_id} not found."

        if order.status == STATUS_CANCELLED:
            return False, f"Order {order_id} is already cancelled."

        if order.status in (STATUS_IN_TRANSIT, STATUS_DELIVERED):
            return False, (
                f"Order {order_id} cannot be cancelled — "
                "it is already in transit or delivered."
            )

        # Release vehicle and driver if already assigned
        if order.vehicle_id:
            self._fleet.release_vehicle(order.vehicle_id)
        if order.driver_id:
            self._fleet.release_driver(order.driver_id)

        order.status = STATUS_CANCELLED
        self.save()

        # Notify customer
        self._notifier.notify_order_cancelled(customer_name, order_id)

        return True, f"Order {order_id} has been cancelled."

    # -----------------------------------------------------------------------
    # Simulate payment
    # -----------------------------------------------------------------------
    def process_payment(
        self,
        order_id: str,
        customer_name: str
    ) -> tuple:
        """
        Simulate payment processing for an order.

        As per Assignment 3 specification, actual payment processing
        is not implemented. A simple confirmation message is shown.

        Args:
            order_id      (str): The order to pay for.
            customer_name (str): Customer name for notification.

        Returns:
            tuple: (success: bool, message: str)
        """
        order = self._orders.get(order_id)
        if not order:
            return False, f"Order {order_id} not found."

        if not order.invoice_id:
            return False, f"No invoice found for Order {order_id}."

        invoice = self._invoices.get(order.invoice_id)
        if not invoice:
            return False, "Invoice not found."

        if invoice.is_paid():
            return False, f"Invoice {invoice.invoice_id} is already paid."

        # Simulate payment (no real gateway in Assignment 3)
        invoice.mark_as_paid()
        self.save()

        # Notify customer
        self._notifier.notify_payment_received(
            customer_name = customer_name,
            order_id      = order_id,
            amount_vnd    = invoice.amount_vnd
        )

        return True, (
            f"[PAYMENT SIMULATED] Payment of {invoice.amount_vnd:,.0f} VND "
            f"for Order {order_id} has been processed successfully. "
            f"Receipt issued."
        )

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------
    def get_order(self, order_id: str):
        """Return an Order by ID or None."""
        return self._orders.get(order_id)

    def get_orders_by_customer(self, customer_id: str) -> list:
        """
        Return all orders for a specific customer.

        Args:
            customer_id (str): The customer ID to filter by.

        Returns:
            list: List of Order objects for that customer.
        """
        return [
            o for o in self._orders.values()
            if o.customer_id == customer_id
        ]

    def get_pending_orders(self) -> list:
        """Return all orders with PENDING status."""
        return [
            o for o in self._orders.values()
            if o.status == STATUS_PENDING
        ]

    def get_all_orders(self) -> list:
        """Return all orders."""
        return list(self._orders.values())

    def get_invoice(self, invoice_id: str):
        """Return an Invoice by ID or None."""
        return self._invoices.get(invoice_id)

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

    def __repr__(self) -> str:
        return (
            f"OrderManager("
            f"orders={len(self._orders)}, "
            f"shipments={len(self._shipments)})"
        )