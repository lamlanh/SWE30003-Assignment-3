# SWE30003-Assignment-3

SmartFM code
=======
>>>>>>> 79862ebffcee8716619d8a74f0a7bc70397356e0
SmartFM/
│
├── manage.py                 ← Django entry point (replaces main.py)
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
├── smartfm_project/          ← Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── smartfm_app/               ← Django app (replaces ui/ folder)
│   ├── __init__.py
│   ├── views.py               ← all page logic
│   ├── urls.py                ← URL routing
│   ├── forms.py               ← form definitions
│   └── templates/
│       └── smartfm_app/
│           ├── base.html      ← dark mode layout
│           ├── login.html
│           ├── register.html
│           ├── dashboard.html
│           ├── place_order.html
│           ├── my_orders.html
│           ├── fleet.html
│           └── assign_order.html
│   
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
    └── drivers.json          ← stored driver data
>>>>>>> 79862ebffcee8716619d8a74f0a7bc70397356e0
