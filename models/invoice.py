from datetime import datetime


class Invoice:
    def __init__(self, invoice_id, order_id, customer_id, amount_vnd, status="UNPAID", date_issued=None):
        self.invoice_id = invoice_id
        self.order_id = order_id
        self.customer_id = customer_id
        self.amount_vnd = amount_vnd
        self.status = status
        self.date_issued = date_issued or datetime.now().isoformat()

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "amount_vnd": self.amount_vnd,
            "status": self.status,
            "date_issued": self.date_issued,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            invoice_id=data.get("invoice_id"),
            order_id=data.get("order_id"),
            customer_id=data.get("customer_id"),
            amount_vnd=data.get("amount_vnd"),
            status=data.get("status", "UNPAID"),
            date_issued=data.get("date_issued"),
        )
