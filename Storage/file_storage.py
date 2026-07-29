import json
import os


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
# Resolve the data/ folder relative to this file's location
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")

# JSON file paths
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
ORDERS_FILE    = os.path.join(DATA_DIR, "orders.json")
VEHICLES_FILE  = os.path.join(DATA_DIR, "vehicles.json")
DRIVERS_FILE   = os.path.join(DATA_DIR, "drivers.json")
SHIPMENTS_FILE = os.path.join(DATA_DIR, "shipments.json")
INVOICES_FILE  = os.path.join(DATA_DIR, "invoices.json")
BRANCHES_FILE  = os.path.join(DATA_DIR, "branches.json")


# ---------------------------------------------------------------------------
# FileStorage
# ---------------------------------------------------------------------------
class FileStorage:
    """
    Handles reading and writing JSON data files for SmartFM.

    Responsibilities:
        - Create the data/ folder and JSON files on first run
        - Load data from JSON files into Python dictionaries
        - Save Python dictionaries back to JSON files
        - Provide a clean interface for all manager classes

    All data is stored as a dictionary keyed by the record's unique ID.
    For example, customers.json looks like:
        {
            "CUST-001": { "customer_id": "CUST-001", "username": "lam", ... },
            "CUST-002": { "customer_id": "CUST-002", "username": "john", ... }
        }
    """

    def __init__(self):
        """
        Initialise FileStorage.
        Creates the data/ directory and all JSON files if they do not exist.
        """
        self._ensure_data_directory()
        self._ensure_all_files()

    # -----------------------------------------------------------------------
    # Setup helpers
    # -----------------------------------------------------------------------
    def _ensure_data_directory(self) -> None:
        """Create the data/ directory if it does not exist."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def _ensure_all_files(self) -> None:
        """
        Create all JSON files with empty dictionaries
        if they do not already exist.
        This runs on every startup — safe to call multiple times.
        """
        files = [
            CUSTOMERS_FILE,
            ORDERS_FILE,
            VEHICLES_FILE,
            DRIVERS_FILE,
            SHIPMENTS_FILE,
            INVOICES_FILE,
            BRANCHES_FILE,
        ]
        for filepath in files:
            self._ensure_file(filepath)

    def _ensure_file(self, filepath: str) -> None:
        """
        Create a JSON file with an empty dictionary if it does not exist.

        Args:
            filepath (str): Full path to the JSON file.
        """
        if not os.path.exists(filepath):
            self._write_json(filepath, {})

    # -----------------------------------------------------------------------
    # Core read / write
    # -----------------------------------------------------------------------
    def _read_json(self, filepath: str) -> dict:
        """
        Read and return the contents of a JSON file as a dictionary.

        Args:
            filepath (str): Full path to the JSON file.

        Returns:
            dict: Parsed JSON content, or empty dict if file is empty/corrupt.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupt or missing, return empty dict safely
            return {}

    def _write_json(self, filepath: str, data: dict) -> None:
        """
        Write a dictionary to a JSON file with pretty formatting.

        Args:
            filepath (str): Full path to the JSON file.
            data     (dict): Data to write.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # -----------------------------------------------------------------------
    # Customer storage
    # -----------------------------------------------------------------------
    def load_customers(self) -> dict:
        """
        Load all customer records from customers.json.

        Returns:
            dict: Dictionary of customer_id -> customer data dict.
        """
        return self._read_json(CUSTOMERS_FILE)

    def save_customers(self, customers: dict) -> None:
        """
        Save all customer records to customers.json.

        Args:
            customers (dict): Dictionary of customer_id -> customer data dict.
        """
        self._write_json(CUSTOMERS_FILE, customers)

    # -----------------------------------------------------------------------
    # Order storage
    # -----------------------------------------------------------------------
    def load_orders(self) -> dict:
        """
        Load all order records from orders.json.

        Returns:
            dict: Dictionary of order_id -> order data dict.
        """
        return self._read_json(ORDERS_FILE)

    def save_orders(self, orders: dict) -> None:
        """
        Save all order records to orders.json.

        Args:
            orders (dict): Dictionary of order_id -> order data dict.
        """
        self._write_json(ORDERS_FILE, orders)

    # -----------------------------------------------------------------------
    # Vehicle storage
    # -----------------------------------------------------------------------
    def load_vehicles(self) -> dict:
        """
        Load all vehicle records from vehicles.json.

        Returns:
            dict: Dictionary of vehicle_id -> vehicle data dict.
        """
        return self._read_json(VEHICLES_FILE)

    def save_vehicles(self, vehicles: dict) -> None:
        """
        Save all vehicle records to vehicles.json.

        Args:
            vehicles (dict): Dictionary of vehicle_id -> vehicle data dict.
        """
        self._write_json(VEHICLES_FILE, vehicles)

    # -----------------------------------------------------------------------
    # Driver storage
    # -----------------------------------------------------------------------
    def load_drivers(self) -> dict:
        """
        Load all driver records from drivers.json.

        Returns:
            dict: Dictionary of driver_id -> driver data dict.
        """
        return self._read_json(DRIVERS_FILE)

    def save_drivers(self, drivers: dict) -> None:
        """
        Save all driver records to drivers.json.

        Args:
            drivers (dict): Dictionary of driver_id -> driver data dict.
        """
        self._write_json(DRIVERS_FILE, drivers)

    # -----------------------------------------------------------------------
    # Shipment storage
    # -----------------------------------------------------------------------
    def load_shipments(self) -> dict:
        """
        Load all shipment records from shipments.json.

        Returns:
            dict: Dictionary of shipment_id -> shipment data dict.
        """
        return self._read_json(SHIPMENTS_FILE)

    def save_shipments(self, shipments: dict) -> None:
        """
        Save all shipment records to shipments.json.

        Args:
            shipments (dict): Dictionary of shipment_id -> shipment data dict.
        """
        self._write_json(SHIPMENTS_FILE, shipments)

    # -----------------------------------------------------------------------
    # Invoice storage
    # -----------------------------------------------------------------------
    def load_invoices(self) -> dict:
        """
        Load all invoice records from invoices.json.

        Returns:
            dict: Dictionary of invoice_id -> invoice data dict.
        """
        return self._read_json(INVOICES_FILE)

    def save_invoices(self, invoices: dict) -> None:
        """
        Save all invoice records to invoices.json.

        Args:
            invoices (dict): Dictionary of invoice_id -> invoice data dict.
        """
        self._write_json(INVOICES_FILE, invoices)

    # -----------------------------------------------------------------------
    # Branch storage
    # -----------------------------------------------------------------------
    def load_branches(self) -> dict:
        """
        Load all branch records from branches.json.

        Returns:
            dict: Dictionary of branch_id -> branch data dict.
        """
        return self._read_json(BRANCHES_FILE)

    def save_branches(self, branches: dict) -> None:
        """
        Save all branch records to branches.json.

        Args:
            branches (dict): Dictionary of branch_id -> branch data dict.
        """
        self._write_json(BRANCHES_FILE, branches)

    # -----------------------------------------------------------------------
    # Utility
    # -----------------------------------------------------------------------
    def get_data_directory(self) -> str:
        """Return the path to the data/ directory."""
        return DATA_DIR

    def __repr__(self) -> str:
        return f"FileStorage(data_dir={DATA_DIR})"