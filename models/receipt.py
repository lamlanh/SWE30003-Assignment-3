from datetime import datetime


class Receipt:
    def __init__(self, receipt_id, invoice_id, amount_vnd, payment_method, date_issued=None, customer_id=None):
        self.receipt_id = receipt_id
        self.invoice_id = invoice_id
        self.amount_vnd = amount_vnd
        self.payment_method = payment_method
        self.date_issued = date_issued or datetime.now().isoformat()
        self.customer_id = customer_id

    def to_dict(self):
        return {
            "receipt_id": self.receipt_id,
            "invoice_id": self.invoice_id,
            "amount_vnd": self.amount_vnd,
            "payment_method": self.payment_method,
            "date_issued": self.date_issued,
            "customer_id": self.customer_id,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            receipt_id=data.get("receipt_id"),
            invoice_id=data.get("invoice_id"),
            amount_vnd=data.get("amount_vnd"),
            payment_method=data.get("payment_method"),
            date_issued=data.get("date_issued"),
            customer_id=data.get("customer_id"),
        )
