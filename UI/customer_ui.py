import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("managers", "services", "models"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

from services.authentication_manager import ROLE_CUSTOMER

DIVIDER = "=" * 60
THIN    = "-" * 60


def print_header(title: str) -> None:
    print()
    print(DIVIDER)
    print(f"  {title}")
    print(DIVIDER)


def get_input(prompt: str) -> str:
    return input(f"  {prompt}").strip()


def get_password(prompt: str) -> str:
    """Get password input — shown as plain text in terminal version."""
    return input(f"  {prompt}").strip()


class CustomerUI:
    """
    Terminal UI for all customer account operations.

    Handles:
        - Register new account
        - Login
        - Logout
        - View account details
        - Update account details
    """

    def __init__(self, system):
        self._system   = system
        self._auth     = system.authentication_manager
        self._accounts = system.account_manager
        self._notifier = system.notification_service

    # -----------------------------------------------------------------------
    # Register
    # -----------------------------------------------------------------------
    def register(self) -> None:
        """Walk the user through registering a new customer account."""
        print_header("REGISTER NEW ACCOUNT")
        print("  Please enter your details below.")
        print("  (Type 'back' at any field to return to main menu.)")
        print(THIN)

        # Collect inputs
        username = get_input("Username         : ")
        if username.lower() == "back":
            return

        password = get_password("Password         : ")
        if password.lower() == "back":
            return

        if len(password) < 6:
            print("\n  Password must be at least 6 characters.")
            return

        confirm = get_password("Confirm password : ")
        if confirm.lower() == "back":
            return

        if password != confirm:
            print("\n  Passwords do not match. Please try again.")
            return

        full_name = get_input("Full name        : ")
        if full_name.lower() == "back":
            return

        email = get_input("Email address    : ")
        if email.lower() == "back":
            return

        phone = get_input("Phone number     : ")
        if phone.lower() == "back":
            return

        address = get_input("Delivery address : ")
        if address.lower() == "back":
            return

        # Attempt registration
        print()
        success, message, customer = self._accounts.register(
            username       = username,
            plain_password = password,
            full_name      = full_name,
            email          = email,
            phone          = phone,
            address        = address
        )

        if success:
            print(f"\n  SUCCESS: {message}")
            self._notifier.notify_account_created(full_name)
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Login
    # -----------------------------------------------------------------------
    def login(self) -> None:
        """Walk the user through logging in."""
        print_header("LOGIN")
        print("  (Type 'back' to return to main menu.)")
        print(THIN)

        username = get_input("Username : ")
        if username.lower() == "back":
            return

        password = get_password("Password : ")
        if password.lower() == "back":
            return

        # Find the customer by username
        customer = self._accounts.find_by_username(username)

        if not customer:
            print(f"\n  ERROR: Username '{username}' not found.")
            input("\n  Press Enter to continue...")
            return

        if not customer.is_active:
            print("\n  ERROR: This account has been deactivated.")
            input("\n  Press Enter to continue...")
            return

        # Attempt login via AuthenticationManager
        success, message = self._auth.login(
            username       = username,
            plain_password = password,
            stored_hash    = customer.password_hash,
            user_id        = customer.customer_id,
            role           = ROLE_CUSTOMER
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Logout
    # -----------------------------------------------------------------------
    def logout(self) -> None:
        """Log out the current user."""
        user = self._auth.get_current_user()
        username = user["username"] if user else "User"
        self._auth.logout()
        print(f"\n  Goodbye, {username}! You have been logged out.")
        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # View account
    # -----------------------------------------------------------------------
    def view_account(self, customer_id: str) -> None:
        """Display the current customer's account details."""
        print_header("MY ACCOUNT")

        customer = self._accounts.get_by_id(customer_id)
        if not customer:
            print("  ERROR: Account not found.")
            input("\n  Press Enter to continue...")
            return

        print(f"  Customer ID      : {customer.customer_id}")
        print(f"  Username         : {customer.username}")
        print(f"  Full Name        : {customer.full_name}")
        print(f"  Email            : {customer.email}")
        print(f"  Phone            : {customer.phone}")
        print(f"  Delivery Address : {customer.address}")
        print(f"  Registered Date  : {customer.registered_date}")
        print(f"  Account Status   : {'Active' if customer.is_active else 'Inactive'}")
        print(THIN)

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Update account
    # -----------------------------------------------------------------------
    def update_account(self, customer_id: str) -> None:
        """Allow the customer to update their account details."""
        print_header("UPDATE MY ACCOUNT")
        print("  Leave a field blank to keep the current value.")
        print("  (Type 'back' to return to menu.)")
        print(THIN)

        customer = self._accounts.get_by_id(customer_id)
        if not customer:
            print("  ERROR: Account not found.")
            input("\n  Press Enter to continue...")
            return

        print(f"  Current Name    : {customer.full_name}")
        print(f"  Current Email   : {customer.email}")
        print(f"  Current Phone   : {customer.phone}")
        print(f"  Current Address : {customer.address}")
        print(THIN)

        full_name = get_input("New full name    (Enter to skip): ")
        if full_name.lower() == "back":
            return

        email = get_input("New email        (Enter to skip): ")
        if email.lower() == "back":
            return

        phone = get_input("New phone        (Enter to skip): ")
        if phone.lower() == "back":
            return

        address = get_input("New address      (Enter to skip): ")
        if address.lower() == "back":
            return

        # Only update fields that were filled in
        success, message = self._accounts.update_customer(
            customer_id = customer_id,
            full_name   = full_name   if full_name   else None,
            email       = email       if email       else None,
            phone       = phone       if phone       else None,
            address     = address     if address     else None
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        # Offer password change
        print()
        change_pw = get_input("Change password? (y/n): ")
        if change_pw.lower() == "y":
            self._change_password(customer_id)

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Change password helper
    # -----------------------------------------------------------------------
    def _change_password(self, customer_id: str) -> None:
        """Walk the user through changing their password."""
        print(THIN)
        old_pw  = get_password("Current password : ")
        new_pw  = get_password("New password     : ")
        confirm = get_password("Confirm new      : ")

        if new_pw != confirm:
            print("\n  ERROR: New passwords do not match.")
            return

        success, message = self._accounts.change_password(
            customer_id  = customer_id,
            old_password = old_pw,
            new_password = new_pw
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")