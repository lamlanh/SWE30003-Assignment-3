import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for subfolder in ("managers", "models"):
    path = os.path.join(BASE_DIR, subfolder)
    if path not in sys.path:
        sys.path.insert(0, path)

DIVIDER = "=" * 60
THIN    = "-" * 60


def print_header(title: str) -> None:
    print()
    print(DIVIDER)
    print(f"  {title}")
    print(DIVIDER)


def get_input(prompt: str) -> str:
    return input(f"  {prompt}").strip()


class FleetUI:
    """
    Terminal UI for fleet management in SmartFM.

    Staff / Admin operations:
        - View all vehicles
        - View all drivers
        - Add a new vehicle
        - Add a new driver
        - Update vehicle status
        - Update driver status
    """

    def __init__(self, system):
        self._system = system
        self._fleet  = system.fleet_manager

    # -----------------------------------------------------------------------
    # View all vehicles
    # -----------------------------------------------------------------------
    def view_all_vehicles(self) -> None:
        """Display all vehicles in the fleet."""
        print_header("ALL VEHICLES")

        vehicles = self._fleet.get_all_vehicles()

        if not vehicles:
            print("  No vehicles in the fleet.")
            input("\n  Press Enter to continue...")
            return

        print(f"  {'ID':<10} {'Registration':<15} {'Type':<8} {'Capacity':<12} {'Status':<15} {'Branch'}")
        print(THIN)
        for v in vehicles:
            print(
                f"  {v.vehicle_id:<10} {v.registration:<15} "
                f"{v.vehicle_type:<8} {str(v.capacity_kg)+' kg':<12} "
                f"{v.status:<15} {v.branch_id}"
            )
            if v.maintenance_note:
                print(f"  {'':10} Note: {v.maintenance_note}")

        print(THIN)
        print(f"  Total vehicles: {len(vehicles)}")
        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # View all drivers
    # -----------------------------------------------------------------------
    def view_all_drivers(self) -> None:
        """Display all drivers in the fleet."""
        print_header("ALL DRIVERS")

        drivers = self._fleet.get_all_drivers()

        if not drivers:
            print("  No drivers in the fleet.")
            input("\n  Press Enter to continue...")
            return

        print(f"  {'ID':<10} {'Name':<20} {'Licence':<15} {'Expiry':<12} {'Status':<12} {'Phone'}")
        print(THIN)
        for d in drivers:
            # Warn if licence is expiring or expired
            licence_status = ""
            if not d.is_licence_valid():
                licence_status = " [EXPIRED]"

            print(
                f"  {d.driver_id:<10} {d.full_name:<20} "
                f"{d.licence_number:<15} {d.licence_expiry:<12} "
                f"{d.status:<12} {d.phone}{licence_status}"
            )
            if d.leave_note:
                print(f"  {'':10} Note: {d.leave_note}")

        print(THIN)
        print(f"  Total drivers: {len(drivers)}")
        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Add vehicle
    # -----------------------------------------------------------------------
    def add_vehicle(self) -> None:
        """Walk staff through adding a new vehicle to the fleet."""
        print_header("ADD NEW VEHICLE")
        print("  (Type 'back' at any field to return to menu.)")
        print(THIN)

        registration = get_input("Registration / Plate No. : ")
        if registration.lower() == "back":
            return

        print()
        print("  Vehicle types:")
        print("    SMALL  — up to 1,000 kg")
        print("    MEDIUM — up to 5,000 kg")
        print("    LARGE  — up to 15,000 kg")
        print()

        vehicle_type = get_input("Vehicle type (SMALL/MEDIUM/LARGE): ").upper()
        if vehicle_type == "BACK":
            return

        if vehicle_type not in ("SMALL", "MEDIUM", "LARGE"):
            print("\n  ERROR: Invalid vehicle type.")
            input("\n  Press Enter to continue...")
            return

        # Auto-set capacity based on type
        default_capacity = {"SMALL": 1000.0, "MEDIUM": 5000.0, "LARGE": 15000.0}
        suggested = default_capacity[vehicle_type]

        while True:
            cap_str = get_input(f"Capacity in kg (suggested: {suggested}): ")
            if cap_str.lower() == "back":
                return
            if cap_str == "":
                capacity = suggested
                break
            try:
                capacity = float(cap_str)
                if capacity <= 0:
                    print("  ERROR: Capacity must be greater than 0.")
                    continue
                break
            except ValueError:
                print("  ERROR: Please enter a valid number.")

        branch_id = self._fleet.get_default_branch_id()

        success, message, vehicle = self._fleet.add_vehicle(
            registration = registration,
            vehicle_type = vehicle_type,
            capacity_kg  = capacity,
            branch_id    = branch_id
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Add driver
    # -----------------------------------------------------------------------
    def add_driver(self) -> None:
        """Walk staff through adding a new driver to the fleet."""
        print_header("ADD NEW DRIVER")
        print("  (Type 'back' at any field to return to menu.)")
        print(THIN)

        full_name = get_input("Full name          : ")
        if full_name.lower() == "back":
            return

        licence_number = get_input("Licence number     : ")
        if licence_number.lower() == "back":
            return

        while True:
            licence_expiry = get_input("Licence expiry (YYYY-MM-DD): ")
            if licence_expiry.lower() == "back":
                return
            try:
                from datetime import datetime
                datetime.strptime(licence_expiry, "%Y-%m-%d")
                break
            except ValueError:
                print("  ERROR: Date must be in YYYY-MM-DD format.")

        phone = get_input("Phone number       : ")
        if phone.lower() == "back":
            return

        branch_id = self._fleet.get_default_branch_id()

        success, message, driver = self._fleet.add_driver(
            full_name      = full_name,
            licence_number = licence_number,
            licence_expiry = licence_expiry,
            phone          = phone,
            branch_id      = branch_id
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Update vehicle status
    # -----------------------------------------------------------------------
    def update_vehicle_status(self) -> None:
        """Allow staff to update a vehicle's status."""
        print_header("UPDATE VEHICLE STATUS")

        vehicles = self._fleet.get_all_vehicles()
        if not vehicles:
            print("  No vehicles available.")
            input("\n  Press Enter to continue...")
            return

        print(f"  {'ID':<10} {'Registration':<15} {'Type':<8} {'Status'}")
        print(THIN)
        for v in vehicles:
            print(f"  {v.vehicle_id:<10} {v.registration:<15} {v.vehicle_type:<8} {v.status}")

        print(THIN)
        vehicle_id = get_input("Enter Vehicle ID to update (or 'back'): ")
        if vehicle_id.lower() == "back":
            return

        print()
        print("  Statuses: AVAILABLE | MAINTENANCE")
        new_status = get_input("New status: ").upper()
        if new_status == "BACK":
            return

        maintenance_note = ""
        if new_status == "MAINTENANCE":
            maintenance_note = get_input("Maintenance note (reason): ")

        success, message = self._fleet.update_vehicle_status(
            vehicle_id       = vehicle_id,
            new_status       = new_status,
            maintenance_note = maintenance_note
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")

    # -----------------------------------------------------------------------
    # Update driver status
    # -----------------------------------------------------------------------
    def update_driver_status(self) -> None:
        """Allow staff to update a driver's status."""
        print_header("UPDATE DRIVER STATUS")

        drivers = self._fleet.get_all_drivers()
        if not drivers:
            print("  No drivers available.")
            input("\n  Press Enter to continue...")
            return

        print(f"  {'ID':<10} {'Name':<20} {'Status'}")
        print(THIN)
        for d in drivers:
            print(f"  {d.driver_id:<10} {d.full_name:<20} {d.status}")

        print(THIN)
        driver_id = get_input("Enter Driver ID to update (or 'back'): ")
        if driver_id.lower() == "back":
            return

        print()
        print("  Statuses: AVAILABLE | ON_LEAVE")
        new_status = get_input("New status: ").upper()
        if new_status == "BACK":
            return

        leave_note = ""
        if new_status == "ON_LEAVE":
            leave_note = get_input("Leave reason: ")

        success, message = self._fleet.update_driver_status(
            driver_id  = driver_id,
            new_status = new_status,
            leave_note = leave_note
        )

        if success:
            print(f"\n  SUCCESS: {message}")
        else:
            print(f"\n  ERROR: {message}")

        input("\n  Press Enter to continue...")