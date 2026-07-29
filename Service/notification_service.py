from datetime import datetime


# ---------------------------------------------------------------------------
# Notification type constants
# ---------------------------------------------------------------------------
NOTIF_ORDER_CONFIRMED  = "ORDER_CONFIRMED"
NOTIF_ORDER_CANCELLED  = "ORDER_CANCELLED"
NOTIF_ORDER_MODIFIED   = "ORDER_MODIFIED"
NOTIF_ASSIGNED         = "ASSIGNED"
NOTIF_PAYMENT_SUCCESS  = "PAYMENT_SUCCESS"
NOTIF_RECEIPT_ISSUED   = "RECEIPT_ISSUED"
NOTIF_DRIVER_SCHEDULE  = "DRIVER_SCHEDULE"
NOTIF_DELIVERY_UPDATE  = "DELIVERY_UPDATE"
NOTIF_ACCOUNT_CREATED  = "ACCOUNT_CREATED"
NOTIF_GENERAL          = "GENERAL"


class NotificationService:
    """
    Centralised notification service for SmartFM.

    Responsibilities (from CRC Card 8):
        - Send order confirmation to customer
        - Send shipment status update to customer
        - Send payment receipt to customer
        - Alert staff of new incoming order
        - Notify driver of assignment and schedule
        - Send delivery delay notification to customer

    Collaborators:
        - Customer (data-holder)
        - Order    (data-holder)
        - Shipment (data-holder)
        - Receipt  (data-holder)
        - Driver   (data-holder)
        - ScheduleManager
    """

    # Notification prefix for visual clarity in terminal
    _PREFIX = "  [NOTIFICATION]"

    def __init__(self):
        """
        Initialise NotificationService.
        Keeps a log of all notifications sent during the session.
        """
        # In-memory log of all notifications sent this session
        # Each entry: { timestamp, recipient, type, message }
        self._notification_log = []

    # -----------------------------------------------------------------------
    # Core send method
    # -----------------------------------------------------------------------
    def send(
        self,
        recipient: str,
        notification_type: str,
        message: str
    ) -> None:
        """
        Send a notification to a recipient.

        In this terminal implementation, the notification is printed
        to the screen with a clear visual indicator. In production,
        this would send an email, SMS, or push notification.

        Args:
            recipient          (str): Name or ID of the recipient.
            notification_type  (str): Type of notification (use constants).
            message            (str): The notification message body.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Print to terminal with clear formatting
        print()
        print(f"{self._PREFIX} ─────────────────────────────")
        print(f"{self._PREFIX} To      : {recipient}")
        print(f"{self._PREFIX} Type    : {notification_type}")
        print(f"{self._PREFIX} Message : {message}")
        print(f"{self._PREFIX} Time    : {timestamp}")
        print(f"{self._PREFIX} ─────────────────────────────")
        print()

        # Log the notification
        self._notification_log.append({
            "timestamp"         : timestamp,
            "recipient"         : recipient,
            "notification_type" : notification_type,
            "message"           : message
        })

    # -----------------------------------------------------------------------
    # Specific notification methods
    # -----------------------------------------------------------------------
    def notify_account_created(self, customer_name: str) -> None:
        """
        Notify a customer that their account has been created.

        Args:
            customer_name (str): The customer's full name.
        """
        self.send(
            recipient         = customer_name,
            notification_type = NOTIF_ACCOUNT_CREATED,
            message           = (
                f"Welcome to SmartFM, {customer_name}! "
                "Your account has been created successfully. "
                "You can now log in and place shipment orders."
            )
        )

    def notify_order_confirmed(
        self,
        customer_name: str,
        order_id: str
    ) -> None:
        """
        Notify a customer that their order has been confirmed.

        Args:
            customer_name (str): The customer's full name.
            order_id      (str): The confirmed order ID.
        """
        self.send(
            recipient         = customer_name,
            notification_type = NOTIF_ORDER_CONFIRMED,
            message           = (
                f"Your order {order_id} has been confirmed. "
                "A vehicle and driver will be assigned shortly."
            )
        )

    def notify_order_cancelled(
        self,
        customer_name: str,
        order_id: str
    ) -> None:
        """
        Notify a customer that their order has been cancelled.

        Args:
            customer_name (str): The customer's full name.
            order_id      (str): The cancelled order ID.
        """
        self.send(
            recipient         = customer_name,
            notification_type = NOTIF_ORDER_CANCELLED,
            message           = (
                f"Your order {order_id} has been cancelled. "
                "If you did not request this, please contact support."
            )
        )

    def notify_vehicle_assigned(
        self,
        customer_name: str,
        order_id: str,
        vehicle_reg: str,
        driver_name: str
    ) -> None:
        """
        Notify a customer that a vehicle and driver have been assigned.

        Args:
            customer_name (str): The customer's full name.
            order_id      (str): The order ID.
            vehicle_reg   (str): The vehicle registration number.
            driver_name   (str): The assigned driver's name.
        """
        self.send(
            recipient         = customer_name,
            notification_type = NOTIF_ASSIGNED,
            message           = (
                f"Your order {order_id} has been assigned. "
                f"Vehicle: {vehicle_reg} | Driver: {driver_name}. "
                "Your shipment will be picked up on your preferred date."
            )
        )

    def notify_driver_assigned(
        self,
        driver_name: str,
        order_id: str,
        pickup_address: str,
        delivery_address: str,
        preferred_date: str
    ) -> None:
        """
        Notify a driver of their new delivery assignment.

        Args:
            driver_name      (str): The driver's full name.
            order_id         (str): The order ID to deliver.
            pickup_address   (str): Where to pick up the cargo.
            delivery_address (str): Where to deliver the cargo.
            preferred_date   (str): The preferred pickup date.
        """
        self.send(
            recipient         = driver_name,
            notification_type = NOTIF_DRIVER_SCHEDULE,
            message           = (
                f"You have been assigned to Order {order_id}. "
                f"Pickup: {pickup_address} | "
                f"Delivery: {delivery_address} | "
                f"Date: {preferred_date}."
            )
        )

    def notify_staff_new_order(
        self,
        order_id: str,
        customer_name: str
    ) -> None:
        """
        Alert staff that a new order has been placed.

        Args:
            order_id      (str): The new order ID.
            customer_name (str): The customer who placed it.
        """
        self.send(
            recipient         = "Staff / Branch Operations",
            notification_type = NOTIF_ORDER_CONFIRMED,
            message           = (
                f"New order received: {order_id} "
                f"from customer {customer_name}. "
                "Please assign a vehicle and driver."
            )
        )

    def notify_payment_received(
        self,
        customer_name: str,
        order_id: str,
        amount_vnd: float
    ) -> None:
        """
        Notify a customer that their payment has been received.

        Args:
            customer_name (str)  : The customer's full name.
            order_id      (str)  : The order ID.
            amount_vnd    (float): The amount paid in VND.
        """
        self.send(
            recipient         = customer_name,
            notification_type = NOTIF_PAYMENT_SUCCESS,
            message           = (
                f"Payment received for Order {order_id}. "
                f"Amount: {amount_vnd:,.0f} VND. "
                "A receipt has been issued to your account."
            )
        )

    def notify_general(self, recipient: str, message: str) -> None:
        """
        Send a general-purpose notification.

        Args:
            recipient (str): Name or ID of the recipient.
            message   (str): The message to send.
        """
        self.send(
            recipient         = recipient,
            notification_type = NOTIF_GENERAL,
            message           = message
        )

    # -----------------------------------------------------------------------
    # Log access
    # -----------------------------------------------------------------------
    def get_notification_log(self) -> list:
        """
        Return the full notification log for this session.

        Returns:
            list: List of notification dictionaries sent this session.
        """
        return self._notification_log

    def get_log_count(self) -> int:
        """Return the number of notifications sent this session."""
        return len(self._notification_log)

    def __repr__(self) -> str:
        return (
            f"NotificationService("
            f"notifications_sent={self.get_log_count()})"
        )