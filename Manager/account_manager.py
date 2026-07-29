import sys
import os

# Ensure model and storage paths are importable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("models", "storage", "services"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

from models.customer import Customer
from storage.file_storage import FileStorage
from service.authentication_manager import AuthenticationManager


class AccountManager:
    """
    Manages customer accounts in SmartFM.

    Responsibilities (from CRC Card 7):
        - Register a new customer account
        - Validate uniqueness of username and email during registration
        - Update customer personal details or delivery addresses
        - Retrieve customer account details for order processing
        - Deactivate or remove a customer account

    Collaborators:
        - Customer (data-holder)
        - AuthenticationManager (for password hashing)
        - FileStorage (for persistence)
    """

    def __init__(self, auth_manager: AuthenticationManager):
        """
        Initialise AccountManager.

        Args:
            auth_manager (AuthenticationManager): Used for password hashing.
        """
        self._auth_manager = auth_manager
        self._storage      = FileStorage()

        # In-memory dictionary of all customers
        # Format: { customer_id: Customer }
        self._customers = {}

        # Load existing customers from JSON on startup
        self._load()

        # Counter for generating unique customer IDs
        self._id_counter = len(self._customers) + 1

    # -----------------------------------------------------------------------
    # Load / Save
    # -----------------------------------------------------------------------
    def _load(self) -> None:
        """Load all customer records from JSON into memory."""
        raw = self._storage.load_customers()
        self._customers = {
            cid: Customer.from_dict(data)
            for cid, data in raw.items()
        }

    def save(self) -> None:
        """Save all customer records from memory to JSON."""
        data = {
            cid: customer.to_dict()
            for cid, customer in self._customers.items()
        }
        self._storage.save_customers(data)

    # -----------------------------------------------------------------------
    # ID generation
    # -----------------------------------------------------------------------
    def _generate_id(self) -> str:
        """
        Generate a unique customer ID.

        Returns:
            str: A unique ID in the format CUST-001.
        """
        customer_id = f"CUST-{self._id_counter:03d}"
        self._id_counter += 1
        return customer_id

    # -----------------------------------------------------------------------
    # Registration
    # -----------------------------------------------------------------------
    def register(
        self,
        username: str,
        plain_password: str,
        full_name: str,
        email: str,
        phone: str,
        address: str
    ) -> tuple:
        """
        Register a new customer account.

        Validates that the username and email are unique before creating
        the account. Passwords are hashed before storage.

        Args:
            username       (str): Desired login username.
            plain_password (str): Raw password (will be hashed).
            full_name      (str): Customer's full name.
            email          (str): Customer's email address.
            phone          (str): Customer's phone number.
            address        (str): Customer's primary delivery address.

        Returns:
            tuple: (success: bool, message: str, customer: Customer or None)
        """
        # Validate required fields are not empty
        if not username.strip():
            return False, "Username cannot be empty.", None
        if not plain_password.strip():
            return False, "Password cannot be empty.", None
        if not full_name.strip():
            return False, "Full name cannot be empty.", None
        if not email.strip():
            return False, "Email cannot be empty.", None
        if not phone.strip():
            return False, "Phone number cannot be empty.", None
        if not address.strip():
            return False, "Address cannot be empty.", None

        # Check username uniqueness
        if self._username_exists(username):
            return False, f"Username '{username}' is already taken.", None

        # Check email uniqueness
        if self._email_exists(email):
            return False, f"Email '{email}' is already registered.", None

        # Validate email format (basic check)
        if "@" not in email or "." not in email:
            return False, "Please enter a valid email address.", None

        # Validate phone (must be digits only, min 9 digits)
        phone_digits = phone.replace(" ", "").replace("-", "")
        if not phone_digits.isdigit() or len(phone_digits) < 9:
            return False, "Phone number must be at least 9 digits.", None

        # Hash the password before storing
        password_hash = self._auth_manager.hash_password(plain_password)

        # Create customer ID and object
        customer_id = self._generate_id()
        customer = Customer(
            customer_id   = customer_id,
            username      = username.strip(),
            password_hash = password_hash,
            full_name     = full_name.strip(),
            email         = email.strip().lower(),
            phone         = phone.strip(),
            address       = address.strip()
        )

        # Store in memory and persist to JSON
        self._customers[customer_id] = customer
        self.save()

        return True, f"Account created successfully! Your ID is {customer_id}.", customer

    # -----------------------------------------------------------------------
    # Login helper
    # -----------------------------------------------------------------------
    def find_by_username(self, username: str):
        """
        Find a customer by their username.

        Args:
            username (str): The username to search for.

        Returns:
            Customer or None: The matching Customer object, or None.
        """
        for customer in self._customers.values():
            if customer.username.lower() == username.strip().lower():
                return customer
        return None

    def get_by_id(self, customer_id: str):
        """
        Retrieve a customer by their ID.

        Args:
            customer_id (str): The customer ID to look up.

        Returns:
            Customer or None: The matching Customer object, or None.
        """
        return self._customers.get(customer_id)

    # -----------------------------------------------------------------------
    # Update
    # -----------------------------------------------------------------------
    def update_customer(
        self,
        customer_id: str,
        full_name: str = None,
        email: str = None,
        phone: str = None,
        address: str = None
    ) -> tuple:
        """
        Update a customer's personal details.

        Only fields that are provided (not None) will be updated.

        Args:
            customer_id (str): The ID of the customer to update.
            full_name   (str): New full name (optional).
            email       (str): New email address (optional).
            phone       (str): New phone number (optional).
            address     (str): New delivery address (optional).

        Returns:
            tuple: (success: bool, message: str)
        """
        customer = self._customers.get(customer_id)
        if not customer:
            return False, f"Customer {customer_id} not found."

        # Update only provided fields
        if full_name and full_name.strip():
            customer.full_name = full_name.strip()

        if email and email.strip():
            # Check email is not taken by another customer
            if self._email_exists(email, exclude_id=customer_id):
                return False, f"Email '{email}' is already in use."
            customer.email = email.strip().lower()

        if phone and phone.strip():
            phone_digits = phone.replace(" ", "").replace("-", "")
            if not phone_digits.isdigit() or len(phone_digits) < 9:
                return False, "Phone number must be at least 9 digits."
            customer.phone = phone.strip()

        if address and address.strip():
            customer.address = address.strip()

        self.save()
        return True, "Account updated successfully."

    def change_password(
        self,
        customer_id: str,
        old_password: str,
        new_password: str
    ) -> tuple:
        """
        Change a customer's password.

        Args:
            customer_id  (str): The ID of the customer.
            old_password (str): The current password for verification.
            new_password (str): The new password to set.

        Returns:
            tuple: (success: bool, message: str)
        """
        customer = self._customers.get(customer_id)
        if not customer:
            return False, "Customer not found."

        # Verify old password
        if not self._auth_manager.verify_password(old_password, customer.password_hash):
            return False, "Current password is incorrect."

        if not new_password.strip():
            return False, "New password cannot be empty."

        if len(new_password) < 6:
            return False, "New password must be at least 6 characters."

        customer.password_hash = self._auth_manager.hash_password(new_password)
        self.save()
        return True, "Password changed successfully."

    # -----------------------------------------------------------------------
    # Deactivate
    # -----------------------------------------------------------------------
    def deactivate_account(self, customer_id: str) -> tuple:
        """
        Deactivate a customer account.

        Args:
            customer_id (str): The ID of the customer to deactivate.

        Returns:
            tuple: (success: bool, message: str)
        """
        customer = self._customers.get(customer_id)
        if not customer:
            return False, "Customer not found."

        customer.is_active = False
        self.save()
        return True, f"Account {customer_id} has been deactivated."

    # -----------------------------------------------------------------------
    # Validation helpers
    # -----------------------------------------------------------------------
    def _username_exists(self, username: str) -> bool:
        """
        Check if a username is already taken.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the username already exists.
        """
        return any(
            c.username.lower() == username.strip().lower()
            for c in self._customers.values()
        )

    def _email_exists(self, email: str, exclude_id: str = None) -> bool:
        """
        Check if an email is already registered.

        Args:
            email      (str): The email to check.
            exclude_id (str): Customer ID to exclude from check (for updates).

        Returns:
            bool: True if the email already exists.
        """
        for cid, customer in self._customers.items():
            if cid == exclude_id:
                continue
            if customer.email.lower() == email.strip().lower():
                return True
        return False

    # -----------------------------------------------------------------------
    # Info
    # -----------------------------------------------------------------------
    def get_all_customers(self) -> list:
        """
        Return a list of all active Customer objects.

        Returns:
            list: List of active Customer objects.
        """
        return [c for c in self._customers.values() if c.is_active]

    def get_customer_count(self) -> int:
        """Return the total number of registered customers."""
        return len(self._customers)

    def __repr__(self) -> str:
        return f"AccountManager(customers={self.get_customer_count()})"