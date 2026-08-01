# SmartFM Team Work Breakdown

Based on the project structure and the requirement that each team member must own at least 2 manager classes, the work is divided into **vertical slices**. This means each person owns a feature from the database models up to the UI frontend.

## 🧑‍💻 Member 1: Accounts & System Infrastructure (The Core)
This member sets up the foundation of the app, user management, and the debugging tools.

* **Managers (2):** `smartfm_system.py` (Bootstrap controller), `account_manager.py`
* **UI Pages:** `customer_page.py`, `inspector_page.py`
* **Models:** `customer.py`
* **Utils/Shared:** `json_helper.py`, `id_generator.py`
* **Core Focus:** Getting the Streamlit session state working properly, establishing the JSON file creation process, and handling user registration/login.

## 🧑‍💻 Member 2: Orders & Billing (The Revenue)
This member handles the customer-facing business logic of placing orders and paying for them.

* **Managers (2):** `order_manager.py`, `payment_processor.py`
* **UI Pages:** `order_page.py`, `payment_page.py`
* **Models:** `order.py`, `invoice.py`, `receipt.py`
* **Utils/Shared:** `validator.py` (crucial for validating order and payment inputs)
* **Core Focus:** Ensuring the order status flow (PENDING → CONFIRMED) works correctly and handling the simulated payment success/failure logic.

## 🧑‍💻 Member 3: Fleet & Logistics (The Operations)
This member handles the staff-facing side of assigning resources to orders and tracking them.

* **Managers (2):** `fleet_manager.py`, `shipment_manager.py`
* **UI Pages:** `fleet_page.py`
* **Models:** `vehicle.py`, `driver.py`, `shipment.py`
* **Utils/Shared:** `app.py` (Main Streamlit routing and sidebar navigation)
* **Core Focus:** Managing the availability status of vehicles and drivers (making sure a driver isn't assigned to two shipments at once) and updating shipment tracking.

---

### 💡 Workflow Tips for the Team
1. **Parallel Development:** Member 2 can mock customer IDs while Member 1 builds the Account Manager. Member 3 can mock pending orders while Member 2 builds the Order Manager.
2. **First Steps:** Member 1 should quickly push the `utils/` folder and empty `managers/` classes so the rest of the team can start importing them without errors.
3. **Validation:** Everyone should use `utils/validator.py` for their respective UI pages to maintain consistency.
