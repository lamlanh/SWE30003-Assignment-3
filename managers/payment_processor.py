import os
import json

from models.invoice import Invoice
from models.receipt import Receipt
from utils.id_generator import generate_new_id
from utils.json_helper import load_data, save_data
from utils.validator import validate_payment_details


class PaymentProcessor:
    def __init__(self, order_manager=None, storage_dir=None):
        self.order_manager = order_manager
        self.storage_dir = storage_dir
        self.invoices = self._load_invoices()
        self.receipts = self._load_receipts()

    def _load_invoices(self):
        data = self._load_json("invoices.json")
        return [Invoice.from_dict(item) for item in data]

    def _load_receipts(self):
        data = self._load_json("receipts.json")
        return [Receipt.from_dict(item) for item in data]

    def _load_json(self, filename):
        if self.storage_dir:
            file_path = os.path.join(self.storage_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as handle:
                    return json.load(handle)
            return []

        data = load_data(filename)
        return data

    def _save_json(self, filename, data):
        if self.storage_dir:
            os.makedirs(self.storage_dir, exist_ok=True)
            file_path = os.path.join(self.storage_dir, filename)
            with open(file_path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=4)
            return

        save_data(filename, data)

    def create_invoice(self, order, amount_vnd):
        if order is None:
            raise ValueError("Order is required")
        if self.order_manager is not None:
            existing_order = self.order_manager.get_order_by_id(order.order_id)
            if existing_order is None:
                raise ValueError("Order not found")

        validated = validate_payment_details(amount_vnd=amount_vnd, payment_method="card")
        invoice_id = generate_new_id([invoice.to_dict() for invoice in self.invoices], "invoice_id", "INV")
        invoice = Invoice(
            invoice_id=invoice_id,
            order_id=order.order_id,
            customer_id=order.customer_id,
            amount_vnd=validated["amount_vnd"],
            status="UNPAID",
        )
        self.invoices.append(invoice)
        self._save_json("invoices.json", [invoice.to_dict() for invoice in self.invoices])
        return invoice

    def process_payment(self, invoice_id, payment_method="card"):
        invoice = self.get_invoice_by_id(invoice_id)
        if invoice is None:
            raise ValueError("Invoice not found")
        validated = validate_payment_details(amount_vnd=invoice.amount_vnd, payment_method=payment_method)
        invoice.status = "PAID"

        if self.order_manager is not None:
            self.order_manager.update_order_status(invoice.order_id, "CONFIRMED")

        receipt = Receipt(
            receipt_id=generate_new_id([receipt.to_dict() for receipt in self.receipts], "receipt_id", "RCT"),
            invoice_id=invoice.invoice_id,
            amount_vnd=validated["amount_vnd"],
            payment_method=validated["payment_method"],
            customer_id=invoice.customer_id,
        )
        self.receipts.append(receipt)
        self._save_json("receipts.json", [receipt.to_dict() for receipt in self.receipts])
        self._save_json("invoices.json", [invoice.to_dict() for invoice in self.invoices])
        return receipt

    def get_invoice_by_id(self, invoice_id):
        for invoice in self.invoices:
            if invoice.invoice_id == invoice_id:
                return invoice
        return None

    def get_receipt_by_id(self, receipt_id):
        for receipt in self.receipts:
            if receipt.receipt_id == receipt_id:
                return receipt
        return None

    def list_unpaid_invoices(self):
        return [invoice for invoice in self.invoices if invoice.status != "PAID"]
