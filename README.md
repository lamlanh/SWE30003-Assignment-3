# SWE30003-Assignment-3
SmartFM/
│
├── main.py                   ← entry point, runs the app
│
├── system/
│   ├── __init__.py
│   └── smartfm_system.py     ← SmartFMSystem (bootstrap)
│
├── managers/
│   ├── __init__.py
│   ├── account_manager.py    ← AccountManager class
│   ├── order_manager.py      ← OrderManager class
│   └── fleet_manager.py      ← FleetManager class
│
├── services/
│   ├── __init__.py
│   ├── authentication_manager.py  ← AuthenticationManager class
│   └── notification_service.py    ← NotificationService class
│
├── models/
│   ├── __init__.py
│   ├── customer.py           ← Customer data-holder
│   ├── order.py              ← Order data-holder
│   ├── shipment.py           ← Shipment data-holder
│   ├── vehicle.py            ← Vehicle data-holder
│   ├── driver.py             ← Driver data-holder
│   ├── invoice.py            ← Invoice data-holder
│   └── branch.py             ← Branch data-holder
│
├── ui/
│   ├── __init__.py
│   ├── main_menu.py          ← main menu UI
│   ├── customer_ui.py        ← customer registration/login screens
│   ├── order_ui.py           ← place order screens
│   └── fleet_ui.py           ← vehicle/driver management screens
│
├── storage/
│   ├── __init__.py
│   └── file_storage.py       ← read/write JSON files for data persistence
│
└── data/
    ├── customers.json        ← stored customer data
    ├── orders.json           ← stored order data
    ├── vehicles.json         ← stored vehicle data
    └── drivers.json          ← stored driver data
