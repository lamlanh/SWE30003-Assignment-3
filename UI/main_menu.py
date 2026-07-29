import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("ui", "services"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

from ui.customer_ui import CustomerUI
from ui.order_ui    import OrderUI
from ui.fleet_ui    import FleetUI


DIVIDER = "=" * 60
THIN    = "-" * 60


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print()
    print(DIVIDER)
    print(f"  {title}")
    print(DIVIDER)


def get_input(prompt: str) -> str:
    """Get stripped input from the user."""
    return input(f"  {prompt}").strip()


class MainMenu:
    """
    Top-level UI controller for SmartFM.

    Routes the user to:
        - CustomerUI  (register, login, account management)
        - OrderUI     (place orders, view orders, cancel orders, pay)
        - FleetUI     (manage vehicles and drivers)
    """

    def __init__(self, system):
        self._system      = system
        self._auth        = system.authentication_manager
        self._customer_ui = CustomerUI(system)
        self._order_ui    = OrderUI(system)
        self._fleet_ui    = FleetUI(system)

    def run(self) -> None:
        """Main application loop."""
        while True:
            if self._auth.is_logged_in():
                self._show_logged_in_menu()
            else:
                self._show_guest_menu()

    def _show_guest_menu(self) -> None:
        """Display the guest menu for unauthenticated users."""
        print_header("SMARTFM — MAIN MENU")
        print("  [1] Login")
        print("  [2] Register new customer account")
        print("  [0] Exit")
        print(THIN)
        choice = get_input("Enter your choice: ")

        if choice == "1":
            self._customer_ui.login()
        elif choice == "2":
            self._customer_ui.register()
        elif choice == "0":
            self._exit()
        else:
            print("\n  Invalid choice. Please try again.")

    def _show_logged_in_menu(self) -> None:
        """Display the menu for authenticated users."""
        user     = self._auth.get_current_user()
        username = user["username"]
        role     = user["role"]

        print_header(f"SMARTFM — WELCOME, {username.upper()} [{role}]")

        if self._auth.is_customer():
            print("  [1] Place a new shipment order")
            print("  [2] View my orders")
            print("  [3] Cancel an order")
            print("  [4] Pay for an order")
            print("  [5] My account details")
            print("  [6] Update my account")
            print("  [0] Logout")
            print(THIN)
            choice = get_input("Enter your choice: ")
            self._handle_customer_choice(choice)

        elif self._auth.is_staff() or self._auth.is_admin():
            print("  [1] View pending orders")
            print("  [2] Assign vehicle & driver to order")
            print("  [3] View all vehicles")
            print("  [4] View all drivers")
            print("  [5] Add a new vehicle")
            print("  [6] Add a new driver")
            print("  [7] Update vehicle status")
            print("  [8] Update driver status")
            print("  [0] Logout")
            print(THIN)
            choice = get_input("Enter your choice: ")
            self._handle_staff_choice(choice)

    def _handle_customer_choice(self, choice: str) -> None:
        """Route customer menu choices."""
        user_id = self._auth.get_current_user_id()
        if choice == "1":
            self._order_ui.place_order(user_id)
        elif choice == "2":
            self._order_ui.view_orders(user_id)
        elif choice == "3":
            self._order_ui.cancel_order(user_id)
        elif choice == "4":
            self._order_ui.pay_for_order(user_id)
        elif choice == "5":
            self._customer_ui.view_account(user_id)
        elif choice == "6":
            self._customer_ui.update_account(user_id)
        elif choice == "0":
            self._customer_ui.logout()
        else:
            print("\n  Invalid choice. Please try again.")

    def _handle_staff_choice(self, choice: str) -> None:
        """Route staff menu choices."""
        if choice == "1":
            self._order_ui.view_pending_orders()
        elif choice == "2":
            self._order_ui.assign_vehicle_driver()
        elif choice == "3":
            self._fleet_ui.view_all_vehicles()
        elif choice == "4":
            self._fleet_ui.view_all_drivers()
        elif choice == "5":
            self._fleet_ui.add_vehicle()
        elif choice == "6":
            self._fleet_ui.add_driver()
        elif choice == "7":
            self._fleet_ui.update_vehicle_status()
        elif choice == "8":
            self._fleet_ui.update_driver_status()
        elif choice == "0":
            self._customer_ui.logout()
        else:
            print("\n  Invalid choice. Please try again.")

    def _exit(self) -> None:
        """Save all data and exit."""
        print("\n  Saving data...")
        self._system.shutdown()
        sys.exit(0)