# smartfm

A fleet management and order processing system for a smart freight management application.

## Project Structure

smartfm/
│
├── `app.py`
│   - Main application entry point.
│
├── `managers/`
│   - Business logic and orchestration modules.
│   ├── `smartfm_system.py` - Core system controller.
│   ├── `account_manager.py` - Customer account management.
│   ├── `order_manager.py` - Order creation and tracking.
│   ├── `shipment_manager.py` - Shipment scheduling and status updates.
│   ├── `fleet_manager.py` - Vehicle and driver coordination.
│   └── `payment_processor.py` - Invoice and payment handling.
│
├── `models/`
│   - Domain data models.
│   ├── `customer.py` - Customer profile and account data.
│   ├── `order.py` - Order data structure.
│   ├── `shipment.py` - Shipment details and status.
│   ├── `invoice.py` - Billing and invoice records.
│   ├── `receipt.py` - Payment receipts and confirmation.
│   ├── `vehicle.py` - Vehicle records and availability.
│   └── `driver.py` - Driver profiles and assignments.
│
├── `ui/`
│   - User interface screens or CLI views.
│   ├── `customer_page.py` - Customer interaction page.
│   ├── `order_page.py` - Order placement and review.
│   ├── `fleet_page.py` - Fleet monitoring and dispatch.
│   ├── `payment_page.py` - Payment processing page.
│   └── `inspector_page.py` - Inspection and audit view.
│
├── `utils/`
│   - Shared helper utilities.
│   ├── `validator.py` - Input validation functions.
│   ├── `json_helper.py` - JSON load/save helpers.
│   └── `id_generator.py` - Unique ID generation.
│
├── `data/`
│   - Persistent test or runtime data stores.
│   ├── `customers.json`
│   ├── `orders.json`
│   ├── `shipments.json`
│   ├── `invoices.json`
│   ├── `vehicles.json`
│   └── `drivers.json`
│
└── `requirements.txt`

## Getting Started

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

## Features

- Customer account management
- Order creation and tracking
- Shipment scheduling and status updates
- Fleet management with vehicles and drivers
- Invoice generation and payment processing
- JSON-backed data persistence for demo/test data

## Notes

- Update `data/` JSON files to add sample customers, orders, shipments, vehicles, and drivers.
- Use the `managers/` folder to customize business rules.
- Use the `ui/` folder to adapt the interface for CLI or GUI frameworks.
