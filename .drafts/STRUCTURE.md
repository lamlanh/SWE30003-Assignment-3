# SmartFM — Smart Fleet Management System

**SWE30003 Software Architectures and Design | Assignment 3**  
**Group:** HN13  
**Tech Stack:** Python + Streamlit (Frontend/GUI) + JSON (Persistent Storage)

---

## Project Structure

```
smartfm/
│
├── app.py
│   - Main Streamlit entry point. Bootstraps SmartFMSystem via
│     st.session_state and renders the sidebar navigation menu.
│   - Run with: streamlit run app.py
│
├── requirements.txt
│   - All Python dependencies (streamlit, etc.)
│   - Run: pip install -r requirements.txt before starting.
│
├── managers/
│   - Business logic and orchestration layer.
│   - All classes use the Singleton pattern — only one instance
│     exists at runtime, held in st.session_state.
│   │
│   ├── smartfm_system.py
│   │   - Core bootstrap controller (Singleton).
│   │   - Creates all manager instances in the correct order
│   │     on startup. Acts as the central reference point.
│   │
│   ├── account_manager.py
│   │   - Customer account registration, login validation,
│   │     profile updates, and password changes.
│   │   - Saves and loads from data/customers.json.
│   │
│   ├── order_manager.py
│   │   - Order creation, validation, status updates,
│   │     cancellation, and invoice generation.
│   │   - Saves and loads from data/orders.json.
│   │
│   ├── shipment_manager.py
│   │   - Shipment record creation and tracking milestone
│   │     updates once a vehicle and driver are assigned.
│   │   - Saves and loads from data/shipments.json.
│   │
│   ├── fleet_manager.py
│   │   - Vehicle and driver record management.
│   │   - Availability checks, assignments, and status updates.
│   │   - Seeds default vehicles and drivers on first run.
│   │   - Saves and loads from data/vehicles.json and drivers.json.
│   │
│   └── payment_processor.py
│       - Invoice generation and simulated payment processing.
│       - No real bank API — shows a success message instead
│         as per Assignment 3 specification.
│       - Saves and loads from data/invoices.json.
│
├── models/
│   - Domain data-holder classes (struct-like, no business logic).
│   - Each has to_dict() for saving to JSON and
│     from_dict() for loading back from JSON.
│   │
│   ├── customer.py
│   │   - Fields: customer_id, username, password_hash,
│   │     full_name, email, phone, address, registered_date.
│   │
│   ├── order.py
│   │   - Fields: order_id, customer_id, cargo_description,
│   │     cargo_weight_kg, pickup_address, delivery_address,
│   │     preferred_date, status, vehicle_id, driver_id.
│   │   - Status flow: PENDING → CONFIRMED → DELIVERED / CANCELLED
│   │
│   ├── shipment.py
│   │   - Fields: shipment_id, order_id, vehicle_id, driver_id,
│   │     status, assigned_date, delivered_date, tracking_events.
│   │
│   ├── invoice.py
│   │   - Fields: invoice_id, order_id, customer_id,
│   │     amount_vnd, status (UNPAID / PAID), date_issued.
│   │
│   ├── receipt.py
│   │   - Fields: receipt_id, invoice_id, amount_vnd,
│   │     payment_method, date_issued, customer_id.
│   │
│   ├── vehicle.py
│   │   - Fields: vehicle_id, registration, vehicle_type,
│   │     capacity_kg, branch_id, status, maintenance_note.
│   │   - Status: AVAILABLE / ASSIGNED / MAINTENANCE
│   │
│   └── driver.py
│       - Fields: driver_id, full_name, licence_number,
│         licence_expiry, phone, branch_id, status, leave_note.
│       - Status: AVAILABLE / ASSIGNED / ON_LEAVE
│
├── ui/
│   - Streamlit page files. One file per sidebar screen.
│   - Pages only handle UI rendering and user input.
│   - All business logic is delegated to managers/ classes.
│   │
│   ├── customer_page.py
│   │   - Screen 1: Customer Account Management.
│   │   - Register new customers, view and update account details.
│   │
│   ├── order_page.py
│   │   - Screen 2: Place Shipment Order.
│   │   - Select customer, enter cargo details, submit order,
│   │     view order history, cancel orders.
│   │
│   ├── fleet_page.py
│   │   - Screen 3: Fleet Dispatch.
│   │   - Assign vehicle & driver to pending orders.
│   │   - View, add, and update vehicles and drivers.
│   │
│   ├── payment_page.py
│   │   - Screen 4: Payment Processing & Receipt Generation.
│   │   - Select unpaid invoice, choose payment method,
│   │     simulate payment, display printable receipt card.
│   │
│   └── inspector_page.py
│       - Screen 5: Live JSON Data Inspector.
│       - View raw contents of all JSON data files in real time.
│       - Useful for demonstrating persistent storage in report.
│
├── utils/
│   - Shared helper utilities used across manager classes.
│   │
│   ├── json_helper.py
│   │   - All JSON file reading and writing.
│   │   - Creates data/ folder and empty JSON files
│   │     automatically on first run if they do not exist.
│   │
│   ├── id_generator.py
│   │   - Generates unique IDs for all records.
│   │   - Format: CUST-001, ORD-001, VEH-001, DRV-001, etc.
│   │
│   └── validator.py
│       - Input validation functions shared across managers.
│       - Validates: email format, phone format, date format,
│         empty fields, cargo weight, licence expiry, etc.
│
└── data/
    - Persistent JSON storage files.
    - Created automatically on first run.
    - Do NOT edit these files manually while the app is running.
    │
    ├── customers.json     ← All registered customer records
    ├── orders.json        ← All shipment order records
    ├── shipments.json     ← All shipment tracking records
    ├── invoices.json      ← All invoice and billing records
    ├── vehicles.json      ← All fleet vehicle records
    └── drivers.json       ← All fleet driver records
```

---

## Getting Started

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
streamlit run app.py
```

> **Important:** Do NOT use `python app.py` — Streamlit apps must
> be launched with `streamlit run app.py` or the UI will not render.

3. Open in browser (Streamlit opens this automatically):

```
http://localhost:8501
```

---

## Default Accounts

These accounts are created automatically on first run:

| Username | Password | Role |
|---|---|---|
| `staff` | `staff123` | STAFF |
| `admin` | `admin123` | ADMIN |

Customer accounts are created through **Screen 1: Customer Account Management**.

---

## Features

- Customer account registration and management
- Order creation, tracking, and cancellation
- Shipment scheduling and status updates
- Fleet management with vehicles and drivers
- Simulated invoice generation and payment processing
- JSON-backed persistent data storage
- Live JSON data inspector for report evidence

---

## Notes

- All business logic lives in `managers/` — do NOT put logic in `ui/` files.
- Use `utils/validator.py` for all input validation — do not duplicate checks.
- Use `utils/id_generator.py` for all ID generation — never hardcode IDs.
- The `data/` folder is created automatically — no manual setup needed.
- Each team member must own at least 2 manager CRC cards — record in contribution document.
- Screenshots for the report must show: empty UI, valid input, invalid input,
  modifying input, and successful completion for each scenario.
- Use Screen 5 (Data Inspector) to show JSON data is saving correctly in screenshots.