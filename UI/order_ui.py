import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("managers", "services", "models"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

DIVIDER = "=" * 60
THIN    = "-" * 60


def print_header(title: str) -> None:
    print()
    print(DIVIDER)
    print(f"  {title}")
    print(DIVIDER)


def get_input(prompt: str) -> str:
    return input(f"  {prompt}").strip()


class OrderUI:
    """
    Terminal UI for order operations in SmartFM.

    Customer operations:
        - Place a new order
        - View orders
        - Cancel an order
        - Pay for an order

    Staff operations:
        - View pending orders
        - Assign vehicle and driver to an order
    """

    def __init__(self, system):
        self._system   = system
        self._auth     = system.authentication_manager
        self._orders   = system.order_manager
        self._fleet    = system.fleet_manager
        self._accounts = system.account_manager

    # -----------------------------------------------------------------------
    # Place order (customer)
    # -----------------------------------------------------------------------
    def place_order(self, customer_id: str) -> None:
        """Walk a customer through placing a new shipment order."""
        print_header("PLACE A NEW SHIPMENT ORDER")
        print("  Please enter your shipment details below.")
        print("  (Type 'back' at any field to return to menu.)")
        print(THIN)

        # Get customer name for notifications
        customer = self._accounts.get_by_id(customer_id)
        customer_name = customer.full_name if customer else "Customer"

        # Show available vehicle types and weight limits
        print("  Available vehicle types:")
        print("    SMALL  — up to 1,000 kg")
        print("    MEDIUM — up to 5,000 kg")
        print("    LARGE  — up to 15,000 kg")
        print(THIN)

        cargo_desc = get_input("Cargo description    : ")
        if cargo_desc.lower() == "back":
            return

        # Validate cargo weight
        while True:
            weight_str = get_input("Cargo weight (kg)    : ")
            if weight_str.lower() == "back":
                return
            try:
                cargo_weight = float(weight_str)
                if cargo_weight <= 0:
                    print("  ERROR: Weight must be greater than 0.")
                    continue
                break
            except ValueError:
                print("  ERROR: Please enter a valid number.")

        pickup = get_input("Pickup address       : ")
        if pickup.lower() == "back":
            return

        delivery = get_input("Delivery address     : ")
        if delivery.lower() == "back":
            return

        # Validate date format
        while True:
            date_str = get_input("Preferred date (YYYY-MM-DD): ")
            if date_str.lower() == "back":
                return
            try:
                from datetime import datetime
                datetime.strptime(date_str, "%Y-%m-%d")
                break
            except ValueError:
                print("  ERROR: Date must be in YYYY-MM-DD format (e.g. 2026-08-15).")

        notes = get_input("Special notes (optional): ")
        if notes.lower() == "back":
            return

        # Show estimated cost
        estimated = cargo_weight * 10_000
        print()
        print(f"  Estimated cost: {estimated:,.0f} VND")
        print(f"  (Rate: 10,000 VND per kg)")
        print()

        confirm = get_input("Confirm order? (y/n): ")
        if confirm.lower() != "y":
            print("\n  Order cancelled.")
            input("\n  Press Enter to continue...")
            return

        # Place the order
        success, message, order = self._orders.place_order(
            customer_id       = customer_id,
            customer_name     = customer_name,
            cargo_description = cargo_desc,
            cargo_weight_kg   = cargo_weight,
            pickup_address    = pickup,
            delivery_address  = delivery,
            preferred_date    = date_str,
            notes             = notes
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # View orders (customer)
    # -----------------------------------------------------------------------
    def view_orders(self, customer_id: str) -> None:
        """Display all orders for a specific customer."""
        print_header("MY ORDERS")

        orders = self._orders.get_orders_by_customer(customer_id)

        if not orders:
            print("  You have no orders yet.")
            input("\n  Press Enter to continue...")
            return

        for order in orders:
            invoice = self._orders.get_invoice(order.invoice_id) if order.invoice_id else None
            print(THIN)
            print(f"  Order ID         : {order.order_id}")
            print(f"  Status           : {order.status}")
            print(f"  Cargo            : {order.cargo_description}")
            print(f"  Weight           : {order.cargo_weight_kg} kg")
            print(f"  Pickup           : {order.pickup_address}")
            print(f"  Delivery         : {order.delivery_address}")
            print(f"  Preferred Date   : {order.preferred_date}")
            print(f"  Vehicle Assigned : {order.vehicle_id or 'Not yet assigned'}")
            print(f"  Driver Assigned  : {order.driver_id  or 'Not yet assigned'}")
            if invoice:
                print(f"  Invoice          : {invoice.invoice_id}")
                print(f"  Amount           : {invoice.amount_vnd:,.0f} VND")
                print(f"  Payment Status   : {invoice.status}")
            if order.notes:
                print(f"  Notes            : {order.notes}")

        print(THIN)
        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Cancel order (customer)
    # -----------------------------------------------------------------------
    def cancel_order(self, customer_id: str) -> None:
        """Allow a customer to cancel one of their orders."""
        print_header("CANCEL AN ORDER")

        customer = self._accounts.get_by_id(customer_id)
        customer_name = customer.full_name if customer else "Customer"

        orders = self._orders.get_orders_by_customer(customer_id)
        # Only show orders that can be cancelled
        cancellable = [
            o for o in orders
            if o.status in ("PENDING", "CONFIRMED")
        ]

        if not cancellable:
            print("  You have no orders available to cancel.")
            input("\n  Press Enter to continue...")
            return

        print("  Orders available for cancellation:")
        print(THIN)
        for order in cancellable:
            print(f"  {order.order_id} | {order.status} | {order.cargo_description} | {order.preferred_date}")

        print(THIN)
        order_id = get_input("Enter Order ID to cancel (or 'back'): ")
        if order_id.lower() == "back":
            return

        # Validate the order belongs to this customer
        order = self._orders.get_order(order_id)
        if not order or order.customer_id != customer_id:
            print("\n  ERROR: Order not found or does not belong to your account.")
            input("\n  Press Enter to continue...")
            return

        confirm = get_input(f"Are you sure you want to cancel {order_id}? (y/n): ")
        if confirm.lower() != "y":
            print("\n  Cancellation aborted.")
            input("\n  Press Enter to continue...")
            return

        success, message = self._orders.cancel_order(order_id, customer_name)

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Pay for order (customer)
    # -----------------------------------------------------------------------
    def pay_for_order(self, customer_id: str) -> None:
        """Allow a customer to pay for a confirmed order."""
        print_header("PAY FOR AN ORDER")

        customer = self._accounts.get_by_id(customer_id)
        customer_name = customer.full_name if customer else "Customer"

        orders = self._orders.get_orders_by_customer(customer_id)
        # Only show confirmed, unpaid orders
        payable = []
        for o in orders:
            if o.status in ("CONFIRMED", "PENDING") and o.invoice_id:
                invoice = self._orders.get_invoice(o.invoice_id)
                if invoice and not invoice.is_paid():
                    payable.append((o, invoice))

        if not payable:
            print("  No orders pending payment.")
            input("\n  Press Enter to continue...")
            return

        print("  Orders pending payment:")
        print(THIN)
        for order, invoice in payable:
            print(
                f"  {order.order_id} | {order.cargo_description} | "
                f"{invoice.amount_vnd:,.0f} VND | Status: {order.status}"
            )

        print(THIN)
        order_id = get_input("Enter Order ID to pay (or 'back'): ")
        if order_id.lower() == "back":
            return

        # Validate
        order = self._orders.get_order(order_id)
        if not order or order.customer_id != customer_id:
            print("\n  ERROR: Order not found.")
            input("\n  Press Enter to continue...")
            return

        invoice = self._orders.get_invoice(order.invoice_id)
        if not invoice:
            print("\n  ERROR: Invoice not found.")
            input("\n  Press Enter to continue...")
            return

        print()
        print(f"  Order    : {order_id}")
        print(f"  Amount   : {invoice.amount_vnd:,.0f} VND")
        print()
        print("  Payment methods:")
        print("  [1] Credit / Debit Card (simulated)")
        print("  [2] Cash at branch")
        print()

        method = get_input("Select payment method (or 'back'): ")
        if method.lower() == "back":
            return

        if method not in ("1", "2"):
            print("\n  ERROR: Invalid payment method.")
            input("\n  Press Enter to continue...")
            return

        method_name = "Credit/Debit Card" if method == "1" else "Cash at Branch"
        print(f"\n  Processing payment via {method_name}...")

        success, message = self._orders.process_payment(order_id, customer_name)

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # View pending orders (staff)
    # -----------------------------------------------------------------------
    def view_pending_orders(self) -> None:
        """Display all pending orders for staff to process."""
        print_header("PENDING ORDERS")

        pending = self._orders.get_pending_orders()

        if not pending:
            print("  No pending orders at this time.")
            input("\n  Press Enter to continue...")
            return

        for order in pending:
            customer = self._accounts.get_by_id(order.customer_id)
            cust_name = customer.full_name if customer else order.customer_id
            print(THIN)
            print(f"  Order ID    : {order.order_id}")
            print(f"  Customer    : {cust_name}")
            print(f"  Cargo       : {order.cargo_description}")
            print(f"  Weight      : {order.cargo_weight_kg} kg")
            print(f"  Pickup      : {order.pickup_address}")
            print(f"  Delivery    : {order.delivery_address}")
            print(f"  Date        : {order.preferred_date}")
            if order.notes:
                print(f"  Notes       : {order.notes}")

        print(THIN)
        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Assign vehicle and driver (staff)
    # -----------------------------------------------------------------------
    def assign_vehicle_driver(self) -> None:
        """Allow staff to assign a vehicle and driver to a pending order."""
        print_header("ASSIGN VEHICLE & DRIVER TO ORDER")

        pending = self._orders.get_pending_orders()
        if not pending:
            print("  No pending orders to assign.")
            input("\n  Press Enter to continue...")
            return

        print("  Pending orders:")
        print(THIN)
        for order in pending:
            print(
                f"  {order.order_id} | {order.cargo_description} | "
                f"{order.cargo_weight_kg} kg | {order.preferred_date}"
            )

        print(THIN)
        order_id = get_input("Enter Order ID to assign (or 'back'): ")
        if order_id.lower() == "back":
            return

        order = self._orders.get_order(order_id)
        if not order:
            print("\n  ERROR: Order not found.")
            input("\n  Press Enter to continue...")
            return

        # Show available vehicles for this cargo weight
        available_vehicles = self._fleet.get_available_vehicles(order.cargo_weight_kg)
        if not available_vehicles:
            print(f"\n  ERROR: No vehicles available for {order.cargo_weight_kg} kg cargo.")
            input("\n  Press Enter to continue...")
            return

        print()
        print("  Available vehicles:")
        print(THIN)
        for v in available_vehicles:
            print(
                f"  {v.vehicle_id} | {v.registration} | "
                f"{v.vehicle_type} | Capacity: {v.capacity_kg} kg"
            )

        print(THIN)
        vehicle_id = get_input("Enter Vehicle ID (or 'back'): ")
        if vehicle_id.lower() == "back":
            return

        # Show available drivers
        available_drivers = self._fleet.get_available_drivers()
        if not available_drivers:
            print("\n  ERROR: No drivers currently available.")
            input("\n  Press Enter to continue...")
            return

        print()
        print("  Available drivers:")
        print(THIN)
        for d in available_drivers:
            print(
                f"  {d.driver_id} | {d.full_name} | "
                f"Licence: {d.licence_number} | Phone: {d.phone}"
            )

        print(THIN)
        driver_id = get_input("Enter Driver ID (or 'back'): ")
        if driver_id.lower() == "back":
            return

        # Get customer name for notification
        customer = self._accounts.get_by_id(order.customer_id)
        customer_name = customer.full_name if customer else order.customer_id

        # Perform assignment
        success, message = self._orders.assign_vehicle_and_driver(
            order_id      = order_id,
            vehicle_id    = vehicle_id,
            driver_id     = driver_id,
            customer_name = customer_name
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")