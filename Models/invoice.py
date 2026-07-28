from datetime import datetime


# ---------------------------------------------------------------------------
# Invoice status constants
# ---------------------------------------------------------------------------
STATUS_UNPAID = "UNPAID"
STATUS_PAID   = "PAID"


class Invoice:
    """
    Data-holder class representing a financial invoice for an order.

    Attributes:
        invoice_id   (str)  : Unique system-generated identifier.
        order_id     (str)  : Reference to the associated Order.
        customer_id  (str)  : Reference to the Customer being billed.
        amount_vnd   (float): Total amount due in Vietnamese Dong (VND).
        status       (str)  : Payment status (UNPAID / PAID).
        date_issued  (str)  : ISO format date when invoice was created.
        date_paid    (str)  : ISO format date when payment was made (or None).
    """

    def __init__(
        self,
        invoice_id: str,
        order_id: str,
        customer_id: str,
        amount_vnd: float,
        status: str = STATUS_UNPAID,
        date_issued: str = None,
        date_paid: str = None
    ):
        self.invoice_id  = invoice_id
        self.order_id    = order_id
        self.customer_id = customer_id
        self.amount_vnd  = amount_vnd
        self.status      = status
        self.date_issued = date_issued or datetime.now().strftime("%Y-%m-%d")
        self.date_paid   = date_paid

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def is_paid(self) -> bool:
        """Return True if the invoice has been paid."""
        return self.status == STATUS_PAID

    def mark_as_paid(self) -> None:
        """Mark the invoice as paid and record the payment date."""
        self.status    = STATUS_PAID
        self.date_paid = datetime.now().strftime("%Y-%m-%d")

    # -----------------------------------------------------------------------
    # Serialisation
    # -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert the Invoice object to a dictionary for JSON storage."""
        return {
            "invoice_id"  : self.invoice_id,
            "order_id"    : self.order_id,
            "customer_id" : self.customer_id,
            "amount_vnd"  : self.amount_vnd,
            "status"      : self.status,
            "date_issued" : self.date_issued,
            "date_paid"   : self.date_paid
        }

    @staticmethod
    def from_dict(data: dict) -> "Invoice":
        """Create an Invoice object from a dictionary loaded from JSON."""
        return Invoice(
            invoice_id  = data["invoice_id"],
            order_id    = data["order_id"],
            customer_id = data["customer_id"],
            amount_vnd  = data["amount_vnd"],
            status      = data.get("status", STATUS_UNPAID),
            date_issued = data.get("date_issued"),
            date_paid   = data.get("date_paid")
        )

    def __repr__(self) -> str:
        return (
            f"Invoice(id={self.invoice_id}, "
            f"order={self.order_id}, "
            f"amount={self.amount_vnd:,.0f} VND, "
            f"status={self.status})"
        )